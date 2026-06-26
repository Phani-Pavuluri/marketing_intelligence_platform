"""Tests for mip.agents flat-kwargs answerability evaluator API."""

from __future__ import annotations

from datetime import UTC, datetime

from mip.agents.answerability import evaluate_agent_answerability
from mip.contracts.agent_answerability import AgentAnswerabilityState, AgentClaimType
from mip.contracts.deterministic_report import (
    ArtifactReference,
    DeterministicReportEnvelope,
    EvidenceMode,
    GovernanceStatus,
    ReportType,
    default_package_version_label,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def _advisory_report() -> DeterministicReportEnvelope:
    return DeterministicReportEnvelope(
        report_id="det-report-adv-local_fitness_studio",
        report_type=ReportType.COLD_START_ADVISORY,
        source_workflow="test_workflow",
        source_input_ref=ArtifactReference(
            artifact_id="stage-a-fixture:local_fitness_studio",
            artifact_type="stage_a_fixture",
            source_workflow="mip.examples.stage_a_fixtures.load_stage_a_fixture",
            source_fixture_id_or_payload_ref="local_fitness_studio",
            source_commit_or_version=default_package_version_label(),
            created_at=_NOW,
            governance_status=GovernanceStatus.ADVISORY_ONLY,
            evidence_mode=EvidenceMode.BUSINESS_PROFILE_ONLY,
            forbidden_downstream_uses=["roi_proof"],
        ),
        generated_at=_NOW,
        evidence_mode=EvidenceMode.BUSINESS_PROFILE_ONLY,
        governance_status=GovernanceStatus.ADVISORY_ONLY,
        summary="Advisory report for tests.",
        blocked_claims=["roi_proof", "causal_lift"],
        forbidden_downstream_uses=["roi_proof", "budget_optimization"],
    )


def test_flat_kwargs_roi_with_advisory_routes_to_core_ml() -> None:
    decision = evaluate_agent_answerability(
        user_intent="documentation only",
        requested_claim_type=AgentClaimType.ROI,
        available_reports=[_advisory_report()],
    )
    assert decision.state == AgentAnswerabilityState.NEEDS_CORE_DIAGNOSTIC_OR_ML


def test_flat_kwargs_roi_asserted_from_advisory_is_blocked() -> None:
    decision = evaluate_agent_answerability(
        user_intent="documentation only",
        requested_claim_type=AgentClaimType.ROI,
        available_reports=[_advisory_report()],
        assert_claim_authorized_by_available_artifacts=True,
    )
    assert decision.state == AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY


def test_source_artifact_ids_populated_from_envelope() -> None:
    decision = evaluate_agent_answerability(
        user_intent="documentation only",
        requested_claim_type=AgentClaimType.EXPERIMENT_CALIBRATION,
        available_reports=[
            DeterministicReportEnvelope(
                report_id="det-report-cal-valid",
                report_type=ReportType.CALIBRATION_MAPPING,
                source_workflow="test_workflow",
                source_input_ref=ArtifactReference(
                    artifact_id="stage-a-fixture:experiment_readout_valid",
                    artifact_type="stage_a_fixture",
                    source_workflow="mip.examples.stage_a_fixtures.load_stage_a_fixture",
                    source_fixture_id_or_payload_ref="experiment_readout_valid",
                    source_commit_or_version=default_package_version_label(),
                    created_at=_NOW,
                    governance_status=GovernanceStatus.CANDIDATE,
                    evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
                ),
                generated_at=_NOW,
                evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
                governance_status=GovernanceStatus.CANDIDATE,
                summary="Calibration report for tests.",
                blocked_claims=["roi_proof"],
            )
        ],
    )
    assert decision.state == AgentAnswerabilityState.ANSWERABLE_FROM_REGISTERED_ARTIFACT
    assert decision.source_artifact_ids == ["stage-a-fixture:experiment_readout_valid"]
