from __future__ import annotations

import pytest

from tests.conftest import load_module_from_path
from tests.helpers import (
    CLEAN_OUTPUT_ROWS,
    COHORT_RETENTION_ROWS,
    CUSTOMER_LEVEL_ROWS,
    DQ_CHECK_COUNT,
    EXECUTIVE_KPI_COUNT,
    MART_CUSTOMER_ORDERS_ROWS,
    MART_CUSTOMER_RFM_ROWS,
    MART_MONTHLY_REVENUE_ROWS,
    MART_REVENUE_AT_RISK_ROWS,
    RAW_ROW_COUNT,
    db_is_reachable,
)


@pytest.mark.smoke
def test_smoke_week1_pipeline_no_db(project_root, tmp_path) -> None:
    import pandas as pd

    download = load_module_from_path("smoke_dl", project_root / "scripts/download_or_import_data.py")
    profile = load_module_from_path("smoke_pr", project_root / "scripts/profile_raw_data.py")
    clean = load_module_from_path("smoke_cl", project_root / "scripts/clean_online_retail.py")

    cols = ["Invoice", "StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID", "Country"]
    df1 = pd.DataFrame([["10001", "A", "Item", 1, "2010-01-01 10:00:00", 1.0, 11111.0, "UK"]], columns=cols)
    df2 = pd.DataFrame([["20001", "B", "Item2", 2, "2011-01-01 10:00:00", 2.0, 22222.0, "DE"]], columns=cols)
    xlsx = tmp_path / "tiny.xlsx"
    csv = tmp_path / "combined.csv"
    with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
        df1.to_excel(w, index=False, sheet_name="Year 2009-2010")
        df2.to_excel(w, index=False, sheet_name="Year 2010-2011")
    download.combine_sheets_to_csv(xlsx, csv)
    combined = pd.read_csv(csv)
    summary = profile.profile_dataframe(combined)
    clean_df, customer_df, clean_summary = clean.clean_transactions(combined)
    assert len(combined) == 2
    assert summary["row_count"] == 2
    assert clean_summary["clean_output_rows"] == 2


@pytest.mark.smoke
@pytest.mark.db
def test_smoke_week1_db_state_when_available(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from sqlalchemy import text

    engine = load_module_from_path("smoke_db", project_root / "scripts/db_config.py").create_db_engine()
    with engine.connect() as conn:
        raw = conn.execute(text("SELECT COUNT(*) FROM raw_online_retail")).scalar()
        stg = conn.execute(text("SELECT COUNT(*) FROM stg_transactions")).scalar()
        kpis = conn.execute(text("SELECT COUNT(*) FROM mart_executive_kpis")).scalar()
        cohort = conn.execute(text("SELECT COUNT(*) FROM mart_cohort_retention")).scalar()
        rfm = conn.execute(text("SELECT COUNT(*) FROM mart_customer_rfm")).scalar()
        risk = conn.execute(text("SELECT COUNT(*) FROM mart_revenue_at_risk")).scalar()
    assert raw == RAW_ROW_COUNT
    assert stg == CLEAN_OUTPUT_ROWS
    assert kpis == EXECUTIVE_KPI_COUNT
    assert cohort == COHORT_RETENTION_ROWS
    assert rfm == MART_CUSTOMER_RFM_ROWS
    assert risk == MART_REVENUE_AT_RISK_ROWS


@pytest.mark.db
def test_smoke_validate_and_mart_scripts_pass(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    validate = load_module_from_path("smoke_val", project_root / "scripts/validate_data.py")
    kpi = load_module_from_path("smoke_kpi", project_root / "scripts/run_kpi_marts.py")
    cohort = load_module_from_path("smoke_coh", project_root / "scripts/run_cohort_retention.py")
    rfm = load_module_from_path("smoke_rfm", project_root / "scripts/run_rfm_segmentation.py")
    risk = load_module_from_path("smoke_risk", project_root / "scripts/run_revenue_at_risk.py")

    v = validate.run_validation()
    k = kpi.run_kpi_marts()
    c = cohort.run_cohort_retention()
    r = rfm.run_rfm_segmentation()
    risk_summary = risk.run_revenue_at_risk()
    assert v["all_checks_passed"] is True
    assert len(v["quality_checks"]) == DQ_CHECK_COUNT
    assert k["mart_row_counts"]["mart_monthly_revenue"] == MART_MONTHLY_REVENUE_ROWS
    assert k["mart_row_counts"]["mart_customer_orders"] == MART_CUSTOMER_ORDERS_ROWS
    assert c["mart_cohort_retention_rows"] == COHORT_RETENTION_ROWS
    assert r["mart_customer_rfm_rows"] == MART_CUSTOMER_RFM_ROWS
    assert risk_summary["mart_revenue_at_risk_rows"] == MART_REVENUE_AT_RISK_ROWS
