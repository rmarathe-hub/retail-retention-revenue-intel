"""
Build Day 8 RFM segmentation mart in PostgreSQL.

Prerequisites:
  1. Docker Postgres running with Day 4 load complete
  2. Day 6 customer order mart recommended for validation

Usage:
  python scripts/run_rfm_segmentation.py
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from db_config import create_db_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"
RFM_SQL_PATH = SQL_DIR / "06_rfm_segmentation.sql"
RFM_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "rfm_mart_summary.json"


def read_sql_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8")


def apply_sql_file(engine: Engine, path: Path) -> None:
    sql = read_sql_file(path)
    with engine.begin() as conn:
        conn.execute(text(sql))


def get_rfm_summary_stats(engine: Engine) -> dict:
    with engine.connect() as conn:
        row_count = int(conn.execute(text("SELECT COUNT(*) FROM mart_customer_rfm")).scalar())
        segment_counts = conn.execute(
            text(
                """
                SELECT customer_segment, COUNT(*)::integer AS customer_count
                FROM mart_customer_rfm
                GROUP BY customer_segment
                ORDER BY customer_segment
                """
            )
        ).mappings().all()
        averages = conn.execute(
            text(
                """
                SELECT
                    ROUND(AVG(recency_days)::numeric, 4) AS avg_recency_days,
                    ROUND(AVG(frequency_orders)::numeric, 4) AS avg_frequency_orders,
                    ROUND(AVG(monetary_value)::numeric, 4) AS avg_monetary_value
                FROM mart_customer_rfm
                """
            )
        ).mappings().one()
        champions = int(
            conn.execute(
                text(
                    "SELECT COUNT(*) FROM mart_customer_rfm WHERE customer_segment = 'Champions'"
                )
            ).scalar()
        )
        at_risk = int(
            conn.execute(
                text(
                    "SELECT COUNT(*) FROM mart_customer_rfm WHERE customer_segment = 'At Risk'"
                )
            ).scalar()
        )

    return {
        "mart_customer_rfm_rows": row_count,
        "champions_count": champions,
        "at_risk_count": at_risk,
        "avg_recency_days": float(averages["avg_recency_days"] or 0),
        "avg_frequency_orders": float(averages["avg_frequency_orders"] or 0),
        "avg_monetary_value": float(averages["avg_monetary_value"] or 0),
        "segment_counts": {
            row["customer_segment"]: row["customer_count"] for row in segment_counts
        },
    }


def run_rfm_segmentation(engine: Engine | None = None) -> dict:
    engine = engine or create_db_engine()
    apply_sql_file(engine, RFM_SQL_PATH)
    stats = get_rfm_summary_stats(engine)

    summary = {
        "rfm_sql_applied": True,
        "sql_file": str(RFM_SQL_PATH.relative_to(PROJECT_ROOT)),
        **stats,
    }

    RFM_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    RFM_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = run_rfm_segmentation()

    print("=" * 60)
    print("RFM SEGMENTATION MART SUMMARY")
    print("=" * 60)
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("=" * 60)
    print(f"Saved: {RFM_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
