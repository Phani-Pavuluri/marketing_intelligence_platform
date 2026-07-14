"""MIP method promotion handoff routing/answerability guard.

Deterministic guard: MIPMethodPromotionHandoffConsumerRecord + user_intent
→ safe routing/answerability output.

Allows explanation/display/defer/block only.
Does not enable answer eligibility, LLM orchestration, DecisionSurface,
TrustReport bypass, RecommendationContract, planning recommendations, or
spend/ROI/claim/catalog/production/method promotion authorization.
"""

from __future__ import annotations

from collections.abc import Mapping
from enum import StrEnum
from typing import Any

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.method_promotion_handoff_consumer import (
    FIXED_AUTH,
    FIXED_BYPASS,
    FIXED_PROMO,
    MIPMethodPromotionHandoffConsumerRecord,
    MIPMethodPromotionHandoffConsumerStatus,
)

ARTIFACT_ID = "MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_001"
READY_STATUS = (
    MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT.value
)
GENERIC_APPROVE_REVIEW_CONTINUATION = "APPROVE_REVIEW_CONTINUATION"

SAFE_GUIDANCE_BASE = (
    "This handoff can be used only as governance context. "
    "It does not authorize planning recommendations or spend movement. "
    "A separate DecisionSurface/TrustReport/RecommendationContract path is required. "
    "The system may display blockers, warnings, lineage, and review scope."
)

ALLOWED_ROUTES: tuple[str, ...] = (
    "ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY",
    "ROUTE_TO_DIAGNOSTIC_EXPLANATION",
    "ROUTE_TO_CATALOG_REVIEW",
    "ROUTE_TO_CLAIM_AUTHORIZATION_REVIEW",
    "ROUTE_TO_PRODUCTION_COMPATIBILITY_REVIEW",
    "ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK",
)

BLOCKED_ROUTES: tuple[str, ...] = (
    "ROUTE_BLOCKED_DECISION_SURFACE_APPROVAL",
    "ROUTE_BLOCKED_TRUST_REPORT_BYPASS",
    "ROUTE_BLOCKED_RECOMMENDATION_CONTRACT",
    "ROUTE_BLOCKED_PLANNING_RECOMMENDATION",
    "ROUTE_BLOCKED_BUDGET_OPTIMIZER",
    "ROUTE_BLOCKED_SPEND_REALLOCATION",
    "ROUTE_BLOCKED_ROI_ROAS_RECOMMENDATION",
    "ROUTE_BLOCKED_PRODUCTION_READOUT",
)


class MIPMethodPromotionHandoffRoutingStatus(StrEnum):
    METHOD_PROMOTION_HANDOFF_ROUTING_CONTEXT_AVAILABLE = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_CONTEXT_AVAILABLE"
    )
    METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISIONING = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISIONING"
    )
    METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_PLANNING_RECOMMENDATION = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_PLANNING_RECOMMENDATION"
    )
    METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_BUDGET_OPTIMIZATION = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_BUDGET_OPTIMIZATION"
    )
    METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_SPEND_REALLOCATION = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_SPEND_REALLOCATION"
    )
    METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_ROI_ROAS = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_ROI_ROAS"
    )
    METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISION_SURFACE = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISION_SURFACE"
    )
    METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_TRUST_BYPASS = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_TRUST_BYPASS"
    )
    METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_RECOMMENDATION_CONTRACT = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_RECOMMENDATION_CONTRACT"
    )
    METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CLAIM_AUTHORIZATION = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CLAIM_AUTHORIZATION"
    )
    METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CATALOG_PRODUCTION = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CATALOG_PRODUCTION"
    )
    METHOD_PROMOTION_HANDOFF_ROUTING_DEFER_TO_SEPARATE_REVIEW_LANE = (
        "METHOD_PROMOTION_HANDOFF_ROUTING_DEFER_TO_SEPARATE_REVIEW_LANE"
    )


class MIPMethodPromotionHandoffAnswerMode(StrEnum):
    EXPLAIN_GOVERNANCE_CONTEXT = "explain_governance_context"
    EXPLAIN_METHOD_REVIEW_SCOPE = "explain_method_review_scope"
    EXPLAIN_BLOCKERS_AND_WARNINGS = "explain_blockers_and_warnings"
    EXPLAIN_NON_AUTHORIZATION_STATUS = "explain_non_authorization_status"
    EXPLAIN_REQUIRED_NEXT_REVIEW = "explain_required_next_review"
    DEFER_TO_CATALOG_REVIEW = "defer_to_catalog_review"
    DEFER_TO_CLAIM_AUTHORIZATION_REVIEW = "defer_to_claim_authorization_review"
    DEFER_TO_PRODUCTION_COMPATIBILITY_REVIEW = (
        "defer_to_production_compatibility_review"
    )
    BLOCK_UNSUPPORTED_RECOMMENDATION = "block_unsupported_recommendation"
    ANSWER_WITH_RECOMMENDATION = "answer_with_recommendation"
    ANSWER_WITH_BUDGET_REALLOCATION = "answer_with_budget_reallocation"
    ANSWER_WITH_SPEND_MOVEMENT = "answer_with_spend_movement"
    ANSWER_WITH_ROI_ROAS_CLAIM = "answer_with_roi_roas_claim"
    ANSWER_WITH_CAUSAL_LIFT_CLAIM = "answer_with_causal_lift_claim"
    ANSWER_WITH_BUSINESS_LIFT_CLAIM = "answer_with_business_lift_claim"
    ANSWER_WITH_STATISTICAL_SIGNIFICANCE_CLAIM = (
        "answer_with_statistical_significance_claim"
    )
    ANSWER_WITH_PRODUCTION_READOUT = "answer_with_production_readout"
    ANSWER_WITH_DECISION_SURFACE = "answer_with_decision_surface"
    ANSWER_WITH_RECOMMENDATION_CONTRACT = "answer_with_recommendation_contract"


class MIPMethodPromotionHandoffReviewLane(StrEnum):
    NONE = "none"
    CATALOG_REVIEW = "catalog_review"
    CLAIM_AUTHORIZATION_REVIEW = "claim_authorization_review"
    PRODUCTION_COMPATIBILITY_REVIEW = "production_compatibility_review"
    DECISION_SURFACE_REVIEW = "decision_surface_review"
    RECOMMENDATION_CONTRACT_REVIEW = "recommendation_contract_review"
    PLANNING_REVIEW = "planning_review"


ALLOWED_ANSWER_MODES: tuple[MIPMethodPromotionHandoffAnswerMode, ...] = (
    MIPMethodPromotionHandoffAnswerMode.EXPLAIN_GOVERNANCE_CONTEXT,
    MIPMethodPromotionHandoffAnswerMode.EXPLAIN_METHOD_REVIEW_SCOPE,
    MIPMethodPromotionHandoffAnswerMode.EXPLAIN_BLOCKERS_AND_WARNINGS,
    MIPMethodPromotionHandoffAnswerMode.EXPLAIN_NON_AUTHORIZATION_STATUS,
    MIPMethodPromotionHandoffAnswerMode.EXPLAIN_REQUIRED_NEXT_REVIEW,
    MIPMethodPromotionHandoffAnswerMode.DEFER_TO_CATALOG_REVIEW,
    MIPMethodPromotionHandoffAnswerMode.DEFER_TO_CLAIM_AUTHORIZATION_REVIEW,
    MIPMethodPromotionHandoffAnswerMode.DEFER_TO_PRODUCTION_COMPATIBILITY_REVIEW,
    MIPMethodPromotionHandoffAnswerMode.BLOCK_UNSUPPORTED_RECOMMENDATION,
)

BLOCKED_ANSWER_MODES: tuple[MIPMethodPromotionHandoffAnswerMode, ...] = (
    MIPMethodPromotionHandoffAnswerMode.ANSWER_WITH_RECOMMENDATION,
    MIPMethodPromotionHandoffAnswerMode.ANSWER_WITH_BUDGET_REALLOCATION,
    MIPMethodPromotionHandoffAnswerMode.ANSWER_WITH_SPEND_MOVEMENT,
    MIPMethodPromotionHandoffAnswerMode.ANSWER_WITH_ROI_ROAS_CLAIM,
    MIPMethodPromotionHandoffAnswerMode.ANSWER_WITH_CAUSAL_LIFT_CLAIM,
    MIPMethodPromotionHandoffAnswerMode.ANSWER_WITH_BUSINESS_LIFT_CLAIM,
    MIPMethodPromotionHandoffAnswerMode.ANSWER_WITH_STATISTICAL_SIGNIFICANCE_CLAIM,
    MIPMethodPromotionHandoffAnswerMode.ANSWER_WITH_PRODUCTION_READOUT,
    MIPMethodPromotionHandoffAnswerMode.ANSWER_WITH_DECISION_SURFACE,
    MIPMethodPromotionHandoffAnswerMode.ANSWER_WITH_RECOMMENDATION_CONTRACT,
)

EXPLANATION_ONLY_MODES: tuple[MIPMethodPromotionHandoffAnswerMode, ...] = (
    MIPMethodPromotionHandoffAnswerMode.EXPLAIN_GOVERNANCE_CONTEXT,
    MIPMethodPromotionHandoffAnswerMode.EXPLAIN_METHOD_REVIEW_SCOPE,
    MIPMethodPromotionHandoffAnswerMode.EXPLAIN_BLOCKERS_AND_WARNINGS,
    MIPMethodPromotionHandoffAnswerMode.EXPLAIN_NON_AUTHORIZATION_STATUS,
    MIPMethodPromotionHandoffAnswerMode.EXPLAIN_REQUIRED_NEXT_REVIEW,
    MIPMethodPromotionHandoffAnswerMode.BLOCK_UNSUPPORTED_RECOMMENDATION,
)

# Intent → (routing_status, next_review_lane, extra explanation codes)
_INTENT_BLOCK_MAP: dict[
    str,
    tuple[
        MIPMethodPromotionHandoffRoutingStatus,
        MIPMethodPromotionHandoffReviewLane,
        tuple[str, ...],
    ],
] = {
    "ask_if_method_can_be_used": (
        MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISIONING,
        MIPMethodPromotionHandoffReviewLane.DECISION_SURFACE_REVIEW,
        ("METHOD_USABILITY_REQUIRES_SEPARATE_GATES",),
    ),
    "ask_for_planning_recommendation": (
        MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_PLANNING_RECOMMENDATION,
        MIPMethodPromotionHandoffReviewLane.PLANNING_REVIEW,
        ("PLANNING_RECOMMENDATION_BLOCKED",),
    ),
    "ask_for_budget_optimization": (
        MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_BUDGET_OPTIMIZATION,
        MIPMethodPromotionHandoffReviewLane.PLANNING_REVIEW,
        ("BUDGET_OPTIMIZATION_BLOCKED",),
    ),
    "ask_for_spend_reallocation": (
        MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_SPEND_REALLOCATION,
        MIPMethodPromotionHandoffReviewLane.PLANNING_REVIEW,
        ("SPEND_REALLOCATION_BLOCKED",),
    ),
    "ask_for_roi_roas": (
        MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_ROI_ROAS,
        MIPMethodPromotionHandoffReviewLane.CLAIM_AUTHORIZATION_REVIEW,
        ("ROI_ROAS_CLAIM_BLOCKED",),
    ),
    "ask_for_lift_claim": (
        MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CLAIM_AUTHORIZATION,
        MIPMethodPromotionHandoffReviewLane.CLAIM_AUTHORIZATION_REVIEW,
        ("LIFT_CLAIM_BLOCKED",),
    ),
    "ask_for_production_readout": (
        MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CATALOG_PRODUCTION,
        MIPMethodPromotionHandoffReviewLane.PRODUCTION_COMPATIBILITY_REVIEW,
        ("PRODUCTION_READOUT_BLOCKED",),
    ),
    "ask_for_catalog_or_claim_approval": (
        MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CATALOG_PRODUCTION,
        MIPMethodPromotionHandoffReviewLane.CATALOG_REVIEW,
        ("CATALOG_OR_CLAIM_APPROVAL_BLOCKED",),
    ),
}


class MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeInput(ContractBaseModel):
    """Input for the method-promotion handoff routing/answerability guard."""

    consumer_record: MIPMethodPromotionHandoffConsumerRecord | None = None
    user_intent: str
    requested_action: str | None = None
    answer_surface: str | None = None
    strict_guardrails: bool = True
    context: Mapping[str, Any] | None = None


class MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeOutput(ContractBaseModel):
    """Output of the method-promotion handoff routing/answerability guard."""

    routing_status: MIPMethodPromotionHandoffRoutingStatus
    allowed_answer_modes: tuple[str, ...] = ()
    blocked_answer_modes: tuple[str, ...] = ()
    allowed_routes: tuple[str, ...] = ALLOWED_ROUTES
    blocked_routes: tuple[str, ...] = BLOCKED_ROUTES
    can_display_governance_context: bool = False
    can_answer_decisioning_question: bool = False
    can_answer_planning_question: bool = False
    can_generate_recommendation: bool = False
    can_create_decision_surface: bool = False
    can_bypass_trust_report: bool = False
    can_generate_recommendation_contract: bool = False
    explanation_codes: tuple[str, ...] = ()
    safe_response_guidance: str = SAFE_GUIDANCE_BASE
    next_review_lane: MIPMethodPromotionHandoffReviewLane = (
        MIPMethodPromotionHandoffReviewLane.NONE
    )
    lineage: Mapping[str, Any] = Field(default_factory=dict)


def _mode_values(modes: tuple[MIPMethodPromotionHandoffAnswerMode, ...]) -> tuple[str, ...]:
    return tuple(mode.value for mode in modes)


def _status_str(value: Any) -> str:
    if isinstance(value, StrEnum):
        return str(value.value)
    return str(value or "").strip()


def _false_capabilities() -> dict[str, bool]:
    return {
        "can_answer_decisioning_question": False,
        "can_answer_planning_question": False,
        "can_generate_recommendation": False,
        "can_create_decision_surface": False,
        "can_bypass_trust_report": False,
        "can_generate_recommendation_contract": False,
    }


def _base_lineage(
    runtime_input: MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeInput,
    *,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    lineage: dict[str, Any] = {
        "artifact_id": ARTIFACT_ID,
        "runtime": "evaluate_method_promotion_handoff_answerability",
        "user_intent": runtime_input.user_intent,
        "strict_guardrails": runtime_input.strict_guardrails,
        "approve_review_continuation_not_answer_eligibility": True,
        "non_authorization_statuses_dominate": True,
        "blocked_actions_dominate": True,
        "prohibited_actions_dominate": True,
        "handoff_governance_context_only": True,
        **_false_capabilities(),
    }
    if runtime_input.requested_action:
        lineage["requested_action"] = runtime_input.requested_action
    if runtime_input.answer_surface:
        lineage["answer_surface"] = runtime_input.answer_surface
    if runtime_input.context:
        lineage["context"] = dict(runtime_input.context)
    if extra:
        lineage.update(dict(extra))
    return lineage


def _dominance_codes(
    record: MIPMethodPromotionHandoffConsumerRecord | None,
) -> tuple[str, ...]:
    codes: list[str] = [
        "NON_AUTHORIZATION_STATUSES_DOMINATE",
        "BLOCKED_ACTIONS_DOMINATE",
        "PROHIBITED_ACTIONS_DOMINATE",
        "APPROVE_REVIEW_CONTINUATION_NOT_ANSWER_ELIGIBILITY",
    ]
    if record is None:
        return tuple(codes)
    if _status_str(record.generic_decision_status) == GENERIC_APPROVE_REVIEW_CONTINUATION:
        codes.append("GENERIC_APPROVE_REVIEW_CONTINUATION_WEAK_CONTEXT_ONLY")
    # Non-authorization statuses dominate any approval-like label.
    if (
        _status_str(record.decision_surface_authorization_status) == FIXED_AUTH
        and _status_str(record.trust_report_bypass_status) == FIXED_BYPASS
        and _status_str(record.recommendation_authorization_status) == FIXED_AUTH
        and _status_str(record.method_promotion_status) == FIXED_PROMO
    ):
        codes.append("FIXED_NON_AUTHORIZATION_STATUSES_PRESERVED")
    if record.consumer_blocked_actions:
        codes.append("CONSUMER_BLOCKED_ACTIONS_DOMINATE_ALLOWED_ACTIONS")
    if record.prohibited_actions or record.mip_prohibited_uses:
        codes.append("PROHIBITED_ACTIONS_DOMINATE_USER_INTENT")
    return tuple(codes)


def _output(
    *,
    routing_status: MIPMethodPromotionHandoffRoutingStatus,
    allowed_modes: tuple[MIPMethodPromotionHandoffAnswerMode, ...],
    can_display: bool,
    explanation_codes: tuple[str, ...],
    guidance: str,
    next_lane: MIPMethodPromotionHandoffReviewLane,
    lineage: Mapping[str, Any],
) -> MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeOutput:
    return MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeOutput(
        routing_status=routing_status,
        allowed_answer_modes=_mode_values(allowed_modes),
        blocked_answer_modes=_mode_values(BLOCKED_ANSWER_MODES),
        allowed_routes=ALLOWED_ROUTES,
        blocked_routes=BLOCKED_ROUTES,
        can_display_governance_context=can_display,
        **_false_capabilities(),
        explanation_codes=explanation_codes,
        safe_response_guidance=guidance,
        next_review_lane=next_lane,
        lineage=dict(lineage),
    )


def evaluate_method_promotion_handoff_answerability(
    runtime_input: MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeInput,
) -> MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeOutput:
    """Evaluate safe answer modes for a method-promotion handoff record + intent.

    Capability booleans for decisioning/planning/recommendation/DecisionSurface/
    TrustReport/RecommendationContract are always false.
    """

    intent = (runtime_input.user_intent or "").strip()
    record = runtime_input.consumer_record

    if record is None:
        return _output(
            routing_status=MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISIONING,
            allowed_modes=(
                MIPMethodPromotionHandoffAnswerMode.EXPLAIN_REQUIRED_NEXT_REVIEW,
                MIPMethodPromotionHandoffAnswerMode.BLOCK_UNSUPPORTED_RECOMMENDATION,
            ),
            can_display=False,
            explanation_codes=(
                "MISSING_CONSUMER_RECORD",
                *_dominance_codes(None),
            ),
            guidance=(
                "No method-promotion handoff governance record is available. "
                + SAFE_GUIDANCE_BASE
            ),
            next_lane=MIPMethodPromotionHandoffReviewLane.NONE,
            lineage=_base_lineage(
                runtime_input,
                extra={"consumer_record_present": False},
            ),
        )

    consumer_status = _status_str(record.consumer_status)
    lineage = _base_lineage(
        runtime_input,
        extra={
            "consumer_record_present": True,
            "consumer_status": consumer_status,
            "profile_id": record.profile_id,
            "generic_decision_status": _status_str(record.generic_decision_status),
            "received_handoff_id": record.received_handoff_id,
            **dict(record.lineage or {}),
        },
    )

    if consumer_status != READY_STATUS:
        return _output(
            routing_status=MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISIONING,
            allowed_modes=EXPLANATION_ONLY_MODES,
            can_display=False,
            explanation_codes=(
                "CONSUMER_RECORD_NOT_READY_FOR_GOVERNANCE_CONTEXT",
                f"CONSUMER_STATUS_{consumer_status}",
                *_dominance_codes(record),
            ),
            guidance=(
                "The method-promotion handoff consumer record is not ready for "
                "governance-context display. "
                + SAFE_GUIDANCE_BASE
            ),
            next_lane=MIPMethodPromotionHandoffReviewLane.NONE,
            lineage=lineage,
        )

    # Ready governance context path.
    if intent == "explain_method_governance":
        return _output(
            routing_status=MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_CONTEXT_AVAILABLE,
            allowed_modes=ALLOWED_ANSWER_MODES,
            can_display=True,
            explanation_codes=(
                "GOVERNANCE_CONTEXT_DISPLAY_ALLOWED",
                *_dominance_codes(record),
            ),
            guidance=SAFE_GUIDANCE_BASE,
            next_lane=MIPMethodPromotionHandoffReviewLane.NONE,
            lineage=lineage,
        )

    if intent in _INTENT_BLOCK_MAP:
        status, lane, extra_codes = _INTENT_BLOCK_MAP[intent]
        defer_modes = (
            *EXPLANATION_ONLY_MODES,
            MIPMethodPromotionHandoffAnswerMode.DEFER_TO_CATALOG_REVIEW,
            MIPMethodPromotionHandoffAnswerMode.DEFER_TO_CLAIM_AUTHORIZATION_REVIEW,
            MIPMethodPromotionHandoffAnswerMode.DEFER_TO_PRODUCTION_COMPATIBILITY_REVIEW,
        )
        return _output(
            routing_status=status,
            allowed_modes=defer_modes,
            can_display=True,
            explanation_codes=(
                *extra_codes,
                "DECISIONING_BLOCKED_GOVERNANCE_CONTEXT_ONLY",
                *_dominance_codes(record),
            ),
            guidance=(
                f"User intent {intent!r} is blocked by the method-promotion handoff "
                "routing guard. "
                + SAFE_GUIDANCE_BASE
            ),
            next_lane=lane,
            lineage={
                **lineage,
                "blocked_user_intent": intent,
                "next_review_lane": lane.value,
            },
        )

    # Unknown / unsupported intent: defer safely without enabling decisioning.
    return _output(
        routing_status=MIPMethodPromotionHandoffRoutingStatus.METHOD_PROMOTION_HANDOFF_ROUTING_DEFER_TO_SEPARATE_REVIEW_LANE,
        allowed_modes=EXPLANATION_ONLY_MODES,
        can_display=True,
        explanation_codes=(
            "UNSUPPORTED_OR_UNSPECIFIED_USER_INTENT",
            "DECISIONING_BLOCKED_GOVERNANCE_CONTEXT_ONLY",
            *_dominance_codes(record),
        ),
        guidance=(
            f"User intent {intent!r} is not an authorized answerability path for "
            "method-promotion handoff governance context. "
            + SAFE_GUIDANCE_BASE
        ),
        next_lane=MIPMethodPromotionHandoffReviewLane.NONE,
        lineage={**lineage, "blocked_user_intent": intent},
    )


def serialize_method_promotion_handoff_answerability_output(
    output: MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeOutput,
) -> dict[str, Any]:
    """Serialize answerability output to a JSON-safe dict."""

    data = output.model_dump(mode="json")
    for key in (
        "allowed_answer_modes",
        "blocked_answer_modes",
        "allowed_routes",
        "blocked_routes",
        "explanation_codes",
    ):
        value = data.get(key)
        if isinstance(value, tuple):
            data[key] = list(value)
    return data


__all__ = [
    "ALLOWED_ANSWER_MODES",
    "ALLOWED_ROUTES",
    "ARTIFACT_ID",
    "BLOCKED_ANSWER_MODES",
    "BLOCKED_ROUTES",
    "MIPMethodPromotionHandoffAnswerMode",
    "MIPMethodPromotionHandoffReviewLane",
    "MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeInput",
    "MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeOutput",
    "MIPMethodPromotionHandoffRoutingStatus",
    "SAFE_GUIDANCE_BASE",
    "evaluate_method_promotion_handoff_answerability",
    "serialize_method_promotion_handoff_answerability_output",
]
