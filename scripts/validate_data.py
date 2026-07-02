"""
Validate PostgreSQL connectivity and Day 4 load row counts.

Full SQL data-quality checks are added on Day 5 (sql/02_data_quality_checks.sql).

Usage:
  python scripts/validate_data.py
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import text

from db_config import create_db_engine
from load_to_postgres import get_table_row_counts, validate_load_counts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "validation_summary.json"


def run_validation() -> dict:
    engine = create_db_engine()

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    counts = get_table_row_counts(engine)
    validation = validate_load_counts(counts)

    summary = {
        "connection": "ok",
        "table_counts": counts,
        "validation": validation,
        "all_checks_passed": all(value == "ok" for value in validation.values()),
    }

    VALIDATION_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = run_validation()

    print("=" * 60)
    print("POSTGRES VALIDATION SUMMARY")
    print("=" * 60)
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("=" * 60)
    print(f"Saved: {VALIDATION_SUMMARY_PATH}")

    if not summary["all_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
