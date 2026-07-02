"""
Build Day 6 KPI and revenue analysis marts in PostgreSQL.

Prerequisites:
  1. Docker Postgres running with Day 4 load complete
  2. stg_transactions populated

Usage:
  python scripts/run_kpi_marts.py
  python scripts/run_kpi_marts.py --kpi-only
  python scripts/run_kpi_marts.py --revenue-only
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from db_config import create_db_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"
KPI_SQL_PATH = SQL_DIR / "03_kpi_definitions.sql"
REVENUE_SQL_PATH = SQL_DIR / "04_revenue_analysis.sql"
KPI_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "kpi_mart_summary.json"


def read_sql_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8")


def apply_sql_file(engine: Engine, path: Path) -> None:
    sql = read_sql_file(path)
    with engine.begin() as conn:
        conn.execute(text(sql))


def get_mart_row_counts(engine: Engine) -> dict[str, int]:
    tables = [
        "mart_executive_kpis",
        "mart_monthly_revenue",
        "mart_customer_orders",
    ]
    counts: dict[str, int] = {}
    with engine.connect() as conn:
        for table in tables:
            counts[table] = int(conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar())
    return counts


def get_executive_kpis(engine: Engine) -> list[dict]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT kpi_name, kpi_value, kpi_unit, as_of_date "
                "FROM mart_executive_kpis ORDER BY kpi_name"
            )
        ).mappings().all()
    return [dict(row) for row in rows]


def run_kpi_marts(
    engine: Engine | None = None,
    *,
    run_kpi: bool = True,
    run_revenue: bool = True,
) -> dict:
    engine = engine or create_db_engine()

    if run_kpi:
        apply_sql_file(engine, KPI_SQL_PATH)
    if run_revenue:
        apply_sql_file(engine, REVENUE_SQL_PATH)

    counts = get_mart_row_counts(engine)
    kpis = get_executive_kpis(engine)

    summary = {
        "kpi_sql_applied": run_kpi,
        "revenue_sql_applied": run_revenue,
        "mart_row_counts": counts,
        "executive_kpis": kpis,
    }

    KPI_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    KPI_SUMMARY_PATH.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Day 6 KPI and revenue marts")
    parser.add_argument("--kpi-only", action="store_true", help="Run 03_kpi_definitions.sql only")
    parser.add_argument(
        "--revenue-only", action="store_true", help="Run 04_revenue_analysis.sql only"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_kpi = not args.revenue_only
    run_revenue = not args.kpi_only

    summary = run_kpi_marts(run_kpi=run_kpi, run_revenue=run_revenue)

    print("=" * 60)
    print("KPI MART BUILD SUMMARY")
    print("=" * 60)
    print(f"mart_row_counts: {summary['mart_row_counts']}")
    print(f"executive_kpis: {len(summary['executive_kpis'])} rows")
    print("=" * 60)
    print(f"Saved: {KPI_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
