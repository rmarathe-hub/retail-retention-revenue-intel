"""
Build Day 7 cohort retention mart in PostgreSQL.

Prerequisites:
  1. Docker Postgres running with Day 4 load complete
  2. Day 6 marts optional but recommended

Usage:
  python scripts/run_cohort_retention.py
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from db_config import create_db_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"
COHORT_SQL_PATH = SQL_DIR / "05_cohort_retention.sql"
COHORT_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "cohort_mart_summary.json"


def read_sql_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8")


def apply_sql_file(engine: Engine, path: Path) -> None:
    sql = read_sql_file(path)
    with engine.begin() as conn:
        conn.execute(text(sql))


def get_cohort_summary_stats(engine: Engine) -> dict:
    with engine.connect() as conn:
        row_count = int(conn.execute(text("SELECT COUNT(*) FROM mart_cohort_retention")).scalar())
        cohort_count = int(
            conn.execute(text("SELECT COUNT(DISTINCT cohort_month) FROM mart_cohort_retention")).scalar()
        )
        month3 = conn.execute(
            text(
                """
                SELECT
                    ROUND(AVG(retention_rate)::numeric, 4) AS avg_month3_retention_rate,
                    ROUND(AVG(revenue_retention_rate)::numeric, 4) AS avg_month3_revenue_retention_rate
                FROM mart_cohort_retention
                WHERE months_since_first_purchase = 3
                """
            )
        ).mappings().one()

    return {
        "mart_cohort_retention_rows": row_count,
        "distinct_cohort_months": cohort_count,
        "avg_month3_retention_rate": float(month3["avg_month3_retention_rate"] or 0),
        "avg_month3_revenue_retention_rate": float(month3["avg_month3_revenue_retention_rate"] or 0),
    }


def run_cohort_retention(engine: Engine | None = None) -> dict:
    engine = engine or create_db_engine()
    apply_sql_file(engine, COHORT_SQL_PATH)
    stats = get_cohort_summary_stats(engine)

    summary = {
        "cohort_sql_applied": True,
        "sql_file": str(COHORT_SQL_PATH.relative_to(PROJECT_ROOT)),
        **stats,
    }

    COHORT_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    COHORT_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = run_cohort_retention()

    print("=" * 60)
    print("COHORT RETENTION MART SUMMARY")
    print("=" * 60)
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("=" * 60)
    print(f"Saved: {COHORT_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
