"""MMM runtime adapter request/response contracts (metadata only)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.planning_mmm_trusted_input_model_run_eligibility import (
    PlanningMMMModelRunEligibilityResult,
)

RECOMMENDED_NEXT_MMM_RUNTIME_RESULT_INGESTION_AND_DIAGNOSTICS_AUDIT_ARTIFACT = (
    "MIP_MMM_RUNTIME_RESULT_INGESTION_AND_DIAGNOSTICS_AUDIT_001"
)

_FORBIDDEN_RESULT_FIELD_NAMES = frozenset(
    {
        "spend_delta",
        "delta_mu",
        "roi",
        "roas",
        "lift",
        "incrementality",
        "optimal_budget",
        "marginal_roi",
        "recommendation",
        "budget_recommendation",
    }
)

DEFAULT_ADAPTER_PLACEHOLDER_REFERENCE = "mip.adapters.mmm:MMMAdapterOutputPlaceholder"
DEFAULT_GOVERNANCE_ADAPTER_REFERENCE = "mip.adapters.governance:adapter_output_to_decision_surface"


class MMMRuntimeCallStatus(StrEnum):
    """Outcome of MMM runtime adapter preparation or recording."""

    READY_TO_CALL_EXTERNAL_RUNTIME = "ready_to_call_external_runtime"
    NOT_CALLED_EXISTING_MODEL_SELECTED = "not_called_existing_model_selected"
    BLOCKED_BY_ELIGIBILITY = "blocked_by_eligibility"
    BLOCKED_MISSING_TRUSTED_INPUT_PACKAGE = "blocked_missing_trusted_input_package"
    BLOCKED_MISSING_MODEL_CONFIG = "blocked_missing_model_config"
    DEFERRED = "deferred"
    EXTERNAL_RUNTIME_CALL_RECORDED = "external_runtime_call_recorded"
    EXTERNAL_RUNTIME_FAILED = "external_runtime_failed"


class MMMRuntimeCallDecision(StrEnum):
    """High-level MMM runtime adapter decision."""

    PREPARE_EXTERNAL_NEW_MODEL_RUN = "prepare_external_new_model_run"
    PREPARE_EXTERNAL_MODEL_REFRESH = "prepare_external_model_refresh"
    USE_EXISTING_MODEL_NO_RUNTIME_CALL = "use_existing_model_no_runtime_call"
    BLOCK_RUNTIME_CALL = "block_runtime_call"
    DEFER_RUNTIME_CALL = "defer_runtime_call"
    RECORD_EXTERNAL_RUNTIME_RESULT = "record_external_runtime_result"


class MMMRuntimeEngineKind(StrEnum):
    """Declared external MMM engine family."""

    EXTERNAL_MMM_ENGINE = "external_mmm_engine"
    EXTERNAL_BAYESIAN_MMM_ENGINE = "external_bayesian_mmm_engine"
    EXTERNAL_RIDGE_MMM_ENGINE = "external_ridge_mmm_engine"
    EXTERNAL_SANDBOX_MMM_ENGINE = "external_sandbox_mmm_engine"
    UNKNOWN = "unknown"


class MMMRuntimeCallIssueCode(StrEnum):
    """Typed issue codes for MMM runtime adapter handoff."""

    ELIGIBILITY_RESULT_PRESENT = "eligibility_result_present"
    ELIGIBILITY_RESULT_MISSING = "eligibility_result_missing"
    TRUSTED_INPUT_PACKAGE_PRESENT = "trusted_input_package_present"
    TRUSTED_INPUT_PACKAGE_MISSING = "trusted_input_package_missing"
    ELIGIBILITY_USE_EXISTING_MODEL = "eligibility_use_existing_model"
    ELIGIBILITY_REQUEST_MODEL_REFRESH = "eligibility_request_model_refresh"
    ELIGIBILITY_REQUEST_NEW_MODEL_RUN = "eligibility_request_new_model_run"
    ELIGIBILITY_BLOCKED = "eligibility_blocked"
    ELIGIBILITY_DEFERRED = "eligibility_deferred"
    MODEL_CONFIG_REFERENCE_PRESENT = "model_config_reference_present"
    MODEL_CONFIG_REFERENCE_MISSING = "model_config_reference_missing"
    EXTERNAL_RUNTIME_REFERENCE_CREATED = "external_runtime_reference_created"
    RUNTIME_REQUEST_CREATED = "runtime_request_created"
    RUNTIME_NOT_CALLED = "runtime_not_called"
    RUNTIME_STATUS_RECORDED = "runtime_status_recorded"
    ADAPTER_PLACEHOLDER_REFERENCE_PRESERVED = "adapter_placeholder_reference_preserved"
    GOVERNANCE_ADAPTER_REFERENCE_PRESERVED = "governance_adapter_reference_preserved"
    TRUSTED_INPUT_REFERENCE_PRESERVED = "trusted_input_reference_preserved"
    EXISTING_MODEL_REFERENCE_PRESERVED = "existing_model_reference_preserved"
    LINEAGE_PRESERVED = "lineage_preserved"
    FAILURE_PACKET_CREATED = "failure_packet_created"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_MODEL_ARTIFACT_LOADING = "no_model_artifact_loading"
    NO_MMM_FITTING = "no_mmm_fitting"
    NO_BAYESIAN_FITTING = "no_bayesian_fitting"
    NO_PRIOR_APPLICATION = "no_prior_application"
    NO_LIKELIHOOD_CONSTRUCTION = "no_likelihood_construction"
    NO_POSTERIOR_CALCULATION = "no_posterior_calculation"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_TRUST_REPORT_CONSTRUCTION = "no_trust_report_construction"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"


class MMMRuntimeReference(ContractBaseModel):
    """Metadata-only reference to an external MMM runtime system."""

    runtime_id: str
    runtime_kind: MMMRuntimeEngineKind = MMMRuntimeEngineKind.UNKNOWN
    runtime_name: str = "external_mmm_runtime"
    runtime_version: str = "unspecified"
    environment: str = "external"
    owner: str = "mmm_engine_operator"
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("runtime_id")
    @classmethod
    def runtime_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "runtime_id cannot be empty"
            raise ValueError(msg)
        return value


class MMMRuntimeFailurePacket(ContractBaseModel):
    """Structured metadata-only failure packet for blocked/failed runtime handoff."""

    failure_id: str
    request_id: str
    status: MMMRuntimeCallStatus
    error_code: str
    message: str
    retryable: bool = False
    blocked_reasons: list[str] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("failure_id", "request_id", "error_code", "message")
    @classmethod
    def non_empty_strings(cls, value: str) -> str:
        if not value.strip():
            msg = "failure packet string fields cannot be empty"
            raise ValueError(msg)
        return value


class MMMRuntimeArtifactHandoff(ContractBaseModel):
    """Metadata-only artifact URI handoff from an external MMM runtime."""

    handoff_id: str
    request_id: str
    external_run_id: str
    artifact_uris: list[str] = Field(default_factory=list)
    manifest_uri: str | None = None
    diagnostics_uri: str | None = None
    model_artifact_uri: str | None = None
    runtime_logs_uri: str | None = None
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("handoff_id", "request_id", "external_run_id")
    @classmethod
    def non_empty_ids(cls, value: str) -> str:
        if not value.strip():
            msg = "artifact handoff id fields cannot be empty"
            raise ValueError(msg)
        return value


class MMMRuntimeCallRequest(ContractBaseModel):
    """Request to prepare or record an external MMM runtime handoff."""

    request_id: str
    eligibility_result: PlanningMMMModelRunEligibilityResult | None = None
    runtime_reference: MMMRuntimeReference | None = None
    requested_run_type: str = "blocked"
    model_config_id: str | None = None
    trusted_input_package_id: str | None = None
    adapter_placeholder_reference: str = DEFAULT_ADAPTER_PLACEHOLDER_REFERENCE
    governance_adapter_reference: str = DEFAULT_GOVERNANCE_ADAPTER_REFERENCE
    external_run_id: str | None = None
    supplied_artifact_handoff: MMMRuntimeArtifactHandoff | None = None
    supplied_failure_packet: MMMRuntimeFailurePacket | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


class MMMRuntimeCallResult(ContractBaseModel):
    """Result of MMM runtime adapter preparation or external result recording."""

    request_id: str
    status: MMMRuntimeCallStatus
    decision: MMMRuntimeCallDecision
    runtime_reference: MMMRuntimeReference | None = None
    runtime_called: bool = False
    external_run_id: str | None = None
    artifact_handoff: MMMRuntimeArtifactHandoff | None = None
    failure_packet: MMMRuntimeFailurePacket | None = None
    blocked_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    issues: list[MMMRuntimeCallIssueCode] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def runtime_called_consistent_with_status(self) -> MMMRuntimeCallResult:
        if self.status == MMMRuntimeCallStatus.EXTERNAL_RUNTIME_CALL_RECORDED:
            if not self.runtime_called:
                msg = "runtime_called must be true when status is EXTERNAL_RUNTIME_CALL_RECORDED"
                raise ValueError(msg)
        elif self.runtime_called and self.status not in {
            MMMRuntimeCallStatus.EXTERNAL_RUNTIME_CALL_RECORDED,
            MMMRuntimeCallStatus.EXTERNAL_RUNTIME_FAILED,
        }:
            msg = "runtime_called must remain false unless external runtime result was recorded"
            raise ValueError(msg)
        return self


FORBIDDEN_MMM_RUNTIME_CALL_RESULT_FIELD_NAMES = _FORBIDDEN_RESULT_FIELD_NAMES
