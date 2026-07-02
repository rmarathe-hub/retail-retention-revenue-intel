from __future__ import annotations

import re

import pytest


@pytest.mark.docs
@pytest.mark.parametrize(
    "required_term",
    [
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
def test_data_dictionary_mentions_columns(data_dictionary_text: str, required_term: str) -> None:
    assert required_term in data_dictionary_text


@pytest.mark.docs
@pytest.mark.parametrize(
    "phrase",
    [
        "invoice line",
        "missing customer",
        "canceled",
        "returns",
        "duplicate",
        "zero unit price",
    ],
)
def test_data_dictionary_mentions_grain_and_quirks(data_dictionary_text: str, phrase: str) -> None:
    assert phrase.lower() in data_dictionary_text.lower()


@pytest.mark.docs
def test_data_dictionary_has_no_unmarked_absolute_local_paths(data_dictionary_text: str) -> None:
    # Allow references to local paths when explicitly marked as local context.
    absolute_paths = re.findall(r"/Users/[^\s`]+", data_dictionary_text)
    assert not absolute_paths

