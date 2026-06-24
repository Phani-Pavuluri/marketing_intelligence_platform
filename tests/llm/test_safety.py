"""Tests for deterministic LLM safety classification."""

import pytest

from mip.contracts import ConfidenceTier
from mip.llm.intents import IntentRiskLevel, WorkflowIntent
from mip.llm.safety import (
    allowed_actions_for_confidence_tier,
    assert_llm_may_explain,
    assert_llm_may_recommend,
    blocked_actions_for_confidence_tier,
    classify_intent,
)

_LOW_MEDIUM_CASES = [
    (
        "explain the TrustReport blockers",
        WorkflowIntent.EXPLAIN_TRUST_REPORT,
        IntentRiskLevel.LOW,
    ),
    (
        "summarize existing evidence diagnostics",
        WorkflowIntent.EXPLAIN_TRUST_REPORT,
        IntentRiskLevel.LOW,
    ),
    (
        "what is in the evidence registry",
        WorkflowIntent.ANSWER_REGISTRY_QUESTION,
        IntentRiskLevel.LOW,
    ),
    (
        "explain calibration readiness",
        WorkflowIntent.EXPLAIN_CALIBRATION_READINESS,
        IntentRiskLevel.LOW,
    ),
    (
        "explain the decision surface",
        WorkflowIntent.EXPLAIN_DECISION_SURFACE,
        IntentRiskLevel.LOW,
    ),
    (
        "plan a measurement workflow",
        WorkflowIntent.PLAN_MEASUREMENT_WORKFLOW,
        IntentRiskLevel.MEDIUM,
    ),
    (
        "draft MMM config for search",
        WorkflowIntent.DRAFT_MMM_CONFIG,
        IntentRiskLevel.MEDIUM,
    ),
    (
        "draft experiment config for GeoX",
        WorkflowIntent.DRAFT_EXPERIMENT_CONFIG,
        IntentRiskLevel.MEDIUM,
    ),
    (
        "evaluate data readiness",
        WorkflowIntent.EVALUATE_DATA_READINESS,
        IntentRiskLevel.MEDIUM,
    ),
    (
        "surface measurement gap opportunities",
        WorkflowIntent.SURFACE_MEASUREMENT_GAP,
        IntentRiskLevel.MEDIUM,
    ),
    (
        "explore scenario without production recommendation",
        WorkflowIntent.EXPLORE_SCENARIO,
        IntentRiskLevel.MEDIUM,
    ),
    (
        "generate draft report from artifacts",
        WorkflowIntent.GENERATE_REPORT,
        IntentRiskLevel.MEDIUM,
    ),
]


@pytest.mark.parametrize(("user_request", "intent", "risk"), _LOW_MEDIUM_CASES)
def test_classify_intent_low_and_medium(
    user_request: str,
    intent: WorkflowIntent,
    risk: IntentRiskLevel,
) -> None:
    result = classify_intent(user_request)
    assert result.intent == intent
    assert result.risk_level == risk
    assert result.reason.strip()
    assert result.blocked_actions


@pytest.mark.parametrize(
    "user_request",
    [
        "approve recommendation for production",
        "launch experiment in production",
        "publish report to stakeholders",
        "export production recommendation",
        "make production decision on spend",
        "shift spend to paid search",
        "change budget allocation",
    ],
)
def test_classify_intent_high_risk_requires_review(user_request: str) -> None:
    result = classify_intent(user_request)
    assert result.risk_level == IntentRiskLevel.HIGH
    assert result.requires_human_review is True
    assert "production_automation" in result.blocked_actions
    assert "production_automation" not in result.allowed_actions


@pytest.mark.parametrize(
    "user_request",
    [
        "estimate lift directly with the LLM",
        "infer causal effect directly",
        "bypass gates and certify",
        "ignore TrustReport warnings",
        "override blocked status",
        "use raw experiment evidence directly in MMM",
        "upgrade confidence tier to decision_ready",
        "certify evidence without gates",
        "invent model results",
        "train MMM directly with LLM",
        "run GeoX inference directly with LLM",
    ],
)
def test_classify_intent_blocked(user_request: str) -> None:
    result = classify_intent(user_request)
    assert result.risk_level == IntentRiskLevel.BLOCKED
    assert result.intent == WorkflowIntent.UNSUPPORTED
    assert result.blocked_actions


def test_classify_intent_empty_request_blocked() -> None:
    result = classify_intent("   ")
    assert result.risk_level == IntentRiskLevel.BLOCKED
    assert "empty_request" in result.blocked_actions


@pytest.mark.parametrize("tier", list(ConfidenceTier))
def test_assert_llm_may_explain_all_tiers(tier: ConfidenceTier) -> None:
    assert assert_llm_may_explain(tier) is True


@pytest.mark.parametrize(
    ("tier", "expected"),
    [
        (ConfidenceTier.DECISION_READY, True),
        (ConfidenceTier.DIRECTIONAL, True),
        (ConfidenceTier.DIAGNOSTIC_ONLY, False),
        (ConfidenceTier.RESEARCH_ONLY, False),
        (ConfidenceTier.BLOCKED, False),
    ],
)
def test_assert_llm_may_recommend(tier: ConfidenceTier, expected: bool) -> None:
    assert assert_llm_may_recommend(tier) is expected


@pytest.mark.parametrize(
    ("tier", "expected"),
    [
        (ConfidenceTier.DECISION_READY, ["bypass_gates"]),
        (ConfidenceTier.DIRECTIONAL, ["production_automation", "bypass_gates"]),
        (
            ConfidenceTier.DIAGNOSTIC_ONLY,
            ["recommendation", "production_use", "production_automation", "bypass_gates"],
        ),
        (
            ConfidenceTier.RESEARCH_ONLY,
            ["recommendation", "production_use", "production_automation", "bypass_gates"],
        ),
        (
            ConfidenceTier.BLOCKED,
            ["recommendation", "production_use", "production_automation", "bypass_gates"],
        ),
    ],
)
def test_blocked_actions_for_confidence_tier(tier: ConfidenceTier, expected: list[str]) -> None:
    assert blocked_actions_for_confidence_tier(tier) == expected


@pytest.mark.parametrize(
    ("tier", "expected"),
    [
        (ConfidenceTier.DECISION_READY, ["explain", "summarize", "recommend_with_evidence"]),
        (ConfidenceTier.DIRECTIONAL, ["explain", "summarize", "suggest_review"]),
        (ConfidenceTier.DIAGNOSTIC_ONLY, ["explain", "summarize"]),
        (ConfidenceTier.RESEARCH_ONLY, ["explain", "summarize"]),
        (ConfidenceTier.BLOCKED, ["explain"]),
    ],
)
def test_allowed_actions_for_confidence_tier(tier: ConfidenceTier, expected: list[str]) -> None:
    assert allowed_actions_for_confidence_tier(tier) == expected
