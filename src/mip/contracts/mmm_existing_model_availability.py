"""MMM existing model availability gate contracts (metadata only)."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel

RECOMMENDED_NEXT_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AND_READINESS_ARTIFACT = (
    "MIP_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AND_READINESS_001"
)
RECOMMENDED_NEXT_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_ARTIFACT = (
    "MIP_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_001"
)

DEFAULT_MAX_MODEL_AGE_DAYS = 180

_FORBIDDEN_RESULT_FIELD_NAMES = frozenset(
    {
        "spend_delta",
        "delta_mu",
        "roi",
        "roas",
        "lift",
        "incrementality",
        "optimal_budget",
        "marginal_roi",
        "recommendation",
        "budget_recommendation",
    }
)


class MMMModelArtifactStatus(StrEnum):
    """Lifecycle status for a registered MMM model artifact."""

    AVAILABLE = "available"
    AVAILABLE_WITH_WARNINGS = "available_with_warnings"
    STALE = "stale"
    DIAGNOSTICS_FAILED = "diagnostics_failed"
    NOT_PROMOTED = "not_promoted"
    ARCHIVED = "archived"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class MMMModelPromotionStatus(StrEnum):
    """Promotion tier for an MMM model artifact."""

    PROMOTED_FOR_PLANNING = "promoted_for_planning"
    PROMOTED_FOR_DIAGNOSTIC_ONLY = "promoted_for_diagnostic_only"
    NOT_PROMOTED = "not_promoted"
    REVOKED = "revoked"
    UNKNOWN = "unknown"


class MMMModelDiagnosticStatus(StrEnum):
    """Diagnostic outcome for an MMM model artifact."""

    PASSED = "passed"
    PASSED_WITH_WARNINGS = "passed_with_warnings"
    FAILED = "failed"
    NOT_AVAILABLE = "not_available"
    UNKNOWN = "unknown"


class MMMModelAllowedUse(StrEnum):
    """Allowed downstream uses for an MMM model artifact."""

    READ_ONLY_SUMMARY = "read_only_summary"
    SCENARIO_SIMULATION = "scenario_simulation"
    BUDGET_PLANNING = "budget_planning"
    BUDGET_OPTIMIZATION = "budget_optimization"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    MODEL_REFRESH_BASELINE = "model_refresh_baseline"


class MMMExistingModelAvailabilityStatus(StrEnum):
    """Outcome of existing-model availability evaluation."""

    USABLE_EXISTING_MODEL = "usable_existing_model"
    USABLE_EXISTING_MODEL_WITH_WARNINGS = "usable_existing_model_with_warnings"
    REQUIRES_MODEL_REFRESH = "requires_model_refresh"
    REQUIRES_NEW_MODEL_RUN = "requires_new_model_run"
    BLOCKED_NO_CANDIDATE_MODEL = "blocked_no_candidate_model"
    BLOCKED_STALE_MODEL = "blocked_stale_model"
    BLOCKED_DIAGNOSTICS_FAILED = "blocked_diagnostics_failed"
    BLOCKED_NOT_PROMOTED = "blocked_not_promoted"
    BLOCKED_SCOPE_MISMATCH = "blocked_scope_mismatch"
    BLOCKED_METRIC_MISMATCH = "blocked_metric_mismatch"
    BLOCKED_CHANNEL_MISMATCH = "blocked_channel_mismatch"
    BLOCKED_USE_NOT_ALLOWED = "blocked_use_not_allowed"
    BLOCKED_MISSING_TRUST_METADATA = "blocked_missing_trust_metadata"
    DIAGNOSTIC_ONLY = "diagnostic_only"


class MMMExistingModelAvailabilityIssueCode(StrEnum):
    """Typed issue codes for existing-model availability evaluation."""

    NO_CANDIDATE_MODEL = "no_candidate_model"
    CANDIDATE_MODEL_FOUND = "candidate_model_found"
    MODEL_SELECTED = "model_selected"
    MODEL_STALE = "model_stale"
    DIAGNOSTICS_FAILED = "diagnostics_failed"
    MODEL_NOT_PROMOTED = "model_not_promoted"
    SCOPE_MISMATCH = "scope_mismatch"
    METRIC_MISMATCH = "metric_mismatch"
    CHANNEL_MISMATCH = "channel_mismatch"
    USE_NOT_ALLOWED = "use_not_allowed"
    TRUST_METADATA_MISSING = "trust_metadata_missing"
    DECISION_SURFACE_REFERENCE_PRESENT = "decision_surface_reference_present"
    MODEL_CALIBRATION_READINESS_REFERENCE_PRESENT = (
        "model_calibration_readiness_reference_present"
    )
    MODEL_ARTIFACT_METADATA_PRESERVED = "model_artifact_metadata_preserved"
    ALLOWED_USE_MATCHED = "allowed_use_matched"
    REQUIRES_MODEL_REFRESH = "requires_model_refresh"
    REQUIRES_NEW_MODEL_RUN = "requires_new_model_run"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"


class MMMModelArtifact(ContractBaseModel):
    """Metadata-only MMM model artifact record."""

    model_id: str
    model_type: str = "mmm"
    artifact_uri: str | None = None
    artifact_fingerprint: str
    version: str = "1"
    created_at: datetime
    training_start_date: date | None = None
    training_end_date: date | None = None
    data_freshness_date: date | None = None
    geo_scope: list[str] = Field(default_factory=list)
    business_unit: str | None = None
    product_scope: list[str] = Field(default_factory=list)
    channels: list[str] = Field(default_factory=list)
    metrics: list[str] = Field(default_factory=list)
    calibration_signal_ids: list[str] = Field(default_factory=list)
    diagnostic_status: MMMModelDiagnosticStatus = MMMModelDiagnosticStatus.UNKNOWN
    promotion_status: MMMModelPromotionStatus = MMMModelPromotionStatus.UNKNOWN
    allowed_uses: list[MMMModelAllowedUse] = Field(default_factory=list)
    trust_report_id: str | None = None
    decision_surface_id: str | None = None
    model_calibration_readiness_id: str | None = None
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("model_id", "artifact_fingerprint")
    @classmethod
    def non_empty_ids(cls, value: str) -> str:
        if not value.strip():
            msg = "model_id and artifact_fingerprint cannot be empty"
            raise ValueError(msg)
        return value


class MMMModelArtifactQuery(ContractBaseModel):
    """Query describing intended planning use and matching requirements."""

    request_id: str
    intended_use: MMMModelAllowedUse
    geo_scope: str | None = None
    business_unit: str | None = None
    product_scope: str | None = None
    channels: list[str] = Field(default_factory=list)
    metric: str | None = None
    planning_start_date: date | None = None
    planning_end_date: date | None = None
    max_model_age_days: int = DEFAULT_MAX_MODEL_AGE_DAYS
    require_promoted: bool = True
    require_diagnostics_passed: bool = True
    require_trust_metadata: bool = False
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("max_model_age_days")
    @classmethod
    def max_model_age_positive(cls, value: int) -> int:
        if value <= 0:
            msg = "max_model_age_days must be positive"
            raise ValueError(msg)
        return value


class MMMModelArtifactMatch(ContractBaseModel):
    """Per-candidate match evaluation."""

    model_artifact: MMMModelArtifact
    scope_match: bool = False
    metric_match: bool = False
    channel_match: bool = False
    freshness_match: bool = False
    promotion_match: bool = False
    diagnostics_match: bool = False
    allowed_use_match: bool = False
    trust_metadata_match: bool = False
    match_score: int = 0
    warnings: list[str] = Field(default_factory=list)
    issues: list[MMMExistingModelAvailabilityIssueCode] = Field(default_factory=list)


class MMMExistingModelAvailabilityRequest(ContractBaseModel):
    """Request to evaluate existing MMM model availability."""

    request_id: str
    query: MMMModelArtifactQuery
    candidate_models: list[MMMModelArtifact] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


class MMMExistingModelAvailabilityResult(ContractBaseModel):
    """Result of existing-model availability evaluation."""

    request_id: str
    status: MMMExistingModelAvailabilityStatus
    selected_model: MMMModelArtifact | None = None
    candidate_matches: list[MMMModelArtifactMatch] = Field(default_factory=list)
    requires_new_model_run: bool = False
    requires_model_refresh: bool = False
    blocked_reasons: list[str] = Field(default_factory=list)
    allowed_uses: list[MMMModelAllowedUse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    issues: list[MMMExistingModelAvailabilityIssueCode] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


FORBIDDEN_MMM_EXISTING_MODEL_AVAILABILITY_RESULT_FIELD_NAMES = _FORBIDDEN_RESULT_FIELD_NAMES
