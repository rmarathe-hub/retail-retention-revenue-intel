from __future__ import annotations

import pytest


@pytest.mark.docs
@pytest.mark.parametrize(
    "required",
    [
        "recency_days",
        "frequency_orders",
        "monetary_value",
        "customer_segment",
        "mart_customer_rfm",
        "06_rfm_segmentation.sql",
        "run_rfm_segmentation.py",
        "2011-12-09",
        "Champions",
        "At Risk",
        "5,881",
        "1,343",
    ],
)
def test_rfm_analysis_notes_required_content(project_root, required: str) -> None:
    text = (project_root / "docs/rfm_analysis_notes.md").read_text(encoding="utf-8")
    assert required.lower() in text.lower()


@pytest.mark.docs
def test_rfm_notes_linked_from_metric_definitions(metric_definitions_text: str) -> None:
    assert "rfm_analysis_notes.md" in metric_definitions_text
    assert "Day 8 Metrics (locked)" in metric_definitions_text
