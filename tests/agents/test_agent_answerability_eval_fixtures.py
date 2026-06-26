"""Regression tests for agent answerability evaluator using file-backed fixtures."""

from __future__ import annotations

from mip.agents.answerability import evaluate_agent_answerability
from mip.contracts.agent_answerability import AgentAnswerabilityState
from mip.evaluation.agent_capability_fixtures import list_agent_capability_eval_fixtures
from mip.workflows.agent.answerability import (
    evaluate_agent_answerability as evaluate_from_request,
)

_NON_ANSWERABLE_STATES = {
    AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY,
    AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML,
    AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA,
}


def test_evaluator_returns_expected_state_for_every_fixture() -> None:
    for fixture in list_agent_capability_eval_fixtures():
        decision = evaluate_from_request(
            fixture.eval_case.request,
            decision_id=f"fixture-{fixture.case_id}",
        )
        allowed_states = fixture.allowed_expected_states or [
            str(fixture.eval_case.expected_state)
        ]
        assert str(decision.state) in allowed_states, fixture.case_id
        if fixture.eval_case.expected_answer_mode is not None:
            assert decision.answer_mode == fixture.eval_case.expected_answer_mode


def test_evaluator_never_returns_forbidden_states() -> None:
    for fixture in list_agent_capability_eval_fixtures():
        if not fixture.forbidden_answerable_states:
            continue
        decision = evaluate_from_request(fixture.eval_case.request)
        assert str(decision.state) not in fixture.forbidden_answerable_states, fixture.case_id


def test_fallback_message_exists_for_non_answerable_states() -> None:
    for fixture in list_agent_capability_eval_fixtures():
        if not fixture.requires_fallback_message:
            continue
        decision = evaluate_from_request(fixture.eval_case.request)
        assert decision.state in _NON_ANSWERABLE_STATES
        assert decision.fallback_message, fixture.case_id


def test_blocked_claims_preserved_where_expected() -> None:
    for fixture in list_agent_capability_eval_fixtures():
        expected = fixture.eval_case.expected_blocked_claims
        if not expected:
            continue
        decision = evaluate_from_request(fixture.eval_case.request)
        for claim in expected:
            assert claim in decision.blocked_claims or claim in decision.forbidden_response_scope


def test_missing_inputs_preserved_where_expected() -> None:
    for fixture in list_agent_capability_eval_fixtures():
        if not fixture.requires_missing_inputs:
            continue
        decision = evaluate_from_request(fixture.eval_case.request)
        for missing in fixture.eval_case.request.missing_inputs:
            assert missing in decision.missing_inputs


def test_flat_kwargs_api_matches_fixture_expectations() -> None:
    fixture = next(
        item
        for item in list_agent_capability_eval_fixtures()
        if item.case_id == "roi_advisory_only"
    )
    request = fixture.eval_case.request
    decision = evaluate_agent_answerability(
        user_intent=request.user_intent,
        requested_claim_type=request.requested_claim_type,
        available_tools=request.available_tools,
        missing_inputs=request.missing_inputs,
        assert_claim_authorized_by_available_artifacts=(
            request.assert_claim_authorized_by_available_artifacts
        ),
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML


def test_forbidden_phrases_not_in_allowed_scope() -> None:
    for fixture in list_agent_capability_eval_fixtures():
        if not fixture.eval_case.forbidden_phrases:
            continue
        decision = evaluate_from_request(fixture.eval_case.request)
        allowed = " ".join(decision.allowed_response_scope).lower()
        for phrase in fixture.eval_case.forbidden_phrases:
            assert phrase.lower() not in allowed, fixture.case_id
