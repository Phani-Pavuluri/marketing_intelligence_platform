"""Tests for agent answerability contracts."""

from __future__ import annotations

import pytest

from mip.contracts.agent_answerability import (
    AgentAnswerabilityDecision,
    AgentAnswerabilityRequest,
    AgentAnswerabilityState,
    AnswerabilityEvidenceLevel,
    RequestedClaimType,
    ToolAvailabilityStatus,
)


def test_answerability_request_accepts_structured_fields_only() -> None:
    request = AgentAnswerabilityRequest(
        requested_claim_type=RequestedClaimType.COLD_START_ADVISORY,
        user_intent="documentation-only intent label",
        available_tools=[
            ToolAvailabilityStatus(
                tool_name="run_cold_start_advisory_for_stage_a_fixture",
                tool_type="deterministic_workflow",
                supports_claim_types=["cold_start_advisory"],
            )
        ],
    )
    assert request.requested_claim_type == RequestedClaimType.COLD_START_ADVISORY


def test_blocked_decision_requires_forbidden_or_blocked_scope() -> None:
    with pytest.raises(ValueError, match="blocked_by_claim_boundary"):
        AgentAnswerabilityDecision(
            decision_id="dec-1",
            state=AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY,
            user_intent="",
            requested_claim_type=RequestedClaimType.ROI,
            evidence_level=AnswerabilityEvidenceLevel.UNSUPPORTED,
            allowed_response_scope=[],
            forbidden_response_scope=[],
            blocked_claims=[],
        )
