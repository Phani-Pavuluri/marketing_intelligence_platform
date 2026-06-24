"""Tests for local workflow orchestration."""

from datetime import date, timedelta

from mip.workflows.configs import GeoXConfigDraft, MMMConfigDraft
from mip.workflows.intake import BusinessObjective, BusinessObjectiveType
from mip.workflows.orchestrator import WorkflowRunStatus, run_local_workflow


def _weekly_rows(count: int = 12, **extra: object) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(count):
        row: dict[str, object] = {
            "date": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "spend": 100,
            "conversions": 10,
        }
        row.update(extra)
        rows.append(row)
    return rows


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


def _experiment_rows() -> list[dict[str, object]]:
    return [
        {
            "date": (date(2024, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "geo": "dma_a" if index % 2 == 0 else "dma_b",
            "outcome": 100 + index,
            "spend": 50,
        }
        for index in range(60)
    ]


def test_clean_conversion_roi_returns_mmm_config() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _long_history_rows(),
    )
    assert isinstance(summary.config_draft, MMMConfigDraft)
    assert summary.status in (
        WorkflowRunStatus.COMPLETED,
        WorkflowRunStatus.COMPLETED_WITH_WARNINGS,
    )
    assert summary.config_draft.outcome_field == "conversions"


def test_awareness_with_conversions_only_is_blocked() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.AWARENESS),
        _weekly_rows(12),
    )
    assert summary.status == WorkflowRunStatus.BLOCKED
    assert summary.blocking_reasons


def test_experiment_design_returns_geox_config() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.EXPERIMENT_DESIGN),
        _experiment_rows(),
    )
    assert isinstance(summary.config_draft, GeoXConfigDraft)
    assert summary.config_draft.treatment_unit_field == "geo"


def test_warnings_aggregate_from_pipeline_stages() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _weekly_rows(12),
    )
    assert summary.warnings
    assert summary.status == WorkflowRunStatus.COMPLETED_WITH_WARNINGS


def test_blocking_reasons_aggregate_correctly() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.AWARENESS),
        _weekly_rows(12),
    )
    assert any("Conversions-only" in reason for reason in summary.blocking_reasons)


def test_recommended_next_questions_and_fixes_included() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _weekly_rows(12),
    )
    assert summary.recommended_next_questions
    assert summary.recommended_fixes


def test_narrative_summary_does_not_claim_execution() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _long_history_rows(),
    )
    lowered = summary.narrative_summary.lower()
    assert "no mmm, geox, adapter, or causal model execution was performed" in lowered
    assert "executed mmm" not in lowered
    assert "ran geox" not in lowered
    assert "estimated lift" not in lowered
