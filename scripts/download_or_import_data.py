"""
Download or import UCI Online Retail II dataset.

Dataset: Online Retail II
Source: UCI Machine Learning Repository
URL: https://archive.ics.uci.edu/dataset/502/online+retail+ii

Output:
  data/raw/online_retail_II.xlsx
  data/raw/online_retail_II_combined.csv  (both Excel sheets stacked)
"""

from __future__ import annotations

import sys
import urllib.request
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
DOWNLOAD_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/00502/online_retail_II.xlsx"
)
XLSX_PATH = RAW_DIR / "online_retail_II.xlsx"
CSV_PATH = RAW_DIR / "online_retail_II_combined.csv"


def download_raw_data(force: bool = False) -> Path:
    """Download the UCI xlsx file if missing or force=True."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    if XLSX_PATH.exists() and not force:
        print(f"Already exists: {XLSX_PATH}")
        return XLSX_PATH

    print(f"Downloading from {DOWNLOAD_URL} ...")
    urllib.request.urlretrieve(DOWNLOAD_URL, XLSX_PATH)
    print(f"Saved: {XLSX_PATH} ({XLSX_PATH.stat().st_size / 1_048_576:.1f} MB)")
    return XLSX_PATH


EXPECTED_COLUMNS = [
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


def combine_sheets_to_csv(xlsx_path: Path = XLSX_PATH, output_csv: Path = CSV_PATH) -> Path:
    """Read all Excel sheets and write one combined CSV for easier profiling."""
    print(f"Reading Excel sheets from {xlsx_path} ...")
    sheets = pd.read_excel(xlsx_path, sheet_name=None)
    if not sheets:
        raise ValueError(f"No sheets found in {xlsx_path}")
    sheet_names = list(sheets.keys())
    print(f"Found sheets: {sheet_names}")

    frames = []
    for sheet_name, df in sheets.items():
        df = df.copy()
        df["source_sheet"] = sheet_name
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)
    combined.to_csv(output_csv, index=False)
    print(f"Combined rows: {len(combined):,}")
    print(f"Saved: {output_csv}")
    return output_csv


def main() -> None:
    force = "--force" in sys.argv
    xlsx_path = download_raw_data(force=force)
    combine_sheets_to_csv(xlsx_path)


if __name__ == "__main__":
    main()
