from __future__ import annotations

import pytest


@pytest.mark.docs
@pytest.mark.parametrize(
    "required",
    [
        "historical_revenue",
        "days_since_last_purchase",
        "inactivity_window",
        "potential_recoverable_revenue",
        "mart_revenue_at_risk",
        "07_revenue_at_risk.sql",
        "run_revenue_at_risk.py",
        "2011-12-09",
        "NTILE(4)",
        "10%",
        "291",
        "1,791,355",
    ],
)
def test_revenue_at_risk_notes_required_content(project_root, required: str) -> None:
    text = (project_root / "docs/revenue_at_risk_notes.md").read_text(encoding="utf-8")
    assert required.lower() in text.lower()


@pytest.mark.docs
def test_revenue_at_risk_notes_linked_from_metric_definitions(metric_definitions_text: str) -> None:
    assert "revenue_at_risk_notes.md" in metric_definitions_text
    assert "Day 9 Metrics (locked)" in metric_definitions_text
