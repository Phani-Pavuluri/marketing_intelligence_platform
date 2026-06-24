"""Fixture-only engine orchestration through governed adapter contracts."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.adapters.geox import (
    build_geox_adapter_input,
    build_geox_adapter_output_placeholder,
)
from mip.adapters.governance import (
    adapter_output_id,
    adapter_output_to_decision_surface,
    register_adapter_output,
    trust_report_for_adapter_output,
)
from mip.adapters.mmm import (
    build_mmm_adapter_input,
    build_mmm_adapter_output_placeholder,
)
from mip.contracts import ExperimentEvidence
from mip.contracts.base import ContractBaseModel
from mip.evidence.registry import EvidenceRegistry
from mip.orchestration.approvals import (
    ApprovalCheckpoint,
    ApprovalRequest,
    ApprovalStatus,
    build_governed_planner_route,
    checkpoint_for_action,
    is_action_approved,
)
from mip.orchestration.manifest import (
    HumanApprovalRequirement,
    WorkflowActionType,
    WorkflowArtifactRef,
)
from mip.orchestration.plans import build_manifest_from_workflow_summary
from mip.orchestration.router import PlannerDecisionStatus
from mip.workflows.configs.base import DraftConfigStatus
from mip.workflows.configs.geox import GeoXConfigDraft
from mip.workflows.configs.mmm import MMMConfigDraft
from mip.workflows.intake.requirements import WorkflowType
from mip.workflows.orchestrator import WorkflowRunStatus, WorkflowRunSummary

_REQUIRED_LABELS = (
    "fixture_engine_orchestration_only",
    "not_real_engine_execution",
)

_PLACEHOLDER_LABELS = (
    "adapter_fixture_placeholder_only",
    "diagnostic_only",
    "not_decision_ready",
)

_FORBIDDEN_CLAIM_PHRASES = (
    "actual roi",
    "true roi",
    "incremental lift",
    "causal impact",
    "model result",
    "budget recommendation",
    "production-ready",
)

_DISCLAIMER = (
    "Fixture engine orchestration only. Adapter outputs are placeholders, "
    "not real engine execution. Diagnostic only and not decision-ready."
)

_MMM_WORKFLOW_TYPES = frozenset(
    {
        WorkflowType.MMM_CHANNEL_ROI,
        WorkflowType.MMM_BUDGET_ALLOCATION,
        WorkflowType.SCENARIO_PLANNING,
    }
)

_GEOX_WORKFLOW_TYPES = frozenset(
    {
        WorkflowType.GEOX_EXPERIMENT_DESIGN,
        WorkflowType.GEOX_EXPERIMENT_READOUT,
    }
)


class FixtureEngineKind(StrEnum):
    """Fixture engine adapter family."""

    MMM = "mmm"
    GEOX = "geox"


class FixtureEngineRunStatus(StrEnum):
    """Status for a fixture engine orchestration run."""

    NOT_STARTED = "not_started"
    BLOCKED = "blocked"
    APPROVAL_REQUIRED = "approval_required"
    COMPLETED_PLACEHOLDER = "completed_placeholder"
    FAILED = "failed"


class FixtureEngineRunResult(ContractBaseModel):
    """Result of a governed fixture engine orchestration attempt."""

    run_id: str
    engine_kind: FixtureEngineKind
    status: FixtureEngineRunStatus
    source_manifest_id: str
    source_config_marker: str
    adapter_input_ref: WorkflowArtifactRef | None = None
    adapter_output_ref: WorkflowArtifactRef | None = None
    governance_artifact_ref: WorkflowArtifactRef | None = None
    trust_report_ref: WorkflowArtifactRef | None = None
    approval_status: ApprovalStatus = ApprovalStatus.NOT_REQUIRED
    approval_checkpoint: ApprovalCheckpoint | None = None
    labels: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    disclaimer: str = _DISCLAIMER

    @field_validator("run_id", "source_manifest_id", "source_config_marker", "disclaimer")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "fixture engine result fields cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("labels", "warnings", "blocking_reasons")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "labels, warnings, and blocking_reasons cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def result_consistency(self) -> FixtureEngineRunResult:
        for label in _REQUIRED_LABELS:
            if label not in self.labels:
                msg = f"fixture engine result labels must include {label}"
                raise ValueError(msg)
        if self.status == FixtureEngineRunStatus.COMPLETED_PLACEHOLDER:
            if self.adapter_output_ref is None or self.trust_report_ref is None:
                msg = (
                    "completed placeholder runs require adapter output and trust report refs"
                )
                raise ValueError(msg)
        if self.status in (
            FixtureEngineRunStatus.BLOCKED,
            FixtureEngineRunStatus.FAILED,
        ):
            if not self.blocking_reasons:
                msg = "blocked or failed runs require blocking reasons"
                raise ValueError(msg)
        if self.status == FixtureEngineRunStatus.APPROVAL_REQUIRED:
            if self.approval_checkpoint is None:
                msg = "approval-required runs require approval checkpoint metadata"
                raise ValueError(msg)
        return self


def orchestrate_mmm_fixture_engine(
    summary: WorkflowRunSummary,
    approvals: list[ApprovalRequest] | None = None,
) -> FixtureEngineRunResult:
    """Orchestrate the governed MMM adapter fixture path for a workflow summary."""
    return orchestrate_fixture_engine(summary, FixtureEngineKind.MMM, approvals)


def orchestrate_geox_fixture_engine(
    summary: WorkflowRunSummary,
    approvals: list[ApprovalRequest] | None = None,
) -> FixtureEngineRunResult:
    """Orchestrate the governed GeoX adapter fixture path for a workflow summary."""
    return orchestrate_fixture_engine(summary, FixtureEngineKind.GEOX, approvals)


def orchestrate_fixture_engine(
    summary: WorkflowRunSummary,
    engine_kind: FixtureEngineKind,
    approvals: list[ApprovalRequest] | None = None,
) -> FixtureEngineRunResult:
    """Orchestrate a fixture-only engine path through governed adapters."""
    manifest = build_manifest_from_workflow_summary(summary)
    route, active_approvals = build_governed_planner_route(manifest, approvals)
    marker = summary.config_draft.metadata.generated_marker
    run_id = f"fixture_engine:{_enum_value(engine_kind)}:{manifest.run_id}"

    if not _engine_eligible(summary, engine_kind):
        return _blocked_result(
            run_id=run_id,
            engine_kind=engine_kind,
            manifest_id=manifest.run_id,
            marker=marker,
            reasons=[_ineligibility_reason(summary, engine_kind)],
        )

    if summary.status == WorkflowRunStatus.BLOCKED:
        return _blocked_result(
            run_id=run_id,
            engine_kind=engine_kind,
            manifest_id=manifest.run_id,
            marker=marker,
            reasons=list(summary.blocking_reasons) or ["Workflow run is blocked."],
        )

    approval_state = _fixture_approval_state(
        manifest,
        route,
        active_approvals,
        engine_kind,
    )
    if approval_state is not None:
        return approval_state

    fixture_action = WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE
    if engine_kind == FixtureEngineKind.MMM and not _route_allows_fixture_action(
        route,
        fixture_action,
    ):
        return _blocked_result(
            run_id=run_id,
            engine_kind=engine_kind,
            manifest_id=manifest.run_id,
            marker=marker,
            reasons=["Fixture engine orchestration is blocked by planner route."],
        )

    try:
        if engine_kind == FixtureEngineKind.MMM:
            return _orchestrate_mmm_placeholder(
                summary,
                run_id=run_id,
                manifest_id=manifest.run_id,
                marker=marker,
                approvals=active_approvals,
            )
        return _orchestrate_geox_placeholder(
            summary,
            run_id=run_id,
            manifest_id=manifest.run_id,
            marker=marker,
            approvals=active_approvals,
        )
    except ValueError as exc:
        return _failed_result(
            run_id=run_id,
            engine_kind=engine_kind,
            manifest_id=manifest.run_id,
            marker=marker,
            reason=str(exc),
        )


def fixture_engine_result_sections(result: FixtureEngineRunResult) -> dict[str, object]:
    """Format a fixture engine result for display-only UI sections."""
    assert_safe_fixture_engine_result(result)
    return {
        "run_id": result.run_id,
        "engine_kind": _enum_value(result.engine_kind),
        "status": _enum_value(result.status),
        "source_manifest_id": result.source_manifest_id,
        "source_config_marker": result.source_config_marker,
        "labels": list(result.labels),
        "approval_status": _enum_value(result.approval_status),
        "adapter_input_ref": _artifact_ref_display(result.adapter_input_ref),
        "adapter_output_ref": _artifact_ref_display(result.adapter_output_ref),
        "governance_artifact_ref": _artifact_ref_display(result.governance_artifact_ref),
        "trust_report_ref": _artifact_ref_display(result.trust_report_ref),
        "trust_report_confidence_tier": _trust_report_tier(result),
        "warnings": list(result.warnings),
        "blocking_reasons": list(result.blocking_reasons),
        "approval_checkpoint": _checkpoint_display(result.approval_checkpoint),
        "disclaimer": result.disclaimer,
    }


def assert_safe_fixture_engine_result(result: FixtureEngineRunResult) -> None:
    """Raise if fixture engine result text includes forbidden claims."""
    combined = result.model_dump_json().lower()
    for phrase in _FORBIDDEN_CLAIM_PHRASES:
        if phrase in combined:
            msg = f"fixture engine result must not include forbidden phrase: {phrase}"
            raise ValueError(msg)
    if _contains_false_production_ready_claim(combined):
        msg = "fixture engine result must not claim production-ready status"
        raise ValueError(msg)


def create_engine_fixture_approval_request(
    manifest_id: str,
    engine_kind: FixtureEngineKind,
    reason: str,
    required_approver_role: str = "fixture_engine_reviewer",
    *,
    created_at: datetime | None = None,
) -> ApprovalRequest:
    """Create an engine-scoped pending approval request for fixture orchestration."""
    timestamp = created_at or datetime.now(tz=UTC)
    action = WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE
    return ApprovalRequest(
        approval_id=_engine_approval_id(manifest_id, engine_kind, action),
        action_type=action,
        manifest_id=manifest_id,
        requested_reason=reason,
        required_approver_role=required_approver_role,
        status=ApprovalStatus.PENDING,
        created_at=timestamp,
    )


def is_engine_fixture_approved(
    engine_kind: FixtureEngineKind,
    approvals: list[ApprovalRequest],
    manifest_id: str,
) -> bool:
    """Return whether fixture orchestration is approved for a specific engine kind."""
    approval_id = _engine_approval_id(
        manifest_id,
        engine_kind,
        WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE,
    )
    return any(
        item.approval_id == approval_id and item.status == ApprovalStatus.APPROVED
        for item in approvals
    )


def _orchestrate_mmm_placeholder(
    summary: WorkflowRunSummary,
    *,
    run_id: str,
    manifest_id: str,
    marker: str,
    approvals: list[ApprovalRequest],
) -> FixtureEngineRunResult:
    if not isinstance(summary.config_draft, MMMConfigDraft):
        msg = "MMM fixture orchestration requires an MMM config draft"
        raise ValueError(msg)

    adapter_input = build_mmm_adapter_input(summary.config_draft)
    adapter_output = build_mmm_adapter_output_placeholder(summary.config_draft)
    surface = adapter_output_to_decision_surface(adapter_output)
    trust_report = trust_report_for_adapter_output(adapter_output)
    output_id = adapter_output_id(adapter_output)

    result = FixtureEngineRunResult(
        run_id=run_id,
        engine_kind=FixtureEngineKind.MMM,
        status=FixtureEngineRunStatus.COMPLETED_PLACEHOLDER,
        source_manifest_id=manifest_id,
        source_config_marker=marker,
        adapter_input_ref=_artifact_ref(
            "adapter_input_bundle",
            f"adapter_input:{marker}",
            marker,
            notes=_enum_value(adapter_input.status),
        ),
        adapter_output_ref=_artifact_ref(
            "adapter_output_bundle",
            output_id,
            marker,
            notes="adapter_fixture_placeholder_only",
        ),
        governance_artifact_ref=_artifact_ref(
            "decision_surface_fixture",
            surface.surface_id,
            marker,
            notes=_enum_value(surface.surface_type),
        ),
        trust_report_ref=_artifact_ref(
            "trust_report",
            trust_report.trust_report_id,
            marker,
            notes=_enum_value(trust_report.confidence_tier),
        ),
        approval_status=_engine_approval_status(
            FixtureEngineKind.MMM,
            manifest_id,
            approvals,
        ),
        labels=_result_labels(),
        warnings=list(summary.warnings),
        disclaimer=_DISCLAIMER,
    )
    assert_safe_fixture_engine_result(result)
    return result


def _orchestrate_geox_placeholder(
    summary: WorkflowRunSummary,
    *,
    run_id: str,
    manifest_id: str,
    marker: str,
    approvals: list[ApprovalRequest],
) -> FixtureEngineRunResult:
    if not isinstance(summary.config_draft, GeoXConfigDraft):
        msg = "GeoX fixture orchestration requires a GeoX config draft"
        raise ValueError(msg)

    adapter_input = build_geox_adapter_input(summary.config_draft)
    adapter_output = build_geox_adapter_output_placeholder(summary.config_draft)
    registry = EvidenceRegistry()
    registration = register_adapter_output(registry, adapter_output)
    evidence = registration.artifact
    if not isinstance(evidence, ExperimentEvidence):
        msg = "GeoX fixture orchestration requires ExperimentEvidence artifact"
        raise ValueError(msg)
    trust_report = registration.trust_report
    output_id = adapter_output_id(adapter_output)

    result = FixtureEngineRunResult(
        run_id=run_id,
        engine_kind=FixtureEngineKind.GEOX,
        status=FixtureEngineRunStatus.COMPLETED_PLACEHOLDER,
        source_manifest_id=manifest_id,
        source_config_marker=marker,
        adapter_input_ref=_artifact_ref(
            "adapter_input_bundle",
            f"adapter_input:{marker}",
            marker,
            notes=_enum_value(adapter_input.status),
        ),
        adapter_output_ref=_artifact_ref(
            "adapter_output_bundle",
            output_id,
            marker,
            notes="adapter_fixture_placeholder_only",
        ),
        governance_artifact_ref=_artifact_ref(
            "experiment_evidence_fixture",
            evidence.evidence_id,
            marker,
            notes=_enum_value(evidence.evidence_role),
        ),
        trust_report_ref=_artifact_ref(
            "trust_report",
            trust_report.trust_report_id,
            marker,
            notes=_enum_value(trust_report.confidence_tier),
        ),
        approval_status=_engine_approval_status(
            FixtureEngineKind.GEOX,
            manifest_id,
            approvals,
        ),
        labels=_result_labels(),
        warnings=list(summary.warnings),
        disclaimer=_DISCLAIMER,
    )
    assert_safe_fixture_engine_result(result)
    return result


def _fixture_approval_state(
    manifest: object,
    route: object,
    approvals: list[ApprovalRequest],
    engine_kind: FixtureEngineKind,
) -> FixtureEngineRunResult | None:
    from mip.orchestration.manifest import WorkflowRunManifest
    from mip.orchestration.router import PlannerRoute

    assert isinstance(manifest, WorkflowRunManifest)
    assert isinstance(route, PlannerRoute)

    marker = manifest.plan.source_config_marker or manifest.run_id
    run_id = f"fixture_engine:{_enum_value(engine_kind)}:{manifest.run_id}"
    fixture_action = WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE

    human_approval = _approval_for_action(
        approvals,
        manifest.run_id,
        WorkflowActionType.REQUEST_HUMAN_APPROVAL,
    )
    human_checkpoint = checkpoint_for_action(
        manifest,
        WorkflowActionType.REQUEST_HUMAN_APPROVAL,
        human_approval,
    )
    if human_checkpoint.requirement in (
        HumanApprovalRequirement.REQUIRED,
        HumanApprovalRequirement.BLOCKED_UNTIL_APPROVED,
    ) and human_checkpoint.blocked_until_approved and not is_action_approved(
        WorkflowActionType.REQUEST_HUMAN_APPROVAL,
        approvals,
    ):
        return FixtureEngineRunResult(
            run_id=run_id,
            engine_kind=engine_kind,
            status=FixtureEngineRunStatus.APPROVAL_REQUIRED,
            source_manifest_id=manifest.run_id,
            source_config_marker=marker,
            approval_status=ApprovalStatus.PENDING,
            approval_checkpoint=human_checkpoint,
            labels=_result_labels(),
            warnings=list(manifest.warnings),
            disclaimer=_DISCLAIMER,
        )

    engine_approval = _approval_for_engine(approvals, manifest.run_id, engine_kind)
    engine_checkpoint = checkpoint_for_action(manifest, fixture_action, engine_approval)
    if engine_approval is not None and engine_approval.status == ApprovalStatus.PENDING:
        return FixtureEngineRunResult(
            run_id=run_id,
            engine_kind=engine_kind,
            status=FixtureEngineRunStatus.APPROVAL_REQUIRED,
            source_manifest_id=manifest.run_id,
            source_config_marker=marker,
            approval_status=ApprovalStatus.PENDING,
            approval_checkpoint=engine_checkpoint,
            labels=_result_labels(),
            warnings=list(manifest.warnings),
            disclaimer=_DISCLAIMER,
        )

    requires_engine_approval = any(
        decision.action_type == fixture_action
        and decision.status == PlannerDecisionStatus.REQUIRES_APPROVAL
        for decision in route.allowed_decisions
    )
    if requires_engine_approval and not is_engine_fixture_approved(
        engine_kind,
        approvals,
        manifest.run_id,
    ):
        pending = create_engine_fixture_approval_request(
            manifest.run_id,
            engine_kind,
            "Engine-scoped fixture orchestration approval required.",
        )
        checkpoint = checkpoint_for_action(manifest, fixture_action, pending)
        return FixtureEngineRunResult(
            run_id=run_id,
            engine_kind=engine_kind,
            status=FixtureEngineRunStatus.APPROVAL_REQUIRED,
            source_manifest_id=manifest.run_id,
            source_config_marker=marker,
            approval_status=ApprovalStatus.PENDING,
            approval_checkpoint=checkpoint,
            labels=_result_labels(),
            warnings=list(manifest.warnings),
            disclaimer=_DISCLAIMER,
        )

    return None


def _engine_eligible(summary: WorkflowRunSummary, engine_kind: FixtureEngineKind) -> bool:
    if engine_kind == FixtureEngineKind.MMM:
        if not isinstance(summary.config_draft, MMMConfigDraft):
            return False
        workflow_type = summary.config_draft.metadata.workflow_type
        if workflow_type not in _MMM_WORKFLOW_TYPES:
            return False
        return _enum_value(summary.config_draft.metadata.status) != DraftConfigStatus.BLOCKED

    if not isinstance(summary.config_draft, GeoXConfigDraft):
        return False
    workflow_type = summary.config_draft.metadata.workflow_type
    if workflow_type not in _GEOX_WORKFLOW_TYPES:
        return False
    return _enum_value(summary.config_draft.metadata.status) != DraftConfigStatus.BLOCKED


def _ineligibility_reason(
    summary: WorkflowRunSummary,
    engine_kind: FixtureEngineKind,
) -> str:
    if engine_kind == FixtureEngineKind.MMM:
        return "Workflow summary is not MMM-eligible for fixture engine orchestration."
    return "Workflow summary is not GeoX-eligible for fixture engine orchestration."


def _route_allows_fixture_action(route: object, action: WorkflowActionType) -> bool:
    from mip.orchestration.router import PlannerRoute

    assert isinstance(route, PlannerRoute)
    return any(
        decision.action_type == action
        and decision.status
        in (PlannerDecisionStatus.ALLOWED, PlannerDecisionStatus.REQUIRES_APPROVAL)
        for decision in route.allowed_decisions
    )


def _blocked_result(
    *,
    run_id: str,
    engine_kind: FixtureEngineKind,
    manifest_id: str,
    marker: str,
    reasons: list[str],
) -> FixtureEngineRunResult:
    result = FixtureEngineRunResult(
        run_id=run_id,
        engine_kind=engine_kind,
        status=FixtureEngineRunStatus.BLOCKED,
        source_manifest_id=manifest_id,
        source_config_marker=marker,
        approval_status=ApprovalStatus.NOT_REQUIRED,
        labels=_result_labels(),
        blocking_reasons=reasons,
        disclaimer=_DISCLAIMER,
    )
    assert_safe_fixture_engine_result(result)
    return result


def _failed_result(
    *,
    run_id: str,
    engine_kind: FixtureEngineKind,
    manifest_id: str,
    marker: str,
    reason: str,
) -> FixtureEngineRunResult:
    result = FixtureEngineRunResult(
        run_id=run_id,
        engine_kind=engine_kind,
        status=FixtureEngineRunStatus.FAILED,
        source_manifest_id=manifest_id,
        source_config_marker=marker,
        approval_status=ApprovalStatus.NOT_REQUIRED,
        labels=_result_labels(),
        blocking_reasons=[reason],
        disclaimer=_DISCLAIMER,
    )
    assert_safe_fixture_engine_result(result)
    return result


def _result_labels() -> list[str]:
    return list(_REQUIRED_LABELS + _PLACEHOLDER_LABELS)


def _artifact_ref(
    artifact_type: str,
    artifact_id: str,
    marker: str,
    *,
    notes: str | None = None,
) -> WorkflowArtifactRef:
    return WorkflowArtifactRef(
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        lineage_marker=marker,
        notes=notes,
    )


def _artifact_ref_display(ref: WorkflowArtifactRef | None) -> dict[str, str] | None:
    if ref is None:
        return None
    return {
        "artifact_type": ref.artifact_type,
        "artifact_id": ref.artifact_id,
        "lineage_marker": ref.lineage_marker or "",
        "notes": ref.notes or "",
    }


def _checkpoint_display(checkpoint: ApprovalCheckpoint | None) -> dict[str, object] | None:
    if checkpoint is None:
        return None
    request = checkpoint.approval_request
    return {
        "action_type": _enum_value(checkpoint.action_type),
        "approval_status": _enum_value(checkpoint.approval_status),
        "blocked_until_approved": checkpoint.blocked_until_approved,
        "reason": checkpoint.reason,
        "approval_id": request.approval_id if request is not None else None,
    }


def _trust_report_tier(result: FixtureEngineRunResult) -> str | None:
    if result.trust_report_ref is None or result.trust_report_ref.notes is None:
        return None
    return result.trust_report_ref.notes


def _engine_approval_id(
    manifest_id: str,
    engine_kind: FixtureEngineKind,
    action: WorkflowActionType,
) -> str:
    return f"approval:{manifest_id}:{_enum_value(engine_kind)}:{_enum_value(action)}"


def _approval_for_engine(
    approvals: list[ApprovalRequest],
    manifest_id: str,
    engine_kind: FixtureEngineKind,
) -> ApprovalRequest | None:
    approval_id = _engine_approval_id(
        manifest_id,
        engine_kind,
        WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE,
    )
    for item in approvals:
        if item.approval_id == approval_id:
            return item
    return None


def _approval_for_action(
    approvals: list[ApprovalRequest],
    manifest_id: str,
    action: WorkflowActionType,
) -> ApprovalRequest | None:
    action_value = _enum_value(action)
    for item in approvals:
        if item.manifest_id == manifest_id and _enum_value(item.action_type) == action_value:
            return item
    return None


def _engine_approval_status(
    engine_kind: FixtureEngineKind,
    manifest_id: str,
    approvals: list[ApprovalRequest],
) -> ApprovalStatus:
    if is_engine_fixture_approved(engine_kind, approvals, manifest_id):
        return ApprovalStatus.APPROVED
    engine_request = _approval_for_engine(approvals, manifest_id, engine_kind)
    if engine_request is not None:
        return engine_request.status
    if is_action_approved(WorkflowActionType.REQUEST_HUMAN_APPROVAL, approvals):
        return ApprovalStatus.APPROVED
    human_request = _approval_for_action(
        approvals,
        manifest_id,
        WorkflowActionType.REQUEST_HUMAN_APPROVAL,
    )
    if human_request is not None:
        return human_request.status
    return ApprovalStatus.NOT_REQUIRED


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
