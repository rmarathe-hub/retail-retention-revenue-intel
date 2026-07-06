from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.conftest import load_module_from_path
from tests.helpers import WEEK1_SCRIPTS


ENTRYPOINT_SYMBOLS = {
    "scripts/download_or_import_data.py": ["main", "combine_sheets_to_csv"],
    "scripts/profile_raw_data.py": ["main", "profile_dataframe"],
    "scripts/clean_online_retail.py": ["main", "clean_transactions"],
    "scripts/db_config.py": ["create_db_engine", "get_database_url"],
    "scripts/load_to_postgres.py": ["main", "run_load_pipeline"],
    "scripts/validate_data.py": ["main", "run_validation"],
    "scripts/run_kpi_marts.py": ["main", "run_kpi_marts"],
    "scripts/export_powerbi_marts.py": ["main", "export_powerbi_marts"],
    "scripts/run_cohort_retention.py": ["main", "run_cohort_retention"],
    "scripts/run_rfm_segmentation.py": ["main", "run_rfm_segmentation"],
    "scripts/run_revenue_at_risk.py": ["main", "run_revenue_at_risk"],
}


SCRIPTS_WITH_MAIN_GUARD = [s for s in WEEK1_SCRIPTS if s != "scripts/db_config.py"]


@pytest.mark.unit
@pytest.mark.parametrize("script_path", SCRIPTS_WITH_MAIN_GUARD)
def test_week1_script_has_main_guard(project_root: Path, script_path: str) -> None:
    content = (project_root / script_path).read_text(encoding="utf-8")
    assert 'if __name__ == "__main__":' in content


@pytest.mark.unit
def test_db_config_is_importable_library_module(project_root: Path) -> None:
    content = (project_root / "scripts/db_config.py").read_text(encoding="utf-8")
    assert "create_db_engine" in content
    assert 'if __name__ == "__main__":' not in content


@pytest.mark.unit
@pytest.mark.parametrize("script_path", WEEK1_SCRIPTS)
def test_week1_script_imports_without_side_effects(project_root: Path, script_path: str) -> None:
    module = load_module_from_path(f"safe_{script_path.replace('/', '_')}", project_root / script_path)
    assert module is not None


@pytest.mark.unit
@pytest.mark.parametrize("script_path,symbols", list(ENTRYPOINT_SYMBOLS.items()))
def test_week1_script_exports_entrypoints(
    project_root: Path, script_path: str, symbols: list[str]
) -> None:
    module = load_module_from_path(f"ep_{script_path.replace('/', '_')}", project_root / script_path)
    for symbol in symbols:
        assert hasattr(module, symbol), f"{script_path} missing {symbol}"


@pytest.mark.unit
@pytest.mark.parametrize("script_path", WEEK1_SCRIPTS)
def test_week1_script_no_absolute_user_paths(project_root: Path, script_path: str) -> None:
    content = (project_root / script_path).read_text(encoding="utf-8")
    matches = re.findall(r"/Users/[^\s\"']+", content)
    assert matches == [], f"{script_path} has hardcoded paths: {matches}"


@pytest.mark.unit
@pytest.mark.parametrize("script_path", WEEK1_SCRIPTS)
def test_week1_script_uses_pathlib_or_project_root(project_root: Path, script_path: str) -> None:
    content = (project_root / script_path).read_text(encoding="utf-8")
    assert "Path" in content or "pathlib" in content or "__file__" in content
