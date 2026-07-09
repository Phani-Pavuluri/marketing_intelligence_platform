"""GeoX readout source inspection contracts (Stage 2B — metadata only)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.geox_readout_input_resolution import (
    ColumnMappingCandidate,
    DatasetReference,
    DatasetSemanticType,
)

RECOMMENDED_NEXT_STAGE_2C_ARTIFACT = "MIP_GEOX_READOUT_INPUT_RESOLUTION_RUNTIME_001C"


class SourceInspectionStatus(StrEnum):
    """Outcome of lightweight dataset source inspection."""

    INSPECTED = "inspected"
    SOURCE_NOT_RESOLVABLE = "source_not_resolvable"
    SOURCE_TYPE_NOT_SUPPORTED = "source_type_not_supported"
    DECLARED_COLUMNS_VALIDATED = "declared_columns_validated"
    DECLARED_COLUMNS_MISSING = "declared_columns_missing"
    NO_COLUMNS_AVAILABLE = "no_columns_available"
    INSPECTION_SKIPPED = "inspection_skipped"


class SourceInspectionIssueCode(StrEnum):
    """Typed inspection issue codes."""

    SOURCE_URI_MISSING = "source_uri_missing"
    SOURCE_NOT_FOUND = "source_not_found"
    SOURCE_TYPE_UNSUPPORTED = "source_type_unsupported"
    DECLARED_COLUMNS_EMPTY = "declared_columns_empty"
    DECLARED_COLUMNS_NOT_FOUND = "declared_columns_not_found"
    DUPLICATE_COLUMNS = "duplicate_columns"
    AMBIGUOUS_SEMANTIC_TYPE = "ambiguous_semantic_type"
    AMBIGUOUS_COLUMN_MAPPING = "ambiguous_column_mapping"
    NO_DATE_COLUMN_CANDIDATE = "no_date_column_candidate"
    NO_GEO_COLUMN_CANDIDATE = "no_geo_column_candidate"
    NO_KPI_COLUMN_CANDIDATE = "no_kpi_column_candidate"
    NO_SPEND_COLUMN_CANDIDATE = "no_spend_column_candidate"
    NO_ASSIGNMENT_COLUMN_CANDIDATE = "no_assignment_column_candidate"
    NO_VALUE_MAPPING_CANDIDATE = "no_value_mapping_candidate"


class ColumnSemanticHint(StrEnum):
    """Semantic hint for a single column name."""

    DATE_OR_WEEK = "date_or_week"
    GEO_OR_UNIT = "geo_or_unit"
    KPI_METRIC = "kpi_metric"
    SPEND_AMOUNT = "spend_amount"
    CURRENCY = "currency"
    CHANNEL = "channel"
    PLATFORM = "platform"
    CAMPAIGN = "campaign"
    TREATMENT_OR_CELL = "treatment_or_cell"
    ASSIGNMENT_LABEL = "assignment_label"
    EXPERIMENT_ID = "experiment_id"
    VALUE_OR_REVENUE = "value_or_revenue"
    MARGIN_OR_PROFIT = "margin_or_profit"
    UNKNOWN = "unknown"


class ColumnInspectionHint(ContractBaseModel):
    """Inspection hint for one column."""

    source_column: str
    semantic_hint: ColumnSemanticHint
    confidence: float = Field(ge=0.0, le=1.0)
    candidate_target_fields: list[str] = Field(default_factory=list)
    notes: str = ""
    warnings: list[str] = Field(default_factory=list)


class DatasetSemanticInspectionHint(ContractBaseModel):
    """Inferred semantic dataset type from column evidence."""

    semantic_type: DatasetSemanticType
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DatasetSourceInspectionResult(ContractBaseModel):
    """Inspection result for one DatasetReference."""

    dataset_ref: DatasetReference
    inspection_status: SourceInspectionStatus
    source_resolvable: bool
    declared_columns: list[str] = Field(default_factory=list)
    available_columns: list[str] = Field(default_factory=list)
    missing_declared_columns: list[str] = Field(default_factory=list)
    semantic_hints: list[DatasetSemanticInspectionHint] = Field(default_factory=list)
    column_hints: list[ColumnInspectionHint] = Field(default_factory=list)
    mapping_candidates: list[ColumnMappingCandidate] = Field(default_factory=list)
    issues: list[SourceInspectionIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class GeoXReadoutSourceInspectionRequest(ContractBaseModel):
    """Batch source inspection request."""

    request_id: str
    dataset_refs: list[DatasetReference] = Field(default_factory=list)
    allow_local_file_metadata_inspection: bool = False
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXReadoutSourceInspectionResult(ContractBaseModel):
    """Batch source inspection result."""

    request_id: str
    dataset_results: list[DatasetSourceInspectionResult] = Field(default_factory=list)
    inspected_dataset_count: int = 0
    unresolved_dataset_count: int = 0
    issues: list[SourceInspectionIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)

    @field_validator("inspected_dataset_count", "unresolved_dataset_count")
    @classmethod
    def counts_non_negative(cls, value: int) -> int:
        if value < 0:
            msg = "counts cannot be negative"
            raise ValueError(msg)
        return value
