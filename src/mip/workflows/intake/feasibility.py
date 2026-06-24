"""Objective feasibility evaluation from declared data availability."""

from enum import StrEnum

from pydantic import Field, model_validator

from mip.contracts.base import ContractBaseModel
from mip.workflows.intake.availability import DataAvailabilityProfile, has_field_or_alias
from mip.workflows.intake.objectives import (
    BusinessObjective,
    BusinessObjectiveType,
    DecisionScope,
)
from mip.workflows.intake.requirements import (
    ObjectiveDataRequirement,
    WorkflowType,
    requirement_for_objective,
)

_AWARENESS_ALIASES = frozenset(
    {
        "brand_search",
        "reach",
        "impressions",
        "site_visits",
        "brand_lift",
        "survey_lift",
        "upper_funnel_kpi",
    }
)

_RETENTION_ALIASES = frozenset(
    {
        "renewals",
        "churn",
        "repeat_purchase",
        "active_users",
    }
)

_OUTCOME_LIKE_FIELDS = frozenset(
    {
        "conversions",
        "revenue",
        "new_customers",
        "outcome",
        "subscriptions",
        "trials",
        "pipeline",
        "margin",
        "experiment_evidence",
        "estimand",
        "retention_kpi",
        "awareness_kpi",
        *_AWARENESS_ALIASES,
        *_RETENTION_ALIASES,
    }
)

_MMM_OBJECTIVES = frozenset(
    {
        BusinessObjectiveType.CONVERSION_ROI,
        BusinessObjectiveType.REVENUE_ROI,
        BusinessObjectiveType.NEW_CUSTOMER_ACQUISITION,
        BusinessObjectiveType.RETENTION,
        BusinessObjectiveType.PROFIT,
        BusinessObjectiveType.SUBSCRIPTIONS,
        BusinessObjectiveType.TRIALS,
        BusinessObjectiveType.PIPELINE,
        BusinessObjectiveType.BUDGET_ALLOCATION,
    }
)

_FIELD_QUESTIONS: dict[str, str] = {
    "revenue": "Do you have revenue or order value data for the same time grain as spend?",
    "new_customers": (
        "Can you provide a KPI that separates new customers from returning customers?"
    ),
    "awareness_kpi": (
        "Do you have upper-funnel data such as brand search, reach, impressions, "
        "site visits, survey lift, or brand-lift results?"
    ),
    "geo": "Do you have region, DMA, state, or market-level identifiers?",
    "channel": "Is spend broken out by marketing channel?",
    "margin": "Do you have margin, cost, or profit data aligned to revenue?",
}


class FeasibilityStatus(StrEnum):
    """Whether an objective is feasible given declared data."""

    FEASIBLE = "feasible"
    FEASIBLE_WITH_WARNINGS = "feasible_with_warnings"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    RESEARCH_ONLY = "research_only"
    BLOCKED = "blocked"


class ObjectiveFeasibilityReport(ContractBaseModel):
    """Deterministic feasibility verdict for a business objective."""

    objective: BusinessObjective
    requirement: ObjectiveDataRequirement
    availability: DataAvailabilityProfile
    status: FeasibilityStatus
    missing_required_fields: list[str] = Field(default_factory=list)
    present_required_fields: list[str] = Field(default_factory=list)
    missing_recommended_fields: list[str] = Field(default_factory=list)
    supported_workflows: list[WorkflowType]
    recommended_workflows: list[WorkflowType]
    fallback_objectives: list[BusinessObjectiveType] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    next_data_to_request: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def status_consistency(self) -> "ObjectiveFeasibilityReport":
        if not self.supported_workflows:
            msg = "supported_workflows cannot be empty"
            raise ValueError(msg)
        if self.status == FeasibilityStatus.BLOCKED and not self.blocking_reasons:
            msg = "blocked status requires blocking_reasons"
            raise ValueError(msg)
        if self.status == FeasibilityStatus.FEASIBLE and self.missing_required_fields:
            msg = "feasible status cannot have missing required fields"
            raise ValueError(msg)
        if self.status == FeasibilityStatus.DIAGNOSTIC_ONLY:
            if WorkflowType.DIAGNOSTIC_ONLY not in self.recommended_workflows:
                msg = "diagnostic_only status must recommend diagnostic_only workflow"
                raise ValueError(msg)
        return self


def evaluate_objective_feasibility(
    objective: BusinessObjective,
    availability: DataAvailabilityProfile,
) -> ObjectiveFeasibilityReport:
    """Evaluate whether an objective is feasible from declared field availability."""
    requirement = requirement_for_objective(objective.objective_type)
    present_required, missing_required = _partition_required_fields(availability, requirement)
    missing_recommended = _missing_recommended_fields(availability, requirement)

    blocking_reasons: list[str] = []
    fallback_objectives: list[BusinessObjectiveType] = []
    warnings: list[str] = []
    force_blocked = False

    force_blocked, blocking_reasons, fallback_objectives = _apply_special_objective_rules(
        objective.objective_type,
        availability,
        missing_required,
        blocking_reasons,
        fallback_objectives,
    )

    diagnostic_reasonable = _diagnostic_fallback_reasonable(availability)
    supported_workflows = list(requirement.supported_workflows)

    if missing_required:
        if force_blocked:
            status = FeasibilityStatus.BLOCKED
            recommended_workflows = (
                [WorkflowType.DIAGNOSTIC_ONLY]
                if diagnostic_reasonable
                else [WorkflowType.DIAGNOSTIC_ONLY]
                if WorkflowType.DIAGNOSTIC_ONLY in supported_workflows
                else supported_workflows[:1]
            )
            if not blocking_reasons:
                blocking_reasons.append(
                    f"Missing required fields: {', '.join(missing_required)}"
                )
        elif diagnostic_reasonable:
            status = FeasibilityStatus.DIAGNOSTIC_ONLY
            recommended_workflows = [WorkflowType.DIAGNOSTIC_ONLY]
            warnings.append(
                "Required fields are missing; only diagnostic analysis is recommended."
            )
        else:
            status = FeasibilityStatus.BLOCKED
            recommended_workflows = [WorkflowType.DIAGNOSTIC_ONLY]
            blocking_reasons.append(
                f"Missing required fields: {', '.join(missing_required)}"
            )
    else:
        status = FeasibilityStatus.FEASIBLE
        recommended_workflows = _recommended_workflows_for_requirement(requirement)
        if missing_recommended:
            status = FeasibilityStatus.FEASIBLE_WITH_WARNINGS
            warnings.append(
                f"Missing recommended fields: {', '.join(missing_recommended)}"
            )

    if not missing_required:
        if (
            objective.objective_type in _MMM_OBJECTIVES
            and availability.history_weeks is not None
            and availability.history_weeks < 52
        ):
            if status == FeasibilityStatus.FEASIBLE:
                status = FeasibilityStatus.FEASIBLE_WITH_WARNINGS
            warnings.append(
                f"Limited history ({availability.history_weeks} weeks) may be insufficient for MMM."
            )

        if (
            objective.decision_scope == DecisionScope.GEO
            and availability.has_geo_breakdown is False
        ):
            warnings.append(
                "Geo-level decision scope requested but geo breakdown is not declared."
            )
            if status == FeasibilityStatus.FEASIBLE:
                status = FeasibilityStatus.FEASIBLE_WITH_WARNINGS

    next_data_to_request = list(missing_required)

    return ObjectiveFeasibilityReport(
        objective=objective,
        requirement=requirement,
        availability=availability,
        status=status,
        missing_required_fields=missing_required,
        present_required_fields=present_required,
        missing_recommended_fields=missing_recommended,
        supported_workflows=supported_workflows,
        recommended_workflows=recommended_workflows,
        fallback_objectives=fallback_objectives,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        next_data_to_request=next_data_to_request,
    )


def recommended_next_questions(report: ObjectiveFeasibilityReport) -> list[str]:
    """Return follow-up intake questions based on missing fields."""
    questions: list[str] = []
    seen: set[str] = set()

    for field_name in [*report.next_data_to_request, *report.missing_recommended_fields]:
        if field_name in seen:
            continue
        seen.add(field_name)
        question = _FIELD_QUESTIONS.get(field_name, f"Can you provide {field_name}?")
        if question not in questions:
            questions.append(question)

    return questions


def _partition_required_fields(
    availability: DataAvailabilityProfile,
    requirement: ObjectiveDataRequirement,
) -> tuple[list[str], list[str]]:
    present: list[str] = []
    missing: list[str] = []
    for field_requirement in requirement.required_fields:
        if has_field_or_alias(availability, field_requirement):
            present.append(field_requirement.field_name)
        else:
            missing.append(field_requirement.field_name)
    return present, missing


def _missing_recommended_fields(
    availability: DataAvailabilityProfile,
    requirement: ObjectiveDataRequirement,
) -> list[str]:
    missing: list[str] = []
    for field_requirement in requirement.recommended_fields:
        if not has_field_or_alias(availability, field_requirement):
            missing.append(field_requirement.field_name)
    return missing


def _diagnostic_fallback_reasonable(availability: DataAvailabilityProfile) -> bool:
    if "date" not in availability.available_fields:
        return False
    return bool(availability.available_fields.intersection(_OUTCOME_LIKE_FIELDS))


def _recommended_workflows_for_requirement(
    requirement: ObjectiveDataRequirement,
) -> list[WorkflowType]:
    non_diagnostic: list[WorkflowType] = [
        workflow
        for workflow in requirement.supported_workflows
        if workflow != WorkflowType.DIAGNOSTIC_ONLY
    ]
    if non_diagnostic:
        return non_diagnostic
    return [WorkflowType.DIAGNOSTIC_ONLY]


def _has_awareness_kpi(availability: DataAvailabilityProfile) -> bool:
    candidates = {"awareness_kpi", *_AWARENESS_ALIASES}
    return bool(candidates.intersection(availability.available_fields))


def _apply_special_objective_rules(
    objective_type: BusinessObjectiveType,
    availability: DataAvailabilityProfile,
    missing_required: list[str],
    blocking_reasons: list[str],
    fallback_objectives: list[BusinessObjectiveType],
) -> tuple[bool, list[str], list[BusinessObjectiveType]]:
    force_blocked = False
    fields = availability.available_fields

    if objective_type == BusinessObjectiveType.AWARENESS:
        if "conversions" in fields and not _has_awareness_kpi(availability):
            force_blocked = True
            blocking_reasons.append(
                "Conversions-only data is not sufficient for awareness measurement."
            )
            fallback_objectives.append(BusinessObjectiveType.CONVERSION_ROI)

    elif objective_type == BusinessObjectiveType.NEW_CUSTOMER_ACQUISITION:
        if "new_customers" in missing_required and (
            "conversions" in fields or "total_conversions" in fields
        ):
            force_blocked = True
            blocking_reasons.append(
                "Total conversions do not distinguish new vs returning customers."
            )
            fallback_objectives.append(BusinessObjectiveType.CONVERSION_ROI)

    elif objective_type == BusinessObjectiveType.REVENUE_ROI:
        if "revenue" in missing_required and "conversions" in fields:
            force_blocked = True
            blocking_reasons.append(
                "Conversion data alone is not sufficient for revenue ROI analysis."
            )
            fallback_objectives.append(BusinessObjectiveType.CONVERSION_ROI)

    elif objective_type == BusinessObjectiveType.PROFIT:
        if "margin" in missing_required and "revenue" in fields:
            force_blocked = True
            blocking_reasons.append(
                "Revenue without margin or cost data is not sufficient for profit analysis."
            )
            fallback_objectives.append(BusinessObjectiveType.REVENUE_ROI)

    return force_blocked, blocking_reasons, fallback_objectives
