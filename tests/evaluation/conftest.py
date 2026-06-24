"""Fixtures and builders for evaluation gate tests."""

from datetime import UTC, datetime
from typing import Any

import pytest

from mip.contracts import (
    ArtifactStatus,
    CalibrationSignal,
    CompatibilityStatus,
    ConfidenceTier,
    DecisionSurface,
    DecisionSurfaceType,
    DiagnosticSummary,
    Estimand,
    EvidenceRole,
    ExperimentEvidence,
    ExperimentType,
    RecommendationContract,
    RecommendationType,
    TimeWindow,
    TrustReport,
)
from mip.contracts.enums import CausalQuantity


@pytest.fixture
def time_window() -> TimeWindow:
    return TimeWindow(
        start=datetime(2025, 1, 1, tzinfo=UTC),
        end=datetime(2025, 6, 1, tzinfo=UTC),
    )


@pytest.fixture
def delta_mu_estimand(time_window: TimeWindow) -> Estimand:
    return Estimand(
        target_metric="revenue",
        causal_quantity=CausalQuantity.DELTA_MU,
        unit="USD",
        time_window=time_window,
        treatment_definition="+10% spend all channels",
        aggregation_level="full_panel",
    )


@pytest.fixture
def passing_diagnostics() -> DiagnosticSummary:
    return DiagnosticSummary(passed=True)


@pytest.fixture
def failed_diagnostics() -> DiagnosticSummary:
    return DiagnosticSummary(passed=False, failures=["check failed"])


def build_experiment_evidence(
    estimand: Estimand,
    diagnostics: DiagnosticSummary,
    **overrides: Any,
) -> ExperimentEvidence:
    base: dict[str, Any] = {
        "evidence_id": "exp-001",
        "experiment_type": ExperimentType.GEOX,
        "evidence_role": EvidenceRole.CALIBRATION_SIGNAL,
        "estimand": estimand,
        "estimate": 0.05,
        "design_diagnostics": diagnostics,
        "execution_diagnostics": diagnostics,
        "inference_diagnostics": diagnostics,
        "quality_score": 0.9,
        "freshness_score": 0.85,
        "confidence_tier": ConfidenceTier.DIRECTIONAL,
        "status": ArtifactStatus.CERTIFIED,
        "created_at": datetime(2025, 3, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return ExperimentEvidence(**base)


def build_calibration_signal(
    diagnostics: DiagnosticSummary,
    **overrides: Any,
) -> CalibrationSignal:
    base: dict[str, Any] = {
        "calibration_id": "cal-001",
        "source_evidence_id": "exp-001",
        "target_model_id": "mmm-001",
        "compatibility_status": CompatibilityStatus.COMPATIBLE,
        "mapping_type": "channel",
        "lift_scale": "absolute",
        "weight": 0.8,
        "freshness_decay": 0.9,
        "diagnostics": diagnostics,
        "confidence_tier": ConfidenceTier.DIRECTIONAL,
    }
    base.update(overrides)
    return CalibrationSignal(**base)


def build_decision_surface(
    estimand: Estimand,
    **overrides: Any,
) -> DecisionSurface:
    base: dict[str, Any] = {
        "surface_id": "surf-001",
        "model_id": "mmm-001",
        "surface_type": DecisionSurfaceType.FULL_PANEL_DELTA_MU,
        "decision_estimand": estimand,
        "certification_status": ArtifactStatus.CERTIFIED,
        "reliability_scorecard_id": "score-001",
        "artifact_fingerprint": "fp-abc",
        "created_at": datetime(2025, 4, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return DecisionSurface(**base)


def build_recommendation(
    diagnostics: DiagnosticSummary,
    **overrides: Any,
) -> RecommendationContract:
    base: dict[str, Any] = {
        "recommendation_id": "rec-001",
        "recommendation_type": RecommendationType.MONITOR,
        "action": {"channel": "search"},
        "diagnostics_summary": diagnostics,
        "confidence_tier": ConfidenceTier.DIRECTIONAL,
        "created_at": datetime(2025, 5, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return RecommendationContract(**base)


def build_trust_report(
    diagnostics: DiagnosticSummary,
    **overrides: Any,
) -> TrustReport:
    base: dict[str, Any] = {
        "trust_report_id": "trust-001",
        "output_id": "out-001",
        "output_type": "recommendation",
        "confidence_tier": ConfidenceTier.DIRECTIONAL,
        "diagnostics": diagnostics,
        "created_at": datetime(2025, 5, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return TrustReport(**base)
