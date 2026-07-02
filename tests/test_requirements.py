from __future__ import annotations

from pathlib import Path

import pytest


REQUIRED_PACKAGES = {
    "pandas",
    "numpy",
    "psycopg2-binary",
    "python-dotenv",
    "sqlalchemy",
    "openpyxl",
    "pytest",
}


def _parse_package_name(requirement_line: str) -> str:
    line = requirement_line.strip()
    for splitter in ("==", ">=", "<=", "~=", "!=", ">", "<"):
        if splitter in line:
            return line.split(splitter, 1)[0].strip().lower()
    return line.lower()


@pytest.mark.unit
def test_requirements_contains_expected_packages(project_root: Path) -> None:
    req_file = project_root / "requirements.txt"
    lines = [line.strip() for line in req_file.read_text(encoding="utf-8").splitlines()]
    lines = [line for line in lines if line and not line.startswith("#")]
    package_names = {_parse_package_name(line) for line in lines}
    missing = REQUIRED_PACKAGES.difference(package_names)
    assert not missing, f"Missing packages: {sorted(missing)}"


@pytest.mark.unit
def test_no_duplicate_requirements(project_root: Path) -> None:
    req_file = project_root / "requirements.txt"
    lines = [line.strip() for line in req_file.read_text(encoding="utf-8").splitlines()]
    lines = [line for line in lines if line and not line.startswith("#")]
    names = [_parse_package_name(line) for line in lines]
    assert len(names) == len(set(names)), "Duplicate package names in requirements.txt"

