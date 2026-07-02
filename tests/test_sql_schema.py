from __future__ import annotations

from pathlib import Path

import pytest


EXPECTED_TABLES = [
    "raw_online_retail",
    "stg_transactions",
    "dim_date",
    "dim_customer",
    "mart_monthly_revenue",
    "mart_customer_orders",
    "mart_customer_rfm",
    "mart_cohort_retention",
    "mart_revenue_at_risk",
    "mart_product_performance",
    "mart_country_performance",
    "mart_executive_kpis",
]

EXPECTED_INDEXES = [
    "idx_stg_transactions_customer_id",
    "idx_stg_transactions_invoice_date",
    "idx_stg_transactions_invoice_no",
    "idx_stg_transactions_stock_code",
    "idx_stg_transactions_invoice_month",
    "idx_dim_customer_first_purchase_month",
]


@pytest.fixture(scope="module")
def schema_sql(project_root: Path) -> str:
    path = project_root / "sql" / "01_schema.sql"
    assert path.exists(), "sql/01_schema.sql is required for Day 4"
    return path.read_text(encoding="utf-8")


@pytest.mark.unit
def test_schema_file_exists(project_root: Path) -> None:
    assert (project_root / "sql" / "01_schema.sql").exists()


@pytest.mark.unit
@pytest.mark.parametrize("table_name", EXPECTED_TABLES)
def test_schema_defines_expected_tables(schema_sql: str, table_name: str) -> None:
    assert f"CREATE TABLE IF NOT EXISTS {table_name}" in schema_sql


@pytest.mark.unit
@pytest.mark.parametrize("index_name", EXPECTED_INDEXES)
def test_schema_defines_expected_indexes(schema_sql: str, index_name: str) -> None:
    assert f"CREATE INDEX IF NOT EXISTS {index_name}" in schema_sql


@pytest.mark.unit
def test_schema_uses_transaction_wrapper(schema_sql: str) -> None:
    assert "BEGIN;" in schema_sql
    assert "COMMIT;" in schema_sql
