"""Tests for mock LLM provider."""

from datetime import date, timedelta

from mip.llm.providers import LLMProviderName, MockLLMProvider
from mip.workflows.intake import BusinessObjective, BusinessObjectiveType
from mip.workflows.orchestrator import WorkflowRunStatus, run_local_workflow


def _weekly_rows(count: int = 12) -> list[dict[str, object]]:
    return [
        {
            "date": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "channel": "search",
            "spend": 100 + index,
            "conversions": 10 + index,
        }
        for index in range(count)
    ]


def test_mock_provider_returns_deterministic_response() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _weekly_rows(12),
    )
    provider = MockLLMProvider()
    first = provider.explain(summary)
    second = provider.explain(summary)
    assert first == second
    assert first.provider == LLMProviderName.MOCK
    assert first.text
    assert first.disclaimers == [
        "No MMM, GeoX, adapter, or causal model execution was performed."
    ]


def test_mock_provider_explains_blockers() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.AWARENESS),
        _weekly_rows(12),
    )
    response = MockLLMProvider().explain_blockers(summary)
    assert summary.status == WorkflowRunStatus.BLOCKED
    assert "blocked because" in response.text.lower()


def test_mock_provider_explains_next_steps() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _weekly_rows(12),
    )
    response = MockLLMProvider().explain_next_steps(summary)
    assert "Recommended" in response.text


def test_mock_provider_does_not_claim_model_output() -> None:
    summary = run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        _weekly_rows(12),
    )
    lowered = MockLLMProvider().explain(summary).text.lower()
    assert "estimated lift" not in lowered
    assert "causal impact" not in lowered
    assert "budget recommendation" not in lowered
