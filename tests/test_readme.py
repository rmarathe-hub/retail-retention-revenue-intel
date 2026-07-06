from __future__ import annotations

import re

import pytest


@pytest.mark.docs
@pytest.mark.parametrize(
    "required",
    [
        "Retail Retention & Revenue Intelligence",
        "1,067,371",
        "UCI Online Retail II",
        "Python",
        "SQL",
        "Postgres",
        "Power BI",
        "02_data_quality_checks.sql",
        "05_cohort_retention.sql",
        "06_rfm_segmentation.sql",
        "07_revenue_at_risk.sql",
        "08_product_market_analysis.sql",
        "run_cohort_retention.py",
        "run_rfm_segmentation.py",
        "run_revenue_at_risk.py",
        "run_product_market_analysis.py",
        "export_powerbi_marts.py",
        "download_or_import_data.py",
        "profile_raw_data.py",
        ".venv",
        "pip install -r requirements.txt",
    ],
)
def test_readme_contains_core_project_context(readme_text: str, required: str) -> None:
    assert required in readme_text


@pytest.mark.docs
def test_readme_contains_data_lineage(readme_text: str) -> None:
    lowered = readme_text.lower()
    assert "data lineage" in lowered
    assert "raw" in lowered
    assert "stg" in lowered
    assert "mart" in lowered
    assert "power bi" in lowered


@pytest.mark.docs
def test_readme_day3_script_reference(readme_text: str) -> None:
    assert "scripts/clean_online_retail.py" in readme_text
    assert "cohort retention" in readme_text.lower()


@pytest.mark.docs
def test_readme_no_hardcoded_absolute_local_paths(readme_text: str) -> None:
    absolute_paths = re.findall(r"/Users/[^\s`]+", readme_text)
    assert not absolute_paths

