"""Tests for contract enumerations."""

from mip.contracts.enums import (
    ArtifactStatus,
    CausalQuantity,
    CompatibilityStatus,
    ConfidenceTier,
    DecisionSurfaceType,
    EvidenceRole,
    ExperimentType,
    RecommendationType,
)


def test_confidence_tier_values() -> None:
    assert ConfidenceTier.DECISION_READY.value == "decision_ready"
    assert ConfidenceTier.BLOCKED.value == "blocked"
    assert len(ConfidenceTier) == 5


def test_artifact_status_values() -> None:
    assert ArtifactStatus.CERTIFIED.value == "certified"
    assert ArtifactStatus.DRAFT.value == "draft"


def test_experiment_type_values() -> None:
    assert ExperimentType.GEOX.value == "geox"
    assert ExperimentType.CALIBRATION_EXPERIMENT.value == "calibration_experiment"


def test_causal_quantity_values() -> None:
    assert CausalQuantity.DELTA_MU.value == "delta_mu"
    assert CausalQuantity.IROAS.value == "iroas"


def test_evidence_role_values() -> None:
    assert EvidenceRole.CALIBRATION_SIGNAL.value == "calibration_signal"


def test_compatibility_status_values() -> None:
    assert CompatibilityStatus.INCOMPATIBLE.value == "incompatible"


def test_recommendation_type_values() -> None:
    assert RecommendationType.BUDGET_SHIFT.value == "budget_shift"


def test_decision_surface_type_values() -> None:
    assert DecisionSurfaceType.FULL_PANEL_DELTA_MU.value == "full_panel_delta_mu"
    assert DecisionSurfaceType.DECOMPOSITION.value == "decomposition"
