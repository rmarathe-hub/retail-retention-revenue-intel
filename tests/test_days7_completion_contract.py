from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import (
    COHORT_AVG_MONTH3_RETENTION_RATE,
    COHORT_AVG_MONTH3_REVENUE_RETENTION_RATE,
    COHORT_DISTINCT_MONTHS,
    COHORT_RETENTION_ROWS,
    PROJECT_NAME,
)


DAY7_FILES = [
    "sql/05_cohort_retention.sql",
    "docs/cohort_analysis_notes.md",
    "scripts/run_cohort_retention.py",
]


@pytest.mark.unit
@pytest.mark.parametrize("relative_path", DAY7_FILES)
def test_day7_required_files_exist(project_root: Path, relative_path: str) -> None:
    assert (project_root / relative_path).exists(), f"Missing {relative_path}"


@pytest.mark.integration
def test_day7_completion_contract(project_root: Path, readme_text: str) -> None:
    assert PROJECT_NAME in readme_text
    assert "05_cohort_retention.sql" in readme_text
    assert "run_cohort_retention.py" in readme_text
    assert "cohort retention" in readme_text.lower()


@pytest.mark.sql
@pytest.mark.parametrize(
    "fragment",
    [
        "mart_cohort_retention",
        "cohort_month",
        "activity_month",
        "months_since_first_purchase",
        "retention_rate",
        "revenue_retention_rate",
        "cohort_size",
        "retained_customers",
    ],
)
def test_cohort_sql_defines_mart_columns(project_root: Path, fragment: str) -> None:
    sql = (project_root / "sql/05_cohort_retention.sql").read_text(encoding="utf-8")
    assert fragment in sql


@pytest.mark.unit
def test_run_cohort_retention_module_has_entrypoints(project_root: Path) -> None:
    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "run_cohort_unit", project_root / "scripts/run_cohort_retention.py"
    )
    assert hasattr(module, "run_cohort_retention")
    assert hasattr(module, "main")


@pytest.mark.db
def test_day7_cohort_mart_after_build(project_root: Path) -> None:
    from tests.helpers import db_is_reachable

    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "run_cohort_db", project_root / "scripts/run_cohort_retention.py"
    )
    summary = module.run_cohort_retention()
    assert summary["mart_cohort_retention_rows"] == COHORT_RETENTION_ROWS
    assert summary["distinct_cohort_months"] == COHORT_DISTINCT_MONTHS
    assert summary["avg_month3_retention_rate"] == pytest.approx(
        COHORT_AVG_MONTH3_RETENTION_RATE, rel=1e-3
    )
    assert summary["avg_month3_revenue_retention_rate"] == pytest.approx(
        COHORT_AVG_MONTH3_REVENUE_RETENTION_RATE, rel=1e-3
    )
