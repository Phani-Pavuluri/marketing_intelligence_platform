"""Builders for evidence registry tests."""

from datetime import UTC, datetime
from typing import Any

import pytest

from mip.contracts import (
    ArtifactStatus,
    CalibrationSignal,
    CompatibilityStatus,
    ConfidenceTier,
    DiagnosticSummary,
    Estimand,
    EvidenceRole,
    ExperimentEvidence,
    ExperimentType,
    TimeWindow,
)
from mip.contracts.enums import CausalQuantity


@pytest.fixture
def passing_diagnostics() -> DiagnosticSummary:
    return DiagnosticSummary(passed=True)


@pytest.fixture
def time_window() -> TimeWindow:
    return TimeWindow(
        start=datetime(2025, 1, 1, tzinfo=UTC),
        end=datetime(2025, 6, 1, tzinfo=UTC),
    )


def build_estimand(
    time_window: TimeWindow,
    *,
    target_metric: str = "revenue",
    causal_quantity: CausalQuantity = CausalQuantity.LIFT,
    scope: dict[str, str | list[str]] | None = None,
) -> Estimand:
    return Estimand(
        target_metric=target_metric,
        causal_quantity=causal_quantity,
        unit="USD",
        time_window=time_window,
        treatment_definition="holdout",
        aggregation_level="geo",
        scope=scope or {},
    )


def build_evidence(
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
        "quality_score": 0.8,
        "freshness_score": 0.7,
        "confidence_tier": ConfidenceTier.DIRECTIONAL,
        "status": ArtifactStatus.VALIDATED,
        "created_at": datetime(2025, 3, 1, tzinfo=UTC),
    }
    base.update(overrides)
    return ExperimentEvidence(**base)


def build_calibration(
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
        "weight": 0.6,
        "freshness_decay": 0.8,
        "diagnostics": diagnostics,
        "confidence_tier": ConfidenceTier.DIRECTIONAL,
    }
    base.update(overrides)
    return CalibrationSignal(**base)
