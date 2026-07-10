"""Planning/MMM tabular source adapter compatibility contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.planning_mmm_uploaded_csv_adapter import PlanningMMMUploadedCSVRole
from mip.contracts.tabular_source_reference import (
    TabularSourceInspectionResult,
    TabularSourceReference,
    TabularSourceType,
)


class PlanningMMMTabularSourceAdapterStatus(StrEnum):
    """Outcome of adapting generic tabular source inspections for Planning/MMM."""

    ADAPTED = "adapted"
    ADAPTED_WITH_WARNINGS = "adapted_with_warnings"
    BLOCKED_MISSING_TABULAR_SOURCE_RESULT = "blocked_missing_tabular_source_result"
    BLOCKED_TABULAR_SOURCE_NOT_READY = "blocked_tabular_source_not_ready"
    BLOCKED_MISSING_REQUIRED_ROLE = "blocked_missing_required_role"
    BLOCKED_DUPLICATE_ROLE = "blocked_duplicate_role"
    BLOCKED_AMBIGUOUS_ROLE = "blocked_ambiguous_role"
    BLOCKED_MISSING_REQUIRED_COLUMNS = "blocked_missing_required_columns"
    BLOCKED_DATA_SOURCE_REF_UNAVAILABLE = "blocked_data_source_ref_unavailable"


class PlanningMMMTabularSourceAdapterIssueCode(StrEnum):
    """Typed Planning/MMM tabular source adapter issue codes."""

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
    OPTIONAL_CHANNEL_TAXONOMY_MISSING = "optional_channel_taxonomy_missing"
    OPTIONAL_BUDGET_CONSTRAINTS_MISSING = "optional_budget_constraints_missing"
    OPTIONAL_CALIBRATION_SIGNALS_MISSING = "optional_calibration_signals_missing"
    OPTIONAL_MODEL_CONFIG_MISSING = "optional_model_config_missing"
    NO_CONNECTOR_RUNTIME = "no_connector_runtime"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"


class PlanningMMMTabularSourceRoleSource(StrEnum):
    """How a Planning/MMM tabular source role was assigned."""

    EXPLICIT = "explicit"
    DECLARED_ROLE_HINT = "declared_role_hint"
    UNKNOWN = "unknown"


class PlanningMMMTabularSourceRoleMapping(ContractBaseModel):
    """Planning/MMM role mapping for one generic tabular source inspection."""

    source_id: str
    source_type: TabularSourceType
    source_name: str = ""
    role: PlanningMMMUploadedCSVRole
    role_source: PlanningMMMTabularSourceRoleSource
    required_columns: list[str] = Field(default_factory=list)
    available_columns: list[str] = Field(default_factory=list)
    normalized_columns: list[str] = Field(default_factory=list)
    missing_columns: list[str] = Field(default_factory=list)
    data_source_ref: DataSourceRef | None = None
    tabular_source_reference: TabularSourceReference | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMTabularSourceAdapterIssueCode] = Field(default_factory=list)


class PlanningMMMTabularSourceAdapterRequest(ContractBaseModel):
    """Request to adapt generic tabular source inspections for Planning/MMM."""

    request_id: str
    tabular_source_result: TabularSourceInspectionResult | None = None
    explicit_role_by_source_id: dict[str, PlanningMMMUploadedCSVRole] = Field(default_factory=dict)
    required_columns_by_role: dict[str, list[str]] = Field(default_factory=dict)
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class PlanningMMMTabularSourceInputAvailability(ContractBaseModel):
    """Planning/MMM input availability from tabular source adapter output."""

    has_historical_spend: bool = False
    has_historical_outcome: bool = False
    has_channel_taxonomy: bool = False
    has_budget_constraints: bool = False
    has_calibration_signals: bool = False
    has_model_config: bool = False
    historical_spend_source_id: str | None = None
    historical_outcome_source_id: str | None = None
    channel_taxonomy_source_id: str | None = None
    budget_constraints_source_id: str | None = None
    calibration_signals_source_id: str | None = None
    model_config_source_id: str | None = None
    data_source_refs: list[DataSourceRef] = Field(default_factory=list)
    role_mappings: list[PlanningMMMTabularSourceRoleMapping] = Field(default_factory=list)
    tabular_source_references: list[TabularSourceReference] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class PlanningMMMTabularSourceAdapterResult(ContractBaseModel):
    """Result of adapting generic tabular source inspections for Planning/MMM."""

    request_id: str
    status: PlanningMMMTabularSourceAdapterStatus
    availability: PlanningMMMTabularSourceInputAvailability | None = None
    role_mappings: list[PlanningMMMTabularSourceRoleMapping] = Field(default_factory=list)
    data_source_refs: list[DataSourceRef] = Field(default_factory=list)
    tabular_source_references: list[TabularSourceReference] = Field(default_factory=list)
    issues: list[PlanningMMMTabularSourceAdapterIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
