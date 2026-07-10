"""GeoX tabular source adapter compatibility contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.geox_uploaded_csv_adapter import GeoXUploadedCSVRole
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.tabular_source_reference import (
    TabularSourceInspectionResult,
    TabularSourceReference,
    TabularSourceType,
)

RECOMMENDED_NEXT_TABULAR_SOURCE_REUSE_COMPLETION_AUDIT_ARTIFACT = (
    "MIP_TABULAR_SOURCE_REUSE_COMPLETION_AUDIT_001"
)
RECOMMENDED_NEXT_GEOX_READOUT_RESULT_ROUTING_FROM_TABULAR_SOURCE_ARTIFACT = (
    "MIP_GEOX_READOUT_RESULT_ROUTING_FROM_TABULAR_SOURCE_001"
)


class GeoXTabularSourceAdapterStatus(StrEnum):
    """Outcome of adapting generic tabular source inspections for GeoX readout."""

    ADAPTED = "adapted"
    ADAPTED_WITH_WARNINGS = "adapted_with_warnings"
    BLOCKED_MISSING_TABULAR_SOURCE_RESULT = "blocked_missing_tabular_source_result"
    BLOCKED_TABULAR_SOURCE_NOT_READY = "blocked_tabular_source_not_ready"
    BLOCKED_MISSING_REQUIRED_ROLE = "blocked_missing_required_role"
    BLOCKED_DUPLICATE_ROLE = "blocked_duplicate_role"
    BLOCKED_AMBIGUOUS_ROLE = "blocked_ambiguous_role"
    BLOCKED_MISSING_REQUIRED_COLUMNS = "blocked_missing_required_columns"
    BLOCKED_DATA_SOURCE_REF_UNAVAILABLE = "blocked_data_source_ref_unavailable"


class GeoXTabularSourceRoleSource(StrEnum):
    """How a GeoX tabular source role was assigned."""

    EXPLICIT = "explicit"
    DECLARED_ROLE_HINT = "declared_role_hint"
    UNKNOWN = "unknown"


class GeoXTabularSourceAdapterIssueCode(StrEnum):
    """Typed GeoX tabular source adapter issue codes."""

    MISSING_TABULAR_SOURCE_RESULT = "missing_tabular_source_result"
    TABULAR_SOURCE_NOT_READY = "tabular_source_not_ready"
    MISSING_REQUIRED_ROLE = "missing_required_role"
    DUPLICATE_ROLE = "duplicate_role"
    AMBIGUOUS_ROLE = "ambiguous_role"
    MISSING_REQUIRED_COLUMNS = "missing_required_columns"
    DATA_SOURCE_REF_UNAVAILABLE = "data_source_ref_unavailable"
    ROLE_HINT_USED = "role_hint_used"
    ROLE_EXPLICITLY_PROVIDED = "role_explicitly_provided"
    TABULAR_SOURCE_SCHEMA_USED = "tabular_source_schema_used"
    TABULAR_SOURCE_LINEAGE_PRESERVED = "tabular_source_lineage_preserved"
    TABULAR_SOURCE_REFERENCE_PRESERVED = "tabular_source_reference_preserved"
    DATA_SOURCE_REF_PRESERVED = "data_source_ref_preserved"
    UPLOADED_CSV_COMPATIBILITY_PATH_SUPPORTED = "uploaded_csv_compatibility_path_supported"
    DESIGN_DATASET_MISSING = "design_dataset_missing"
    OUTCOME_DATASET_MISSING = "outcome_dataset_missing"
    SPEND_DATASET_MISSING = "spend_dataset_missing"
    OPTIONAL_COVARIATE_DATASET_MISSING = "optional_covariate_dataset_missing"
    OPTIONAL_GEO_METADATA_MISSING = "optional_geo_metadata_missing"
    NO_CONNECTOR_RUNTIME = "no_connector_runtime"
    NO_PANEL_EXP_RUNTIME_EXECUTION = "no_panel_exp_runtime_execution"
    NO_LIFT_COMPUTATION = "no_lift_computation"
    NO_DELTA_MU_COMPUTATION = "no_delta_mu_computation"
    NO_SPEND_DELTA_COMPUTATION = "no_spend_delta_computation"
    NO_ROI_ROAS_COMPUTATION = "no_roi_roas_computation"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"


class GeoXTabularSourceRoleMapping(ContractBaseModel):
    """GeoX role mapping for one generic tabular source inspection."""

    source_id: str
    source_type: TabularSourceType
    source_name: str = ""
    role: GeoXUploadedCSVRole
    role_source: GeoXTabularSourceRoleSource
    required_columns: list[str] = Field(default_factory=list)
    available_columns: list[str] = Field(default_factory=list)
    normalized_columns: list[str] = Field(default_factory=list)
    missing_columns: list[str] = Field(default_factory=list)
    data_source_ref: DataSourceRef | None = None
    tabular_source_reference: TabularSourceReference | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    issues: list[GeoXTabularSourceAdapterIssueCode] = Field(default_factory=list)


class GeoXTabularSourceAdapterRequest(ContractBaseModel):
    """Request to adapt generic tabular source inspections for GeoX readout."""

    request_id: str
    tabular_source_result: TabularSourceInspectionResult | None = None
    explicit_role_by_source_id: dict[str, GeoXUploadedCSVRole] = Field(default_factory=dict)
    required_columns_by_role: dict[str, list[str]] = Field(default_factory=dict)
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXTabularSourceInputAvailability(ContractBaseModel):
    """GeoX readout availability from tabular source adapter output."""

    has_kpi_panel: bool = False
    has_spend_panel: bool = False
    has_assignment_table: bool = False
    has_experiment_metadata: bool = False
    kpi_panel_source_id: str | None = None
    spend_panel_source_id: str | None = None
    assignment_table_source_id: str | None = None
    metadata_source_id: str | None = None
    data_source_refs: list[DataSourceRef] = Field(default_factory=list)
    role_mappings: list[GeoXTabularSourceRoleMapping] = Field(default_factory=list)
    tabular_source_references: list[TabularSourceReference] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class GeoXTabularSourceAdapterResult(ContractBaseModel):
    """Result of adapting generic tabular source inspections for GeoX readout."""

    request_id: str
    status: GeoXTabularSourceAdapterStatus
    availability: GeoXTabularSourceInputAvailability | None = None
    role_mappings: list[GeoXTabularSourceRoleMapping] = Field(default_factory=list)
    data_source_refs: list[DataSourceRef] = Field(default_factory=list)
    tabular_source_references: list[TabularSourceReference] = Field(default_factory=list)
    issues: list[GeoXTabularSourceAdapterIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
