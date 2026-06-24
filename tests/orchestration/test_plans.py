"""Tests for workflow plan and manifest builders."""

from datetime import UTC, datetime, timedelta

from mip.orchestration.manifest import (
    WorkflowActionType,
    WorkflowRunManifest,
    WorkflowStep,
    WorkflowStepStatus,
)
from mip.orchestration.plans import (
    build_manifest_from_workflow_summary,
    build_manifest_with_mmm_fixture,
    build_plan_from_workflow_summary,
)
from mip.reports.mmm_fixture import build_mmm_fixture_report
from mip.workflows.intake import BusinessObjective, BusinessObjectiveType
from mip.workflows.orchestrator import WorkflowRunStatus, WorkflowRunSummary, run_local_workflow


def _weekly_rows(count: int = 12) -> list[dict[str, object]]:
    base = datetime(2025, 1, 1, tzinfo=UTC)
    return [
        {
            "date": (base + timedelta(days=7 * index)).date().isoformat(),
            "channel": "search",
            "spend": 100 + index,
            "conversions": 10 + index,
        }
        for index in range(count)
    ]


def _long_history_rows() -> list[dict[str, object]]:
    base = datetime(2024, 1, 1, tzinfo=UTC)
    return [
        {
            "date": (base + timedelta(days=7 * index)).date().isoformat(),
            "spend": 100,
            "conversions": 10,
            "channel": "search" if index % 2 == 0 else "social",
            "geo": "us" if index % 2 == 0 else "uk",
        }
        for index in range(60)
    ]


def _summary(objective_type: str, records: list[dict[str, object]]) -> WorkflowRunSummary:
    return run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType(objective_type)),
        records,
    )


def _step(manifest: WorkflowRunManifest, action: WorkflowActionType) -> WorkflowStep:
    for step in manifest.plan.steps:
        if step.action_type == action:
            return step
    msg = f"missing step: {action}"
    raise AssertionError(msg)


def test_clean_conversion_roi_manifest_has_completed_intake_steps() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    manifest = build_manifest_from_workflow_summary(
        summary,
        created_at=datetime(2025, 6, 1, tzinfo=UTC),
    )
    assert manifest.agentic_planning_enabled is False
    assert _step(manifest, WorkflowActionType.PROFILE_DATA).status in (
        WorkflowStepStatus.COMPLETED,
        WorkflowStepStatus.WARNING,
    )
    assert _step(manifest, WorkflowActionType.DRAFT_CONFIG).status in (
        WorkflowStepStatus.COMPLETED,
        WorkflowStepStatus.WARNING,
    )


def test_blocked_awareness_manifest_blocks_or_skips_downstream() -> None:
    summary = _summary("awareness", _weekly_rows(12))
    assert summary.status == WorkflowRunStatus.BLOCKED
    manifest = build_manifest_from_workflow_summary(summary)
    adapter_step = _step(manifest, WorkflowActionType.BUILD_ADAPTER_INPUT)
    assert adapter_step.status in (WorkflowStepStatus.BLOCKED, WorkflowStepStatus.SKIPPED)
    assert manifest.blockers


def test_mmm_fixture_report_adds_placeholder_artifact_refs() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    fixture_report = build_mmm_fixture_report(summary)
    assert fixture_report is not None
    manifest = build_manifest_with_mmm_fixture(summary, fixture_report)
    artifact_types = {ref.artifact_type for ref in manifest.artifact_refs}
    assert "decision_surface_fixture" in artifact_types
    assert "mmm_fixture_report" in artifact_types
    render_step = _step(manifest, WorkflowActionType.RENDER_REPORT)
    assert render_step.status == WorkflowStepStatus.COMPLETED


def test_build_plan_from_summary_marks_steps_planned() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    plan = build_plan_from_workflow_summary(summary)
    assert all(step.status == WorkflowStepStatus.PLANNED for step in plan.steps)


def test_manifest_does_not_claim_forbidden_output() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    manifest = build_manifest_from_workflow_summary(summary)
    combined = manifest.model_dump_json().lower()
    assert "actual roi" not in combined
    assert "budget recommendation" not in combined
    assert "autonomous agent executed" not in combined


def test_public_imports() -> None:
    from mip.orchestration import (
        WorkflowRunManifest,
        build_manifest_from_workflow_summary,
        build_plan_from_workflow_summary,
    )

    assert callable(build_plan_from_workflow_summary)
    assert callable(build_manifest_from_workflow_summary)
    assert WorkflowRunManifest is not None
