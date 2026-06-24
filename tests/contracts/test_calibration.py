"""Tests for calibration signal contracts."""

import pytest
from pydantic import ValidationError

from mip.contracts import (
    CalibrationSignal,
    CompatibilityStatus,
    ConfidenceTier,
    DiagnosticSummary,
)


def test_incompatible_calibration_must_have_zero_weight(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="weight 0"):
        CalibrationSignal(
            calibration_id="cal-001",
            source_evidence_id="exp-001",
            target_model_id="mmm-001",
            compatibility_status=CompatibilityStatus.INCOMPATIBLE,
            mapping_type="channel",
            lift_scale="absolute",
            weight=0.5,
            diagnostics=passing_diagnostics,
            confidence_tier=ConfidenceTier.RESEARCH_ONLY,
        )


def test_decision_ready_calibration_requires_compatible(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="compatible status"):
        CalibrationSignal(
            calibration_id="cal-002",
            source_evidence_id="exp-001",
            target_model_id="mmm-001",
            compatibility_status=CompatibilityStatus.PARTIALLY_COMPATIBLE,
            mapping_type="channel",
            lift_scale="absolute",
            weight=0.8,
            diagnostics=passing_diagnostics,
            confidence_tier=ConfidenceTier.DECISION_READY,
        )


def test_decision_ready_calibration_requires_passing_diagnostics(
    failed_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="passing diagnostics"):
        CalibrationSignal(
            calibration_id="cal-003",
            source_evidence_id="exp-001",
            target_model_id="mmm-001",
            compatibility_status=CompatibilityStatus.COMPATIBLE,
            mapping_type="channel",
            lift_scale="absolute",
            weight=0.8,
            diagnostics=failed_diagnostics,
            confidence_tier=ConfidenceTier.DECISION_READY,
        )


def test_valid_incompatible_zero_weight(passing_diagnostics: DiagnosticSummary) -> None:
    signal = CalibrationSignal(
        calibration_id="cal-004",
        source_evidence_id="exp-001",
        target_model_id="mmm-001",
        compatibility_status=CompatibilityStatus.INCOMPATIBLE,
        mapping_type="channel",
        lift_scale="absolute",
        weight=0.0,
        diagnostics=passing_diagnostics,
        confidence_tier=ConfidenceTier.BLOCKED,
    )
    assert signal.weight == 0.0
