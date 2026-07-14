"""Narrow internal application path for method-promotion handoff answerability.

Chains:
  raw handoff payload
  → validate_and_normalize_method_promotion_handoff
  → evaluate_method_promotion_handoff_answerability
  → JSON-safe application result

Deterministic fixture/application wrapper only.
No LLM orchestration, answer eligibility, DecisionSurface, TrustReport bypass,
RecommendationContract, planning, spend/ROI, or claim/catalog/production auth.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.method_promotion_handoff_consumer import (
    MIPMethodPromotionHandoffConsumerRuntimeInput,
    validate_and_normalize_method_promotion_handoff,
)
from mip.contracts.method_promotion_handoff_routing_answerability import (
    MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeInput,
    evaluate_method_promotion_handoff_answerability,
)

ARTIFACT_ID = "MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_APPLICATION_001"


class MethodPromotionHandoffAnswerabilityApplicationInput(ContractBaseModel):
    """Application input: raw package handoff + user intent."""

    raw_handoff_payload: Mapping[str, Any] | None = None
    user_intent: str
    requested_action: str | None = None
    answer_surface: str | None = None
    strict_guardrails: bool = True
    ingestion_context: Mapping[str, Any] | None = None
    lineage_context: Mapping[str, Any] | None = None


class MethodPromotionHandoffAnswerabilityApplicationOutput(ContractBaseModel):
    """Application output: consumer + answerability guard result summary."""

    consumer_runtime_status: str
    consumer_accepted_for_governance_context: bool = False
    consumer_rejected_for_decisioning: bool = True
    answerability_routing_status: str
    allowed_answer_modes: tuple[str, ...] = ()
    blocked_answer_modes: tuple[str, ...] = ()
    can_display_governance_context: bool = False
    can_answer_decisioning_question: bool = False
    can_answer_planning_question: bool = False
    can_generate_recommendation: bool = False
    can_create_decision_surface: bool = False
    can_bypass_trust_report: bool = False
    can_generate_recommendation_contract: bool = False
    safe_response_guidance: str = ""
    next_review_lane: str = "none"
    explanation_codes: tuple[str, ...] = ()
    consumer_validation_errors: tuple[str, ...] = ()
    lineage: Mapping[str, Any] = Field(default_factory=dict)


def apply_method_promotion_handoff_answerability_guard(
    application_input: MethodPromotionHandoffAnswerabilityApplicationInput,
) -> MethodPromotionHandoffAnswerabilityApplicationOutput:
    """Apply consumer validation then the answerability guard.

    Always returns false for decisioning/planning/recommendation/DecisionSurface/
    TrustReport/RecommendationContract capability flags.
    """

    consumer_output = validate_and_normalize_method_promotion_handoff(
        MIPMethodPromotionHandoffConsumerRuntimeInput(
            raw_handoff_payload=application_input.raw_handoff_payload,
            ingestion_context=application_input.ingestion_context,
            strict_validation=application_input.strict_guardrails,
            lineage_context=application_input.lineage_context,
        )
    )

    # Pass ready record only when consumer accepted governance context.
    consumer_record = None
    if (
        consumer_output.accepted_for_governance_context
        and consumer_output.consumer_record is not None
    ):
        consumer_record = consumer_output.consumer_record

    answerability_output = evaluate_method_promotion_handoff_answerability(
        MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeInput(
            consumer_record=consumer_record,
            user_intent=application_input.user_intent,
            requested_action=application_input.requested_action,
            answer_surface=application_input.answer_surface,
            strict_guardrails=application_input.strict_guardrails,
            context={
                "application_artifact_id": ARTIFACT_ID,
                "consumer_runtime_status": str(consumer_output.consumer_status),
                "consumer_accepted_for_governance_context": (
                    consumer_output.accepted_for_governance_context
                ),
            },
        )
    )

    lineage: dict[str, Any] = {
        "artifact_id": ARTIFACT_ID,
        "application": "apply_method_promotion_handoff_answerability_guard",
        "consumer_runtime_called": True,
        "answerability_guard_called": True,
        "handoff_governance_context_only": True,
        "llm_orchestration_integration_implemented": False,
        "answer_eligibility_integration_implemented": False,
        "user_facing_answer_generation_implemented": False,
        "consumer_lineage": dict(consumer_output.lineage or {}),
        "answerability_lineage": dict(answerability_output.lineage or {}),
        "user_intent": application_input.user_intent,
    }

    return MethodPromotionHandoffAnswerabilityApplicationOutput(
        consumer_runtime_status=str(consumer_output.consumer_status),
        consumer_accepted_for_governance_context=(
            consumer_output.accepted_for_governance_context
        ),
        consumer_rejected_for_decisioning=consumer_output.rejected_for_decisioning,
        answerability_routing_status=str(answerability_output.routing_status),
        allowed_answer_modes=tuple(answerability_output.allowed_answer_modes),
        blocked_answer_modes=tuple(answerability_output.blocked_answer_modes),
        can_display_governance_context=answerability_output.can_display_governance_context,
        can_answer_decisioning_question=False,
        can_answer_planning_question=False,
        can_generate_recommendation=False,
        can_create_decision_surface=False,
        can_bypass_trust_report=False,
        can_generate_recommendation_contract=False,
        safe_response_guidance=answerability_output.safe_response_guidance,
        next_review_lane=str(answerability_output.next_review_lane),
        explanation_codes=tuple(answerability_output.explanation_codes),
        consumer_validation_errors=tuple(consumer_output.validation_errors),
        lineage=lineage,
    )


def serialize_method_promotion_handoff_answerability_application_output(
    output: MethodPromotionHandoffAnswerabilityApplicationOutput,
) -> dict[str, Any]:
    """Serialize application output to a JSON-safe dict."""

    data = output.model_dump(mode="json")
    for key in (
        "allowed_answer_modes",
        "blocked_answer_modes",
        "explanation_codes",
        "consumer_validation_errors",
    ):
        value = data.get(key)
        if isinstance(value, tuple):
            data[key] = list(value)
    return data


__all__ = [
    "ARTIFACT_ID",
    "MethodPromotionHandoffAnswerabilityApplicationInput",
    "MethodPromotionHandoffAnswerabilityApplicationOutput",
    "apply_method_promotion_handoff_answerability_guard",
    "serialize_method_promotion_handoff_answerability_application_output",
]
