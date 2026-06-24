"""Tests for fixture engine orchestration."""

from datetime import date, timedelta

import pytest

from mip.orchestration.approvals import (
    ApprovalDecision,
    ApprovalDecisionType,
    ApprovalRequest,
    apply_approval_decision,
    create_approval_request,
)
from mip.orchestration.engine_fixtures import (
    FixtureEngineKind,
    FixtureEngineRunStatus,
    assert_safe_fixture_engine_result,
    create_engine_fixture_approval_request,
    fixture_engine_result_sections,
    is_engine_fixture_approved,
    orchestrate_fixture_engine,
    orchestrate_geox_fixture_engine,
    orchestrate_mmm_fixture_engine,
)
from mip.orchestration.manifest import WorkflowActionType
from mip.orchestration.plans import build_manifest_from_workflow_summary
from mip.workflows.intake import BusinessObjective, BusinessObjectiveType
from mip.workflows.orchestrator import WorkflowRunStatus, WorkflowRunSummary, run_local_workflow


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


def _weekly_rows() -> list[dict[str, object]]:
    return [
        {
            "date": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "spend": 100,
            "conversions": 10,
        }
        for index in range(12)
    ]


def _summary(objective_type: str, records: list[dict[str, object]]) -> WorkflowRunSummary:
    return run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType(objective_type)),
        records,
    )


def _approved_human_approvals(summary: WorkflowRunSummary) -> list[ApprovalRequest]:
    manifest = build_manifest_from_workflow_summary(summary)
    pending = create_approval_request(
        manifest,
        action_type=WorkflowActionType.REQUEST_HUMAN_APPROVAL,
        reason="Human review approved for fixture orchestration test.",
        required_approver_role="diagnostic_reviewer",
    )
    return [
        apply_approval_decision(
            pending,
            ApprovalDecision(
                approval_id=pending.approval_id,
                decision_type=ApprovalDecisionType.APPROVE,
                decided_by="reviewer@example.com",
                decision_note="Approved for fixture orchestration test only.",
            ),
        )
    ]


def test_mmm_eligible_summary_produces_completed_placeholder() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    result = orchestrate_mmm_fixture_engine(summary, approvals=_approved_human_approvals(summary))
    assert result.status == FixtureEngineRunStatus.COMPLETED_PLACEHOLDER
    assert result.engine_kind == FixtureEngineKind.MMM
    assert result.adapter_output_ref is not None
    assert result.trust_report_ref is not None


def test_geox_eligible_summary_produces_completed_placeholder() -> None:
    summary = _summary("experiment_design", _experiment_rows())
    result = orchestrate_geox_fixture_engine(summary, approvals=_approved_human_approvals(summary))
    assert result.status == FixtureEngineRunStatus.COMPLETED_PLACEHOLDER
    assert result.engine_kind == FixtureEngineKind.GEOX
    assert result.governance_artifact_ref is not None
    assert result.trust_report_ref is not None


def test_non_mmm_summary_blocks_mmm_fixture_orchestration() -> None:
    summary = _summary("experiment_design", _experiment_rows())
    result = orchestrate_mmm_fixture_engine(summary)
    assert result.status == FixtureEngineRunStatus.BLOCKED
    assert result.blocking_reasons


def test_non_geox_summary_blocks_geox_fixture_orchestration() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    result = orchestrate_geox_fixture_engine(summary)
    assert result.status == FixtureEngineRunStatus.BLOCKED
    assert result.blocking_reasons


def test_blocked_config_returns_blocked_result() -> None:
    summary = _summary("awareness", _weekly_rows())
    assert summary.status == WorkflowRunStatus.BLOCKED
    result = orchestrate_mmm_fixture_engine(summary)
    assert result.status == FixtureEngineRunStatus.BLOCKED
    assert result.blocking_reasons


def test_approval_required_route_does_not_complete_without_approval() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    manifest = build_manifest_from_workflow_summary(summary)
    pending = create_engine_fixture_approval_request(
        manifest.run_id,
        FixtureEngineKind.MMM,
        "Engine-scoped fixture orchestration approval required.",
    )
    result = orchestrate_mmm_fixture_engine(summary, approvals=[pending])
    assert result.status == FixtureEngineRunStatus.APPROVAL_REQUIRED
    assert result.approval_checkpoint is not None
    assert result.adapter_output_ref is None


def test_approval_for_one_engine_does_not_approve_the_other() -> None:
    mmm_summary = _summary("conversion_roi", _long_history_rows())
    geox_summary = _summary("experiment_design", _experiment_rows())
    manifest = build_manifest_from_workflow_summary(mmm_summary)
    pending = create_engine_fixture_approval_request(
        manifest.run_id,
        FixtureEngineKind.MMM,
        "MMM fixture approval required.",
    )
    approved = apply_approval_decision(
        pending,
        ApprovalDecision(
            approval_id=pending.approval_id,
            decision_type=ApprovalDecisionType.APPROVE,
            decided_by="reviewer@example.com",
            decision_note="Approved MMM fixture orchestration only.",
        ),
    )
    assert is_engine_fixture_approved(FixtureEngineKind.MMM, [approved], manifest.run_id)
    geox_manifest = build_manifest_from_workflow_summary(geox_summary)
    assert not is_engine_fixture_approved(
        FixtureEngineKind.GEOX,
        [approved],
        geox_manifest.run_id,
    )
    geox_result = orchestrate_geox_fixture_engine(
        geox_summary,
        approvals=_approved_human_approvals(geox_summary),
    )
    assert geox_result.status == FixtureEngineRunStatus.COMPLETED_PLACEHOLDER


def test_completed_placeholder_includes_adapter_output_and_trust_report_refs() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    result = orchestrate_mmm_fixture_engine(summary, approvals=_approved_human_approvals(summary))
    assert result.adapter_output_ref is not None
    assert result.trust_report_ref is not None
    assert result.governance_artifact_ref is not None


def test_result_sections_contain_fixture_labels() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    result = orchestrate_mmm_fixture_engine(summary, approvals=_approved_human_approvals(summary))
    sections = fixture_engine_result_sections(result)
    labels = sections["labels"]
    assert isinstance(labels, list)
    assert "fixture_engine_orchestration_only" in labels
    assert "not_real_engine_execution" in labels
    assert sections["disclaimer"]


def test_assert_safe_rejects_forbidden_claims() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    result = orchestrate_mmm_fixture_engine(summary)
    unsafe = result.model_copy(
        update={"blocking_reasons": ["This shows actual ROI from model results"]}
    )
    with pytest.raises(ValueError, match="forbidden phrase"):
        assert_safe_fixture_engine_result(unsafe)


def test_orchestrate_fixture_engine_dispatches_by_kind() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    result = orchestrate_fixture_engine(
        summary,
        FixtureEngineKind.MMM,
        approvals=_approved_human_approvals(summary),
    )
    assert result.engine_kind == FixtureEngineKind.MMM


def test_human_approval_required_blocks_without_approval() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    manifest = build_manifest_from_workflow_summary(summary)
    pending = create_approval_request(
        manifest,
        action_type=WorkflowActionType.REQUEST_HUMAN_APPROVAL,
        reason="Human review required before production action.",
        required_approver_role="production_reviewer",
    )
    if summary.config_draft.metadata.production_eligible:
        result = orchestrate_mmm_fixture_engine(summary, approvals=[pending])
        assert result.status == FixtureEngineRunStatus.APPROVAL_REQUIRED
    else:
        pytest.skip("summary is not production eligible")


def test_public_imports() -> None:
    from mip.orchestration import (
        FixtureEngineRunResult,
        orchestrate_mmm_fixture_engine,
    )

    assert FixtureEngineRunResult is not None
    assert callable(orchestrate_mmm_fixture_engine)
