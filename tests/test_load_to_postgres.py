from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from tests.conftest import load_module_from_path


@pytest.fixture(scope="module")
def load_module(project_root: Path):
    return load_module_from_path(
        "load_postgres_module", project_root / "scripts/load_to_postgres.py"
    )


@pytest.fixture(scope="module")
def db_config_module(project_root: Path):
    return load_module_from_path("db_config_module", project_root / "scripts/db_config.py")


@pytest.mark.unit
def test_get_database_url_from_database_url_env(db_config_module) -> None:
    with patch.dict(
        os.environ,
        {"DATABASE_URL": "postgresql://user:pass@localhost:5433/testdb"},
        clear=False,
    ):
        assert (
            db_config_module.get_database_url()
            == "postgresql+psycopg2://user:pass@localhost:5433/testdb"
        )


@pytest.mark.unit
def test_get_database_url_from_components_defaults_to_port_5433(db_config_module) -> None:
    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": "",
            "POSTGRES_PASSWORD": "secret",
        },
        clear=True,
    ):
        url = db_config_module.get_database_url()
        assert url == "postgresql+psycopg2://retail_user:secret@localhost:5433/retail_analytics"


@pytest.mark.unit
def test_get_database_url_from_components_explicit_port(db_config_module) -> None:
    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": "",
            "POSTGRES_HOST": "dbhost",
            "POSTGRES_PORT": "5433",
            "POSTGRES_DB": "retail",
            "POSTGRES_USER": "app",
            "POSTGRES_PASSWORD": "secret",
        },
        clear=False,
    ):
        url = db_config_module.get_database_url()
        assert url == "postgresql+psycopg2://app:secret@dbhost:5433/retail"


@pytest.mark.unit
def test_get_database_url_requires_password(db_config_module) -> None:
    with patch.dict(
        os.environ,
        {
            "DATABASE_URL": "",
            "POSTGRES_PASSWORD": "",
        },
        clear=False,
    ):
        with pytest.raises(ValueError, match="POSTGRES_PASSWORD"):
            db_config_module.get_database_url()


@pytest.mark.unit
def test_env_example_uses_host_port_5433_only(project_root: Path) -> None:
    env_example = (project_root / ".env.example").read_text(encoding="utf-8")
    assert "POSTGRES_PORT=5433" in env_example
    assert "localhost:5433" in env_example
    assert "POSTGRES_PORT=5432" not in env_example
    assert "@localhost:5432/" not in env_example


@pytest.mark.docs
def test_postgres_setup_doc_mentions_host_port_5433(project_root: Path) -> None:
    doc = (project_root / "docs/postgres_setup.md").read_text(encoding="utf-8")
    assert "5433" in doc
    assert "5433:5432" in doc
    assert "localhost:5433" in doc


@pytest.mark.unit
def test_prepare_raw_dataframe_maps_columns(project_root: Path, load_module, tmp_path: Path) -> None:
    raw_csv = tmp_path / "raw.csv"
    pd.DataFrame(
        {
            "Invoice": ["1001"],
            "StockCode": ["A1"],
            "Description": ["Item"],
            "Quantity": [1],
            "InvoiceDate": ["2010-01-01 10:00:00"],
            "Price": [2.5],
            "Customer ID": [12345],
            "Country": ["United Kingdom"],
            "source_sheet": ["Year 2009-2010"],
        }
    ).to_csv(raw_csv, index=False)

    out = load_module.prepare_raw_dataframe(raw_csv)
    assert list(out.columns) == [
        "invoice",
        "stock_code",
        "description",
        "quantity",
        "invoice_date",
        "price",
        "customer_id",
        "country",
        "source_sheet",
    ]


@pytest.mark.unit
def test_prepare_stg_dataframe_casts_bools(project_root: Path, load_module, tmp_path: Path) -> None:
    stg_csv = tmp_path / "stg.csv"
    pd.DataFrame(
        {
            "invoice_no": ["1001"],
            "stock_code": ["A1"],
            "description": ["Item"],
            "quantity": [1],
            "invoice_date": ["2010-01-01 10:00:00"],
            "invoice_month": ["2010-01"],
            "unit_price": [2.5],
            "customer_id": ["12345"],
            "country": ["United Kingdom"],
            "source_sheet": ["Year 2009-2010"],
            "is_canceled": [False],
            "is_return": [False],
            "is_missing_customer": [False],
            "is_missing_description": [False],
            "is_zero_or_negative_price": [False],
            "is_invalid_invoice_date": [False],
            "line_revenue": [2.5],
        }
    ).to_csv(stg_csv, index=False)

    out = load_module.prepare_stg_dataframe(stg_csv)
    assert out["is_canceled"].dtype == bool


@pytest.mark.unit
def test_validate_load_counts_expected_values(project_root: Path, load_module) -> None:
    expected_dim_date = (
        pd.Timestamp(load_module.DATE_RANGE_END) - pd.Timestamp(load_module.DATE_RANGE_START)
    ).days + 1
    counts = {
        "raw_online_retail": 1_067_371,
        "stg_transactions": 1_055_238,
        "dim_customer": 5_942,
        "dim_date": expected_dim_date,
    }
    checks = load_module.validate_load_counts(counts)
    assert checks["raw_online_retail"] == "ok"
    assert checks["stg_transactions"] == "ok"
    assert checks["dim_customer"] == "ok"
    assert checks["dim_date"] == "ok"


@pytest.mark.db
def test_run_load_pipeline_integration(project_root: Path, load_module) -> None:
    if not (project_root / ".env").exists():
        pytest.skip(".env not configured for PostgreSQL db test")

    try:
        engine = load_module.create_db_engine()
        with engine.connect() as conn:
            conn.execute(load_module.text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"PostgreSQL unavailable on host port 5433: {exc}")

    summary = load_module.run_load_pipeline(engine, truncate=True)
    assert summary["raw_rows_loaded"] == 1_067_371
    assert summary["stg_rows_loaded"] == 1_055_238
    assert summary["validation"]["dim_customer"] == "ok"


@pytest.mark.db
def test_validate_data_script_integration(project_root: Path) -> None:
    if not (project_root / ".env").exists():
        pytest.skip(".env not configured for PostgreSQL db test")

    validate_module = load_module_from_path(
        "validate_module", project_root / "scripts/validate_data.py"
    )

    try:
        summary = validate_module.run_validation()
    except Exception as exc:  # pragma: no cover - environment dependent
        pytest.skip(f"PostgreSQL unavailable on host port 5433: {exc}")

    assert summary["connection"] == "ok"
    assert "validation" in summary
