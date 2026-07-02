"""
Validate PostgreSQL connectivity, Day 4 load row counts, and SQL data-quality checks.

Runs sql/02_data_quality_checks.sql after load and writes validation_summary.json.

Usage:
  python scripts/validate_data.py
"""

from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from db_config import create_db_engine
from load_to_postgres import get_table_row_counts, validate_load_counts

PROJECT_ROOT = Path(__file__).resolve().parents[1]
VALIDATION_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "validation_summary.json"
DQ_CHECKS_SQL_PATH = PROJECT_ROOT / "sql" / "02_data_quality_checks.sql"

MISSING_CUSTOMER_REVENUE_SQL = """
SELECT
    ROUND(COALESCE(SUM(line_revenue), 0)::numeric, 2) AS missing_customer_revenue_gbp,
    COUNT(*)::bigint AS missing_customer_line_count
FROM stg_transactions
WHERE is_missing_customer = TRUE
"""


def load_dq_checks_sql(path: Path = DQ_CHECKS_SQL_PATH) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Data quality SQL not found: {path}")
    raw = path.read_text(encoding="utf-8")
    # Strip full-line SQL comments; keep the main SELECT intact.
    lines = [line for line in raw.splitlines() if not line.strip().startswith("--")]
    sql = "\n".join(lines).strip()
    if not sql.upper().startswith("SELECT"):
        raise ValueError(f"Expected SELECT query in {path}")
    return sql


def run_sql_quality_checks(engine: Engine, sql: str | None = None) -> list[dict]:
    query = sql or load_dq_checks_sql()
    with engine.connect() as conn:
        rows = conn.execute(text(query)).mappings().all()

    checks: list[dict] = []
    for row in rows:
        expected = int(row["expected_value"])
        actual = int(row["actual_value"])
        status = "ok" if actual == expected else "fail"
        checks.append(
            {
                "check_name": row["check_name"],
                "expected": expected,
                "actual": actual,
                "status": status,
            }
        )
    return checks


def run_missing_customer_revenue_metric(engine: Engine) -> dict:
    with engine.connect() as conn:
        row = conn.execute(text(MISSING_CUSTOMER_REVENUE_SQL)).mappings().one()
    return {
        "missing_customer_revenue_gbp": float(row["missing_customer_revenue_gbp"]),
        "missing_customer_line_count": int(row["missing_customer_line_count"]),
    }


def summarize_quality_checks(checks: list[dict]) -> dict[str, str]:
    return {check["check_name"]: check["status"] for check in checks}


def run_validation() -> dict:
    engine = create_db_engine()

    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

    counts = get_table_row_counts(engine)
    load_validation = validate_load_counts(counts)
    quality_checks = run_sql_quality_checks(engine)
    quality_summary = summarize_quality_checks(quality_checks)
    revenue_metric = run_missing_customer_revenue_metric(engine)

    all_load_ok = all(value == "ok" for value in load_validation.values())
    all_quality_ok = all(check["status"] == "ok" for check in quality_checks)

    summary = {
        "connection": "ok",
        "table_counts": counts,
        "load_validation": load_validation,
        "quality_checks": quality_checks,
        "quality_validation": quality_summary,
        "metrics": revenue_metric,
        "all_checks_passed": all_load_ok and all_quality_ok,
    }

    VALIDATION_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    summary = run_validation()

    print("=" * 60)
    print("POSTGRES VALIDATION SUMMARY")
    print("=" * 60)
    print(f"connection: {summary['connection']}")
    print(f"all_checks_passed: {summary['all_checks_passed']}")
    print(f"load_validation: {summary['load_validation']}")
    print(f"quality_checks_run: {len(summary['quality_checks'])}")
    failed = [c for c in summary["quality_checks"] if c["status"] != "ok"]
    if failed:
        print("failed_quality_checks:")
        for check in failed:
            print(f"  - {check['check_name']}: expected {check['expected']}, got {check['actual']}")
    print(f"metrics: {summary['metrics']}")
    print("=" * 60)
    print(f"Saved: {VALIDATION_SUMMARY_PATH}")

    if not summary["all_checks_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
