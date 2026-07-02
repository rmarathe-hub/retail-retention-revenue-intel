from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def raw_dir(project_root: Path) -> Path:
    return project_root / "data" / "raw"


@pytest.fixture(scope="session")
def combined_csv_path(raw_dir: Path) -> Path:
    return raw_dir / "online_retail_II_combined.csv"


@pytest.fixture(scope="session")
def profile_json_path(raw_dir: Path) -> Path:
    return raw_dir / "profile_summary.json"


@pytest.fixture(scope="session")
def readme_text(project_root: Path) -> str:
    return (project_root / "README.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def data_dictionary_text(project_root: Path) -> str:
    return (project_root / "docs" / "data_dictionary.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def data_quality_text(project_root: Path) -> str:
    return (project_root / "docs" / "data_quality_report.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def profile_summary(profile_json_path: Path) -> dict:
    if not profile_json_path.exists():
        pytest.skip("profile_summary.json not found locally")
    return json.loads(profile_json_path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def postgres_setup_text(project_root: Path) -> str:
    return (project_root / "docs/postgres_setup.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def business_problem_text(project_root: Path) -> str:
    return (project_root / "docs/business_problem.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def metric_definitions_text(project_root: Path) -> str:
    return (project_root / "docs/metric_definitions.md").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def env_example_text(project_root: Path) -> str:
    return (project_root / ".env.example").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def docker_compose_text(project_root: Path) -> str:
    return (project_root / "docker-compose.yml").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def schema_sql_text(project_root: Path) -> str:
    return (project_root / "sql/01_schema.sql").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def clean_csv_path(project_root: Path) -> Path:
    return project_root / "data/processed/retail_transactions_clean.csv"


@pytest.fixture(scope="session")
def customer_level_csv_path(project_root: Path) -> Path:
    return project_root / "data/processed/retail_transactions_customer_level.csv"


@pytest.fixture(scope="session")
def cleaning_summary_path(project_root: Path) -> Path:
    return project_root / "data/processed/cleaning_summary.json"


@pytest.fixture(scope="session")
def load_summary_path(project_root: Path) -> Path:
    return project_root / "data/processed/load_summary.json"


def load_module_from_path(module_name: str, path: Path):
    scripts_dir = str(path.parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to import module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
