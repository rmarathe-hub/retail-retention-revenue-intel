from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import (
    MART_REVENUE_AT_RISK_ROWS,
    PROJECT_NAME,
    RISK_INACTIVE_120D_COUNT,
    RISK_INACTIVE_180D_COUNT,
    RISK_INACTIVE_90D_COUNT,
    RISK_RECOVERABLE_10PCT,
    RISK_TOP_10PCT_REVENUE_SHARE,
    RISK_TOP_1PCT_REVENUE_SHARE,
    RISK_TOTAL_REVENUE_AT_RISK,
)


DAY9_FILES = [
    "sql/07_revenue_at_risk.sql",
    "docs/revenue_at_risk_notes.md",
    "scripts/run_revenue_at_risk.py",
]


@pytest.mark.unit
@pytest.mark.parametrize("relative_path", DAY9_FILES)
def test_day9_required_files_exist(project_root: Path, relative_path: str) -> None:
    assert (project_root / relative_path).exists(), f"Missing {relative_path}"


@pytest.mark.integration
def test_day9_completion_contract(project_root: Path, readme_text: str) -> None:
    assert PROJECT_NAME in readme_text
    assert "07_revenue_at_risk.sql" in readme_text
    assert "run_revenue_at_risk.py" in readme_text
    assert "revenue-at-risk" in readme_text.lower() or "revenue at risk" in readme_text.lower()


@pytest.mark.sql
@pytest.mark.parametrize(
    "fragment",
    [
        "mart_revenue_at_risk",
        "last_purchase_date",
        "days_since_last_purchase",
        "historical_revenue",
        "inactivity_window",
        "potential_recoverable_revenue",
        "NTILE(4)",
        "180d",
        "120d",
        "90d",
        "2011-12-09",
        "0.10",
    ],
)
def test_revenue_at_risk_sql_defines_mart_columns(project_root: Path, fragment: str) -> None:
    sql = (project_root / "sql/07_revenue_at_risk.sql").read_text(encoding="utf-8")
    assert fragment in sql


@pytest.mark.unit
def test_run_revenue_at_risk_module_has_entrypoints(project_root: Path) -> None:
    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "run_risk_unit", project_root / "scripts/run_revenue_at_risk.py"
    )
    assert hasattr(module, "run_revenue_at_risk")
    assert hasattr(module, "main")


@pytest.mark.db
def test_day9_revenue_at_risk_mart_after_build(project_root: Path) -> None:
    from tests.helpers import db_is_reachable

    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "run_risk_db", project_root / "scripts/run_revenue_at_risk.py"
    )
    summary = module.run_revenue_at_risk()
    assert summary["mart_revenue_at_risk_rows"] == MART_REVENUE_AT_RISK_ROWS
    assert summary["total_revenue_at_risk"] == pytest.approx(RISK_TOTAL_REVENUE_AT_RISK, rel=1e-3)
    assert summary["recoverable_revenue_10pct"] == pytest.approx(RISK_RECOVERABLE_10PCT, rel=1e-3)
    assert summary["inactive_90d_count"] == RISK_INACTIVE_90D_COUNT
    assert summary["inactive_120d_count"] == RISK_INACTIVE_120D_COUNT
    assert summary["inactive_180d_count"] == RISK_INACTIVE_180D_COUNT
    assert summary["top_1pct_revenue_share"] == pytest.approx(RISK_TOP_1PCT_REVENUE_SHARE, rel=1e-3)
    assert summary["top_10pct_revenue_share"] == pytest.approx(RISK_TOP_10PCT_REVENUE_SHARE, rel=1e-3)


@pytest.mark.db
def test_revenue_at_risk_rows_align_with_customer_orders(project_root: Path) -> None:
    from tests.helpers import db_is_reachable

    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    from sqlalchemy import text
    from tests.conftest import load_module_from_path

    engine = load_module_from_path("risk_align", project_root / "scripts/db_config.py").create_db_engine()
    with engine.connect() as conn:
        mismatches = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM mart_revenue_at_risk r
                JOIN mart_customer_orders o ON r.customer_id = o.customer_id
                WHERE r.historical_revenue <> o.total_revenue
                """
            )
        ).scalar()
    assert mismatches == 0
