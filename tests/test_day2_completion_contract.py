from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.integration
def test_day2_completion_contract(project_root: Path, readme_text: str) -> None:
    assert (project_root / "scripts" / "download_or_import_data.py").exists()
    assert (project_root / "scripts" / "profile_raw_data.py").exists()
    assert (project_root / "scripts" / "clean_online_retail.py").exists()
    assert (project_root / "docs" / "data_dictionary.md").exists()
    assert (project_root / "docs" / "data_quality_report.md").exists()
    assert "Week 1 Day" in readme_text
    assert "profiles raw data" in readme_text


@pytest.mark.data
def test_day2_local_data_artifacts_optional(project_root: Path) -> None:
    raw_dir = project_root / "data" / "raw"
    if not raw_dir.exists():
        pytest.skip("raw directory not present")

    combined = raw_dir / "online_retail_II_combined.csv"
    summary = raw_dir / "profile_summary.json"
    # Allow local development without artifacts; but if one exists the other should too.
    if not combined.exists() and not summary.exists():
        pytest.skip("local Day 2 artifacts not present")

    assert combined.exists()
    assert summary.exists()

