from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from tests.conftest import load_module_from_path
from tests.helpers import (
    COHORT_RETENTION_ROWS,
    EXECUTIVE_KPI_COUNT,
    MART_CUSTOMER_ORDERS_ROWS,
    MART_MONTHLY_REVENUE_ROWS,
    POPULATED_MARTS,
    skip_if_missing,
)


EXPORT_MART_COUNTS = {
    "mart_executive_kpis.csv": EXECUTIVE_KPI_COUNT,
    "mart_monthly_revenue.csv": MART_MONTHLY_REVENUE_ROWS,
    "mart_customer_orders.csv": MART_CUSTOMER_ORDERS_ROWS,
    "mart_cohort_retention.csv": COHORT_RETENTION_ROWS,
}


@pytest.mark.unit
def test_export_module_lists_day6_and_cohort_marts(project_root: Path) -> None:
    module = load_module_from_path("export_unit", project_root / "scripts/export_powerbi_marts.py")
    assert "mart_executive_kpis" in module.DAY6_MARTS
    assert "mart_cohort_retention" in module.LATER_MARTS
    assert "mart_customer_rfm" in module.LATER_MARTS


@pytest.mark.unit
@pytest.mark.parametrize("mart_name", list(POPULATED_MARTS.keys()))
def test_export_targets_populated_marts(project_root: Path, mart_name: str) -> None:
    module = load_module_from_path("export_unit2", project_root / "scripts/export_powerbi_marts.py")
    all_marts = module.DAY6_MARTS + module.LATER_MARTS
    assert mart_name in all_marts


@pytest.mark.unit
def test_export_mart_writes_csv_to_marts_dir(project_root: Path, tmp_path: Path) -> None:
    module = load_module_from_path("export_unit3", project_root / "scripts/export_powerbi_marts.py")
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__ = MagicMock(return_value=conn)
    engine.connect.return_value.__exit__ = MagicMock(return_value=False)
    conn.execute.return_value.scalar.return_value = 2
    df = pd.DataFrame({"kpi_name": ["a", "b"], "kpi_value": [1.0, 2.0]})
    with patch.object(pd, "read_sql", return_value=df):
        path = module.export_mart(engine, "mart_executive_kpis", output_dir=tmp_path)
    assert path is not None
    assert path.parent == tmp_path
    assert path.name == "mart_executive_kpis.csv"
    assert path.exists()


@pytest.mark.unit
def test_export_skips_empty_mart(project_root: Path, tmp_path: Path) -> None:
    module = load_module_from_path("export_unit4", project_root / "scripts/export_powerbi_marts.py")
    engine = MagicMock()
    conn = MagicMock()
    engine.connect.return_value.__enter__ = MagicMock(return_value=conn)
    engine.connect.return_value.__exit__ = MagicMock(return_value=False)
    conn.execute.return_value.scalar.return_value = 0
    path = module.export_mart(engine, "mart_customer_rfm", output_dir=tmp_path)
    assert path is None


@pytest.mark.data
@pytest.mark.parametrize("filename,expected_rows", list(EXPORT_MART_COUNTS.items()))
def test_exported_csv_row_counts(marts_dir: Path, filename: str, expected_rows: int) -> None:
    path = marts_dir / filename
    skip_if_missing(path, f"{filename} not exported locally")
    df = pd.read_csv(path)
    assert len(df) == expected_rows


@pytest.mark.data
@pytest.mark.parametrize(
    "filename,required_col",
    [
        ("mart_executive_kpis.csv", "kpi_name"),
        ("mart_executive_kpis.csv", "kpi_value"),
        ("mart_monthly_revenue.csv", "invoice_month"),
        ("mart_monthly_revenue.csv", "total_revenue"),
        ("mart_customer_orders.csv", "customer_id"),
        ("mart_customer_orders.csv", "is_repeat_customer"),
        ("mart_cohort_retention.csv", "retention_rate"),
        ("mart_cohort_retention.csv", "months_since_first_purchase"),
    ],
)
def test_exported_csv_required_columns(
    marts_dir: Path, filename: str, required_col: str
) -> None:
    path = marts_dir / filename
    skip_if_missing(path, f"{filename} not exported locally")
    df = pd.read_csv(path)
    assert required_col in df.columns
