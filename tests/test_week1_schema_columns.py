from __future__ import annotations

import pytest

from tests.helpers import (
    CLEAN_COLUMNS,
    EMPTY_FUTURE_MARTS,
    RAW_COLUMNS,
)


SCHEMA_TABLES = [
    "raw_online_retail",
    "stg_transactions",
    "dim_date",
    "dim_customer",
    "mart_executive_kpis",
    "mart_monthly_revenue",
    "mart_customer_orders",
    "mart_cohort_retention",
    "mart_customer_rfm",
    "mart_revenue_at_risk",
    "mart_product_performance",
    "mart_country_performance",
]

SCHEMA_INDEXES = [
    "idx_stg_transactions_customer_id",
    "idx_stg_transactions_invoice_date",
    "idx_stg_transactions_invoice_no",
    "idx_stg_transactions_stock_code",
]

STG_TYPE_FRAGMENTS = [
    "invoice_date TIMESTAMP",
    "quantity INTEGER",
    "unit_price NUMERIC",
    "line_revenue NUMERIC",
    "is_canceled BOOLEAN",
    "is_return BOOLEAN",
]


@pytest.mark.sql
@pytest.mark.parametrize("table", SCHEMA_TABLES)
def test_schema_creates_table(schema_sql_text: str, table: str) -> None:
    assert f"CREATE TABLE IF NOT EXISTS {table}" in schema_sql_text


@pytest.mark.sql
@pytest.mark.parametrize("index_name", SCHEMA_INDEXES)
def test_schema_creates_indexes(schema_sql_text: str, index_name: str) -> None:
    assert index_name in schema_sql_text


@pytest.mark.sql
@pytest.mark.parametrize("type_fragment", STG_TYPE_FRAGMENTS)
def test_schema_stg_column_types(schema_sql_text: str, type_fragment: str) -> None:
    assert type_fragment in schema_sql_text


@pytest.mark.sql
@pytest.mark.parametrize("column", RAW_COLUMNS)
def test_raw_columns_documented_in_dictionary(data_dictionary_text: str, column: str) -> None:
    assert column in data_dictionary_text or column.replace(" ", "") in data_dictionary_text


@pytest.mark.sql
@pytest.mark.parametrize("column", CLEAN_COLUMNS)
def test_clean_columns_documented_in_dictionary(data_dictionary_text: str, column: str) -> None:
    aliases = {
        "stock_code": "StockCode",
        "description": "Description",
        "invoice_no": "Invoice",
        "unit_price": "Price",
        "customer_id": "Customer ID",
        "is_missing_description": "missing",
    }
    needle = aliases.get(column, column)
    assert needle in data_dictionary_text


@pytest.mark.sql
@pytest.mark.parametrize("mart", EMPTY_FUTURE_MARTS)
def test_schema_has_future_mart_placeholder(schema_sql_text: str, mart: str) -> None:
    assert f"CREATE TABLE IF NOT EXISTS {mart}" in schema_sql_text
