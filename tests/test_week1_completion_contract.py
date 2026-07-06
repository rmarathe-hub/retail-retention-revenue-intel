from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import (
    DAY8_PLUS_FILES,
    PROJECT_NAME,
    WEEK1_DOCS,
    WEEK1_SCRIPTS,
    WEEK1_SQL_FILES,
)


ROOT_FILES = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    "docker-compose.yml",
    ".env.example",
    "pytest.ini",
]

DATA_DIRS = [
    "data/raw/.gitkeep",
    "data/processed/.gitkeep",
    "data/marts/.gitkeep",
    "dashboard/screenshots/.gitkeep",
]


@pytest.mark.unit
@pytest.mark.parametrize("relative_path", ROOT_FILES + DATA_DIRS + WEEK1_DOCS + WEEK1_SCRIPTS + WEEK1_SQL_FILES)
def test_week1_required_files_exist(project_root: Path, relative_path: str) -> None:
    assert (project_root / relative_path).exists(), f"Missing {relative_path}"


@pytest.mark.unit
@pytest.mark.hygiene
@pytest.mark.parametrize("relative_path", DAY8_PLUS_FILES)
def test_day8_plus_files_not_present(project_root: Path, relative_path: str) -> None:
    assert not (project_root / relative_path).exists(), f"Premature file exists: {relative_path}"


@pytest.mark.integration
def test_week1_master_contract(project_root: Path, readme_text: str) -> None:
    assert PROJECT_NAME in readme_text
    assert "run_cohort_retention.py" in readme_text
    assert "05_cohort_retention.sql" in readme_text
    assert not (project_root / "sql/08_product_market_analysis.sql").exists()
    for script in WEEK1_SCRIPTS:
        assert (project_root / script).exists()
