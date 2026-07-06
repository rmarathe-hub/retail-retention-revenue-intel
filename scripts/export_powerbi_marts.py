"""
Export PostgreSQL marts to CSV for Power BI.

Exports executive KPIs, monthly revenue, customer orders, cohort, RFM,
and revenue-at-risk marts when populated. Writes a manifest JSON for dashboard builds.

Usage:
  python scripts/export_powerbi_marts.py
  python scripts/export_powerbi_marts.py --mart mart_executive_kpis
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from db_config import create_db_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MARTS_DIR = PROJECT_ROOT / "data" / "marts"
MANIFEST_PATH = PROJECT_ROOT / "data" / "processed" / "powerbi_export_manifest.json"

DAY6_MARTS = [
    "mart_executive_kpis",
    "mart_monthly_revenue",
    "mart_customer_orders",
]

LATER_MARTS = [
    "mart_cohort_retention",
    "mart_customer_rfm",
    "mart_revenue_at_risk",
    "mart_product_performance",
    "mart_country_performance",
]

POWERBI_PAGE1_MARTS = [
    "mart_executive_kpis",
    "mart_monthly_revenue",
]

POWERBI_PAGE2_MARTS = [
    "mart_cohort_retention",
]


def export_mart(engine: Engine, table_name: str, output_dir: Path = MARTS_DIR) -> Path | None:
    with engine.connect() as conn:
        row_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
        if row_count == 0:
            return None
        df = pd.read_sql(text(f"SELECT * FROM {table_name}"), conn)

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{table_name}.csv"
    df.to_csv(output_path, index=False)
    return output_path


def export_powerbi_marts(
    engine: Engine | None = None,
    tables: list[str] | None = None,
    output_dir: Path = MARTS_DIR,
) -> dict[str, str | None]:
    engine = engine or create_db_engine()
    tables = tables or (DAY6_MARTS + LATER_MARTS)

    exported: dict[str, str | None] = {}
    row_counts: dict[str, int] = {}
    for table in tables:
        path = export_mart(engine, table, output_dir)
        exported[table] = str(path) if path else None
        if path:
            with engine.connect() as conn:
                row_counts[table] = int(conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar())
        else:
            row_counts[table] = 0

    manifest = {
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(output_dir.relative_to(PROJECT_ROOT)),
        "exported_files": exported,
        "row_counts": row_counts,
        "powerbi_pages": {
            "executive_overview": {
                "page_number": 1,
                "required_marts": POWERBI_PAGE1_MARTS,
                "guide": "docs/powerbi_dashboard_guide.md#page-1--executive-revenue-overview",
            },
            "cohort_retention": {
                "page_number": 2,
                "required_marts": POWERBI_PAGE2_MARTS,
                "guide": "docs/powerbi_dashboard_guide.md#page-2--cohort-retention",
            },
        },
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return exported


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export marts to CSV for Power BI")
    parser.add_argument(
        "--mart",
        action="append",
        dest="marts",
        help="Export a specific mart table (repeatable)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(MARTS_DIR),
        help="Directory for exported CSV files",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    tables = args.marts if args.marts else None
    exported = export_powerbi_marts(output_dir=Path(args.output_dir), tables=tables)

    print("=" * 60)
    print("POWER BI MART EXPORT")
    print("=" * 60)
    for table, path in exported.items():
        status = path if path else "skipped (empty)"
        print(f"{table}: {status}")
    print("=" * 60)
    print(f"Manifest: {MANIFEST_PATH}")


if __name__ == "__main__":
    main()
