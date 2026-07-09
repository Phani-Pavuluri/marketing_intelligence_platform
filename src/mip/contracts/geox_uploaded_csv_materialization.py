"""GeoX uploaded CSV materialization contracts (narrow local uploads only)."""

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
ALLOWED_UPLOADED_SOURCE_TYPES = ("uploaded_csv", "local_uploaded_csv")
ALLOWED_FILE_EXTENSIONS = (".csv",)

RECOMMENDED_NEXT_UPLOADED_CSV_RUNTIME_BRIDGE_ARTIFACT = (
    "MIP_GEOX_READOUT_UPLOADED_CSV_RUNTIME_BRIDGE_001"
)


class GeoXUploadedCSVRole(StrEnum):
    """Explicit role for an uploaded GeoX readout CSV."""

    KPI_PANEL = "kpi_panel"
    SPEND_PANEL = "spend_panel"
    ASSIGNMENT_TABLE = "assignment_table"
    EXPERIMENT_METADATA = "experiment_metadata"
    UNKNOWN = "unknown"


class GeoXUploadedCSVMaterializationStatus(StrEnum):
    """Outcome of uploaded CSV materialization."""

    MATERIALIZED = "materialized"
    MATERIALIZED_WITH_WARNINGS = "materialized_with_warnings"
    BLOCKED_MISSING_UPLOAD = "blocked_missing_upload"
    BLOCKED_UNSUPPORTED_FILE_TYPE = "blocked_unsupported_file_type"
    BLOCKED_FILE_TOO_LARGE = "blocked_file_too_large"
    BLOCKED_ROW_LIMIT_EXCEEDED = "blocked_row_limit_exceeded"
    BLOCKED_EMPTY_FILE = "blocked_empty_file"
    BLOCKED_MALFORMED_CSV = "blocked_malformed_csv"
    BLOCKED_MISSING_REQUIRED_COLUMNS = "blocked_missing_required_columns"
    BLOCKED_AMBIGUOUS_ROLE = "blocked_ambiguous_role"
    BLOCKED_UNSUPPORTED_SOURCE_TYPE = "blocked_unsupported_source_type"


class GeoXUploadedCSVIssueCode(StrEnum):
    """Typed uploaded CSV materialization issue codes."""

    MISSING_UPLOAD = "missing_upload"
    UNSUPPORTED_FILE_TYPE = "unsupported_file_type"
    FILE_TOO_LARGE = "file_too_large"
    ROW_LIMIT_EXCEEDED = "row_limit_exceeded"
    EMPTY_FILE = "empty_file"
    MALFORMED_CSV = "malformed_csv"
    MISSING_REQUIRED_COLUMNS = "missing_required_columns"
    AMBIGUOUS_ROLE = "ambiguous_role"
    UNSUPPORTED_SOURCE_TYPE = "unsupported_source_type"
    DUPLICATE_ROLE = "duplicate_role"
    HEADER_ONLY_FILE = "header_only_file"
    COLUMN_NAME_NORMALIZED = "column_name_normalized"
    OPTIONAL_METADATA_MISSING = "optional_metadata_missing"
    LINEAGE_RECORDED = "lineage_recorded"


class GeoXUploadedCSVPolicy(StrEnum):
    """Uploaded CSV materialization policy mode."""

    STRICT_LOCAL_TEST_ONLY = "strict_local_test_only"
    STRICT_UPLOADED_CSV_ONLY = "strict_uploaded_csv_only"


class GeoXUploadedCSVSource(ContractBaseModel):
    """Declared uploaded CSV source — local/dev paths only."""

    source_id: str
    role: GeoXUploadedCSVRole
    path: str
    original_filename: str
    source_type: str = "uploaded_csv"
    declared_columns: list[str] = Field(default_factory=list)
    required_columns: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class GeoXUploadedCSVInspection(ContractBaseModel):
    """Header/shape inspection for one uploaded CSV."""

    source_id: str
    role: GeoXUploadedCSVRole
    columns: list[str] = Field(default_factory=list)
    row_count: int = 0
    column_count: int = 0
    file_size_bytes: int = 0
    issues: list[GeoXUploadedCSVIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class GeoXUploadedCSVDataset(BaseModel):
    """Materialized uploaded CSV dataset for local/test paths only."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    source_id: str
    role: GeoXUploadedCSVRole
    dataframe: Any
    columns: list[str] = Field(default_factory=list)
    row_count: int = 0
    column_count: int = 0
    lineage: dict[str, str] = Field(default_factory=dict)


class GeoXUploadedCSVMaterializationRequest(ContractBaseModel):
    """Batch uploaded CSV materialization request."""

    request_id: str
    sources: list[GeoXUploadedCSVSource] = Field(default_factory=list)
    policy: GeoXUploadedCSVPolicy = GeoXUploadedCSVPolicy.STRICT_UPLOADED_CSV_ONLY
    max_file_size_bytes: int = DEFAULT_MAX_UPLOAD_FILE_SIZE_BYTES
    max_rows: int = DEFAULT_MAX_UPLOAD_ROWS
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXUploadedCSVMaterializationResult(BaseModel):
    """Uploaded CSV materialization result — may include in-memory dataframes."""

    model_config = _MATERIALIZED_MODEL_CONFIG

    request_id: str
    status: GeoXUploadedCSVMaterializationStatus
    datasets: list[GeoXUploadedCSVDataset] = Field(default_factory=list)
    inspections: list[GeoXUploadedCSVInspection] = Field(default_factory=list)
    issues: list[GeoXUploadedCSVIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
