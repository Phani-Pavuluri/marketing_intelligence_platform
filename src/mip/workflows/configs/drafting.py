"""Deterministic config drafting from intake and readiness artifacts."""

from mip.workflows.configs.base import (
    ConfigDraftMetadata,
    ConfigDraftValidationReport,
    DraftConfigStatus,
)
from mip.workflows.configs.geox import (
    CONTROLS_PLACEHOLDER,
    EXCLUSIONS_PLACEHOLDER,
    PRE_PERIOD_PLACEHOLDER,
    TEST_PERIOD_PLACEHOLDER,
    GeoXConfigDraft,
)
from mip.workflows.configs.mmm import MMMConfigDraft
from mip.workflows.intake.feasibility import FeasibilityStatus, ObjectiveFeasibilityReport
from mip.workflows.intake.objectives import BusinessObjective, BusinessObjectiveType
from mip.workflows.intake.requirements import WorkflowType, requirement_for_objective
from mip.workflows.readiness.profile import DatasetProfile
from mip.workflows.readiness.report import DataReadinessReport, DataReadinessStatus

_MMM_WORKFLOWS = frozenset(
    {
        WorkflowType.MMM_CHANNEL_ROI,
        WorkflowType.MMM_BUDGET_ALLOCATION,
        WorkflowType.SCENARIO_PLANNING,
    }
)

_GEOX_WORKFLOWS = frozenset(
    {
        WorkflowType.GEOX_EXPERIMENT_DESIGN,
        WorkflowType.GEOX_EXPERIMENT_READOUT,
    }
)

_OUTCOME_CANDIDATES: dict[BusinessObjectiveType, tuple[str, ...]] = {
    BusinessObjectiveType.CONVERSION_ROI: ("conversions",),
    BusinessObjectiveType.REVENUE_ROI: ("revenue",),
    BusinessObjectiveType.NEW_CUSTOMER_ACQUISITION: ("new_customers",),
    BusinessObjectiveType.AWARENESS: (
        "awareness_kpi",
        "brand_search",
        "reach",
        "impressions",
        "site_visits",
        "brand_lift",
        "survey_lift",
        "upper_funnel_kpi",
    ),
    BusinessObjectiveType.RETENTION: (
        "retention_kpi",
        "renewals",
        "churn",
        "repeat_purchase",
        "active_users",
    ),
    BusinessObjectiveType.PROFIT: ("margin", "revenue"),
    BusinessObjectiveType.SUBSCRIPTIONS: ("subscriptions",),
    BusinessObjectiveType.TRIALS: ("trials",),
    BusinessObjectiveType.PIPELINE: ("pipeline",),
    BusinessObjectiveType.BUDGET_ALLOCATION: ("outcome", "revenue", "conversions"),
    BusinessObjectiveType.EXPERIMENT_DESIGN: ("outcome",),
    BusinessObjectiveType.MMM_CALIBRATION: ("experiment_evidence", "estimand"),
    BusinessObjectiveType.DIAGNOSTIC_ANALYSIS: ("outcome", "conversions", "revenue"),
}


def draft_mmm_config(
    objective: BusinessObjective,
    feasibility: ObjectiveFeasibilityReport,
    readiness_report: DataReadinessReport,
) -> MMMConfigDraft:
    """Draft an MMM config from objective, feasibility, and readiness context."""
    profile = readiness_report.profile
    requirement = requirement_for_objective(objective.objective_type)
    workflow_type = _select_workflow(feasibility.recommended_workflows, _MMM_WORKFLOWS)

    warnings = _collect_warnings(feasibility, readiness_report)
    blocking_reasons = _collect_blocking_reasons(feasibility, readiness_report)

    if not _mmm_workflow_supported(feasibility):
        blocking_reasons.append(
            "No MMM, budget allocation, or scenario planning workflow is "
            "supported for this objective."
        )

    outcome_field = _resolve_outcome_field(profile, objective.objective_type)
    spend_field = _resolve_field(profile, "spend")
    date_field = profile.date_field

    if workflow_type != WorkflowType.DIAGNOSTIC_ONLY:
        if outcome_field is None:
            blocking_reasons.append(
                f"Outcome field for {objective.objective_type.value} is not present in the dataset."
            )
        if spend_field is None:
            blocking_reasons.append("Spend field is not present in the dataset.")
        if date_field is None:
            blocking_reasons.append("Date field is not present in the dataset.")

    if objective.objective_type == BusinessObjectiveType.AWARENESS:
        blocking_reasons.append(
            "Awareness objectives do not support production MMM configuration."
        )

    status = _derive_draft_status(feasibility, readiness_report, warnings, blocking_reasons)

    source_fields = _source_fields(
        profile,
        outcome_field,
        spend_field,
        date_field,
        profile.channel_field,
        profile.geo_field,
        profile.product_field,
        profile.campaign_field,
    )
    production_eligible = _production_eligible(status, workflow_type)

    metadata = _build_metadata(
        objective=objective,
        workflow_type=workflow_type,
        status=status,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        source_fields=source_fields,
        feasibility=feasibility,
        readiness_report=readiness_report,
        production_eligible=production_eligible,
    )

    time_grain = _profile_time_grain(profile)
    return MMMConfigDraft(
        metadata=metadata,
        outcome_field=outcome_field,
        spend_field=spend_field,
        date_field=date_field,
        channel_field=profile.channel_field,
        geo_field=profile.geo_field,
        product_field=profile.product_field,
        campaign_field=profile.campaign_field,
        controls=list(requirement.recommended_controls),
        time_grain=time_grain,
        history_weeks=profile.history_weeks,
    )


def draft_geox_config(
    objective: BusinessObjective,
    feasibility: ObjectiveFeasibilityReport,
    readiness_report: DataReadinessReport,
) -> GeoXConfigDraft:
    """Draft a GeoX experiment config from objective, feasibility, and readiness context."""
    profile = readiness_report.profile
    workflow_type = _select_workflow(feasibility.recommended_workflows, _GEOX_WORKFLOWS)

    warnings = _collect_warnings(feasibility, readiness_report)
    blocking_reasons = _collect_blocking_reasons(feasibility, readiness_report)

    if not _geox_workflow_supported(feasibility):
        blocking_reasons.append(
            "No GeoX experiment design or readout workflow is supported for this objective."
        )

    outcome_field = _resolve_outcome_field(profile, objective.objective_type)
    if outcome_field is None:
        outcome_field = _resolve_field(profile, "outcome")
    treatment_unit_field = profile.geo_field
    if treatment_unit_field is None:
        blocking_reasons.append(
            "Geo/DMA/region/market treatment unit field is not present in the dataset."
        )
    elif not profile.has_geo_breakdown:
        warnings.append(
            "Treatment unit field is present but geo breakdown has fewer than two units."
        )

    date_field = profile.date_field
    if date_field is None:
        blocking_reasons.append("Date field is not present in the dataset.")

    status = _derive_draft_status(feasibility, readiness_report, warnings, blocking_reasons)
    source_fields = _source_fields(
        profile,
        outcome_field,
        date_field,
        treatment_unit_field,
        _resolve_field(profile, "spend"),
        profile.channel_field,
    )
    production_eligible = _production_eligible(status, workflow_type)

    metadata = _build_metadata(
        objective=objective,
        workflow_type=workflow_type,
        status=status,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        source_fields=source_fields,
        feasibility=feasibility,
        readiness_report=readiness_report,
        production_eligible=production_eligible,
    )

    return GeoXConfigDraft(
        metadata=metadata,
        outcome_field=outcome_field,
        date_field=date_field,
        pre_period_field=PRE_PERIOD_PLACEHOLDER,
        test_period_field=TEST_PERIOD_PLACEHOLDER,
        treatment_unit_field=treatment_unit_field,
        spend_field=_resolve_field(profile, "spend"),
        channel_field=profile.channel_field,
        controls_placeholder=CONTROLS_PLACEHOLDER,
        exclusions_placeholder=EXCLUSIONS_PLACEHOLDER,
    )


def draft_config_for_objective(
    objective: BusinessObjective,
    feasibility: ObjectiveFeasibilityReport,
    readiness_report: DataReadinessReport,
) -> MMMConfigDraft | GeoXConfigDraft:
    """Route config drafting to MMM or GeoX based on objective and supported workflows."""
    recommended = set(feasibility.recommended_workflows)
    geox_capable = bool(recommended & _GEOX_WORKFLOWS)
    mmm_capable = _mmm_workflow_supported(feasibility)

    if objective.objective_type == BusinessObjectiveType.EXPERIMENT_DESIGN:
        return draft_geox_config(objective, feasibility, readiness_report)
    if objective.objective_type == BusinessObjectiveType.AWARENESS and geox_capable:
        return draft_geox_config(objective, feasibility, readiness_report)
    if geox_capable and not mmm_capable:
        return draft_geox_config(objective, feasibility, readiness_report)
    return draft_mmm_config(objective, feasibility, readiness_report)


def _derive_draft_status(
    feasibility: ObjectiveFeasibilityReport,
    readiness_report: DataReadinessReport,
    warnings: list[str],
    blocking_reasons: list[str],
) -> DraftConfigStatus:
    if blocking_reasons:
        return DraftConfigStatus.BLOCKED
    if (
        feasibility.status == FeasibilityStatus.BLOCKED
        or readiness_report.status == DataReadinessStatus.BLOCKED
    ):
        return DraftConfigStatus.BLOCKED
    if (
        readiness_report.status == DataReadinessStatus.DIAGNOSTIC_ONLY
        or feasibility.status == FeasibilityStatus.DIAGNOSTIC_ONLY
    ):
        return DraftConfigStatus.DIAGNOSTIC_ONLY
    if (
        feasibility.status == FeasibilityStatus.FEASIBLE_WITH_WARNINGS
        or readiness_report.status == DataReadinessStatus.READY_WITH_WARNINGS
        or warnings
    ):
        return DraftConfigStatus.DRAFTABLE_WITH_WARNINGS
    return DraftConfigStatus.DRAFTABLE


def _collect_warnings(
    feasibility: ObjectiveFeasibilityReport,
    readiness_report: DataReadinessReport,
) -> list[str]:
    return _dedupe_stable([*feasibility.warnings, *readiness_report.warnings])


def _collect_blocking_reasons(
    feasibility: ObjectiveFeasibilityReport,
    readiness_report: DataReadinessReport,
) -> list[str]:
    return _dedupe_stable(
        [*feasibility.blocking_reasons, *readiness_report.blocking_reasons]
    )


def _mmm_workflow_supported(feasibility: ObjectiveFeasibilityReport) -> bool:
    recommended = set(feasibility.recommended_workflows)
    return bool(recommended & _MMM_WORKFLOWS)


def _geox_workflow_supported(feasibility: ObjectiveFeasibilityReport) -> bool:
    recommended = set(feasibility.recommended_workflows)
    return bool(recommended & _GEOX_WORKFLOWS)


def _select_workflow(
    recommended_workflows: list[WorkflowType],
    allowed: frozenset[WorkflowType],
) -> WorkflowType:
    for workflow in recommended_workflows:
        if workflow in allowed:
            return workflow
    if WorkflowType.DIAGNOSTIC_ONLY in recommended_workflows:
        return WorkflowType.DIAGNOSTIC_ONLY
    return next(iter(recommended_workflows))


def _resolve_field(profile: DatasetProfile, field_name: str) -> str | None:
    if field_name in profile.available_fields:
        return field_name
    return None


def _resolve_outcome_field(
    profile: DatasetProfile,
    objective_type: BusinessObjectiveType,
) -> str | None:
    for candidate in _OUTCOME_CANDIDATES.get(objective_type, ()):
        resolved = _resolve_field(profile, candidate)
        if resolved is not None:
            return resolved
    return None


def _profile_time_grain(profile: DatasetProfile) -> str | None:
    grain = profile.time_grain
    if grain == "unknown":
        return None
    return str(grain)


def _source_fields(profile: DatasetProfile, *fields: str | None) -> list[str]:
    ordered = list(profile.available_fields)
    selected = [field for field in fields if field is not None]
    return _dedupe_stable([*selected, *sorted(ordered)])


def _production_eligible(status: DraftConfigStatus, workflow_type: WorkflowType) -> bool:
    if status not in (
        DraftConfigStatus.DRAFTABLE,
        DraftConfigStatus.DRAFTABLE_WITH_WARNINGS,
    ):
        return False
    return workflow_type != WorkflowType.DIAGNOSTIC_ONLY


def _generated_marker(
    objective: BusinessObjective,
    workflow_type: WorkflowType,
    feasibility: ObjectiveFeasibilityReport,
    readiness_report: DataReadinessReport,
) -> str:
    return (
        f"draft:{objective.objective_type}:{workflow_type}:"
        f"{feasibility.status}:{readiness_report.status}"
    )


def _build_metadata(
    *,
    objective: BusinessObjective,
    workflow_type: WorkflowType,
    status: DraftConfigStatus,
    warnings: list[str],
    blocking_reasons: list[str],
    source_fields: list[str],
    feasibility: ObjectiveFeasibilityReport,
    readiness_report: DataReadinessReport,
    production_eligible: bool,
) -> ConfigDraftMetadata:
    validation = ConfigDraftValidationReport(
        status=status,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        production_eligible=production_eligible,
    )
    return ConfigDraftMetadata(
        objective_type=objective.objective_type,
        workflow_type=workflow_type,
        status=status,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        source_fields=source_fields,
        generated_marker=_generated_marker(
            objective,
            workflow_type,
            feasibility,
            readiness_report,
        ),
        production_eligible=production_eligible,
        validation=validation,
    )


def _dedupe_stable(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
