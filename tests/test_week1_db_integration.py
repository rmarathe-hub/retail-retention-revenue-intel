from __future__ import annotations

import pytest

from tests.helpers import (
    COHORT_AVG_MONTH3_RETENTION_RATE,
    COHORT_AVG_MONTH3_REVENUE_RETENTION_RATE,
    COHORT_DISTINCT_MONTHS,
    COHORT_RETENTION_ROWS,
    EXECUTIVE_KPI_COUNT,
    KPI_AOV,
    KPI_TOTAL_CUSTOMERS,
    KPI_TOTAL_ORDERS,
    KPI_TOTAL_REVENUE,
    KPI_TOTAL_REVENUE_CUSTOMER,
    MART_CUSTOMER_ORDERS_ROWS,
    MART_MONTHLY_REVENUE_ROWS,
    EMPTY_FUTURE_MARTS,
    POPULATED_MARTS,
    db_is_reachable,
)


@pytest.mark.db
@pytest.mark.parametrize("table,expected_rows", list(POPULATED_MARTS.items()))
def test_db_populated_mart_row_counts(project_root, table: str, expected_rows: int) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from sqlalchemy import text
    from tests.conftest import load_module_from_path

    engine = load_module_from_path("db_state", project_root / "scripts/db_config.py").create_db_engine()
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    assert count == expected_rows


@pytest.mark.db
@pytest.mark.parametrize("table", EMPTY_FUTURE_MARTS)
def test_db_future_marts_empty(project_root, table: str) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from sqlalchemy import text
    from tests.conftest import load_module_from_path

    engine = load_module_from_path("db_empty", project_root / "scripts/db_config.py").create_db_engine()
    with engine.connect() as conn:
        count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
    assert count == 0


@pytest.mark.db
@pytest.mark.parametrize(
    ("kpi_name", "expected"),
    [
        ("total_revenue", KPI_TOTAL_REVENUE),
        ("total_revenue_customer_attributed", KPI_TOTAL_REVENUE_CUSTOMER),
        ("total_orders", KPI_TOTAL_ORDERS),
        ("total_customers", KPI_TOTAL_CUSTOMERS),
        ("average_order_value", KPI_AOV),
    ],
)
def test_db_executive_kpi_values(project_root, kpi_name: str, expected: float) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from sqlalchemy import text
    from tests.conftest import load_module_from_path

    engine = load_module_from_path("db_kpi", project_root / "scripts/db_config.py").create_db_engine()
    with engine.connect() as conn:
        value = conn.execute(
            text("SELECT kpi_value FROM mart_executive_kpis WHERE kpi_name = :n"),
            {"n": kpi_name},
        ).scalar()
    assert float(value) == pytest.approx(expected, rel=1e-3)


@pytest.mark.db
def test_db_cohort_month_zero_retention_is_100(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from sqlalchemy import text
    from tests.conftest import load_module_from_path

    engine = load_module_from_path("db_cohort0", project_root / "scripts/db_config.py").create_db_engine()
    with engine.connect() as conn:
        bad = conn.execute(
            text(
                "SELECT COUNT(*) FROM mart_cohort_retention "
                "WHERE months_since_first_purchase = 0 AND retention_rate <> 100.0000"
            )
        ).scalar()
    assert bad == 0


@pytest.mark.db
def test_db_cohort_month3_averages(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from sqlalchemy import text
    from tests.conftest import load_module_from_path

    engine = load_module_from_path("db_cohort3", project_root / "scripts/db_config.py").create_db_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT AVG(retention_rate), AVG(revenue_retention_rate) "
                "FROM mart_cohort_retention WHERE months_since_first_purchase = 3"
            )
        ).one()
    assert float(row[0]) == pytest.approx(COHORT_AVG_MONTH3_RETENTION_RATE, rel=1e-3)
    assert float(row[1]) == pytest.approx(COHORT_AVG_MONTH3_REVENUE_RETENTION_RATE, rel=1e-3)


@pytest.mark.db
def test_db_customer_orders_revenue_matches_kpi(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from sqlalchemy import text
    from tests.conftest import load_module_from_path

    engine = load_module_from_path("db_cust_rev", project_root / "scripts/db_config.py").create_db_engine()
    with engine.connect() as conn:
        total = conn.execute(text("SELECT SUM(total_revenue) FROM mart_customer_orders")).scalar()
    assert float(total) == pytest.approx(KPI_TOTAL_REVENUE_CUSTOMER, rel=1e-3)


@pytest.mark.db
def test_db_monthly_revenue_row_count(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from sqlalchemy import text
    from tests.conftest import load_module_from_path

    engine = load_module_from_path("db_monthly", project_root / "scripts/db_config.py").create_db_engine()
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM mart_monthly_revenue")).scalar()
        distinct = conn.execute(text("SELECT COUNT(DISTINCT invoice_month) FROM mart_monthly_revenue")).scalar()
    assert count == MART_MONTHLY_REVENUE_ROWS
    assert distinct == count


@pytest.mark.db
def test_db_cohort_no_duplicate_cohort_activity_pairs(project_root) -> None:
    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")
    from sqlalchemy import text
    from tests.conftest import load_module_from_path

    engine = load_module_from_path("db_cohort_dup", project_root / "scripts/db_config.py").create_db_engine()
    with engine.connect() as conn:
        dupes = conn.execute(
            text(
                "SELECT COUNT(*) FROM ("
                "SELECT cohort_month, activity_month, COUNT(*) c "
                "FROM mart_cohort_retention GROUP BY 1,2 HAVING COUNT(*) > 1"
                ") d"
            )
        ).scalar()
    assert dupes == 0
