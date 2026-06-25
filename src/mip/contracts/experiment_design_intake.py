"""Experiment design objective and data requirement contracts (P4b / I6b)."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake import DataGrain, GeoGrain
from mip.contracts.intake_assets import DataAssetType

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "roi is",
    "lift estimate",
    "lift is",
    "budget allocation",
    "coefficient",
    "causal effect",
    "production-ready",
    "matched market",
    "matched markets",
    "mde is",
    "power is",
    "powered test",
    "treatment assignment",
    "control assignment",
    "effect estimate is",
)


class ExperimentDesignEntryPath(StrEnum):
    """How experiment-design intent entered the intake flow."""

    MMM_DRIVEN = "mmm_driven"
    STANDALONE_GEOX = "standalone_geox"


class ExperimentObjectiveCategory(StrEnum):
    """High-level experiment objective category."""

    AWARENESS = "awareness"
    DEMAND_CREATION = "demand_creation"
    CONVERSION = "conversion"
    RETENTION_USAGE = "retention_usage"
    MMM_CALIBRATION = "mmm_calibration"
    INCREMENTALITY_VALIDATION = "incrementality_validation"
    UNKNOWN = "unknown"


class ExperimentKpiFamily(StrEnum):
    """Candidate KPI family for experiment design."""

    AWARENESS_SEARCH = "awareness_search"
    TRAFFIC = "traffic"
    FUNNEL_ENGAGEMENT = "funnel_engagement"
    TRIALS_LEADS = "trials_leads"
    CONVERSION_SALES = "conversion_sales"
    REVENUE_ARR = "revenue_arr"
    RETENTION_USAGE = "retention_usage"
    CALIBRATION_ALIGNED = "calibration_aligned"
    UNKNOWN = "unknown"


class ExperimentDesignStatus(StrEnum):
    """Lifecycle status for experiment design intake."""

    DRAFT = "draft"
    NEEDS_CLARIFICATION = "needs_clarification"
    REQUIREMENTS_READY = "requirements_ready"
    DIAGNOSTIC_REQUEST_READY = "diagnostic_request_ready"
    BLOCKED = "blocked"


class ExperimentDesignTriggerReason(StrEnum):
    """Why MMM context triggered an experiment-design bridge."""

    MMM_UNCERTAINTY = "mmm_uncertainty"
    CALIBRATION_GAP = "calibration_gap"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    WEAK_SUPPORT = "weak_support"
    DECISION_SURFACE_AMBIGUITY = "decision_surface_ambiguity"
    STAKEHOLDER_REQUEST = "stakeholder_request"
    CAMPAIGN_LAUNCH = "campaign_launch"
    TACTIC_VALIDATION = "tactic_validation"
    UNKNOWN = "unknown"


class ExperimentDiagnosticRequestStatus(StrEnum):
    """Status for a future panel_exp diagnostic request."""

    DRAFT = "draft"
    READY_FOR_PANEL_EXP_DIAGNOSTICS = "ready_for_panel_exp_diagnostics"
    NEEDS_DATA = "needs_data"
    BLOCKED = "blocked"


def _assert_no_forbidden_claims(*text_fields: str) -> None:
    combined = " ".join(text_fields).lower()
    for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
        if fragment in combined:
            msg = f"experiment design contract must not contain forbidden claim: {fragment}"
            raise ValueError(msg)


class ExperimentDesignObjective(ContractBaseModel):
    """Structured experiment-design objective before GeoX execution."""

    objective_id: str
    entry_path: ExperimentDesignEntryPath
    objective_category: ExperimentObjectiveCategory
    business_question: str
    product_scope: str | None = None
    platform_scope: str | None = None
    channel_scope: str | None = None
    tactic_scope: str | None = None
    geo_grain: GeoGrain = GeoGrain.UNKNOWN
    market_scope: str | None = None
    candidate_kpi_families: list[ExperimentKpiFamily] = Field(default_factory=list)
    primary_kpi_candidates: list[str] = Field(default_factory=list)
    intended_decision: str | None = None
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("objective_id", "business_question")
    @classmethod
    def required_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "objective_id and business_question cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator(
        "product_scope",
        "platform_scope",
        "channel_scope",
        "tactic_scope",
        "market_scope",
        "intended_decision",
    )
    @classmethod
    def optional_strings_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "optional scope fields cannot be empty when provided"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def no_forbidden_claims(self) -> "ExperimentDesignObjective":
        _assert_no_forbidden_claims(
            self.business_question,
            *(self.primary_kpi_candidates or []),
            *(self.warnings or []),
            *(self.blocking_reasons or []),
            self.intended_decision or "",
        )
        return self


class MMMToGeoXDesignBridge(ContractBaseModel):
    """MMM context that motivates a future GeoX design request."""

    bridge_id: str
    source_mmm_artifact_id: str | None = None
    source_trust_report_id: str | None = None
    source_recommendation_id: str | None = None
    trigger_reason: ExperimentDesignTriggerReason
    channel_scope: str | None = None
    platform_scope: str | None = None
    product_scope: str | None = None
    geo_scope: str | None = None
    metric_id: str | None = None
    estimand_id: str | None = None
    why_experiment_needed: str
    requires_calibration_signal_output: bool = False
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("bridge_id", "why_experiment_needed")
    @classmethod
    def required_bridge_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "bridge_id and why_experiment_needed cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def bridge_rules(self) -> "MMMToGeoXDesignBridge":
        _assert_no_forbidden_claims(
            self.why_experiment_needed,
            *(self.warnings or []),
            *(self.blocking_reasons or []),
        )
        return self


class StandaloneGeoXDesignRequest(ContractBaseModel):
    """Standalone GeoX experiment-design request without MMM bridge."""

    request_id: str
    business_question: str
    objective_category: ExperimentObjectiveCategory = ExperimentObjectiveCategory.UNKNOWN
    product_scope: str | None = None
    platform_scope: str | None = None
    channel_scope: str | None = None
    tactic_scope: str | None = None
    geo_grain: GeoGrain = GeoGrain.UNKNOWN
    market_scope: str | None = None
    candidate_kpi_families: list[ExperimentKpiFamily] = Field(default_factory=list)
    primary_kpi_candidates: list[str] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("request_id", "business_question")
    @classmethod
    def required_request_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id and business_question cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def unknown_objective_requires_questions(self) -> "StandaloneGeoXDesignRequest":
        if (
            self.objective_category == ExperimentObjectiveCategory.UNKNOWN
            and not self.clarification_questions
        ):
            msg = "unknown objective_category requires non-empty clarification_questions"
            raise ValueError(msg)
        _assert_no_forbidden_claims(
            self.business_question,
            *(self.clarification_questions or []),
            *(self.warnings or []),
            *(self.blocking_reasons or []),
        )
        return self


class ExperimentDesignDataRequirement(ContractBaseModel):
    """Objective-specific data requirement guidance (not data validation)."""

    requirement_id: str
    objective_category: ExperimentObjectiveCategory
    kpi_family: ExperimentKpiFamily
    required_data_assets: list[DataAssetType] = Field(default_factory=list)
    recommended_data_assets: list[DataAssetType] = Field(default_factory=list)
    minimum_geo_grain: GeoGrain = GeoGrain.UNKNOWN
    minimum_time_grain: DataGrain = DataGrain.UNKNOWN
    required_history_guidance: str
    why_required: str
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("requirement_id", "required_history_guidance", "why_required")
    @classmethod
    def requirement_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "requirement_id, required_history_guidance, and why_required cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def no_forbidden_claims(self) -> "ExperimentDesignDataRequirement":
        _assert_no_forbidden_claims(
            self.required_history_guidance,
            self.why_required,
            *(self.warnings or []),
            *(self.blocking_reasons or []),
        )
        return self


class ExperimentDesignIntake(ContractBaseModel):
    """Governed experiment-design intake bundle before diagnostics."""

    intake_id: str
    session_id: str
    recommendation_id: str
    entry_path: ExperimentDesignEntryPath
    objective: ExperimentDesignObjective
    mmm_bridge: MMMToGeoXDesignBridge | None = None
    standalone_request: StandaloneGeoXDesignRequest | None = None
    data_requirements: list[ExperimentDesignDataRequirement] = Field(default_factory=list)
    clarification_questions: list[str] = Field(default_factory=list)
    status: ExperimentDesignStatus = ExperimentDesignStatus.DRAFT
    allowed_next_steps: list[str] = Field(default_factory=list)
    blocked_next_steps: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("intake_id", "session_id", "recommendation_id")
    @classmethod
    def intake_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "intake_id, session_id, and recommendation_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def intake_entry_path_rules(self) -> "ExperimentDesignIntake":
        if self.entry_path == ExperimentDesignEntryPath.MMM_DRIVEN and self.mmm_bridge is None:
            msg = "mmm_driven entry_path requires mmm_bridge"
            raise ValueError(msg)
        if (
            self.entry_path == ExperimentDesignEntryPath.STANDALONE_GEOX
            and self.standalone_request is None
        ):
            msg = "standalone_geox entry_path requires standalone_request"
            raise ValueError(msg)
        if self.status == ExperimentDesignStatus.BLOCKED and not self.blocking_reasons:
            msg = "blocked experiment design intake requires blocking_reasons"
            raise ValueError(msg)
        _assert_no_forbidden_claims(
            *(self.clarification_questions or []),
            *(self.warnings or []),
            *(self.blocking_reasons or []),
            *(self.allowed_next_steps or []),
        )
        return self


class ExperimentDiagnosticRequest(ContractBaseModel):
    """Request for future panel_exp/GeoX diagnostics (no diagnostic results)."""

    diagnostic_request_id: str
    experiment_intake_id: str
    session_id: str
    entry_path: ExperimentDesignEntryPath
    objective_category: ExperimentObjectiveCategory
    candidate_kpi_families: list[ExperimentKpiFamily] = Field(default_factory=list)
    product_scope: str | None = None
    platform_scope: str | None = None
    channel_scope: str | None = None
    tactic_scope: str | None = None
    geo_grain: GeoGrain = GeoGrain.UNKNOWN
    market_scope: str | None = None
    required_data_assets: list[DataAssetType] = Field(default_factory=list)
    requires_power_diagnostic: bool = True
    requires_matchability_diagnostic: bool = False
    requires_duration_sensitivity: bool = True
    requires_calibration_signal_output: bool = False
    status: ExperimentDiagnosticRequestStatus = ExperimentDiagnosticRequestStatus.DRAFT
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("diagnostic_request_id", "experiment_intake_id", "session_id")
    @classmethod
    def diagnostic_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "diagnostic_request_id, experiment_intake_id, and session_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def diagnostic_request_rules(self) -> "ExperimentDiagnosticRequest":
        if self.status == ExperimentDiagnosticRequestStatus.BLOCKED and not self.blocking_reasons:
            msg = "blocked diagnostic request requires blocking_reasons"
            raise ValueError(msg)
        _assert_no_forbidden_claims(
            *(self.warnings or []),
            *(self.blocking_reasons or []),
        )
        return self
