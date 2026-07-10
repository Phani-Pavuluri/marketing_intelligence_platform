"""Planning/MMM trusted input package and model-run eligibility contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.mmm_existing_model_availability import MMMExistingModelAvailabilityResult
from mip.contracts.planning_mmm_calibration_signal_mapping_readiness import (
    PlanningMMMCalibrationSignalMappingReadinessResult,
)
from mip.contracts.planning_mmm_readiness_report_adapter import (
    PlanningMMMReadinessReportAdapterResult,
)

RECOMMENDED_NEXT_MMM_RUNTIME_ADAPTER_CONTRACT_ARTIFACT = "MIP_MMM_RUNTIME_ADAPTER_CONTRACT_001"

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


class PlanningMMMTrustedInputStatus(StrEnum):
    """Trusted input package readiness."""

    TRUSTED_INPUT_READY = "trusted_input_ready"
    TRUSTED_INPUT_READY_WITH_WARNINGS = "trusted_input_ready_with_warnings"
    TRUSTED_INPUT_DIAGNOSTIC_ONLY = "trusted_input_diagnostic_only"
    TRUSTED_INPUT_BLOCKED = "trusted_input_blocked"
    TRUSTED_INPUT_DEFERRED = "trusted_input_deferred"


class PlanningMMMModelRunEligibilityStatus(StrEnum):
    """Model-run eligibility outcome."""

    ELIGIBLE_TO_REQUEST_MODEL_RUN = "eligible_to_request_model_run"
    ELIGIBLE_TO_REQUEST_MODEL_RUN_WITH_WARNINGS = "eligible_to_request_model_run_with_warnings"
    USE_EXISTING_MODEL = "use_existing_model"
    REQUIRES_MODEL_REFRESH = "requires_model_refresh"
    REQUIRES_NEW_MODEL_RUN = "requires_new_model_run"
    BLOCKED_MISSING_REQUIRED_DATA = "blocked_missing_required_data"
    BLOCKED_DATA_READINESS_FAILED = "blocked_data_readiness_failed"
    BLOCKED_CALIBRATION_READINESS_FAILED = "blocked_calibration_readiness_failed"
    BLOCKED_EXISTING_MODEL_DECISION_CONFLICT = "blocked_existing_model_decision_conflict"
    BLOCKED_MISSING_MODEL_CONFIG = "blocked_missing_model_config"
    BLOCKED_GOVERNANCE_REVIEW_REQUIRED = "blocked_governance_review_required"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


class PlanningMMMModelRunEligibilityDecision(StrEnum):
    """High-level model-run decision."""

    USE_EXISTING_MODEL = "use_existing_model"
    REQUEST_MODEL_REFRESH = "request_model_refresh"
    REQUEST_NEW_MODEL_RUN = "request_new_model_run"
    BLOCK = "block"
    DEFER = "defer"


class PlanningMMMModelRunEligibilityIssueCode(StrEnum):
    """Typed issue codes for trusted input and model-run eligibility."""

    DATA_READINESS_PRESENT = "data_readiness_present"
    DATA_READINESS_MISSING = "data_readiness_missing"
    DATA_READINESS_BLOCKED = "data_readiness_blocked"
    HISTORICAL_SPEND_PRESENT = "historical_spend_present"
    HISTORICAL_SPEND_MISSING = "historical_spend_missing"
    HISTORICAL_OUTCOME_PRESENT = "historical_outcome_present"
    HISTORICAL_OUTCOME_MISSING = "historical_outcome_missing"
    CHANNEL_TAXONOMY_PRESENT = "channel_taxonomy_present"
    CHANNEL_TAXONOMY_MISSING = "channel_taxonomy_missing"
    BUDGET_CONSTRAINTS_PRESENT = "budget_constraints_present"
    BUDGET_CONSTRAINTS_MISSING = "budget_constraints_missing"
    MODEL_CONFIG_PRESENT = "model_config_present"
    MODEL_CONFIG_MISSING = "model_config_missing"
    CALIBRATION_READINESS_PRESENT = "calibration_readiness_present"
    CALIBRATION_READINESS_READY = "calibration_readiness_ready"
    CALIBRATION_READINESS_WARNINGS = "calibration_readiness_warnings"
    CALIBRATION_READINESS_DIAGNOSTIC_ONLY = "calibration_readiness_diagnostic_only"
    CALIBRATION_READINESS_BLOCKED = "calibration_readiness_blocked"
    EXISTING_MODEL_AVAILABILITY_PRESENT = "existing_model_availability_present"
    EXISTING_MODEL_USABLE = "existing_model_usable"
    EXISTING_MODEL_REFRESH_REQUIRED = "existing_model_refresh_required"
    EXISTING_MODEL_NOT_USABLE = "existing_model_not_usable"
    NEW_MODEL_RUN_REQUIRED = "new_model_run_required"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    TRUSTED_INPUT_PACKAGE_CREATED = "trusted_input_package_created"
    MODEL_RUN_ELIGIBILITY_EVALUATED = "model_run_eligibility_evaluated"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_MODEL_ARTIFACT_LOADING = "no_model_artifact_loading"
    NO_PRIOR_APPLICATION = "no_prior_application"
    NO_LIKELIHOOD_CONSTRUCTION = "no_likelihood_construction"
    NO_POSTERIOR_CALCULATION = "no_posterior_calculation"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_TRUST_REPORT_CONSTRUCTION = "no_trust_report_construction"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"


class PlanningMMMTrustedInputComponentStatus(ContractBaseModel):
    """Status for one trusted-input component."""

    component_name: str
    present: bool = False
    required: bool = False
    status: str = "unknown"
    warnings: list[str] = Field(default_factory=list)


class PlanningMMMTrustedInputPackage(ContractBaseModel):
    """Metadata-only trusted input package for Planning/MMM model-run decisions."""

    package_id: str
    request_id: str
    data_readiness_request_id: str | None = None
    data_readiness_status: str | None = None
    calibration_readiness_request_id: str | None = None
    calibration_readiness_status: str | None = None
    existing_model_availability_request_id: str | None = None
    existing_model_availability_status: str | None = None
    existing_model_selected_id: str | None = None
    model_config_id: str | None = None
    model_config_present: bool = False
    required_component_statuses: list[PlanningMMMTrustedInputComponentStatus] = Field(
        default_factory=list
    )
    optional_component_statuses: list[PlanningMMMTrustedInputComponentStatus] = Field(
        default_factory=list
    )
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMModelRunEligibilityIssueCode] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class PlanningMMMModelRunEligibilityRequest(ContractBaseModel):
    """Request to evaluate trusted input and model-run eligibility."""

    request_id: str
    data_readiness_result: PlanningMMMReadinessReportAdapterResult | None = None
    calibration_readiness_result: PlanningMMMCalibrationSignalMappingReadinessResult | None = None
    existing_model_availability_result: MMMExistingModelAvailabilityResult | None = None
    model_config_present: bool = False
    model_config_id: str | None = None
    require_calibration_readiness: bool = False
    allow_diagnostic_only_calibration: bool = False
    allow_existing_model_reuse: bool = True
    require_human_review_for_warnings: bool = False
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


class PlanningMMMModelRunEligibilityResult(ContractBaseModel):
    """Result of trusted input and model-run eligibility evaluation."""

    request_id: str
    trusted_input_status: PlanningMMMTrustedInputStatus
    eligibility_status: PlanningMMMModelRunEligibilityStatus
    decision: PlanningMMMModelRunEligibilityDecision
    trusted_input_package: PlanningMMMTrustedInputPackage | None = None
    eligible_to_request_model_run: bool = False
    use_existing_model: bool = False
    requires_model_refresh: bool = False
    requires_new_model_run: bool = False
    human_review_required: bool = False
    blocked_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    issues: list[PlanningMMMModelRunEligibilityIssueCode] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


FORBIDDEN_PLANNING_MMM_MODEL_RUN_ELIGIBILITY_RESULT_FIELD_NAMES = _FORBIDDEN_RESULT_FIELD_NAMES
