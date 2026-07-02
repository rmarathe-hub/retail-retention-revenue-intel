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
        "Week 1 Day",
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
    assert "scripts/clean_online_retail.py       # Day 3" in readme_text
    assert "Status:** Week 1 Day" in readme_text


@pytest.mark.docs
def test_readme_no_hardcoded_absolute_local_paths(readme_text: str) -> None:
    absolute_paths = re.findall(r"/Users/[^\s`]+", readme_text)
    assert not absolute_paths

