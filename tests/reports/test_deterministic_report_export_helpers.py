"""Tests for deterministic report export helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from mip.contracts.deterministic_report import (
    DETERMINISTIC_REPORT_SCHEMA_VERSION,
    ArtifactReference,
    DeterministicReportEnvelope,
    EvidenceMode,
    GovernanceStatus,
    ReportType,
    default_package_version_label,
)
from mip.reports.deterministic_reports import (
    DeterministicReportExportError,
    report_to_dict,
    report_to_json,
    validate_report_has_no_unsupported_advanced_outputs,
    write_report_json,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def _sample_report(**overrides: object) -> DeterministicReportEnvelope:
    source_ref = ArtifactReference(
        artifact_id="stage-a-fixture:experiment_readout_valid",
        artifact_type="stage_a_fixture",
        source_workflow="mip.examples.stage_a_fixtures.load_stage_a_fixture",
        source_fixture_id_or_payload_ref="experiment_readout_valid",
        source_commit_or_version=default_package_version_label(),
        created_at=_NOW,
        governance_status=GovernanceStatus.CANDIDATE,
        evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
        allowed_downstream_uses=["diagnostic_review"],
        forbidden_downstream_uses=["decision_recommendation"],
    )
    base = {
        "report_id": "det-report-cal-test",
        "report_type": ReportType.CALIBRATION_MAPPING,
        "source_workflow": "map_evidence_to_calibration_signal",
        "source_input_ref": source_ref,
        "generated_at": _NOW,
        "evidence_mode": EvidenceMode.DIAGNOSTIC_CANDIDATE,
        "governance_status": GovernanceStatus.CANDIDATE,
        "summary": "Synthetic calibration mapping summary.",
        "blocked_claims": ["causal_lift", "roi_proof"],
        "forbidden_downstream_uses": ["decision_recommendation"],
        "artifact_refs": [source_ref],
        "workflow_payload": {"calibration_mapping_report": {"status": "mapped"}},
    }
    base.update(overrides)
    return DeterministicReportEnvelope(**base)  # type: ignore[arg-type]


def test_report_serializes_to_dict() -> None:
    payload = report_to_dict(_sample_report())
    assert payload["schema_version"] == DETERMINISTIC_REPORT_SCHEMA_VERSION
    assert payload["report_type"] == ReportType.CALIBRATION_MAPPING.value


def test_report_serializes_to_json() -> None:
    text = report_to_json(_sample_report())
    parsed = json.loads(text)
    assert parsed["report_id"] == "det-report-cal-test"
    assert "causal_lift" in parsed["blocked_claims"]


def test_blocked_claims_and_forbidden_downstream_uses_preserved() -> None:
    report = _sample_report(
        blocked_claims=["causal_lift", "budget_optimization"],
        forbidden_downstream_uses=["decision_recommendation", "budget_optimization"],
    )
    payload = report_to_dict(report)
    assert payload["blocked_claims"] == ["causal_lift", "budget_optimization"]
    assert "budget_optimization" in payload["forbidden_downstream_uses"]


def test_artifact_references_preserved() -> None:
    payload = report_to_dict(_sample_report())
    assert payload["source_input_ref"]["source_fixture_id_or_payload_ref"] == (
        "experiment_readout_valid"
    )
    assert payload["artifact_refs"][0]["artifact_type"] == "stage_a_fixture"


def test_write_report_json_creates_valid_artifact(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "report.json"
    path = write_report_json(_sample_report(), output)
    assert path.is_file()
    parsed = json.loads(path.read_text(encoding="utf-8"))
    assert parsed["schema_version"] == DETERMINISTIC_REPORT_SCHEMA_VERSION


def test_write_report_json_blocks_overwrite_by_default(tmp_path: Path) -> None:
    output = tmp_path / "report.json"
    write_report_json(_sample_report(), output)
    with pytest.raises(DeterministicReportExportError, match="already exists"):
        write_report_json(_sample_report(), output, overwrite=False)


def test_validate_rejects_unsupported_advanced_output_in_workflow_payload() -> None:
    payload = _sample_report().model_dump()
    payload["workflow_payload"] = {"notes": "channel_roi ranking"}
    report = DeterministicReportEnvelope.model_construct(**payload)
    with pytest.raises(DeterministicReportExportError, match="unsupported advanced output"):
        validate_report_has_no_unsupported_advanced_outputs(report)
