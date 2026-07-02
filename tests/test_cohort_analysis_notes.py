from __future__ import annotations

import pytest


@pytest.mark.docs
@pytest.mark.parametrize(
    "required",
    [
        "cohort month",
        "activity month",
        "retention_rate",
        "revenue_retention_rate",
        "months_since_first_purchase",
        "mart_cohort_retention",
        "05_cohort_retention.sql",
        "run_cohort_retention.py",
        "2011-12-09",
    ],
)
def test_cohort_analysis_notes_required_content(
    project_root, required: str
) -> None:
    text = (project_root / "docs/cohort_analysis_notes.md").read_text(encoding="utf-8")
    assert required.lower() in text.lower()


@pytest.mark.docs
def test_cohort_notes_linked_from_metric_definitions(metric_definitions_text: str) -> None:
    assert "cohort_analysis_notes.md" in metric_definitions_text
    assert "Cohort Retention Rate" in metric_definitions_text
    assert "Day 7 Metrics (locked)" in metric_definitions_text
