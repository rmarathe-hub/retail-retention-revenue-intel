from __future__ import annotations

import pytest

from tests.helpers import (
    EXECUTIVE_KPI_NAMES,
    KPI_AOV,
    KPI_CANCELLATION_LINE_RATE,
    KPI_ONE_TIME_BUYER_RATE,
    KPI_REPEAT_PURCHASE_RATE,
    KPI_REVENUE_PER_CUSTOMER,
    KPI_TOTAL_CUSTOMERS,
    KPI_TOTAL_ORDERS,
    KPI_TOTAL_REVENUE,
    KPI_TOTAL_REVENUE_CUSTOMER,
)


@pytest.mark.docs
def test_metric_definitions_status_locked(metric_definitions_text: str) -> None:
    assert "locked" in metric_definitions_text.lower()
    assert "03_kpi_definitions.sql" in metric_definitions_text


@pytest.mark.docs
@pytest.mark.parametrize("kpi_name", EXECUTIVE_KPI_NAMES)
def test_metric_definitions_lists_executive_kpis(metric_definitions_text: str, kpi_name: str) -> None:
    assert kpi_name in metric_definitions_text or kpi_name.replace("_", " ") in metric_definitions_text


@pytest.mark.docs
@pytest.mark.parametrize(
    ("snippet", "value"),
    [
        ("20,755,215.33", KPI_TOTAL_REVENUE),
        ("17,685,460.64", KPI_TOTAL_REVENUE_CUSTOMER),
        ("36,975", KPI_TOTAL_ORDERS),
        ("5,881", KPI_TOTAL_CUSTOMERS),
        ("478.31", KPI_AOV),
        ("3,007.22", KPI_REVENUE_PER_CUSTOMER),
        ("72.35%", KPI_REPEAT_PURCHASE_RATE),
        ("27.65%", KPI_ONE_TIME_BUYER_RATE),
        ("1.84%", KPI_CANCELLATION_LINE_RATE),
    ],
)
def test_metric_definitions_contains_locked_values(
    metric_definitions_text: str, snippet: str, value: float
) -> None:
    assert snippet in metric_definitions_text


@pytest.mark.docs
def test_metric_definitions_global_rules_finalized(metric_definitions_text: str) -> None:
    assert "Global Rules (locked)" in metric_definitions_text
    assert "is_canceled = FALSE" in metric_definitions_text
    assert "2011-12-09" in metric_definitions_text


@pytest.mark.docs
def test_planned_metrics_still_documented(metric_definitions_text: str) -> None:
    assert "Planned Day 7" in metric_definitions_text
    assert "mart_cohort_retention" in metric_definitions_text
    assert "mart_customer_rfm" in metric_definitions_text
