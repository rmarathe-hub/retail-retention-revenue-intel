from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.mark.unit
@pytest.mark.parametrize(
    "required_pattern",
    [
        "data/raw/*",
        "data/processed/*",
        ".env",
        ".venv/",
        "__pycache__/",
        "*.py[cod]",
        ".DS_Store",
        ".pytest_cache/",
    ],
)
def test_gitignore_has_required_patterns(project_root: Path, required_pattern: str) -> None:
    gitignore_text = (project_root / ".gitignore").read_text(encoding="utf-8")
    assert required_pattern in gitignore_text


def _git_tracked_files(project_root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        pytest.skip("git ls-files unavailable")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


@pytest.mark.integration
@pytest.mark.hygiene
def test_no_raw_or_processed_data_tracked(project_root: Path) -> None:
    tracked = _git_tracked_files(project_root)
    forbidden_prefixes = ("data/raw/", "data/processed/", ".venv/")
    allowed = {"data/raw/.gitkeep", "data/processed/.gitkeep"}
    bad = [
        path
        for path in tracked
        if path.startswith(forbidden_prefixes) and path not in allowed
    ]
    assert bad == []


@pytest.mark.integration
@pytest.mark.hygiene
def test_no_env_file_tracked(project_root: Path) -> None:
    tracked = _git_tracked_files(project_root)
    assert ".env" not in tracked


@pytest.mark.integration
@pytest.mark.hygiene
def test_no_pycache_or_pyc_tracked(project_root: Path) -> None:
    tracked = _git_tracked_files(project_root)
    bad = [p for p in tracked if "__pycache__" in p or p.endswith(".pyc")]
    assert bad == []


@pytest.mark.integration
@pytest.mark.hygiene
def test_no_ds_store_tracked(project_root: Path) -> None:
    tracked = _git_tracked_files(project_root)
    bad = [p for p in tracked if p.endswith(".DS_Store")]
    assert bad == []


@pytest.mark.integration
@pytest.mark.hygiene
def test_no_raw_xlsx_or_csv_tracked(project_root: Path) -> None:
    tracked = _git_tracked_files(project_root)
    bad = [
        path
        for path in tracked
        if (path.startswith("data/raw/") or path.startswith("data/processed/"))
        and (path.endswith(".xlsx") or path.endswith(".csv"))
    ]
    assert bad == []


@pytest.mark.integration
@pytest.mark.hygiene
def test_no_obvious_secret_files_tracked(project_root: Path) -> None:
    tracked = _git_tracked_files(project_root)
    suspicious = [
        path
        for path in tracked
        if any(
            token in path.lower()
            for token in ("secret", "credential", "private_key", "id_rsa", ".pem")
        )
        and not path.endswith("tests/test_secrets_hygiene.py")
    ]
    assert suspicious == []
