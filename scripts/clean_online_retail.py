"""
Clean Online Retail II data for Day 3 outputs.

Inputs:
  data/raw/online_retail_II_combined.csv

Outputs:
  data/processed/retail_transactions_clean.csv
  data/processed/retail_transactions_customer_level.csv
  data/processed/cleaning_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "online_retail_II_combined.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
CLEAN_PATH = PROCESSED_DIR / "retail_transactions_clean.csv"
CUSTOMER_LEVEL_PATH = PROCESSED_DIR / "retail_transactions_customer_level.csv"
SUMMARY_PATH = PROCESSED_DIR / "cleaning_summary.json"

REQUIRED_COLUMNS = [
    "Invoice",
    "StockCode",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
    "Country",
    "source_sheet",
]

COLUMN_RENAME_MAP = {
    "Invoice": "invoice_no",
    "StockCode": "stock_code",
    "Description": "description",
    "Quantity": "quantity",
    "InvoiceDate": "invoice_date",
    "Price": "unit_price",
    "Customer ID": "customer_id",
    "Country": "country",
    "source_sheet": "source_sheet",
}


def ensure_input_exists(input_path: Path = RAW_PATH) -> None:
    if not input_path.exists():
        raise FileNotFoundError(
            f"{input_path} not found. Run: python scripts/download_or_import_data.py"
        )


def load_raw(input_path: Path = RAW_PATH) -> pd.DataFrame:
    ensure_input_exists(input_path)
    return pd.read_csv(input_path, low_memory=False)


def validate_expected_columns(df: pd.DataFrame) -> None:
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def standardize_country(series: pd.Series) -> pd.Series:
    # Keep canonical country values (e.g., EIRE) while normalizing whitespace.
    cleaned = series.astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
    return cleaned


def clean_transactions(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    validate_expected_columns(df)

    start_rows = len(df)
    duplicate_rows = int(df.duplicated().sum())

    work = df.drop_duplicates().copy()
    work = work.rename(columns=COLUMN_RENAME_MAP)

    # Standardize basic text fields.
    work["invoice_no"] = work["invoice_no"].astype("string").str.strip()
    work["stock_code"] = work["stock_code"].astype("string").str.strip()
    work["description"] = work["description"].astype("string")
    work["description"] = work["description"].fillna("Unknown").str.strip()
    work["country"] = standardize_country(work["country"])

    # Parse date fields.
    work["invoice_date"] = pd.to_datetime(work["invoice_date"], errors="coerce")
    work["invoice_month"] = work["invoice_date"].dt.to_period("M").astype("string")

    # Customer ID as canonical nullable string.
    # Keep missing values as <NA>, but normalize non-null IDs.
    customer_numeric = pd.to_numeric(work["customer_id"], errors="coerce")
    work["customer_id"] = customer_numeric.round(0).astype("Int64").astype("string")

    # Core business flags.
    work["is_canceled"] = work["invoice_no"].fillna("").str.startswith("C")
    work["is_return"] = work["quantity"] < 0
    work["is_missing_customer"] = work["customer_id"].isna()
    work["is_missing_description"] = work["description"].isna() | (
        work["description"].fillna("").str.strip() == ""
    )
    work["is_zero_or_negative_price"] = work["unit_price"] <= 0
    work["is_invalid_invoice_date"] = work["invoice_date"].isna()

    # Financial calculation.
    work["line_revenue"] = work["quantity"] * work["unit_price"]

    # Customer-level analytical dataset.
    customer_level = work[~work["is_missing_customer"]].copy()

    summary = {
        "raw_input_rows": int(start_rows),
        "duplicate_rows_removed": int(duplicate_rows),
        "clean_output_rows": int(len(work)),
        "customer_level_rows": int(len(customer_level)),
        "excluded_rows_missing_customer_id": int(work["is_missing_customer"].sum()),
        "excluded_rows_missing_customer_id_pct_of_clean": round(
            100 * work["is_missing_customer"].mean(), 2
        ),
        "canceled_invoice_lines": int(work["is_canceled"].sum()),
        "return_lines": int(work["is_return"].sum()),
        "zero_or_negative_price_lines": int(work["is_zero_or_negative_price"].sum()),
        "invalid_invoice_dates": int(work["is_invalid_invoice_date"].sum()),
        "missing_description_after_fill": int(
            (work["description"].fillna("").str.strip() == "").sum()
        ),
    }

    return work, customer_level, summary


def save_outputs(
    clean_df: pd.DataFrame,
    customer_df: pd.DataFrame,
    summary: dict,
    clean_path: Path = CLEAN_PATH,
    customer_path: Path = CUSTOMER_LEVEL_PATH,
    summary_path: Path = SUMMARY_PATH,
) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(clean_path, index=False)
    customer_df.to_csv(customer_path, index=False)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    raw_df = load_raw()
    clean_df, customer_df, summary = clean_transactions(raw_df)
    save_outputs(clean_df, customer_df, summary)

    print("=" * 60)
    print("ONLINE RETAIL II — DAY 3 CLEANING SUMMARY")
    print("=" * 60)
    for k, v in summary.items():
        print(f"{k}: {v}")
    print("=" * 60)
    print(f"Saved: {CLEAN_PATH}")
    print(f"Saved: {CUSTOMER_LEVEL_PATH}")
    print(f"Saved: {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
