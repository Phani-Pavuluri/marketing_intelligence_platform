"""Tests for agent answerability contracts."""

from __future__ import annotations

import json

import pytest

from mip.contracts.agent_answerability import (
    AgentAnswerabilityDecision,
    AgentAnswerabilityRequest,
    AgentAnswerabilityState,
    AgentAnswerMode,
    AgentCapabilityEvalCase,
    AgentClaimType,
    AgentEvidenceLevel,
    AnswerabilityEvidenceLevel,
    RequestedClaimType,
    RoutingConfidence,
    ToolAvailabilityStatus,
)


def test_all_five_answerability_states_exist() -> None:
    assert len(AgentAnswerabilityState) == 5


def test_required_claim_types_exist() -> None:
    assert AgentClaimType is RequestedClaimType
    assert AgentEvidenceLevel is AnswerabilityEvidenceLevel
    assert AgentClaimType.ROI.value == "roi"


def test_answerability_request_accepts_structured_fields_only() -> None:
    request = AgentAnswerabilityRequest(
        requested_claim_type=AgentClaimType.COLD_START_ADVISORY,
        user_intent="documentation-only intent label",
        available_tools=[
            ToolAvailabilityStatus(
                tool_name="run_cold_start_advisory_for_stage_a_fixture",
                tool_type="deterministic_workflow",
                supports_claim_types=["cold_start_advisory"],
            )
        ],
    )
    assert request.requested_claim_type == AgentClaimType.COLD_START_ADVISORY


def test_blocked_decision_requires_forbidden_or_blocked_scope() -> None:
    with pytest.raises(ValueError, match="blocked_by_claim_boundary"):
        AgentAnswerabilityDecision(
            decision_id="dec-1",
            state=AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY,
            user_intent="",
            requested_claim_type=AgentClaimType.ROI,
            evidence_level=AgentEvidenceLevel.UNSUPPORTED,
            allowed_response_scope=[],
            forbidden_response_scope=[],
            blocked_claims=[],
        )


def test_invalid_confidence_in_routing_is_rejected() -> None:
    with pytest.raises(ValueError):
        AgentAnswerabilityDecision(
            decision_id="dec-2",
            state=AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA,
            user_intent="",
            requested_claim_type=AgentClaimType.COLD_START_ADVISORY,
            evidence_level=AgentEvidenceLevel.BUSINESS_PROFILE_ONLY,
            allowed_response_scope=[],
            forbidden_response_scope=[],
            blocked_claims=["x"],
            confidence_in_routing="invalid",  # type: ignore[arg-type]
        )


def test_eval_case_model_validates_expected_state() -> None:
    case = AgentCapabilityEvalCase(
        case_id="eval-1",
        user_question="documentation only",
        request=AgentAnswerabilityRequest(requested_claim_type=AgentClaimType.ROI),
        expected_state=AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML,
        expected_answer_mode=AgentAnswerMode.ROUTE_TO_MMM,
        expected_evidence_level=AgentEvidenceLevel.CORE_MMM_REQUIRED,
    )
    assert case.expected_state == AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML


def test_serialization_is_stable() -> None:
    decision = AgentAnswerabilityDecision(
        decision_id="dec-stable",
        state=AgentAnswerabilityState.ANSWERABLE_FROM_REGISTERED_ARTIFACT,
        user_intent="explain report",
        requested_claim_type=AgentClaimType.EXPERIMENT_CALIBRATION,
        answer_mode=AgentAnswerMode.DIRECT_REPORT_EXPLANATION,
        evidence_level=AgentEvidenceLevel.DETERMINISTIC_WORKFLOW_REPORT,
        source_artifact_ids=["artifact-1"],
        available_report_ids=["report-1"],
        allowed_response_scope=["diagnostic_review"],
        forbidden_response_scope=["decision_recommendation"],
        blocked_claims=["roi_proof"],
        confidence_in_routing=RoutingConfidence.HIGH,
    )
    first = json.loads(decision.model_dump_json())
    second = json.loads(decision.model_dump_json())
    assert first == second
