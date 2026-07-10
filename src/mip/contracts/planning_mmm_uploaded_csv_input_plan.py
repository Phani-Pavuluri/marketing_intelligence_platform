"""Planning/MMM uploaded CSV input plan contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.planning_mmm_uploaded_csv_adapter import (
    PlanningMMMUploadedCSVAdapterResult,
    PlanningMMMUploadedCSVRole,
)

RECOMMENDED_NEXT_PLANNING_MMM_WORKFLOW_READINESS_ARTIFACT = (
    "MIP_PLANNING_MMM_WORKFLOW_READINESS_FROM_UPLOADED_CSV_001"
)


class PlanningMMMUploadedCSVInputPlanStatus(StrEnum):
    """Outcome of building a Planning/MMM uploaded CSV input plan."""

    PLAN_READY = "plan_ready"
    PLAN_READY_WITH_WARNINGS = "plan_ready_with_warnings"
    PLAN_BLOCKED_MISSING_ADAPTER_RESULT = "plan_blocked_missing_adapter_result"
    PLAN_BLOCKED_ADAPTER_NOT_READY = "plan_blocked_adapter_not_ready"
    PLAN_BLOCKED_MISSING_REQUIRED_INPUT = "plan_blocked_missing_required_input"
    PLAN_BLOCKED_MISSING_REQUIRED_COLUMNS = "plan_blocked_missing_required_columns"
    PLAN_DIAGNOSTIC_ONLY = "plan_diagnostic_only"


class PlanningMMMUploadedCSVInputPlanIssueCode(StrEnum):
    """Typed Planning/MMM uploaded CSV input plan issue codes."""

    MISSING_ADAPTER_RESULT = "missing_adapter_result"
    ADAPTER_NOT_READY = "adapter_not_ready"
    MISSING_REQUIRED_INPUT = "missing_required_input"
    MISSING_REQUIRED_COLUMNS = "missing_required_columns"
    OPTIONAL_INPUT_MISSING = "optional_input_missing"
    DATA_SOURCE_REF_INCLUDED = "data_source_ref_included"
    INTAKE_MANIFEST_DEFERRED = "intake_manifest_deferred"
    MMM_CONFIG_DRAFT_DEFERRED = "mmm_config_draft_deferred"
    MODEL_READINESS_DEFERRED = "model_readiness_deferred"
    CALIBRATION_SIGNAL_MAPPING_DEFERRED = "calibration_signal_mapping_deferred"
    READINESS_METADATA_CREATED = "readiness_metadata_created"
    LINEAGE_PRESERVED = "lineage_preserved"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"


class PlanningMMMUploadedCSVInputPlanReadinessTier(StrEnum):
    """Readiness tier for future MMM workflow entry."""

    READY_FOR_WORKFLOW_READINESS = "ready_for_workflow_readiness"
    READY_WITH_OPTIONAL_GAPS = "ready_with_optional_gaps"
    BLOCKED = "blocked"
    DIAGNOSTIC_ONLY = "diagnostic_only"


class PlanningMMMUploadedCSVInputRequirement(ContractBaseModel):
    """One Planning/MMM input requirement in an uploaded CSV input plan."""

    role: PlanningMMMUploadedCSVRole
    required: bool = True
    required_columns: list[str] = Field(default_factory=list)
    available: bool = False
    source_id: str | None = None
    data_source_ref: DataSourceRef | None = None
    missing_columns: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMUploadedCSVInputPlanIssueCode] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class PlanningMMMUploadedCSVInputPlanRequest(ContractBaseModel):
    """Request to build a Planning/MMM uploaded CSV input plan."""

    request_id: str
    adapter_result: PlanningMMMUploadedCSVAdapterResult | None = None
    required_columns_by_role: dict[str, list[str]] = Field(default_factory=dict)
    require_channel_taxonomy: bool = False
    require_budget_constraints: bool = False
    require_calibration_signals: bool = False
    require_model_config: bool = False
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class PlanningMMMUploadedCSVInputPlan(ContractBaseModel):
    """Governed Planning/MMM input plan from uploaded CSV adapter output."""

    plan_id: str
    readiness_tier: PlanningMMMUploadedCSVInputPlanReadinessTier
    requirements: list[PlanningMMMUploadedCSVInputRequirement] = Field(default_factory=list)
    data_source_refs: list[DataSourceRef] = Field(default_factory=list)
    required_inputs_present: list[str] = Field(default_factory=list)
    optional_inputs_present: list[str] = Field(default_factory=list)
    missing_required_inputs: list[str] = Field(default_factory=list)
    missing_optional_inputs: list[str] = Field(default_factory=list)
    deferred_objects: dict[str, str] = Field(default_factory=dict)
    readiness_metadata: dict[str, str | bool] = Field(default_factory=dict)
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMUploadedCSVInputPlanIssueCode] = Field(default_factory=list)


class PlanningMMMUploadedCSVInputPlanResult(ContractBaseModel):
    """Result of building a Planning/MMM uploaded CSV input plan."""

    request_id: str
    status: PlanningMMMUploadedCSVInputPlanStatus
    plan: PlanningMMMUploadedCSVInputPlan | None = None
    issues: list[PlanningMMMUploadedCSVInputPlanIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
