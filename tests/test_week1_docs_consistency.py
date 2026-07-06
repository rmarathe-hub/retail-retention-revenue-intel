from __future__ import annotations

import pytest

from tests.helpers import (
    COHORT_AVG_MONTH3_RETENTION_RATE,
    COHORT_AVG_MONTH3_REVENUE_RETENTION_RATE,
    COHORT_DISTINCT_MONTHS,
    COHORT_RETENTION_ROWS,
)


METRIC_DEFINITION_SNIPPETS = [
    "Total Revenue",
    "Customer-attributed revenue",
    "Total Orders",
    "Total Customers",
    "Average Order Value",
    "Revenue per Customer",
    "Repeat Purchase Rate",
    "One-time Buyer Rate",
    "Cancellation Line Rate",
    "Cohort Retention Rate",
    "Revenue Retention Rate",
    "cohort_size",
    "retained_customers",
    "retention_rate",
    "cohort_revenue",
    "revenue_retention_rate",
    "2011-12-09",
    "is_canceled = FALSE",
    "valid `customer_id`",
    "Day 9 Metrics (locked)",
    "mart_revenue_at_risk",
    "Product & Market Metrics (locked)",
    "85.06%",
]

COHORT_NOTES_SNIPPETS = [
    "first purchase month",
    "null `customer_id`",
    "non-canceled",
    "2011-12-09",
    "months_since_first_purchase",
    "retention_rate",
    "revenue_retention_rate",
    "mart_cohort_retention",
    "05_cohort_retention.sql",
    "cohort_month",
    "cohort_size",
    "retained_customers",
]

COHORT_LOCKED_STATS = [
    ("21.61", COHORT_AVG_MONTH3_RETENTION_RATE),
    ("26.44", COHORT_AVG_MONTH3_REVENUE_RETENTION_RATE),
    ("325", COHORT_RETENTION_ROWS),
    ("25", COHORT_DISTINCT_MONTHS),
]

DATA_QUALITY_SNIPPETS = [
    "1,067,371",
    "1,055,238",
    "812,368",
    "242,870",
    "2,638,407.51",
    "27 automated",
    "02_data_quality_checks.sql",
    "validation_summary.json",
    "flag",
    "do not silently drop",
    "duplicate",
    "missing customer",
    "canceled",
    "returns",
]

README_SNIPPETS = [
    "Retail Retention & Revenue Intelligence",
    "1,067,371",
    "UCI Online Retail II",
    "5433",
    "docker compose up",
    "download_or_import_data.py",
    "profile_raw_data.py",
    "clean_online_retail.py",
    "load_to_postgres.py",
    "validate_data.py",
    "run_kpi_marts.py",
    "run_cohort_retention.py",
    "run_product_market_analysis.py",
    "export_powerbi_marts.py",
    "recommendations.md",
    "portfolio_case_study.md",
    "Case Study",
    "page1_executive_overview.png",
    "gitignored",
    "Power BI",
]


@pytest.mark.docs
@pytest.mark.parametrize("snippet", METRIC_DEFINITION_SNIPPETS)
def test_metric_definitions_contains_snippet(metric_definitions_text: str, snippet: str) -> None:
    assert snippet in metric_definitions_text


@pytest.mark.docs
@pytest.mark.parametrize("snippet", COHORT_NOTES_SNIPPETS)
def test_cohort_notes_contains_snippet(cohort_analysis_notes_text: str, snippet: str) -> None:
    assert snippet.lower() in cohort_analysis_notes_text.lower()


@pytest.mark.docs
def test_locked_cohort_stats_in_metric_definitions_or_summary(
    metric_definitions_text: str,
    cohort_mart_summary_path,
) -> None:
    """Locked cohort stats live in metric_definitions (Day 7) and cohort_mart_summary.json."""
    locked_section = metric_definitions_text.split("## Day 7 Metrics (locked)")[1]
    for needle, _ in COHORT_LOCKED_STATS:
        assert needle in locked_section or needle in metric_definitions_text
    if cohort_mart_summary_path.exists():
        import json
        summary = json.loads(cohort_mart_summary_path.read_text(encoding="utf-8"))
        assert summary["mart_cohort_retention_rows"] == COHORT_RETENTION_ROWS
        assert summary["distinct_cohort_months"] == COHORT_DISTINCT_MONTHS


@pytest.mark.docs
@pytest.mark.parametrize("snippet", DATA_QUALITY_SNIPPETS)
def test_data_quality_report_contains_snippet(data_quality_text: str, snippet: str) -> None:
    assert snippet.lower() in data_quality_text.lower()


@pytest.mark.docs
@pytest.mark.parametrize("snippet", README_SNIPPETS)
def test_readme_contains_snippet(readme_text: str, snippet: str) -> None:
    assert snippet in readme_text


@pytest.mark.docs
@pytest.mark.parametrize(
    "phrase",
    [
        "RFM segmentation complete",
        "revenue at risk complete",
        "Power BI dashboard complete",
        "dashboard complete",
        "Screenshots complete",
        "recommendations complete",
        "Day 8 complete",
        "Day 9 complete",
        "Week 2 complete",
    ],
)
def test_readme_does_not_claim_future_work_complete(readme_text: str, phrase: str) -> None:
    assert phrase.lower() not in readme_text.lower()


@pytest.mark.docs
@pytest.mark.parametrize(
    "phrase",
    [
        "Executive Summary Rollup",
        "09_executive_summary.sql",
    ],
)
def test_metric_definitions_executive_summary_still_planned(
    metric_definitions_text: str, phrase: str
) -> None:
    planned = metric_definitions_text.split("## Planned Metrics")[1]
    assert phrase.lower() in planned.lower()
