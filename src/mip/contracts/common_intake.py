"""Common data intake workbench and preliminary profiling contracts (P4c / I6c)."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake import DataGrain, GeoGrain
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import DataSourceMode

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
    "mde result",
    "power is",
    "power result",
    "powered test",
    "treatment assignment",
    "control assignment",
    "effect estimate is",
)


class CommonIntakeStatus(StrEnum):
    """Lifecycle status for the common intake workbench."""

    DRAFT = "draft"
    COLLECTING_SOURCES = "collecting_sources"
    SOURCES_DECLARED = "sources_declared"
    PROFILED = "profiled"
    SUPPORT_ASSESSED = "support_assessed"
    BLOCKED = "blocked"


class IngestionMode(StrEnum):
    """How data entered the common intake workbench."""

    STREAMLIT_FILE_UPLOAD = "streamlit_file_upload"
    CHAT_FILE_UPLOAD = "chat_file_upload"
    LOCAL_FILE_PATH_MANIFEST = "local_file_path_manifest"
    LOCAL_DROPZONE_FOLDER = "local_dropzone_folder"
    GOVERNED_TABLE_REFERENCE = "governed_table_reference"
    WAREHOUSE_CONNECTION = "warehouse_connection"
    SIBLING_REPO_STATIC_EXPORT = "sibling_repo_static_export"
    SAMPLE_DEMO_DATA = "sample_demo_data"


class DataSnapshotStatus(StrEnum):
    """Lifecycle status for a declared data snapshot."""

    DECLARED = "declared"
    SNAPSHOT_RECORDED = "snapshot_recorded"
    PROFILE_AVAILABLE = "profile_available"
    PROFILE_MISSING = "profile_missing"
    BLOCKED = "blocked"


class WorkflowSupportStatus(StrEnum):
    """Structural workflow support assessment status."""

    SUPPORTED = "supported"
    SUPPORTED_WITH_WARNINGS = "supported_with_warnings"
    NEEDS_MORE_DATA = "needs_more_data"
    BLOCKED = "blocked"
    NOT_ASSESSED = "not_assessed"


class WorkflowSupportRoute(StrEnum):
    """Workflow routes the common intake layer may structurally support."""

    NATIONAL_MMM = "national_mmm"
    GEO_LEVEL_MMM = "geo_level_mmm"
    CALIBRATED_MMM = "calibrated_mmm"
    GEOX_DESIGN_DIAGNOSTICS = "geox_design_diagnostics"
    GEOX_READOUT = "geox_readout"
    CALIBRATION_SIGNAL_INTAKE = "calibration_signal_intake"
    DECISION_REVIEW = "decision_review"


class ProfileFindingSeverity(StrEnum):
    """Severity for profile summary findings."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    BLOCKER = "blocker"


def _assert_no_forbidden_claims(*text_fields: str) -> None:
    combined = " ".join(text_fields).lower()
    for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
        if fragment in combined:
            msg = f"common intake contract must not contain forbidden claim: {fragment}"
            raise ValueError(msg)


def _enum_slug(value: object) -> str:
    if isinstance(value, StrEnum):
        return value.value
    return str(value)


class SourceIngestionRecord(ContractBaseModel):
    """Declared ingestion metadata (no actual file I/O)."""

    ingestion_id: str
    source_id: str
    asset_type: DataAssetType
    source_mode: DataSourceMode
    ingestion_mode: IngestionMode
    declared_uri_or_ref: str
    snapshot_id: str | None = None
    ingested_at: datetime
    ingested_by: str | None = None
    status: DataSnapshotStatus = DataSnapshotStatus.DECLARED
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("ingestion_id", "source_id", "declared_uri_or_ref")
    @classmethod
    def required_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "ingestion_id, source_id, and declared_uri_or_ref cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("snapshot_id", "ingested_by")
    @classmethod
    def optional_strings_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "optional ingestion metadata cannot be empty when provided"
            raise ValueError(msg)
        return value


class DataSnapshot(ContractBaseModel):
    """Snapshot metadata only — no raw rows or dataframes."""

    snapshot_id: str
    source_id: str
    asset_type: DataAssetType
    snapshot_status: DataSnapshotStatus = DataSnapshotStatus.SNAPSHOT_RECORDED
    snapshot_version: str = "1.0.0"
    row_count: int | None = None
    column_count: int | None = None
    time_min: datetime | None = None
    time_max: datetime | None = None
    geo_grain: GeoGrain = GeoGrain.UNKNOWN
    time_grain: DataGrain = DataGrain.UNKNOWN
    scope_summary: str | None = None
    checksum_or_version: str | None = None
    contains_sensitive_data: bool = False
    created_at: datetime
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("snapshot_id", "source_id")
    @classmethod
    def snapshot_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "snapshot_id and source_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def metadata_only(self) -> "DataSnapshot":
        forbidden_keys = {"rows", "dataframe", "raw_data", "file_path"}
        if forbidden_keys.intersection(self.model_fields_set):
            msg = "data snapshot must not include raw data fields"
            raise ValueError(msg)
        return self


class MetricAvailabilitySummary(ContractBaseModel):
    """Metric availability from governed profile metadata."""

    summary_id: str
    source_id: str
    metric_ids: list[str] = Field(default_factory=list)
    primary_metric_candidates: list[str] = Field(default_factory=list)
    missing_metric_ids: list[str] = Field(default_factory=list)
    metric_missingness: float | None = None
    metric_sparsity: float | None = None
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("summary_id", "source_id")
    @classmethod
    def summary_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "summary_id and source_id cannot be empty"
            raise ValueError(msg)
        return value


class GeoCoverageSummary(ContractBaseModel):
    """Geo coverage from governed profile metadata."""

    summary_id: str
    source_id: str
    geo_grain: GeoGrain = GeoGrain.UNKNOWN
    geo_count: int | None = None
    missing_geo_count: int | None = None
    geo_values_sample: list[str] = Field(default_factory=list)
    coverage_warnings: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("summary_id", "source_id")
    @classmethod
    def geo_summary_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "summary_id and source_id cannot be empty"
            raise ValueError(msg)
        return value


class TimeCoverageSummary(ContractBaseModel):
    """Time coverage from governed profile metadata."""

    summary_id: str
    source_id: str
    time_grain: DataGrain = DataGrain.UNKNOWN
    period_count: int | None = None
    time_min: datetime | None = None
    time_max: datetime | None = None
    missing_period_count: int | None = None
    pre_period_count: int | None = None
    post_period_count: int | None = None
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("summary_id", "source_id")
    @classmethod
    def time_summary_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "summary_id and source_id cannot be empty"
            raise ValueError(msg)
        return value


class MediaCoverageSummary(ContractBaseModel):
    """Media coverage from governed profile metadata."""

    summary_id: str
    source_id: str
    channels: list[str] = Field(default_factory=list)
    platforms: list[str] = Field(default_factory=list)
    campaigns_sample: list[str] = Field(default_factory=list)
    spend_present: bool = False
    impressions_present: bool = False
    clicks_present: bool = False
    media_missingness: float | None = None
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("summary_id", "source_id")
    @classmethod
    def media_summary_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "summary_id and source_id cannot be empty"
            raise ValueError(msg)
        return value


class ControlCoverageSummary(ContractBaseModel):
    """Control and seasonality coverage from governed profile metadata."""

    summary_id: str
    source_id: str
    control_columns: list[str] = Field(default_factory=list)
    seasonality_present: bool = False
    promo_present: bool = False
    pricing_present: bool = False
    holiday_present: bool = False
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("summary_id", "source_id")
    @classmethod
    def control_summary_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "summary_id and source_id cannot be empty"
            raise ValueError(msg)
        return value


class CommonDataProfileSummary(ContractBaseModel):
    """Governed preliminary profile summary for LLM grounding."""

    profile_id: str
    snapshot_id: str
    source_id: str
    asset_type: DataAssetType
    metric_availability: MetricAvailabilitySummary | None = None
    geo_coverage: GeoCoverageSummary | None = None
    time_coverage: TimeCoverageSummary | None = None
    media_coverage: MediaCoverageSummary | None = None
    control_coverage: ControlCoverageSummary | None = None
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("profile_id", "snapshot_id", "source_id")
    @classmethod
    def profile_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "profile_id, snapshot_id, and source_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def no_forbidden_claims(self) -> "CommonDataProfileSummary":
        text_fields = [
            *(self.warnings or []),
            *(self.blocking_reasons or []),
        ]
        _assert_no_forbidden_claims(*text_fields)
        return self


class WorkflowSupportAssessment(ContractBaseModel):
    """Structural workflow support assessment (not feasibility certification)."""

    assessment_id: str
    session_id: str
    recommendation_id: str
    plan_id: str
    manifest_id: str
    profile_ids: list[str] = Field(default_factory=list)
    supported_routes: list[WorkflowSupportRoute] = Field(default_factory=list)
    blocked_routes: list[WorkflowSupportRoute] = Field(default_factory=list)
    support_status: WorkflowSupportStatus = WorkflowSupportStatus.NOT_ASSESSED
    route_reasons: list[str] = Field(default_factory=list)
    missing_data_requirements: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    allowed_next_steps: list[str] = Field(default_factory=list)
    blocked_next_steps: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator(
        "assessment_id",
        "session_id",
        "recommendation_id",
        "plan_id",
        "manifest_id",
    )
    @classmethod
    def assessment_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "assessment identifiers cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def assessment_rules(self) -> "WorkflowSupportAssessment":
        supported_slugs = {_enum_slug(route) for route in self.supported_routes}
        blocked_slugs = {_enum_slug(route) for route in self.blocked_routes}
        overlap = supported_slugs.intersection(blocked_slugs)
        if overlap:
            msg = (
                "supported_routes and blocked_routes must be disjoint; "
                f"overlap: {sorted(overlap)}"
            )
            raise ValueError(msg)
        if self.support_status == WorkflowSupportStatus.BLOCKED and not self.blocking_reasons:
            msg = "blocked workflow support assessment requires blocking_reasons"
            raise ValueError(msg)
        _assert_no_forbidden_claims(
            *(self.route_reasons or []),
            *(self.warnings or []),
            *(self.blocking_reasons or []),
            *(self.allowed_next_steps or []),
        )
        return self


class LLMAnswerGroundingContext(ContractBaseModel):
    """Governed sources the LLM may use for data-grounded answers."""

    context_id: str
    session_id: str
    allowed_sources: list[str] = Field(default_factory=list)
    profile_summaries: list[str] = Field(default_factory=list)
    workflow_support_assessment: str | None = None
    readiness_report_ids: list[str] = Field(default_factory=list)
    diagnostic_report_ids: list[str] = Field(default_factory=list)
    trust_report_ids: list[str] = Field(default_factory=list)
    allowed_answer_topics: list[str] = Field(default_factory=list)
    blocked_answer_topics: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("context_id", "session_id")
    @classmethod
    def context_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "context_id and session_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def grounding_rules(self) -> "LLMAnswerGroundingContext":
        _assert_no_forbidden_claims(
            *(self.warnings or []),
            *(self.blocking_reasons or []),
            *(self.allowed_answer_topics or []),
        )
        return self


class CommonIntakeWorkbench(ContractBaseModel):
    """Shared intake workbench for MMM, GeoX, CalibrationSignal, and decision-review."""

    workbench_id: str
    session_id: str
    recommendation_id: str
    plan_id: str
    manifest_id: str
    ingestion_records: list[SourceIngestionRecord] = Field(default_factory=list)
    snapshots: list[DataSnapshot] = Field(default_factory=list)
    profile_summaries: list[CommonDataProfileSummary] = Field(default_factory=list)
    workflow_support_assessment: WorkflowSupportAssessment | None = None
    llm_grounding_context: LLMAnswerGroundingContext | None = None
    status: CommonIntakeStatus = CommonIntakeStatus.DRAFT
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator(
        "workbench_id",
        "session_id",
        "recommendation_id",
        "plan_id",
        "manifest_id",
    )
    @classmethod
    def workbench_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "workbench identifiers cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def workbench_rules(self) -> "CommonIntakeWorkbench":
        if self.status == CommonIntakeStatus.BLOCKED and not self.blocking_reasons:
            msg = "blocked workbench requires blocking_reasons"
            raise ValueError(msg)
        _assert_no_forbidden_claims(
            *(self.warnings or []),
            *(self.blocking_reasons or []),
        )
        return self
