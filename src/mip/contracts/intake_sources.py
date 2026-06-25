"""Data source reference and intake manifest contracts (P3 / I5)."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake import (
    DataGrain,
    GeoGrain,
    IntakeCandidatePath,
    IntakeIntendedUse,
)
from mip.contracts.intake_assets import DataAssetType

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "roi is",
    "lift estimate",
    "lift is",
    "budget allocation",
    "coefficient",
    "causal effect",
    "production-ready",
)


class DataSourceMode(StrEnum):
    """How the user or system declares a data source."""

    STREAMLIT_FILE_UPLOAD = "streamlit_file_upload"
    CHAT_FILE_UPLOAD = "chat_file_upload"
    LOCAL_DROPZONE_FOLDER = "local_dropzone_folder"
    LOCAL_FILE_PATH_MANIFEST = "local_file_path_manifest"
    GOVERNED_TABLE_REFERENCE = "governed_table_reference"
    WAREHOUSE_CONNECTION = "warehouse_connection"
    SIBLING_REPO_STATIC_EXPORT = "sibling_repo_static_export"
    SAMPLE_DEMO_DATA = "sample_demo_data"


class DataSourceType(StrEnum):
    """Structural category for a declared data source."""

    FILE = "file"
    TABLE = "table"
    FOLDER = "folder"
    CONNECTION = "connection"
    REGISTRY_RECORD = "registry_record"
    SIBLING_EXPORT = "sibling_export"
    DEMO_FIXTURE = "demo_fixture"


class DataSourceStatus(StrEnum):
    """Lifecycle status for a declared data source reference."""

    DRAFT = "draft"
    DECLARED = "declared"
    NEEDS_CONFIRMATION = "needs_confirmation"
    READY_FOR_VALIDATION = "ready_for_validation"
    BLOCKED = "blocked"


class IntakeManifestStatus(StrEnum):
    """Lifecycle status for an intake manifest."""

    DRAFT = "draft"
    NEEDS_DATA_SOURCES = "needs_data_sources"
    READY_FOR_VALIDATION = "ready_for_validation"
    BLOCKED = "blocked"


def _enum_slug(value: object) -> str:
    if isinstance(value, StrEnum):
        return value.value
    return str(value)


class DataSourceRef(ContractBaseModel):
    """Declared source for a required intake data asset (no I/O)."""

    source_id: str
    source_mode: DataSourceMode
    source_type: DataSourceType
    asset_type: DataAssetType
    uri_or_table_ref: str
    schema_version: str | None = None
    declared_owner: str | None = None
    declared_grain: DataGrain = DataGrain.UNKNOWN
    declared_geo_grain: GeoGrain = GeoGrain.UNKNOWN
    declared_scope: dict[str, str] = Field(default_factory=dict)
    created_at: datetime
    data_snapshot_id: str | None = None
    checksum_or_version: str | None = None
    read_only: bool = True
    contains_sensitive_data: bool = False
    status: DataSourceStatus = DataSourceStatus.DECLARED
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("source_id", "uri_or_table_ref")
    @classmethod
    def required_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "source_id and uri_or_table_ref cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator(
        "schema_version",
        "declared_owner",
        "data_snapshot_id",
        "checksum_or_version",
    )
    @classmethod
    def optional_strings_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "optional source metadata fields cannot be empty when provided"
            raise ValueError(msg)
        return value


class TableSourceRef(DataSourceRef):
    """Governed table or warehouse connection reference."""

    @model_validator(mode="after")
    def validate_table_source(self) -> "TableSourceRef":
        allowed_modes = {
            _enum_slug(DataSourceMode.GOVERNED_TABLE_REFERENCE),
            _enum_slug(DataSourceMode.WAREHOUSE_CONNECTION),
        }
        allowed_types = {
            _enum_slug(DataSourceType.TABLE),
            _enum_slug(DataSourceType.CONNECTION),
            _enum_slug(DataSourceType.REGISTRY_RECORD),
        }
        if _enum_slug(self.source_mode) not in allowed_modes:
            msg = "table source ref requires governed_table_reference or warehouse_connection mode"
            raise ValueError(msg)
        if _enum_slug(self.source_type) not in allowed_types:
            msg = "table source ref requires table, connection, or registry_record source_type"
            raise ValueError(msg)
        return self


class FileSourceRef(DataSourceRef):
    """Local file path manifest reference."""

    @model_validator(mode="after")
    def validate_file_source(self) -> "FileSourceRef":
        if _enum_slug(self.source_mode) != _enum_slug(DataSourceMode.LOCAL_FILE_PATH_MANIFEST):
            msg = "file source ref requires local_file_path_manifest mode"
            raise ValueError(msg)
        if _enum_slug(self.source_type) != _enum_slug(DataSourceType.FILE):
            msg = "file source ref requires file source_type"
            raise ValueError(msg)
        return self


class DropzoneSourceRef(DataSourceRef):
    """Local drop-zone folder reference."""

    @model_validator(mode="after")
    def validate_dropzone_source(self) -> "DropzoneSourceRef":
        if _enum_slug(self.source_mode) != _enum_slug(DataSourceMode.LOCAL_DROPZONE_FOLDER):
            msg = "dropzone source ref requires local_dropzone_folder mode"
            raise ValueError(msg)
        if _enum_slug(self.source_type) != _enum_slug(DataSourceType.FOLDER):
            msg = "dropzone source ref requires folder source_type"
            raise ValueError(msg)
        return self


class UploadedFileSourceRef(DataSourceRef):
    """Uploaded file reference from Streamlit or chat intake."""

    @model_validator(mode="after")
    def validate_uploaded_file_source(self) -> "UploadedFileSourceRef":
        allowed_modes = {
            _enum_slug(DataSourceMode.STREAMLIT_FILE_UPLOAD),
            _enum_slug(DataSourceMode.CHAT_FILE_UPLOAD),
        }
        if _enum_slug(self.source_mode) not in allowed_modes:
            msg = "uploaded file source ref requires streamlit_file_upload or chat_file_upload mode"
            raise ValueError(msg)
        if _enum_slug(self.source_type) != _enum_slug(DataSourceType.FILE):
            msg = "uploaded file source ref requires file source_type"
            raise ValueError(msg)
        return self


class SiblingExportSourceRef(DataSourceRef):
    """Sibling repository static export reference."""

    @model_validator(mode="after")
    def validate_sibling_export_source(self) -> "SiblingExportSourceRef":
        if _enum_slug(self.source_mode) != _enum_slug(DataSourceMode.SIBLING_REPO_STATIC_EXPORT):
            msg = "sibling export source ref requires sibling_repo_static_export mode"
            raise ValueError(msg)
        if _enum_slug(self.source_type) != _enum_slug(DataSourceType.SIBLING_EXPORT):
            msg = "sibling export source ref requires sibling_export source_type"
            raise ValueError(msg)
        return self


class MMMIntakeManifest(ContractBaseModel):
    """Reproducible MMM intake manifest tying session, plan, and data sources."""

    manifest_id: str
    session_id: str
    recommendation_id: str
    plan_id: str
    business_question: str
    intended_use: IntakeIntendedUse
    recommended_path: IntakeCandidatePath
    metric_id: str | None = None
    estimand_id: str | None = None
    time_grain: DataGrain = DataGrain.UNKNOWN
    geo_grain: GeoGrain = GeoGrain.UNKNOWN
    reporting_window_start: datetime | None = None
    reporting_window_end: datetime | None = None
    outcome_source: DataSourceRef | None = None
    media_sources: list[DataSourceRef] = Field(default_factory=list)
    control_sources: list[DataSourceRef] = Field(default_factory=list)
    mapping_sources: list[DataSourceRef] = Field(default_factory=list)
    calibration_signal_sources: list[DataSourceRef] = Field(default_factory=list)
    experiment_export_sources: list[DataSourceRef] = Field(default_factory=list)
    created_by: str | None = None
    created_at: datetime
    manifest_version: str = "1.0.0"
    approval_status: str = "draft"
    status: IntakeManifestStatus = IntakeManifestStatus.DRAFT
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator(
        "manifest_id",
        "session_id",
        "recommendation_id",
        "plan_id",
        "business_question",
    )
    @classmethod
    def manifest_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "manifest identifiers and business_question cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def manifest_rules(self) -> "MMMIntakeManifest":
        return self._assert_no_forbidden_claims()

    def _assert_no_forbidden_claims(self) -> "MMMIntakeManifest":
        text_fields = [
            self.business_question,
            *self.warnings,
            *self.blocking_reasons,
        ]
        for source in (
            *([self.outcome_source] if self.outcome_source else []),
            *self.media_sources,
            *self.control_sources,
            *self.mapping_sources,
            *self.calibration_signal_sources,
            *self.experiment_export_sources,
        ):
            text_fields.extend(source.warnings)
            text_fields.extend(source.blocking_reasons)
        combined = " ".join(text_fields).lower()
        for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
            if fragment in combined:
                msg = f"manifest must not contain forbidden claim fragment: {fragment}"
                raise ValueError(msg)
        return self


class GeoXIntakeManifest(ContractBaseModel):
    """Reproducible GeoX intake manifest tying session, plan, and data sources."""

    manifest_id: str
    session_id: str
    recommendation_id: str
    plan_id: str
    business_question: str
    intended_use: IntakeIntendedUse
    recommended_path: IntakeCandidatePath
    metric_id: str | None = None
    estimand_id: str | None = None
    time_grain: DataGrain = DataGrain.UNKNOWN
    geo_grain: GeoGrain = GeoGrain.UNKNOWN
    reporting_window_start: datetime | None = None
    reporting_window_end: datetime | None = None
    outcome_source: DataSourceRef | None = None
    geo_mapping_source: DataSourceRef | None = None
    media_sources: list[DataSourceRef] = Field(default_factory=list)
    experiment_export_sources: list[DataSourceRef] = Field(default_factory=list)
    created_by: str | None = None
    created_at: datetime
    manifest_version: str = "1.0.0"
    approval_status: str = "draft"
    status: IntakeManifestStatus = IntakeManifestStatus.DRAFT
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator(
        "manifest_id",
        "session_id",
        "recommendation_id",
        "plan_id",
        "business_question",
    )
    @classmethod
    def manifest_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "manifest identifiers and business_question cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def manifest_rules(self) -> "GeoXIntakeManifest":
        return self._assert_no_forbidden_claims()

    def _assert_no_forbidden_claims(self) -> "GeoXIntakeManifest":
        text_fields = [
            self.business_question,
            *self.warnings,
            *self.blocking_reasons,
        ]
        for source in (
            *([self.outcome_source] if self.outcome_source else []),
            *([self.geo_mapping_source] if self.geo_mapping_source else []),
            *self.media_sources,
            *self.experiment_export_sources,
        ):
            text_fields.extend(source.warnings)
            text_fields.extend(source.blocking_reasons)
        combined = " ".join(text_fields).lower()
        for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
            if fragment in combined:
                msg = f"manifest must not contain forbidden claim fragment: {fragment}"
                raise ValueError(msg)
        return self
