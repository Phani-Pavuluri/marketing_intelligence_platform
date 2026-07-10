"""GeoX readout uploaded CSV adapter contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.geox_readout_input_resolution import DatasetReference
from mip.contracts.uploaded_csv_materialization import UploadedCSVMaterializationResult

RECOMMENDED_NEXT_GEOX_UPLOADED_CSV_RUNTIME_BRIDGE_ARTIFACT = (
    "MIP_GEOX_READOUT_UPLOADED_CSV_RUNTIME_BRIDGE_001"
)

DEFAULT_REQUIRED_GEOX_ROLES = (
    "kpi_panel",
    "spend_panel",
    "assignment_table",
)
DEFAULT_OPTIONAL_GEOX_ROLE = "experiment_metadata"


class GeoXUploadedCSVRole(StrEnum):
    """GeoX readout roles for uploaded CSV adapter mapping."""

    KPI_PANEL = "kpi_panel"
    SPEND_PANEL = "spend_panel"
    ASSIGNMENT_TABLE = "assignment_table"
    EXPERIMENT_METADATA = "experiment_metadata"
    UNKNOWN = "unknown"


class GeoXUploadedCSVRoleSource(StrEnum):
    """How a GeoX uploaded CSV role was assigned."""

    EXPLICIT = "explicit"
    DECLARED_ROLE_HINT = "declared_role_hint"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


class GeoXUploadedCSVAdapterStatus(StrEnum):
    """Outcome of adapting shared uploaded CSV materialization for GeoX readout."""

    ADAPTED = "adapted"
    ADAPTED_WITH_WARNINGS = "adapted_with_warnings"
    BLOCKED_MISSING_MATERIALIZATION_RESULT = "blocked_missing_materialization_result"
    BLOCKED_MATERIALIZATION_NOT_READY = "blocked_materialization_not_ready"
    BLOCKED_MISSING_REQUIRED_ROLE = "blocked_missing_required_role"
    BLOCKED_DUPLICATE_ROLE = "blocked_duplicate_role"
    BLOCKED_AMBIGUOUS_ROLE = "blocked_ambiguous_role"
    BLOCKED_MISSING_REQUIRED_COLUMNS = "blocked_missing_required_columns"
    BLOCKED_DATASET_REFERENCE_BUILD_FAILED = "blocked_dataset_reference_build_failed"


class GeoXUploadedCSVAdapterIssueCode(StrEnum):
    """Typed GeoX uploaded CSV adapter issue codes."""

    MISSING_MATERIALIZATION_RESULT = "missing_materialization_result"
    MATERIALIZATION_NOT_READY = "materialization_not_ready"
    MISSING_REQUIRED_ROLE = "missing_required_role"
    DUPLICATE_ROLE = "duplicate_role"
    AMBIGUOUS_ROLE = "ambiguous_role"
    MISSING_REQUIRED_COLUMNS = "missing_required_columns"
    DATASET_REFERENCE_BUILD_FAILED = "dataset_reference_build_failed"
    ROLE_HINT_USED = "role_hint_used"
    ROLE_EXPLICITLY_PROVIDED = "role_explicitly_provided"
    OPTIONAL_METADATA_MISSING = "optional_metadata_missing"
    DATASET_REFERENCE_CREATED = "dataset_reference_created"
    SOURCE_INSPECTION_COMPATIBLE = "source_inspection_compatible"
    INPUT_RESOLUTION_COMPATIBLE = "input_resolution_compatible"
    LINEAGE_PRESERVED = "lineage_preserved"


class GeoXUploadedCSVRoleMapping(ContractBaseModel):
    """GeoX role mapping for one materialized uploaded CSV dataset."""

    source_id: str
    dataset_id: str
    role: GeoXUploadedCSVRole
    role_source: GeoXUploadedCSVRoleSource
    required_columns: list[str] = Field(default_factory=list)
    available_columns: list[str] = Field(default_factory=list)
    normalized_columns: list[str] = Field(default_factory=list)
    missing_columns: list[str] = Field(default_factory=list)
    dataset_reference: DatasetReference | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    issues: list[GeoXUploadedCSVAdapterIssueCode] = Field(default_factory=list)


class GeoXUploadedCSVAdapterRequest(ContractBaseModel):
    """Request to adapt shared uploaded CSV materialization for GeoX readout."""

    request_id: str
    materialization_result: UploadedCSVMaterializationResult | None = None
    explicit_role_by_source_id: dict[str, GeoXUploadedCSVRole] = Field(default_factory=dict)
    required_columns_by_role: dict[str, list[str]] = Field(default_factory=dict)
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXUploadedCSVAdapterAvailability(ContractBaseModel):
    """GeoX readout availability metadata from uploaded CSV adapter output."""

    has_kpi_panel: bool = False
    has_spend_panel: bool = False
    has_assignment_table: bool = False
    has_experiment_metadata: bool = False
    kpi_panel_source_id: str | None = None
    spend_panel_source_id: str | None = None
    assignment_table_source_id: str | None = None
    metadata_source_id: str | None = None
    dataset_references: list[DatasetReference] = Field(default_factory=list)
    role_mappings: list[GeoXUploadedCSVRoleMapping] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class GeoXUploadedCSVAdapterResult(ContractBaseModel):
    """Result of adapting shared uploaded CSV materialization for GeoX readout."""

    request_id: str
    status: GeoXUploadedCSVAdapterStatus
    availability: GeoXUploadedCSVAdapterAvailability | None = None
    role_mappings: list[GeoXUploadedCSVRoleMapping] = Field(default_factory=list)
    dataset_references: list[DatasetReference] = Field(default_factory=list)
    issues: list[GeoXUploadedCSVAdapterIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
