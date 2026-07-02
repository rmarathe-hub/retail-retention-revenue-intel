from __future__ import annotations

from pathlib import Path

import pytest

from tests.helpers import (
    MART_CUSTOMER_RFM_ROWS,
    PROJECT_NAME,
    RFM_AT_RISK_COUNT,
    RFM_AVG_FREQUENCY_ORDERS,
    RFM_AVG_MONETARY_VALUE,
    RFM_AVG_RECENCY_DAYS,
    RFM_CHAMPIONS_COUNT,
    RFM_SEGMENT_COUNTS,
)


DAY8_FILES = [
    "sql/06_rfm_segmentation.sql",
    "docs/rfm_analysis_notes.md",
    "scripts/run_rfm_segmentation.py",
]


@pytest.mark.unit
@pytest.mark.parametrize("relative_path", DAY8_FILES)
def test_day8_required_files_exist(project_root: Path, relative_path: str) -> None:
    assert (project_root / relative_path).exists(), f"Missing {relative_path}"


@pytest.mark.integration
def test_day8_completion_contract(project_root: Path, readme_text: str) -> None:
    assert PROJECT_NAME in readme_text
    assert "06_rfm_segmentation.sql" in readme_text
    assert "run_rfm_segmentation.py" in readme_text
    assert "rfm segmentation" in readme_text.lower()


@pytest.mark.sql
@pytest.mark.parametrize(
    "fragment",
    [
        "mart_customer_rfm",
        "recency_days",
        "frequency_orders",
        "monetary_value",
        "r_score",
        "f_score",
        "m_score",
        "rfm_score",
        "customer_segment",
        "NTILE(5)",
        "Champions",
        "At Risk",
        "2011-12-09",
    ],
)
def test_rfm_sql_defines_mart_columns(project_root: Path, fragment: str) -> None:
    sql = (project_root / "sql/06_rfm_segmentation.sql").read_text(encoding="utf-8")
    assert fragment in sql


@pytest.mark.unit
def test_run_rfm_segmentation_module_has_entrypoints(project_root: Path) -> None:
    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "run_rfm_unit", project_root / "scripts/run_rfm_segmentation.py"
    )
    assert hasattr(module, "run_rfm_segmentation")
    assert hasattr(module, "main")


@pytest.mark.db
def test_day8_rfm_mart_after_build(project_root: Path) -> None:
    from tests.helpers import db_is_reachable

    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    from tests.conftest import load_module_from_path

    module = load_module_from_path(
        "run_rfm_db", project_root / "scripts/run_rfm_segmentation.py"
    )
    summary = module.run_rfm_segmentation()
    assert summary["mart_customer_rfm_rows"] == MART_CUSTOMER_RFM_ROWS
    assert summary["champions_count"] == RFM_CHAMPIONS_COUNT
    assert summary["at_risk_count"] == RFM_AT_RISK_COUNT
    assert summary["avg_recency_days"] == pytest.approx(RFM_AVG_RECENCY_DAYS, rel=1e-3)
    assert summary["avg_frequency_orders"] == pytest.approx(RFM_AVG_FREQUENCY_ORDERS, rel=1e-3)
    assert summary["avg_monetary_value"] == pytest.approx(RFM_AVG_MONETARY_VALUE, rel=1e-3)
    assert summary["segment_counts"] == RFM_SEGMENT_COUNTS


@pytest.mark.db
def test_rfm_aligns_with_customer_orders_mart(project_root: Path) -> None:
    from tests.helpers import db_is_reachable

    if not db_is_reachable(project_root):
        pytest.skip("PostgreSQL on localhost:5433 not reachable")

    from sqlalchemy import text
    from tests.conftest import load_module_from_path

    engine = load_module_from_path("rfm_align", project_root / "scripts/db_config.py").create_db_engine()
    with engine.connect() as conn:
        mismatches = conn.execute(
            text(
                """
                SELECT COUNT(*) FROM mart_customer_rfm r
                JOIN mart_customer_orders o ON r.customer_id = o.customer_id
                WHERE r.frequency_orders <> o.total_orders
                   OR r.monetary_value <> o.total_revenue
                """
            )
        ).scalar()
    assert mismatches == 0
