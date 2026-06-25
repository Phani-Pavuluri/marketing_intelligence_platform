"""Local/demo tabular profiling contracts (P8)."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.common_intake import ProfileFindingSeverity, WorkflowSupportRoute

MAX_DEMO_PROFILE_ROWS = 5000
MAX_DEMO_COLUMN_SAMPLE_VALUES = 5

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "roi is",
    "lift estimate",
    "expected lift",
    "optimal mix",
    "budget recommendation",
    "causal effect is",
    "matched markets",
    "mde result",
    "power result",
)


class DemoProfileStatus(StrEnum):
    """Status for a local/demo dataset profile."""

    CREATED = "created"
    PROFILED = "profiled"
    NEEDS_MAPPING = "needs_mapping"
    UNSUPPORTED = "unsupported"
    BLOCKED = "blocked"


class DemoDatasetKind(StrEnum):
    """Known demo dataset categories."""

    WEBSITE_TRAFFIC = "website_traffic"
    MEDIA_SPEND = "media_spend"
    GEO_OUTCOME = "geo_outcome"
    EXPERIMENT_READOUT = "experiment_readout"
    BUSINESS_PROFILE = "business_profile"
    UNKNOWN = "unknown"


class DemoColumnSemanticRole(StrEnum):
    """Inferred semantic role for a demo dataset column."""

    DATE = "date"
    GEO = "geo"
    CHANNEL = "channel"
    SOURCE = "source"
    MEDIUM = "medium"
    CAMPAIGN = "campaign"
    LANDING_PAGE = "landing_page"
    DEVICE = "device"
    SESSIONS = "sessions"
    ENGAGED_SESSIONS = "engaged_sessions"
    CONVERSIONS = "conversions"
    REVENUE = "revenue"
    SPEND = "spend"
    IMPRESSIONS = "impressions"
    CLICKS = "clicks"
    OUTCOME = "outcome"
    EFFECT_ESTIMATE = "effect_estimate"
    STANDARD_ERROR = "standard_error"
    CONFIDENCE_INTERVAL_LOW = "confidence_interval_low"
    CONFIDENCE_INTERVAL_HIGH = "confidence_interval_high"
    METRIC = "metric"
    ESTIMAND = "estimand"
    UNKNOWN = "unknown"


def _assert_no_forbidden_claims(*text_fields: str) -> None:
    combined = " ".join(text_fields).lower()
    for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
        if fragment in combined:
            msg = f"demo profile contract must not contain forbidden claim: {fragment}"
            raise ValueError(msg)


def _collect_text(*groups: list[str] | None) -> list[str]:
    collected: list[str] = []
    for group in groups:
        if group:
            collected.extend(group)
    return collected


class DemoColumnProfile(ContractBaseModel):
    """Governed column summary for demo profiling (no raw column dumps)."""

    column_name: str
    semantic_role: DemoColumnSemanticRole = DemoColumnSemanticRole.UNKNOWN
    dtype_summary: str = "unknown"
    non_null_count: int = 0
    null_count: int = 0
    distinct_count: int = 0
    sample_values: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("column_name")
    @classmethod
    def column_name_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "column_name cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def column_profile_rules(self) -> "DemoColumnProfile":
        if len(self.sample_values) > MAX_DEMO_COLUMN_SAMPLE_VALUES:
            msg = f"sample_values capped at {MAX_DEMO_COLUMN_SAMPLE_VALUES}"
            raise ValueError(msg)
        _assert_no_forbidden_claims(
            self.column_name,
            self.dtype_summary,
            *_collect_text(self.sample_values, self.warnings, self.blocking_reasons),
        )
        return self


class DemoDatasetProfile(ContractBaseModel):
    """Summary-only demo dataset profile (no raw rows stored)."""

    profile_id: str
    dataset_kind: DemoDatasetKind = DemoDatasetKind.UNKNOWN
    status: DemoProfileStatus = DemoProfileStatus.CREATED
    row_count: int = 0
    column_count: int = 0
    columns: list[DemoColumnProfile] = Field(default_factory=list)
    detected_time_coverage: str | None = None
    detected_geo_coverage: str | None = None
    detected_channels: list[str] = Field(default_factory=list)
    detected_sources: list[str] = Field(default_factory=list)
    detected_metrics: list[str] = Field(default_factory=list)
    has_outcome_data: bool = False
    has_media_data: bool = False
    has_geo_data: bool = False
    has_time_data: bool = False
    has_uncertainty_data: bool = False
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("profile_id")
    @classmethod
    def profile_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "profile_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def dataset_profile_rules(self) -> "DemoDatasetProfile":
        if self.row_count > MAX_DEMO_PROFILE_ROWS:
            msg = f"row_count exceeds demo cap of {MAX_DEMO_PROFILE_ROWS}"
            raise ValueError(msg)
        _assert_no_forbidden_claims(
            self.detected_time_coverage or "",
            self.detected_geo_coverage or "",
            *_collect_text(
                self.detected_channels,
                self.detected_sources,
                self.detected_metrics,
                self.warnings,
                self.blocking_reasons,
            ),
        )
        return self


class DemoProfileToWorkflowSummary(ContractBaseModel):
    """Links a demo profile to governed workflow object identifiers."""

    summary_id: str
    profile_id: str
    dataset_kind: DemoDatasetKind
    common_profile_summary_id: str | None = None
    traffic_profile_id: str | None = None
    calibration_evidence_input_id: str | None = None
    supported_workflow_routes: list[WorkflowSupportRoute] = Field(default_factory=list)
    blocked_workflow_routes: list[WorkflowSupportRoute] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("summary_id", "profile_id")
    @classmethod
    def summary_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "summary identifiers cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def workflow_summary_rules(self) -> "DemoProfileToWorkflowSummary":
        _assert_no_forbidden_claims(
            *_collect_text(self.warnings, self.blocking_reasons),
        )
        return self


# Re-export for callers that reference demo finding severity.
DemoProfileFindingSeverity = ProfileFindingSeverity
