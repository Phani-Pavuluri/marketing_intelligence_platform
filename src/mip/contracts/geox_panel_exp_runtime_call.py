"""GeoX panel_exp runtime-call contracts (Stage 3B — fixture path only)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.geox_fixture_materialization import GeoXFixtureMaterializationResult
from mip.contracts.geox_panel_exp_integration import (
    GeoXPanelExpIntegrationStatus,
    GeoXPanelExpRuntimeReference,
    GeoXPostTestSpendAdapterInputPlan,
)

RECOMMENDED_NEXT_STAGE_3C_ARTIFACT = "MIP_GEOX_READOUT_RESULT_INGESTION_AND_EXPLANATION_001"
CLAIM_AUTHORIZATION_OWNER = "CLAIM_AUTHORIZATION_RUNTIME_001"


class GeoXPanelExpRuntimeCallStatus(StrEnum):
    """Outcome of a fixture-only panel_exp runtime call attempt."""

    READY = "ready"
    CALLED_PANEL_EXP_RUNTIME = "called_panel_exp_runtime"
    BLOCKED_PANEL_EXP_IMPORT_FAILED = "blocked_panel_exp_import_failed"
    BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED = "blocked_materialized_spend_input_required"
    BLOCKED_MATERIALIZED_ASSIGNMENT_INPUT_REQUIRED = (
        "blocked_materialized_assignment_input_required"
    )
    BLOCKED_POST_TEST_SPEND_INPUT_BUILD_FAILED = "blocked_post_test_spend_input_build_failed"
    BLOCKED_PANEL_EXP_RUNTIME_FAILED = "blocked_panel_exp_runtime_failed"
    BLOCKED_TRUSTED_READOUT_HANDOFF_FAILED = "blocked_trusted_readout_spend_handoff_failed"
    BLOCKED_RUNTIME_CALL_NOT_ALLOWED = "blocked_runtime_call_not_allowed"
    BLOCKED_FIXTURE_MATERIALIZATION_REQUIRED = "blocked_fixture_materialization_required"


class GeoXPanelExpRuntimeCallIssueCode(StrEnum):
    """Typed runtime-call issue codes."""

    PANEL_EXP_IMPORT_FAILED = "panel_exp_import_failed"
    MATERIALIZED_SPEND_DF_MISSING = "materialized_spend_df_missing"
    MATERIALIZED_ASSIGNMENT_DF_OR_MAPPING_MISSING = (
        "materialized_assignment_df_or_mapping_missing"
    )
    POST_TEST_SPEND_INPUT_BUILD_FAILED = "post_test_spend_input_build_failed"
    PANEL_EXP_RUNTIME_EXCEPTION = "panel_exp_runtime_exception"
    TRUSTED_READOUT_HANDOFF_EXCEPTION = "trusted_readout_handoff_exception"
    RUNTIME_CALL_NOT_ALLOWED = "runtime_call_not_allowed"
    FIXTURE_ONLY_RUNTIME_CALL = "fixture_only_runtime_call"
    CLAIM_AUTHORIZATION_DELEGATED = "claim_authorization_delegated"
    ROI_ROAS_NOT_COMPUTED_IN_MIP = "roi_roas_not_computed_in_mip"
    SPEND_DELTA_PACKAGE_COMPUTED = "spend_delta_package_computed"


class GeoXPanelExpRuntimeCallMode(StrEnum):
    """Allowed runtime-call execution modes."""

    FIXTURE_ONLY = "fixture_only"
    DISABLED = "disabled"


class GeoXPostTestSpendEvidenceArtifact(ContractBaseModel):
    """MIP envelope for package PostTestSpendEvidence (package output preserved)."""

    artifact_id: str
    experiment_id: str
    source_dataset_ref: str | None = None
    source_lineage: dict[str, str] = Field(default_factory=dict)
    readiness_status: str
    blocking_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    package_output_summary: dict[str, str | float | int | bool | None] = Field(
        default_factory=dict
    )
    package_runtime_reference: GeoXPanelExpRuntimeReference = Field(
        default_factory=GeoXPanelExpRuntimeReference
    )
    claim_authorization_owner: str = CLAIM_AUTHORIZATION_OWNER


class GeoXTrustedReadoutSpendHandoffArtifact(ContractBaseModel):
    """MIP envelope for package trusted readout spend handoff."""

    artifact_id: str
    experiment_id: str
    spend_readiness_summary: dict[str, str | bool] = Field(default_factory=dict)
    blocked_efficiency_metrics: list[str] = Field(default_factory=list)
    spend_lineage: dict[str, str] = Field(default_factory=dict)
    spend_warnings: list[str] = Field(default_factory=list)
    package_handoff_summary: dict[str, str] = Field(default_factory=dict)
    claim_authorization_owner: str = CLAIM_AUTHORIZATION_OWNER


class GeoXPanelExpRuntimeCallRequest(ContractBaseModel):
    """Request to call panel_exp post-test spend runtime on fixture materialization."""

    request_id: str
    adapter_input_plan: GeoXPostTestSpendAdapterInputPlan
    fixture_materialization_result: GeoXFixtureMaterializationResult | None = None
    call_mode: GeoXPanelExpRuntimeCallMode = GeoXPanelExpRuntimeCallMode.FIXTURE_ONLY
    allow_runtime_call: bool = False
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXPanelExpRuntimeCallResult(ContractBaseModel):
    """Fixture-only panel_exp runtime call result."""

    request_id: str
    status: GeoXPanelExpRuntimeCallStatus
    runtime_called: bool = False
    post_test_spend_evidence_artifact: GeoXPostTestSpendEvidenceArtifact | None = None
    trusted_readout_spend_handoff_artifact: GeoXTrustedReadoutSpendHandoffArtifact | None = None
    issues: list[GeoXPanelExpRuntimeCallIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def runtime_called_consistent_with_status(self) -> GeoXPanelExpRuntimeCallResult:
        if self.status == GeoXPanelExpRuntimeCallStatus.CALLED_PANEL_EXP_RUNTIME:
            if not self.runtime_called:
                msg = "runtime_called must be true when status is CALLED_PANEL_EXP_RUNTIME"
                raise ValueError(msg)
        elif self.runtime_called:
            msg = "runtime_called must remain false unless panel_exp runtime succeeded"
            raise ValueError(msg)
        return self


_PLAN_READY_STATUSES = frozenset(
    {
        GeoXPanelExpIntegrationStatus.READY_TO_BUILD_POST_TEST_SPEND_INPUT,
        GeoXPanelExpIntegrationStatus.READY_TO_CALL_GEOX_POST_TEST_SPEND_RUNTIME,
    }
)
