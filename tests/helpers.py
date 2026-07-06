"""Shared helpers and constants for Week 1 (Days 1-7) test suite."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

# Raw data contracts (Day 2)
RAW_ROW_COUNT = 1_067_371
RAW_DATE_MIN = "2009-12-01"
RAW_DATE_MAX = "2011-12-09"
RAW_MISSING_CUSTOMER_ID = 243_007
RAW_MISSING_CUSTOMER_PCT = 22.77
RAW_CANCELED_LINES = 19_494
RAW_NEGATIVE_QTY = 22_950
RAW_DUPLICATE_ROWS = 12_133
RAW_ZERO_PRICE = 6_202
RAW_NEGATIVE_PRICE = 5
RAW_DISTINCT_CUSTOMERS = 5_942
RAW_DISTINCT_COUNTRIES = 43
RAW_UK_SHARE_MIN = 0.915
RAW_UK_SHARE_MAX = 0.925

# Cleaned data contracts (Day 3)
CLEAN_INPUT_ROWS = 1_067_371
CLEAN_DUPLICATES_REMOVED = 12_133
CLEAN_OUTPUT_ROWS = 1_055_238
CUSTOMER_LEVEL_ROWS = 812_368
EXCLUDED_MISSING_CUSTOMER = 242_870
EXCLUDED_MISSING_CUSTOMER_PCT = 23.02
CLEAN_CANCELED_LINES = 19_433
CLEAN_RETURN_LINES = 22_889
CLEAN_ZERO_OR_NEG_PRICE = 6_196

# Postgres contracts (Day 4)
DB_HOST_PORT = "5433"
DB_CONTAINER_PORT = "5432"
DB_NAME = "retail_analytics"
DB_USER = "retail_user"
DB_PASSWORD = "retail_pass"
DB_DIM_CUSTOMER_COUNT = 5_942
DB_DIM_DATE_COUNT = 739

# Day 6 mart contracts
EXECUTIVE_KPI_COUNT = 9
MART_MONTHLY_REVENUE_ROWS = 25
MART_CUSTOMER_ORDERS_ROWS = 5_881
KPI_TOTAL_REVENUE = 20_755_215.3280
KPI_TOTAL_REVENUE_CUSTOMER = 17_685_460.6380
KPI_TOTAL_ORDERS = 36_975
KPI_TOTAL_CUSTOMERS = 5_881
KPI_AOV = 478.3086
KPI_REVENUE_PER_CUSTOMER = 3_007.2200
KPI_REPEAT_PURCHASE_RATE = 72.3516
KPI_ONE_TIME_BUYER_RATE = 27.6484
KPI_CANCELLATION_LINE_RATE = 1.8416
KPI_REFERENCE_DATE = "2011-12-09"

EXECUTIVE_KPI_NAMES = [
    "average_order_value",
    "cancellation_line_rate",
    "one_time_buyer_rate",
    "repeat_purchase_rate",
    "revenue_per_customer",
    "total_customers",
    "total_orders",
    "total_revenue",
    "total_revenue_customer_attributed",
]

# Day 7 cohort contracts
COHORT_RETENTION_ROWS = 325
COHORT_DISTINCT_MONTHS = 25
COHORT_AVG_MONTH3_RETENTION_RATE = 21.6088
COHORT_AVG_MONTH3_REVENUE_RETENTION_RATE = 26.4364

# Day 8 RFM contracts
MART_CUSTOMER_RFM_ROWS = 5_881
RFM_CHAMPIONS_COUNT = 1_343
RFM_AT_RISK_COUNT = 543
RFM_AVG_RECENCY_DAYS = 200.9929
RFM_AVG_FREQUENCY_ORDERS = 6.2872
RFM_AVG_MONETARY_VALUE = 3_007.2200
RFM_SEGMENT_COUNTS = {
    "About to Sleep": 639,
    "At Risk": 543,
    "Cannot Lose Them": 265,
    "Champions": 1343,
    "Hibernating": 906,
    "Loyal Customers": 447,
    "Need Attention": 286,
    "New Customers": 443,
    "Others": 215,
    "Potential Loyalists": 429,
    "Promising": 365,
}

# Day 9 revenue-at-risk contracts
MART_REVENUE_AT_RISK_ROWS = 291
RISK_TOTAL_REVENUE_AT_RISK = 1_791_355.3360
RISK_RECOVERABLE_10PCT = 179_135.5336
RISK_INACTIVE_90D_COUNT = 59
RISK_INACTIVE_120D_COUNT = 68
RISK_INACTIVE_180D_COUNT = 164
RISK_TOP_1PCT_REVENUE_SHARE = 32.0164
RISK_TOP_10PCT_REVENUE_SHARE = 64.0410

# Day 12 product & country contracts
MART_PRODUCT_PERFORMANCE_ROWS = 5_304
MART_COUNTRY_PERFORMANCE_ROWS = 43
PRODUCT_TOP_STOCK_CODE = "22423"
PRODUCT_TOP_REVENUE = 344_069.3000
PRODUCT_TOP_CANCELLATION_RATE = 7.8583
COUNTRY_TOP = "United Kingdom"
COUNTRY_TOP_REVENUE = 17_655_379.7870
COUNTRY_TOP_ORDERS = 33_546
UK_REVENUE_SHARE_PCT = 85.0648

# Day 5 validation contracts
DQ_CHECK_COUNT = 27
MISSING_CUSTOMER_REVENUE_GBP = 2_638_407.51

DQ_CHECK_NAMES = [
    "raw_row_count",
    "stg_row_count",
    "dim_customer_count",
    "dim_date_count",
    "mart_monthly_revenue_rows",
    "mart_customer_orders_rows",
    "mart_executive_kpis_rows",
    "mart_cohort_retention_rows",
    "mart_cohort_distinct_months",
    "cohort_month_zero_retention_mismatch",
    "mart_customer_rfm_rows",
    "mart_revenue_at_risk_rows",
    "mart_product_performance_rows",
    "mart_country_performance_rows",
    "missing_customer_lines",
    "canceled_lines",
    "return_lines",
    "zero_or_negative_price_lines",
    "invalid_invoice_date_lines",
    "canceled_flag_mismatch",
    "return_flag_mismatch",
    "missing_customer_flag_mismatch",
    "zero_price_flag_mismatch",
    "line_revenue_mismatch",
    "stg_distinct_customers",
    "min_invoice_date_key",
    "max_invoice_date_key",
]

POPULATED_MARTS = {
    "mart_executive_kpis": EXECUTIVE_KPI_COUNT,
    "mart_monthly_revenue": MART_MONTHLY_REVENUE_ROWS,
    "mart_customer_orders": MART_CUSTOMER_ORDERS_ROWS,
    "mart_cohort_retention": COHORT_RETENTION_ROWS,
    "mart_customer_rfm": MART_CUSTOMER_RFM_ROWS,
    "mart_revenue_at_risk": MART_REVENUE_AT_RISK_ROWS,
    "mart_product_performance": MART_PRODUCT_PERFORMANCE_ROWS,
    "mart_country_performance": MART_COUNTRY_PERFORMANCE_ROWS,
}

EMPTY_FUTURE_MARTS: list[str] = []

WEEK1_SCRIPTS = [
    "scripts/download_or_import_data.py",
    "scripts/profile_raw_data.py",
    "scripts/clean_online_retail.py",
    "scripts/db_config.py",
    "scripts/load_to_postgres.py",
    "scripts/validate_data.py",
    "scripts/run_kpi_marts.py",
    "scripts/export_powerbi_marts.py",
    "scripts/run_cohort_retention.py",
    "scripts/run_rfm_segmentation.py",
    "scripts/run_revenue_at_risk.py",
    "scripts/run_product_market_analysis.py",
]

WEEK1_SQL_FILES = [
    "sql/01_schema.sql",
    "sql/02_data_quality_checks.sql",
    "sql/03_kpi_definitions.sql",
    "sql/04_revenue_analysis.sql",
    "sql/05_cohort_retention.sql",
    "sql/06_rfm_segmentation.sql",
    "sql/07_revenue_at_risk.sql",
    "sql/08_product_market_analysis.sql",
]

WEEK1_DOCS = [
    "docs/business_problem.md",
    "docs/metric_definitions.md",
    "docs/data_dictionary.md",
    "docs/data_quality_report.md",
    "docs/postgres_setup.md",
    "docs/cohort_analysis_notes.md",
    "docs/rfm_analysis_notes.md",
    "docs/revenue_at_risk_notes.md",
    "docs/product_market_notes.md",
    "docs/recommendations.md",
    "docs/portfolio_case_study.md",
    "docs/powerbi_dashboard_guide.md",
]

DAY8_PLUS_FILES = [
    "sql/09_executive_summary.sql",
    "dashboard/Retail_Retention_Revenue_Intelligence.pbix",
]

PORT_SCAN_PATHS = [
    "docker-compose.yml",
    ".env.example",
    "README.md",
    "docs/postgres_setup.md",
    "scripts/db_config.py",
    "scripts/load_to_postgres.py",
    "scripts/validate_data.py",
    "scripts/run_kpi_marts.py",
    "scripts/run_cohort_retention.py",
    "scripts/run_rfm_segmentation.py",
    "scripts/run_revenue_at_risk.py",
    "scripts/run_product_market_analysis.py",
    "scripts/export_powerbi_marts.py",
]

FORBIDDEN_HOST_PORT_PATTERNS = [
    "POSTGRES_PORT=5432",
    "localhost:5432",
    "@localhost:5432/",
    '"5432:5432"',
    "'5432:5432'",
]

PROJECT_NAME = "Retail Retention & Revenue Intelligence"
GITHUB_REPO = "retail-retention-revenue-intel"

CLEAN_COLUMNS = [
    "invoice_no",
    "stock_code",
    "description",
    "quantity",
    "invoice_date",
    "invoice_month",
    "unit_price",
    "customer_id",
    "country",
    "source_sheet",
    "is_canceled",
    "is_return",
    "is_missing_customer",
    "is_missing_description",
    "is_zero_or_negative_price",
    "is_invalid_invoice_date",
    "line_revenue",
]

RAW_COLUMNS = [
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

PROFILE_SUMMARY_KEYS = [
    "row_count",
    "date_range",
    "duplicate_rows",
    "missing_customer_id",
    "canceled_invoice_lines",
    "negative_quantity",
    "zero_unit_price",
    "negative_unit_price",
    "distinct_invoices",
    "distinct_customers",
    "distinct_stock_codes",
    "distinct_countries",
    "top_countries",
]

CLEANING_SUMMARY_KEYS = [
    "raw_input_rows",
    "duplicate_rows_removed",
    "clean_output_rows",
    "customer_level_rows",
    "excluded_rows_missing_customer_id",
    "canceled_invoice_lines",
    "return_lines",
    "zero_or_negative_price_lines",
]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def read_json(path: Path) -> dict:
    return json.loads(read_text(path))


def git_tracked_files(project_root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files"],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        pytest.skip("git ls-files unavailable")
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def skip_if_missing(path: Path, reason: str) -> None:
    if not path.exists():
        pytest.skip(reason)


def db_is_reachable(project_root: Path) -> bool:
    if not (project_root / ".env").exists():
        return False
    try:
        from sqlalchemy import text

        from tests.conftest import load_module_from_path

        db_config = load_module_from_path(
            "db_config_reachability", project_root / "scripts/db_config.py"
        )
        engine = db_config.create_db_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def assert_no_host_port_5432_in_connection_strings(text: str) -> None:
    """Host connections must not use localhost:5432."""
    forbidden = [
        "POSTGRES_PORT=5432",
        "localhost:5432",
        "@localhost:5432/",
    ]
    for token in forbidden:
        assert token not in text, f"Found forbidden host port reference: {token}"
