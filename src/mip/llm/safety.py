"""Deterministic LLM safety rules and intent classification."""

from typing import TypeAlias

from mip.contracts import ConfidenceTier
from mip.llm.intents import IntentClassification, IntentRiskLevel, WorkflowIntent

_PhraseActionRule: TypeAlias = tuple[tuple[str, ...], str]
_IntentRule: TypeAlias = tuple[tuple[str, ...], WorkflowIntent]

_BLOCKED_PHRASES: tuple[_PhraseActionRule, ...] = (
    (("estimate lift", "estimate incremental"), "direct_lift_estimation"),
    (("infer causal", "causal effect directly"), "direct_causal_inference"),
    (("bypass gate", "bypass gates", "skip gate"), "bypass_gates"),
    (("ignore trustreport", "ignore trust report"), "ignore_trust_report"),
    (("override blocked", "override block"), "override_blocked_status"),
    (
        ("raw experiment", "experiment evidence directly in mmm", "raw evidence in mmm"),
        "raw_evidence_to_mmm",
    ),
    (("upgrade confidence", "upgrade tier"), "upgrade_confidence_tier"),
    (("certify evidence",), "certify_evidence"),
    (("invent model", "invent results", "make up results"), "invent_model_results"),
    (("train mmm", "train the mmm"), "train_mmm_with_llm"),
    (("run geox inference", "run geox directly", "geox inference directly"), "run_geox_inference"),
)

_HIGH_RISK_PHRASES: tuple[_IntentRule, ...] = (
    (
        ("change budget", "reallocate budget", "shift spend", "shift budget"),
        WorkflowIntent.EXPLORE_SCENARIO,
    ),
    (("approve recommendation",), WorkflowIntent.UNSUPPORTED),
    (("approve promotion",), WorkflowIntent.UNSUPPORTED),
    (("launch experiment",), WorkflowIntent.DRAFT_EXPERIMENT_CONFIG),
    (("publish report",), WorkflowIntent.GENERATE_REPORT),
    (("export production", "production recommendation"), WorkflowIntent.GENERATE_REPORT),
    (("make production decision", "production decision"), WorkflowIntent.UNSUPPORTED),
)

_MEDIUM_PHRASES: tuple[_IntentRule, ...] = (
    (("plan measurement", "measurement workflow"), WorkflowIntent.PLAN_MEASUREMENT_WORKFLOW),
    (("draft mmm", "mmm config"), WorkflowIntent.DRAFT_MMM_CONFIG),
    (
        ("draft experiment", "draft geox", "experiment config", "geox config"),
        WorkflowIntent.DRAFT_EXPERIMENT_CONFIG,
    ),
    (("data readiness", "evaluate data"), WorkflowIntent.EVALUATE_DATA_READINESS),
    (
        ("measurement gap", "experiment opportunit", "surface gap"),
        WorkflowIntent.SURFACE_MEASUREMENT_GAP,
    ),
    (("explore scenario", "what if scenario"), WorkflowIntent.EXPLORE_SCENARIO),
    (("generate report", "draft report"), WorkflowIntent.GENERATE_REPORT),
)

_LOW_PHRASES: tuple[_IntentRule, ...] = (
    (("trustreport", "trust report"), WorkflowIntent.EXPLAIN_TRUST_REPORT),
    (("experiment evidence", "explain experiment"), WorkflowIntent.EXPLAIN_EXPERIMENT_EVIDENCE),
    (
        ("calibration readiness", "calibration ready"),
        WorkflowIntent.EXPLAIN_CALIBRATION_READINESS,
    ),
    (("decision surface", "delta mu", "delta-mu"), WorkflowIntent.EXPLAIN_DECISION_SURFACE),
    (("registry", "evidence id", "calibration id"), WorkflowIntent.ANSWER_REGISTRY_QUESTION),
    (
        ("diagnostic", "blocker", "warning", "confidence tier", "readiness"),
        WorkflowIntent.EXPLAIN_TRUST_REPORT,
    ),
    (("summarize", "summary of"), WorkflowIntent.EXPLAIN_TRUST_REPORT),
    (("explain",), WorkflowIntent.EXPLAIN_TRUST_REPORT),
)


def classify_intent(user_request: str) -> IntentClassification:
    """Classify a user request using deterministic keyword rules."""
    normalized = " ".join(user_request.lower().split())

    if not normalized.strip():
        return _blocked_classification(
            WorkflowIntent.UNSUPPORTED,
            "empty request is not allowed",
            ("empty_request",),
        )

    for phrases, action in _BLOCKED_PHRASES:
        if _contains_any(normalized, phrases):
            return _blocked_classification(
                WorkflowIntent.UNSUPPORTED,
                f"request matches blocked pattern: {action}",
                (action, "llm_statistical_execution"),
            )

    for phrases, intent in _MEDIUM_PHRASES:
        if _contains_any(normalized, phrases):
            return IntentClassification(
                intent=intent,
                risk_level=IntentRiskLevel.MEDIUM,
                requires_human_review=False,
                allowed_actions=["explain", "summarize", "draft_config", "evaluate"],
                blocked_actions=["production_automation", "bypass_gates"],
                reason="medium-risk planning or drafting action",
            )

    for phrases, intent in _HIGH_RISK_PHRASES:
        if _contains_any(normalized, phrases):
            return IntentClassification(
                intent=intent,
                risk_level=IntentRiskLevel.HIGH,
                requires_human_review=True,
                allowed_actions=["explain", "summarize", "suggest_review"],
                blocked_actions=[
                    "production_automation",
                    "execute_production",
                    "bypass_gates",
                ],
                reason="high-risk production or approval action requires human review",
            )

    for phrases, intent in _LOW_PHRASES:
        if _contains_any(normalized, phrases):
            return IntentClassification(
                intent=intent,
                risk_level=IntentRiskLevel.LOW,
                requires_human_review=False,
                allowed_actions=["explain", "summarize"],
                blocked_actions=["production_automation", "bypass_gates"],
                reason="low-risk explanation or registry query",
            )

    return IntentClassification(
        intent=WorkflowIntent.UNSUPPORTED,
        risk_level=IntentRiskLevel.MEDIUM,
        requires_human_review=False,
        allowed_actions=["explain", "summarize"],
        blocked_actions=["production_automation", "bypass_gates"],
        reason="unrecognized request; default to cautious medium-risk handling",
    )


def assert_llm_may_explain(confidence_tier: ConfidenceTier) -> bool:
    """Return whether LLM may explain an artifact at this tier (always true)."""
    _ = confidence_tier
    return True


def assert_llm_may_recommend(confidence_tier: ConfidenceTier) -> bool:
    """Return whether LLM may recommend actions for this confidence tier."""
    return confidence_tier in (
        ConfidenceTier.DECISION_READY,
        ConfidenceTier.DIRECTIONAL,
    )


def blocked_actions_for_confidence_tier(confidence_tier: ConfidenceTier) -> list[str]:
    """Return blocked LLM actions for a confidence tier."""
    if confidence_tier == ConfidenceTier.DECISION_READY:
        return ["bypass_gates"]
    if confidence_tier == ConfidenceTier.DIRECTIONAL:
        return ["production_automation", "bypass_gates"]
    if confidence_tier in (ConfidenceTier.DIAGNOSTIC_ONLY, ConfidenceTier.RESEARCH_ONLY):
        return ["recommendation", "production_use", "production_automation", "bypass_gates"]
    if confidence_tier == ConfidenceTier.BLOCKED:
        return ["recommendation", "production_use", "production_automation", "bypass_gates"]
    return ["bypass_gates"]


def allowed_actions_for_confidence_tier(confidence_tier: ConfidenceTier) -> list[str]:
    """Return allowed LLM actions for a confidence tier."""
    if confidence_tier == ConfidenceTier.DECISION_READY:
        return ["explain", "summarize", "recommend_with_evidence"]
    if confidence_tier == ConfidenceTier.DIRECTIONAL:
        return ["explain", "summarize", "suggest_review"]
    if confidence_tier in (ConfidenceTier.DIAGNOSTIC_ONLY, ConfidenceTier.RESEARCH_ONLY):
        return ["explain", "summarize"]
    if confidence_tier == ConfidenceTier.BLOCKED:
        return ["explain"]
    return ["explain"]


def _blocked_classification(
    intent: WorkflowIntent,
    reason: str,
    blocked_actions: tuple[str, ...],
) -> IntentClassification:
    return IntentClassification(
        intent=intent,
        risk_level=IntentRiskLevel.BLOCKED,
        requires_human_review=True,
        allowed_actions=["explain"],
        blocked_actions=list(blocked_actions),
        reason=reason,
    )


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    return any(phrase in text for phrase in phrases)
