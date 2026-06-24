"""Tests for workflow intent models and validation."""

import pytest
from pydantic import ValidationError

from mip.llm.intents import IntentClassification, IntentRiskLevel, WorkflowIntent


def test_workflow_intent_values() -> None:
    assert WorkflowIntent.EXPLAIN_TRUST_REPORT.value == "explain_trust_report"
    assert WorkflowIntent.UNSUPPORTED.value == "unsupported"


def test_intent_risk_level_values() -> None:
    assert IntentRiskLevel.LOW.value == "low"
    assert IntentRiskLevel.BLOCKED.value == "blocked"


def test_valid_intent_classification() -> None:
    classification = IntentClassification(
        intent=WorkflowIntent.EXPLAIN_TRUST_REPORT,
        risk_level=IntentRiskLevel.LOW,
        requires_human_review=False,
        allowed_actions=["explain", "summarize"],
        blocked_actions=["production_automation"],
        reason="low-risk explanation",
    )
    assert classification.intent == WorkflowIntent.EXPLAIN_TRUST_REPORT


def test_reason_cannot_be_empty() -> None:
    with pytest.raises(ValidationError, match="reason cannot be empty"):
        IntentClassification(
            intent=WorkflowIntent.UNSUPPORTED,
            risk_level=IntentRiskLevel.MEDIUM,
            requires_human_review=False,
            reason="   ",
        )


def test_blocked_risk_requires_blocked_actions() -> None:
    with pytest.raises(ValidationError, match="blocked_actions"):
        IntentClassification(
            intent=WorkflowIntent.UNSUPPORTED,
            risk_level=IntentRiskLevel.BLOCKED,
            requires_human_review=True,
            allowed_actions=["explain"],
            blocked_actions=[],
            reason="blocked without actions",
        )


def test_human_review_cannot_allow_production_execution() -> None:
    with pytest.raises(ValidationError, match="production execution"):
        IntentClassification(
            intent=WorkflowIntent.UNSUPPORTED,
            risk_level=IntentRiskLevel.HIGH,
            requires_human_review=True,
            allowed_actions=["explain", "production_automation"],
            blocked_actions=["bypass_gates"],
            reason="invalid production allowance",
        )


def test_human_review_may_allow_non_production_actions() -> None:
    classification = IntentClassification(
        intent=WorkflowIntent.GENERATE_REPORT,
        risk_level=IntentRiskLevel.HIGH,
        requires_human_review=True,
        allowed_actions=["explain", "summarize", "suggest_review"],
        blocked_actions=["production_automation"],
        reason="review required",
    )
    assert classification.requires_human_review is True
