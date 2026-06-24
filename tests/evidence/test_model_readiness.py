"""Tests for model-scoped calibration readiness."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from mip.contracts import (
    ArtifactStatus,
    CompatibilityStatus,
    ConfidenceTier,
    DiagnosticSummary,
    TimeWindow,
)
from mip.evaluation import reasons as R
from mip.evidence import (
    CalibrationAuditReport,
    EvidenceRegistry,
    ModelCalibrationReadiness,
    audit_calibration_for_model,
    evaluate_model_calibration_readiness,
)
from tests.evidence.conftest import (
    build_calibration,
    build_estimand,
    build_evidence,
)


@pytest.fixture
def registry() -> EvidenceRegistry:
    return EvidenceRegistry()


def test_audit_calibration_for_model_filters_by_target_model_id(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, calibration_id="cal-a", target_model_id="mmm-001")
    )
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, calibration_id="cal-b", target_model_id="mmm-002")
    )
    report = audit_calibration_for_model(registry, "mmm-001")
    assert report.total_signals == 1
    assert report.traces[0].calibration_id == "cal-a"


def test_audit_calibration_for_model_default_audit_id(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, target_model_id="mmm-001")
    )
    report = audit_calibration_for_model(registry, "mmm-001")
    assert report.audit_id == "calibration_audit:mmm-001"


def test_audit_calibration_for_model_explicit_audit_id(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, target_model_id="mmm-001")
    )
    report = audit_calibration_for_model(
        registry,
        "mmm-001",
        audit_id="custom-model-audit",
    )
    assert report.audit_id == "custom-model-audit"


def test_audit_calibration_for_model_explicit_created_at(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, target_model_id="mmm-001")
    )
    ts = datetime(2024, 8, 1, tzinfo=UTC)
    report = audit_calibration_for_model(registry, "mmm-001", created_at=ts)
    assert report.created_at == ts


def test_audit_calibration_for_model_empty_blocked(
    registry: EvidenceRegistry,
) -> None:
    report = audit_calibration_for_model(registry, "mmm-empty")
    assert report.total_signals == 0
    assert report.overall_confidence_tier == ConfidenceTier.BLOCKED


def test_evaluate_readiness_blocks_on_empty_target_model_id(
    registry: EvidenceRegistry,
) -> None:
    with pytest.raises(ValueError, match="target_model_id"):
        evaluate_model_calibration_readiness(registry, "  ")


def test_readiness_blocks_when_no_calibration_signals(registry: EvidenceRegistry) -> None:
    readiness = evaluate_model_calibration_readiness(registry, "mmm-001")
    assert readiness.readiness_tier == ConfidenceTier.BLOCKED
    assert readiness.is_calibration_ready is False


def test_readiness_includes_no_calibration_signals_reason(
    registry: EvidenceRegistry,
) -> None:
    readiness = evaluate_model_calibration_readiness(registry, "mmm-001")
    assert R.NO_CALIBRATION_SIGNALS in readiness.reason_codes


def test_readiness_decision_ready_when_all_signals_pass(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_evidence(
        build_evidence(
            build_estimand(time_window),
            passing_diagnostics,
            evidence_id="exp-001",
            status=ArtifactStatus.CERTIFIED,
            confidence_tier=ConfidenceTier.DECISION_READY,
        )
    )
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            target_model_id="mmm-001",
            weight=0.9,
            freshness_decay=0.9,
            confidence_tier=ConfidenceTier.DECISION_READY,
        )
    )
    readiness = evaluate_model_calibration_readiness(registry, "mmm-001")
    assert readiness.readiness_tier == ConfidenceTier.DECISION_READY
    assert readiness.is_calibration_ready is True


def test_readiness_blocks_when_any_signal_blocked(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-block",
            target_model_id="mmm-001",
            source_evidence_id="exp-missing",
        )
    )
    readiness = evaluate_model_calibration_readiness(registry, "mmm-001")
    assert readiness.readiness_tier == ConfidenceTier.BLOCKED
    assert readiness.is_calibration_ready is False


def test_readiness_includes_blocked_calibration_signal_reason(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, source_evidence_id="exp-missing")
    )
    readiness = evaluate_model_calibration_readiness(registry, "mmm-001")
    assert R.BLOCKED_CALIBRATION_SIGNAL in readiness.reason_codes


def test_readiness_blocks_when_no_compatible_signals(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-a",
            target_model_id="mmm-001",
            compatibility_status=CompatibilityStatus.INCOMPATIBLE,
            weight=0.0,
        )
    )
    readiness = evaluate_model_calibration_readiness(registry, "mmm-001")
    assert readiness.readiness_tier == ConfidenceTier.BLOCKED
    assert R.NO_COMPATIBLE_CALIBRATION_SIGNALS in readiness.reason_codes


def test_readiness_includes_no_compatible_calibration_signals_reason(
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
    readiness = evaluate_model_calibration_readiness(registry, "mmm-001")
    assert R.NO_COMPATIBLE_CALIBRATION_SIGNALS in readiness.reason_codes


def test_readiness_not_calibration_ready_when_warnings_exist(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_evidence(build_evidence(build_estimand(time_window), passing_diagnostics))
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            compatibility_status=CompatibilityStatus.COMPATIBLE,
            freshness_decay=0.2,
            confidence_tier=ConfidenceTier.DIRECTIONAL,
        )
    )
    readiness = evaluate_model_calibration_readiness(registry, "mmm-001")
    assert readiness.is_calibration_ready is False
    assert readiness.readiness_tier != ConfidenceTier.DECISION_READY


def test_readiness_includes_calibration_warnings_present(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_evidence(build_evidence(build_estimand(time_window), passing_diagnostics))
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            compatibility_status=CompatibilityStatus.COMPATIBLE,
            freshness_decay=0.2,
        )
    )
    readiness = evaluate_model_calibration_readiness(registry, "mmm-001")
    assert R.CALIBRATION_WARNINGS_PRESENT in readiness.reason_codes


def test_readiness_includes_trace_reason_codes(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_calibration_signal(
        build_calibration(passing_diagnostics, source_evidence_id="exp-missing")
    )
    readiness = evaluate_model_calibration_readiness(registry, "mmm-001")
    assert R.MISSING_EVIDENCE in readiness.reason_codes


def test_readiness_warnings_are_deduplicated(
    registry: EvidenceRegistry,
    time_window: TimeWindow,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    registry.add_evidence(build_evidence(build_estimand(time_window), passing_diagnostics))
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-a",
            compatibility_status=CompatibilityStatus.PARTIALLY_COMPATIBLE,
        )
    )
    registry.add_calibration_signal(
        build_calibration(
            passing_diagnostics,
            calibration_id="cal-b",
            compatibility_status=CompatibilityStatus.PARTIALLY_COMPATIBLE,
        )
    )
    readiness = evaluate_model_calibration_readiness(registry, "mmm-001")
    assert len(readiness.warnings) == len(set(readiness.warnings))


def test_model_calibration_readiness_validation_inconsistent_counts(
    registry: EvidenceRegistry,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    report = audit_calibration_for_model(registry, "mmm-001")
    with pytest.raises(ValidationError, match="total_signals"):
        ModelCalibrationReadiness(
            target_model_id="mmm-001",
            audit_id=report.audit_id,
            created_at=report.created_at,
            readiness_tier=ConfidenceTier.BLOCKED,
            is_calibration_ready=False,
            total_signals=99,
            traceable_signals=report.traceable_signals,
            missing_source_evidence=report.missing_source_evidence,
            passed_signals=report.passed_signals,
            warned_signals=report.warned_signals,
            blocked_signals=report.blocked_signals,
            compatible_signals=report.compatible_signals,
            partially_compatible_signals=report.partially_compatible_signals,
            unknown_compatibility_signals=report.unknown_compatibility_signals,
            incompatible_signals=report.incompatible_signals,
            reason_codes=[R.NO_CALIBRATION_SIGNALS],
            audit_report=report,
        )


def test_model_calibration_readiness_rejects_ready_without_decision_tier(
    registry: EvidenceRegistry,
) -> None:
    report = CalibrationAuditReport(
        audit_id="calibration_audit:mmm-001",
        created_at=datetime(2025, 1, 1, tzinfo=UTC),
        total_signals=0,
        traceable_signals=0,
        missing_source_evidence=0,
        passed_signals=0,
        warned_signals=0,
        blocked_signals=0,
        compatible_signals=0,
        partially_compatible_signals=0,
        unknown_compatibility_signals=0,
        incompatible_signals=0,
        overall_confidence_tier=ConfidenceTier.BLOCKED,
        traces=[],
    )
    with pytest.raises(ValidationError, match="decision_ready"):
        ModelCalibrationReadiness(
            target_model_id="mmm-001",
            audit_id=report.audit_id,
            created_at=report.created_at,
            readiness_tier=ConfidenceTier.DIRECTIONAL,
            is_calibration_ready=True,
            total_signals=0,
            traceable_signals=0,
            missing_source_evidence=0,
            passed_signals=0,
            warned_signals=0,
            blocked_signals=0,
            compatible_signals=0,
            partially_compatible_signals=0,
            unknown_compatibility_signals=0,
            incompatible_signals=0,
            reason_codes=["X"],
            audit_report=report,
        )


def test_public_imports_from_mip_evidence() -> None:
    from mip.evidence import (
        ModelCalibrationReadiness as readiness_cls,
    )
    from mip.evidence import (
        audit_calibration_for_model as audit_fn,
    )
    from mip.evidence import (
        evaluate_model_calibration_readiness as eval_fn,
    )

    assert readiness_cls is not None
    assert callable(audit_fn)
    assert callable(eval_fn)
