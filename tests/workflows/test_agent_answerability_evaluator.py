"""Deterministic answerability evaluator eval harness (no LLM, no question-text branching)."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from mip.contracts.agent_answerability import (
    AgentAnswerabilityRequest,
    AgentAnswerabilityState,
    AgentAnswerMode,
    AvailableReportSummary,
    RequestedClaimType,
    ToolAvailabilityStatus,
)
from mip.contracts.deterministic_report import ReportType
from mip.workflows.agent.answerability import evaluate_agent_answerability

_EVALUATOR_SOURCE = Path("src/mip/workflows/agent/answerability.py")

_ADVISORY_REPORT = AvailableReportSummary(
    report_id="det-report-adv-local_fitness_studio",
    report_type=ReportType.COLD_START_ADVISORY.value,
    governance_status="advisory_only",
    evidence_mode="business_profile_only",
    blocked_claims=["causal_lift", "roi_proof", "budget_optimization"],
    allowed_downstream_uses=["explain_advisory_recommendation", "identify_missing_data"],
    forbidden_downstream_uses=["roi_proof", "budget_optimization", "mmm_model_output"],
)

_CALIBRATION_REPORT = AvailableReportSummary(
    report_id="det-report-cal-valid",
    report_type=ReportType.CALIBRATION_MAPPING.value,
    governance_status="candidate",
    evidence_mode="diagnostic_candidate",
    blocked_claims=["causal_lift", "roi_proof"],
    allowed_downstream_uses=["diagnostic_review", "education"],
    forbidden_downstream_uses=["decision_recommendation", "budget_optimization"],
)

_READINESS_REPORT = AvailableReportSummary(
    report_id="det-report-readiness-national",
    report_type=ReportType.READINESS_ASSESSMENT.value,
    governance_status="diagnostic_only",
    evidence_mode="readiness_only",
    blocked_claims=["fitted_mmm_outputs", "power_mde_results"],
    allowed_downstream_uses=["readiness_reassessment", "data_collection"],
    forbidden_downstream_uses=["geox_inference", "matched_market_selection"],
)


def _advisory_tool(*, available: bool = True) -> ToolAvailabilityStatus:
    return ToolAvailabilityStatus(
        tool_name="run_cold_start_advisory_for_stage_a_fixture",
        tool_type="deterministic_workflow",
        available=available,
        supports_claim_types=["cold_start_advisory", "general_marketing_advice"],
        unsupported_claim_types=["roi", "causal_lift", "budget_optimization"],
    )


def test_evaluator_does_not_branch_on_question_text() -> None:
    source = _EVALUATOR_SOURCE.read_text(encoding="utf-8")
    assert 'if "roi"' not in source.lower()
    assert "should i increase spend" not in source.lower()
    assert "fixture_id ==" not in source
    assert "user_question" not in source


def test_roi_with_advisory_report_routes_to_core_ml_by_default() -> None:
    decision = evaluate_agent_answerability(
        AgentAnswerabilityRequest(
            requested_claim_type=RequestedClaimType.ROI,
            user_intent="User asks for ROI (documentation only).",
            available_reports=[_ADVISORY_REPORT],
            assert_claim_authorized_by_available_artifacts=False,
        ),
        decision_id="eval-roi-advisory-default",
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML
    assert decision.answer_mode == AgentAnswerMode.ROUTE_TO_MMM
    assert decision.required_core_engine == "mmm"


def test_roi_asserted_from_advisory_report_is_blocked() -> None:
    decision = evaluate_agent_answerability(
        AgentAnswerabilityRequest(
            requested_claim_type=RequestedClaimType.ROI,
            user_intent="User asks to prove ROI from advisory report.",
            available_reports=[_ADVISORY_REPORT],
            assert_claim_authorized_by_available_artifacts=True,
        ),
        decision_id="eval-roi-advisory-assert-blocked",
    )
    assert decision.state == AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY
    assert decision.answer_mode == AgentAnswerMode.BLOCKED_UNSUPPORTED_CLAIM


def test_cold_start_tool_available_is_answerable_from_deterministic_tool() -> None:
    decision = evaluate_agent_answerability(
        AgentAnswerabilityRequest(
            requested_claim_type=RequestedClaimType.COLD_START_ADVISORY,
            available_tools=[_advisory_tool()],
        ),
        decision_id="eval-cold-start-tool",
    )
    assert decision.state == AgentAnswerabilityState.ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT
    assert decision.answer_mode == AgentAnswerMode.ADVISORY_ONLY_GUIDANCE


def test_explain_calibration_report_from_registered_artifact() -> None:
    decision = evaluate_agent_answerability(
        AgentAnswerabilityRequest(
            requested_claim_type=RequestedClaimType.EXPERIMENT_CALIBRATION,
            available_reports=[_CALIBRATION_REPORT],
        ),
        decision_id="eval-explain-calibration-report",
    )
    assert decision.state == AgentAnswerabilityState.ANSWERABLE_FROM_REGISTERED_ARTIFACT
    assert decision.answer_mode == AgentAnswerMode.DIRECT_REPORT_EXPLANATION


def test_missing_se_calibration_inputs_need_user_data() -> None:
    decision = evaluate_agent_answerability(
        AgentAnswerabilityRequest(
            requested_claim_type=RequestedClaimType.EXPERIMENT_CALIBRATION,
            missing_inputs=["standard_error"],
            available_tools=[
                ToolAvailabilityStatus(
                    tool_name="run_calibration_mapping_for_stage_a_fixture",
                    tool_type="deterministic_workflow",
                    supports_claim_types=["experiment_calibration"],
                )
            ],
        ),
        decision_id="eval-missing-se-calibration",
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA
    assert "standard_error" in decision.missing_inputs


def test_matched_markets_from_readiness_routes_to_geox() -> None:
    decision = evaluate_agent_answerability(
        AgentAnswerabilityRequest(
            requested_claim_type=RequestedClaimType.MATCHED_MARKET_DESIGN,
            available_reports=[_READINESS_REPORT],
        ),
        decision_id="eval-matched-markets-readiness",
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML
    assert decision.answer_mode == AgentAnswerMode.ROUTE_TO_GEOX


def test_unavailable_tool_uses_fallback_mode() -> None:
    decision = evaluate_agent_answerability(
        AgentAnswerabilityRequest(
            requested_claim_type=RequestedClaimType.COLD_START_ADVISORY,
            available_tools=[_advisory_tool(available=False)],
        ),
        decision_id="eval-tool-unavailable",
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA
    assert decision.answer_mode == AgentAnswerMode.TOOL_UNAVAILABLE_FALLBACK


def test_budget_optimization_without_inputs_needs_core_or_data() -> None:
    decision = evaluate_agent_answerability(
        AgentAnswerabilityRequest(
            requested_claim_type=RequestedClaimType.BUDGET_OPTIMIZATION,
            user_intent="Ambiguous spend increase question (documentation only).",
        ),
        decision_id="eval-budget-optimization-ambiguous",
    )
    assert decision.state in {
        AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA,
        AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML,
    }
    assert decision.answer_mode != AgentAnswerMode.DIRECT_REPORT_EXPLANATION


def test_causal_proof_from_synthetic_advisory_is_blocked_when_asserted() -> None:
    decision = evaluate_agent_answerability(
        AgentAnswerabilityRequest(
            requested_claim_type=RequestedClaimType.CAUSAL_LIFT,
            available_reports=[_ADVISORY_REPORT],
            assert_claim_authorized_by_available_artifacts=True,
        ),
        decision_id="eval-causal-from-advisory-blocked",
    )
    assert decision.state == AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY


def test_governance_forbids_roi_tool_even_when_tool_listed() -> None:
    decision = evaluate_agent_answerability(
        AgentAnswerabilityRequest(
            requested_claim_type=RequestedClaimType.ROI,
            available_reports=[_ADVISORY_REPORT],
            available_tools=[
                ToolAvailabilityStatus(
                    tool_name="run_cold_start_advisory_for_stage_a_fixture",
                    tool_type="deterministic_workflow",
                    supports_claim_types=["roi"],
                )
            ],
        ),
        decision_id="eval-roi-tool-blocked-by-report",
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML


@pytest.mark.parametrize(
    ("claim", "report"),
    [
        (RequestedClaimType.ROI, _ADVISORY_REPORT),
        (RequestedClaimType.MATCHED_MARKET_DESIGN, _READINESS_REPORT),
    ],
)
def test_decision_output_avoids_forbidden_measurement_claims_in_scope(
    claim: RequestedClaimType,
    report: AvailableReportSummary,
) -> None:
    decision = evaluate_agent_answerability(
        AgentAnswerabilityRequest(
            requested_claim_type=claim,
            available_reports=[report],
        ),
        decision_id=f"eval-forbidden-scope-{claim.value}",
    )
    combined = " ".join(
        [
            decision.fallback_message or "",
            " ".join(decision.allowed_response_scope),
        ]
    ).lower()
    assert decision.state in {
        AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML,
        AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY,
    }
    assert not re.search(r"\bchannel_roi\b", combined)
