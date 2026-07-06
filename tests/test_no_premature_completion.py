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
    "sql/09_executive_summary.sql",
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
def test_metric_definitions_product_market_metrics_locked(metric_definitions_text: str) -> None:
    assert "**Locked**" in metric_definitions_text
    assert "Product & Market Metrics (locked)" in metric_definitions_text
    assert "mart_product_performance" in metric_definitions_text
    assert "mart_country_performance" in metric_definitions_text
    assert "5,304" in metric_definitions_text
    assert "85.06%" in metric_definitions_text


@pytest.mark.docs
def test_metric_definitions_no_tbd_on_locked_metrics(metric_definitions_text: str) -> None:
    locked_section = metric_definitions_text.split("## Planned Metrics")[0]
    assert "TBD" not in locked_section
