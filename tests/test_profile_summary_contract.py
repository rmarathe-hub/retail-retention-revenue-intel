from __future__ import annotations

from pathlib import Path

import pytest


@pytest.mark.data
def test_profile_summary_has_expected_keys(profile_summary: dict) -> None:
    expected = {
        "row_count",
        "column_count",
        "columns",
        "date_range",
        "duplicate_rows",
        "missing_customer_id",
        "missing_customer_id_pct",
        "missing_description",
        "missing_description_pct",
        "negative_quantity",
        "zero_quantity",
        "negative_unit_price",
        "zero_unit_price",
        "canceled_invoice_lines",
        "distinct_canceled_invoices",
        "null_country",
        "invalid_dates",
        "distinct_invoices",
        "distinct_customers",
        "distinct_stock_codes",
        "distinct_countries",
        "line_value_p99",
        "line_value_p999",
        "outlier_lines_above_p999",
        "top_countries",
    }
    missing = expected.difference(set(profile_summary.keys()))
    assert not missing, f"Missing keys in profile summary: {sorted(missing)}"


@pytest.mark.data
def test_profile_summary_core_values(profile_summary: dict) -> None:
    assert profile_summary["row_count"] == 1_067_371
    assert profile_summary["date_range"]["min"].startswith("2009-12-01")
    assert profile_summary["date_range"]["max"].startswith("2011-12-09")
    assert profile_summary["missing_customer_id"] == 243_007
    assert profile_summary["canceled_invoice_lines"] == 19_494
    assert profile_summary["negative_quantity"] == 22_950
    assert profile_summary["duplicate_rows"] == 12_133
    assert profile_summary["zero_unit_price"] == 6_202
    assert profile_summary["negative_unit_price"] == 5
    assert profile_summary["distinct_invoices"] == 53_628
    assert profile_summary["distinct_customers"] == 5_942
    assert profile_summary["distinct_stock_codes"] == 5_305
    assert profile_summary["distinct_countries"] == 43


@pytest.mark.data
def test_profile_summary_top_country_uk_share(profile_summary: dict) -> None:
    top_countries = profile_summary["top_countries"]
    uk_rows = top_countries["United Kingdom"]
    total_rows = profile_summary["row_count"]
    uk_share = uk_rows / total_rows
    assert 0.915 <= uk_share <= 0.925


@pytest.mark.data
def test_profile_summary_source_sheets_optional(profile_summary: dict) -> None:
    # Current implementation includes this key; keep check resilient if absent.
    if "source_sheets" not in profile_summary:
        pytest.skip("source_sheets key not present")
    assert profile_summary["source_sheets"]["Year 2009-2010"] == 525_461
    assert profile_summary["source_sheets"]["Year 2010-2011"] == 541_910

