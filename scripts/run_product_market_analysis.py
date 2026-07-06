"""
Build product and country performance marts in PostgreSQL.

Prerequisites:
  1. Docker Postgres running with Day 4 load complete

Usage:
  python scripts/run_product_market_analysis.py
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from db_config import create_db_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"
PRODUCT_MARKET_SQL_PATH = SQL_DIR / "08_product_market_analysis.sql"
PRODUCT_MARKET_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "product_market_summary.json"


def read_sql_file(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8")


def apply_sql_file(engine: Engine, path: Path) -> None:
    sql = read_sql_file(path)
    with engine.begin() as conn:
        conn.execute(text(sql))


def get_product_market_summary_stats(engine: Engine) -> dict:
    with engine.connect() as conn:
        product_rows = int(conn.execute(text("SELECT COUNT(*) FROM mart_product_performance")).scalar())
        country_rows = int(conn.execute(text("SELECT COUNT(*) FROM mart_country_performance")).scalar())
        top_product = conn.execute(
            text(
                """
                SELECT stock_code, description, total_revenue, cancellation_rate
                FROM mart_product_performance
                ORDER BY total_revenue DESC
                LIMIT 1
                """
            )
        ).mappings().one()
        top_country = conn.execute(
            text(
                """
                SELECT country, total_revenue, total_orders, active_customers
                FROM mart_country_performance
                ORDER BY total_revenue DESC
                LIMIT 1
                """
            )
        ).mappings().one()
        uk_share = conn.execute(
            text(
                """
                WITH totals AS (
                    SELECT SUM(total_revenue) AS company_revenue
                    FROM mart_country_performance
                )
                SELECT ROUND(
                    100.0 * c.total_revenue / NULLIF(t.company_revenue, 0),
                    4
                ) AS uk_revenue_share_pct
                FROM mart_country_performance c
                CROSS JOIN totals t
                WHERE c.country = 'United Kingdom'
                """
            )
        ).scalar()

    return {
        "mart_product_performance_rows": product_rows,
        "mart_country_performance_rows": country_rows,
        "top_product_stock_code": top_product["stock_code"],
        "top_product_description": top_product["description"],
        "top_product_revenue": float(top_product["total_revenue"] or 0),
        "top_product_cancellation_rate": float(top_product["cancellation_rate"] or 0),
        "top_country": top_country["country"],
        "top_country_revenue": float(top_country["total_revenue"] or 0),
        "top_country_orders": int(top_country["total_orders"] or 0),
        "uk_revenue_share_pct": float(uk_share or 0),
    }


def run_product_market_analysis(engine: Engine | None = None) -> dict:
    engine = engine or create_db_engine()
    apply_sql_file(engine, PRODUCT_MARKET_SQL_PATH)
    stats = get_product_market_summary_stats(engine)

    summary = {
        "product_market_sql_applied": True,
        "sql_file": str(PRODUCT_MARKET_SQL_PATH.relative_to(PROJECT_ROOT)),
        **stats,
    }

    PRODUCT_MARKET_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    PRODUCT_MARKET_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = run_product_market_analysis()

    print("=" * 60)
    print("PRODUCT & MARKET MART SUMMARY")
    print("=" * 60)
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("=" * 60)
    print(f"Saved: {PRODUCT_MARKET_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
