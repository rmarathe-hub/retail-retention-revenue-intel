from __future__ import annotations

import pytest


@pytest.mark.docs
@pytest.mark.parametrize(
    "required_snippet",
    [
        "1,067,371",
        "243,007",
        "22.77%",
        "19,494",
        "8,292",
        "22,950",
        "12,133",
        "6,202",
        "negative unit price | 5",
        "5,942",
        "92.0%",
        "retail_transactions_clean.csv",
        "retail_transactions_customer_level.csv",
        "do not silently drop",
    ],
)
def test_data_quality_report_contains_expected_numbers(
    data_quality_text: str, required_snippet: str
) -> None:
    assert required_snippet.lower() in data_quality_text.lower()


@pytest.mark.docs
def test_data_quality_report_mentions_flag_not_blind_delete(data_quality_text: str) -> None:
    lowered = data_quality_text.lower()
    assert "flag" in lowered
    assert "planned" in lowered
    assert "day 3" in lowered

