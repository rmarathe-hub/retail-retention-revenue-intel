from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import (
    EXECUTIVE_KPI_COUNT,
    EXECUTIVE_KPI_NAMES,
    KPI_AOV,
    KPI_TOTAL_CUSTOMERS,
    KPI_TOTAL_ORDERS,
    KPI_TOTAL_REVENUE,
    MART_CUSTOMER_ORDERS_ROWS,
    MART_MONTHLY_REVENUE_ROWS,
    PROJECT_NAME,
)


DAY6_FILES = [
    "sql/03_kpi_definitions.sql",
    "sql/04_revenue_analysis.sql",
    "scripts/run_kpi_marts.py",
    "scripts/export_powerbi_marts.py",
]


@pytest.mark.unit
@pytest.mark.parametrize("relative_path", DAY6_FILES)
def test_day6_required_files_exist(project_root: Path, relative_path: str) -> None:
    assert (project_root / relative_path).exists(), f"Missing {relative_path}"


@pytest.mark.integration
def test_day6_completion_contract(project_root: Path, readme_text: str) -> None:
    assert PROJECT_NAME in readme_text
    assert "run_kpi_marts.py" in readme_text
    assert "03_kpi_definitions.sql" in readme_text



@pytest.mark.sql
@pytest.mark.parametrize("kpi_name", EXECUTIVE_KPI_NAMES)
def test_kpi_definitions_sql_references_kpi(project_root: Path, kpi_name: str) -> None:
    sql = (project_root / "sql/03_kpi_definitions.sql").read_text(encoding="utf-8")
    assert kpi_name in sql or kpi_name.replace("_", " ") in sql.lower()


@pytest.mark.unit
def test_run_kpi_marts_module_has_entrypoints(project_root: Path) -> None:
    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "run_kpi_marts_unit", project_root / "scripts/run_kpi_marts.py"
    )
    assert hasattr(module, "run_kpi_marts")
    assert hasattr(module, "main")


@pytest.mark.unit
def test_export_powerbi_marts_module_has_entrypoints(project_root: Path) -> None:
    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "export_marts_unit", project_root / "scripts/export_powerbi_marts.py"
    )
    assert hasattr(module, "export_powerbi_marts")
    assert hasattr(module, "main")


@pytest.mark.db
def test_day6_mart_row_counts_after_build(project_root: Path) -> None:
    from tests.helpers import db_is_reachable

    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    from tests.conftest import load_module_from_path

    kpi_module = load_module_from_path(
        "run_kpi_db", project_root / "scripts/run_kpi_marts.py"
    )
    summary = kpi_module.run_kpi_marts()
    counts = summary["mart_row_counts"]
    assert counts["mart_executive_kpis"] == EXECUTIVE_KPI_COUNT
    assert counts["mart_monthly_revenue"] == MART_MONTHLY_REVENUE_ROWS
    assert counts["mart_customer_orders"] == MART_CUSTOMER_ORDERS_ROWS

    kpi_map = {row["kpi_name"]: float(row["kpi_value"]) for row in summary["executive_kpis"]}
    assert kpi_map["total_revenue"] == pytest.approx(KPI_TOTAL_REVENUE, rel=1e-4)
    assert kpi_map["total_orders"] == KPI_TOTAL_ORDERS
    assert kpi_map["total_customers"] == KPI_TOTAL_CUSTOMERS
    assert kpi_map["average_order_value"] == pytest.approx(KPI_AOV, rel=1e-4)
