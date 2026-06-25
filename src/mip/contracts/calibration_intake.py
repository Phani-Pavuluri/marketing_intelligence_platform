"""CalibrationSignal intake mapping contracts (P6 / I9)."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.calibration import CalibrationSignal

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "roi is",
    "budget allocation",
    "budget recommendation",
    "model refresh",
    "mmm calibration executed",
    "causal effect is proven",
    "decision recommendation",
    "production-ready",
    "optimizer",
)


class CalibrationIntakeStatus(StrEnum):
    """Status of CalibrationSignal intake mapping."""

    DRAFT = "draft"
    READY_FOR_MAPPING = "ready_for_mapping"
    MAPPED = "mapped"
    NEEDS_MORE_DATA = "needs_more_data"
    BLOCKED = "blocked"
    INCOMPATIBLE = "incompatible"


class CalibrationIntakeBlockingReason(StrEnum):
    """Structured blocking reason for calibration intake mapping."""

    MISSING_EFFECT_ESTIMATE = "missing_effect_estimate"
    MISSING_UNCERTAINTY = "missing_uncertainty"
    MISSING_METRIC_MAPPING = "missing_metric_mapping"
    MISSING_ESTIMAND_MAPPING = "missing_estimand_mapping"
    MISSING_CHANNEL_MAPPING = "missing_channel_mapping"
    MISSING_GEO_SCOPE = "missing_geo_scope"
    MISSING_TIME_WINDOW = "missing_time_window"
    INCOMPATIBLE_METRIC = "incompatible_metric"
    INCOMPATIBLE_ESTIMAND = "incompatible_estimand"
    INCOMPATIBLE_SCALE = "incompatible_scale"
    UNSUPPORTED_EVIDENCE_TYPE = "unsupported_evidence_type"
    STALE_EVIDENCE = "stale_evidence"
    NOT_CAUSAL_EVIDENCE = "not_causal_evidence"
    TRUST_REPORT_REQUIRED = "trust_report_required"


_FORBIDDEN_RESULT_FIELD_NAMES = frozenset(
    {
        "roi_estimate",
        "budget_recommendation",
        "lift_estimate",
        "expected_lift",
        "causal_certification",
        "model_refresh_result",
        "optimizer_result",
    }
)


def _assert_no_forbidden_claims(*text_fields: str) -> None:
    combined = " ".join(text_fields).lower()
    for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
        if fragment in combined:
            msg = f"calibration intake contract must not contain forbidden claim: {fragment}"
            raise ValueError(msg)


def _collect_text(*groups: list[str] | None) -> list[str]:
    collected: list[str] = []
    for group in groups:
        if group:
            collected.extend(group)
    return collected


class CalibrationEvidenceInput(ContractBaseModel):
    """Governed experiment evidence fields for CalibrationSignal mapping."""

    input_id: str
    source_artifact_id: str | None = None
    source_experiment_id: str | None = None
    source_readout_id: str | None = None
    source_trust_report_id: str | None = None
    metric_id: str | None = None
    estimand_id: str | None = None
    channel: str | None = None
    platform: str | None = None
    product_scope: str | None = None
    geo_scope: str | None = None
    time_window_start: datetime | None = None
    time_window_end: datetime | None = None
    effect_estimate: float | None = None
    standard_error: float | None = None
    confidence_interval_low: float | None = None
    confidence_interval_high: float | None = None
    lift_scale: str | None = None
    evidence_type: str | None = None
    is_causal: bool = False
    freshness_status: str = "unknown"
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("input_id")
    @classmethod
    def input_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "input_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def evidence_input_rules(self) -> "CalibrationEvidenceInput":
        if (
            self.time_window_start is not None
            and self.time_window_end is not None
            and self.time_window_end <= self.time_window_start
        ):
            msg = "time_window_end must be after time_window_start"
            raise ValueError(msg)
        if (
            self.confidence_interval_low is not None
            and self.confidence_interval_high is not None
            and self.confidence_interval_low > self.confidence_interval_high
        ):
            msg = "confidence interval lower bound must be <= upper bound"
            raise ValueError(msg)
        _assert_no_forbidden_claims(
            *_collect_text(self.warnings, self.blocking_reasons),
            self.evidence_type or "",
        )
        return self


class CalibrationMappingRequirement(ContractBaseModel):
    """Target MMM/calibration context expected before evidence can be mapped."""

    requirement_id: str
    target_model_id: str
    required_metric_id: str | None = None
    required_estimand_id: str | None = None
    required_channel: str | None = None
    required_platform: str | None = None
    required_product_scope: str | None = None
    required_geo_scope: str | None = None
    required_time_window_start: datetime | None = None
    required_time_window_end: datetime | None = None
    required_lift_scale: str | None = None
    allow_stale_evidence: bool = False
    require_causal_flag: bool = False
    require_trust_report: bool = False
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("requirement_id", "target_model_id")
    @classmethod
    def requirement_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "requirement identifiers cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def requirement_rules(self) -> "CalibrationMappingRequirement":
        _assert_no_forbidden_claims(*_collect_text(self.warnings, self.blocking_reasons))
        return self


class CalibrationMappingReport(ContractBaseModel):
    """Validation and mapping outcome for CalibrationSignal intake."""

    report_id: str
    input_id: str
    requirement_id: str | None = None
    status: CalibrationIntakeStatus = CalibrationIntakeStatus.DRAFT
    mapped_signal_id: str | None = None
    mapped_signal: CalibrationSignal | None = None
    alignment_passed: bool = False
    missing_fields: list[str] = Field(default_factory=list)
    incompatible_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    allowed_next_steps: list[str] = Field(default_factory=list)
    blocked_next_steps: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("report_id", "input_id")
    @classmethod
    def report_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "report identifiers cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def mapping_report_rules(self) -> "CalibrationMappingReport":
        if self.status == CalibrationIntakeStatus.MAPPED and not self.mapped_signal_id:
            msg = "mapped status requires mapped_signal_id"
            raise ValueError(msg)
        if self.status in {
            CalibrationIntakeStatus.BLOCKED,
            CalibrationIntakeStatus.INCOMPATIBLE,
        } and not self.blocking_reasons:
            msg = "blocked or incompatible mapping report requires blocking_reasons"
            raise ValueError(msg)
        text_fields = _collect_text(
            self.warnings,
            self.blocking_reasons,
            self.missing_fields,
            self.incompatible_fields,
            self.allowed_next_steps,
            self.blocked_next_steps,
        )
        _assert_no_forbidden_claims(*text_fields)
        return self


FORBIDDEN_CALIBRATION_INTAKE_RESULT_FIELD_NAMES = _FORBIDDEN_RESULT_FIELD_NAMES
