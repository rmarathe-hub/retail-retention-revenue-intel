from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import CI_PYTEST_MARKERS, CI_WORKFLOW_PATH, GITHUB_REPO, PROJECT_NAME


@pytest.mark.unit
def test_ci_workflow_file_exists(project_root: Path) -> None:
    assert (project_root / CI_WORKFLOW_PATH).exists()


@pytest.mark.unit
def test_ci_workflow_runs_pytest_with_ci_markers(project_root: Path) -> None:
    text = (project_root / CI_WORKFLOW_PATH).read_text(encoding="utf-8")
    assert "pytest" in text
    assert CI_PYTEST_MARKERS in text
    assert "actions/checkout@v4" in text
    assert "actions/setup-python@v5" in text


@pytest.mark.docs
def test_ci_doc_exists_and_documents_markers(project_root: Path) -> None:
    text = (project_root / "docs/ci.md").read_text(encoding="utf-8")
    assert CI_WORKFLOW_PATH in text
    assert CI_PYTEST_MARKERS in text
    assert "ubuntu-latest" in text


@pytest.mark.docs
def test_readme_has_ci_badge(readme_text: str) -> None:
    assert f"github.com/rmarathe-hub/{GITHUB_REPO}/actions/workflows/ci.yml/badge.svg" in readme_text


@pytest.mark.docs
def test_readme_links_ci_doc(readme_text: str) -> None:
    assert "docs/ci.md" in readme_text
    assert "GitHub Actions" in readme_text


@pytest.mark.integration
def test_day14_completion_contract(project_root: Path, readme_text: str) -> None:
    assert PROJECT_NAME in readme_text
    assert (project_root / CI_WORKFLOW_PATH).exists()
    assert (project_root / "docs/ci.md").exists()
    assert "pytest" in readme_text.lower()
