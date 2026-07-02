from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


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


def _load_or_skip(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        pytest.skip("Raw combined CSV not found locally")
    return pd.read_csv(csv_path, low_memory=False, parse_dates=["InvoiceDate"])


@pytest.mark.data
@pytest.mark.slow
def test_raw_data_columns_and_rowcount(combined_csv_path: Path) -> None:
    df = _load_or_skip(combined_csv_path)
    assert len(df) == 1_067_371
    assert list(df.columns) == EXPECTED_COLUMNS


@pytest.mark.data
@pytest.mark.slow
def test_raw_data_date_range(combined_csv_path: Path) -> None:
    df = _load_or_skip(combined_csv_path)
    min_date = df["InvoiceDate"].min()
    max_date = df["InvoiceDate"].max()
    assert str(min_date).startswith("2009-12-01")
    assert str(max_date).startswith("2011-12-09")


@pytest.mark.data
@pytest.mark.slow
def test_raw_data_source_sheets(combined_csv_path: Path) -> None:
    df = _load_or_skip(combined_csv_path)
    values = set(df["source_sheet"].dropna().unique())
    assert values == {"Year 2009-2010", "Year 2010-2011"}


@pytest.mark.data
@pytest.mark.slow
def test_raw_data_distribution_contracts(combined_csv_path: Path) -> None:
    df = _load_or_skip(combined_csv_path)
    # Exact values from current Day-2 profile
    assert int(df["Customer ID"].isna().sum()) == 243_007
    assert int(df["Invoice"].astype(str).str.startswith("C").sum()) == 19_494
    assert int((df["Quantity"] < 0).sum()) == 22_950
    assert int(df.duplicated().sum()) == 12_133
    assert int((df["Price"] == 0).sum()) == 6_202
    assert int((df["Price"] < 0).sum()) == 5
    assert int(df["Customer ID"].nunique()) == 5_942


@pytest.mark.data
@pytest.mark.slow
def test_raw_data_uk_share_approx(combined_csv_path: Path) -> None:
    df = _load_or_skip(combined_csv_path)
    uk_share = (df["Country"] == "United Kingdom").mean()
    assert 0.915 <= uk_share <= 0.925

