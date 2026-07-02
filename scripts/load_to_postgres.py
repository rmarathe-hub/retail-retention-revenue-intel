"""
Load raw and cleaned retail data into PostgreSQL.

Prerequisites:
  1. Docker Postgres running on host port 5433 (see docs/postgres_setup.md)
  2. Day 2 raw CSV and Day 3 processed CSV generated
  3. .env configured from .env.example

Usage:
  python scripts/load_to_postgres.py
  python scripts/load_to_postgres.py --schema-only
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from db_config import create_db_engine, get_database_url

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "sql"
SCHEMA_PATH = SQL_DIR / "01_schema.sql"

RAW_CSV_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II_combined.csv"
STG_CSV_PATH = PROJECT_ROOT / "data" / "processed" / "retail_transactions_clean.csv"
LOAD_SUMMARY_PATH = PROJECT_ROOT / "data" / "processed" / "load_summary.json"

RAW_COLUMN_MAP = {
    "Invoice": "invoice",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "price",
    "Customer ID": "customer_id",
    "Country": "country",
    "source_sheet": "source_sheet",
}

DATE_RANGE_START = "2009-12-01"
DATE_RANGE_END = "2011-12-09"


def read_sql_file(path: Path = SCHEMA_PATH) -> str:
    if not path.exists():
        raise FileNotFoundError(f"SQL file not found: {path}")
    return path.read_text(encoding="utf-8")


def apply_schema(engine: Engine, schema_path: Path = SCHEMA_PATH) -> None:
    sql = read_sql_file(schema_path)
    with engine.begin() as conn:
        conn.execute(text(sql))


def truncate_load_tables(engine: Engine) -> None:
    tables = [
        "raw_online_retail",
        "stg_transactions",
        "dim_date",
        "dim_customer",
    ]
    with engine.begin() as conn:
        for table in tables:
            conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))


def _load_csv_in_chunks(
    engine: Engine,
    df: pd.DataFrame,
    table_name: str,
    chunksize: int = 50_000,
) -> int:
    rows_loaded = 0
    for start in range(0, len(df), chunksize):
        chunk = df.iloc[start : start + chunksize]
        chunk.to_sql(table_name, engine, if_exists="append", index=False, method="multi")
        rows_loaded += len(chunk)
    return rows_loaded


def prepare_raw_dataframe(csv_path: Path = RAW_CSV_PATH) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} not found. Run: python scripts/download_or_import_data.py"
        )

    df = pd.read_csv(csv_path, low_memory=False)
    missing = [col for col in RAW_COLUMN_MAP if col not in df.columns]
    if missing:
        raise ValueError(f"Raw CSV missing columns: {missing}")

    out = df[list(RAW_COLUMN_MAP.keys())].rename(columns=RAW_COLUMN_MAP)
    out["invoice_date"] = pd.to_datetime(out["invoice_date"], errors="coerce")
    out["customer_id"] = out["customer_id"].astype("string")
    return out


def prepare_stg_dataframe(csv_path: Path = STG_CSV_PATH) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} not found. Run: python scripts/clean_online_retail.py"
        )

    df = pd.read_csv(csv_path, low_memory=False)
    if "invoice_date" in df.columns:
        df["invoice_date"] = pd.to_datetime(df["invoice_date"], errors="coerce")

    bool_cols = [
        "is_canceled",
        "is_return",
        "is_missing_customer",
        "is_missing_description",
        "is_zero_or_negative_price",
        "is_invalid_invoice_date",
    ]
    for col in bool_cols:
        if col in df.columns:
            df[col] = df[col].astype(bool)

    return df


def load_raw_online_retail(engine: Engine, csv_path: Path = RAW_CSV_PATH) -> int:
    df = prepare_raw_dataframe(csv_path)
    return _load_csv_in_chunks(engine, df, "raw_online_retail")


def load_stg_transactions(engine: Engine, csv_path: Path = STG_CSV_PATH) -> int:
    df = prepare_stg_dataframe(csv_path)
    return _load_csv_in_chunks(engine, df, "stg_transactions")


def populate_dim_date(engine: Engine) -> int:
    sql = text(
        """
        INSERT INTO dim_date (date_key, full_date, year, month, month_name, quarter, year_month)
        SELECT
            CAST(TO_CHAR(d::date, 'YYYYMMDD') AS INTEGER) AS date_key,
            d::date AS full_date,
            EXTRACT(YEAR FROM d)::INTEGER AS year,
            EXTRACT(MONTH FROM d)::INTEGER AS month,
            TO_CHAR(d::date, 'Month') AS month_name,
            EXTRACT(QUARTER FROM d)::INTEGER AS quarter,
            TO_CHAR(d::date, 'YYYY-MM') AS year_month
        FROM generate_series(CAST(:start_date AS date), CAST(:end_date AS date), interval '1 day') AS d
        ON CONFLICT (date_key) DO NOTHING
        """
    )
    with engine.begin() as conn:
        result = conn.execute(
            sql, {"start_date": DATE_RANGE_START, "end_date": DATE_RANGE_END}
        )
        return result.rowcount or 0


def populate_dim_customer(engine: Engine) -> int:
    sql = text(
        """
        INSERT INTO dim_customer (
            customer_id,
            first_purchase_date,
            first_purchase_month,
            primary_country,
            total_orders,
            total_revenue,
            is_repeat_customer
        )
        SELECT
            customer_id,
            MIN(invoice_date::date) AS first_purchase_date,
            TO_CHAR(MIN(invoice_date), 'YYYY-MM') AS first_purchase_month,
            MODE() WITHIN GROUP (ORDER BY country) AS primary_country,
            COUNT(DISTINCT CASE WHEN NOT is_canceled THEN invoice_no END) AS total_orders,
            COALESCE(SUM(line_revenue), 0) AS total_revenue,
            COUNT(DISTINCT CASE WHEN NOT is_canceled THEN invoice_no END) >= 2 AS is_repeat_customer
        FROM stg_transactions
        WHERE NOT is_missing_customer
        GROUP BY customer_id
        ON CONFLICT (customer_id) DO UPDATE SET
            first_purchase_date = EXCLUDED.first_purchase_date,
            first_purchase_month = EXCLUDED.first_purchase_month,
            primary_country = EXCLUDED.primary_country,
            total_orders = EXCLUDED.total_orders,
            total_revenue = EXCLUDED.total_revenue,
            is_repeat_customer = EXCLUDED.is_repeat_customer,
            loaded_at = NOW()
        """
    )
    with engine.begin() as conn:
        result = conn.execute(sql)
        return result.rowcount or 0


def get_table_row_counts(engine: Engine) -> dict[str, int]:
    tables = [
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
    counts: dict[str, int] = {}
    with engine.connect() as conn:
        for table in tables:
            value = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            counts[table] = int(value or 0)
    return counts


def validate_load_counts(counts: dict[str, int]) -> dict[str, str]:
    checks: dict[str, str] = {}

    if counts.get("raw_online_retail", 0) == 1_067_371:
        checks["raw_online_retail"] = "ok"
    else:
        checks["raw_online_retail"] = f"unexpected: {counts.get('raw_online_retail', 0)}"

    if counts.get("stg_transactions", 0) == 1_055_238:
        checks["stg_transactions"] = "ok"
    else:
        checks["stg_transactions"] = f"unexpected: {counts.get('stg_transactions', 0)}"

    if counts.get("dim_customer", 0) == 5_942:
        checks["dim_customer"] = "ok"
    else:
        checks["dim_customer"] = f"unexpected: {counts.get('dim_customer', 0)}"

    expected_dim_date = (
        pd.Timestamp(DATE_RANGE_END) - pd.Timestamp(DATE_RANGE_START)
    ).days + 1
    if counts.get("dim_date", 0) == expected_dim_date:
        checks["dim_date"] = "ok"
    else:
        checks["dim_date"] = f"unexpected: {counts.get('dim_date', 0)}"

    return checks


def save_load_summary(summary: dict, output_path: Path = LOAD_SUMMARY_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def run_load_pipeline(
    engine: Engine,
    raw_csv: Path = RAW_CSV_PATH,
    stg_csv: Path = STG_CSV_PATH,
    schema_path: Path = SCHEMA_PATH,
    truncate: bool = True,
) -> dict:
    apply_schema(engine, schema_path)

    if truncate:
        truncate_load_tables(engine)

    raw_rows = load_raw_online_retail(engine, raw_csv)
    stg_rows = load_stg_transactions(engine, stg_csv)
    dim_date_rows = populate_dim_date(engine)
    dim_customer_rows = populate_dim_customer(engine)
    counts = get_table_row_counts(engine)
    validation = validate_load_counts(counts)

    summary = {
        "raw_rows_loaded": raw_rows,
        "stg_rows_loaded": stg_rows,
        "dim_date_rows_inserted": dim_date_rows,
        "dim_customer_rows_upserted": dim_customer_rows,
        "table_counts": counts,
        "validation": validation,
    }
    save_load_summary(summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load retail data into PostgreSQL")
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Apply schema SQL only; do not load data",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    engine = create_db_engine()

    if args.schema_only:
        apply_schema(engine)
        print(f"Schema applied from {SCHEMA_PATH}")
        return

    summary = run_load_pipeline(engine)

    print("=" * 60)
    print("POSTGRES LOAD SUMMARY")
    print("=" * 60)
    for key, value in summary.items():
        print(f"{key}: {value}")
    print("=" * 60)
    print(f"Saved: {LOAD_SUMMARY_PATH}")


if __name__ == "__main__":
    main()
