from __future__ import annotations

import importlib

import pytest


REQUIRED_PACKAGES = [
    "pandas",
    "numpy",
    "openpyxl",
    "psycopg2",
    "dotenv",
    "sqlalchemy",
    "pytest",
]


@pytest.mark.unit
@pytest.mark.parametrize("package_name", REQUIRED_PACKAGES)
def test_required_packages_import(package_name: str) -> None:
    importlib.import_module(package_name)


@pytest.mark.docs
@pytest.mark.parametrize(
    "required",
    [
        "online retail",
        "retention",
        "revenue",
        "stakeholder",
        "success criteria",
        "UCI",
    ],
)
def test_business_problem_doc_content(business_problem_text: str, required: str) -> None:
    assert required.lower() in business_problem_text.lower()


@pytest.mark.docs
@pytest.mark.parametrize(
    "required",
    [
        "line_revenue",
        "invoice_month",
        "is_canceled",
        "is_return",
        "is_missing_customer",
        "is_zero_or_negative_price",
        "is_invalid_invoice_date",
    ],
)
def test_data_dictionary_cleaned_fields(data_dictionary_text: str, required: str) -> None:
    assert required in data_dictionary_text


@pytest.mark.docs
@pytest.mark.parametrize(
    "required",
    [
        "1,055,238",
        "812,368",
        "retail_transactions_clean.csv",
        "retail_transactions_customer_level.csv",
        "flag",
        "duplicate",
        "242,870",
    ],
)
def test_data_quality_day3_content(data_quality_text: str, required: str) -> None:
    assert required in data_quality_text
