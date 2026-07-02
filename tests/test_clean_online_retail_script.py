from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from tests.conftest import load_module_from_path


def _raw_fixture_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["10001", "A1", "Item A", 2, "2010-01-01 10:00:00", 1.00, 11111, "United Kingdom", "Y1"],
            ["10001", "A1", "Item A", 2, "2010-01-01 10:00:00", 1.00, 11111, "United Kingdom", "Y1"],  # duplicate
            ["C10002", "A2", None, -1, "2010-01-02 10:00:00", 0.00, None, " France ", "Y1"],
            ["10003", "A3", "Item C", 1, "2010-01-03 10:00:00", -1.50, 22222, "Germany", "Y2"],
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
def test_clean_transactions_basic_behavior(project_root: Path) -> None:
    module = load_module_from_path(
        "clean_module", project_root / "scripts/clean_online_retail.py"
    )
    clean_df, customer_df, summary = module.clean_transactions(_raw_fixture_df())

    assert summary["raw_input_rows"] == 4
    assert summary["duplicate_rows_removed"] == 1
    assert summary["clean_output_rows"] == 3
    assert summary["customer_level_rows"] == 2
    assert "line_revenue" in clean_df.columns
    assert "invoice_month" in clean_df.columns
    assert "is_canceled" in clean_df.columns
    assert "is_return" in clean_df.columns
    assert "is_missing_customer" in clean_df.columns
    assert "is_zero_or_negative_price" in clean_df.columns
    assert clean_df["description"].isna().sum() == 0
    assert customer_df["customer_id"].isna().sum() == 0


@pytest.mark.unit
def test_save_outputs_writes_files(tmp_path: Path, project_root: Path) -> None:
    module = load_module_from_path(
        "clean_module_save", project_root / "scripts/clean_online_retail.py"
    )
    clean_df = pd.DataFrame({"a": [1]})
    customer_df = pd.DataFrame({"b": [2]})
    summary = {"ok": True}

    clean_path = tmp_path / "clean.csv"
    customer_path = tmp_path / "customer.csv"
    summary_path = tmp_path / "summary.json"

    module.save_outputs(clean_df, customer_df, summary, clean_path, customer_path, summary_path)

    assert clean_path.exists()
    assert customer_path.exists()
    assert summary_path.exists()
    assert json.loads(summary_path.read_text(encoding="utf-8"))["ok"] is True


@pytest.mark.data
def test_day3_processed_outputs_exist_if_generated(project_root: Path) -> None:
    clean_path = project_root / "data" / "processed" / "retail_transactions_clean.csv"
    customer_path = (
        project_root / "data" / "processed" / "retail_transactions_customer_level.csv"
    )
    summary_path = project_root / "data" / "processed" / "cleaning_summary.json"

    if not clean_path.exists() and not customer_path.exists() and not summary_path.exists():
        pytest.skip("Day 3 processed artifacts not generated locally")

    assert clean_path.exists()
    assert customer_path.exists()
    assert summary_path.exists()

