from __future__ import annotations

import pytest

from tests.helpers import (
    CLEAN_CANCELED_LINES,
    CLEAN_OUTPUT_ROWS,
    CLEAN_RETURN_LINES,
    CLEAN_ZERO_OR_NEG_PRICE,
    DB_DIM_CUSTOMER_COUNT,
    DB_DIM_DATE_COUNT,
    EXCLUDED_MISSING_CUSTOMER,
    RAW_ROW_COUNT,
)


EXPECTED_DQ_CHECKS = [
    "raw_row_count",
    "stg_row_count",
    "dim_customer_count",
    "dim_date_count",
    "mart_monthly_revenue_rows",
    "mart_customer_orders_rows",
    "mart_executive_kpis_rows",
    "mart_customer_rfm_empty",
    "mart_cohort_retention_empty",
    "mart_revenue_at_risk_empty",
    "mart_product_performance_empty",
    "mart_country_performance_empty",
    "missing_customer_lines",
    "canceled_lines",
    "return_lines",
    "zero_or_negative_price_lines",
    "invalid_invoice_date_lines",
    "canceled_flag_mismatch",
    "return_flag_mismatch",
    "missing_customer_flag_mismatch",
    "zero_price_flag_mismatch",
    "line_revenue_mismatch",
    "stg_distinct_customers",
    "min_invoice_date_key",
    "max_invoice_date_key",
]

EXPECTED_VALUES = {
    "raw_row_count": RAW_ROW_COUNT,
    "stg_row_count": CLEAN_OUTPUT_ROWS,
    "dim_customer_count": DB_DIM_CUSTOMER_COUNT,
    "dim_date_count": DB_DIM_DATE_COUNT,
    "missing_customer_lines": EXCLUDED_MISSING_CUSTOMER,
    "canceled_lines": CLEAN_CANCELED_LINES,
    "return_lines": CLEAN_RETURN_LINES,
    "zero_or_negative_price_lines": CLEAN_ZERO_OR_NEG_PRICE,
    "invalid_invoice_date_lines": 0,
    "min_invoice_date_key": 20091201,
    "max_invoice_date_key": 20111209,
    "stg_distinct_customers": DB_DIM_CUSTOMER_COUNT,
    "mart_monthly_revenue_rows": 25,
    "mart_customer_orders_rows": 5_881,
    "mart_executive_kpis_rows": 9,
}


@pytest.mark.sql
def test_dq_sql_file_exists(project_root) -> None:
    assert (project_root / "sql/02_data_quality_checks.sql").exists()


@pytest.mark.sql
@pytest.mark.parametrize("check_name", EXPECTED_DQ_CHECKS)
def test_dq_sql_references_check_name(dq_sql_text: str, check_name: str) -> None:
    assert f"'{check_name}'" in dq_sql_text


@pytest.mark.sql
@pytest.mark.parametrize(
    ("check_name", "expected"),
    list(EXPECTED_VALUES.items()),
)
def test_dq_sql_embeds_expected_values(
    dq_sql_text: str, check_name: str, expected: int
) -> None:
    assert str(expected) in dq_sql_text


@pytest.mark.sql
@pytest.mark.parametrize(
    "fragment",
    [
        "is_missing_customer",
        "is_canceled",
        "is_return",
        "is_zero_or_negative_price",
        "line_revenue",
        "quantity * unit_price",
    ],
)
def test_dq_sql_validates_stg_flags_and_revenue(dq_sql_text: str, fragment: str) -> None:
    assert fragment in dq_sql_text


@pytest.mark.unit
def test_validate_module_exposes_dq_helpers(project_root) -> None:
    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "validate_dq_unit", project_root / "scripts/validate_data.py"
    )
    assert hasattr(module, "load_dq_checks_sql")
    assert hasattr(module, "run_sql_quality_checks")
    assert hasattr(module, "run_missing_customer_revenue_metric")


@pytest.mark.unit
def test_load_dq_checks_sql_strips_comments(project_root) -> None:
    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "validate_dq_load", project_root / "scripts/validate_data.py"
    )
    sql = module.load_dq_checks_sql()
    assert sql.upper().startswith("SELECT")
    assert "--" not in sql
