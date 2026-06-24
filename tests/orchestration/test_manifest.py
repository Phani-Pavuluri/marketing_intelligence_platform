"""Tests for workflow manifest contracts."""

from datetime import UTC, datetime

import pytest

from mip.orchestration.manifest import (
    HumanApprovalRequirement,
    WorkflowActionType,
    WorkflowArtifactRef,
    WorkflowPlan,
    WorkflowRunManifest,
    WorkflowStep,
    WorkflowStepStatus,
    assert_safe_workflow_manifest,
)


def _sample_plan() -> WorkflowPlan:
    return WorkflowPlan(
        plan_id="plan:test",
        objective_type="conversion_roi",
        steps=[
            WorkflowStep(
                step_id="step:parse_input",
                action_type=WorkflowActionType.PARSE_INPUT,
                status=WorkflowStepStatus.PLANNED,
                completion_note="planned deterministic step",
            )
        ],
    )


def _sample_manifest() -> WorkflowRunManifest:
    return WorkflowRunManifest(
        run_id="run:test:1",
        created_at=datetime(2025, 6, 1, tzinfo=UTC),
        source="local_deterministic_workflow",
        objective_marker="conversion_roi:marker",
        plan=_sample_plan(),
    )


def test_blocked_step_requires_block_reason() -> None:
    with pytest.raises(ValueError, match="blocked steps require a block reason"):
        WorkflowStep(
            step_id="step:draft_config",
            action_type=WorkflowActionType.DRAFT_CONFIG,
            status=WorkflowStepStatus.BLOCKED,
        )


def test_completed_step_requires_output_or_note() -> None:
    with pytest.raises(ValueError, match="completed steps require output artifacts"):
        WorkflowStep(
            step_id="step:profile_data",
            action_type=WorkflowActionType.PROFILE_DATA,
            status=WorkflowStepStatus.COMPLETED,
        )


def test_requires_approval_step_requires_approval_metadata() -> None:
    with pytest.raises(ValueError, match="requires_approval steps must declare human approval"):
        WorkflowStep(
            step_id="step:request_human_approval",
            action_type=WorkflowActionType.REQUEST_HUMAN_APPROVAL,
            status=WorkflowStepStatus.REQUIRES_APPROVAL,
            human_approval_requirement=HumanApprovalRequirement.NOT_REQUIRED,
            completion_note="needs approval metadata",
        )


def test_assert_safe_rejects_forbidden_claims() -> None:
    manifest = _sample_manifest().model_copy(
        update={"completion_note": "This run produced actual ROI from model results"}
    )
    with pytest.raises(ValueError, match="forbidden phrase"):
        assert_safe_workflow_manifest(manifest)


def test_assert_safe_rejects_production_ready_claim() -> None:
    manifest = _sample_manifest().model_copy(
        update={"completion_note": "This workflow is production-ready"}
    )
    with pytest.raises(ValueError, match="production-ready"):
        assert_safe_workflow_manifest(manifest)


def test_completed_step_accepts_output_artifacts() -> None:
    step = WorkflowStep(
        step_id="step:profile_data",
        action_type=WorkflowActionType.PROFILE_DATA,
        status=WorkflowStepStatus.COMPLETED,
        output_artifacts=[
            WorkflowArtifactRef(artifact_type="dataset_profile", artifact_id="profile:1")
        ],
    )
    assert step.status == WorkflowStepStatus.COMPLETED


def test_step_requires_approval_gate() -> None:
    from mip.orchestration.manifest import (
        HumanApprovalRequirement,
        WorkflowActionType,
        WorkflowStep,
        WorkflowStepStatus,
        step_requires_approval_gate,
    )

    gated = WorkflowStep(
        step_id="step:request_human_approval",
        action_type=WorkflowActionType.REQUEST_HUMAN_APPROVAL,
        status=WorkflowStepStatus.REQUIRES_APPROVAL,
        human_approval_requirement=HumanApprovalRequirement.RECOMMENDED,
        completion_note="needs review",
    )
    assert step_requires_approval_gate(gated) is True


def test_public_imports() -> None:
    from mip.orchestration.manifest import WorkflowRunManifest

    assert WorkflowRunManifest is not None
