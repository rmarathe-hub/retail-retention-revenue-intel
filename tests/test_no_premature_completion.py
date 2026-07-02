from __future__ import annotations

from pathlib import Path

import pytest


PREMATURE_COMPLETE_PHRASES = [
    "Week 2 complete",
    "Day 5 complete",
    "Day 6 complete",
    "Day 7 complete",
    "Day 8 complete",
    "Day 9 complete",
    "KPI definitions locked",
    "dashboard complete",
    "Power BI dashboard complete",
    "cohort retention complete",
    "RFM segmentation complete",
    "revenue at risk complete",
]


NOT_YET_FILES = [
    "sql/02_data_quality_checks.sql",
    "sql/03_kpi_definitions.sql",
    "sql/04_revenue_analysis.sql",
    "sql/05_cohort_retention.sql",
    "sql/06_rfm_segmentation.sql",
    "sql/07_revenue_at_risk.sql",
    "sql/08_product_market_analysis.sql",
    "sql/09_executive_summary.sql",
    "scripts/export_powerbi_marts.py",
    "dashboard/Retail_Retention_Revenue_Intelligence.pbix",
]


@pytest.mark.docs
@pytest.mark.hygiene
@pytest.mark.parametrize("phrase", PREMATURE_COMPLETE_PHRASES)
def test_readme_does_not_claim_premature_completion(readme_text: str, phrase: str) -> None:
    assert phrase.lower() not in readme_text.lower()


@pytest.mark.unit
@pytest.mark.hygiene
@pytest.mark.parametrize("relative_path", NOT_YET_FILES)
def test_day5_plus_files_not_present_yet(project_root: Path, relative_path: str) -> None:
    assert not (project_root / relative_path).exists()


@pytest.mark.docs
def test_metric_definitions_still_has_tbd_entries(metric_definitions_text: str) -> None:
    assert "TBD" in metric_definitions_text
    assert "Day 6" in metric_definitions_text or "locked by" in metric_definitions_text
