"""Tests for human approval checkpoint contracts."""

from datetime import UTC, datetime, timedelta

import pytest

from mip.orchestration.approvals import (
    ApprovalCheckpoint,
    ApprovalDecision,
    ApprovalDecisionType,
    ApprovalRequest,
    ApprovalStatus,
    apply_approval_decision,
    assert_safe_approval_checkpoint,
    build_governed_planner_route,
    create_approval_request,
    enforce_approval_for_route,
    is_action_approved,
)
from mip.orchestration.manifest import HumanApprovalRequirement, WorkflowActionType, WorkflowRunManifest
from mip.orchestration.plans import build_manifest_from_workflow_summary
from mip.orchestration.router import PlannerDecisionStatus, route_next_actions
from mip.workflows.intake import BusinessObjective, BusinessObjectiveType
from mip.workflows.orchestrator import run_local_workflow


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


def _manifest() -> WorkflowRunManifest:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _long_history_rows(),
    )
    return build_manifest_from_workflow_summary(summary)


def _approval_request() -> ApprovalRequest:
    manifest = _manifest()
    return create_approval_request(
        manifest,
        WorkflowActionType.REQUEST_HUMAN_APPROVAL,
        "Human review required before any production or budget action.",
        "diagnostic_reviewer",
        created_at=datetime(2025, 6, 1, tzinfo=UTC),
    )


def test_create_pending_approval_request() -> None:
    request = _approval_request()
    assert request.status == ApprovalStatus.PENDING
    assert request.decided_at is None


def test_apply_approve_decision() -> None:
    request = _approval_request()
    decided = apply_approval_decision(
        request,
        ApprovalDecision(
            approval_id=request.approval_id,
            decision_type=ApprovalDecisionType.APPROVE,
            decided_by="reviewer@example.com",
            decision_note="Approved for routing visibility only.",
            decided_at=datetime(2025, 6, 2, tzinfo=UTC),
        ),
    )
    assert decided.status == ApprovalStatus.APPROVED
    assert decided.decided_by == "reviewer@example.com"


def test_apply_reject_decision() -> None:
    request = _approval_request()
    decided = apply_approval_decision(
        request,
        ApprovalDecision(
            approval_id=request.approval_id,
            decision_type=ApprovalDecisionType.REJECT,
            decided_by="reviewer@example.com",
            decision_note="Rejected pending additional evidence.",
            decided_at=datetime(2025, 6, 2, tzinfo=UTC),
        ),
    )
    assert decided.status == ApprovalStatus.REJECTED


def test_apply_expire_decision() -> None:
    request = _approval_request()
    decided = apply_approval_decision(
        request,
        ApprovalDecision(
            approval_id=request.approval_id,
            decision_type=ApprovalDecisionType.EXPIRE,
            decided_by="system@local",
            decision_note="Approval request expired in local demo state.",
            decided_at=datetime(2025, 6, 2, tzinfo=UTC),
        ),
    )
    assert decided.status == ApprovalStatus.EXPIRED


def test_approved_action_unblocks_only_matching_action() -> None:
    manifest = _manifest()
    base_route = route_next_actions(manifest)
    pending = create_approval_request(
        manifest,
        WorkflowActionType.REQUEST_HUMAN_APPROVAL,
        "Human review required.",
        "diagnostic_reviewer",
    )
    approved = apply_approval_decision(
        pending,
        ApprovalDecision(
            approval_id=pending.approval_id,
            decision_type=ApprovalDecisionType.APPROVE,
            decided_by="reviewer@example.com",
            decision_note="Approved for routing visibility only.",
        ),
    )
    enforce_approval_for_route(base_route, [approved], manifest)
    assert is_action_approved(WorkflowActionType.REQUEST_HUMAN_APPROVAL, [approved])
    assert not is_action_approved(WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE, [approved])


def test_rejected_action_remains_blocked() -> None:
    manifest = _manifest()
    base_route = route_next_actions(manifest)
    pending = create_approval_request(
        manifest,
        WorkflowActionType.REQUEST_HUMAN_APPROVAL,
        "Human review required.",
        "diagnostic_reviewer",
    )
    rejected = apply_approval_decision(
        pending,
        ApprovalDecision(
            approval_id=pending.approval_id,
            decision_type=ApprovalDecisionType.REJECT,
            decided_by="reviewer@example.com",
            decision_note="Rejected pending additional evidence.",
        ),
    )
    route = enforce_approval_for_route(base_route, [rejected], manifest)
    blocked_types = {item.action_type for item in route.blocked_decisions}
    assert WorkflowActionType.REQUEST_HUMAN_APPROVAL in blocked_types


def test_route_requiring_approval_stays_blocked_without_approval() -> None:
    manifest = _manifest()
    route, approvals = build_governed_planner_route(manifest)
    approval_decisions = [
        decision
        for decision in route.allowed_decisions
        if decision.action_type == WorkflowActionType.REQUEST_HUMAN_APPROVAL
    ]
    if not approval_decisions:
        pytest.skip("workflow summary did not require human approval")
    decision = approval_decisions[0]
    assert decision.status == PlannerDecisionStatus.REQUIRES_APPROVAL
    assert decision.approval_checkpoint is not None
    checkpoint = decision.approval_checkpoint
    assert isinstance(checkpoint, ApprovalCheckpoint)
    assert checkpoint.blocked_until_approved is True
    assert approvals[0].status == ApprovalStatus.PENDING


def test_route_moves_approved_action_to_allowed_without_execution() -> None:
    manifest = _manifest()
    base_route = route_next_actions(manifest)
    pending = create_approval_request(
        manifest,
        WorkflowActionType.REQUEST_HUMAN_APPROVAL,
        "Human review required.",
        "diagnostic_reviewer",
    )
    approved = apply_approval_decision(
        pending,
        ApprovalDecision(
            approval_id=pending.approval_id,
            decision_type=ApprovalDecisionType.APPROVE,
            decided_by="reviewer@example.com",
            decision_note="Approved for routing visibility only.",
        ),
    )
    route = enforce_approval_for_route(base_route, [approved], manifest)
    decision = next(
        item
        for item in route.allowed_decisions
        if item.action_type == WorkflowActionType.REQUEST_HUMAN_APPROVAL
    )
    assert decision.status == PlannerDecisionStatus.ALLOWED
    assert "no execution performed" in decision.reason.lower()


def test_approval_required_decision_includes_checkpoint_metadata() -> None:
    manifest = _manifest()
    route, _ = build_governed_planner_route(manifest)
    gated = [
        decision
        for decision in route.allowed_decisions
        if decision.status == PlannerDecisionStatus.REQUIRES_APPROVAL
    ]
    if not gated:
        pytest.skip("workflow summary did not require human approval")
    assert gated[0].approval_checkpoint is not None
    checkpoint = gated[0].approval_checkpoint
    assert isinstance(checkpoint, ApprovalCheckpoint)
    assert checkpoint.approval_status == ApprovalStatus.PENDING


def test_assert_safe_rejects_forbidden_claims() -> None:
    request = _approval_request().model_copy(
        update={"requested_reason": "Approve this budget recommendation now"}
    )
    with pytest.raises(ValueError, match="forbidden phrase"):
        assert_safe_approval_checkpoint(request)


def test_pending_approval_must_not_have_decided_timestamp() -> None:
    with pytest.raises(ValueError, match="pending approvals must not have a decided timestamp"):
        ApprovalRequest(
            approval_id="approval:test:1",
            action_type=WorkflowActionType.REQUEST_HUMAN_APPROVAL,
            manifest_id="run:test:1",
            requested_reason="Needs review",
            required_approver_role="reviewer",
            status=ApprovalStatus.PENDING,
            created_at=datetime(2025, 6, 1, tzinfo=UTC),
            decided_at=datetime(2025, 6, 2, tzinfo=UTC),
        )


def test_approved_checkpoint_must_not_remain_blocked() -> None:
    with pytest.raises(ValueError, match="approved checkpoints must not remain blocked"):
        ApprovalCheckpoint(
            action_type=WorkflowActionType.REQUEST_HUMAN_APPROVAL,
            requirement=HumanApprovalRequirement.REQUIRED,
            approval_status=ApprovalStatus.APPROVED,
            blocked_until_approved=True,
            reason="Approved checkpoint",
        )


def test_public_imports() -> None:
    from mip.orchestration import (
        ApprovalRequest,
        apply_approval_decision,
        create_approval_request,
        enforce_approval_for_route,
    )

    assert ApprovalRequest is not None
    assert callable(create_approval_request)
    assert callable(apply_approval_decision)
    assert callable(enforce_approval_for_route)
