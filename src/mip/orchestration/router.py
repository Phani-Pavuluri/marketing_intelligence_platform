"""Governed deterministic planner/router over workflow manifests."""

from __future__ import annotations

import re
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.orchestration.manifest import (
    HumanApprovalRequirement,
    WorkflowActionType,
    WorkflowRunManifest,
    WorkflowStep,
    WorkflowStepStatus,
)
from mip.orchestration.plans import (
    build_manifest_from_workflow_summary,
    build_manifest_with_mmm_fixture,
)
from mip.reports.mmm_fixture import MMMFixtureReport
from mip.workflows.orchestrator import WorkflowRunSummary

_FORBIDDEN_CLAIM_PHRASES = (
    "actual roi",
    "true roi",
    "incremental lift",
    "causal impact",
    "model result",
    "budget recommendation",
    "production-ready",
    "autonomous agent executed",
    "llm chose this step",
)

_MMM_OBJECTIVES = frozenset(
    {"conversion_roi", "revenue_roi", "budget_allocation", "mmm_calibration"}
)


class PlannerDecisionStatus(StrEnum):
    """Routing status for a candidate next workflow action."""

    ALLOWED = "allowed"
    BLOCKED = "blocked"
    REQUIRES_APPROVAL = "requires_approval"
    NOT_APPLICABLE = "not_applicable"


class PlannerDecision(ContractBaseModel):
    """Governed routing decision for a single workflow action."""

    action_type: WorkflowActionType
    status: PlannerDecisionStatus
    reason: str
    required_inputs: list[str] = Field(default_factory=list)
    produced_artifact_type: str | None = None
    produced_artifact_marker: str | None = None
    human_approval_requirement: HumanApprovalRequirement = HumanApprovalRequirement.NOT_REQUIRED
    approval_checkpoint: object | None = None
    safety_notes: list[str] = Field(default_factory=list)

    @field_validator("reason")
    @classmethod
    def reason_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "planner decision reason cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("required_inputs", "safety_notes")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "required_inputs and safety_notes cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def decision_consistency(self) -> PlannerDecision:
        if self.status == PlannerDecisionStatus.BLOCKED and not self.reason.strip():
            msg = "blocked decisions require a reason"
            raise ValueError(msg)
        if self.status == PlannerDecisionStatus.REQUIRES_APPROVAL:
            if self.human_approval_requirement == HumanApprovalRequirement.NOT_REQUIRED:
                msg = "approval-required decisions must declare human approval requirement"
                raise ValueError(msg)
        return self


class PlannerRoute(ContractBaseModel):
    """Governed routing view over a workflow run manifest."""

    manifest_id: str
    agentic_planning_enabled: bool = False
    allowed_decisions: list[PlannerDecision] = Field(default_factory=list)
    blocked_decisions: list[PlannerDecision] = Field(default_factory=list)
    recommended_next_action: WorkflowActionType | None = None
    human_approval_required: bool = False
    routing_notes: list[str] = Field(default_factory=list)

    @field_validator("manifest_id")
    @classmethod
    def manifest_id_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "manifest_id cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("routing_notes")
    @classmethod
    def routing_notes_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "routing_notes cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def route_consistency(self) -> PlannerRoute:
        allowed_actions = {
            decision.action_type
            for decision in self.allowed_decisions
            if decision.status
            in (PlannerDecisionStatus.ALLOWED, PlannerDecisionStatus.REQUIRES_APPROVAL)
        }
        if self.recommended_next_action is not None and allowed_actions:
            if self.recommended_next_action not in allowed_actions:
                msg = "recommended next action must be one of the allowed decisions"
                raise ValueError(msg)
        if self.recommended_next_action is not None and not allowed_actions:
            msg = "recommended next action cannot be set when no actions are allowed"
            raise ValueError(msg)
        return self


def route_next_actions(manifest: WorkflowRunManifest) -> PlannerRoute:
    """Select allowed, blocked, and approval-gated next actions from a manifest."""
    if manifest.agentic_planning_enabled:
        msg = "planner router requires agentic_planning_enabled=False"
        raise ValueError(msg)

    marker = manifest.plan.source_config_marker or manifest.run_id
    workflow_blocked = bool(manifest.blockers)
    has_fixture = _has_mmm_fixture(manifest)
    objective = manifest.plan.objective_type

    allowed: list[PlannerDecision] = []
    blocked: list[PlannerDecision] = []
    routing_notes = [
        "Governed deterministic planner router only; no autonomous agent execution.",
        "Router selects safe next actions; it does not execute workflow steps.",
    ]

    blocked.append(
        _blocked_decision(
            WorkflowActionType.BUILD_ADAPTER_INPUT,
            "Real MMM/GeoX engine execution is not available in this phase.",
            safety_notes=["Only governed adapter fixture placeholders are permitted."],
        )
    )

    if has_fixture:
        _route_mmm_fixture_manifest(manifest, marker, allowed, blocked, routing_notes)
    elif workflow_blocked:
        _route_blocked_workflow(manifest, marker, objective, allowed, blocked, routing_notes)
    else:
        _route_clean_workflow(manifest, marker, objective, allowed, blocked, routing_notes)

    if not has_fixture:
        _append_approval_decisions(manifest, allowed, blocked)
    _append_production_blocks(manifest, allowed, blocked, has_fixture=has_fixture)

    recommended = _pick_recommended(allowed, manifest, has_fixture, workflow_blocked, objective)
    human_approval_required = _human_approval_required(allowed, manifest)

    route = PlannerRoute(
        manifest_id=manifest.run_id,
        allowed_decisions=allowed,
        blocked_decisions=blocked,
        recommended_next_action=recommended,
        human_approval_required=human_approval_required,
        routing_notes=routing_notes,
    )
    assert_safe_planner_route(route)
    return route


def planner_route_from_summary(
    summary: WorkflowRunSummary,
    approvals: list[object] | None = None,
) -> PlannerRoute:
    """Build a manifest and governed planner route from a workflow summary."""
    from mip.orchestration.approvals import build_governed_planner_route

    manifest = build_manifest_from_workflow_summary(summary)
    route, _ = build_governed_planner_route(manifest, approvals)  # type: ignore[arg-type]
    return route


def planner_route_with_mmm_fixture(
    summary: WorkflowRunSummary,
    mmm_fixture_report: MMMFixtureReport,
    approvals: list[object] | None = None,
) -> PlannerRoute:
    """Build a manifest with MMM fixture lineage and return the governed route."""
    from mip.orchestration.approvals import build_governed_planner_route

    manifest = build_manifest_with_mmm_fixture(summary, mmm_fixture_report)
    route, _ = build_governed_planner_route(manifest, approvals)  # type: ignore[arg-type]
    return route


def assert_safe_planner_route(route: PlannerRoute) -> None:
    """Raise if planner route text claims forbidden causal, model, or agentic execution."""
    combined = route.model_dump_json().lower()
    for phrase in _FORBIDDEN_CLAIM_PHRASES:
        if phrase in combined:
            msg = f"planner route must not include forbidden phrase: {phrase}"
            raise ValueError(msg)
    if _contains_false_production_ready_claim(combined):
        msg = "planner route must not claim production-ready status"
        raise ValueError(msg)


def format_planner_route_for_display(route: PlannerRoute) -> dict[str, object]:
    """Format a planner route for UI display without executing actions."""
    assert_safe_planner_route(route)
    return {
        "manifest_id": route.manifest_id,
        "agentic_planning_enabled": route.agentic_planning_enabled,
        "recommended_next_action": _enum_value(route.recommended_next_action)
        if route.recommended_next_action is not None
        else None,
        "human_approval_required": route.human_approval_required,
        "routing_notes": list(route.routing_notes),
        "allowed_actions": [_decision_display(decision) for decision in route.allowed_decisions],
        "blocked_actions": [_decision_display(decision) for decision in route.blocked_decisions],
        "safety_notes": _collect_safety_notes(route),
    }


def _route_clean_workflow(
    manifest: WorkflowRunManifest,
    marker: str,
    objective: str,
    allowed: list[PlannerDecision],
    blocked: list[PlannerDecision],
    routing_notes: list[str],
) -> None:
    allowed.append(
        PlannerDecision(
            action_type=WorkflowActionType.RENDER_REPORT,
            status=PlannerDecisionStatus.ALLOWED,
            reason="Render the governed local workflow summary report.",
            produced_artifact_type="workflow_run_summary",
            produced_artifact_marker=marker,
            safety_notes=["Display-only; does not execute engines or change trust verdicts."],
        )
    )

    if _fixture_demo_eligible(manifest, objective):
        allowed.append(
            PlannerDecision(
                action_type=WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE,
                status=PlannerDecisionStatus.ALLOWED,
                reason="Run the governed MMM fixture demo over the existing config draft.",
                produced_artifact_type="mmm_fixture_report",
                produced_artifact_marker=marker,
                safety_notes=[
                    "Adapter fixture placeholder only; not model execution.",
                    "Diagnostic governance demo; not decision-ready.",
                ],
            )
        )
        routing_notes.append(
            "MMM fixture demo is allowed only as a governed placeholder path."
        )
    else:
        routing_notes.append("MMM fixture demo is not applicable for this objective.")

    blocked.append(
        _blocked_decision(
            WorkflowActionType.MAP_TO_GOVERNANCE_ARTIFACT,
            "Production decision surfaces require certified engine outputs and gates.",
            safety_notes=["Fixture-only governance artifacts are not production decisions."],
        )
    )


def _route_blocked_workflow(
    manifest: WorkflowRunManifest,
    marker: str,
    objective: str,
    allowed: list[PlannerDecision],
    blocked: list[PlannerDecision],
    routing_notes: list[str],
) -> None:
    blocker_text = "; ".join(manifest.blockers)
    required_inputs = _missing_input_hints(manifest, objective)

    allowed.append(
        PlannerDecision(
            action_type=WorkflowActionType.EVALUATE_FEASIBILITY,
            status=PlannerDecisionStatus.ALLOWED,
            reason="Review feasibility blockers and objective constraints.",
            produced_artifact_type="objective_feasibility_report",
            produced_artifact_marker=f"feasibility:{marker}",
            safety_notes=["Explain blockers only; no estimand certification."],
        )
    )
    allowed.append(
        PlannerDecision(
            action_type=WorkflowActionType.BUILD_READINESS_REPORT,
            status=PlannerDecisionStatus.ALLOWED,
            reason="Review data readiness gaps and recommended fixes.",
            produced_artifact_type="data_readiness_report",
            produced_artifact_marker=f"readiness:{marker}",
            safety_notes=["Diagnostic review only."],
        )
    )
    allowed.append(
        PlannerDecision(
            action_type=WorkflowActionType.PARSE_INPUT,
            status=PlannerDecisionStatus.ALLOWED,
            reason="Request missing objective inputs and KPI fields before adapter work.",
            required_inputs=required_inputs,
            safety_notes=["Collect missing inputs; do not auto-approve downstream actions."],
        )
    )
    allowed.append(
        PlannerDecision(
            action_type=WorkflowActionType.RENDER_REPORT,
            status=PlannerDecisionStatus.ALLOWED,
            reason="Render the blocked workflow diagnostic report.",
            produced_artifact_type="workflow_run_summary",
            produced_artifact_marker=marker,
            safety_notes=[f"Blockers: {blocker_text}"],
        )
    )
    routing_notes.append("Blocked workflow: adapter and model execution remain unavailable.")

    for action, reason in (
        (
            WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE,
            "Adapter fixture execution is blocked until workflow blockers are resolved.",
        ),
        (
            WorkflowActionType.MAP_TO_GOVERNANCE_ARTIFACT,
            "Governance artifact mapping is blocked until workflow blockers are resolved.",
        ),
        (
            WorkflowActionType.BUILD_TRUST_REPORT,
            (
                "TrustReport build from adapter outputs is blocked "
                "until workflow blockers are resolved."
            ),
        ),
    ):
        blocked.append(
            _blocked_decision(
                action,
                reason,
                safety_notes=["Resolve blockers before any adapter or model path."],
            )
        )


def _route_mmm_fixture_manifest(
    manifest: WorkflowRunManifest,
    marker: str,
    allowed: list[PlannerDecision],
    blocked: list[PlannerDecision],
    routing_notes: list[str],
) -> None:
    fixture_ref = next(
        ref for ref in manifest.artifact_refs if ref.artifact_type == "mmm_fixture_report"
    )
    allowed.append(
        PlannerDecision(
            action_type=WorkflowActionType.RENDER_REPORT,
            status=PlannerDecisionStatus.ALLOWED,
            reason="Render the placeholder MMM governance report only.",
            produced_artifact_type="mmm_fixture_report",
            produced_artifact_marker=fixture_ref.artifact_id,
            safety_notes=[
                "Placeholder governance report only; not model execution.",
                "Diagnostic only and not decision-ready.",
            ],
        )
    )
    routing_notes.append("MMM fixture manifest: only placeholder report rendering is allowed.")

    blocked.extend(
        [
            _blocked_decision(
                WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE,
                "Fixture already produced; real MMM engine execution remains blocked.",
            ),
            _blocked_decision(
                WorkflowActionType.REQUEST_HUMAN_APPROVAL,
                "Budget action and production recommendation are blocked in this phase.",
                safety_notes=["Human approval may be reviewed later; never auto-approved."],
            ),
            _blocked_decision(
                WorkflowActionType.MAP_TO_GOVERNANCE_ARTIFACT,
                "Production decision surfaces require certified engine outputs and gates.",
            ),
        ]
    )


def _append_approval_decisions(
    manifest: WorkflowRunManifest,
    allowed: list[PlannerDecision],
    blocked: list[PlannerDecision],
) -> None:
    approval_step = _step_for(manifest, WorkflowActionType.REQUEST_HUMAN_APPROVAL)
    if approval_step is None:
        return

    requirement = approval_step.human_approval_requirement
    if approval_step.status == WorkflowStepStatus.BLOCKED:
        reason = (
            approval_step.block_reason.message
            if approval_step.block_reason is not None
            else "Human approval is blocked until workflow blockers are resolved."
        )
        blocked.append(
            _blocked_decision(
                WorkflowActionType.REQUEST_HUMAN_APPROVAL,
                reason,
                human_approval_requirement=requirement,
            )
        )
        return

    if approval_step.status == WorkflowStepStatus.REQUIRES_APPROVAL:
        allowed.append(
            PlannerDecision(
                action_type=WorkflowActionType.REQUEST_HUMAN_APPROVAL,
                status=PlannerDecisionStatus.REQUIRES_APPROVAL,
                reason="Human review is required before any production or budget action.",
                human_approval_requirement=requirement,
                safety_notes=["No autonomous approval is permitted."],
            )
        )


def _append_production_blocks(
    manifest: WorkflowRunManifest,
    allowed: list[PlannerDecision],
    blocked: list[PlannerDecision],
    *,
    has_fixture: bool = False,
) -> None:
    if has_fixture:
        return
    approval_step = _step_for(manifest, WorkflowActionType.REQUEST_HUMAN_APPROVAL)
    approval_pending = approval_step is not None and approval_step.status in (
        WorkflowStepStatus.REQUIRES_APPROVAL,
        WorkflowStepStatus.BLOCKED,
    )
    if approval_pending:
        return

    if any(
        decision.action_type == WorkflowActionType.REQUEST_HUMAN_APPROVAL
        for decision in blocked
    ):
        return

    blocked.append(
        _blocked_decision(
            WorkflowActionType.REQUEST_HUMAN_APPROVAL,
            "Production decision and budget recommendation actions are blocked in this phase.",
            safety_notes=["No automatic human approval or budget action is permitted."],
        )
    )


def _pick_recommended(
    allowed: list[PlannerDecision],
    manifest: WorkflowRunManifest,
    has_fixture: bool,
    workflow_blocked: bool,
    objective: str,
) -> WorkflowActionType | None:
    routable = [
        decision
        for decision in allowed
        if decision.status
        in (PlannerDecisionStatus.ALLOWED, PlannerDecisionStatus.REQUIRES_APPROVAL)
    ]
    if not routable:
        return None

    if has_fixture:
        priority: tuple[WorkflowActionType, ...] = (WorkflowActionType.RENDER_REPORT,)
    elif workflow_blocked:
        priority = (
            WorkflowActionType.PARSE_INPUT,
            WorkflowActionType.RENDER_REPORT,
            WorkflowActionType.EVALUATE_FEASIBILITY,
            WorkflowActionType.BUILD_READINESS_REPORT,
        )
        if objective != "awareness":
            priority = (
                WorkflowActionType.RENDER_REPORT,
                WorkflowActionType.PARSE_INPUT,
                WorkflowActionType.EVALUATE_FEASIBILITY,
            )
    else:
        priority = (
            WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE,
            WorkflowActionType.RENDER_REPORT,
            WorkflowActionType.REQUEST_HUMAN_APPROVAL,
        )

    allowed_types = {decision.action_type for decision in routable}
    for action in priority:
        if action in allowed_types:
            return action
    return routable[0].action_type


def _human_approval_required(
    allowed: list[PlannerDecision],
    manifest: WorkflowRunManifest,
) -> bool:
    for decision in allowed:
        if decision.status == PlannerDecisionStatus.REQUIRES_APPROVAL:
            return True
        if decision.human_approval_requirement in (
            HumanApprovalRequirement.REQUIRED,
            HumanApprovalRequirement.BLOCKED_UNTIL_APPROVED,
        ):
            return True
    approval_step = _step_for(manifest, WorkflowActionType.REQUEST_HUMAN_APPROVAL)
    if approval_step is None:
        return False
    return approval_step.human_approval_requirement in (
        HumanApprovalRequirement.REQUIRED,
        HumanApprovalRequirement.RECOMMENDED,
        HumanApprovalRequirement.BLOCKED_UNTIL_APPROVED,
    )


def _fixture_demo_eligible(manifest: WorkflowRunManifest, objective: str) -> bool:
    if objective not in _MMM_OBJECTIVES:
        return False
    if _has_mmm_fixture(manifest):
        return False
    draft_step = _step_for(manifest, WorkflowActionType.DRAFT_CONFIG)
    if draft_step is None:
        return False
    return draft_step.status in (
        WorkflowStepStatus.COMPLETED,
        WorkflowStepStatus.WARNING,
    )


def _missing_input_hints(manifest: WorkflowRunManifest, objective: str) -> list[str]:
    hints = list(manifest.blockers)
    if objective == "awareness":
        hints.append("awareness_kpi")
        hints.append("upper_funnel_kpi")
    return _dedupe_strings(hints)


def _blocked_decision(
    action_type: WorkflowActionType,
    reason: str,
    *,
    human_approval_requirement: HumanApprovalRequirement = HumanApprovalRequirement.NOT_REQUIRED,
    safety_notes: list[str] | None = None,
) -> PlannerDecision:
    return PlannerDecision(
        action_type=action_type,
        status=PlannerDecisionStatus.BLOCKED,
        reason=reason,
        human_approval_requirement=human_approval_requirement,
        safety_notes=safety_notes or [],
    )


def _decision_display(decision: PlannerDecision) -> dict[str, object]:
    return {
        "action_type": _enum_value(decision.action_type),
        "status": _enum_value(decision.status),
        "reason": decision.reason,
        "required_inputs": list(decision.required_inputs),
        "produced_artifact_type": decision.produced_artifact_type,
        "produced_artifact_marker": decision.produced_artifact_marker,
        "human_approval_requirement": _enum_value(decision.human_approval_requirement),
        "approval_checkpoint": _checkpoint_display(decision.approval_checkpoint),
        "safety_notes": list(decision.safety_notes),
    }


def _checkpoint_display(checkpoint: object) -> dict[str, object] | None:
    if checkpoint is None:
        return None
    request = getattr(checkpoint, "approval_request", None)
    return {
        "action_type": _enum_value(getattr(checkpoint, "action_type", "")),
        "requirement": _enum_value(getattr(checkpoint, "requirement", "")),
        "approval_status": _enum_value(getattr(checkpoint, "approval_status", "")),
        "blocked_until_approved": getattr(checkpoint, "blocked_until_approved", False),
        "reason": getattr(checkpoint, "reason", ""),
        "approval_id": getattr(request, "approval_id", None) if request is not None else None,
    }


def _collect_safety_notes(route: PlannerRoute) -> list[str]:
    notes: list[str] = []
    for decision in [*route.allowed_decisions, *route.blocked_decisions]:
        notes.extend(decision.safety_notes)
    return _dedupe_strings(notes)


def _has_mmm_fixture(manifest: WorkflowRunManifest) -> bool:
    return any(ref.artifact_type == "mmm_fixture_report" for ref in manifest.artifact_refs)


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


def _dedupe_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _enum_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))
