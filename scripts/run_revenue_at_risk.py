"""
Build Day 9 revenue-at-risk mart in PostgreSQL.

Prerequisites:
  1. Docker Postgres running with Day 4 load complete
  2. Day 6 customer order mart recommended for concentration metrics

Usage:
  python scripts/run_revenue_at_risk.py
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from db_config import create_db_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"
RISK_SQL_PATH = SQL_DIR / "07_revenue_at_risk.sql"
RISK_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "revenue_at_risk_summary.json"


def read_sql_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8")


def apply_sql_file(engine: Engine, path: Path) -> None:
    sql = read_sql_file(path)
    with engine.begin() as conn:
        conn.execute(text(sql))


def get_revenue_at_risk_summary_stats(engine: Engine) -> dict:
    with engine.connect() as conn:
        row_count = int(conn.execute(text("SELECT COUNT(*) FROM mart_revenue_at_risk")).scalar())
        totals = conn.execute(
            text(
                """
                SELECT
                    ROUND(SUM(historical_revenue)::numeric, 4) AS total_revenue_at_risk,
                    ROUND(SUM(potential_recoverable_revenue)::numeric, 4) AS recoverable_revenue_10pct
                FROM mart_revenue_at_risk
                """
            )
        ).mappings().one()
        window_counts = conn.execute(
            text(
                """
                SELECT inactivity_window, COUNT(*)::integer AS customer_count
                FROM mart_revenue_at_risk
                GROUP BY inactivity_window
                ORDER BY inactivity_window
                """
            )
        ).mappings().all()
        concentration = conn.execute(
            text(
                """
                WITH ranked AS (
                    SELECT
                        total_revenue,
                        SUM(total_revenue) OVER () AS total_customer_revenue,
                        PERCENT_RANK() OVER (ORDER BY total_revenue DESC) AS pct_rank
                    FROM mart_customer_orders
                )
                SELECT
                    ROUND(
                        100.0 * SUM(
                            CASE WHEN pct_rank <= 0.01 THEN total_revenue ELSE 0 END
                        ) / MAX(total_customer_revenue),
                        4
                    ) AS top_1pct_revenue_share,
                    ROUND(
                        100.0 * SUM(
                            CASE WHEN pct_rank <= 0.10 THEN total_revenue ELSE 0 END
                        ) / MAX(total_customer_revenue),
                        4
                    ) AS top_10pct_revenue_share
                FROM ranked
                """
            )
        ).mappings().one()

    return {
        "mart_revenue_at_risk_rows": row_count,
        "total_revenue_at_risk": float(totals["total_revenue_at_risk"] or 0),
        "recoverable_revenue_10pct": float(totals["recoverable_revenue_10pct"] or 0),
        "inactive_90d_count": next(
            (row["customer_count"] for row in window_counts if row["inactivity_window"] == "90d"),
            0,
        ),
        "inactive_120d_count": next(
            (row["customer_count"] for row in window_counts if row["inactivity_window"] == "120d"),
            0,
        ),
        "inactive_180d_count": next(
            (row["customer_count"] for row in window_counts if row["inactivity_window"] == "180d"),
            0,
        ),
        "top_1pct_revenue_share": float(concentration["top_1pct_revenue_share"] or 0),
        "top_10pct_revenue_share": float(concentration["top_10pct_revenue_share"] or 0),
    }


def run_revenue_at_risk(engine: Engine | None = None) -> dict:
    engine = engine or create_db_engine()
    apply_sql_file(engine, RISK_SQL_PATH)
    stats = get_revenue_at_risk_summary_stats(engine)

    summary = {
        "revenue_at_risk_sql_applied": True,
        "sql_file": str(RISK_SQL_PATH.relative_to(PROJECT_ROOT)),
        **stats,
    }

    RISK_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    RISK_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = run_revenue_at_risk()

    print("=" * 60)
    print("REVENUE AT RISK MART SUMMARY")
    print("=" * 60)
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("=" * 60)
    print(f"Saved: {RISK_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
