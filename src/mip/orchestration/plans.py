"""Deterministic workflow plan and manifest builders."""

from __future__ import annotations

from datetime import UTC, datetime

from mip.orchestration.manifest import (
    HumanApprovalRequirement,
    WorkflowActionType,
    WorkflowArtifactRef,
    WorkflowBlockReason,
    WorkflowPlan,
    WorkflowRunManifest,
    WorkflowStep,
    WorkflowStepStatus,
    assert_safe_workflow_manifest,
)
from mip.reports.mmm_fixture import MMMFixtureReport
from mip.workflows.configs.base import DraftConfigStatus
from mip.workflows.orchestrator import WorkflowRunStatus, WorkflowRunSummary

_STANDARD_ACTIONS: tuple[WorkflowActionType, ...] = (
    WorkflowActionType.PARSE_INPUT,
    WorkflowActionType.CLASSIFY_INTENT,
    WorkflowActionType.PROFILE_DATA,
    WorkflowActionType.EVALUATE_FEASIBILITY,
    WorkflowActionType.BUILD_READINESS_REPORT,
    WorkflowActionType.DRAFT_CONFIG,
    WorkflowActionType.BUILD_ADAPTER_INPUT,
    WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE,
    WorkflowActionType.MAP_TO_GOVERNANCE_ARTIFACT,
    WorkflowActionType.BUILD_TRUST_REPORT,
    WorkflowActionType.RENDER_REPORT,
    WorkflowActionType.REQUEST_HUMAN_APPROVAL,
)


def build_plan_from_workflow_summary(summary: WorkflowRunSummary) -> WorkflowPlan:
    """Build a deterministic workflow plan from a workflow summary."""
    marker = summary.config_draft.metadata.generated_marker
    steps = [
        WorkflowStep(
            step_id=f"step:{_enum_value(action)}",
            action_type=action,
            status=WorkflowStepStatus.PLANNED,
            completion_note="planned deterministic step; not yet executed in plan view",
        )
        for action in _STANDARD_ACTIONS
    ]
    plan = WorkflowPlan(
        plan_id=f"plan:{marker}",
        objective_type=_enum_value(summary.objective.objective_type),
        source_config_marker=marker,
        steps=steps,
    )
    return plan


def build_manifest_from_workflow_summary(
    summary: WorkflowRunSummary,
    *,
    created_at: datetime | None = None,
) -> WorkflowRunManifest:
    """Build a governed workflow run manifest from a local workflow summary."""
    marker = summary.config_draft.metadata.generated_marker
    timestamp = created_at or datetime.now(tz=UTC)
    steps = _build_executed_steps(summary)
    artifact_refs = _collect_artifact_refs(steps)
    manifest = WorkflowRunManifest(
        run_id=f"run:{marker}:{int(timestamp.timestamp())}",
        created_at=timestamp,
        source="local_deterministic_workflow",
        objective_marker=f"{_enum_value(summary.objective.objective_type)}:{marker}",
        plan=WorkflowPlan(
            plan_id=f"plan:{marker}",
            objective_type=_enum_value(summary.objective.objective_type),
            source_config_marker=marker,
            steps=steps,
        ),
        artifact_refs=artifact_refs,
        warnings=list(summary.warnings),
        blockers=list(summary.blocking_reasons),
    )
    assert_safe_workflow_manifest(manifest)
    return manifest


def build_manifest_with_mmm_fixture(
    summary: WorkflowRunSummary,
    mmm_fixture_report: MMMFixtureReport,
    *,
    created_at: datetime | None = None,
) -> WorkflowRunManifest:
    """Extend a workflow manifest with MMM fixture governance artifact lineage."""
    manifest = build_manifest_from_workflow_summary(summary, created_at=created_at)
    steps = list(manifest.plan.steps)
    updated_steps = _apply_mmm_fixture_steps(steps, summary, mmm_fixture_report)
    artifact_refs = _collect_artifact_refs(updated_steps)
    artifact_refs.extend(_mmm_fixture_artifact_refs(mmm_fixture_report))
    manifest = manifest.model_copy(
        update={
            "plan": manifest.plan.model_copy(update={"steps": updated_steps}),
            "artifact_refs": _dedupe_artifact_refs(artifact_refs),
            "warnings": _dedupe_strings(
                [*manifest.warnings, *mmm_fixture_report.trust_report_warnings]
            ),
        }
    )
    assert_safe_workflow_manifest(manifest)
    return manifest


def _build_executed_steps(summary: WorkflowRunSummary) -> list[WorkflowStep]:
    marker = summary.config_draft.metadata.generated_marker
    workflow_blocked = summary.status == WorkflowRunStatus.BLOCKED
    draft_blocked = summary.config_draft.metadata.status == DraftConfigStatus.BLOCKED
    has_warnings = bool(summary.warnings)
    approval_requirement = _approval_requirement(summary)

    steps: list[WorkflowStep] = [
        WorkflowStep(
            step_id="step:parse_input",
            action_type=WorkflowActionType.PARSE_INPUT,
            status=_status_with_warnings(WorkflowStepStatus.COMPLETED, has_warnings),
            completion_note="Objective and records accepted for local workflow run",
        ),
        WorkflowStep(
            step_id="step:classify_intent",
            action_type=WorkflowActionType.CLASSIFY_INTENT,
            status=_status_with_warnings(WorkflowStepStatus.COMPLETED, has_warnings),
            output_artifacts=[
                WorkflowArtifactRef(
                    artifact_type="business_objective",
                    artifact_id=_enum_value(summary.objective.objective_type),
                    lineage_marker=marker,
                )
            ],
        ),
        WorkflowStep(
            step_id="step:profile_data",
            action_type=WorkflowActionType.PROFILE_DATA,
            status=_status_with_warnings(WorkflowStepStatus.COMPLETED, has_warnings),
            output_artifacts=[
                WorkflowArtifactRef(
                    artifact_type="dataset_profile",
                    artifact_id=f"profile:{marker}",
                    lineage_marker=marker,
                    notes=f"row_count={summary.profile.row_count}",
                )
            ],
        ),
        WorkflowStep(
            step_id="step:evaluate_feasibility",
            action_type=WorkflowActionType.EVALUATE_FEASIBILITY,
            status=_feasibility_step_status(summary, workflow_blocked),
            output_artifacts=[
                WorkflowArtifactRef(
                    artifact_type="objective_feasibility_report",
                    artifact_id=f"feasibility:{marker}",
                    lineage_marker=marker,
                    notes=f"status={_enum_value(summary.feasibility.status)}",
                )
            ],
            warnings=_feasibility_warnings(summary),
            block_reason=_primary_block_reason(summary) if workflow_blocked else None,
        ),
        WorkflowStep(
            step_id="step:build_readiness_report",
            action_type=WorkflowActionType.BUILD_READINESS_REPORT,
            status=_readiness_step_status(summary, workflow_blocked),
            output_artifacts=[
                WorkflowArtifactRef(
                    artifact_type="data_readiness_report",
                    artifact_id=f"readiness:{marker}",
                    lineage_marker=marker,
                    notes=f"status={_enum_value(summary.readiness.status)}",
                )
            ],
            block_reason=_primary_block_reason(summary) if workflow_blocked else None,
        ),
        WorkflowStep(
            step_id="step:draft_config",
            action_type=WorkflowActionType.DRAFT_CONFIG,
            status=_config_step_status(summary, draft_blocked, has_warnings),
            output_artifacts=[
                WorkflowArtifactRef(
                    artifact_type="config_draft",
                    artifact_id=marker,
                    lineage_marker=marker,
                    notes=f"workflow_type={_enum_value(summary.config_draft.metadata.workflow_type)}",
                )
            ],
            block_reason=_primary_block_reason(summary) if draft_blocked else None,
        ),
    ]
    steps.extend(_downstream_placeholder_steps(summary, workflow_blocked, draft_blocked))
    steps.append(_approval_step(summary, approval_requirement, workflow_blocked, draft_blocked))
    return steps


def _downstream_placeholder_steps(
    summary: WorkflowRunSummary,
    workflow_blocked: bool,
    draft_blocked: bool,
) -> list[WorkflowStep]:
    downstream_blocked = workflow_blocked or draft_blocked
    block_reason = _primary_block_reason(summary) if downstream_blocked else None
    skipped_note = "Deferred in base manifest; execute MMM fixture path for adapter steps"
    return [
        WorkflowStep(
            step_id=f"step:{_enum_value(action)}",
            action_type=action,
            status=WorkflowStepStatus.BLOCKED if downstream_blocked else WorkflowStepStatus.SKIPPED,
            completion_note=None if downstream_blocked else skipped_note,
            block_reason=block_reason if downstream_blocked else None,
            output_artifacts=[],
        )
        for action in (
            WorkflowActionType.BUILD_ADAPTER_INPUT,
            WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE,
            WorkflowActionType.MAP_TO_GOVERNANCE_ARTIFACT,
            WorkflowActionType.BUILD_TRUST_REPORT,
            WorkflowActionType.RENDER_REPORT,
        )
    ]


def _approval_step(
    summary: WorkflowRunSummary,
    approval_requirement: HumanApprovalRequirement,
    workflow_blocked: bool,
    draft_blocked: bool,
) -> WorkflowStep:
    if workflow_blocked or draft_blocked:
        return WorkflowStep(
            step_id="step:request_human_approval",
            action_type=WorkflowActionType.REQUEST_HUMAN_APPROVAL,
            status=WorkflowStepStatus.BLOCKED,
            human_approval_requirement=HumanApprovalRequirement.BLOCKED_UNTIL_APPROVED,
            block_reason=_primary_block_reason(summary)
            or WorkflowBlockReason(
                code="workflow_blocked",
                message="Human approval blocked until workflow blockers are resolved",
            ),
            completion_note="Approval checkpoint not reachable while workflow is blocked",
        )
    if approval_requirement in (
        HumanApprovalRequirement.REQUIRED,
        HumanApprovalRequirement.RECOMMENDED,
    ):
        return WorkflowStep(
            step_id="step:request_human_approval",
            action_type=WorkflowActionType.REQUEST_HUMAN_APPROVAL,
            status=WorkflowStepStatus.REQUIRES_APPROVAL,
            human_approval_requirement=approval_requirement,
            completion_note="Human review required before any production or budget action",
            warnings=["No autonomous approval or budget action is permitted"],
        )
    return WorkflowStep(
        step_id="step:request_human_approval",
        action_type=WorkflowActionType.REQUEST_HUMAN_APPROVAL,
        status=WorkflowStepStatus.COMPLETED,
        human_approval_requirement=HumanApprovalRequirement.NOT_REQUIRED,
        completion_note="No human approval required for diagnostic-only local manifest",
    )


def _apply_mmm_fixture_steps(
    steps: list[WorkflowStep],
    summary: WorkflowRunSummary,
    report: MMMFixtureReport,
) -> list[WorkflowStep]:
    if summary.status == WorkflowRunStatus.BLOCKED:
        return steps
    marker = report.source_config_marker
    replacement: dict[str, WorkflowStep] = {
        "step:build_adapter_input": WorkflowStep(
            step_id="step:build_adapter_input",
            action_type=WorkflowActionType.BUILD_ADAPTER_INPUT,
            status=WorkflowStepStatus.COMPLETED,
            output_artifacts=[
                WorkflowArtifactRef(
                    artifact_type="adapter_input_bundle",
                    artifact_id=f"adapter_input:{marker}",
                    lineage_marker=marker,
                    notes="placeholder adapter input only",
                )
            ],
            completion_note="MMM adapter input placeholder built from config draft",
        ),
        "step:build_adapter_output_fixture": WorkflowStep(
            step_id="step:build_adapter_output_fixture",
            action_type=WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE,
            status=WorkflowStepStatus.COMPLETED,
            output_artifacts=[
                WorkflowArtifactRef(
                    artifact_type="adapter_output_bundle",
                    artifact_id=report.adapter_output_id,
                    lineage_marker=marker,
                    notes="adapter_fixture_placeholder_only",
                )
            ],
        ),
        "step:map_to_governance_artifact": WorkflowStep(
            step_id="step:map_to_governance_artifact",
            action_type=WorkflowActionType.MAP_TO_GOVERNANCE_ARTIFACT,
            status=WorkflowStepStatus.COMPLETED,
            output_artifacts=[
                WorkflowArtifactRef(
                    artifact_type="decision_surface_fixture",
                    artifact_id=report.decision_surface_id,
                    lineage_marker=marker,
                    notes=report.decision_surface_type,
                )
            ],
            completion_note="Mapped to diagnostic DecisionSurface fixture only",
        ),
        "step:build_trust_report": WorkflowStep(
            step_id="step:build_trust_report",
            action_type=WorkflowActionType.BUILD_TRUST_REPORT,
            status=WorkflowStepStatus.WARNING,
            output_artifacts=[
                WorkflowArtifactRef(
                    artifact_type="trust_report",
                    artifact_id=f"trust_report:decision_surface:{report.decision_surface_id}",
                    lineage_marker=marker,
                    notes=f"confidence_tier={report.trust_report_confidence_tier}",
                )
            ],
            warnings=report.trust_report_warnings,
            completion_note="TrustReport built from placeholder fixture via existing gates",
        ),
        "step:render_report": WorkflowStep(
            step_id="step:render_report",
            action_type=WorkflowActionType.RENDER_REPORT,
            status=WorkflowStepStatus.COMPLETED,
            output_artifacts=[
                WorkflowArtifactRef(
                    artifact_type="mmm_fixture_report",
                    artifact_id=f"mmm_fixture:{marker}",
                    lineage_marker=marker,
                    notes="diagnostic_only; not_model_execution",
                )
            ],
            completion_note=report.placeholder_explanation,
        ),
    }
    return [replacement.get(step.step_id, step) for step in steps]


def _mmm_fixture_artifact_refs(report: MMMFixtureReport) -> list[WorkflowArtifactRef]:
    marker = report.source_config_marker
    return [
        WorkflowArtifactRef(
            artifact_type="adapter_output_bundle",
            artifact_id=report.adapter_output_id,
            lineage_marker=marker,
        ),
        WorkflowArtifactRef(
            artifact_type="decision_surface_fixture",
            artifact_id=report.decision_surface_id,
            lineage_marker=marker,
        ),
        WorkflowArtifactRef(
            artifact_type="mmm_fixture_report",
            artifact_id=f"mmm_fixture:{marker}",
            lineage_marker=marker,
        ),
    ]


def _approval_requirement(summary: WorkflowRunSummary) -> HumanApprovalRequirement:
    if summary.config_draft.metadata.production_eligible:
        return HumanApprovalRequirement.REQUIRED
    if _enum_value(summary.config_draft.metadata.status) in (
        DraftConfigStatus.DRAFTABLE,
        DraftConfigStatus.DRAFTABLE_WITH_WARNINGS,
    ):
        return HumanApprovalRequirement.RECOMMENDED
    return HumanApprovalRequirement.NOT_REQUIRED


def _primary_block_reason(summary: WorkflowRunSummary) -> WorkflowBlockReason | None:
    if not summary.blocking_reasons:
        return None
    return WorkflowBlockReason(code="workflow_blocked", message=summary.blocking_reasons[0])


def _feasibility_warnings(summary: WorkflowRunSummary) -> list[str]:
    return [item for item in summary.feasibility.warnings if item.strip()]


def _status_with_warnings(
    status: WorkflowStepStatus,
    has_warnings: bool,
) -> WorkflowStepStatus:
    if has_warnings and status == WorkflowStepStatus.COMPLETED:
        return WorkflowStepStatus.WARNING
    return status


def _feasibility_step_status(
    summary: WorkflowRunSummary,
    workflow_blocked: bool,
) -> WorkflowStepStatus:
    if workflow_blocked:
        return WorkflowStepStatus.BLOCKED
    if summary.warnings or summary.feasibility.warnings:
        return WorkflowStepStatus.WARNING
    return WorkflowStepStatus.COMPLETED


def _readiness_step_status(
    summary: WorkflowRunSummary,
    workflow_blocked: bool,
) -> WorkflowStepStatus:
    if workflow_blocked:
        return WorkflowStepStatus.BLOCKED
    if summary.warnings:
        return WorkflowStepStatus.WARNING
    return WorkflowStepStatus.COMPLETED


def _config_step_status(
    summary: WorkflowRunSummary,
    draft_blocked: bool,
    has_warnings: bool,
) -> WorkflowStepStatus:
    if draft_blocked:
        return WorkflowStepStatus.BLOCKED
    if has_warnings:
        return WorkflowStepStatus.WARNING
    return WorkflowStepStatus.COMPLETED


def _collect_artifact_refs(steps: list[WorkflowStep]) -> list[WorkflowArtifactRef]:
    refs: list[WorkflowArtifactRef] = []
    for step in steps:
        refs.extend(step.output_artifacts)
    return _dedupe_artifact_refs(refs)


def _dedupe_artifact_refs(refs: list[WorkflowArtifactRef]) -> list[WorkflowArtifactRef]:
    seen: set[tuple[str, str]] = set()
    ordered: list[WorkflowArtifactRef] = []
    for ref in refs:
        key = (ref.artifact_type, ref.artifact_id)
        if key not in seen:
            seen.add(key)
            ordered.append(ref)
    return ordered


def _dedupe_strings(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered


def _enum_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))
