"""Local deterministic workflow orchestration."""

from collections.abc import Mapping, Sequence

from mip.workflows.configs.base import DraftConfigStatus
from mip.workflows.configs.drafting import draft_config_for_objective
from mip.workflows.configs.geox import GeoXConfigDraft
from mip.workflows.configs.mmm import MMMConfigDraft
from mip.workflows.intake.feasibility import (
    FeasibilityStatus,
    ObjectiveFeasibilityReport,
    evaluate_objective_feasibility,
    recommended_next_questions,
)
from mip.workflows.intake.objectives import BusinessObjective
from mip.workflows.orchestrator.summary import WorkflowRunStatus, WorkflowRunSummary
from mip.workflows.readiness.profile import (
    DatasetProfile,
    profile_from_records,
    profile_to_availability,
)
from mip.workflows.readiness.report import (
    DataReadinessReport,
    DataReadinessStatus,
    build_data_readiness_report,
)

_EXECUTION_DISCLAIMER = "No MMM, GeoX, adapter, or causal model execution was performed."


def _enum_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))


def run_local_workflow(
    objective: BusinessObjective,
    records: Sequence[Mapping[str, object]],
) -> WorkflowRunSummary:
    """Run the full local deterministic workflow pipeline on input records."""
    profile = profile_from_records(records)
    availability = profile_to_availability(profile)
    feasibility = evaluate_objective_feasibility(objective, availability)
    readiness = build_data_readiness_report(profile, feasibility)
    config_draft = draft_config_for_objective(objective, feasibility, readiness)

    warnings = _aggregate_warnings(feasibility, readiness, config_draft)
    blocking_reasons = _aggregate_blocking_reasons(feasibility, readiness, config_draft)
    status = _derive_run_status(feasibility, readiness, config_draft, warnings, blocking_reasons)
    next_questions = recommended_next_questions(feasibility)
    fixes = list(readiness.recommended_fixes)
    narrative = _build_narrative_summary(
        objective=objective,
        profile=profile,
        feasibility=feasibility,
        readiness=readiness,
        config_draft=config_draft,
        status=status,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
    )

    return WorkflowRunSummary(
        objective=objective,
        profile=profile,
        feasibility=feasibility,
        readiness=readiness,
        config_draft=config_draft,
        status=status,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        recommended_next_questions=next_questions,
        recommended_fixes=fixes,
        narrative_summary=narrative,
    )


def _derive_run_status(
    feasibility: ObjectiveFeasibilityReport,
    readiness: DataReadinessReport,
    config_draft: MMMConfigDraft | GeoXConfigDraft,
    warnings: list[str],
    blocking_reasons: list[str],
) -> WorkflowRunStatus:
    if blocking_reasons:
        return WorkflowRunStatus.BLOCKED
    if (
        feasibility.status == FeasibilityStatus.BLOCKED
        or readiness.status == DataReadinessStatus.BLOCKED
        or config_draft.metadata.status == DraftConfigStatus.BLOCKED
    ):
        return WorkflowRunStatus.BLOCKED
    if (
        feasibility.status == FeasibilityStatus.DIAGNOSTIC_ONLY
        or readiness.status == DataReadinessStatus.DIAGNOSTIC_ONLY
        or config_draft.metadata.status == DraftConfigStatus.DIAGNOSTIC_ONLY
        or warnings
    ):
        return WorkflowRunStatus.COMPLETED_WITH_WARNINGS
    return WorkflowRunStatus.COMPLETED


def _aggregate_warnings(
    feasibility: ObjectiveFeasibilityReport,
    readiness: DataReadinessReport,
    config_draft: MMMConfigDraft | GeoXConfigDraft,
) -> list[str]:
    return _dedupe_stable(
        [
            *feasibility.warnings,
            *readiness.warnings,
            *config_draft.metadata.warnings,
        ]
    )


def _aggregate_blocking_reasons(
    feasibility: ObjectiveFeasibilityReport,
    readiness: DataReadinessReport,
    config_draft: MMMConfigDraft | GeoXConfigDraft,
) -> list[str]:
    return _dedupe_stable(
        [
            *feasibility.blocking_reasons,
            *readiness.blocking_reasons,
            *config_draft.metadata.blocking_reasons,
        ]
    )


def _build_narrative_summary(
    *,
    objective: BusinessObjective,
    profile: DatasetProfile,
    feasibility: ObjectiveFeasibilityReport,
    readiness: DataReadinessReport,
    config_draft: MMMConfigDraft | GeoXConfigDraft,
    status: WorkflowRunStatus,
    warnings: list[str],
    blocking_reasons: list[str],
) -> str:
    workflow = config_draft.metadata.workflow_type
    draft_status = config_draft.metadata.status
    lines = [
        (
            f"Reviewed {profile.row_count} records for objective "
            f"{_enum_value(objective.objective_type)}."
        ),
        (
            f"Feasibility is {_enum_value(feasibility.status)}; readiness is "
            f"{_enum_value(readiness.status)}; config draft is {_enum_value(draft_status)} for "
            f"workflow {_enum_value(workflow)}."
        ),
        f"Workflow run status is {_enum_value(status)}.",
        _EXECUTION_DISCLAIMER,
    ]
    if blocking_reasons:
        lines.append(f"Blocking reasons: {'; '.join(blocking_reasons)}")
    if warnings:
        lines.append(f"Warnings: {'; '.join(warnings)}")
    if status != WorkflowRunStatus.BLOCKED and not config_draft.metadata.production_eligible:
        lines.append("Config draft is not production-eligible.")
    return " ".join(lines)


def _dedupe_stable(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
