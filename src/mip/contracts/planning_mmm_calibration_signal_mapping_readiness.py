"""Planning/MMM calibration-signal mapping and readiness contracts."""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.mmm_existing_model_availability import MMMExistingModelAvailabilityResult
from mip.contracts.planning_mmm_calibration_signal_tabular_intake import (
    PlanningMMMCalibrationSignalTabularIntakeResult,
)
from mip.contracts.tabular_source_reference import TabularSourceReference

RECOMMENDED_NEXT_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_ARTIFACT = (
    "MIP_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_001"
)

DEFAULT_MAX_SIGNAL_AGE_DAYS = 365

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

_CAUSAL_EVIDENCE_SOURCES = frozenset(
    {
        "experiment",
        "randomized_experiment",
        "geox",
        "geo_experiment",
        "causal",
        "incrementality_test",
    }
)


class PlanningMMMCalibrationSignalMappingStatus(StrEnum):
    """Outcome of calibration-signal mapping from tabular intake."""

    MAPPING_READY = "mapping_ready"
    MAPPING_READY_WITH_WARNINGS = "mapping_ready_with_warnings"
    MAPPING_DEFERRED = "mapping_deferred"
    BLOCKED_MISSING_INTAKE = "blocked_missing_intake"
    BLOCKED_INTAKE_NOT_READY = "blocked_intake_not_ready"
    BLOCKED_MISSING_REQUIRED_FIELDS = "blocked_missing_required_fields"
    BLOCKED_INCOMPATIBLE_ESTIMAND = "blocked_incompatible_estimand"
    BLOCKED_INCOMPATIBLE_METRIC = "blocked_incompatible_metric"
    BLOCKED_INCOMPATIBLE_CHANNEL = "blocked_incompatible_channel"
    BLOCKED_INCOMPATIBLE_TIME_WINDOW = "blocked_incompatible_time_window"
    DIAGNOSTIC_ONLY = "diagnostic_only"


class PlanningMMMCalibrationSignalReadinessStatus(StrEnum):
    """Calibration readiness for model calibration purposes."""

    READY_FOR_MODEL_CALIBRATION = "ready_for_model_calibration"
    READY_WITH_WARNINGS = "ready_with_warnings"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    STALE_REQUIRES_REVIEW = "stale_requires_review"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


class PlanningMMMCalibrationSignalUsability(StrEnum):
    """Usability classification for one mapped calibration signal."""

    USABLE_FOR_CALIBRATION = "usable_for_calibration"
    USABLE_WITH_WARNINGS = "usable_with_warnings"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    STALE = "stale"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


class PlanningMMMCalibrationSignalMappingIssueCode(StrEnum):
    """Typed issue codes for calibration-signal mapping and readiness."""

    INTAKE_MISSING = "intake_missing"
    INTAKE_NOT_READY = "intake_not_ready"
    REQUIRED_FIELD_MISSING = "required_field_missing"
    METRIC_ALIGNED = "metric_aligned"
    METRIC_MISMATCH = "metric_mismatch"
    CHANNEL_ALIGNED = "channel_aligned"
    CHANNEL_MISMATCH = "channel_mismatch"
    ESTIMAND_ALIGNED = "estimand_aligned"
    ESTIMAND_MISMATCH = "estimand_mismatch"
    TIME_WINDOW_ALIGNED = "time_window_aligned"
    TIME_WINDOW_MISMATCH = "time_window_mismatch"
    FRESHNESS_VALID = "freshness_valid"
    FRESHNESS_STALE = "freshness_stale"
    UNCERTAINTY_PRESENT = "uncertainty_present"
    UNCERTAINTY_MISSING = "uncertainty_missing"
    CAUSAL_SIGNAL = "causal_signal"
    DIAGNOSTIC_ONLY_SIGNAL = "diagnostic_only_signal"
    MAPPING_DEFERRED = "mapping_deferred"
    CALIBRATION_SIGNAL_METADATA_COMPATIBLE = "calibration_signal_metadata_compatible"
    MODEL_CALIBRATION_READINESS_REFERENCE_CREATED = "model_calibration_readiness_reference_created"
    DATA_SOURCE_REF_PRESERVED = "data_source_ref_preserved"
    TABULAR_SOURCE_REF_PRESERVED = "tabular_source_ref_preserved"
    LINEAGE_PRESERVED = "lineage_preserved"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_PRIOR_APPLICATION = "no_prior_application"
    NO_LIKELIHOOD_CONSTRUCTION = "no_likelihood_construction"
    NO_POSTERIOR_CALCULATION = "no_posterior_calculation"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"


class PlanningMMMCalibrationSignalMappingTarget(ContractBaseModel):
    """Target model/planning context for calibration-signal alignment."""

    target_model_id: str
    metric: str
    channels: list[str] = Field(default_factory=list)
    estimand: str
    planning_start_date: date | None = None
    planning_end_date: date | None = None
    max_signal_age_days: int = DEFAULT_MAX_SIGNAL_AGE_DAYS
    allow_diagnostic_only: bool = False
    require_uncertainty: bool = True
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("target_model_id", "metric", "estimand")
    @classmethod
    def non_empty_target_fields(cls, value: str) -> str:
        if not value.strip():
            msg = "target_model_id, metric, and estimand cannot be empty"
            raise ValueError(msg)
        return value


class PlanningMMMCalibrationSignalRecordMetadata(ContractBaseModel):
    """Row-level calibration signal metadata for mapping evaluation."""

    record_id: str
    source_id: str
    metric: str | None = None
    channel: str | None = None
    estimand: str | None = None
    effect_field_name: str | None = None
    uncertainty_field_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    freshness_date: date | None = None
    evidence_source: str | None = None
    geo_scope: str | None = None


class PlanningMMMCalibrationSignalMappedRecord(ContractBaseModel):
    """Metadata-only mapped calibration signal record."""

    record_id: str
    source_id: str
    intake_record_id: str | None = None
    metric: str | None = None
    channel: str | None = None
    estimand: str | None = None
    effect_field_name: str | None = None
    uncertainty_field_name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    freshness_date: date | None = None
    evidence_source: str | None = None
    geo_scope: str | None = None
    usability: PlanningMMMCalibrationSignalUsability = (
        PlanningMMMCalibrationSignalUsability.DEFERRED
    )
    calibration_signal_id: str | None = None
    calibration_signal_construction_deferred: bool = True
    data_source_ref: DataSourceRef | None = None
    tabular_source_reference: TabularSourceReference | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMCalibrationSignalMappingIssueCode] = Field(default_factory=list)


class PlanningMMMCalibrationSignalReadinessAssessment(ContractBaseModel):
    """Aggregated calibration readiness assessment."""

    mapped_records: list[PlanningMMMCalibrationSignalMappedRecord] = Field(default_factory=list)
    usable_signal_ids: list[str] = Field(default_factory=list)
    diagnostic_only_signal_ids: list[str] = Field(default_factory=list)
    blocked_signal_ids: list[str] = Field(default_factory=list)
    stale_signal_ids: list[str] = Field(default_factory=list)
    deferred_signal_ids: list[str] = Field(default_factory=list)
    readiness_status: PlanningMMMCalibrationSignalReadinessStatus = (
        PlanningMMMCalibrationSignalReadinessStatus.DEFERRED
    )
    model_calibration_readiness_reference_id: str | None = None
    model_calibration_readiness_deferred: bool = True
    model_calibration_readiness_deferred_reason: str = ""
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMCalibrationSignalMappingIssueCode] = Field(default_factory=list)


class PlanningMMMCalibrationSignalMappingReadinessRequest(ContractBaseModel):
    """Request to evaluate calibration-signal mapping and readiness."""

    request_id: str
    intake_result: PlanningMMMCalibrationSignalTabularIntakeResult | None = None
    target: PlanningMMMCalibrationSignalMappingTarget
    signal_records: list[PlanningMMMCalibrationSignalRecordMetadata] = Field(default_factory=list)
    existing_model_availability_result: MMMExistingModelAvailabilityResult | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


class PlanningMMMCalibrationSignalMappingReadinessResult(ContractBaseModel):
    """Result of calibration-signal mapping and readiness evaluation."""

    request_id: str
    mapping_status: PlanningMMMCalibrationSignalMappingStatus
    readiness_status: PlanningMMMCalibrationSignalReadinessStatus
    assessment: PlanningMMMCalibrationSignalReadinessAssessment
    mapped_records: list[PlanningMMMCalibrationSignalMappedRecord] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMCalibrationSignalMappingIssueCode] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
    execution_allowed: dict[str, bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


FORBIDDEN_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_READINESS_RESULT_FIELD_NAMES = (
    _FORBIDDEN_RESULT_FIELD_NAMES
)
