"""Generic tabular source reference and inspection contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import ConfigDict, Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.uploaded_csv_materialization import MaterializedTabularDataset

RECOMMENDED_NEXT_PLANNING_MMM_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_ARTIFACT = (
    "MIP_PLANNING_MMM_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001"
)
RECOMMENDED_NEXT_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_ARTIFACT = (
    "MIP_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001"
)


class TabularSourceType(StrEnum):
    """Declared tabular source kinds (enum-only; no runtime adapters in this artifact)."""

    UPLOADED_CSV = "uploaded_csv"
    DATABRICKS_TABLE = "databricks_table"
    WAREHOUSE_TABLE = "warehouse_table"
    API_EXTRACT = "api_extract"
    REGISTERED_TABLE = "registered_table"
    REGISTERED_ARTIFACT = "registered_artifact"
    UNKNOWN = "unknown"


class TabularSourceAccessMode(StrEnum):
    """How a tabular source may be accessed."""

    LOCAL_FILE = "local_file"
    REFERENCE_ONLY = "reference_only"
    SCHEMA_ONLY = "schema_only"
    SAMPLED = "sampled"
    MATERIALIZED = "materialized"
    UNKNOWN = "unknown"


class TabularSourceInspectionStatus(StrEnum):
    """Outcome of tabular source inspection."""

    INSPECTED = "inspected"
    INSPECTED_WITH_WARNINGS = "inspected_with_warnings"
    BLOCKED_MISSING_SOURCE = "blocked_missing_source"
    BLOCKED_UNSUPPORTED_SOURCE_TYPE = "blocked_unsupported_source_type"
    BLOCKED_SCHEMA_UNAVAILABLE = "blocked_schema_unavailable"
    BLOCKED_MATERIALIZATION_UNAVAILABLE = "blocked_materialization_unavailable"
    BLOCKED_LINEAGE_UNAVAILABLE = "blocked_lineage_unavailable"


class TabularSourceMaterializationMode(StrEnum):
    """Whether and how tabular data is materialized."""

    NOT_MATERIALIZED = "not_materialized"
    MATERIALIZED_IN_MEMORY = "materialized_in_memory"
    MATERIALIZED_SAMPLE_ONLY = "materialized_sample_only"
    REFERENCE_ONLY = "reference_only"


class TabularSourceIssueCode(StrEnum):
    """Typed tabular source inspection issue codes."""

    SOURCE_REFERENCE_CREATED = "source_reference_created"
    SOURCE_INSPECTION_CREATED = "source_inspection_created"
    SCHEMA_CREATED = "schema_created"
    LINEAGE_CREATED = "lineage_created"
    AVAILABILITY_CREATED = "availability_created"
    MATERIALIZED_DATASET_ATTACHED = "materialized_dataset_attached"
    REFERENCE_ONLY_SOURCE = "reference_only_source"
    SCHEMA_ONLY_SOURCE = "schema_only_source"
    DECLARED_ROLE_HINT_PRESERVED = "declared_role_hint_preserved"
    DATA_SOURCE_REF_COMPATIBLE = "data_source_ref_compatible"
    UPLOADED_CSV_COMPATIBILITY_CREATED = "uploaded_csv_compatibility_created"
    MISSING_SOURCE = "missing_source"
    UNSUPPORTED_SOURCE_TYPE = "unsupported_source_type"
    SCHEMA_UNAVAILABLE = "schema_unavailable"
    MATERIALIZATION_UNAVAILABLE = "materialization_unavailable"
    LINEAGE_UNAVAILABLE = "lineage_unavailable"
    NO_CONNECTOR_RUNTIME = "no_connector_runtime"
    NO_NETWORK_CALLS = "no_network_calls"
    NO_SQL_EXECUTION = "no_sql_execution"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"


class TabularSourceColumn(ContractBaseModel):
    """Column metadata for a tabular source schema."""

    name: str
    normalized_name: str = ""
    semantic_hint: str | None = None
    dtype: str | None = None
    nullable: bool | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class TabularSourceSchema(ContractBaseModel):
    """Schema metadata for a tabular source."""

    columns: list[TabularSourceColumn] = Field(default_factory=list)
    column_names: list[str] = Field(default_factory=list)
    normalized_column_names: list[str] = Field(default_factory=list)
    row_count: int | None = None
    estimated_row_count: int | None = None
    schema_source: str = ""
    metadata: dict[str, str] = Field(default_factory=dict)


class TabularSourceLineage(ContractBaseModel):
    """Provenance metadata for a tabular source."""

    source_id: str
    source_type: TabularSourceType
    source_uri: str = ""
    source_name: str = ""
    created_from: str = ""
    upstream_lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str] = Field(default_factory=dict)


class TabularSourceReference(ContractBaseModel):
    """Source-neutral reference to a tabular origin."""

    model_config = ConfigDict(populate_by_name=True)

    source_id: str
    source_type: TabularSourceType
    access_mode: TabularSourceAccessMode
    materialization_mode: TabularSourceMaterializationMode
    declared_role_hint: str | None = None
    source_uri: str = ""
    source_name: str = ""
    source_schema: TabularSourceSchema | None = Field(default=None, alias="schema")
    lineage: TabularSourceLineage | None = None
    data_source_ref: DataSourceRef | None = None
    metadata: dict[str, str] = Field(default_factory=dict)


class TabularSourceAvailability(ContractBaseModel):
    """Availability flags for a tabular source inspection."""

    has_schema: bool = False
    has_lineage: bool = False
    has_data_source_ref: bool = False
    has_materialized_dataset: bool = False
    has_materialized_sample: bool = False
    is_reference_only: bool = False
    is_connector_runtime_required: bool = False
    materialized_dataset_id: str | None = None
    warnings: list[str] = Field(default_factory=list)
    issues: list[TabularSourceIssueCode] = Field(default_factory=list)


class TabularSourceInspection(ContractBaseModel):
    """Inspection payload for one tabular source."""

    model_config = ConfigDict(populate_by_name=True)

    source_reference: TabularSourceReference
    source_schema: TabularSourceSchema | None = Field(default=None, alias="schema")
    lineage: TabularSourceLineage | None = None
    availability: TabularSourceAvailability | None = None
    materialized_dataset: MaterializedTabularDataset | None = None
    warnings: list[str] = Field(default_factory=list)
    issues: list[TabularSourceIssueCode] = Field(default_factory=list)


class TabularSourceInspectionResult(ContractBaseModel):
    """Batch tabular source inspection result."""

    request_id: str
    status: TabularSourceInspectionStatus
    inspections: list[TabularSourceInspection] = Field(default_factory=list)
    source_references: list[TabularSourceReference] = Field(default_factory=list)
    issues: list[TabularSourceIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
