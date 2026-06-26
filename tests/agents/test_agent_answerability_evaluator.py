"""Deterministic answerability evaluator eval harness via mip.agents flat-kwargs API."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path

import pytest

from mip.agents.answerability import evaluate_agent_answerability
from mip.contracts.agent_answerability import (
    AgentAnswerabilityState,
    AgentAnswerMode,
    AgentClaimType,
    ToolAvailabilityStatus,
)
from mip.contracts.deterministic_report import (
    ArtifactReference,
    DeterministicReportEnvelope,
    EvidenceMode,
    GovernanceStatus,
    ReportType,
    default_package_version_label,
)

_EVALUATOR_SOURCE = Path("src/mip/workflows/agent/answerability.py")
_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def _artifact_ref(
    *,
    artifact_id: str,
    governance_status: GovernanceStatus,
    evidence_mode: EvidenceMode,
) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=artifact_id,
        artifact_type="stage_a_fixture",
        source_workflow="mip.examples.stage_a_fixtures.load_stage_a_fixture",
        source_fixture_id_or_payload_ref=artifact_id.split(":")[-1],
        source_commit_or_version=default_package_version_label(),
        created_at=_NOW,
        governance_status=governance_status,
        evidence_mode=evidence_mode,
    )


def _envelope(
    *,
    report_id: str,
    report_type: ReportType,
    governance_status: GovernanceStatus,
    evidence_mode: EvidenceMode,
    artifact_id: str,
    blocked_claims: list[str],
    allowed_downstream_uses: list[str],
    forbidden_downstream_uses: list[str],
) -> DeterministicReportEnvelope:
    return DeterministicReportEnvelope(
        report_id=report_id,
        report_type=report_type,
        source_workflow="test_workflow",
        source_input_ref=_artifact_ref(
            artifact_id=artifact_id,
            governance_status=governance_status,
            evidence_mode=evidence_mode,
        ),
        generated_at=_NOW,
        evidence_mode=evidence_mode,
        governance_status=governance_status,
        summary="Synthetic report for answerability tests.",
        blocked_claims=blocked_claims,
        allowed_downstream_uses=allowed_downstream_uses,
        forbidden_downstream_uses=forbidden_downstream_uses,
    )


_ADVISORY_REPORT = _envelope(
    report_id="det-report-adv-local_fitness_studio",
    report_type=ReportType.COLD_START_ADVISORY,
    governance_status=GovernanceStatus.ADVISORY_ONLY,
    evidence_mode=EvidenceMode.BUSINESS_PROFILE_ONLY,
    artifact_id="stage-a-fixture:local_fitness_studio",
    blocked_claims=["causal_lift", "roi_proof", "budget_optimization"],
    allowed_downstream_uses=["explain_advisory_recommendation", "identify_missing_data"],
    forbidden_downstream_uses=["roi_proof", "budget_optimization", "mmm_model_output"],
)

_CALIBRATION_REPORT = _envelope(
    report_id="det-report-cal-valid",
    report_type=ReportType.CALIBRATION_MAPPING,
    governance_status=GovernanceStatus.CANDIDATE,
    evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
    artifact_id="stage-a-fixture:experiment_readout_valid",
    blocked_claims=["causal_lift", "roi_proof"],
    allowed_downstream_uses=["diagnostic_review", "education"],
    forbidden_downstream_uses=["decision_recommendation", "budget_optimization"],
)

_READINESS_REPORT = _envelope(
    report_id="det-report-readiness-national",
    report_type=ReportType.READINESS_ASSESSMENT,
    governance_status=GovernanceStatus.DIAGNOSTIC_ONLY,
    evidence_mode=EvidenceMode.READINESS_ONLY,
    artifact_id="stage-a-fixture:national_readiness",
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
        user_intent="User asks for ROI (documentation only).",
        requested_claim_type=AgentClaimType.ROI,
        available_reports=[_ADVISORY_REPORT],
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML
    assert decision.answer_mode == AgentAnswerMode.ROUTE_TO_MMM
    assert decision.fallback_message is not None


def test_roi_asserted_from_advisory_report_is_blocked() -> None:
    decision = evaluate_agent_answerability(
        user_intent="User asks to prove ROI from advisory report.",
        requested_claim_type=AgentClaimType.ROI,
        available_reports=[_ADVISORY_REPORT],
        assert_claim_authorized_by_available_artifacts=True,
    )
    assert decision.state == AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY
    assert decision.fallback_message is not None


def test_cold_start_tool_available_is_answerable_from_deterministic_tool() -> None:
    decision = evaluate_agent_answerability(
        user_intent="What should we do next?",
        requested_claim_type=AgentClaimType.COLD_START_ADVISORY,
        available_tools=[_advisory_tool()],
    )
    assert decision.state == AgentAnswerabilityState.ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT
    assert decision.answer_mode == AgentAnswerMode.ADVISORY_ONLY_GUIDANCE


def test_explain_calibration_report_from_registered_artifact() -> None:
    decision = evaluate_agent_answerability(
        user_intent="Explain calibration report.",
        requested_claim_type=AgentClaimType.EXPERIMENT_CALIBRATION,
        available_reports=[_CALIBRATION_REPORT],
    )
    assert decision.state == AgentAnswerabilityState.ANSWERABLE_FROM_REGISTERED_ARTIFACT
    assert decision.available_report_ids == ["det-report-cal-valid"]
    assert decision.source_artifact_ids == ["stage-a-fixture:experiment_readout_valid"]


def test_missing_se_calibration_inputs_need_user_data() -> None:
    decision = evaluate_agent_answerability(
        user_intent="Use experiment readout without SE.",
        requested_claim_type=AgentClaimType.EXPERIMENT_CALIBRATION,
        missing_inputs=["standard_error"],
        available_tools=[
            ToolAvailabilityStatus(
                tool_name="run_calibration_mapping_for_stage_a_fixture",
                tool_type="deterministic_workflow",
                supports_claim_types=["experiment_calibration"],
            )
        ],
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA
    assert "standard_error" in decision.missing_inputs
    assert decision.fallback_message is not None


def test_matched_markets_from_readiness_routes_to_geox() -> None:
    decision = evaluate_agent_answerability(
        user_intent="Design matched markets.",
        requested_claim_type=AgentClaimType.MATCHED_MARKET_DESIGN,
        available_reports=[_READINESS_REPORT],
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML
    assert decision.answer_mode == AgentAnswerMode.ROUTE_TO_GEOX
    assert decision.forbidden_response_scope


def test_unavailable_tool_uses_fallback_mode() -> None:
    decision = evaluate_agent_answerability(
        user_intent="Run advisory workflow.",
        requested_claim_type=AgentClaimType.COLD_START_ADVISORY,
        available_tools=[_advisory_tool(available=False)],
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA
    assert decision.answer_mode == AgentAnswerMode.TOOL_UNAVAILABLE_FALLBACK
    assert decision.fallback_message is not None


def test_budget_optimization_without_inputs_needs_core_or_data() -> None:
    decision = evaluate_agent_answerability(
        user_intent="Should I increase spend?",
        requested_claim_type=AgentClaimType.BUDGET_OPTIMIZATION,
    )
    assert decision.state in {
        AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA,
        AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML,
    }
    assert decision.state not in {
        AgentAnswerabilityState.ANSWERABLE_FROM_REGISTERED_ARTIFACT,
        AgentAnswerabilityState.ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT,
    }


def test_causal_proof_from_synthetic_advisory_is_blocked_when_asserted() -> None:
    decision = evaluate_agent_answerability(
        user_intent="Prove causal lift from advisory fixture.",
        requested_claim_type=AgentClaimType.CAUSAL_LIFT,
        available_reports=[_ADVISORY_REPORT],
        assert_claim_authorized_by_available_artifacts=True,
    )
    assert decision.state == AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY


def test_governance_forbids_roi_tool_even_when_tool_listed() -> None:
    decision = evaluate_agent_answerability(
        user_intent="ROI from advisory context.",
        requested_claim_type=AgentClaimType.ROI,
        available_reports=[_ADVISORY_REPORT],
        available_tools=[
            ToolAvailabilityStatus(
                tool_name="run_cold_start_advisory_for_stage_a_fixture",
                tool_type="deterministic_workflow",
                supports_claim_types=["roi"],
            )
        ],
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML


@pytest.mark.parametrize(
    ("claim", "report"),
    [
        (AgentClaimType.ROI, _ADVISORY_REPORT),
        (AgentClaimType.MATCHED_MARKET_DESIGN, _READINESS_REPORT),
    ],
)
def test_forbidden_response_scope_populated_for_risky_claims(
    claim: AgentClaimType,
    report: DeterministicReportEnvelope,
) -> None:
    decision = evaluate_agent_answerability(
        user_intent="documentation only",
        requested_claim_type=claim,
        available_reports=[report],
    )
    allowed_combined = " ".join(
        [decision.fallback_message or "", " ".join(decision.allowed_response_scope)]
    ).lower()
    assert decision.state in {
        AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML,
        AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY,
    }
    assert not re.search(r"\bchannel_roi\b", allowed_combined)
    assert decision.forbidden_response_scope
