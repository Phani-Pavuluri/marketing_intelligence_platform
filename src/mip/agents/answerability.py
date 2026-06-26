"""MIP agent governance helpers (no LLM runtime)."""

from __future__ import annotations

from collections.abc import Sequence

from mip.contracts.agent_answerability import (
    AgentAnswerabilityDecision,
    AgentAnswerabilityRequest,
    AgentClaimType,
    ToolAvailabilityStatus,
    available_report_from_envelope,
)
from mip.contracts.deterministic_report import DeterministicReportEnvelope
from mip.workflows.agent.answerability import (
    evaluate_agent_answerability as _evaluate_agent_answerability_from_request,
)


def evaluate_agent_answerability(
    request: AgentAnswerabilityRequest | None = None,
    *,
    user_intent: str = "",
    requested_claim_type: AgentClaimType | None = None,
    available_reports: Sequence[DeterministicReportEnvelope] = (),
    available_tools: Sequence[ToolAvailabilityStatus] = (),
    missing_inputs: Sequence[str] = (),
    assert_claim_authorized_by_available_artifacts: bool = False,
    decision_id: str | None = None,
) -> AgentAnswerabilityDecision:
    """Classify structured answerability input into exactly one state."""
    if request is not None:
        return _evaluate_agent_answerability_from_request(request, decision_id=decision_id)
    if requested_claim_type is None:
        msg = "requested_claim_type is required when request is not provided"
        raise TypeError(msg)
    structured_request = AgentAnswerabilityRequest(
        user_intent=user_intent,
        requested_claim_type=requested_claim_type,
        available_reports=[
            available_report_from_envelope(report) for report in available_reports
        ],
        available_tools=list(available_tools),
        missing_inputs=list(missing_inputs),
        assert_claim_authorized_by_available_artifacts=(
            assert_claim_authorized_by_available_artifacts
        ),
    )
    return _evaluate_agent_answerability_from_request(
        structured_request,
        decision_id=decision_id,
    )


__all__ = ["evaluate_agent_answerability"]
