from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import (
    CLEAN_CANCELED_LINES,
    CLEAN_RETURN_LINES,
    CLEAN_ZERO_OR_NEG_PRICE,
    DB_DIM_CUSTOMER_COUNT,
    DB_DIM_DATE_COUNT,
    EXCLUDED_MISSING_CUSTOMER,
    PROJECT_NAME,
    RAW_ROW_COUNT,
)


DAY5_FILES = [
    "sql/02_data_quality_checks.sql",
]


@pytest.mark.unit
@pytest.mark.parametrize("relative_path", DAY5_FILES)
def test_day5_required_files_exist(project_root: Path, relative_path: str) -> None:
    assert (project_root / relative_path).exists(), f"Missing {relative_path}"


@pytest.mark.integration
def test_day5_completion_contract(project_root: Path, readme_text: str) -> None:
    assert PROJECT_NAME in readme_text
    assert "02_data_quality_checks.sql" in readme_text
    assert "data quality checks" in readme_text.lower()
    assert (project_root / "scripts/validate_data.py").exists()
    assert (project_root / "sql/02_data_quality_checks.sql").exists()
