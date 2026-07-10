"""MMM planning-answer envelope contracts (metadata only)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.mmm_planning_answer_eligibility import (
    MMMPlanningAnswerEligibilityResult,
    MMMPlanningAnswerGateReference,
    MMMPlanningAnswerMode,
    MMMPlanningQuestionClass,
)

RECOMMENDED_NEXT_MMM_PLANNING_ANSWER_ENVELOPE_CHECKPOINT_AUDIT_ARTIFACT = (
    "MIP_MMM_PLANNING_ANSWER_ENVELOPE_CHECKPOINT_AUDIT_001"
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


class MMMPlanningAnswerEnvelopeStatus(StrEnum):
    """Status of a packaged MMM planning-answer envelope."""

    READY_TO_EXPLAIN = "ready_to_explain"
    READY_TO_EXPLAIN_WITH_CAVEATS = "ready_to_explain_with_caveats"
    BLOCKED = "blocked"
    DEFERRED = "deferred"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    UNKNOWN = "unknown"


class MMMPlanningAnswerClaimBoundary(StrEnum):
    """Boundary class for metadata-only response-boundary statements."""

    CAN_SAY = "can_say"
    CANNOT_SAY = "cannot_say"
    CAN_SAY_WITH_CAVEAT = "can_say_with_caveat"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"
    REQUIRES_APPROVED_ARTIFACT = "requires_approved_artifact"


class MMMPlanningAnswerEvidenceType(StrEnum):
    """Evidence reference types for planning-answer envelopes."""

    PLANNING_ANSWER_ELIGIBILITY = "planning_answer_eligibility"
    MMM_ARTIFACT_USE_READINESS = "mmm_artifact_use_readiness"
    DECISION_SURFACE_GATE = "decision_surface_gate"
    TRUST_REPORT_GATE = "trust_report_gate"
    RECOMMENDATION_GATE = "recommendation_gate"
    RUNTIME_RESULT = "runtime_result"
    MODEL_ARTIFACT = "model_artifact"
    CALIBRATION_READINESS = "calibration_readiness"
    SOURCE_DATA_READINESS = "source_data_readiness"
    OTHER = "other"


class MMMPlanningAnswerEnvelopeIssueCode(StrEnum):
    """Typed issue codes for MMM planning-answer envelopes."""

    ELIGIBILITY_RESULT_PRESENT = "eligibility_result_present"
    ELIGIBILITY_RESULT_MISSING = "eligibility_result_missing"
    ANSWER_ALLOWED = "answer_allowed"
    ANSWER_BLOCKED = "answer_blocked"
    ANSWER_DEFERRED = "answer_deferred"
    ANSWER_MODE_PRESERVED = "answer_mode_preserved"
    CAVEATS_PRESERVED = "caveats_preserved"
    BLOCKED_REASONS_PRESERVED = "blocked_reasons_preserved"
    DEFERRED_REASONS_PRESERVED = "deferred_reasons_preserved"
    GATE_REFERENCES_PRESERVED = "gate_references_preserved"
    HUMAN_REVIEW_REQUIRED_PRESERVED = "human_review_required_preserved"
    EVIDENCE_REFERENCES_ADDED = "evidence_references_added"
    CAN_SAY_BOUNDARY_ADDED = "can_say_boundary_added"
    CANNOT_SAY_BOUNDARY_ADDED = "cannot_say_boundary_added"
    UNSUPPORTED_NUMERIC_CLAIMS_BLOCKED = "unsupported_numeric_claims_blocked"
    RECOMMENDATION_CLAIMS_BLOCKED_WITHOUT_GATE = "recommendation_claims_blocked_without_gate"
    OPTIMIZER_SIMULATOR_CLAIMS_BLOCKED = "optimizer_simulator_claims_blocked"  # must not
    DECISION_SURFACE_REQUIRED_FOR_SCENARIO = "decision_surface_required_for_scenario"
    TRUST_REVIEW_REQUIRED_FOR_PLANNING = "trust_review_required_for_planning"
    RECOMMENDATION_CONTRACT_REQUIRED_FOR_RECOMMENDATION = (
        "recommendation_contract_required_for_recommendation"
    )
    LINEAGE_PRESERVED = "lineage_preserved"
    NO_DECISION_SURFACE_CONSTRUCTION = "no_decision_surface_construction"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_TRUST_REPORT_CONSTRUCTION = "no_trust_report_construction"
    NO_TRUST_REPORT_BYPASS = "no_trust_report_bypass"
    NO_RECOMMENDATION_CONTRACT_GENERATION = "no_recommendation_contract_generation"
    NO_RECOMMENDATION_GENERATION = "no_recommendation_generation"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"  # must not execute optimizer
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"  # must not execute simulator
    NO_BUDGET_ALLOCATION_CALCULATION = "no_budget_allocation_calculation"
    NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION = "no_roi_roas_lift_incrementality_calculation"
    NO_ARTIFACT_LOADING = "no_artifact_loading"
    NO_MODEL_LOADING = "no_model_loading"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_MMM_FITTING = "no_mmm_fitting"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"
    NO_LLM_PROVIDER_BEHAVIOR_CHANGE = "no_llm_provider_behavior_change"


class MMMPlanningAnswerEvidenceReference(ContractBaseModel):
    """Metadata-only evidence reference for a planning-answer envelope."""

    evidence_id: str
    evidence_type: MMMPlanningAnswerEvidenceType
    source_id: str | None = None
    source_uri: str | None = None
    artifact_id: str | None = None
    gate_name: str | None = None
    status: str | None = None
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("evidence_id")
    @classmethod
    def evidence_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "evidence_id cannot be empty"
            raise ValueError(msg)
        return value


class MMMPlanningAnswerClaimStatement(ContractBaseModel):
    """Metadata-only response-boundary statement (not a business/math claim)."""

    claim_id: str
    boundary: MMMPlanningAnswerClaimBoundary
    statement: str
    reason: str
    required_gate: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("claim_id", "statement", "reason")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "claim_id, statement, and reason cannot be empty"
            raise ValueError(msg)
        return value


class MMMPlanningAnswerEnvelopeRequest(ContractBaseModel):
    """Request to build a metadata-only MMM planning-answer envelope."""

    request_id: str
    eligibility_result: MMMPlanningAnswerEligibilityResult | None = None
    evidence_references: list[MMMPlanningAnswerEvidenceReference] = Field(default_factory=list)
    include_default_boundaries: bool = True
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


class MMMPlanningAnswerEnvelope(ContractBaseModel):
    """Metadata-only package of an eligible MMM planning-answer response boundary."""

    request_id: str
    status: MMMPlanningAnswerEnvelopeStatus
    question_class: MMMPlanningQuestionClass
    answer_mode: MMMPlanningAnswerMode
    answer_allowed: bool = False
    human_review_required: bool = False
    decision_surface_required: bool = False
    trust_review_required: bool = False
    recommendation_contract_required: bool = False
    caveats: list[str] = Field(default_factory=list)
    blocked_reasons: list[str] = Field(default_factory=list)
    deferred_reasons: list[str] = Field(default_factory=list)
    gate_references: list[MMMPlanningAnswerGateReference] = Field(default_factory=list)
    evidence_references: list[MMMPlanningAnswerEvidenceReference] = Field(default_factory=list)
    can_say: list[MMMPlanningAnswerClaimStatement] = Field(default_factory=list)
    cannot_say: list[MMMPlanningAnswerClaimStatement] = Field(default_factory=list)
    issues: list[MMMPlanningAnswerEnvelopeIssueCode] = Field(default_factory=list)
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


FORBIDDEN_MMM_PLANNING_ANSWER_ENVELOPE_FIELD_NAMES = _FORBIDDEN_RESULT_FIELD_NAMES
