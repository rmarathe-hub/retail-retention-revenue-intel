from __future__ import annotations

from pathlib import Path

import pytest

from tests.conftest import load_module_from_path
from tests.helpers import (
    CLEAN_OUTPUT_ROWS,
    DB_DIM_CUSTOMER_COUNT,
    DB_DIM_DATE_COUNT,
    EXCLUDED_MISSING_CUSTOMER,
    RAW_ROW_COUNT,
    db_is_reachable,
)


@pytest.fixture(scope="module")
def validate_module(project_root):
    return load_module_from_path(
        "validate_module", project_root / "scripts/validate_data.py"
    )


@pytest.mark.unit
def test_validate_module_has_run_validation(validate_module) -> None:
    assert hasattr(validate_module, "run_validation")
    assert hasattr(validate_module, "main")


@pytest.mark.db
def test_validate_data_against_loaded_db(project_root: Path, validate_module) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    summary = validate_module.run_validation()
    assert summary["connection"] == "ok"
    assert summary["all_checks_passed"] is True
    assert summary["table_counts"]["raw_online_retail"] == RAW_ROW_COUNT
    assert summary["table_counts"]["stg_transactions"] == CLEAN_OUTPUT_ROWS
    assert summary["table_counts"]["dim_customer"] == DB_DIM_CUSTOMER_COUNT
    assert summary["table_counts"]["dim_date"] == DB_DIM_DATE_COUNT
    assert len(summary["quality_checks"]) == 25
    assert all(c["status"] == "ok" for c in summary["quality_checks"])
    assert summary["metrics"]["missing_customer_line_count"] == EXCLUDED_MISSING_CUSTOMER
    assert summary["metrics"]["missing_customer_revenue_gbp"] > 0


@pytest.mark.db
def test_db_table_counts_after_day4_load(project_root: Path) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    load_module = load_module_from_path(
        "load_db_contract", project_root / "scripts/load_to_postgres.py"
    )
    engine = load_module.create_db_engine()
    counts = load_module.get_table_row_counts(engine)
    validation = load_module.validate_load_counts(counts)
    assert all(v == "ok" for v in validation.values())
