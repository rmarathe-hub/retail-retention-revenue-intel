"""
Profile raw Online Retail II data and print summary statistics.

Run after download_or_import_data.py:
  python scripts/profile_raw_data.py

Writes: data/raw/profile_summary.json (gitignored with other raw data)
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CSV_PATH = RAW_DIR / "online_retail_II_combined.csv"
SUMMARY_PATH = RAW_DIR / "profile_summary.json"


def load_raw() -> pd.DataFrame:
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"{CSV_PATH} not found. Run: python scripts/download_or_import_data.py"
        )
    return pd.read_csv(CSV_PATH, parse_dates=["InvoiceDate"], low_memory=False)


def profile_dataframe(df: pd.DataFrame) -> dict:
    invoice_col = "Invoice"
    customer_col = "Customer ID"
    desc_col = "Description"
    qty_col = "Quantity"
    price_col = "Price"
    date_col = "InvoiceDate"
    country_col = "Country"

    duplicate_rows = int(df.duplicated().sum())
    missing_customer = int(df[customer_col].isna().sum())
    missing_description = int(df[desc_col].isna().sum())
    negative_qty = int((df[qty_col] < 0).sum())
    zero_qty = int((df[qty_col] == 0).sum())
    negative_price = int((df[price_col] < 0).sum())
    zero_price = int((df[price_col] == 0).sum())
    canceled = int(df[invoice_col].astype(str).str.startswith("C").sum())
    null_country = int(df[country_col].isna().sum())

    df_dates = pd.to_datetime(df[date_col], errors="coerce")
    invalid_dates = int(df_dates.isna().sum())

    line_value = df[qty_col] * df[price_col]
    outlier_threshold = line_value.quantile(0.999)
    outlier_lines = int((line_value > outlier_threshold).sum())

    country_counts = (
        df[country_col].fillna("NULL").value_counts().head(15).to_dict()
    )
    country_counts = {str(k): int(v) for k, v in country_counts.items()}

    summary = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "columns": list(df.columns),
        "date_range": {
            "min": str(df_dates.min()),
            "max": str(df_dates.max()),
        },
        "duplicate_rows": duplicate_rows,
        "missing_customer_id": missing_customer,
        "missing_customer_id_pct": round(100 * missing_customer / len(df), 2),
        "missing_description": missing_description,
        "missing_description_pct": round(100 * missing_description / len(df), 2),
        "negative_quantity": negative_qty,
        "zero_quantity": zero_qty,
        "negative_unit_price": negative_price,
        "zero_unit_price": zero_price,
        "canceled_invoice_lines": canceled,
        "distinct_canceled_invoices": int(
            df.loc[df[invoice_col].astype(str).str.startswith("C"), invoice_col]
            .nunique()
        ),
        "null_country": null_country,
        "invalid_dates": invalid_dates,
        "distinct_invoices": int(df[invoice_col].nunique()),
        "distinct_customers": int(df[customer_col].nunique()),
        "distinct_stock_codes": int(df["StockCode"].nunique()),
        "distinct_countries": int(df[country_col].nunique()),
        "line_value_p99": float(line_value.quantile(0.99)),
        "line_value_p999": float(outlier_threshold),
        "outlier_lines_above_p999": outlier_lines,
        "top_countries": country_counts,
        "source_sheets": df["source_sheet"].value_counts().to_dict()
        if "source_sheet" in df.columns
        else {},
    }
    return summary


def profile(df: pd.DataFrame) -> dict:
    """Backward-compatible alias."""
    return profile_dataframe(df)


def print_summary(summary: dict) -> None:
    print("=" * 60)
    print("ONLINE RETAIL II — RAW PROFILE SUMMARY")
    print("=" * 60)
    for key, value in summary.items():
        if key in ("top_countries", "source_sheets"):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {v}")
        elif key == "columns":
            print(f"\n{key}: {', '.join(value)}")
        else:
            print(f"{key}: {value}")
    print("=" * 60)


def write_profile(summary: dict, output_path: Path = SUMMARY_PATH) -> None:
    output_path.write_text(json.dumps(summary, indent=2))


def main() -> None:
    df = load_raw()
    summary = profile_dataframe(df)
    print_summary(summary)
    write_profile(summary, SUMMARY_PATH)
    print(f"\nWrote {SUMMARY_PATH}")


if __name__ == "__main__":
    main()
