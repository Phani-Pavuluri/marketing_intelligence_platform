"""Tests for public mip.llm exports."""


def test_public_imports() -> None:
    from mip.llm import (
        IntentClassification,
        IntentRiskLevel,
        LLMExplanationContext,
        LLMProviderName,
        LLMProviderResponse,
        MockLLMProvider,
        WorkflowIntent,
        allowed_actions_for_confidence_tier,
        assert_llm_may_explain,
        assert_llm_may_recommend,
        assert_safe_explanation,
        blocked_actions_for_confidence_tier,
        classify_intent,
        context_from_trust_report,
        explain_blockers,
        explain_next_steps,
        explain_workflow_summary,
    )

    assert WorkflowIntent.EXPLAIN_TRUST_REPORT.value == "explain_trust_report"
    assert IntentRiskLevel.LOW.value == "low"
    assert callable(classify_intent)
    assert callable(assert_llm_may_explain)
    assert callable(assert_llm_may_recommend)
    assert callable(allowed_actions_for_confidence_tier)
    assert callable(blocked_actions_for_confidence_tier)
    assert callable(context_from_trust_report)
    assert callable(explain_workflow_summary)
    assert callable(explain_blockers)
    assert callable(explain_next_steps)
    assert callable(assert_safe_explanation)
    assert IntentClassification is not None
    assert LLMExplanationContext is not None
    assert LLMProviderName.MOCK.value == "mock"
    assert LLMProviderResponse is not None
    assert MockLLMProvider is not None
