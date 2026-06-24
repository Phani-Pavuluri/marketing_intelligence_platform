"""Tests for deterministic workflow summary explanations."""

from datetime import date, timedelta

from mip.llm.explanations import (
    explain_blockers,
    explain_next_steps,
    explain_workflow_summary,
)
from mip.workflows.intake import BusinessObjective, BusinessObjectiveType
from mip.workflows.orchestrator import WorkflowRunStatus, run_local_workflow


def _weekly_rows(count: int = 12) -> list[dict[str, object]]:
    return [
        {
            "date": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "channel": "search",
            "spend": 100 + index,
            "conversions": 10 + index,
        }
        for index in range(count)
    ]


def _long_history_rows() -> list[dict[str, object]]:
    return [
        {
            "date": (date(2024, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "spend": 100,
            "conversions": 10,
            "channel": "search" if index % 2 == 0 else "social",
            "geo": "us" if index % 2 == 0 else "uk",
        }
        for index in range(60)
    ]


def test_explanation_is_deterministic() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _weekly_rows(12),
    )
    first = explain_workflow_summary(summary)
    second = explain_workflow_summary(summary)
    assert first == second


def test_blocked_awareness_workflow_explanation() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.AWARENESS),
        _weekly_rows(12),
    )
    explanation = explain_workflow_summary(summary)
    assert summary.status == WorkflowRunStatus.BLOCKED
    assert "awareness" in explanation
    assert "blocked" in explanation.lower()
    assert "This workflow is blocked because:" in explanation


def test_clean_conversion_workflow_explanation() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _long_history_rows(),
    )
    explanation = explain_workflow_summary(summary)
    assert "conversion_roi" in explanation
    assert summary.status in (
        WorkflowRunStatus.COMPLETED,
        WorkflowRunStatus.COMPLETED_WITH_WARNINGS,
    )
    assert "completed" in explanation.lower()


def test_warning_and_fix_explanation() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _weekly_rows(12),
    )
    explanation = explain_workflow_summary(summary)
    assert summary.warnings
    assert summary.recommended_fixes
    assert "Warnings to review:" in explanation
    assert "Recommended fixes:" in explanation
    assert explain_next_steps(summary).startswith("Recommended")


def test_explanation_does_not_claim_model_output() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _long_history_rows(),
    )
    explanation = explain_workflow_summary(summary).lower()
    assert "no mmm, geox, adapter, or causal model execution was performed" in explanation
    assert "estimated lift" not in explanation
    assert "causal impact" not in explanation
    assert "budget recommendation" not in explanation
    assert "model results" not in explanation


def test_explain_blockers_without_blockers() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _long_history_rows(),
    )
    assert "no blocking reasons" in explain_blockers(summary).lower()
