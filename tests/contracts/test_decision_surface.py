"""Tests for decision surface contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from mip.contracts import (
    ArtifactStatus,
    CausalQuantity,
    DecisionSurface,
    DecisionSurfaceType,
    Estimand,
    TimeWindow,
)


def test_full_panel_delta_mu_requires_delta_mu_estimand(time_window: TimeWindow) -> None:
    wrong_estimand = Estimand(
        target_metric="revenue",
        causal_quantity=CausalQuantity.LIFT,
        unit="USD",
        time_window=time_window,
        treatment_definition="+10% spend",
        aggregation_level="full_panel",
    )
    with pytest.raises(ValidationError, match="delta_mu estimand"):
        DecisionSurface(
            surface_id="surf-001",
            model_id="mmm-001",
            surface_type=DecisionSurfaceType.FULL_PANEL_DELTA_MU,
            decision_estimand=wrong_estimand,
            certification_status=ArtifactStatus.DRAFT,
            artifact_fingerprint="abc123",
            created_at=datetime(2025, 4, 1, tzinfo=UTC),
        )


def test_certified_surface_must_be_full_panel_delta_mu(
    delta_mu_estimand: Estimand,
) -> None:
    with pytest.raises(ValidationError, match="full_panel_delta_mu"):
        DecisionSurface(
            surface_id="surf-002",
            model_id="mmm-001",
            surface_type=DecisionSurfaceType.DECOMPOSITION,
            decision_estimand=delta_mu_estimand,
            certification_status=ArtifactStatus.CERTIFIED,
            reliability_scorecard_id="score-001",
            artifact_fingerprint="abc123",
            created_at=datetime(2025, 4, 1, tzinfo=UTC),
        )


def test_certified_requires_reliability_scorecard(delta_mu_estimand: Estimand) -> None:
    with pytest.raises(ValidationError, match="reliability_scorecard_id"):
        DecisionSurface(
            surface_id="surf-003",
            model_id="mmm-001",
            surface_type=DecisionSurfaceType.FULL_PANEL_DELTA_MU,
            decision_estimand=delta_mu_estimand,
            certification_status=ArtifactStatus.CERTIFIED,
            artifact_fingerprint="abc123",
            created_at=datetime(2025, 4, 1, tzinfo=UTC),
        )


def test_valid_certified_full_panel_surface(delta_mu_estimand: Estimand) -> None:
    surface = DecisionSurface(
        surface_id="surf-004",
        model_id="mmm-001",
        surface_type=DecisionSurfaceType.FULL_PANEL_DELTA_MU,
        decision_estimand=delta_mu_estimand,
        certification_status=ArtifactStatus.CERTIFIED,
        reliability_scorecard_id="score-001",
        artifact_fingerprint="abc123",
        created_at=datetime(2025, 4, 1, tzinfo=UTC),
    )
    assert surface.surface_type == DecisionSurfaceType.FULL_PANEL_DELTA_MU
