"""Tests for experiment evidence contracts."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from mip.contracts import (
    ArtifactStatus,
    ConfidenceTier,
    DiagnosticSummary,
    Estimand,
    EvidenceRole,
    ExperimentEvidence,
    ExperimentType,
)


def _evidence_kwargs(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
    **overrides: object,
) -> Any:
    base = {
        "evidence_id": "exp-001",
        "experiment_type": ExperimentType.GEOX,
        "evidence_role": EvidenceRole.CALIBRATION_SIGNAL,
        "estimand": delta_mu_estimand,
        "estimate": 0.05,
        "design_diagnostics": passing_diagnostics,
        "execution_diagnostics": passing_diagnostics,
        "inference_diagnostics": passing_diagnostics,
        "quality_score": 0.9,
        "freshness_score": 0.85,
        "confidence_tier": ConfidenceTier.DIRECTIONAL,
        "status": ArtifactStatus.DRAFT,
        "created_at": datetime(2025, 3, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return base


def test_valid_experiment_evidence(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = ExperimentEvidence(**_evidence_kwargs(delta_mu_estimand, passing_diagnostics))
    assert evidence.evidence_id == "exp-001"


def test_diagnostic_summary_failed_without_detail_rejected() -> None:
    with pytest.raises(ValidationError, match="warning or failure"):
        DiagnosticSummary(passed=False)


def test_invalid_confidence_interval(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="lower bound"):
        ExperimentEvidence(
            **_evidence_kwargs(
                delta_mu_estimand,
                passing_diagnostics,
                confidence_interval=(0.2, 0.1),
            )
        )


def test_decision_ready_requires_passing_diagnostics(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
    failed_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="design diagnostics"):
        ExperimentEvidence(
            **_evidence_kwargs(
                delta_mu_estimand,
                passing_diagnostics,
                confidence_tier=ConfidenceTier.DECISION_READY,
                status=ArtifactStatus.VALIDATED,
                design_diagnostics=failed_diagnostics,
            )
        )


def test_decision_ready_requires_validated_status(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="validated or certified"):
        ExperimentEvidence(
            **_evidence_kwargs(
                delta_mu_estimand,
                passing_diagnostics,
                confidence_tier=ConfidenceTier.DECISION_READY,
                status=ArtifactStatus.DRAFT,
            )
        )


def test_certified_cannot_be_blocked_tier(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    with pytest.raises(ValidationError, match="research_only or blocked"):
        ExperimentEvidence(
            **_evidence_kwargs(
                delta_mu_estimand,
                passing_diagnostics,
                status=ArtifactStatus.CERTIFIED,
                confidence_tier=ConfidenceTier.BLOCKED,
            )
        )
