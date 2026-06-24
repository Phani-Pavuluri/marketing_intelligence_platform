"""Tests for trust report contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from mip.contracts import ConfidenceTier, DiagnosticSummary, TrustReport


def test_decision_ready_trust_requires_passing_diagnostics(
    failed_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="passing diagnostics"):
        TrustReport(
            trust_report_id="trust-001",
            output_id="out-001",
            output_type="recommendation",
            confidence_tier=ConfidenceTier.DECISION_READY,
            diagnostics=failed_diagnostics,
            created_at=datetime(2025, 5, 1, tzinfo=UTC),
        )


def test_blocked_trust_requires_warnings_or_unsupported(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="warnings or unsupported"):
        TrustReport(
            trust_report_id="trust-002",
            output_id="out-002",
            output_type="mmm_surface",
            confidence_tier=ConfidenceTier.BLOCKED,
            diagnostics=passing_diagnostics,
            created_at=datetime(2025, 5, 1, tzinfo=UTC),
        )


def test_valid_decision_ready_trust(passing_diagnostics: DiagnosticSummary) -> None:
    report = TrustReport(
        trust_report_id="trust-003",
        output_id="out-003",
        output_type="recommendation",
        confidence_tier=ConfidenceTier.DECISION_READY,
        diagnostics=passing_diagnostics,
        created_at=datetime(2025, 5, 1, tzinfo=UTC),
    )
    assert report.confidence_tier == ConfidenceTier.DECISION_READY


def test_public_imports() -> None:
    from mip.contracts import (
        CalibrationSignal,
        ConfidenceTier,
        DecisionSurface,
        Estimand,
        ExperimentEvidence,
        RecommendationContract,
        TrustReport,
    )

    assert ConfidenceTier.DECISION_READY.value == "decision_ready"
    assert Estimand is not None
    assert ExperimentEvidence is not None
    assert CalibrationSignal is not None
    assert DecisionSurface is not None
    assert RecommendationContract is not None
    assert TrustReport is not None
