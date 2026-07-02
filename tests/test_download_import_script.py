from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from .conftest import load_module_from_path


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


def _build_fake_xlsx(path: Path) -> None:
    cols = EXPECTED_COLUMNS[:-1]
    df1 = pd.DataFrame(
        [
            ["10001", "A1", "Item A", 2, "2010-01-01 10:00:00", 1.25, 12345, "United Kingdom"],
            ["10002", "A2", "Item B", 1, "2010-01-01 11:00:00", 2.00, 12346, "France"],
        ],
        columns=cols,
    )
    df2 = pd.DataFrame(
        [
            ["20001", "B1", "Item C", -1, "2011-01-02 09:00:00", 3.10, 12347, "Germany"],
        ],
        columns=cols,
    )
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df1.to_excel(writer, index=False, sheet_name="Year 2009-2010")
        df2.to_excel(writer, index=False, sheet_name="Year 2010-2011")


@pytest.mark.unit
def test_combine_sheets_to_csv_works(tmp_path: Path, project_root: Path) -> None:
    module = load_module_from_path(
        "download_module", project_root / "scripts/download_or_import_data.py"
    )
    xlsx_path = tmp_path / "tiny.xlsx"
    out_csv = tmp_path / "out.csv"
    _build_fake_xlsx(xlsx_path)

    result_path = module.combine_sheets_to_csv(xlsx_path, out_csv)

    assert result_path == out_csv
    assert out_csv.exists()
    combined = pd.read_csv(out_csv)
    assert len(combined) == 3
    assert list(combined.columns) == EXPECTED_COLUMNS
    assert set(combined["source_sheet"].unique()) == {"Year 2009-2010", "Year 2010-2011"}


@pytest.mark.unit
def test_download_uses_existing_file_without_network(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, project_root: Path
) -> None:
    module = load_module_from_path(
        "download_module_existing", project_root / "scripts/download_or_import_data.py"
    )
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    xlsx_path = raw_dir / "online_retail_II.xlsx"
    xlsx_path.write_bytes(b"already-there")

    monkeypatch.setattr(module, "RAW_DIR", raw_dir)
    monkeypatch.setattr(module, "XLSX_PATH", xlsx_path)

    called = {"value": False}

    def fake_urlretrieve(*args, **kwargs):
        called["value"] = True
        raise AssertionError("Network should not be called when file exists")

    monkeypatch.setattr(module.urllib.request, "urlretrieve", fake_urlretrieve)
    result = module.download_raw_data(force=False)
    assert result == xlsx_path
    assert called["value"] is False


@pytest.mark.unit
def test_download_force_true_calls_urlretrieve(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, project_root: Path
) -> None:
    module = load_module_from_path(
        "download_module_force", project_root / "scripts/download_or_import_data.py"
    )
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    xlsx_path = raw_dir / "online_retail_II.xlsx"

    monkeypatch.setattr(module, "RAW_DIR", raw_dir)
    monkeypatch.setattr(module, "XLSX_PATH", xlsx_path)

    def fake_urlretrieve(_url: str, target: Path):
        Path(target).write_bytes(b"fresh-download")

    monkeypatch.setattr(module.urllib.request, "urlretrieve", fake_urlretrieve)
    result = module.download_raw_data(force=True)
    assert result == xlsx_path
    assert xlsx_path.exists()


@pytest.mark.unit
def test_combine_empty_workbook_raises(tmp_path: Path, project_root: Path) -> None:
    module = load_module_from_path(
        "download_module_empty", project_root / "scripts/download_or_import_data.py"
    )
    xlsx_path = tmp_path / "empty.xlsx"
    out_csv = tmp_path / "out.csv"

    # Create workbook with no data rows but valid sheet/headers.
    pd.DataFrame(columns=EXPECTED_COLUMNS[:-1]).to_excel(
        xlsx_path, index=False, sheet_name="Year 2009-2010"
    )

    result_path = module.combine_sheets_to_csv(xlsx_path, out_csv)
    assert result_path == out_csv
    df = pd.read_csv(out_csv)
    assert list(df.columns) == EXPECTED_COLUMNS

