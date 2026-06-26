"""Tests for agent capability eval fixture loading."""

from __future__ import annotations

from pathlib import Path

import pytest

from mip.contracts.agent_answerability import AgentAnswerabilityState
from mip.evaluation.agent_capability_fixtures import (
    AgentCapabilityEvalFixtureError,
    list_agent_capability_eval_cases,
    list_agent_capability_eval_fixtures,
    load_agent_capability_eval_case,
    load_agent_capability_eval_fixture,
    load_agent_capability_eval_manifest,
)

_REQUIRED_RISKY_CLAIMS = {
    "roi",
    "causal_lift",
    "budget_optimization",
    "matched_market_design",
    "experiment_calibration",
    "cold_start_advisory",
}
_ALL_STATES = {state.value for state in AgentAnswerabilityState}
_NON_ANSWERABLE_STATES = {
    AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY.value,
    AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML.value,
    AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA.value,
}
_EVAL_ROOT = Path("examples/fixtures/agent_capability_eval")


def test_manifest_exists() -> None:
    manifest = load_agent_capability_eval_manifest()
    assert manifest["schema_version"] == "agent_capability_eval_v1"
    assert len(manifest["cases"]) >= 10


def test_all_case_files_exist() -> None:
    manifest = load_agent_capability_eval_manifest()
    for entry in manifest["cases"]:
        case_path = _EVAL_ROOT / entry["case_file"]
        assert case_path.is_file(), entry["case_id"]


def test_all_case_ids_are_unique() -> None:
    fixtures = list_agent_capability_eval_fixtures()
    case_ids = [fixture.case_id for fixture in fixtures]
    assert len(case_ids) == len(set(case_ids))


def test_all_cases_validate_as_agent_capability_eval_case() -> None:
    cases = list_agent_capability_eval_cases()
    assert len(cases) >= 10
    for case in cases:
        assert case.case_id
        assert case.request.requested_claim_type


def test_every_required_state_appears_at_least_once() -> None:
    states = {str(case.expected_state) for case in list_agent_capability_eval_cases()}
    assert states == _ALL_STATES


def test_risky_claim_types_are_represented() -> None:
    claims = {str(case.request.requested_claim_type) for case in list_agent_capability_eval_cases()}
    assert _REQUIRED_RISKY_CLAIMS.issubset(claims)


def test_non_answerable_cases_require_fallback_or_forbidden_states() -> None:
    for fixture in list_agent_capability_eval_fixtures():
        if str(fixture.eval_case.expected_state) in _NON_ANSWERABLE_STATES:
            assert fixture.requires_fallback_message or fixture.forbidden_answerable_states


def test_no_case_expects_numeric_measurement_output() -> None:
    forbidden_output_tokens = (
        "channel_roi_value",
        "optimized_budget_allocation",
        "incremental_lift_percent",
        "matched_market_pair",
        "roi_is",
        "optimized_mix",
    )
    for case in list_agent_capability_eval_cases():
        combined = " ".join(case.forbidden_phrases).lower()
        for token in forbidden_output_tokens:
            if token in combined:
                assert str(case.expected_state) not in {
                    AgentAnswerabilityState.ANSWERABLE_FROM_REGISTERED_ARTIFACT.value,
                    AgentAnswerabilityState.ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT.value,
                }


def test_load_case_by_id() -> None:
    case = load_agent_capability_eval_case("roi_advisory_only")
    assert case.expected_state == AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML


def test_missing_case_id_fails_closed() -> None:
    with pytest.raises(AgentCapabilityEvalFixtureError, match="not found"):
        load_agent_capability_eval_fixture("missing_case_id")


def test_fixture_record_includes_manifest_metadata() -> None:
    fixture = load_agent_capability_eval_fixture("explain_calibration_report")
    assert fixture.requires_report is True
    assert "experiment_calibration" in fixture.tags
