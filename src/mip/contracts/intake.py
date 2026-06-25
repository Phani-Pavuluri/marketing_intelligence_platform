"""Intake session and path recommendation contracts (P1 / I1–I2)."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "roi is",
    "lift estimate",
    "lift is",
    "budget allocation",
    "coefficient",
    "causal effect",
    "production-ready",
)


class IntakeSessionStatus(StrEnum):
    """Lifecycle status for a governed intake session."""

    DRAFT = "draft"
    NEEDS_CLARIFICATION = "needs_clarification"
    READY_FOR_RECOMMENDATION = "ready_for_recommendation"
    RECOMMENDATION_READY = "recommendation_ready"
    BLOCKED = "blocked"


class MeasurementWorkflowKind(StrEnum):
    """High-level measurement workflow the user is entering."""

    MMM = "mmm"
    GEOX = "geox"
    CALIBRATION_INTAKE = "calibration_intake"
    DECISION_REVIEW = "decision_review"


class IntakeIntendedUse(StrEnum):
    """Declared intended use for the intake session."""

    DIAGNOSTIC_ONLY = "diagnostic_only"
    CALIBRATED_MMM = "calibrated_mmm"
    GEO_EXPERIMENT_DESIGN = "geo_experiment_design"
    GEO_EXPERIMENT_READOUT = "geo_experiment_readout"
    DECISION_SURFACE_CANDIDATE = "decision_surface_candidate"
    DECISION_REVIEW_PACKET = "decision_review_packet"
    OPTIMIZER_CANDIDATE = "optimizer_candidate"
    HISTORICAL_EXPLANATION = "historical_explanation"
    CURRENT_PERFORMANCE_SUMMARY = "current_performance_summary"


class IntakeCandidatePath(StrEnum):
    """Candidate modeling or measurement path."""

    NATIONAL_DIAGNOSTIC_MMM = "national_diagnostic_mmm"
    GEO_LEVEL_MMM = "geo_level_mmm"
    CALIBRATED_MMM = "calibrated_mmm"
    EXPERIMENT_CALIBRATION_INTAKE = "experiment_calibration_intake"
    GEO_EXPERIMENT_DESIGN = "geo_experiment_design"
    GEO_EXPERIMENT_READOUT = "geo_experiment_readout"
    DECISION_SURFACE_CERTIFICATION = "decision_surface_certification"
    DECISION_REVIEW_PACKET = "decision_review_packet"
    BLOCKED_NEEDS_MORE_DATA = "blocked_needs_more_data"


class IntakeRecommendationStatus(StrEnum):
    """Status of a deterministic path recommendation."""

    RECOMMENDED = "recommended"
    RECOMMENDED_WITH_WARNINGS = "recommended_with_warnings"
    BLOCKED = "blocked"
    NEEDS_CLARIFICATION = "needs_clarification"


class DataGrain(StrEnum):
    """Temporal grain for intake data."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    UNKNOWN = "unknown"


class GeoGrain(StrEnum):
    """Geographic grain for intake scope."""

    NATIONAL = "national"
    GEO = "geo"
    DMA = "dma"
    REGION = "region"
    MARKET = "market"
    UNKNOWN = "unknown"


class MeasurementIntakeSession(ContractBaseModel):
    """Base intake session capturing user intent before data handoff."""

    session_id: str
    business_question: str
    intended_use: IntakeIntendedUse
    workflow_kind: MeasurementWorkflowKind
    status: IntakeSessionStatus = IntakeSessionStatus.DRAFT
    metric_id: str | None = None
    estimand_id: str | None = None
    time_grain: DataGrain = DataGrain.UNKNOWN
    geo_grain: GeoGrain = GeoGrain.UNKNOWN
    channel_scope: str | None = None
    platform_scope: str | None = None
    campaign_scope: str | None = None
    product_scope: str | None = None
    audience_scope: str | None = None
    market_scope: str | None = None
    reporting_window_start: datetime | None = None
    reporting_window_end: datetime | None = None
    desired_output: str | None = None
    unresolved_questions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_by: str | None = None
    created_at: datetime

    @field_validator("session_id", "business_question")
    @classmethod
    def required_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "session_id and business_question cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator(
        "channel_scope",
        "platform_scope",
        "campaign_scope",
        "product_scope",
        "audience_scope",
        "market_scope",
        "desired_output",
        "created_by",
        "metric_id",
        "estimand_id",
    )
    @classmethod
    def optional_strings_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "optional scope and identifier fields cannot be empty when provided"
            raise ValueError(msg)
        return value


class MMMIntakeSession(MeasurementIntakeSession):
    """MMM-specific intake session fields."""

    model_goal: str | None = None
    requires_calibration: bool = False
    requires_decision_surface: bool = False

    @field_validator("model_goal")
    @classmethod
    def model_goal_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "model_goal cannot be empty when provided"
            raise ValueError(msg)
        return value


class GeoXIntakeSession(MeasurementIntakeSession):
    """GeoX experiment intake session fields."""

    experiment_goal: str | None = None
    design_or_readout: str | None = None
    requires_power: bool = False
    requires_readout: bool = False

    @field_validator("experiment_goal", "design_or_readout")
    @classmethod
    def geox_strings_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "experiment_goal and design_or_readout cannot be empty when provided"
            raise ValueError(msg)
        return value


class IntakePathRecommendation(ContractBaseModel):
    """Deterministic path recommendation for a governed intake session."""

    recommendation_id: str
    session_id: str
    status: IntakeRecommendationStatus
    recommended_path: IntakeCandidatePath
    workflow_kind: MeasurementWorkflowKind
    why_this_path: str
    why_other_paths_blocked: list[str] = Field(default_factory=list)
    required_next_questions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    allowed_next_steps: list[str] = Field(default_factory=list)
    blocked_next_steps: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("recommendation_id", "session_id", "why_this_path")
    @classmethod
    def required_recommendation_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "recommendation_id, session_id, and why_this_path cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def recommendation_status_rules(self) -> "IntakePathRecommendation":
        if self.status == IntakeRecommendationStatus.BLOCKED and not self.blocking_reasons:
            msg = "blocked recommendation requires blocking_reasons"
            raise ValueError(msg)
        if (
            self.status == IntakeRecommendationStatus.NEEDS_CLARIFICATION
            and not self.required_next_questions
        ):
            msg = "needs_clarification recommendation requires required_next_questions"
            raise ValueError(msg)
        self._assert_no_forbidden_claims()
        return self

    def _assert_no_forbidden_claims(self) -> None:
        text_fields = [
            self.why_this_path,
            *self.why_other_paths_blocked,
            *self.warnings,
            *self.allowed_next_steps,
        ]
        combined = " ".join(text_fields).lower()
        for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
            if fragment in combined:
                msg = f"recommendation must not contain forbidden claim fragment: {fragment}"
                raise ValueError(msg)
