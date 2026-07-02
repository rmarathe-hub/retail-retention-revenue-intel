from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import PROJECT_NAME


DAY1_ROOT_FILES = [
    "README.md",
    "requirements.txt",
    ".gitignore",
    "pytest.ini",
]

DAY1_DOCS = [
    "docs/business_problem.md",
    "docs/metric_definitions.md",
]

DAY2_SCRIPTS = [
    "scripts/download_or_import_data.py",
    "scripts/profile_raw_data.py",
]

DAY3_SCRIPTS = [
    "scripts/clean_online_retail.py",
]

DAY4_FILES = [
    "docker-compose.yml",
    ".env.example",
    "docs/postgres_setup.md",
    "scripts/db_config.py",
    "scripts/load_to_postgres.py",
    "scripts/validate_data.py",
    "sql/01_schema.sql",
]


@pytest.mark.unit
@pytest.mark.parametrize("relative_path", DAY1_ROOT_FILES + DAY1_DOCS + DAY2_SCRIPTS + DAY3_SCRIPTS + DAY4_FILES)
def test_days1_4_required_files_exist(project_root: Path, relative_path: str) -> None:
    assert (project_root / relative_path).exists(), f"Missing {relative_path}"


@pytest.mark.integration
def test_days1_4_completion_contract(project_root: Path, readme_text: str) -> None:
    assert PROJECT_NAME in readme_text
    for script in DAY2_SCRIPTS + DAY3_SCRIPTS + ["scripts/load_to_postgres.py", "scripts/validate_data.py"]:
        assert (project_root / script).exists()
