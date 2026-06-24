"""Business objective models for progressive intake."""

from enum import StrEnum

from pydantic import field_validator

from mip.contracts.base import ContractBaseModel


class BusinessObjectiveType(StrEnum):
    """Measurable business goal a user wants to address."""

    CONVERSION_ROI = "conversion_roi"
    REVENUE_ROI = "revenue_roi"
    NEW_CUSTOMER_ACQUISITION = "new_customer_acquisition"
    AWARENESS = "awareness"
    RETENTION = "retention"
    PROFIT = "profit"
    SUBSCRIPTIONS = "subscriptions"
    TRIALS = "trials"
    PIPELINE = "pipeline"
    BUDGET_ALLOCATION = "budget_allocation"
    EXPERIMENT_DESIGN = "experiment_design"
    MMM_CALIBRATION = "mmm_calibration"
    DIAGNOSTIC_ANALYSIS = "diagnostic_analysis"


class DecisionHorizon(StrEnum):
    """Time horizon for the decision."""

    CAMPAIGN = "campaign"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    ALWAYS_ON = "always_on"
    TEST_PERIOD = "test_period"
    UNKNOWN = "unknown"


class DecisionScope(StrEnum):
    """Granularity at which the user wants to decide or analyze."""

    CHANNEL = "channel"
    GEO = "geo"
    PRODUCT = "product"
    SEGMENT = "segment"
    CAMPAIGN = "campaign"
    WITHIN_CHANNEL = "within_channel"
    PORTFOLIO = "portfolio"
    UNKNOWN = "unknown"


class RiskTolerance(StrEnum):
    """User tolerance for uncertainty in recommendations."""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    UNKNOWN = "unknown"


class BusinessObjective(ContractBaseModel):
    """User-stated business objective; fields may be filled progressively."""

    objective_type: BusinessObjectiveType
    primary_kpi: str | None = None
    decision_horizon: DecisionHorizon = DecisionHorizon.UNKNOWN
    decision_scope: DecisionScope = DecisionScope.UNKNOWN
    risk_tolerance: RiskTolerance = RiskTolerance.UNKNOWN
    description: str | None = None

    @field_validator("primary_kpi", "description")
    @classmethod
    def optional_strings_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "primary_kpi and description cannot be empty when provided"
            raise ValueError(msg)
        return value
