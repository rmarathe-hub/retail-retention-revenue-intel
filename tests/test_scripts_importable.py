from __future__ import annotations

from pathlib import Path

import pytest

from .conftest import load_module_from_path


@pytest.mark.unit
@pytest.mark.parametrize(
    ("script_path", "expected_symbols"),
    [
        (
            "scripts/download_or_import_data.py",
            ["main", "download_raw_data", "combine_sheets_to_csv"],
        ),
        (
            "scripts/profile_raw_data.py",
            ["main", "load_raw", "profile_dataframe", "write_profile"],
        ),
        (
            "scripts/load_to_postgres.py",
            ["main", "run_load_pipeline", "validate_load_counts", "get_table_row_counts"],
        ),
        (
            "scripts/validate_data.py",
            ["main", "run_validation", "run_sql_quality_checks"],
        ),
        (
            "scripts/run_kpi_marts.py",
            ["main", "run_kpi_marts"],
        ),
        (
            "scripts/run_cohort_retention.py",
            ["main", "run_cohort_retention"],
        ),
        (
            "scripts/run_rfm_segmentation.py",
            ["main", "run_rfm_segmentation"],
        ),
        (
            "scripts/run_revenue_at_risk.py",
            ["main", "run_revenue_at_risk"],
        ),
        (
            "scripts/export_powerbi_marts.py",
            ["main", "export_powerbi_marts"],
        ),
        (
            "scripts/db_config.py",
            ["get_database_url", "create_db_engine"],
        ),
    ],
)
def test_scripts_import_and_entrypoints(
    project_root: Path, script_path: str, expected_symbols: list[str]
) -> None:
    module = load_module_from_path("test_module", project_root / script_path)
    for symbol in expected_symbols:
        assert hasattr(module, symbol), f"{script_path} missing symbol: {symbol}"


@pytest.mark.unit
def test_scripts_have_main_guard(project_root: Path) -> None:
    for script in (
        "scripts/download_or_import_data.py",
        "scripts/profile_raw_data.py",
        "scripts/load_to_postgres.py",
        "scripts/validate_data.py",
        "scripts/run_kpi_marts.py",
        "scripts/run_cohort_retention.py",
        "scripts/run_rfm_segmentation.py",
        "scripts/run_revenue_at_risk.py",
        "scripts/export_powerbi_marts.py",
    ):
        text = (project_root / script).read_text(encoding="utf-8")
        assert 'if __name__ == "__main__":' in text

