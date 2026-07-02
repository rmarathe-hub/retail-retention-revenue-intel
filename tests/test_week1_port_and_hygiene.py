from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import (
    FORBIDDEN_HOST_PORT_PATTERNS,
    PORT_SCAN_PATHS,
    git_tracked_files,
)


@pytest.mark.unit
@pytest.mark.hygiene
@pytest.mark.parametrize("relative_path", PORT_SCAN_PATHS)
def test_port_scan_files_exist(project_root: Path, relative_path: str) -> None:
    assert (project_root / relative_path).exists()


@pytest.mark.unit
@pytest.mark.hygiene
@pytest.mark.parametrize("relative_path", PORT_SCAN_PATHS)
@pytest.mark.parametrize("forbidden", FORBIDDEN_HOST_PORT_PATTERNS)
def test_no_forbidden_host_port_in_config_files(
    project_root: Path, relative_path: str, forbidden: str
) -> None:
    content = (project_root / relative_path).read_text(encoding="utf-8")
    assert forbidden not in content, f"{forbidden} found in {relative_path}"


@pytest.mark.unit
@pytest.mark.hygiene
@pytest.mark.parametrize("relative_path", PORT_SCAN_PATHS)
def test_port_scan_files_reference_5433(project_root: Path, relative_path: str) -> None:
    content = (project_root / relative_path).read_text(encoding="utf-8")
    if relative_path == "docker-compose.yml":
        assert "5433:5432" in content
    elif relative_path.endswith(".py") and "db_config" in relative_path:
        assert "5433" in content


@pytest.mark.integration
@pytest.mark.hygiene
@pytest.mark.parametrize(
    "prefix",
    ["data/raw/", "data/processed/", "data/marts/", ".venv/"],
)
def test_git_tracked_excludes_data_prefixes(project_root: Path, prefix: str) -> None:
    tracked = git_tracked_files(project_root)
    allowed_gitkeeps = {"data/raw/.gitkeep", "data/processed/.gitkeep", "data/marts/.gitkeep"}
    bad = [
        p for p in tracked
        if p.startswith(prefix) and p not in allowed_gitkeeps
    ]
    assert bad == [], f"Tracked files under {prefix}: {bad}"


@pytest.mark.integration
@pytest.mark.hygiene
@pytest.mark.parametrize("suffix", [".xlsx", ".csv", ".env"])
def test_no_sensitive_suffixes_tracked(project_root: Path, suffix: str) -> None:
    tracked = git_tracked_files(project_root)
    if suffix == ".env":
        assert ".env" not in tracked
    else:
        bad = [p for p in tracked if p.endswith(suffix) and "data/" in p]
        assert bad == []


@pytest.mark.unit
@pytest.mark.hygiene
def test_gitignore_protects_marts(gitignore_text: str) -> None:
    assert "data/marts/*" in gitignore_text
    assert "data/processed/*" in gitignore_text
    assert "data/raw/*" in gitignore_text


@pytest.mark.unit
@pytest.mark.hygiene
@pytest.mark.parametrize("script_path", [
    "scripts/db_config.py",
    "scripts/load_to_postgres.py",
    "scripts/validate_data.py",
    "scripts/run_kpi_marts.py",
    "scripts/run_cohort_retention.py",
    "scripts/export_powerbi_marts.py",
])
def test_scripts_no_hardcoded_host_5432(project_root: Path, script_path: str) -> None:
    content = (project_root / script_path).read_text(encoding="utf-8")
    for forbidden in FORBIDDEN_HOST_PORT_PATTERNS:
        assert forbidden not in content
