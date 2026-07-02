from __future__ import annotations

from pathlib import Path

import pytest


REQUIRED_PATHS = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    ".env.example",
    "scripts/download_or_import_data.py",
    "scripts/profile_raw_data.py",
    "scripts/clean_online_retail.py",
    "scripts/load_to_postgres.py",
    "scripts/validate_data.py",
    "scripts/db_config.py",
    "docker-compose.yml",
    "sql/01_schema.sql",
    "docs/postgres_setup.md",
    "docs/business_problem.md",
    "docs/metric_definitions.md",
    "docs/data_dictionary.md",
    "docs/data_quality_report.md",
    "data",
    "data/raw",
    "data/processed",
    "sql",
    "dashboard",
    "dashboard/screenshots",
    "docs",
    "scripts",
]


@pytest.mark.unit
@pytest.mark.parametrize("relative_path", REQUIRED_PATHS)
def test_required_paths_exist(project_root: Path, relative_path: str) -> None:
    assert (project_root / relative_path).exists(), f"Missing required path: {relative_path}"


@pytest.mark.unit
def test_tests_directory_exists(project_root: Path) -> None:
    assert (project_root / "tests").exists()

