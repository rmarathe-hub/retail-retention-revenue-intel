from __future__ import annotations

import pytest

from tests.helpers import DB_DIM_CUSTOMER_COUNT, DB_DIM_DATE_COUNT, db_is_reachable


STG_COLUMNS = [
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "invoice_month",
    "unit_price",
    "customer_id",
    "country",
    "source_sheet",
    "is_canceled",
    "is_return",
    "is_missing_customer",
    "is_zero_or_negative_price",
    "is_invalid_invoice_date",
    "line_revenue",
]


@pytest.mark.sql
@pytest.mark.parametrize("fragment", STG_COLUMNS)
def test_schema_stg_transactions_columns(schema_sql_text: str, fragment: str) -> None:
    assert fragment in schema_sql_text


@pytest.mark.sql
@pytest.mark.parametrize(
    "type_fragment",
    [
        "invoice_date TIMESTAMP",
        "quantity INTEGER",
        "unit_price NUMERIC",
        "line_revenue NUMERIC",
        "is_canceled BOOLEAN",
        "is_return BOOLEAN",
    ],
)
def test_schema_has_expected_column_types(schema_sql_text: str, type_fragment: str) -> None:
    assert type_fragment in schema_sql_text


@pytest.mark.sql
@pytest.mark.parametrize("keyword", ["IF NOT EXISTS", "CREATE INDEX IF NOT EXISTS"])
def test_schema_is_idempotent_friendly(schema_sql_text: str, keyword: str) -> None:
    assert keyword in schema_sql_text


@pytest.mark.sql
@pytest.mark.db
def test_db_tables_exist_after_schema(project_root, schema_sql_text: str) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    from sqlalchemy import text

    from tests.conftest import load_module_from_path

    load_module = load_module_from_path(
        "schema_db_check", project_root / "scripts/load_to_postgres.py"
    )
    engine = load_module.create_db_engine()
    tables = [
        "raw_online_retail",
        "stg_transactions",
        "dim_date",
        "dim_customer",
        "mart_monthly_revenue",
        "mart_executive_kpis",
    ]
    with engine.connect() as conn:
        for table in tables:
            exists = conn.execute(
                text(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='public' AND table_name=:t)"
                ),
                {"t": table},
            ).scalar()
            assert exists is True


@pytest.mark.sql
@pytest.mark.db
def test_db_dim_counts_sane(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    from sqlalchemy import text

    from tests.conftest import load_module_from_path

    load_module = load_module_from_path(
        "schema_db_counts", project_root / "scripts/load_to_postgres.py"
    )
    engine = load_module.create_db_engine()
    with engine.connect() as conn:
        dim_customer = conn.execute(text("SELECT COUNT(*) FROM dim_customer")).scalar()
        dim_date = conn.execute(text("SELECT COUNT(*) FROM dim_date")).scalar()
    assert dim_customer == DB_DIM_CUSTOMER_COUNT
    assert dim_date == DB_DIM_DATE_COUNT
