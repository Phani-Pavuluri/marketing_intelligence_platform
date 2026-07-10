"""Planning/MMM uploaded CSV adapter contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.uploaded_csv_materialization import UploadedCSVMaterializationResult

RECOMMENDED_NEXT_PLANNING_MMM_UPLOADED_CSV_INPUT_PLAN_ARTIFACT = (
    "MIP_PLANNING_MMM_UPLOADED_CSV_INPUT_PLAN_001"
)

DEFAULT_REQUIRED_PLANNING_MMM_ROLES = (
    "historical_spend",
    "historical_outcome",
)
DEFAULT_OPTIONAL_PLANNING_MMM_ROLES = (
    "channel_taxonomy",
    "budget_constraints",
    "calibration_signals",
    "model_config",
)


class PlanningMMMUploadedCSVRole(StrEnum):
    """Planning/MMM roles for uploaded CSV adapter mapping."""

    HISTORICAL_SPEND = "historical_spend"
    HISTORICAL_OUTCOME = "historical_outcome"
    CHANNEL_TAXONOMY = "channel_taxonomy"
    BUDGET_CONSTRAINTS = "budget_constraints"
    CALIBRATION_SIGNALS = "calibration_signals"
    MODEL_CONFIG = "model_config"
    UNKNOWN = "unknown"


class PlanningMMMUploadedCSVRoleSource(StrEnum):
    """How a Planning/MMM uploaded CSV role was assigned."""

    EXPLICIT = "explicit"
    DECLARED_ROLE_HINT = "declared_role_hint"
    UNKNOWN = "unknown"


class PlanningMMMUploadedCSVAdapterStatus(StrEnum):
    """Outcome of adapting shared uploaded CSV materialization for Planning/MMM."""

    ADAPTED = "adapted"
    ADAPTED_WITH_WARNINGS = "adapted_with_warnings"
    BLOCKED_MISSING_MATERIALIZATION_RESULT = "blocked_missing_materialization_result"
    BLOCKED_MATERIALIZATION_NOT_READY = "blocked_materialization_not_ready"
    BLOCKED_MISSING_REQUIRED_ROLE = "blocked_missing_required_role"
    BLOCKED_DUPLICATE_ROLE = "blocked_duplicate_role"
    BLOCKED_AMBIGUOUS_ROLE = "blocked_ambiguous_role"
    BLOCKED_MISSING_REQUIRED_COLUMNS = "blocked_missing_required_columns"
    BLOCKED_DATA_SOURCE_REF_BUILD_FAILED = "blocked_data_source_ref_build_failed"


class PlanningMMMUploadedCSVAdapterIssueCode(StrEnum):
    """Typed Planning/MMM uploaded CSV adapter issue codes."""

    MISSING_MATERIALIZATION_RESULT = "missing_materialization_result"
    MATERIALIZATION_NOT_READY = "materialization_not_ready"
    MISSING_REQUIRED_ROLE = "missing_required_role"
    DUPLICATE_ROLE = "duplicate_role"
    AMBIGUOUS_ROLE = "ambiguous_role"
    MISSING_REQUIRED_COLUMNS = "missing_required_columns"
    DATA_SOURCE_REF_BUILD_FAILED = "data_source_ref_build_failed"
    ROLE_HINT_USED = "role_hint_used"
    ROLE_EXPLICITLY_PROVIDED = "role_explicitly_provided"
    OPTIONAL_CHANNEL_TAXONOMY_MISSING = "optional_channel_taxonomy_missing"
    OPTIONAL_BUDGET_CONSTRAINTS_MISSING = "optional_budget_constraints_missing"
    OPTIONAL_CALIBRATION_SIGNALS_MISSING = "optional_calibration_signals_missing"
    OPTIONAL_MODEL_CONFIG_MISSING = "optional_model_config_missing"
    DATA_SOURCE_REF_CREATED = "data_source_ref_created"
    INTAKE_MANIFEST_COMPATIBLE = "intake_manifest_compatible"
    MMM_CONFIG_DRAFT_COMPATIBLE = "mmm_config_draft_compatible"
    MODEL_READINESS_COMPATIBLE = "model_readiness_compatible"
    LINEAGE_PRESERVED = "lineage_preserved"
    CSV_REPARSE_AVOIDED = "csv_reparse_avoided"


class PlanningMMMUploadedCSVRoleMapping(ContractBaseModel):
    """Planning/MMM role mapping for one materialized uploaded CSV dataset."""

    source_id: str
    dataset_id: str
    role: PlanningMMMUploadedCSVRole
    role_source: PlanningMMMUploadedCSVRoleSource
    required_columns: list[str] = Field(default_factory=list)
    available_columns: list[str] = Field(default_factory=list)
    normalized_columns: list[str] = Field(default_factory=list)
    missing_columns: list[str] = Field(default_factory=list)
    data_source_ref: DataSourceRef | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMUploadedCSVAdapterIssueCode] = Field(default_factory=list)


class PlanningMMMUploadedCSVAdapterRequest(ContractBaseModel):
    """Request to adapt shared uploaded CSV materialization for Planning/MMM."""

    request_id: str
    materialization_result: UploadedCSVMaterializationResult | None = None
    explicit_role_by_source_id: dict[str, PlanningMMMUploadedCSVRole] = Field(default_factory=dict)
    required_columns_by_role: dict[str, list[str]] = Field(default_factory=dict)
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class PlanningMMMUploadedCSVInputAvailability(ContractBaseModel):
    """Planning/MMM input availability from uploaded CSV adapter output."""

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
    role_mappings: list[PlanningMMMUploadedCSVRoleMapping] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class PlanningMMMUploadedCSVAdapterResult(ContractBaseModel):
    """Result of adapting shared uploaded CSV materialization for Planning/MMM."""

    request_id: str
    status: PlanningMMMUploadedCSVAdapterStatus
    availability: PlanningMMMUploadedCSVInputAvailability | None = None
    role_mappings: list[PlanningMMMUploadedCSVRoleMapping] = Field(default_factory=list)
    data_source_refs: list[DataSourceRef] = Field(default_factory=list)
    issues: list[PlanningMMMUploadedCSVAdapterIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
