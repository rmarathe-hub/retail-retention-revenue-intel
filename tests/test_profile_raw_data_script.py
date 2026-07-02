from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from .conftest import load_module_from_path


def _sample_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["10001", "A1", "Item A", 2, "2010-01-01 10:00:00", 1.00, 11111, "United Kingdom", "S1"],
            ["10001", "A1", "Item A", 2, "2010-01-01 10:00:00", 1.00, 11111, "United Kingdom", "S1"],
            ["C10002", "A2", "Item B", -1, "2010-01-02 10:00:00", 2.00, None, "France", "S1"],
            ["10003", "A3", None, 1, "2010-01-03 10:00:00", 0.00, 22222, "Germany", "S2"],
            ["10004", "A4", "Item D", 1, "2010-01-04 10:00:00", -1.00, 33333, "Germany", "S2"],
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
def test_profile_dataframe_expected_metrics(project_root: Path) -> None:
    module = load_module_from_path("profile_module", project_root / "scripts/profile_raw_data.py")
    df = _sample_df()
    summary = module.profile_dataframe(df)

    assert summary["row_count"] == 5
    assert summary["duplicate_rows"] == 1
    assert summary["missing_customer_id"] == 1
    assert summary["missing_description"] == 1
    assert summary["negative_quantity"] == 1
    assert summary["zero_unit_price"] == 1
    assert summary["negative_unit_price"] == 1
    assert summary["canceled_invoice_lines"] == 1
    assert summary["distinct_invoices"] == 4
    assert summary["distinct_customers"] == 3
    assert summary["distinct_stock_codes"] == 4
    assert summary["distinct_countries"] == 3
    assert "date_range" in summary and summary["date_range"]["min"].startswith("2010-01-01")
    assert summary["source_sheets"]["S1"] == 3
    assert summary["source_sheets"]["S2"] == 2


@pytest.mark.unit
def test_write_profile_creates_json(tmp_path: Path, project_root: Path) -> None:
    module = load_module_from_path(
        "profile_module_write", project_root / "scripts/profile_raw_data.py"
    )
    out_path = tmp_path / "summary.json"
    payload = {"row_count": 123, "test": True}
    module.write_profile(payload, out_path)
    loaded = json.loads(out_path.read_text(encoding="utf-8"))
    assert loaded == payload


@pytest.mark.unit
def test_load_raw_raises_when_csv_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, project_root: Path
) -> None:
    module = load_module_from_path(
        "profile_module_load", project_root / "scripts/profile_raw_data.py"
    )
    missing_csv = tmp_path / "missing.csv"
    monkeypatch.setattr(module, "CSV_PATH", missing_csv)
    with pytest.raises(FileNotFoundError):
        module.load_raw()

