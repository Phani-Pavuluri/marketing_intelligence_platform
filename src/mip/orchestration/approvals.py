"""Human approval checkpoint contracts and deterministic enforcement."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.orchestration.manifest import (
    HumanApprovalRequirement,
    WorkflowActionType,
    WorkflowRunManifest,
    WorkflowStep,
    step_requires_approval_gate,
)
from mip.orchestration.router import (
    PlannerDecision,
    PlannerDecisionStatus,
    PlannerRoute,
    route_next_actions,
)

_FORBIDDEN_CLAIM_PHRASES = (
    "actual roi",
    "true roi",
    "incremental lift",
    "causal impact",
    "model result",
    "budget recommendation",
    "production-ready",
    "autonomous agent executed",
)


class ApprovalStatus(StrEnum):
    """Lifecycle status for a human approval request."""

    NOT_REQUESTED = "not_requested"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    NOT_REQUIRED = "not_required"


class ApprovalDecisionType(StrEnum):
    """Human decision applied to an approval request."""

    APPROVE = "approve"
    REJECT = "reject"
    EXPIRE = "expire"


class ApprovalRequest(ContractBaseModel):
    """Local in-memory human approval request for a governed workflow action."""

    approval_id: str
    action_type: WorkflowActionType
    manifest_id: str
    requested_reason: str
    required_approver_role: str
    status: ApprovalStatus
    created_at: datetime
    decided_at: datetime | None = None
    decided_by: str | None = None
    decision_note: str | None = None

    @field_validator(
        "approval_id",
        "manifest_id",
        "requested_reason",
        "required_approver_role",
    )
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "approval request fields cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def request_consistency(self) -> ApprovalRequest:
        if self.status == ApprovalStatus.PENDING and self.decided_at is not None:
            msg = "pending approvals must not have a decided timestamp"
            raise ValueError(msg)
        if self.status in (
            ApprovalStatus.APPROVED,
            ApprovalStatus.REJECTED,
            ApprovalStatus.EXPIRED,
        ):
            if self.decided_at is None:
                msg = "decided approvals must include decided_at"
                raise ValueError(msg)
            if not self.decided_by or not self.decided_by.strip():
                msg = "decided approvals must include decided_by"
                raise ValueError(msg)
            if not self.decision_note or not self.decision_note.strip():
                msg = "decided approvals must include decision_note"
                raise ValueError(msg)
        return self


class ApprovalDecision(ContractBaseModel):
    """Human approval decision event applied to a request."""

    approval_id: str
    decision_type: ApprovalDecisionType
    decided_by: str
    decision_note: str
    decided_at: datetime | None = None

    @field_validator("approval_id", "decided_by", "decision_note")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "approval decision fields cannot be empty"
            raise ValueError(msg)
        return value


class ApprovalCheckpoint(ContractBaseModel):
    """Approval gate metadata for a workflow action."""

    action_type: WorkflowActionType
    requirement: HumanApprovalRequirement
    approval_status: ApprovalStatus
    approval_request: ApprovalRequest | None = None
    blocked_until_approved: bool
    reason: str

    @field_validator("reason")
    @classmethod
    def reason_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "approval checkpoint reason cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def checkpoint_consistency(self) -> ApprovalCheckpoint:
        if self.approval_status == ApprovalStatus.APPROVED and self.blocked_until_approved:
            msg = "approved checkpoints must not remain blocked_until_approved"
            raise ValueError(msg)
        if self.approval_status in (ApprovalStatus.REJECTED, ApprovalStatus.EXPIRED):
            if not self.blocked_until_approved:
                msg = "rejected or expired approvals must remain blocked"
                raise ValueError(msg)
        if self.approval_status in (ApprovalStatus.PENDING, ApprovalStatus.NOT_REQUESTED):
            if self.requirement != HumanApprovalRequirement.NOT_REQUIRED:
                if not self.blocked_until_approved:
                    msg = "pending or unrequested gated approvals must remain blocked"
                    raise ValueError(msg)
        return self


def create_approval_request(
    manifest: WorkflowRunManifest,
    action_type: WorkflowActionType,
    reason: str,
    required_approver_role: str,
    *,
    created_at: datetime | None = None,
) -> ApprovalRequest:
    """Create a pending local approval request for a manifest action."""
    timestamp = created_at or datetime.now(tz=UTC)
    request = ApprovalRequest(
        approval_id=f"approval:{manifest.run_id}:{_enum_value(action_type)}",
        action_type=action_type,
        manifest_id=manifest.run_id,
        requested_reason=reason,
        required_approver_role=required_approver_role,
        status=ApprovalStatus.PENDING,
        created_at=timestamp,
    )
    assert_safe_approval_checkpoint(request)
    return request


def apply_approval_decision(
    request: ApprovalRequest,
    decision: ApprovalDecision,
) -> ApprovalRequest:
    """Apply a human approval decision to a pending request."""
    if request.approval_id != decision.approval_id:
        msg = "approval decision does not match request id"
        raise ValueError(msg)
    if request.status != ApprovalStatus.PENDING:
        msg = "only pending approval requests can be decided"
        raise ValueError(msg)

    status_map = {
        ApprovalDecisionType.APPROVE: ApprovalStatus.APPROVED,
        ApprovalDecisionType.REJECT: ApprovalStatus.REJECTED,
        ApprovalDecisionType.EXPIRE: ApprovalStatus.EXPIRED,
    }
    decided_at = decision.decided_at or datetime.now(tz=UTC)
    updated = request.model_copy(
        update={
            "status": status_map[decision.decision_type],
            "decided_at": decided_at,
            "decided_by": decision.decided_by,
            "decision_note": decision.decision_note,
        }
    )
    assert_safe_approval_checkpoint(updated)
    return updated


def checkpoint_for_action(
    manifest: WorkflowRunManifest,
    action_type: WorkflowActionType,
    approval_request: ApprovalRequest | None = None,
) -> ApprovalCheckpoint:
    """Build approval checkpoint metadata for a manifest action."""
    step = _step_for(manifest, action_type)
    requirement = _requirement_for_action(manifest, action_type, step)
    if requirement == HumanApprovalRequirement.NOT_REQUIRED:
        checkpoint = ApprovalCheckpoint(
            action_type=action_type,
            requirement=requirement,
            approval_status=ApprovalStatus.NOT_REQUIRED,
            approval_request=approval_request,
            blocked_until_approved=False,
            reason="No human approval required for this action.",
        )
        assert_safe_approval_checkpoint(checkpoint)
        return checkpoint

    if approval_request is None:
        status = ApprovalStatus.NOT_REQUESTED
        reason = "Human approval has not been requested yet."
    else:
        status = approval_request.status
        reason = approval_request.requested_reason

    if status in (ApprovalStatus.REJECTED, ApprovalStatus.EXPIRED):
        reason = (
            approval_request.decision_note
            if approval_request is not None and approval_request.decision_note
            else f"Approval {status.value}."
        )

    if status == ApprovalStatus.APPROVED:
        blocked = False
    else:
        blocked = True

    checkpoint = ApprovalCheckpoint(
        action_type=action_type,
        requirement=requirement,
        approval_status=status,
        approval_request=approval_request,
        blocked_until_approved=blocked,
        reason=reason,
    )
    assert_safe_approval_checkpoint(checkpoint)
    return checkpoint


def is_action_approved(
    action_type: WorkflowActionType,
    approvals: list[ApprovalRequest],
) -> bool:
    """Return whether a specific action has an approved request."""
    action = _enum_value(action_type)
    return any(
        _enum_value(item.action_type) == action and item.status == ApprovalStatus.APPROVED
        for item in approvals
    )


def enforce_approval_for_route(
    route: PlannerRoute,
    approvals: list[ApprovalRequest],
    manifest: WorkflowRunManifest,
) -> PlannerRoute:
    """Apply approval checkpoint state to a planner route without executing actions."""
    allowed: list[PlannerDecision] = []
    blocked: list[PlannerDecision] = []
    for existing_blocked in route.blocked_decisions:
        request = _approval_for_action(
            existing_blocked.action_type,
            approvals,
            route.manifest_id,
        )
        checkpoint = checkpoint_for_action(manifest, existing_blocked.action_type, request)
        blocked.append(existing_blocked.model_copy(update={"approval_checkpoint": checkpoint}))

    for decision in route.allowed_decisions:
        request = _approval_for_action(decision.action_type, approvals, route.manifest_id)
        checkpoint = checkpoint_for_action(manifest, decision.action_type, request)
        updated = decision.model_copy(update={"approval_checkpoint": checkpoint})

        if decision.status == PlannerDecisionStatus.REQUIRES_APPROVAL:
            if request is None or request.status == ApprovalStatus.NOT_REQUESTED:
                allowed.append(updated)
                continue
            if request.status == ApprovalStatus.PENDING:
                allowed.append(updated)
                continue
            if request.status == ApprovalStatus.APPROVED:
                allowed.append(
                    updated.model_copy(
                        update={
                            "status": PlannerDecisionStatus.ALLOWED,
                            "reason": (
                                "Human approval recorded for this action; "
                                "routing only and no execution performed."
                            ),
                            "safety_notes": [
                                *updated.safety_notes,
                                "Approved for routing visibility only; action is not executed.",
                            ],
                        }
                    )
                )
                continue
            blocked.append(
                updated.model_copy(
                    update={
                        "status": PlannerDecisionStatus.BLOCKED,
                        "reason": checkpoint.reason,
                    }
                )
            )
            continue

        if checkpoint.blocked_until_approved and not is_action_approved(
            decision.action_type,
            approvals,
        ):
            blocked.append(
                updated.model_copy(
                    update={
                        "status": PlannerDecisionStatus.BLOCKED,
                        "reason": checkpoint.reason,
                    }
                )
            )
            continue

        allowed.append(updated)

    recommended = _pick_recommended_after_approval(allowed, route.recommended_next_action)
    human_approval_required = _route_human_approval_required(allowed, blocked)

    updated_route = route.model_copy(
        update={
            "allowed_decisions": allowed,
            "blocked_decisions": blocked,
            "recommended_next_action": recommended,
            "human_approval_required": human_approval_required,
            "routing_notes": [
                *route.routing_notes,
                "Approval checkpoints are local demo state only; no actions are executed.",
            ],
        }
    )
    return updated_route


def approval_requests_for_route(
    manifest: WorkflowRunManifest,
    route: PlannerRoute,
) -> list[ApprovalRequest]:
    """Create pending approval requests for approval-gated route decisions."""
    requests: list[ApprovalRequest] = []
    for decision in route.allowed_decisions:
        if decision.status != PlannerDecisionStatus.REQUIRES_APPROVAL:
            continue
        requests.append(
            create_approval_request(
                manifest,
                decision.action_type,
                decision.reason,
                _required_approver_role(decision.human_approval_requirement),
            )
        )
    return requests


def finalize_planner_route(
    manifest: WorkflowRunManifest,
    route: PlannerRoute,
    approvals: list[ApprovalRequest] | None = None,
) -> tuple[PlannerRoute, list[ApprovalRequest]]:
    """Attach approval requests and enforce checkpoint state on a planner route."""
    active_approvals = list(approvals) if approvals is not None else approval_requests_for_route(
        manifest,
        route,
    )
    finalized = enforce_approval_for_route(route, active_approvals, manifest)
    return finalized, active_approvals


def approval_checkpoints_for_route(
    manifest: WorkflowRunManifest,
    route: PlannerRoute,
    approvals: list[ApprovalRequest],
) -> list[ApprovalCheckpoint]:
    """Collect approval checkpoints for all routed actions."""
    action_types = {
        decision.action_type
        for decision in [*route.allowed_decisions, *route.blocked_decisions]
    }
    checkpoints: list[ApprovalCheckpoint] = []
    for action_type in action_types:
        request = _approval_for_action(action_type, approvals, route.manifest_id)
        checkpoints.append(checkpoint_for_action(manifest, action_type, request))
    return checkpoints


def format_approval_checkpoints_for_display(
    checkpoints: list[ApprovalCheckpoint],
) -> dict[str, object]:
    """Format approval checkpoints for display-only UI sections."""
    for checkpoint in checkpoints:
        assert_safe_approval_checkpoint(checkpoint)
    gated = [
        checkpoint
        for checkpoint in checkpoints
        if checkpoint.requirement != HumanApprovalRequirement.NOT_REQUIRED
        or checkpoint.approval_status != ApprovalStatus.NOT_REQUIRED
    ]
    return {
        "safety_note": (
            "Approvals are local demo state only and do not execute workflow actions."
        ),
        "checkpoints": [_checkpoint_display(checkpoint) for checkpoint in gated],
    }


def build_governed_planner_route(
    manifest: WorkflowRunManifest,
    approvals: list[ApprovalRequest] | None = None,
) -> tuple[PlannerRoute, list[ApprovalRequest]]:
    """Build a planner route with approval checkpoint enforcement."""
    route = route_next_actions(manifest)
    return finalize_planner_route(manifest, route, approvals)


def assert_safe_approval_checkpoint(obj: ApprovalRequest | ApprovalCheckpoint) -> None:
    """Raise if approval object text includes forbidden causal or production claims."""
    combined = obj.model_dump_json().lower()
    for phrase in _FORBIDDEN_CLAIM_PHRASES:
        if phrase in combined:
            msg = f"approval object must not include forbidden phrase: {phrase}"
            raise ValueError(msg)
    if _contains_false_production_ready_claim(combined):
        msg = "approval object must not claim production-ready status"
        raise ValueError(msg)


def _checkpoint_display(checkpoint: ApprovalCheckpoint) -> dict[str, object]:
    request = checkpoint.approval_request
    return {
        "action_type": _enum_value(checkpoint.action_type),
        "requirement": _enum_value(checkpoint.requirement),
        "approval_status": _enum_value(checkpoint.approval_status),
        "blocked_until_approved": checkpoint.blocked_until_approved,
        "reason": checkpoint.reason,
        "approval_id": request.approval_id if request is not None else None,
        "required_approver_role": request.required_approver_role if request is not None else None,
        "decided_by": request.decided_by if request is not None else None,
        "decision_note": request.decision_note if request is not None else None,
    }


def _approval_for_action(
    action_type: WorkflowActionType,
    approvals: list[ApprovalRequest],
    manifest_id: str,
) -> ApprovalRequest | None:
    action = _enum_value(action_type)
    for item in approvals:
        if item.manifest_id == manifest_id and _enum_value(item.action_type) == action:
            return item
    return None


def _requirement_for_action(
    manifest: WorkflowRunManifest,
    action_type: WorkflowActionType,
    step: WorkflowStep | None,
) -> HumanApprovalRequirement:
    if step is not None and step_requires_approval_gate(step):
        return step.human_approval_requirement
    if action_type == WorkflowActionType.REQUEST_HUMAN_APPROVAL:
        approval_step = _step_for(manifest, WorkflowActionType.REQUEST_HUMAN_APPROVAL)
        if approval_step is not None:
            return approval_step.human_approval_requirement
    return HumanApprovalRequirement.NOT_REQUIRED


def _required_approver_role(requirement: HumanApprovalRequirement) -> str:
    if requirement == HumanApprovalRequirement.REQUIRED:
        return "production_reviewer"
    if requirement == HumanApprovalRequirement.BLOCKED_UNTIL_APPROVED:
        return "workflow_reviewer"
    return "diagnostic_reviewer"


def _pick_recommended_after_approval(
    allowed: list[PlannerDecision],
    previous: WorkflowActionType | None,
) -> WorkflowActionType | None:
    routable = [
        decision
        for decision in allowed
        if decision.status == PlannerDecisionStatus.ALLOWED
    ]
    if not routable:
        pending = [
            decision
            for decision in allowed
            if decision.status == PlannerDecisionStatus.REQUIRES_APPROVAL
        ]
        return pending[0].action_type if pending else None
    allowed_types = {decision.action_type for decision in routable}
    if previous is not None and previous in allowed_types:
        return previous
    return routable[0].action_type


def _route_human_approval_required(
    allowed: list[PlannerDecision],
    blocked: list[PlannerDecision],
) -> bool:
    for decision in [*allowed, *blocked]:
        checkpoint = decision.approval_checkpoint
        if checkpoint is None:
            continue
        approval_status = getattr(checkpoint, "approval_status", None)
        requirement = getattr(checkpoint, "requirement", None)
        if approval_status in (
            ApprovalStatus.PENDING,
            ApprovalStatus.NOT_REQUESTED,
        ) and requirement != HumanApprovalRequirement.NOT_REQUIRED:
            return True
        if decision.status == PlannerDecisionStatus.REQUIRES_APPROVAL:
            return True
    return False


def _step_for(
    manifest: WorkflowRunManifest,
    action_type: WorkflowActionType,
) -> WorkflowStep | None:
    for step in manifest.plan.steps:
        if step.action_type == action_type:
            return step
    return None


def _contains_false_production_ready_claim(text: str) -> bool:
    for match in re.finditer(r"production[- ]ready", text):
        start = match.start()
        prefix = text[max(0, start - 4) : start]
        if not prefix.endswith("not "):
            return True
    return False


def _enum_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))
