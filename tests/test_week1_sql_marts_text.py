from __future__ import annotations

import pytest

from tests.helpers import (
    COHORT_RETENTION_ROWS,
    DQ_CHECK_NAMES,
    EXECUTIVE_KPI_NAMES,
    MART_CUSTOMER_ORDERS_ROWS,
    MART_MONTHLY_REVENUE_ROWS,
)


@pytest.mark.sql
@pytest.mark.parametrize("check_name", DQ_CHECK_NAMES)
def test_dq_sql_contains_check_name(dq_sql_text: str, check_name: str) -> None:
    assert f"'{check_name}'" in dq_sql_text


@pytest.mark.sql
@pytest.mark.parametrize("kpi_name", EXECUTIVE_KPI_NAMES)
def test_kpi_sql_contains_kpi_name(kpi_sql_text: str, kpi_name: str) -> None:
    assert f"'{kpi_name}'" in kpi_sql_text


@pytest.mark.sql
@pytest.mark.parametrize(
    "fragment",
    [
        "mart_executive_kpis",
        "is_canceled = FALSE",
        "TRUNCATE TABLE mart_executive_kpis",
        "2011-12-09",
        "repeat_purchase_rate",
        "cancellation_line_rate",
    ],
)
def test_kpi_sql_business_rules(kpi_sql_text: str, fragment: str) -> None:
    assert fragment in kpi_sql_text


@pytest.mark.sql
@pytest.mark.parametrize(
    "fragment",
    [
        "mart_monthly_revenue",
        "mart_customer_orders",
        "new_customer_revenue",
        "returning_customer_revenue",
        "is_repeat_customer",
        "first_order_date",
        "last_order_date",
    ],
)
def test_revenue_sql_populates_marts(revenue_sql_text: str, fragment: str) -> None:
    assert fragment in revenue_sql_text


@pytest.mark.sql
@pytest.mark.parametrize(
    "fragment",
    [
        "mart_cohort_retention",
        "cohort_month",
        "activity_month",
        "months_since_first_purchase",
        "cohort_size",
        "retained_customers",
        "retention_rate",
        "cohort_revenue",
        "revenue_retention_rate",
        "customer_id IS NOT NULL",
    ],
)
def test_cohort_sql_defines_retention_mart(cohort_sql_text: str, fragment: str) -> None:
    assert fragment in cohort_sql_text


@pytest.mark.sql
def test_dq_sql_has_27_distinct_checks(dq_sql_text: str) -> None:
    import re
    names = re.findall(r"SELECT '([a-z_0-9]+)'", dq_sql_text)
    assert len(names) == 27
    assert len(set(names)) == 27
