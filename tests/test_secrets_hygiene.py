from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.helpers import DB_PASSWORD, DB_USER, git_tracked_files


ALLOWED_DEMO_SECRETS = {DB_USER, DB_PASSWORD, "retail_analytics", "retail_pass"}


@pytest.mark.hygiene
def test_tracked_files_exclude_pycache_and_ds_store(project_root: Path) -> None:
    tracked = git_tracked_files(project_root)
    bad = [p for p in tracked if "__pycache__" in p or p.endswith(".DS_Store")]
    assert bad == []


@pytest.mark.hygiene
def test_tracked_files_exclude_venv(project_root: Path) -> None:
    tracked = git_tracked_files(project_root)
    bad = [p for p in tracked if p.startswith(".venv/") or "/.venv/" in p]
    assert bad == []


@pytest.mark.hygiene
@pytest.mark.parametrize(
    "pattern",
    [
        r"sk-[A-Za-z0-9]{10,}",
        r"AKIA[0-9A-Z]{16}",
        r"-----BEGIN (RSA |OPENSSH )?PRIVATE KEY-----",
    ],
)
def test_tracked_text_files_have_no_obvious_secrets(project_root: Path, pattern: str) -> None:
    tracked = git_tracked_files(project_root)
    text_files = [
        project_root / p
        for p in tracked
        if p.endswith((".md", ".py", ".txt", ".ini", ".yml", ".example", ".sql"))
    ]
    regex = re.compile(pattern)
    for path in text_files:
        content = path.read_text(encoding="utf-8", errors="ignore")
        assert not regex.search(content), f"Suspicious secret pattern in {path}"


@pytest.mark.hygiene
def test_env_file_not_tracked(project_root: Path) -> None:
    tracked = git_tracked_files(project_root)
    assert ".env" not in tracked
