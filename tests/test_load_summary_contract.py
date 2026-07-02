from __future__ import annotations

import json

import pytest

from tests.helpers import (
    CLEAN_OUTPUT_ROWS,
    DB_DIM_CUSTOMER_COUNT,
    DB_DIM_DATE_COUNT,
    RAW_ROW_COUNT,
    skip_if_missing,
)


@pytest.fixture(scope="module")
def load_summary(load_summary_path):
    skip_if_missing(load_summary_path, "load_summary.json not found locally")
    return json.loads(load_summary_path.read_text(encoding="utf-8"))


@pytest.mark.data
@pytest.mark.parametrize(
    ("key", "expected"),
    [
        ("raw_rows_loaded", RAW_ROW_COUNT),
        ("stg_rows_loaded", CLEAN_OUTPUT_ROWS),
        ("dim_date_rows_inserted", DB_DIM_DATE_COUNT),
        ("dim_customer_rows_upserted", DB_DIM_CUSTOMER_COUNT),
    ],
)
def test_load_summary_top_level_counts(load_summary: dict, key: str, expected: int) -> None:
    assert load_summary[key] == expected


@pytest.mark.data
@pytest.mark.parametrize(
    ("table", "expected"),
    [
        ("raw_online_retail", RAW_ROW_COUNT),
        ("stg_transactions", CLEAN_OUTPUT_ROWS),
        ("dim_customer", DB_DIM_CUSTOMER_COUNT),
        ("dim_date", DB_DIM_DATE_COUNT),
    ],
)
def test_load_summary_table_counts(load_summary: dict, table: str, expected: int) -> None:
    assert load_summary["table_counts"][table] == expected


@pytest.mark.data
def test_load_summary_validation_all_ok(load_summary: dict) -> None:
    assert all(v == "ok" for v in load_summary["validation"].values())
