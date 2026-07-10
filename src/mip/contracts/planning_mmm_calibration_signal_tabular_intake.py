"""Planning/MMM calibration-signal tabular intake contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.tabular_source_reference import (
    TabularSourceInspectionResult,
    TabularSourceReference,
    TabularSourceType,
)

RECOMMENDED_NEXT_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AUDIT_ARTIFACT = (
    "MIP_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AUDIT_FROM_TABULAR_INTAKE_001"
)
RECOMMENDED_NEXT_GEOX_READOUT_RESULT_ROUTING_FROM_TABULAR_SOURCE_ARTIFACT = (
    "MIP_GEOX_READOUT_RESULT_ROUTING_FROM_TABULAR_SOURCE_001"
)

DEFAULT_REQUIRED_CALIBRATION_COLUMNS = (
    "channel",
    "metric",
    "estimand",
    "lift",
    "standard_error",
    "start_date",
    "end_date",
)
DEFAULT_OPTIONAL_CALIBRATION_COLUMNS = (
    "lower_bound",
    "upper_bound",
    "geo_scope",
    "evidence_source",
    "freshness_date",
)


class PlanningMMMCalibrationSignalTabularIntakeStatus(StrEnum):
    """Outcome of calibration-signal tabular intake for Planning/MMM."""

    INTAKE_READY = "intake_ready"
    INTAKE_READY_WITH_WARNINGS = "intake_ready_with_warnings"
    BLOCKED_MISSING_TABULAR_SOURCE_RESULT = "blocked_missing_tabular_source_result"
    BLOCKED_TABULAR_SOURCE_NOT_READY = "blocked_tabular_source_not_ready"
    BLOCKED_MISSING_CALIBRATION_SIGNAL_SOURCE = "blocked_missing_calibration_signal_source"
    BLOCKED_DUPLICATE_CALIBRATION_SIGNAL_SOURCE = "blocked_duplicate_calibration_signal_source"
    BLOCKED_MISSING_REQUIRED_COLUMNS = "blocked_missing_required_columns"
    BLOCKED_CALIBRATION_SIGNAL_CONTRACT_UNAVAILABLE = (
        "blocked_calibration_signal_contract_unavailable"
    )
    DIAGNOSTIC_ONLY = "diagnostic_only"


class PlanningMMMCalibrationSignalConstructionMode(StrEnum):
    """How closely tabular intake maps to CalibrationSignal construction."""

    METADATA_ONLY = "metadata_only"
    CALIBRATION_SIGNAL_CONSTRUCTION_READY = "calibration_signal_construction_ready"
    CALIBRATION_SIGNAL_CONSTRUCTION_DEFERRED = "calibration_signal_construction_deferred"
    DIAGNOSTIC_ONLY = "diagnostic_only"


class PlanningMMMCalibrationSignalColumnRole(StrEnum):
    """Schema column roles for calibration-signal tabular intake."""

    SOURCE_ID = "source_id"
    CHANNEL = "channel"
    METRIC = "metric"
    ESTIMAND = "estimand"
    LIFT = "lift"
    STANDARD_ERROR = "standard_error"
    LOWER_BOUND = "lower_bound"
    UPPER_BOUND = "upper_bound"
    START_DATE = "start_date"
    END_DATE = "end_date"
    GEO_SCOPE = "geo_scope"
    EVIDENCE_SOURCE = "evidence_source"
    FRESHNESS_DATE = "freshness_date"
    UNKNOWN = "unknown"


class PlanningMMMCalibrationSignalTabularIntakeIssueCode(StrEnum):
    """Typed Planning/MMM calibration-signal tabular intake issue codes."""

    MISSING_TABULAR_SOURCE_RESULT = "missing_tabular_source_result"
    TABULAR_SOURCE_NOT_READY = "tabular_source_not_ready"
    MISSING_CALIBRATION_SIGNAL_SOURCE = "missing_calibration_signal_source"
    DUPLICATE_CALIBRATION_SIGNAL_SOURCE = "duplicate_calibration_signal_source"
    MISSING_REQUIRED_COLUMNS = "missing_required_columns"
    OPTIONAL_COLUMNS_MISSING = "optional_columns_missing"
    CALIBRATION_SIGNAL_METADATA_COMPATIBLE = "calibration_signal_metadata_compatible"
    CALIBRATION_SIGNAL_CONSTRUCTION_READY = "calibration_signal_construction_ready"
    CALIBRATION_SIGNAL_CONSTRUCTION_DEFERRED = "calibration_signal_construction_deferred"
    CALIBRATION_SIGNAL_CONTRACT_UNAVAILABLE = "calibration_signal_contract_unavailable"
    TABULAR_SOURCE_SCHEMA_USED = "tabular_source_schema_used"
    TABULAR_SOURCE_REFERENCE_PRESERVED = "tabular_source_reference_preserved"
    DATA_SOURCE_REF_PRESERVED = "data_source_ref_preserved"
    LINEAGE_PRESERVED = "lineage_preserved"
    DEFERRED_MAPPING_CREATED = "deferred_mapping_created"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_BAYESIAN_FITTING = "no_bayesian_fitting"
    NO_PRIOR_APPLICATION = "no_prior_application"
    NO_LIKELIHOOD_CONSTRUCTION = "no_likelihood_construction"
    NO_POSTERIOR_CALCULATION = "no_posterior_calculation"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"


class PlanningMMMCalibrationSignalColumnMapping(ContractBaseModel):
    """Column role mapping for calibration-signal tabular intake."""

    column_name: str = ""
    normalized_column_name: str = ""
    column_role: PlanningMMMCalibrationSignalColumnRole
    required: bool = False
    present: bool = False
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMCalibrationSignalTabularIntakeIssueCode] = Field(
        default_factory=list
    )


class PlanningMMMCalibrationSignalTabularSource(ContractBaseModel):
    """Calibration-signal tabular source intake metadata."""

    source_id: str
    source_type: TabularSourceType
    source_name: str = ""
    data_source_ref: DataSourceRef | None = None
    tabular_source_reference: TabularSourceReference | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    schema_columns: list[str] = Field(default_factory=list)
    normalized_columns: list[str] = Field(default_factory=list)
    column_mappings: list[PlanningMMMCalibrationSignalColumnMapping] = Field(
        default_factory=list
    )
    missing_required_columns: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMCalibrationSignalTabularIntakeIssueCode] = Field(
        default_factory=list
    )


class PlanningMMMCalibrationSignalDeferredMapping(ContractBaseModel):
    """Deferred calibration-signal mapping from tabular intake metadata."""

    mapping_id: str
    source_id: str
    construction_mode: PlanningMMMCalibrationSignalConstructionMode
    metadata_compatible: bool = False
    calibration_signal_contract_available: bool = False
    full_construction_deferred_reason: str = ""
    compatible_fields: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)
    deferred_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMCalibrationSignalTabularIntakeIssueCode] = Field(
        default_factory=list
    )


class PlanningMMMCalibrationSignalTabularIntakeRequest(ContractBaseModel):
    """Request to intake calibration signals from generic tabular source inspection."""

    request_id: str
    tabular_source_result: TabularSourceInspectionResult | None = None
    explicit_calibration_source_ids: list[str] = Field(default_factory=list)
    required_columns: list[str] = Field(
        default_factory=lambda: list(DEFAULT_REQUIRED_CALIBRATION_COLUMNS)
    )
    optional_columns: list[str] = Field(
        default_factory=lambda: list(DEFAULT_OPTIONAL_CALIBRATION_COLUMNS)
    )
    column_role_aliases: dict[str, list[str]] = Field(default_factory=dict)
    require_full_calibration_signal_construction: bool = False
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class PlanningMMMCalibrationSignalTabularIntakeEnvelope(ContractBaseModel):
    """Metadata-only calibration-signal intake envelope."""

    envelope_id: str
    status: PlanningMMMCalibrationSignalTabularIntakeStatus
    construction_mode: PlanningMMMCalibrationSignalConstructionMode
    calibration_signal_sources: list[PlanningMMMCalibrationSignalTabularSource] = Field(
        default_factory=list
    )
    deferred_mappings: list[PlanningMMMCalibrationSignalDeferredMapping] = Field(
        default_factory=list
    )
    data_source_refs: list[DataSourceRef] = Field(default_factory=list)
    tabular_source_references: list[TabularSourceReference] = Field(default_factory=list)
    missing_required_columns: list[str] = Field(default_factory=list)
    optional_columns_missing: list[str] = Field(default_factory=list)
    readiness_metadata: dict[str, str | bool] = Field(default_factory=dict)
    execution_allowed: dict[str, bool] = Field(default_factory=dict)
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMCalibrationSignalTabularIntakeIssueCode] = Field(
        default_factory=list
    )


class PlanningMMMCalibrationSignalTabularIntakeResult(ContractBaseModel):
    """Result of calibration-signal tabular intake for Planning/MMM."""

    request_id: str
    status: PlanningMMMCalibrationSignalTabularIntakeStatus
    envelope: PlanningMMMCalibrationSignalTabularIntakeEnvelope | None = None
    issues: list[PlanningMMMCalibrationSignalTabularIntakeIssueCode] = Field(
        default_factory=list
    )
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
