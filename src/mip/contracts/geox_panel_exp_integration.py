"""GeoX panel_exp integration boundary contracts (Stage 3A — adapter plan only)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.geox_readout_input_resolution import GeoXReadoutInputHandoff

RECOMMENDED_NEXT_STAGE_3B_ARTIFACT = "MIP_GEOX_READOUT_PANEL_EXP_RUNTIME_CALL_001B"

GEOX_PACKAGE_MAIN_HEAD = "9fe4b92"
GEOX_RUNTIME_COMMIT = "b400912"
GEOX_INTEGRATION_COMMIT = "9039fda"
GEOX_RUNTIME_MODULE_PATH = (
    "panel_exp/validation/post_test_spend_readiness_adapter_runtime_001.py"
)
GEOX_INTEGRATION_MODULE_PATH = (
    "panel_exp/validation/trusted_readout_spend_readiness_integration_runtime_001.py"
)
GEOX_PRIMARY_CALLABLE = "build_post_test_spend_evidence"
GEOX_HANDOFF_HELPER_CALLABLE = "build_trusted_readout_spend_handoff"
GEOX_INTEGRATION_CALLABLES = (
    "integrate_spend_readiness_into_trusted_readout",
    "generate_trusted_readout_report_with_spend_readiness",
)
GEOX_INPUT_MODEL = "PostTestSpendInput"
GEOX_OUTPUT_MODEL = "PostTestSpendEvidence"
GEOX_READINESS_STATUS_VALUES = (
    "ready",
    "blocked_missing_spend",
    "blocked_missing_assignment",
    "blocked_mapping_confirmation",
    "blocked_missing_dates",
    "blocked_missing_baseline",
)


class GeoXPanelExpIntegrationStatus(StrEnum):
    """MIP-side panel_exp integration readiness status."""

    READY_TO_BUILD_POST_TEST_SPEND_INPUT = "ready_to_build_post_test_spend_input"
    READY_TO_CALL_GEOX_POST_TEST_SPEND_RUNTIME = (
        "ready_to_call_geox_post_test_spend_runtime"
    )
    BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED = (
        "blocked_materialized_spend_input_required"
    )
    BLOCKED_MATERIALIZED_ASSIGNMENT_INPUT_REQUIRED = (
        "blocked_materialized_assignment_input_required"
    )
    BLOCKED_MISSING_CONFIRMED_SPEND_MAPPING = "blocked_missing_confirmed_spend_mapping"
    BLOCKED_MISSING_CONFIRMED_ASSIGNMENT_MAPPING = (
        "blocked_missing_confirmed_assignment_mapping"
    )
    BLOCKED_MISSING_POST_PERIOD_DATES = "blocked_missing_post_period_dates"
    BLOCKED_MISSING_EXPERIMENT_TYPE = "blocked_missing_experiment_type"
    BLOCKED_MISSING_BASELINE_FOR_EXPERIMENT_TYPE = (
        "blocked_missing_baseline_for_experiment_type"
    )
    BLOCKED_NO_SPEND_READINESS_REQUESTED = "blocked_no_spend_readiness_requested"
    BLOCKED_PANEL_EXP_RUNTIME_NOT_CONFIGURED = "blocked_panel_exp_runtime_not_configured"
    BLOCKED_PANEL_EXP_IMPORT_NOT_ALLOWED = "blocked_panel_exp_import_not_allowed"


class GeoXPanelExpIntegrationIssueCode(StrEnum):
    """Typed integration boundary issue codes."""

    MATERIALIZED_SPEND_DF_MISSING = "materialized_spend_df_missing"
    MATERIALIZED_ASSIGNMENT_DF_OR_MAPPING_MISSING = (
        "materialized_assignment_df_or_mapping_missing"
    )
    SPEND_DATE_COLUMN_MISSING = "spend_date_column_missing"
    SPEND_GEO_COLUMN_MISSING = "spend_geo_column_missing"
    SPEND_AMOUNT_COLUMN_MISSING = "spend_amount_column_missing"
    ASSIGNMENT_JOIN_KEYS_MISSING = "assignment_join_keys_missing"
    POST_PERIOD_START_MISSING = "post_period_start_missing"
    POST_PERIOD_END_MISSING = "post_period_end_missing"
    EXPERIMENT_TYPE_MISSING = "experiment_type_missing"
    BASELINE_OR_COUNTERFACTUAL_SPEND_MISSING = "baseline_or_counterfactual_spend_missing"
    VALUE_MAPPING_NOT_CONSUMED_BY_SPEND_RUNTIME = (
        "value_mapping_not_consumed_by_spend_runtime"
    )
    PANEL_EXP_RUNTIME_REQUIRES_MATERIALIZED_INPUTS = (
        "panel_exp_runtime_requires_materialized_inputs"
    )
    PANEL_EXP_RUNTIME_NOT_CALLED_IN_STAGE_3A = "panel_exp_runtime_not_called_in_stage_3a"
    CLAIM_AUTHORIZATION_DELEGATED = "claim_authorization_delegated"


class GeoXPostTestExperimentType(StrEnum):
    """GeoX post-test experiment taxonomy for spend adapter planning."""

    GO_DARK = "go_dark"
    HEAVY_UP = "heavy_up"
    HOLDOUT = "holdout"
    DOSAGE = "dosage"
    REALLOCATION = "reallocation"
    UNKNOWN = "unknown"


class GeoXPanelExpRuntimeCallable(StrEnum):
    """panel_exp runtime callables recorded for Stage 3B targeting."""

    BUILD_POST_TEST_SPEND_EVIDENCE = "build_post_test_spend_evidence"
    BUILD_TRUSTED_READOUT_SPEND_HANDOFF = "build_trusted_readout_spend_handoff"
    INTEGRATE_SPEND_READINESS_INTO_TRUSTED_READOUT = (
        "integrate_spend_readiness_into_trusted_readout"
    )
    GENERATE_TRUSTED_READOUT_REPORT_WITH_SPEND_READINESS = (
        "generate_trusted_readout_report_with_spend_readiness"
    )


class GeoXMaterializedInputAvailability(ContractBaseModel):
    """Materialized package-side input indicators — refs/booleans only."""

    has_materialized_spend_df: bool = False
    has_materialized_assignment_df: bool = False
    has_assignment_mapping: bool = False
    materialized_spend_ref_optional: str | None = None
    materialized_assignment_ref_optional: str | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXPostTestSpendInputRequirements(ContractBaseModel):
    """Required fields for package PostTestSpendInput (documented, not instantiated)."""

    experiment_id_required: bool = True
    spend_df_required: bool = True
    assignment_df_or_mapping_required: bool = True
    spend_date_column_required: bool = True
    spend_geo_column_required: bool = True
    spend_amount_column_required: bool = True
    post_period_start_required: bool = True
    post_period_end_required: bool = True
    experiment_type_required: bool = True
    assignment_join_keys_required: bool = True
    baseline_or_counterfactual_required: bool = False
    required_fields: list[str] = Field(default_factory=list)
    optional_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class GeoXPanelExpRuntimeReference(ContractBaseModel):
    """Recorded GeoX / panel_exp runtime API handoff metadata."""

    package_main_head: str = GEOX_PACKAGE_MAIN_HEAD
    runtime_commit: str = GEOX_RUNTIME_COMMIT
    integration_commit: str = GEOX_INTEGRATION_COMMIT
    runtime_module_path: str = GEOX_RUNTIME_MODULE_PATH
    primary_callable: str = GEOX_PRIMARY_CALLABLE
    handoff_helper_callable: str = GEOX_HANDOFF_HELPER_CALLABLE
    integration_module_path: str = GEOX_INTEGRATION_MODULE_PATH
    integration_callables: list[str] = Field(
        default_factory=lambda: list(GEOX_INTEGRATION_CALLABLES)
    )
    input_model: str = GEOX_INPUT_MODEL
    output_model: str = GEOX_OUTPUT_MODEL
    readiness_status_values: list[str] = Field(
        default_factory=lambda: list(GEOX_READINESS_STATUS_VALUES)
    )
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXPostTestSpendAdapterInputPlan(ContractBaseModel):
    """Adapter plan from MIP handoff to package PostTestSpendInput requirements."""

    request_id: str
    experiment_id: str
    integration_status: GeoXPanelExpIntegrationStatus
    runtime_reference: GeoXPanelExpRuntimeReference = Field(
        default_factory=GeoXPanelExpRuntimeReference
    )
    handoff_ref_summary: dict[str, str] = Field(default_factory=dict)
    materialized_input_availability: GeoXMaterializedInputAvailability
    input_requirements: GeoXPostTestSpendInputRequirements = Field(
        default_factory=GeoXPostTestSpendInputRequirements
    )
    required_panel_exp_fields: list[str] = Field(default_factory=list)
    mapped_handoff_fields: dict[str, str] = Field(default_factory=dict)
    missing_materialized_inputs: list[str] = Field(default_factory=list)
    missing_required_mappings: list[str] = Field(default_factory=list)
    missing_required_metadata: list[str] = Field(default_factory=list)
    experiment_type: GeoXPostTestExperimentType = GeoXPostTestExperimentType.UNKNOWN
    baseline_requirements: list[str] = Field(default_factory=list)
    source_lineage: dict[str, str] = Field(default_factory=dict)
    issues: list[GeoXPanelExpIntegrationIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    ready_to_call_runtime: bool = False


class GeoXPanelExpIntegrationRequest(ContractBaseModel):
    """Request to evaluate MIP handoff against panel_exp materialization boundary."""

    request_id: str
    handoff: GeoXReadoutInputHandoff
    materialized_input_availability: GeoXMaterializedInputAvailability = Field(
        default_factory=GeoXMaterializedInputAvailability
    )
    allow_panel_exp_import: bool = False
    allow_panel_exp_runtime_call: bool = False
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXPanelExpIntegrationResult(ContractBaseModel):
    """Stage 3A integration boundary result — no runtime execution."""

    request_id: str
    integration_status: GeoXPanelExpIntegrationStatus
    adapter_input_plan: GeoXPostTestSpendAdapterInputPlan
    runtime_called: bool = False
    post_test_spend_evidence_ref_optional: str | None = None
    trusted_readout_spend_handoff_ref_optional: str | None = None
    user_messages: list[str] = Field(default_factory=list)
    issues: list[GeoXPanelExpIntegrationIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def runtime_not_called_in_stage_3a(self) -> GeoXPanelExpIntegrationResult:
        if self.runtime_called:
            msg = "runtime_called must remain false in Stage 3A"
            raise ValueError(msg)
        return self
