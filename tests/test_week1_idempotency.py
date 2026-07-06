from __future__ import annotations

import pytest

from tests.helpers import (
    COHORT_DISTINCT_MONTHS,
    COHORT_RETENTION_ROWS,
    EXECUTIVE_KPI_COUNT,
    MART_CUSTOMER_ORDERS_ROWS,
    MART_CUSTOMER_RFM_ROWS,
    MART_MONTHLY_REVENUE_ROWS,
    MART_REVENUE_AT_RISK_ROWS,
    db_is_reachable,
)


@pytest.mark.db
def test_run_kpi_marts_idempotent(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from tests.conftest import load_module_from_path

    module = load_module_from_path("kpi_idem", project_root / "scripts/run_kpi_marts.py")
    first = module.run_kpi_marts()
    second = module.run_kpi_marts()
    assert first["mart_row_counts"] == second["mart_row_counts"]
    assert first["mart_row_counts"]["mart_executive_kpis"] == EXECUTIVE_KPI_COUNT
    assert first["mart_row_counts"]["mart_monthly_revenue"] == MART_MONTHLY_REVENUE_ROWS
    assert first["mart_row_counts"]["mart_customer_orders"] == MART_CUSTOMER_ORDERS_ROWS


@pytest.mark.db
def test_run_cohort_retention_idempotent(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from tests.conftest import load_module_from_path

    module = load_module_from_path("cohort_idem", project_root / "scripts/run_cohort_retention.py")
    first = module.run_cohort_retention()
    second = module.run_cohort_retention()
    assert first["mart_cohort_retention_rows"] == second["mart_cohort_retention_rows"]
    assert first["mart_cohort_retention_rows"] == COHORT_RETENTION_ROWS
    assert first["distinct_cohort_months"] == COHORT_DISTINCT_MONTHS


@pytest.mark.db
def test_run_rfm_segmentation_idempotent(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from tests.conftest import load_module_from_path

    module = load_module_from_path("rfm_idem", project_root / "scripts/run_rfm_segmentation.py")
    first = module.run_rfm_segmentation()
    second = module.run_rfm_segmentation()
    assert first["mart_customer_rfm_rows"] == second["mart_customer_rfm_rows"]
    assert first["segment_counts"] == second["segment_counts"]


@pytest.mark.db
def test_run_revenue_at_risk_idempotent(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from tests.conftest import load_module_from_path

    module = load_module_from_path("risk_idem", project_root / "scripts/run_revenue_at_risk.py")
    first = module.run_revenue_at_risk()
    second = module.run_revenue_at_risk()
    assert first["mart_revenue_at_risk_rows"] == second["mart_revenue_at_risk_rows"]
    assert first["mart_revenue_at_risk_rows"] == MART_REVENUE_AT_RISK_ROWS


@pytest.mark.db
def test_validate_data_idempotent_after_marts_built(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from tests.conftest import load_module_from_path

    module = load_module_from_path("val_idem", project_root / "scripts/validate_data.py")
    first = module.run_validation()
    second = module.run_validation()
    assert first["all_checks_passed"] is True
    assert second["all_checks_passed"] is True
    assert len(first["quality_checks"]) == len(second["quality_checks"])
