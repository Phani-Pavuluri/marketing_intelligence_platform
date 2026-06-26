"""Tests for deterministic report envelope contracts."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from mip.contracts.deterministic_report import (
    DETERMINISTIC_REPORT_SCHEMA_VERSION,
    ArtifactReference,
    DeterministicReportEnvelope,
    EvidenceMode,
    FindingSeverity,
    GovernanceStatus,
    ReportFinding,
    ReportType,
    default_package_version_label,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def _artifact_ref(
    *,
    governance_status: GovernanceStatus = GovernanceStatus.CANDIDATE,
) -> ArtifactReference:
    return ArtifactReference(
        artifact_id="stage-a-fixture:experiment_readout_valid",
        artifact_type="stage_a_fixture",
        source_workflow="mip.examples.stage_a_fixtures.load_stage_a_fixture",
        source_fixture_id_or_payload_ref="experiment_readout_valid",
        source_commit_or_version=default_package_version_label(),
        created_at=_NOW,
        governance_status=governance_status,
        evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
        allowed_downstream_uses=["diagnostic_review"],
        forbidden_downstream_uses=["decision_recommendation"],
    )


def _minimal_envelope(**overrides: object) -> DeterministicReportEnvelope:
    base = {
        "report_id": "det-report-cal-test",
        "report_type": ReportType.CALIBRATION_MAPPING,
        "source_workflow": "map_evidence_to_calibration_signal",
        "source_input_ref": _artifact_ref(),
        "generated_at": _NOW,
        "evidence_mode": EvidenceMode.DIAGNOSTIC_CANDIDATE,
        "governance_status": GovernanceStatus.CANDIDATE,
        "summary": "Synthetic calibration mapping summary for tests.",
        "blocked_claims": ["causal_lift", "roi_proof"],
        "forbidden_downstream_uses": ["decision_recommendation"],
    }
    base.update(overrides)
    return DeterministicReportEnvelope(**base)  # type: ignore[arg-type]


def test_report_envelope_requires_core_fields() -> None:
    envelope = _minimal_envelope()
    assert envelope.report_id == "det-report-cal-test"
    assert envelope.report_type == ReportType.CALIBRATION_MAPPING
    assert envelope.schema_version == DETERMINISTIC_REPORT_SCHEMA_VERSION


def test_schema_version_must_be_deterministic_report_v1() -> None:
    with pytest.raises(ValueError, match="schema_version"):
        _minimal_envelope(schema_version="other_version")


def test_invalid_report_type_rejected() -> None:
    with pytest.raises(ValueError):
        _minimal_envelope(report_type="not_a_report_type")


def test_blocked_claims_and_forbidden_downstream_uses_preserved() -> None:
    envelope = _minimal_envelope(
        blocked_claims=["causal_lift", "budget_optimization"],
        forbidden_downstream_uses=["decision_recommendation", "budget_optimization"],
    )
    assert "causal_lift" in envelope.blocked_claims
    assert "budget_optimization" in envelope.forbidden_downstream_uses


def test_artifact_reference_captures_fixture_provenance() -> None:
    ref = _artifact_ref(governance_status=GovernanceStatus.NEEDS_MORE_DATA)
    assert ref.source_fixture_id_or_payload_ref == "experiment_readout_valid"
    assert ref.artifact_type == "stage_a_fixture"


def test_needs_more_data_requires_findings_or_missing_data_or_blocked_claims() -> None:
    with pytest.raises(ValueError, match="needs_more_data reports require"):
        _minimal_envelope(
            governance_status=GovernanceStatus.NEEDS_MORE_DATA,
            blocked_claims=[],
            missing_data=[],
            findings=[],
        )


def test_deterministic_serialization_is_stable() -> None:
    envelope = _minimal_envelope(
        findings=[
            ReportFinding(
                finding_id="blocking-0",
                severity=FindingSeverity.BLOCKING,
                message="missing_uncertainty",
            )
        ],
        missing_data=["standard_error"],
    )
    first = envelope.model_dump(mode="json")
    second = envelope.model_dump(mode="json")
    assert first == second
    assert first["schema_version"] == DETERMINISTIC_REPORT_SCHEMA_VERSION
