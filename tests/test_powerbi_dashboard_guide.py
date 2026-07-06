from __future__ import annotations

import pytest


POWERBI_GUIDE_SNIPPETS = [
    "Executive Revenue Overview",
    "Cohort Retention",
    "RFM Customer Segmentation",
    "Revenue Concentration & At-Risk",
    "mart_executive_kpis.csv",
    "mart_monthly_revenue.csv",
    "mart_cohort_retention.csv",
    "mart_customer_rfm.csv",
    "mart_revenue_at_risk.csv",
    "mart_customer_orders.csv",
    "customer_segment",
    "inactivity_window",
    "potential_recoverable_revenue",
    "months_since_first_purchase",
    "retention_rate",
    "revenue_retention_rate",
    "export_powerbi_marts.py",
    "powerbi_export_manifest.json",
    "21.61",
    "26.44",
    "72.35",
    "1,343",
    "1,791,355",
    "32.02%",
]

DASHBOARD_README_SNIPPETS = [
    "Executive Revenue Overview",
    "Cohort Retention",
    "RFM Customer Segmentation",
    "Revenue Concentration & At-Risk",
    "powerbi_dashboard_guide.md",
    "powerbi_export_manifest.json",
    "screenshots",
]


@pytest.mark.docs
@pytest.mark.parametrize("snippet", POWERBI_GUIDE_SNIPPETS)
def test_powerbi_dashboard_guide_contains_snippet(project_root, snippet: str) -> None:
    text = (project_root / "docs/powerbi_dashboard_guide.md").read_text(encoding="utf-8")
    assert snippet.lower() in text.lower()


@pytest.mark.docs
@pytest.mark.parametrize("snippet", DASHBOARD_README_SNIPPETS)
def test_dashboard_readme_contains_snippet(project_root, snippet: str) -> None:
    text = (project_root / "dashboard/README.md").read_text(encoding="utf-8")
    assert snippet.lower() in text.lower()


@pytest.mark.docs
def test_readme_key_insights_use_locked_numbers(readme_text: str) -> None:
    assert "X%" not in readme_text
    assert "£X" not in readme_text
    assert "72.35%" in readme_text
    assert "1,343 Champions" in readme_text
    assert "64.04%" in readme_text
    assert "179,135.53" in readme_text
    assert "21.61%" in readme_text
    assert "26.44%" in readme_text
    assert "1.84%" in readme_text


@pytest.mark.docs
def test_readme_links_powerbi_dashboard_guide(readme_text: str) -> None:
    assert "powerbi_dashboard_guide.md" in readme_text
    assert "Guide + CSV exports ready" in readme_text
    assert "RFM Customer Segmentation" in readme_text
    assert "Revenue Concentration & At-Risk" in readme_text


@pytest.mark.unit
def test_export_module_declares_powerbi_page_marts(project_root) -> None:
    from tests.conftest import load_module_from_path

    module = load_module_from_path("pbi_pages", project_root / "scripts/export_powerbi_marts.py")
    assert "mart_executive_kpis" in module.POWERBI_PAGE1_MARTS
    assert "mart_monthly_revenue" in module.POWERBI_PAGE1_MARTS
    assert module.POWERBI_PAGE2_MARTS == ["mart_cohort_retention"]
    assert module.POWERBI_PAGE3_MARTS == ["mart_customer_rfm"]
    assert module.POWERBI_PAGE4_MARTS == ["mart_revenue_at_risk", "mart_customer_orders"]
    assert module.MANIFEST_PATH.name == "powerbi_export_manifest.json"
