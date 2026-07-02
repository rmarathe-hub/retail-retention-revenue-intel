from __future__ import annotations

import pandas as pd
import pytest

from tests.conftest import load_module_from_path


@pytest.fixture(scope="module")
def clean_module(project_root):
    return load_module_from_path(
        "clean_rules_ext", project_root / "scripts/clean_online_retail.py"
    )


def _df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["10001", "A1", None, 2, "2010-01-01 10:00:00", 2.0, 11111, " United Kingdom ", "S1"],
            ["C10002", "A2", "B", -1, "2010-01-02 10:00:00", 0.0, 22222, "France", "S1"],
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


@pytest.mark.unit
@pytest.mark.parametrize(
    ("column", "check"),
    [
        ("invoice_no", lambda df: df["invoice_no"].dtype.name in {"string", "object"}),
        ("invoice_month", lambda df: df["invoice_month"].astype(str).str.len().ge(7).all()),
        ("line_revenue", lambda df: (df["line_revenue"] == df["quantity"] * df["unit_price"]).all()),
        ("is_canceled", lambda df: df.loc[df["invoice_no"].str.startswith("C"), "is_canceled"].all()),
        ("is_return", lambda df: (df["quantity"] < 0).eq(df["is_return"]).all()),
        ("is_zero_or_negative_price", lambda df: (df["unit_price"] <= 0).eq(df["is_zero_or_negative_price"]).all()),
        ("country", lambda df: df["country"].str.strip().eq(df["country"]).all()),
    ],
)
def test_cleaning_rule_parametrized(clean_module, column: str, check) -> None:
    clean_df, _, _ = clean_module.clean_transactions(_df())
    assert column in clean_df.columns
    assert bool(check(clean_df))


@pytest.mark.unit
def test_cleaning_keeps_returns_and_cancellations_in_clean_output(clean_module) -> None:
    clean_df, _, _ = clean_module.clean_transactions(_df())
    assert clean_df["is_canceled"].any()
    assert clean_df["is_return"].any()


@pytest.mark.unit
def test_cleaning_customer_level_excludes_only_missing_customers(clean_module) -> None:
    df = _df()
    clean_df, customer_df, summary = clean_module.clean_transactions(df)
    assert summary["customer_level_rows"] == len(customer_df)
    assert customer_df["customer_id"].notna().all()
    assert len(customer_df) <= len(clean_df)
