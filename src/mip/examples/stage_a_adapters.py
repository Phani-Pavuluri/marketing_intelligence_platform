"""Stage A fixture adapters for deterministic workflow inputs (Stage A.3)."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from mip.contracts.calibration_intake import (
    CalibrationEvidenceInput,
    CalibrationIntakeStatus,
    CalibrationMappingReport,
    CalibrationMappingRequirement,
)
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
from mip.examples.stage_a_fixtures import (
    load_stage_a_fixture,
)
from mip.workflows.intake.calibration_mapping import map_evidence_to_calibration_signal

_CALIBRATION_FIXTURE_IDS = frozenset(
    {
        "experiment_readout_valid",
        "experiment_readout_missing_se",
        "experiment_readout_metric_mismatch",
    }
)

_CALIBRATION_WORKFLOW = "map_evidence_to_calibration_signal"

_DEFAULT_FORBIDDEN_DOWNSTREAM = (
    "decision_recommendation",
    "budget_optimization",
    "mmm_calibration_executed",
    "causal_certification",
    "roi_proof",
)

_DEFAULT_BLOCKED_CLAIMS = (
    "causal_lift",
    "roi_proof",
    "budget_optimization",
    "mmm_calibration_executed",
    "decision_authorization",
)

_STATUS_TO_GOVERNANCE: dict[str, GovernanceStatus] = {
    CalibrationIntakeStatus.MAPPED.value: GovernanceStatus.CANDIDATE,
    CalibrationIntakeStatus.NEEDS_MORE_DATA.value: GovernanceStatus.NEEDS_MORE_DATA,
    CalibrationIntakeStatus.INCOMPATIBLE.value: GovernanceStatus.INCOMPATIBLE,
    CalibrationIntakeStatus.BLOCKED.value: GovernanceStatus.BLOCKED,
    CalibrationIntakeStatus.READY_FOR_MAPPING.value: GovernanceStatus.DIAGNOSTIC_ONLY,
    CalibrationIntakeStatus.DRAFT.value: GovernanceStatus.DIAGNOSTIC_ONLY,
}


class StageAAdapterError(Exception):
    """Raised when a Stage A fixture cannot be adapted to a workflow input."""


def list_supported_calibration_fixture_ids() -> list[str]:
    """Return calibration fixture IDs supported by Stage A.3 adapters."""
    return sorted(_CALIBRATION_FIXTURE_IDS)


def _assert_calibration_fixture_id(fixture_id: str) -> None:
    if fixture_id not in _CALIBRATION_FIXTURE_IDS:
        msg = (
            f"fixture_id {fixture_id!r} is not a supported calibration fixture; "
            f"supported: {sorted(_CALIBRATION_FIXTURE_IDS)}"
        )
        raise StageAAdapterError(msg)


def build_calibration_input_from_stage_a_fixture(fixture_id: str) -> dict[str, Any]:
    """Load a Stage A calibration fixture and return evidence/requirement payloads."""
    _assert_calibration_fixture_id(fixture_id)
    payload = load_stage_a_fixture(fixture_id)
    if payload.get("workflow_area") != "calibration_mapping":
        msg = f"fixture {fixture_id!r} is not a calibration_mapping fixture"
        raise StageAAdapterError(msg)
    evidence = payload.get("evidence")
    requirement = payload.get("requirement")
    if not isinstance(evidence, dict) or not isinstance(requirement, dict):
        msg = f"fixture {fixture_id!r} is missing evidence/requirement objects"
        raise StageAAdapterError(msg)
    return {
        "fixture_id": fixture_id,
        "synthetic": payload.get("synthetic") is True,
        "workflow_area": payload.get("workflow_area"),
        "demo_journey": payload.get("demo_journey"),
        "evidence_level": payload.get("evidence_level"),
        "expected_status": payload.get("expected_status"),
        "requires_mmm_or_geox_engine": payload.get("requires_mmm_or_geox_engine") is False,
        "evidence": evidence,
        "requirement": requirement,
    }


def _fixture_artifact_reference(
    fixture_id: str,
    *,
    created_at: datetime,
    governance_status: GovernanceStatus,
) -> ArtifactReference:
    return ArtifactReference(
        artifact_id=f"stage-a-fixture:{fixture_id}",
        artifact_type="stage_a_fixture",
        source_workflow="mip.examples.stage_a_fixtures.load_stage_a_fixture",
        source_fixture_id_or_payload_ref=fixture_id,
        source_commit_or_version=default_package_version_label(),
        created_at=created_at,
        governance_status=governance_status,
        evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
        allowed_downstream_uses=["diagnostic_review", "calibration_mapping_candidate"],
        forbidden_downstream_uses=list(_DEFAULT_FORBIDDEN_DOWNSTREAM),
    )


def _governance_status_for_mapping(status: str) -> GovernanceStatus:
    return _STATUS_TO_GOVERNANCE.get(status, GovernanceStatus.UNSUPPORTED)


def _summary_for_mapping_report(
    fixture_id: str,
    mapping_report: CalibrationMappingReport,
) -> str:
    status = str(mapping_report.status)
    if status == CalibrationIntakeStatus.MAPPED.value:
        return (
            f"Stage A calibration fixture {fixture_id} mapped structurally to a "
            "diagnostic calibration candidate. MMM calibration execution remains deferred."
        )
    if status == CalibrationIntakeStatus.NEEDS_MORE_DATA.value:
        return (
            f"Stage A calibration fixture {fixture_id} requires additional governed "
            "fields before calibration mapping can proceed."
        )
    if status == CalibrationIntakeStatus.INCOMPATIBLE.value:
        return (
            f"Stage A calibration fixture {fixture_id} is incompatible with the "
            "stated calibration requirement."
        )
    return f"Stage A calibration fixture {fixture_id} produced status {status}."


def _findings_from_mapping_report(
    mapping_report: CalibrationMappingReport,
) -> list[ReportFinding]:
    findings: list[ReportFinding] = []
    for index, reason in enumerate(mapping_report.blocking_reasons):
        findings.append(
            ReportFinding(
                finding_id=f"blocking-{index}",
                severity=FindingSeverity.BLOCKING,
                message=reason,
            )
        )
    for index, field_name in enumerate(mapping_report.missing_fields):
        findings.append(
            ReportFinding(
                finding_id=f"missing-{index}",
                severity=FindingSeverity.BLOCKING,
                message=f"Missing field: {field_name}",
                field_ref=field_name,
            )
        )
    for index, field_name in enumerate(mapping_report.incompatible_fields):
        findings.append(
            ReportFinding(
                finding_id=f"incompatible-{index}",
                severity=FindingSeverity.BLOCKING,
                message=f"Incompatible field: {field_name}",
                field_ref=field_name,
            )
        )
    for index, warning in enumerate(mapping_report.warnings):
        findings.append(
            ReportFinding(
                finding_id=f"warning-{index}",
                severity=FindingSeverity.WARNING,
                message=warning,
            )
        )
    return findings


def build_calibration_report_envelope(
    fixture_id: str,
    mapping_report: CalibrationMappingReport,
    *,
    generated_at: datetime | None = None,
    report_id: str | None = None,
) -> DeterministicReportEnvelope:
    """Build a deterministic report envelope from a calibration mapping report."""
    _assert_calibration_fixture_id(fixture_id)
    governance_status = _governance_status_for_mapping(str(mapping_report.status))
    created_at = generated_at or mapping_report.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=UTC)

    source_ref = _fixture_artifact_reference(
        fixture_id,
        created_at=created_at,
        governance_status=governance_status,
    )
    workflow_payload: dict[str, Any] = {
        "calibration_mapping_report": mapping_report.model_dump(mode="json"),
    }
    if mapping_report.mapped_signal is not None:
        workflow_payload["calibration_signal"] = mapping_report.mapped_signal.model_dump(
            mode="json"
        )

    return DeterministicReportEnvelope(
        report_id=report_id or f"det-report-cal-{fixture_id}",
        report_type=ReportType.CALIBRATION_MAPPING,
        schema_version=DETERMINISTIC_REPORT_SCHEMA_VERSION,
        source_workflow=_CALIBRATION_WORKFLOW,
        source_input_ref=source_ref,
        generated_at=created_at,
        evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
        governance_status=governance_status,
        summary=_summary_for_mapping_report(fixture_id, mapping_report),
        findings=_findings_from_mapping_report(mapping_report),
        recommended_next_steps=list(mapping_report.allowed_next_steps),
        missing_data=list(mapping_report.missing_fields),
        blocked_claims=list(_DEFAULT_BLOCKED_CLAIMS),
        allowed_downstream_uses=["diagnostic_review", "education"],
        forbidden_downstream_uses=list(
            dict.fromkeys(
                [
                    *mapping_report.blocked_next_steps,
                    *_DEFAULT_FORBIDDEN_DOWNSTREAM,
                ]
            )
        ),
        artifact_refs=[source_ref],
        workflow_payload=workflow_payload,
    )


def run_calibration_mapping_for_stage_a_fixture(
    fixture_id: str,
    *,
    generated_at: datetime | None = None,
    report_id: str | None = None,
) -> DeterministicReportEnvelope:
    """Adapt a Stage A calibration fixture, run mapping, and return a report envelope."""
    adapter_input = build_calibration_input_from_stage_a_fixture(fixture_id)
    evidence = CalibrationEvidenceInput(**adapter_input["evidence"])
    requirement = CalibrationMappingRequirement(**adapter_input["requirement"])
    _signal, mapping_report = map_evidence_to_calibration_signal(evidence, requirement)
    return build_calibration_report_envelope(
        fixture_id,
        mapping_report,
        generated_at=generated_at,
        report_id=report_id,
    )
