"""GeoX readout input resolution contracts (Stage 2A — declared refs only)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.deterministic_report import ArtifactReference

PANEL_EXP_TARGET_CONTRACT = "GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001"
PANEL_EXP_EXPECTED_RUNTIME = "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001"


class GeoXReadoutIntent(StrEnum):
    """Classified GeoX readout request intent."""

    READOUT_KPI_ONLY = "readout_kpi_only"
    READOUT_WITH_LIFT = "readout_with_lift"
    READOUT_WITH_COST_PER = "readout_with_cost_per"
    READOUT_WITH_ROAS = "readout_with_roas"
    READOUT_WITH_PROFIT_ROI = "readout_with_profit_roi"
    READOUT_WITH_DECISION_RECOMMENDATION_REQUEST = (
        "readout_with_decision_recommendation_request"
    )
    READOUT_UNCLEAR_METRIC_REQUEST = "readout_unclear_metric_request"


class DatasetSourceType(StrEnum):
    """Declared dataset source type (no runtime parsing in Stage 2A)."""

    UPLOADED_CSV = "uploaded_csv"
    UPLOADED_EXCEL = "uploaded_excel"
    UPLOADED_PARQUET = "uploaded_parquet"
    WAREHOUSE_TABLE = "warehouse_table"
    API_REFERENCE = "api_reference"
    REGISTERED_ARTIFACT = "registered_artifact"
    MANUAL_USER_ENTRY = "manual_user_entry"
    UNKNOWN = "unknown"


class DatasetSemanticType(StrEnum):
    """Semantic classification for declared dataset references."""

    KPI_PANEL = "kpi_panel"
    SPEND_PANEL = "spend_panel"
    ASSIGNMENT_TABLE = "assignment_table"
    EXPERIMENT_METADATA = "experiment_metadata"
    VALUE_MAPPING = "value_mapping"
    MARGIN_MAPPING = "margin_mapping"
    DESIGN_ARTIFACT = "design_artifact"
    UNKNOWN_DATASET = "unknown_dataset"


class MappingInferenceStatus(StrEnum):
    """How a column mapping was established."""

    INFERRED_HIGH_CONFIDENCE = "inferred_high_confidence"
    INFERRED_LOW_CONFIDENCE = "inferred_low_confidence"
    DECLARED_BY_USER = "declared_by_user"
    NOT_INFERRED = "not_inferred"


class MappingConfirmationStatus(StrEnum):
    """User confirmation state for column mappings."""

    USER_CONFIRMED = "user_confirmed"
    USER_REJECTED = "user_rejected"
    CONFIRMATION_REQUIRED = "confirmation_required"
    NOT_REQUIRED = "not_required"
    MISSING = "missing"
    AMBIGUOUS = "ambiguous"


class GeoXReadoutResolutionStatus(StrEnum):
    """MIP resolution outcome before panel_exp handoff."""

    READY_FOR_GEOX_READOUT = "ready_for_geox_readout"
    READY_FOR_KPI_ONLY_READOUT = "ready_for_kpi_only_readout"
    READY_FOR_LIFT_ONLY_READOUT = "ready_for_lift_only_readout"
    READY_FOR_COST_PER_READOUT = "ready_for_cost_per_readout"
    PARTIAL_READOUT_ALLOWED = "partial_readout_allowed"
    BLOCKED_MISSING_KPI_DATA = "blocked_missing_kpi_data"
    BLOCKED_MISSING_EXPERIMENT_METADATA = "blocked_missing_experiment_metadata"
    BLOCKED_MISSING_ASSIGNMENT = "blocked_missing_assignment"
    BLOCKED_MISSING_DATES = "blocked_missing_dates"
    BLOCKED_MISSING_SPEND_FOR_EFFICIENCY = "blocked_missing_spend_for_efficiency"
    BLOCKED_MISSING_VALUE_MAPPING_FOR_ROAS = "blocked_missing_value_mapping_for_roas"
    BLOCKED_MISSING_MARGIN_MAPPING_FOR_PROFIT_ROI = (
        "blocked_missing_margin_mapping_for_profit_roi"
    )
    BLOCKED_MAPPING_CONFIRMATION_REQUIRED = "blocked_mapping_confirmation_required"
    BLOCKED_UNCLEAR_USER_INTENT = "blocked_unclear_user_intent"
    BLOCKED_NO_GEOX_RUNTIME_AVAILABLE = "blocked_no_geox_runtime_available"
    BLOCKED_DECISION_RECOMMENDATION_REQUIRES_DECISION_SURFACE = (
        "blocked_decision_recommendation_requires_decision_surface"
    )


class GeoXMissingInputReason(StrEnum):
    """Typed missing-input reason codes."""

    MISSING_KPI_DATA = "missing_kpi_data"
    MISSING_EXPERIMENT_METADATA = "missing_experiment_metadata"
    MISSING_ASSIGNMENT = "missing_assignment"
    MISSING_DATES = "missing_dates"
    MISSING_SPEND_FOR_EFFICIENCY = "missing_spend_for_efficiency"
    MISSING_VALUE_MAPPING_FOR_ROAS = "missing_value_mapping_for_roas"
    MISSING_MARGIN_MAPPING_FOR_PROFIT_ROI = "missing_margin_mapping_for_profit_roi"
    MAPPING_CONFIRMATION_REQUIRED = "mapping_confirmation_required"
    UNCLEAR_USER_INTENT = "unclear_user_intent"
    NO_GEOX_RUNTIME_AVAILABLE = "no_geox_runtime_available"
    DECISION_RECOMMENDATION_REQUIRES_DECISION_SURFACE = (
        "decision_recommendation_requires_decision_surface"
    )


class DatasetReference(ContractBaseModel):
    """Declared dataset reference — no file parsing in Stage 2A."""

    dataset_ref_id: str
    source_type: DatasetSourceType
    semantic_type: DatasetSemanticType
    source_uri_or_handle: str
    file_name_or_table_name: str
    declared_or_detected_columns: list[str] = Field(default_factory=list)
    classification_confidence: float = Field(ge=0.0, le=1.0)
    user_confirmation_status: MappingConfirmationStatus = MappingConfirmationStatus.NOT_REQUIRED
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class ColumnMappingCandidate(ContractBaseModel):
    """Candidate column binding with inference and confirmation metadata."""

    source_column: str
    target_field: str
    inference_status: MappingInferenceStatus
    confirmation_status: MappingConfirmationStatus
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str = ""


class KPIColumnMapping(ContractBaseModel):
    """KPI panel column bindings."""

    date_week_column: str | None = None
    geo_unit_column: str | None = None
    kpi_metric_column: str | None = None
    kpi_metric_name: str | None = None
    kpi_metric_unit: str | None = None
    kpi_is_revenue_denominator: bool = False
    kpi_is_profit_denominator: bool = False
    confirmation_status: MappingConfirmationStatus = MappingConfirmationStatus.NOT_REQUIRED
    candidates: list[ColumnMappingCandidate] = Field(default_factory=list)


class SpendColumnMapping(ContractBaseModel):
    """Spend panel column bindings."""

    date_week_column: str | None = None
    geo_unit_column: str | None = None
    spend_amount_column: str | None = None
    currency_column: str | None = None
    channel_column: str | None = None
    platform_column: str | None = None
    campaign_column: str | None = None
    treatment_cell_join_key: str | None = None
    confirmation_status: MappingConfirmationStatus = MappingConfirmationStatus.NOT_REQUIRED
    candidates: list[ColumnMappingCandidate] = Field(default_factory=list)


class AssignmentColumnMapping(ContractBaseModel):
    """Treatment/control assignment column bindings."""

    geo_unit_column: str | None = None
    cell_column: str | None = None
    treatment_control_label_column: str | None = None
    experiment_id_column: str | None = None
    confirmation_status: MappingConfirmationStatus = MappingConfirmationStatus.NOT_REQUIRED
    candidates: list[ColumnMappingCandidate] = Field(default_factory=list)


class ValueMapping(ContractBaseModel):
    """Revenue or margin mapping for efficiency readouts."""

    value_per_incremental_kpi: float | None = None
    revenue_mapping_source: str | None = None
    margin_profit_mapping_source: str | None = None
    currency: str | None = None
    value_window: str | None = None
    source_lineage: dict[str, str] = Field(default_factory=dict)
    confirmation_status: MappingConfirmationStatus = MappingConfirmationStatus.NOT_REQUIRED
    candidates: list[ColumnMappingCandidate] = Field(default_factory=list)

    @field_validator("value_per_incremental_kpi")
    @classmethod
    def value_per_kpi_non_negative(cls, value: float | None) -> float | None:
        if value is not None and value < 0:
            msg = "value_per_incremental_kpi cannot be negative"
            raise ValueError(msg)
        return value


class GeoXExperimentMetadataRef(ContractBaseModel):
    """Experiment window and design references."""

    experiment_id: str
    design_artifact_ref: ArtifactReference | None = None
    assignment_artifact_ref: ArtifactReference | None = None
    test_start_date: str | None = None
    test_end_date: str | None = None
    post_period_start: str | None = None
    post_period_end: str | None = None
    pre_period_start: str | None = None
    pre_period_end: str | None = None
    estimator_or_inference_identity: str | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXReadoutInputResolutionRequest(ContractBaseModel):
    """Input to the deterministic GeoX readout resolver (Stage 2A)."""

    request_id: str
    user_request: str = ""
    requested_intent: GeoXReadoutIntent | None = None
    requested_metrics: list[str] = Field(default_factory=list)
    dataset_refs: list[DatasetReference] = Field(default_factory=list)
    kpi_column_mapping: KPIColumnMapping | None = None
    spend_column_mapping: SpendColumnMapping | None = None
    assignment_column_mapping: AssignmentColumnMapping | None = None
    value_mapping: ValueMapping | None = None
    experiment_metadata: GeoXExperimentMetadataRef | None = None
    spend_baseline_definition_optional: str | None = None
    geox_runtime_available: bool = False
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXReadoutInputHandoff(ContractBaseModel):
    """Typed handoff object for panel_exp (built when core inputs exist)."""

    request_id: str
    user_request: str = ""
    readout_intent: GeoXReadoutIntent
    experiment_id: str
    design_artifact_ref: ArtifactReference | None = None
    assignment_artifact_ref: ArtifactReference | None = None
    kpi_dataset_ref: DatasetReference | None = None
    kpi_column_mapping: KPIColumnMapping | None = None
    spend_dataset_ref_optional: DatasetReference | None = None
    spend_column_mapping_optional: SpendColumnMapping | None = None
    spend_baseline_definition_optional: str | None = None
    value_mapping_optional: ValueMapping | None = None
    requested_metrics: list[str] = Field(default_factory=list)
    missing_inputs: list[GeoXMissingInputReason] = Field(default_factory=list)
    mip_resolution_status: GeoXReadoutResolutionStatus
    panel_exp_target_contract: str = PANEL_EXP_TARGET_CONTRACT
    panel_exp_expected_runtime: str = PANEL_EXP_EXPECTED_RUNTIME
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXReadoutInputResolutionResult(ContractBaseModel):
    """Resolver output with status, messages, and optional handoff."""

    request_id: str
    readout_intent: GeoXReadoutIntent
    resolution_status: GeoXReadoutResolutionStatus
    missing_inputs: list[GeoXMissingInputReason] = Field(default_factory=list)
    dataset_refs_used: list[DatasetReference] = Field(default_factory=list)
    mapping_confirmation_required: bool = False
    handoff: GeoXReadoutInputHandoff | None = None
    user_messages: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
