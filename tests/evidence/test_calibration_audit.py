"""Tests for calibration traceability audit."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from mip.contracts import (
    CompatibilityStatus,
    ConfidenceTier,
    DiagnosticSummary,
    TimeWindow,
    TrustReport,
)
from mip.evaluation import reasons as R
from mip.evaluation.gates import GateDecision
from mip.evidence import (
    CalibrationAuditReport,
    CalibrationTrace,
    EvidenceRegistry,
    audit_calibration_registry,
    trace_calibration_signal,
)
from tests.evidence.conftest import (
    build_calibration,
    build_estimand,
    build_evidence,
)


@pytest.fixture
def registry() -> EvidenceRegistry:
    return EvidenceRegistry()


def test_trace_returns_traceable_when_source_evidence_exists(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    estimand = build_estimand(time_window)
    registry.add_evidence(
        build_evidence(estimand, passing_diagnostics, evidence_id="exp-001")
    )
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, calibration_id="cal-001")
    )
    trace = trace_calibration_signal(registry, "cal-001")
    assert trace.source_evidence_found is True
    assert R.MISSING_EVIDENCE not in trace.reason_codes


def test_trace_source_evidence_found_false_when_missing(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-missing",
            source_evidence_id="exp-missing",
        )
    )
    trace = trace_calibration_signal(registry, "cal-missing")
    assert trace.source_evidence_found is False


def test_missing_source_forces_block_decision(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, source_evidence_id="exp-absent")
    )
    trace = trace_calibration_signal(registry, "cal-001")
    assert trace.gate_decision == GateDecision.BLOCK
    assert trace.max_confidence_tier == ConfidenceTier.BLOCKED


def test_missing_source_includes_missing_evidence_reason(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, source_evidence_id="exp-absent")
    )
    trace = trace_calibration_signal(registry, "cal-001")
    assert R.MISSING_EVIDENCE in trace.reason_codes
    assert R.MISSING_EVIDENCE in trace.warnings


def test_trace_includes_trust_report(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_evidence(build_evidence(build_estimand(time_window), passing_diagnostics))
    registry.add_calibration_signal(build_calibration(passing_diagnostics))
    trace = trace_calibration_signal(registry, "cal-001")
    assert isinstance(trace.trust_report, TrustReport)


def test_incompatible_calibration_signal_blocked(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            compatibility_status=CompatibilityStatus.INCOMPATIBLE,
            weight=0.0,
        )
    )
    trace = trace_calibration_signal(registry, "cal-001")
    assert trace.gate_decision == GateDecision.BLOCK
    assert R.INCOMPATIBLE_CALIBRATION in trace.reason_codes


def test_partially_compatible_calibration_warns(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_evidence(build_evidence(build_estimand(time_window), passing_diagnostics))
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            compatibility_status=CompatibilityStatus.PARTIALLY_COMPATIBLE,
            confidence_tier=ConfidenceTier.DIRECTIONAL,
        )
    )
    trace = trace_calibration_signal(registry, "cal-001")
    assert trace.gate_decision == GateDecision.WARN
    assert trace.max_confidence_tier == ConfidenceTier.DIRECTIONAL


def test_audit_empty_registry_blocked_overall(registry: EvidenceRegistry) -> None:
    report = audit_calibration_registry(registry)
    assert report.total_signals == 0
    assert report.overall_confidence_tier == ConfidenceTier.BLOCKED


def test_audit_counts_total_signals(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(build_calibration(passing_diagnostics, calibration_id="cal-a"))
    registry.add_calibration_signal(build_calibration(passing_diagnostics, calibration_id="cal-b"))
    report = audit_calibration_registry(registry)
    assert report.total_signals == 2


def test_audit_counts_traceable_signals(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_evidence(build_evidence(build_estimand(time_window), passing_diagnostics))
    registry.add_calibration_signal(build_calibration(passing_diagnostics, calibration_id="cal-ok"))
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-miss",
            source_evidence_id="exp-missing",
        )
    )
    report = audit_calibration_registry(registry)
    assert report.traceable_signals == 1


def test_audit_counts_missing_source_evidence(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, source_evidence_id="exp-missing")
    )
    report = audit_calibration_registry(registry)
    assert report.missing_source_evidence == 1


def test_audit_counts_pass_warn_block(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_evidence(build_evidence(build_estimand(time_window), passing_diagnostics))
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-pass",
            source_evidence_id="exp-001",
        )
    )
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-warn",
            source_evidence_id="exp-001",
            compatibility_status=CompatibilityStatus.PARTIALLY_COMPATIBLE,
        )
    )
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-block",
            source_evidence_id="exp-missing",
        )
    )
    report = audit_calibration_registry(registry)
    assert report.passed_signals == 1
    assert report.warned_signals == 1
    assert report.blocked_signals == 1


def test_audit_counts_compatibility_statuses(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-compatible",
            compatibility_status=CompatibilityStatus.COMPATIBLE,
        )
    )
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-partial",
            compatibility_status=CompatibilityStatus.PARTIALLY_COMPATIBLE,
        )
    )
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-unknown",
            compatibility_status=CompatibilityStatus.UNKNOWN,
        )
    )
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-incompatible",
            compatibility_status=CompatibilityStatus.INCOMPATIBLE,
            weight=0.0,
        )
    )
    report = audit_calibration_registry(registry)
    assert report.compatible_signals == 1
    assert report.partially_compatible_signals == 1
    assert report.unknown_compatibility_signals == 1
    assert report.incompatible_signals == 1


def test_audit_overall_confidence_is_most_restrictive(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_evidence(build_evidence(build_estimand(time_window), passing_diagnostics))
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-pass",
            confidence_tier=ConfidenceTier.DECISION_READY,
        )
    )
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-warn",
            compatibility_status=CompatibilityStatus.UNKNOWN,
            confidence_tier=ConfidenceTier.DIRECTIONAL,
        )
    )
    report = audit_calibration_registry(registry)
    assert report.overall_confidence_tier == ConfidenceTier.DIAGNOSTIC_ONLY


def test_audit_id_override(registry: EvidenceRegistry) -> None:
    report = audit_calibration_registry(registry, audit_id="custom-audit")
    assert report.audit_id == "custom-audit"


def test_created_at_override(registry: EvidenceRegistry) -> None:
    ts = datetime(2024, 12, 1, tzinfo=UTC)
    report = audit_calibration_registry(registry, created_at=ts)
    assert report.created_at == ts


def test_calibration_audit_report_validation_inconsistent_counts() -> None:
    with pytest.raises(ValidationError, match="total_signals"):
        CalibrationAuditReport(
            audit_id="bad",
            created_at=datetime(2025, 1, 1, tzinfo=UTC),
            total_signals=2,
            traceable_signals=1,
            missing_source_evidence=1,
            passed_signals=1,
            warned_signals=0,
            blocked_signals=0,
            compatible_signals=1,
            partially_compatible_signals=0,
            unknown_compatibility_signals=0,
            incompatible_signals=0,
            overall_confidence_tier=ConfidenceTier.BLOCKED,
            traces=[],
        )


def test_calibration_trace_requires_missing_evidence_reason(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(build_calibration(passing_diagnostics))
    trace = trace_calibration_signal(registry, "cal-001")
    with pytest.raises(ValidationError, match="MISSING_EVIDENCE"):
        CalibrationTrace(
            calibration_id=trace.calibration_id,
            source_evidence_id=trace.source_evidence_id,
            target_model_id=trace.target_model_id,
            source_evidence_found=False,
            compatibility_status=trace.compatibility_status,
            gate_decision=trace.gate_decision,
            max_confidence_tier=trace.max_confidence_tier,
            reason_codes=[],
            warnings=trace.warnings,
            trust_report=trace.trust_report,
        )


def test_public_imports_from_mip_evidence() -> None:
    from mip.evidence import (
        CalibrationAuditReport as report_cls,
    )
    from mip.evidence import (
        CalibrationTrace as trace_cls,
    )
    from mip.evidence import (
        audit_calibration_registry as audit_fn,
    )
    from mip.evidence import (
        trace_calibration_signal as trace_fn,
    )

    assert trace_cls is not None
    assert report_cls is not None
    assert callable(trace_fn)
    assert callable(audit_fn)
