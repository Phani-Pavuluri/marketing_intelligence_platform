"""MMM LLM response boundary contracts (metadata only; no provider calls)."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.mmm_planning_answer_eligibility import MMMPlanningAnswerMode

RECOMMENDED_NEXT_MMM_LLM_RESPONSE_BOUNDARY_CHECKPOINT_AUDIT_ARTIFACT = (
    "MIP_MMM_LLM_RESPONSE_BOUNDARY_CHECKPOINT_AUDIT_001"
)

_FORBIDDEN_RESULT_FIELD_NAMES = frozenset(
    {
        "prompt",
        "system_prompt",
        "provider",
        "model",
        "completion",
        "message",
        "spend_delta",
        "delta_mu",
        "lift",
        "roi",
        "roas",
        "incrementality",
        "optimal_budget",
        "marginal_roi",
        "recommendation",
        "recommended_budget",
    }
)


class MMMLLMResponseBoundaryStatus(StrEnum):
    """Status of an MMM LLM response boundary package."""

    READY_FOR_LLM_EXPLANATION = "ready_for_llm_explanation"
    READY_FOR_LLM_EXPLANATION_WITH_CAVEATS = "ready_for_llm_explanation_with_caveats"
    BLOCKED = "blocked"
    DEFERRED = "deferred"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    UNKNOWN = "unknown"


class MMMLLMSectionUsePolicy(StrEnum):
    """How an LLM may use a rendered planning section."""

    MUST_PRESERVE_VERBATIM = "must_preserve_verbatim"
    MAY_REWRITE_LIGHTLY = "may_rewrite_lightly"
    MUST_PRESERVE_MEANING = "must_preserve_meaning"
    MUST_INCLUDE = "must_include"
    MUST_NOT_OMIT = "must_not_omit"
    FORBIDDEN_TO_EXPAND = "forbidden_to_expand"
    REFUSAL_REQUIRED = "refusal_required"


class MMMLLMForbiddenAdditionType(StrEnum):
    """Additions an LLM must not introduce beyond rendered sections."""

    NEW_NUMERIC_CLAIM = "new_numeric_claim"
    ROI_ROAS_LIFT_INCREMENTALITY_CLAIM = "roi_roas_lift_incrementality_claim"
    BUDGET_RECOMMENDATION = "budget_recommendation"
    SPEND_REALLOCATION_ADVICE = "spend_reallocation_advice"
    OPTIMIZER_OUTPUT = "optimizer_output"  # must not
    SIMULATOR_OUTPUT = "simulator_output"  # must not
    DECISION_SURFACE_OUTPUT = "decision_surface_output"
    TRUST_TIER_CLAIM = "trust_tier_claim"
    RECOMMENDATION_CONTRACT_CLAIM = "recommendation_contract_claim"
    MODEL_ARTIFACT_INTERPRETATION = "model_artifact_interpretation"
    CAUSAL_INTERPRETATION = "causal_interpretation"
    UNSUPPORTED_BUSINESS_INTERPRETATION = "unsupported_business_interpretation"
    GATE_BYPASS_LANGUAGE = "gate_bypass_language"
    BLOCKER_SOFTENING = "blocker_softening"
    CAVEAT_REMOVAL = "caveat_removal"
    HUMAN_REVIEW_REMOVAL = "human_review_removal"
    EVIDENCE_REFERENCE_REMOVAL = "evidence_reference_removal"


class MMMLLMResponseBoundaryIssueCode(StrEnum):
    """Typed issue codes for MMM LLM response boundaries."""

    RENDERED_RESPONSE_PRESENT = "rendered_response_present"
    RENDERED_RESPONSE_MISSING = "rendered_response_missing"
    VERBATIM_POLICY_ADDED = "verbatim_policy_added"
    REWRITE_POLICY_ADDED = "rewrite_policy_added"
    PRESERVE_POLICY_ADDED = "preserve_policy_added"
    FORBIDDEN_ADDITIONS_ADDED = "forbidden_additions_added"
    CANNOT_SAY_MUST_BE_PRESERVED = "cannot_say_must_be_preserved"
    CAVEATS_MUST_BE_PRESERVED = "caveats_must_be_preserved"
    BLOCKED_DEFERRED_STATUS_MUST_BE_PRESERVED = "blocked_deferred_status_must_be_preserved"
    HUMAN_REVIEW_MUST_BE_PRESERVED = "human_review_must_be_preserved"
    EVIDENCE_REFERENCES_MUST_BE_PRESERVED = "evidence_references_must_be_preserved"
    RECOMMENDATION_REQUEST_REFUSAL_ADDED = "recommendation_request_refusal_added"
    OPTIMIZER_SIMULATOR_REQUEST_REFUSAL_ADDED = (
        "optimizer_simulator_request_refusal_added"  # must not
    )
    UNSUPPORTED_NUMERIC_CLAIM_BLOCKED = "unsupported_numeric_claim_blocked"
    CLAIM_INVENTION_BLOCKED = "claim_invention_blocked"
    BLOCKER_SOFTENING_BLOCKED = "blocker_softening_blocked"
    GATE_BYPASS_BLOCKED = "gate_bypass_blocked"
    READY_FOR_LLM_EXPLANATION = "ready_for_llm_explanation"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    LINEAGE_PRESERVED = "lineage_preserved"
    NO_LLM_CALL = "no_llm_call"  # No LLM
    NO_PROVIDER_INTEGRATION = "no_provider_integration"  # No LLM provider integration
    NO_PROMPT_TEMPLATE_EXECUTION = "no_prompt_template_execution"
    NO_ORCHESTRATION_ROUTING = "no_orchestration_routing"
    NO_RENDERER_BEHAVIOR_CHANGE = "no_renderer_behavior_change"
    NO_DECISION_SURFACE_CONSTRUCTION = "no_decision_surface_construction"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_TRUST_REPORT_CONSTRUCTION = "no_trust_report_construction"
    NO_TRUST_REPORT_BYPASS = "no_trust_report_bypass"
    NO_RECOMMENDATION_CONTRACT_GENERATION = "no_recommendation_contract_generation"
    NO_RECOMMENDATION_GENERATION = "no_recommendation_generation"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"  # must not
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"  # must not
    NO_BUDGET_ALLOCATION_CALCULATION = "no_budget_allocation_calculation"
    NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION = "no_roi_roas_lift_incrementality_calculation"
    NO_ARTIFACT_LOADING = "no_artifact_loading"
    NO_MODEL_LOADING = "no_model_loading"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_MMM_FITTING = "no_mmm_fitting"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"
    NO_LLM_PROVIDER_BEHAVIOR_CHANGE = "no_llm_provider_behavior_change"  # No LLM


class MMMLLMSectionPolicy(ContractBaseModel):
    """Policy for how an LLM may use one rendered planning section."""

    section_id: str
    title: str
    use_policy: MMMLLMSectionUsePolicy
    must_include: bool = False
    must_preserve_verbatim: bool = False
    may_rewrite_lightly: bool = False
    forbidden_to_expand: bool = False
    reason: str
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("section_id", "title", "reason")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "section_id, title, and reason cannot be empty"
            raise ValueError(msg)
        return value


class MMMLLMRefusalPolicy(ContractBaseModel):
    """Deterministic refusal policy for unsafe user escalations."""

    refusal_id: str
    trigger: str
    required_response: str
    reason: str
    forbidden_additions: list[MMMLLMForbiddenAdditionType] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("refusal_id", "trigger", "required_response", "reason")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "refusal_id, trigger, required_response, and reason cannot be empty"
            raise ValueError(msg)
        return value


class MMMLLMResponseBoundaryRequest(ContractBaseModel):
    """Request to build a metadata-only MMM LLM response boundary.

    ``rendered_response`` must be an ``MMMPlanningRenderedResponse`` instance or None.
    Typed as Any to avoid a contracts→reports import cycle.
    """

    request_id: str
    rendered_response: Any | None = None
    user_intent: str | None = None
    include_default_policies: bool = True
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


class MMMLLMResponseBoundary(ContractBaseModel):
    """Metadata-only LLM response boundary over rendered MMM planning sections."""

    request_id: str
    status: MMMLLMResponseBoundaryStatus
    answer_mode: MMMPlanningAnswerMode
    answer_allowed: bool = False
    human_review_required: bool = False
    section_policies: list[MMMLLMSectionPolicy] = Field(default_factory=list)
    forbidden_additions: list[MMMLLMForbiddenAdditionType] = Field(default_factory=list)
    refusal_policies: list[MMMLLMRefusalPolicy] = Field(default_factory=list)
    must_include_sections: list[str] = Field(default_factory=list)
    must_preserve_sections: list[str] = Field(default_factory=list)
    may_rewrite_sections: list[str] = Field(default_factory=list)
    cannot_omit_sections: list[str] = Field(default_factory=list)
    issues: list[MMMLLMResponseBoundaryIssueCode] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


FORBIDDEN_MMM_LLM_RESPONSE_BOUNDARY_FIELD_NAMES = _FORBIDDEN_RESULT_FIELD_NAMES
