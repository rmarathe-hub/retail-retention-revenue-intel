from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import (
    COUNTRY_TOP,
    COUNTRY_TOP_ORDERS,
    COUNTRY_TOP_REVENUE,
    MART_COUNTRY_PERFORMANCE_ROWS,
    MART_PRODUCT_PERFORMANCE_ROWS,
    PRODUCT_TOP_CANCELLATION_RATE,
    PRODUCT_TOP_REVENUE,
    PRODUCT_TOP_STOCK_CODE,
    PROJECT_NAME,
    UK_REVENUE_SHARE_PCT,
)


DAY12_FILES = [
    "sql/08_product_market_analysis.sql",
    "docs/product_market_notes.md",
    "docs/recommendations.md",
    "scripts/run_product_market_analysis.py",
]


@pytest.mark.unit
@pytest.mark.parametrize("relative_path", DAY12_FILES)
def test_day12_required_files_exist(project_root: Path, relative_path: str) -> None:
    assert (project_root / relative_path).exists(), f"Missing {relative_path}"


@pytest.mark.integration
def test_day12_completion_contract(project_root: Path, readme_text: str) -> None:
    assert PROJECT_NAME in readme_text
    assert "08_product_market_analysis.sql" in readme_text
    assert "run_product_market_analysis.py" in readme_text
    assert "recommendations.md" in readme_text
    assert "Product & Market Performance" in readme_text
    assert "Retention Action Plan" in readme_text


@pytest.mark.sql
@pytest.mark.parametrize(
    "fragment",
    [
        "mart_product_performance",
        "mart_country_performance",
        "stock_code",
        "cancellation_rate",
        "total_quantity",
        "active_customers",
        "is_canceled = FALSE",
    ],
)
def test_product_market_sql_defines_marts(project_root: Path, fragment: str) -> None:
    sql = (project_root / "sql/08_product_market_analysis.sql").read_text(encoding="utf-8")
    assert fragment in sql


@pytest.mark.unit
def test_run_product_market_module_has_entrypoints(project_root: Path) -> None:
    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "run_product_unit", project_root / "scripts/run_product_market_analysis.py"
    )
    assert hasattr(module, "run_product_market_analysis")
    assert hasattr(module, "main")


@pytest.mark.db
def test_day12_product_market_marts_after_build(project_root: Path) -> None:
    from tests.helpers import db_is_reachable

    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "run_product_db", project_root / "scripts/run_product_market_analysis.py"
    )
    summary = module.run_product_market_analysis()
    assert summary["mart_product_performance_rows"] == MART_PRODUCT_PERFORMANCE_ROWS
    assert summary["mart_country_performance_rows"] == MART_COUNTRY_PERFORMANCE_ROWS
    assert summary["top_product_stock_code"] == PRODUCT_TOP_STOCK_CODE
    assert summary["top_product_revenue"] == pytest.approx(PRODUCT_TOP_REVENUE, rel=1e-3)
    assert summary["top_product_cancellation_rate"] == pytest.approx(
        PRODUCT_TOP_CANCELLATION_RATE, rel=1e-3
    )
    assert summary["top_country"] == COUNTRY_TOP
    assert summary["top_country_revenue"] == pytest.approx(COUNTRY_TOP_REVENUE, rel=1e-3)
    assert summary["top_country_orders"] == COUNTRY_TOP_ORDERS
    assert summary["uk_revenue_share_pct"] == pytest.approx(UK_REVENUE_SHARE_PCT, rel=1e-3)


@pytest.mark.docs
def test_recommendations_doc_has_prioritized_actions(project_root: Path) -> None:
    text = (project_root / "docs/recommendations.md").read_text(encoding="utf-8")
    assert "£179,135" in text or "179,135" in text
    assert "Win-back" in text or "win-back" in text
    assert "Champions" in text
    assert "85.06" in text or "85.06%" in text
