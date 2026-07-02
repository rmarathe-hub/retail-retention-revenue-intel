from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from tests.conftest import load_module_from_path


def _tiny_raw_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["10001", "A1", "Item A", 2, "2010-01-01 10:00:00", 2.0, 11111, "United Kingdom", "S1"],
            ["C10002", "A2", None, -1, "2010-01-02 10:00:00", 0.0, None, "France", "S1"],
            ["10003", "A3", "Item C", 1, "2010-01-03 10:00:00", 1.5, 22222, "Germany", "S2"],
        ],
        columns=[
            "Invoice",
            "StockCode",
            "Description",
            "Quantity",
            "InvoiceDate",
            "Price",
            "Customer ID",
            "Country",
            "source_sheet",
        ],
    )


def _build_tiny_xlsx(path: Path) -> None:
    cols = [
        "Invoice",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "Price",
        "Customer ID",
        "Country",
    ]
    df1 = pd.DataFrame(
        [["10001", "A1", "Item A", 1, "2010-01-01 10:00:00", 1.0, 11111, "UK"]],
        columns=cols,
    )
    df2 = pd.DataFrame(
        [["20001", "B1", "Item B", 2, "2011-01-01 10:00:00", 2.0, 22222, "DE"]],
        columns=cols,
    )
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df1.to_excel(writer, index=False, sheet_name="Year 2009-2010")
        df2.to_excel(writer, index=False, sheet_name="Year 2010-2011")


@pytest.mark.smoke
def test_smoke_download_profile_clean_pipeline(project_root: Path, tmp_path: Path) -> None:
    download = load_module_from_path(
        "smoke_download", project_root / "scripts/download_or_import_data.py"
    )
    profile = load_module_from_path(
        "smoke_profile", project_root / "scripts/profile_raw_data.py"
    )
    clean = load_module_from_path(
        "smoke_clean", project_root / "scripts/clean_online_retail.py"
    )

    xlsx = tmp_path / "tiny.xlsx"
    combined = tmp_path / "combined.csv"
    profile_json = tmp_path / "profile.json"
    clean_csv = tmp_path / "clean.csv"
    customer_csv = tmp_path / "customer.csv"
    summary_json = tmp_path / "summary.json"

    _build_tiny_xlsx(xlsx)
    download.combine_sheets_to_csv(xlsx, combined)
    combined_df = pd.read_csv(combined)
    assert len(combined_df) == 2

    summary = profile.profile_dataframe(combined_df)
    profile.write_profile(summary, profile_json)
    assert json.loads(profile_json.read_text())["row_count"] == 2

    clean_df, customer_df, clean_summary = clean.clean_transactions(combined_df)
    clean.save_outputs(clean_df, customer_df, clean_summary, clean_csv, customer_csv, summary_json)

    assert clean_csv.exists()
    assert customer_csv.exists()
    assert summary_json.exists()
    assert clean_summary["clean_output_rows"] == len(clean_df)


@pytest.mark.smoke
def test_smoke_no_db_required_for_core_pipeline(project_root: Path, tmp_path: Path) -> None:
    clean = load_module_from_path(
        "smoke_clean2", project_root / "scripts/clean_online_retail.py"
    )
    clean_df, customer_df, summary = clean.clean_transactions(_tiny_raw_df())
    assert summary["clean_output_rows"] == 3
    assert len(customer_df) == 2
