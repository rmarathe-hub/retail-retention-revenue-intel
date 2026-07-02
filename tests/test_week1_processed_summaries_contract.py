from __future__ import annotations

import json

import pytest

from tests.helpers import (
    CLEAN_CANCELED_LINES,
    CLEAN_DUPLICATES_REMOVED,
    CLEAN_INPUT_ROWS,
    CLEAN_OUTPUT_ROWS,
    CLEAN_RETURN_LINES,
    CLEAN_ZERO_OR_NEG_PRICE,
    CUSTOMER_LEVEL_ROWS,
    DB_DIM_CUSTOMER_COUNT,
    DB_DIM_DATE_COUNT,
    DQ_CHECK_COUNT,
    EXCLUDED_MISSING_CUSTOMER,
    KPI_AOV,
    KPI_CANCELLATION_LINE_RATE,
    KPI_ONE_TIME_BUYER_RATE,
    KPI_REPEAT_PURCHASE_RATE,
    KPI_REVENUE_PER_CUSTOMER,
    KPI_TOTAL_CUSTOMERS,
    KPI_TOTAL_ORDERS,
    KPI_TOTAL_REVENUE,
    KPI_TOTAL_REVENUE_CUSTOMER,
    MART_CUSTOMER_ORDERS_ROWS,
    MART_MONTHLY_REVENUE_ROWS,
    EXECUTIVE_KPI_COUNT,
    COHORT_AVG_MONTH3_RETENTION_RATE,
    COHORT_AVG_MONTH3_REVENUE_RETENTION_RATE,
    COHORT_DISTINCT_MONTHS,
    COHORT_RETENTION_ROWS,
    MISSING_CUSTOMER_REVENUE_GBP,
    RAW_ROW_COUNT,
    skip_if_missing,
)


@pytest.fixture(scope="module")
def validation_summary(validation_summary_path):
    skip_if_missing(validation_summary_path, "validation_summary.json not found")
    return json.loads(validation_summary_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def kpi_mart_summary(kpi_mart_summary_path):
    skip_if_missing(kpi_mart_summary_path, "kpi_mart_summary.json not found")
    return json.loads(kpi_mart_summary_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def cohort_mart_summary(cohort_mart_summary_path):
    skip_if_missing(cohort_mart_summary_path, "cohort_mart_summary.json not found")
    return json.loads(cohort_mart_summary_path.read_text(encoding="utf-8"))


@pytest.mark.data
def test_validation_summary_is_valid_json(validation_summary: dict) -> None:
    assert isinstance(validation_summary, dict)


@pytest.mark.data
def test_validation_summary_all_checks_passed(validation_summary: dict) -> None:
    assert validation_summary["all_checks_passed"] is True


@pytest.mark.data
def test_validation_summary_has_27_quality_checks(validation_summary: dict) -> None:
    assert len(validation_summary["quality_checks"]) == DQ_CHECK_COUNT


@pytest.mark.data
@pytest.mark.parametrize("check_name", [
    "raw_row_count", "stg_row_count", "mart_cohort_retention_rows",
    "cohort_month_zero_retention_mismatch", "line_revenue_mismatch",
])
def test_validation_summary_critical_checks_ok(
    validation_summary: dict, check_name: str
) -> None:
    statuses = {c["check_name"]: c["status"] for c in validation_summary["quality_checks"]}
    assert statuses[check_name] == "ok"


@pytest.mark.data
def test_validation_summary_missing_customer_revenue(validation_summary: dict) -> None:
    metrics = validation_summary["metrics"]
    assert metrics["missing_customer_line_count"] == EXCLUDED_MISSING_CUSTOMER
    assert metrics["missing_customer_revenue_gbp"] == pytest.approx(
        MISSING_CUSTOMER_REVENUE_GBP, rel=1e-4
    )


@pytest.mark.data
@pytest.mark.parametrize(
    ("table", "expected"),
    [
        ("raw_online_retail", RAW_ROW_COUNT),
        ("stg_transactions", CLEAN_OUTPUT_ROWS),
        ("dim_customer", DB_DIM_CUSTOMER_COUNT),
        ("dim_date", DB_DIM_DATE_COUNT),
    ],
)
def test_validation_summary_table_counts(
    validation_summary: dict, table: str, expected: int
) -> None:
    assert validation_summary["table_counts"][table] == expected


@pytest.mark.data
@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("mart_executive_kpis", EXECUTIVE_KPI_COUNT),
        ("mart_monthly_revenue", MART_MONTHLY_REVENUE_ROWS),
        ("mart_customer_orders", MART_CUSTOMER_ORDERS_ROWS),
    ],
)
def test_kpi_mart_summary_row_counts(kpi_mart_summary: dict, key: str, expected: int) -> None:
    assert kpi_mart_summary["mart_row_counts"][key] == expected


@pytest.mark.data
def test_kpi_mart_summary_excludes_cohort_mart(kpi_mart_summary: dict) -> None:
    assert "mart_cohort_retention" not in kpi_mart_summary["mart_row_counts"]


@pytest.mark.data
@pytest.mark.parametrize(
    ("kpi_name", "expected"),
    [
        ("total_revenue", KPI_TOTAL_REVENUE),
        ("total_revenue_customer_attributed", KPI_TOTAL_REVENUE_CUSTOMER),
        ("total_orders", KPI_TOTAL_ORDERS),
        ("total_customers", KPI_TOTAL_CUSTOMERS),
        ("average_order_value", KPI_AOV),
        ("revenue_per_customer", KPI_REVENUE_PER_CUSTOMER),
        ("repeat_purchase_rate", KPI_REPEAT_PURCHASE_RATE),
        ("one_time_buyer_rate", KPI_ONE_TIME_BUYER_RATE),
        ("cancellation_line_rate", KPI_CANCELLATION_LINE_RATE),
    ],
)
def test_kpi_mart_summary_locked_kpi_values(
    kpi_mart_summary: dict, kpi_name: str, expected: float
) -> None:
    kpi_map = {row["kpi_name"]: float(row["kpi_value"]) for row in kpi_mart_summary["executive_kpis"]}
    assert kpi_name in kpi_map
    assert kpi_map[kpi_name] == pytest.approx(expected, rel=1e-3)


@pytest.mark.data
@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("mart_cohort_retention_rows", COHORT_RETENTION_ROWS),
        ("distinct_cohort_months", COHORT_DISTINCT_MONTHS),
        ("avg_month3_retention_rate", COHORT_AVG_MONTH3_RETENTION_RATE),
        ("avg_month3_revenue_retention_rate", COHORT_AVG_MONTH3_REVENUE_RETENTION_RATE),
    ],
)
def test_cohort_mart_summary_values(cohort_mart_summary: dict, key: str, expected: float) -> None:
    assert cohort_mart_summary[key] == pytest.approx(expected, rel=1e-3)


@pytest.mark.data
@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("raw_input_rows", CLEAN_INPUT_ROWS),
        ("duplicate_rows_removed", CLEAN_DUPLICATES_REMOVED),
        ("clean_output_rows", CLEAN_OUTPUT_ROWS),
        ("customer_level_rows", CUSTOMER_LEVEL_ROWS),
        ("excluded_rows_missing_customer_id", EXCLUDED_MISSING_CUSTOMER),
        ("canceled_invoice_lines", CLEAN_CANCELED_LINES),
        ("return_lines", CLEAN_RETURN_LINES),
        ("zero_or_negative_price_lines", CLEAN_ZERO_OR_NEG_PRICE),
    ],
)
def test_cleaning_summary_contract(cleaning_summary_path, key: str, expected: int) -> None:
    skip_if_missing(cleaning_summary_path, "cleaning_summary.json not found")
    summary = json.loads(cleaning_summary_path.read_text(encoding="utf-8"))
    assert summary[key] == expected
