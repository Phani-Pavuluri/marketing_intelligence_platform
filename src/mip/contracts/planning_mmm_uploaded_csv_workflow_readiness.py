"""Planning/MMM uploaded CSV workflow readiness contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.planning_mmm_uploaded_csv_input_plan import (
    PlanningMMMUploadedCSVInputPlanResult,
)

RECOMMENDED_NEXT_PLANNING_MMM_READINESS_REPORT_ADAPTER_ARTIFACT = (
    "MIP_PLANNING_MMM_READINESS_REPORT_ADAPTER_001"
)


class PlanningMMMUploadedCSVWorkflowReadinessStatus(StrEnum):
    """Outcome of evaluating Planning/MMM uploaded CSV workflow readiness."""

    READY_FOR_MMM_WORKFLOW_READINESS = "ready_for_mmm_workflow_readiness"
    READY_WITH_WARNINGS = "ready_with_warnings"
    BLOCKED_MISSING_INPUT_PLAN_RESULT = "blocked_missing_input_plan_result"
    BLOCKED_INPUT_PLAN_NOT_READY = "blocked_input_plan_not_ready"
    BLOCKED_MISSING_REQUIRED_INPUT = "blocked_missing_required_input"
    BLOCKED_MISSING_REQUIRED_COLUMNS = "blocked_missing_required_columns"
    BLOCKED_EXECUTION_FLAGS_NOT_SAFE = "blocked_execution_flags_not_safe"
    DIAGNOSTIC_ONLY = "diagnostic_only"


class PlanningMMMUploadedCSVWorkflowReadinessTier(StrEnum):
    """Tier for entering gated MMM workflow readiness."""

    READY_FOR_GATED_WORKFLOW = "ready_for_gated_workflow"
    READY_FOR_GATED_WORKFLOW_WITH_WARNINGS = "ready_for_gated_workflow_with_warnings"
    BLOCKED = "blocked"
    DIAGNOSTIC_ONLY = "diagnostic_only"


class PlanningMMMUploadedCSVWorkflowReadinessIssueCode(StrEnum):
    """Typed Planning/MMM uploaded CSV workflow readiness issue codes."""

    MISSING_INPUT_PLAN_RESULT = "missing_input_plan_result"
    INPUT_PLAN_NOT_READY = "input_plan_not_ready"
    MISSING_REQUIRED_INPUT = "missing_required_input"
    MISSING_REQUIRED_COLUMNS = "missing_required_columns"
    OPTIONAL_INPUT_MISSING = "optional_input_missing"
    EXECUTION_FLAGS_NOT_SAFE = "execution_flags_not_safe"
    DATA_SOURCE_REFS_AVAILABLE = "data_source_refs_available"
    INTAKE_MANIFEST_DEFERRED = "intake_manifest_deferred"
    MMM_CONFIG_DRAFT_DEFERRED = "mmm_config_draft_deferred"
    MODEL_READINESS_DEFERRED = "model_readiness_deferred"
    CALIBRATION_SIGNAL_MAPPING_DEFERRED = "calibration_signal_mapping_deferred"
    MMM_DATA_READINESS_COMPATIBLE = "mmm_data_readiness_compatible"
    MMM_DATA_READINESS_COMPATIBILITY_DEFERRED = "mmm_data_readiness_compatibility_deferred"
    WORKFLOW_READINESS_METADATA_CREATED = "workflow_readiness_metadata_created"
    LINEAGE_PRESERVED = "lineage_preserved"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"


class PlanningMMMUploadedCSVWorkflowReadinessRequest(ContractBaseModel):
    """Request to evaluate Planning/MMM workflow readiness from uploaded CSV input plan."""

    request_id: str
    input_plan_result: PlanningMMMUploadedCSVInputPlanResult | None = None
    require_column_validated_schema: bool = False
    require_optional_inputs: bool = False
    required_optional_inputs: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class PlanningMMMUploadedCSVWorkflowReadinessReport(ContractBaseModel):
    """Metadata-only workflow readiness report for uploaded CSV Planning/MMM input."""

    report_id: str
    status: PlanningMMMUploadedCSVWorkflowReadinessStatus
    tier: PlanningMMMUploadedCSVWorkflowReadinessTier
    input_plan_id: str | None = None
    data_source_refs: list[DataSourceRef] = Field(default_factory=list)
    readiness_metadata: dict[str, str | bool] = Field(default_factory=dict)
    missing_required_inputs: list[str] = Field(default_factory=list)
    missing_optional_inputs: list[str] = Field(default_factory=list)
    missing_required_columns: list[str] = Field(default_factory=list)
    deferred_objects: dict[str, str] = Field(default_factory=dict)
    compatibility: dict[str, bool] = Field(default_factory=dict)
    execution_allowed: dict[str, bool] = Field(default_factory=dict)
    issues: list[PlanningMMMUploadedCSVWorkflowReadinessIssueCode] = Field(
        default_factory=list
    )
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class PlanningMMMUploadedCSVWorkflowReadinessResult(ContractBaseModel):
    """Result of evaluating Planning/MMM workflow readiness from uploaded CSV input plan."""

    request_id: str
    status: PlanningMMMUploadedCSVWorkflowReadinessStatus
    report: PlanningMMMUploadedCSVWorkflowReadinessReport | None = None
    issues: list[PlanningMMMUploadedCSVWorkflowReadinessIssueCode] = Field(
        default_factory=list
    )
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
