"""MMM planning-answer eligibility gate contracts (metadata only)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.mmm_artifact_governance_use_readiness import (
    MMMArtifactGovernanceUseReadinessResult,
)

RECOMMENDED_NEXT_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_CHECKPOINT_AUDIT_ARTIFACT = (
    "MIP_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_CHECKPOINT_AUDIT_001"
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
        "recommended_budget",
        "budget_recommendation",
    }
)


class MMMPlanningQuestionClass(StrEnum):
    """Class of MMM-backed planning question being evaluated."""

    DESCRIPTIVE_PERFORMANCE = "descriptive_performance"
    DIAGNOSTIC_DRIVER = "diagnostic_driver"
    SCENARIO_COMPARISON = "scenario_comparison"
    SIMULATION_REQUEST = "simulation_request"
    OPTIMIZATION_REQUEST = "optimization_request"
    RECOMMENDATION_REQUEST = "recommendation_request"
    UNKNOWN = "unknown"


class MMMPlanningAnswerMode(StrEnum):
    """Allowed answer mode for an MMM-backed planning question."""

    DESCRIPTIVE = "descriptive"
    DIAGNOSTIC = "diagnostic"
    SCENARIO_COMPARISON = "scenario_comparison"
    SIMULATION_ONLY = "simulation_only"
    RECOMMENDATION_ELIGIBLE = "recommendation_eligible"
    BLOCKED = "blocked"
    DEFERRED = "deferred"


class MMMPlanningAnswerEligibilityStatus(StrEnum):
    """Outcome of MMM planning-answer eligibility evaluation."""

    ANSWER_ELIGIBLE = "answer_eligible"
    ANSWER_ELIGIBLE_WITH_CAVEATS = "answer_eligible_with_caveats"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    SCENARIO_ONLY = "scenario_only"
    SIMULATION_ONLY = "simulation_only"
    RECOMMENDATION_REQUIRES_GATES = "recommendation_requires_gates"
    BLOCKED = "blocked"
    DEFERRED = "deferred"
    UNKNOWN = "unknown"


class MMMPlanningAnswerEligibilityIssueCode(StrEnum):
    """Typed issue codes for MMM planning-answer eligibility."""

    QUESTION_CLASS_PRESENT = "question_class_present"
    QUESTION_CLASS_UNKNOWN = "question_class_unknown"
    ARTIFACT_USE_READINESS_PRESENT = "artifact_use_readiness_present"
    ARTIFACT_USE_READINESS_MISSING = "artifact_use_readiness_missing"
    ARTIFACT_PLANNING_READY = "artifact_planning_ready"
    ARTIFACT_DIAGNOSTIC_ONLY = "artifact_diagnostic_only"
    ARTIFACT_NOT_PLANNING_READY = "artifact_not_planning_ready"
    TRUST_REVIEW_ROUTE_AVAILABLE = "trust_review_route_available"
    TRUST_REVIEW_ROUTE_MISSING = "trust_review_route_missing"
    DECISION_SURFACE_REVIEW_ROUTE_AVAILABLE = "decision_surface_review_route_available"
    DECISION_SURFACE_REVIEW_ROUTE_MISSING = "decision_surface_review_route_missing"
    RECOMMENDATION_GATE_PRESENT = "recommendation_gate_present"
    RECOMMENDATION_GATE_MISSING = "recommendation_gate_missing"
    RECOMMENDATION_BLOCKED_PENDING_GATES = "recommendation_blocked_pending_gates"
    RECOMMENDATION_ALLOWED_BY_GATES = "recommendation_allowed_by_gates"
    DESCRIPTIVE_ANSWER_ALLOWED = "descriptive_answer_allowed"
    DIAGNOSTIC_ANSWER_ALLOWED = "diagnostic_answer_allowed"
    SCENARIO_COMPARISON_ALLOWED = "scenario_comparison_allowed"
    SIMULATION_ONLY_ALLOWED = "simulation_only_allowed"
    OPTIMIZATION_REQUIRES_EXTERNAL_RUNTIME_OR_DECISION_SURFACE = (
        "optimization_requires_external_runtime_or_decision_surface"
    )
    RECOMMENDATION_REQUIRES_RECOMMENDATION_CONTRACT = (
        "recommendation_requires_recommendation_contract"
    )
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    CAVEATS_REQUIRED = "caveats_required"
    BLOCKED_BY_ARTIFACT_READINESS = "blocked_by_artifact_readiness"
    BLOCKED_BY_TRUST_GATE = "blocked_by_trust_gate"
    BLOCKED_BY_DECISION_SURFACE_GATE = "blocked_by_decision_surface_gate"
    BLOCKED_BY_RECOMMENDATION_GATE = "blocked_by_recommendation_gate"
    DEFERRED_PENDING_GOVERNANCE_REVIEW = "deferred_pending_governance_review"
    DEFERRED_PENDING_DECISION_SURFACE_REVIEW = "deferred_pending_decision_surface_review"
    DEFERRED_PENDING_RECOMMENDATION_REVIEW = "deferred_pending_recommendation_review"
    LINEAGE_PRESERVED = "lineage_preserved"
    NO_DECISION_SURFACE_CONSTRUCTION = "no_decision_surface_construction"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_TRUST_REPORT_CONSTRUCTION = "no_trust_report_construction"
    NO_RECOMMENDATION_CONTRACT_GENERATION = "no_recommendation_contract_generation"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"  # must not execute optimizer
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"  # must not execute simulator
    NO_BUDGET_ALLOCATION_CALCULATION = "no_budget_allocation_calculation"
    NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION = (
        "no_roi_roas_lift_incrementality_calculation"
    )
    NO_ARTIFACT_LOADING = "no_artifact_loading"
    NO_MODEL_LOADING = "no_model_loading"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_MMM_FITTING = "no_mmm_fitting"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"
    NO_LLM_PROVIDER_BEHAVIOR_CHANGE = "no_llm_provider_behavior_change"


class MMMPlanningAnswerGateReference(ContractBaseModel):
    """Metadata-only reference to an existing DecisionSurface/Trust/Recommendation gate."""

    gate_name: str
    gate_status: str
    passed: bool = False
    required: bool = False
    blocked_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("gate_name", "gate_status")
    @classmethod
    def non_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "gate_name and gate_status cannot be empty"
            raise ValueError(msg)
        return value


class MMMPlanningAnswerEligibilityRequest(ContractBaseModel):
    """Request to evaluate whether an MMM-backed planning question is answerable."""

    request_id: str
    question_class: MMMPlanningQuestionClass = MMMPlanningQuestionClass.UNKNOWN
    question_text: str | None = None
    artifact_use_readiness: MMMArtifactGovernanceUseReadinessResult | None = None
    decision_surface_gate: MMMPlanningAnswerGateReference | None = None
    trust_report_gate: MMMPlanningAnswerGateReference | None = None
    recommendation_gate: MMMPlanningAnswerGateReference | None = None
    require_trust_review_for_planning: bool = True
    require_decision_surface_for_scenario: bool = True
    require_recommendation_gate_for_recommendation: bool = True
    allow_descriptive_without_decision_surface: bool = True
    allow_diagnostic_without_decision_surface: bool = True
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


class MMMPlanningAnswerEligibilityResult(ContractBaseModel):
    """Result of MMM planning-answer eligibility evaluation (metadata only)."""

    request_id: str
    question_class: MMMPlanningQuestionClass
    answer_mode: MMMPlanningAnswerMode
    status: MMMPlanningAnswerEligibilityStatus
    answer_allowed: bool = False
    decision_surface_required: bool = False
    trust_review_required: bool = False
    recommendation_contract_required: bool = False
    human_review_required: bool = False
    artifact_planning_ready: bool = False
    artifact_diagnostic_only: bool = False
    ready_for_decision_surface_review: bool = False
    ready_for_trust_report_review: bool = False
    blocked_reasons: list[str] = Field(default_factory=list)
    deferred_reasons: list[str] = Field(default_factory=list)
    caveats: list[str] = Field(default_factory=list)
    issues: list[MMMPlanningAnswerEligibilityIssueCode] = Field(default_factory=list)
    gate_references: list[MMMPlanningAnswerGateReference] = Field(default_factory=list)
    external_run_id: str | None = None
    model_artifact_id: str | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


FORBIDDEN_MMM_PLANNING_ANSWER_ELIGIBILITY_RESULT_FIELD_NAMES = _FORBIDDEN_RESULT_FIELD_NAMES
