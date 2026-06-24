"""Objective-to-data requirement catalog."""

from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.workflows.intake.objectives import BusinessObjectiveType


class WorkflowType(StrEnum):
    """Feasible analytical workflow for an objective."""

    MMM_CHANNEL_ROI = "mmm_channel_roi"
    MMM_BUDGET_ALLOCATION = "mmm_budget_allocation"
    GEOX_EXPERIMENT_DESIGN = "geox_experiment_design"
    GEOX_EXPERIMENT_READOUT = "geox_experiment_readout"
    MMM_CALIBRATION = "mmm_calibration"
    SCENARIO_PLANNING = "scenario_planning"
    DIAGNOSTIC_ONLY = "diagnostic_only"


class DataFieldRole(StrEnum):
    """Whether a data field is required, recommended, or optional."""

    REQUIRED = "required"
    RECOMMENDED = "recommended"
    OPTIONAL = "optional"


class DataFieldRequirement(ContractBaseModel):
    """Single data field needed for an objective."""

    field_name: str
    role: DataFieldRole
    description: str
    accepted_aliases: list[str] = Field(default_factory=list)

    @field_validator("field_name", "description")
    @classmethod
    def non_empty_strings(cls, value: str) -> str:
        if not value.strip():
            msg = "field_name and description cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("accepted_aliases")
    @classmethod
    def aliases_not_empty(cls, value: list[str]) -> list[str]:
        if any(not alias.strip() for alias in value):
            msg = "accepted_aliases cannot contain empty strings"
            raise ValueError(msg)
        return value


class ObjectiveDataRequirement(ContractBaseModel):
    """Data and workflow requirements for a business objective type."""

    objective_type: BusinessObjectiveType
    required_fields: list[DataFieldRequirement]
    recommended_fields: list[DataFieldRequirement] = Field(default_factory=list)
    optional_fields: list[DataFieldRequirement] = Field(default_factory=list)
    recommended_controls: list[str] = Field(default_factory=list)
    minimum_time_grain: str
    recommended_time_grain: str | None = None
    minimum_history: str
    supported_workflows: list[WorkflowType]
    notes: list[str] = Field(default_factory=list)

    @field_validator("minimum_time_grain", "minimum_history")
    @classmethod
    def grain_and_history_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "minimum_time_grain and minimum_history cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("recommended_controls", "notes")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "recommended_controls and notes cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def requirement_lists_valid(self) -> "ObjectiveDataRequirement":
        if not self.required_fields:
            msg = "required_fields cannot be empty"
            raise ValueError(msg)
        if not self.supported_workflows:
            msg = "supported_workflows cannot be empty"
            raise ValueError(msg)
        return self


def _field(
    name: str,
    role: DataFieldRole,
    description: str,
    aliases: list[str] | None = None,
) -> DataFieldRequirement:
    return DataFieldRequirement(
        field_name=name,
        role=role,
        description=description,
        accepted_aliases=aliases or [],
    )


def _req(
    objective_type: BusinessObjectiveType,
    *,
    required: list[DataFieldRequirement],
    recommended: list[DataFieldRequirement] | None = None,
    controls: list[str] | None = None,
    minimum_time_grain: str = "weekly",
    recommended_time_grain: str | None = "weekly",
    minimum_history: str = "52 weeks",
    workflows: list[WorkflowType],
    notes: list[str] | None = None,
) -> ObjectiveDataRequirement:
    return ObjectiveDataRequirement(
        objective_type=objective_type,
        required_fields=required,
        recommended_fields=recommended or [],
        recommended_controls=controls or [],
        minimum_time_grain=minimum_time_grain,
        recommended_time_grain=recommended_time_grain,
        minimum_history=minimum_history,
        supported_workflows=workflows,
        notes=notes or [],
    )


_MMM_WORKFLOWS = [
    WorkflowType.MMM_CHANNEL_ROI,
    WorkflowType.MMM_BUDGET_ALLOCATION,
    WorkflowType.SCENARIO_PLANNING,
    WorkflowType.DIAGNOSTIC_ONLY,
]

_AWARENESS_ALIASES = [
    "brand_search",
    "reach",
    "impressions",
    "site_visits",
    "brand_lift",
    "survey_lift",
    "upper_funnel_kpi",
]

_RETENTION_ALIASES = [
    "renewals",
    "churn",
    "repeat_purchase",
    "active_users",
]

_REQUIREMENTS: dict[BusinessObjectiveType, ObjectiveDataRequirement] = {
    BusinessObjectiveType.CONVERSION_ROI: _req(
        BusinessObjectiveType.CONVERSION_ROI,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("spend", DataFieldRole.REQUIRED, "Marketing spend"),
            _field("conversions", DataFieldRole.REQUIRED, "Conversion count or rate"),
        ],
        recommended=[
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geographic market identifier"),
            _field("impressions", DataFieldRole.RECOMMENDED, "Impression volume"),
            _field("clicks", DataFieldRole.RECOMMENDED, "Click volume"),
            _field("revenue", DataFieldRole.RECOMMENDED, "Revenue aligned to conversions"),
        ],
        controls=["promotions", "seasonality", "pricing changes", "product launches"],
        workflows=_MMM_WORKFLOWS,
    ),
    BusinessObjectiveType.REVENUE_ROI: _req(
        BusinessObjectiveType.REVENUE_ROI,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("spend", DataFieldRole.REQUIRED, "Marketing spend"),
            _field("revenue", DataFieldRole.REQUIRED, "Revenue outcome"),
        ],
        recommended=[
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geographic market identifier"),
            _field("orders", DataFieldRole.RECOMMENDED, "Order count"),
            _field("conversions", DataFieldRole.RECOMMENDED, "Conversion count"),
        ],
        controls=["promotions", "pricing changes", "discounts", "seasonality"],
        workflows=_MMM_WORKFLOWS,
    ),
    BusinessObjectiveType.NEW_CUSTOMER_ACQUISITION: _req(
        BusinessObjectiveType.NEW_CUSTOMER_ACQUISITION,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("spend", DataFieldRole.REQUIRED, "Marketing spend"),
            _field("new_customers", DataFieldRole.REQUIRED, "New customer count"),
        ],
        recommended=[
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geographic market identifier"),
            _field("total_conversions", DataFieldRole.RECOMMENDED, "Total conversions"),
            _field("returning_customers", DataFieldRole.RECOMMENDED, "Returning customer count"),
        ],
        controls=["promotions", "pricing changes", "product launches", "seasonality"],
        workflows=_MMM_WORKFLOWS,
    ),
    BusinessObjectiveType.AWARENESS: _req(
        BusinessObjectiveType.AWARENESS,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("spend", DataFieldRole.REQUIRED, "Marketing spend"),
            _field(
                "awareness_kpi",
                DataFieldRole.REQUIRED,
                "Upper-funnel awareness KPI",
                aliases=_AWARENESS_ALIASES,
            ),
        ],
        recommended=[
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geographic market identifier"),
            _field("frequency", DataFieldRole.RECOMMENDED, "Exposure frequency"),
        ],
        controls=["seasonality", "product launches", "brand campaigns", "competitive events"],
        workflows=[
            WorkflowType.DIAGNOSTIC_ONLY,
            WorkflowType.GEOX_EXPERIMENT_DESIGN,
            WorkflowType.GEOX_EXPERIMENT_READOUT,
        ],
        notes=["Conversions-only data is not sufficient for awareness measurement."],
    ),
    BusinessObjectiveType.RETENTION: _req(
        BusinessObjectiveType.RETENTION,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("spend", DataFieldRole.REQUIRED, "Marketing spend"),
            _field(
                "retention_kpi",
                DataFieldRole.REQUIRED,
                "Retention outcome KPI",
                aliases=_RETENTION_ALIASES,
            ),
        ],
        recommended=[
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geographic market identifier"),
            _field("customer_cohort", DataFieldRole.RECOMMENDED, "Customer cohort identifier"),
        ],
        controls=["pricing changes", "lifecycle campaigns", "product launches", "seasonality"],
        workflows=[WorkflowType.MMM_CHANNEL_ROI, WorkflowType.DIAGNOSTIC_ONLY],
    ),
    BusinessObjectiveType.PROFIT: _req(
        BusinessObjectiveType.PROFIT,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("spend", DataFieldRole.REQUIRED, "Marketing spend"),
            _field("revenue", DataFieldRole.REQUIRED, "Revenue outcome"),
            _field("margin", DataFieldRole.REQUIRED, "Margin or profit metric"),
        ],
        recommended=[
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geographic market identifier"),
            _field("discounts", DataFieldRole.RECOMMENDED, "Discount depth or incidence"),
            _field("cost", DataFieldRole.RECOMMENDED, "Cost basis for margin"),
        ],
        controls=["promotions", "pricing changes", "discounts", "seasonality"],
        workflows=_MMM_WORKFLOWS,
    ),
    BusinessObjectiveType.SUBSCRIPTIONS: _req(
        BusinessObjectiveType.SUBSCRIPTIONS,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("spend", DataFieldRole.REQUIRED, "Marketing spend"),
            _field("subscriptions", DataFieldRole.REQUIRED, "Subscription count"),
        ],
        recommended=[
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geographic market identifier"),
            _field("trials", DataFieldRole.RECOMMENDED, "Trial starts"),
            _field(
                "trial_to_paid_rate",
                DataFieldRole.RECOMMENDED,
                "Trial-to-paid conversion rate",
            ),
        ],
        controls=["pricing changes", "product launches", "promotions", "seasonality"],
        workflows=_MMM_WORKFLOWS,
    ),
    BusinessObjectiveType.TRIALS: _req(
        BusinessObjectiveType.TRIALS,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("spend", DataFieldRole.REQUIRED, "Marketing spend"),
            _field("trials", DataFieldRole.REQUIRED, "Trial starts"),
        ],
        recommended=[
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geographic market identifier"),
            _field("paid_conversions", DataFieldRole.RECOMMENDED, "Paid conversion count"),
        ],
        controls=["promotions", "product launches", "trial-flow changes", "seasonality"],
        workflows=[WorkflowType.MMM_CHANNEL_ROI, WorkflowType.DIAGNOSTIC_ONLY],
    ),
    BusinessObjectiveType.PIPELINE: _req(
        BusinessObjectiveType.PIPELINE,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("spend", DataFieldRole.REQUIRED, "Marketing spend"),
            _field("pipeline", DataFieldRole.REQUIRED, "Pipeline value or count"),
        ],
        recommended=[
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geographic market identifier"),
            _field("leads", DataFieldRole.RECOMMENDED, "Lead count"),
            _field("opportunities", DataFieldRole.RECOMMENDED, "Opportunity count"),
        ],
        controls=["sales capacity", "pricing changes", "product launches", "seasonality"],
        workflows=[WorkflowType.MMM_CHANNEL_ROI, WorkflowType.DIAGNOSTIC_ONLY],
    ),
    BusinessObjectiveType.BUDGET_ALLOCATION: _req(
        BusinessObjectiveType.BUDGET_ALLOCATION,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("spend", DataFieldRole.REQUIRED, "Marketing spend"),
            _field("outcome", DataFieldRole.REQUIRED, "Primary outcome KPI"),
        ],
        recommended=[
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geographic market identifier"),
            _field("revenue", DataFieldRole.RECOMMENDED, "Revenue outcome"),
            _field("conversions", DataFieldRole.RECOMMENDED, "Conversion count"),
        ],
        controls=["promotions", "pricing changes", "seasonality"],
        workflows=[
            WorkflowType.MMM_BUDGET_ALLOCATION,
            WorkflowType.SCENARIO_PLANNING,
            WorkflowType.DIAGNOSTIC_ONLY,
        ],
    ),
    BusinessObjectiveType.EXPERIMENT_DESIGN: _req(
        BusinessObjectiveType.EXPERIMENT_DESIGN,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("geo", DataFieldRole.REQUIRED, "Geographic unit identifier"),
            _field("outcome", DataFieldRole.REQUIRED, "Outcome KPI for experiment readout"),
        ],
        recommended=[
            _field("spend", DataFieldRole.RECOMMENDED, "Marketing spend"),
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("pre_period", DataFieldRole.RECOMMENDED, "Pre-period indicator or dates"),
            _field("eligible_units", DataFieldRole.RECOMMENDED, "Eligible geo or unit list"),
        ],
        controls=["promotions", "seasonality", "geo exclusions"],
        minimum_time_grain="weekly",
        recommended_time_grain="weekly",
        minimum_history="26 weeks",
        workflows=[WorkflowType.GEOX_EXPERIMENT_DESIGN],
    ),
    BusinessObjectiveType.MMM_CALIBRATION: _req(
        BusinessObjectiveType.MMM_CALIBRATION,
        required=[
            _field("experiment_evidence", DataFieldRole.REQUIRED, "Certified experiment evidence"),
            _field("estimand", DataFieldRole.REQUIRED, "Target estimand for calibration"),
            _field(
                "standard_error",
                DataFieldRole.REQUIRED,
                "Standard error for calibration signal",
            ),
        ],
        recommended=[
            _field(
                "source_experiment_id",
                DataFieldRole.RECOMMENDED,
                "Source experiment identifier",
            ),
            _field("time_window", DataFieldRole.RECOMMENDED, "Calibration time window"),
            _field("channel", DataFieldRole.RECOMMENDED, "Channel mapping target"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geo mapping target"),
        ],
        controls=[],
        minimum_time_grain="experiment window",
        recommended_time_grain=None,
        minimum_history="one experiment readout",
        workflows=[WorkflowType.MMM_CALIBRATION],
    ),
    BusinessObjectiveType.DIAGNOSTIC_ANALYSIS: _req(
        BusinessObjectiveType.DIAGNOSTIC_ANALYSIS,
        required=[
            _field("date", DataFieldRole.REQUIRED, "Calendar date for each observation"),
            _field("outcome", DataFieldRole.REQUIRED, "Outcome KPI to diagnose"),
        ],
        recommended=[
            _field("spend", DataFieldRole.RECOMMENDED, "Marketing spend"),
            _field("channel", DataFieldRole.RECOMMENDED, "Marketing channel identifier"),
            _field("geo", DataFieldRole.RECOMMENDED, "Geographic market identifier"),
        ],
        controls=["seasonality"],
        workflows=[WorkflowType.DIAGNOSTIC_ONLY],
    ),
}


def requirement_for_objective(objective_type: BusinessObjectiveType) -> ObjectiveDataRequirement:
    """Return deterministic data requirements for a business objective type."""
    try:
        return _REQUIREMENTS[objective_type]
    except KeyError as exc:
        msg = f"unsupported objective type: {objective_type}"
        raise ValueError(msg) from exc
