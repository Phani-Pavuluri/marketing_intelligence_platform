"""Shared uploaded CSV materialization contracts (lane-neutral)."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from mip.contracts.base import ContractBaseModel

_MATERIALIZED_MODEL_CONFIG = ConfigDict(
    extra="forbid",
    validate_assignment=True,
    use_enum_values=True,
    str_strip_whitespace=True,
    arbitrary_types_allowed=True,
)

DEFAULT_MAX_UPLOAD_FILE_SIZE_BYTES = 25 * 1024 * 1024
DEFAULT_MAX_UPLOAD_ROWS = 250_000
ALLOWED_FILE_EXTENSIONS = (".csv",)

RECOMMENDED_NEXT_GEOX_UPLOADED_CSV_ADAPTER_ARTIFACT = (
    "MIP_GEOX_READOUT_UPLOADED_CSV_ADAPTER_001"
)
RECOMMENDED_NEXT_PLANNING_UPLOADED_CSV_ADAPTER_ARTIFACT = (
    "MIP_PLANNING_MMM_UPLOADED_CSV_ADAPTER_001"
)


class UploadedCSVSourceType(StrEnum):
    """Allowed uploaded CSV source types for shared materialization."""

    UPLOADED_CSV = "uploaded_csv"
    LOCAL_UPLOADED_CSV = "local_uploaded_csv"


class UploadedCSVMaterializationStatus(StrEnum):
    """Outcome of shared uploaded CSV materialization."""

    MATERIALIZED = "materialized"
    MATERIALIZED_WITH_WARNINGS = "materialized_with_warnings"
    BLOCKED_MISSING_UPLOAD = "blocked_missing_upload"
    BLOCKED_UNSUPPORTED_FILE_TYPE = "blocked_unsupported_file_type"
    BLOCKED_FILE_TOO_LARGE = "blocked_file_too_large"
    BLOCKED_ROW_LIMIT_EXCEEDED = "blocked_row_limit_exceeded"
    BLOCKED_EMPTY_FILE = "blocked_empty_file"
    BLOCKED_HEADER_ONLY_FILE = "blocked_header_only_file"
    BLOCKED_MALFORMED_CSV = "blocked_malformed_csv"
    BLOCKED_MISSING_REQUIRED_COLUMNS = "blocked_missing_required_columns"
    BLOCKED_UNSUPPORTED_SOURCE_TYPE = "blocked_unsupported_source_type"


class UploadedCSVIssueCode(StrEnum):
    """Typed shared uploaded CSV materialization issue codes."""

    MISSING_UPLOAD = "missing_upload"
    UNSUPPORTED_FILE_TYPE = "unsupported_file_type"
    FILE_TOO_LARGE = "file_too_large"
    ROW_LIMIT_EXCEEDED = "row_limit_exceeded"
    EMPTY_FILE = "empty_file"
    HEADER_ONLY_FILE = "header_only_file"
    MALFORMED_CSV = "malformed_csv"
    MISSING_REQUIRED_COLUMNS = "missing_required_columns"
    UNSUPPORTED_SOURCE_TYPE = "unsupported_source_type"
    COLUMN_NAME_NORMALIZED = "column_name_normalized"
    DUPLICATE_COLUMN_NAME = "duplicate_column_name"
    LINEAGE_RECORDED = "lineage_recorded"
    DATAFRAME_MATERIALIZED = "dataframe_materialized"
    REQUIRED_COLUMNS_VALIDATED = "required_columns_validated"


class UploadedCSVPolicy(StrEnum):
    """Shared uploaded CSV materialization policy mode."""

    STRICT_UPLOADED_CSV_ONLY = "strict_uploaded_csv_only"
    STRICT_LOCAL_TEST_ONLY = "strict_local_test_only"


class UploadedCSVSource(ContractBaseModel):
    """Declared uploaded CSV source for shared materialization."""

    source_id: str
    source_type: UploadedCSVSourceType = UploadedCSVSourceType.UPLOADED_CSV
    path: str
    original_filename: str
    declared_role_hint: str | None = None
    declared_columns: list[str] = Field(default_factory=list)
    required_columns: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class UploadedCSVInspection(ContractBaseModel):
    """Header/shape inspection for one uploaded CSV."""

    source_id: str
    source_type: UploadedCSVSourceType
    original_filename: str
    declared_role_hint: str | None = None
    columns: list[str] = Field(default_factory=list)
    normalized_columns: list[str] = Field(default_factory=list)
    row_count: int = 0
    column_count: int = 0
    file_size_bytes: int = 0
    issues: list[UploadedCSVIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class MaterializedTabularDataset(BaseModel):
    """Materialized tabular dataset from an uploaded CSV."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    dataset_id: str
    source_id: str
    source_type: UploadedCSVSourceType
    declared_role_hint: str | None = None
    dataframe: Any
    columns: list[str] = Field(default_factory=list)
    normalized_columns: list[str] = Field(default_factory=list)
    row_count: int = 0
    column_count: int = 0
    lineage: dict[str, str] = Field(default_factory=dict)


class UploadedCSVMaterializationRequest(ContractBaseModel):
    """Batch shared uploaded CSV materialization request."""

    request_id: str
    sources: list[UploadedCSVSource] = Field(default_factory=list)
    policy: UploadedCSVPolicy = UploadedCSVPolicy.STRICT_UPLOADED_CSV_ONLY
    max_file_size_bytes: int = DEFAULT_MAX_UPLOAD_FILE_SIZE_BYTES
    max_rows: int = DEFAULT_MAX_UPLOAD_ROWS
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class UploadedCSVMaterializationResult(BaseModel):
    """Shared uploaded CSV materialization result."""

    model_config = _MATERIALIZED_MODEL_CONFIG

    request_id: str
    status: UploadedCSVMaterializationStatus
    datasets: list[MaterializedTabularDataset] = Field(default_factory=list)
    inspections: list[UploadedCSVInspection] = Field(default_factory=list)
    issues: list[UploadedCSVIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
