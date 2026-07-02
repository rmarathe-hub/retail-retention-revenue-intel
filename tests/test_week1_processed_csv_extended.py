from __future__ import annotations

import pytest

from tests.helpers import (
    CLEAN_COLUMNS,
    CLEAN_OUTPUT_ROWS,
    CUSTOMER_LEVEL_ROWS,
    RAW_ROW_COUNT,
    skip_if_missing,
)


@pytest.mark.data
@pytest.mark.slow
def test_clean_csv_row_count(clean_csv_path) -> None:
    skip_if_missing(clean_csv_path, "clean CSV not found")
    import pandas as pd
    # count lines without loading full file into memory twice
    with clean_csv_path.open(encoding="utf-8") as f:
        row_count = sum(1 for _ in f) - 1
    assert row_count == CLEAN_OUTPUT_ROWS


@pytest.mark.data
@pytest.mark.slow
def test_customer_level_csv_row_count(customer_level_csv_path) -> None:
    skip_if_missing(customer_level_csv_path, "customer level CSV not found")
    with customer_level_csv_path.open(encoding="utf-8") as f:
        row_count = sum(1 for _ in f) - 1
    assert row_count == CUSTOMER_LEVEL_ROWS


@pytest.mark.data
@pytest.mark.parametrize("column", CLEAN_COLUMNS)
def test_clean_csv_has_column(clean_csv_path, column: str) -> None:
    skip_if_missing(clean_csv_path, "clean CSV not found")
    import pandas as pd
    df = pd.read_csv(clean_csv_path, nrows=5)
    assert column in df.columns


@pytest.mark.data
@pytest.mark.slow
def test_clean_csv_no_exact_duplicates(clean_csv_path) -> None:
    skip_if_missing(clean_csv_path, "clean CSV not found")
    import pandas as pd
    df = pd.read_csv(clean_csv_path)
    assert len(df) == len(df.drop_duplicates())


@pytest.mark.data
@pytest.mark.slow
def test_customer_level_no_null_customer_id(customer_level_csv_path) -> None:
    skip_if_missing(customer_level_csv_path, "customer level CSV not found")
    import pandas as pd
    df = pd.read_csv(customer_level_csv_path, usecols=["customer_id"])
    assert df["customer_id"].notna().all()


@pytest.mark.data
def test_customer_level_fewer_rows_than_clean(clean_csv_path, customer_level_csv_path) -> None:
    skip_if_missing(clean_csv_path, "clean CSV not found")
    skip_if_missing(customer_level_csv_path, "customer level CSV not found")
    assert CUSTOMER_LEVEL_ROWS < CLEAN_OUTPUT_ROWS


@pytest.mark.data
@pytest.mark.parametrize(
    "path_name,expected",
    [
        ("clean_csv_path", CLEAN_OUTPUT_ROWS),
        ("customer_level_csv_path", CUSTOMER_LEVEL_ROWS),
    ],
)
def test_processed_row_counts_match_contract(request, path_name: str, expected: int) -> None:
    path = request.getfixturevalue(path_name)
    skip_if_missing(path, f"{path_name} not found")
    with path.open(encoding="utf-8") as f:
        rows = sum(1 for _ in f) - 1
    assert rows == expected
