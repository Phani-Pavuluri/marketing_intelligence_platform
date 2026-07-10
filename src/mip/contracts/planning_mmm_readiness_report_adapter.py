"""Planning/MMM readiness report adapter contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.planning_mmm_uploaded_csv_workflow_readiness import (
    PlanningMMMUploadedCSVWorkflowReadinessResult,
)
from mip.contracts.tabular_source_reference import TabularSourceReference

RECOMMENDED_NEXT_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_ARTIFACT = (
    "MIP_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001"
)
RECOMMENDED_NEXT_PLANNING_MMM_CALIBRATION_SIGNAL_INTAKE_ARTIFACT = (
    "MIP_PLANNING_MMM_CALIBRATION_SIGNAL_INTAKE_FROM_TABULAR_SOURCE_001"
)


class PlanningMMMReadinessReportAdapterStatus(StrEnum):
    """Outcome of adapting Planning/MMM workflow readiness to readiness report semantics."""

    REPORT_ADAPTED = "report_adapted"
    REPORT_ADAPTED_WITH_WARNINGS = "report_adapted_with_warnings"
    BLOCKED_MISSING_WORKFLOW_READINESS_RESULT = "blocked_missing_workflow_readiness_result"
    BLOCKED_WORKFLOW_READINESS_NOT_READY = "blocked_workflow_readiness_not_ready"
    BLOCKED_MISSING_REQUIRED_INPUT = "blocked_missing_required_input"
    BLOCKED_MISSING_REQUIRED_COLUMNS = "blocked_missing_required_columns"
    BLOCKED_MMM_DATA_READINESS_CONTRACT_UNAVAILABLE = (
        "blocked_mmm_data_readiness_contract_unavailable"
    )
    DIAGNOSTIC_ONLY = "diagnostic_only"


class PlanningMMMReadinessReportCompatibilityMode(StrEnum):
    """How closely workflow readiness maps to MMMDataReadinessReport construction."""

    METADATA_COMPATIBLE = "metadata_compatible"
    FULL_REPORT_CONSTRUCTION_READY = "full_report_construction_ready"
    FULL_REPORT_CONSTRUCTION_DEFERRED = "full_report_construction_deferred"
    DIAGNOSTIC_ONLY = "diagnostic_only"


class PlanningMMMReadinessReportAdapterIssueCode(StrEnum):
    """Typed Planning/MMM readiness report adapter issue codes."""

    MISSING_WORKFLOW_READINESS_RESULT = "missing_workflow_readiness_result"
    WORKFLOW_READINESS_NOT_READY = "workflow_readiness_not_ready"
    MISSING_REQUIRED_INPUT = "missing_required_input"
    MISSING_REQUIRED_COLUMNS = "missing_required_columns"
    OPTIONAL_INPUT_MISSING = "optional_input_missing"
    MMM_DATA_READINESS_METADATA_COMPATIBLE = "mmm_data_readiness_metadata_compatible"
    MMM_DATA_READINESS_FULL_CONSTRUCTION_READY = "mmm_data_readiness_full_construction_ready"
    MMM_DATA_READINESS_FULL_CONSTRUCTION_DEFERRED = (
        "mmm_data_readiness_full_construction_deferred"
    )
    DATA_SOURCE_REFS_PRESERVED = "data_source_refs_preserved"
    TABULAR_SOURCE_REFS_PRESERVED = "tabular_source_refs_preserved"
    READINESS_STATUS_PRESERVED = "readiness_status_preserved"
    READINESS_TIER_PRESERVED = "readiness_tier_preserved"
    DEFERRED_OBJECTS_PRESERVED = "deferred_objects_preserved"
    LINEAGE_PRESERVED = "lineage_preserved"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_BAYESIAN_FITTING = "no_bayesian_fitting"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"


class PlanningMMMReadinessReportAdapterRequest(ContractBaseModel):
    """Request to adapt Planning/MMM workflow readiness into readiness report semantics."""

    request_id: str
    workflow_readiness_result: PlanningMMMUploadedCSVWorkflowReadinessResult | None = None
    require_full_mmm_data_readiness_report: bool = False
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class PlanningMMMReadinessReportCompatibility(ContractBaseModel):
    """Compatibility metadata for MMMDataReadinessReport construction."""

    mode: PlanningMMMReadinessReportCompatibilityMode
    mmm_data_readiness_report_available: bool = False
    full_report_constructed: bool = False
    full_report_deferred_reason: str = ""
    metadata_compatible: bool = False
    compatible_fields: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    deferred_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMReadinessReportAdapterIssueCode] = Field(default_factory=list)


class PlanningMMMReadinessReportAdapterEnvelope(ContractBaseModel):
    """Metadata-only readiness report adapter envelope."""

    envelope_id: str
    source_workflow_readiness_status: str
    source_workflow_readiness_tier: str
    readiness_report_status: str
    compatibility: PlanningMMMReadinessReportCompatibility
    data_source_refs: list[DataSourceRef] = Field(default_factory=list)
    tabular_source_refs: list[TabularSourceReference] = Field(default_factory=list)
    missing_required_inputs: list[str] = Field(default_factory=list)
    missing_optional_inputs: list[str] = Field(default_factory=list)
    missing_required_columns: list[str] = Field(default_factory=list)
    deferred_objects: dict[str, str] = Field(default_factory=dict)
    readiness_metadata: dict[str, str | bool] = Field(default_factory=dict)
    execution_allowed: dict[str, bool] = Field(default_factory=dict)
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMReadinessReportAdapterIssueCode] = Field(default_factory=list)


class PlanningMMMReadinessReportAdapterResult(ContractBaseModel):
    """Result of adapting Planning/MMM workflow readiness to readiness report semantics."""

    request_id: str
    status: PlanningMMMReadinessReportAdapterStatus
    envelope: PlanningMMMReadinessReportAdapterEnvelope | None = None
    issues: list[PlanningMMMReadinessReportAdapterIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
