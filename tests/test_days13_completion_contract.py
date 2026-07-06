from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import PROJECT_NAME


DAY13_FILES = [
    "docs/portfolio_case_study.md",
    "dashboard/screenshots/README.md",
]


CASE_STUDY_SNIPPETS = [
    "Case Study",
    "Business problem",
    "Approach",
    "Results",
    "Recommended actions",
    "portfolio_case_study.md",
]

SCREENSHOT_PATHS = [
    "page1_executive_overview.png",
    "page2_cohort_retention.png",
    "page3_rfm_segmentation.png",
    "page4_revenue_at_risk.png",
    "page5_product_market.png",
    "page6_action_plan.png",
]


@pytest.mark.unit
@pytest.mark.parametrize("relative_path", DAY13_FILES)
def test_day13_required_files_exist(project_root: Path, relative_path: str) -> None:
    assert (project_root / relative_path).exists(), f"Missing {relative_path}"


@pytest.mark.docs
@pytest.mark.parametrize("snippet", CASE_STUDY_SNIPPETS)
def test_readme_case_study_sections(readme_text: str, snippet: str) -> None:
    assert snippet.lower() in readme_text.lower()


@pytest.mark.docs
@pytest.mark.parametrize("filename", SCREENSHOT_PATHS)
def test_readme_documents_screenshot_paths(readme_text: str, filename: str) -> None:
    assert filename in readme_text


@pytest.mark.docs
def test_readme_screenshots_pending_not_claimed_complete(readme_text: str) -> None:
    assert "Add after Power BI Desktop build" in readme_text
    assert "Power BI dashboard complete" not in readme_text.lower()
    assert "dashboard complete" not in readme_text.lower()


@pytest.mark.integration
def test_day13_completion_contract(project_root: Path, readme_text: str) -> None:
    assert PROJECT_NAME in readme_text
    assert "recommendations.md" in readme_text
    assert "£179,135" in readme_text or "179,135.53" in readme_text
    assert "run_product_market_analysis.py" in readme_text
    assert (project_root / "docs/portfolio_case_study.md").exists()


@pytest.mark.docs
def test_portfolio_case_study_has_locked_metrics(project_root: Path) -> None:
    text = (project_root / "docs/portfolio_case_study.md").read_text(encoding="utf-8")
    assert "72.35%" in text
    assert "179,135" in text
    assert "1,343" in text
    assert "64.04%" in text
