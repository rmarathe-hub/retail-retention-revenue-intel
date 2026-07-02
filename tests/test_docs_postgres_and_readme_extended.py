from __future__ import annotations

import pytest

from tests.helpers import DB_HOST_PORT, DB_NAME, DB_USER, PROJECT_NAME


@pytest.mark.docs
@pytest.mark.parametrize(
    "required",
    [
        "Docker Postgres",
        "5433",
        "5433:5432",
        "cp .env.example .env",
        "docker compose up -d",
        "pg_isready",
        DB_USER,
        DB_NAME,
        "python scripts/load_to_postgres.py",
        "python scripts/validate_data.py",
        'pytest -q -m "db"',
        ".env is gitignored",
    ],
)
def test_postgres_setup_doc_required_content(postgres_setup_text: str, required: str) -> None:
    assert required in postgres_setup_text


@pytest.mark.docs
def test_postgres_setup_doc_explains_internal_5432(postgres_setup_text: str) -> None:
    assert "5432" in postgres_setup_text
    assert "5433" in postgres_setup_text


@pytest.mark.docs
@pytest.mark.parametrize(
    "required",
    [
        PROJECT_NAME,
        "1,067,371",
        "UCI Online Retail II",
        "Python",
        "SQL",
        "Postgres",
        "Power BI",
        "5433",
        "docker compose up -d",
        "python scripts/download_or_import_data.py",
        "python scripts/profile_raw_data.py",
        "python scripts/clean_online_retail.py",
        "python scripts/load_to_postgres.py",
        "python scripts/validate_data.py",
        "pip install -r requirements.txt",
        ".venv",
        "gitignored",
        "Week 1 Day 4",
        "ecommerce-retention-analytics-platform",
    ],
)
def test_readme_extended_required_content(readme_text: str, required: str) -> None:
    assert required in readme_text


@pytest.mark.docs
def test_readme_power_bi_not_complete(readme_text: str) -> None:
    assert "Screenshots coming Week 2" in readme_text or "coming Week 2" in readme_text


@pytest.mark.docs
def test_readme_mentions_port_5433_intentional(readme_text: str) -> None:
    lowered = readme_text.lower()
    assert "5433" in readme_text
    assert "postgres_setup.md" in readme_text or "docker" in lowered
