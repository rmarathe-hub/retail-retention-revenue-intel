from __future__ import annotations

import json

import pandas as pd
import pytest

from tests.helpers import (
    CLEAN_CANCELED_LINES,
    CLEAN_COLUMNS,
    CLEAN_OUTPUT_ROWS,
    CLEAN_RETURN_LINES,
    CLEAN_ZERO_OR_NEG_PRICE,
    CUSTOMER_LEVEL_ROWS,
    EXCLUDED_MISSING_CUSTOMER,
    skip_if_missing,
)


@pytest.fixture(scope="module")
def clean_df(clean_csv_path):
    skip_if_missing(clean_csv_path, "clean CSV not found locally")
    return pd.read_csv(clean_csv_path, low_memory=False, parse_dates=["invoice_date"])


@pytest.fixture(scope="module")
def customer_df(customer_level_csv_path):
    skip_if_missing(customer_level_csv_path, "customer-level CSV not found locally")
    return pd.read_csv(customer_level_csv_path, low_memory=False, parse_dates=["invoice_date"])


@pytest.fixture(scope="module")
def cleaning_summary(cleaning_summary_path):
    skip_if_missing(cleaning_summary_path, "cleaning_summary.json not found locally")
    return json.loads(cleaning_summary_path.read_text(encoding="utf-8"))


@pytest.mark.data
@pytest.mark.slow
def test_clean_csv_row_count(clean_df) -> None:
    assert len(clean_df) == CLEAN_OUTPUT_ROWS


@pytest.mark.data
@pytest.mark.slow
@pytest.mark.parametrize("column", CLEAN_COLUMNS)
def test_clean_csv_has_required_columns(clean_df, column: str) -> None:
    assert column in clean_df.columns


@pytest.mark.data
@pytest.mark.slow
def test_clean_csv_no_exact_duplicates(clean_df) -> None:
    assert clean_df.duplicated().sum() == 0


@pytest.mark.data
@pytest.mark.slow
def test_clean_csv_line_revenue_numeric(clean_df) -> None:
    assert pd.api.types.is_numeric_dtype(clean_df["line_revenue"])


@pytest.mark.data
@pytest.mark.slow
def test_clean_csv_invoice_month_format(clean_df) -> None:
    sample = clean_df["invoice_month"].dropna().astype(str).head(100)
    assert all(len(v) == 7 and v[4] == "-" for v in sample)


@pytest.mark.data
@pytest.mark.slow
def test_clean_csv_missing_descriptions_filled(clean_df) -> None:
    assert clean_df["description"].isna().sum() == 0
    assert (clean_df["description"].astype(str).str.strip() == "").sum() == 0


@pytest.mark.data
@pytest.mark.slow
def test_clean_csv_flag_counts_match_summary(clean_df, cleaning_summary: dict) -> None:
    assert int(clean_df["is_canceled"].sum()) == CLEAN_CANCELED_LINES
    assert int(clean_df["is_return"].sum()) == CLEAN_RETURN_LINES
    assert int(clean_df["is_zero_or_negative_price"].sum()) == CLEAN_ZERO_OR_NEG_PRICE
    assert int(clean_df["is_missing_customer"].sum()) == EXCLUDED_MISSING_CUSTOMER


@pytest.mark.data
@pytest.mark.slow
def test_customer_level_row_count(customer_df) -> None:
    assert len(customer_df) == CUSTOMER_LEVEL_ROWS


@pytest.mark.data
@pytest.mark.slow
def test_customer_level_has_no_missing_customers(customer_df) -> None:
    assert customer_df["customer_id"].isna().sum() == 0
    assert (customer_df["customer_id"].astype(str).str.strip() == "").sum() == 0


@pytest.mark.data
@pytest.mark.slow
def test_customer_level_subset_of_clean(clean_df, customer_df) -> None:
    assert len(customer_df) < len(clean_df)
    assert len(customer_df) + EXCLUDED_MISSING_CUSTOMER == len(clean_df)


@pytest.mark.data
@pytest.mark.slow
@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("raw_input_rows", 1_067_371),
        ("duplicate_rows_removed", 12_133),
        ("clean_output_rows", CLEAN_OUTPUT_ROWS),
        ("customer_level_rows", CUSTOMER_LEVEL_ROWS),
        ("excluded_rows_missing_customer_id", EXCLUDED_MISSING_CUSTOMER),
        ("canceled_invoice_lines", CLEAN_CANCELED_LINES),
        ("return_lines", CLEAN_RETURN_LINES),
        ("zero_or_negative_price_lines", CLEAN_ZERO_OR_NEG_PRICE),
    ],
)
def test_cleaning_summary_contract(cleaning_summary: dict, key: str, expected: int) -> None:
    assert cleaning_summary[key] == expected
