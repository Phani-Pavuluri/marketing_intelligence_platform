"""Tests for intake session and path recommendation contracts."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from mip.contracts.intake import (
    DataGrain,
    GeoGrain,
    GeoXIntakeSession,
    IntakeCandidatePath,
    IntakeIntendedUse,
    IntakePathRecommendation,
    IntakeRecommendationStatus,
    MeasurementIntakeSession,
    MeasurementWorkflowKind,
    MMMIntakeSession,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def _session_kwargs(**overrides: Any) -> Any:
    base: dict[str, Any] = {
        "session_id": "sess-001",
        "business_question": "How are paid channels affecting conversions?",
        "intended_use": IntakeIntendedUse.DIAGNOSTIC_ONLY,
        "workflow_kind": MeasurementWorkflowKind.MMM,
        "time_grain": DataGrain.WEEKLY,
        "geo_grain": GeoGrain.NATIONAL,
        "created_at": _NOW,
    }
    base.update(overrides)
    return base


def test_measurement_intake_session_requires_core_fields() -> None:
    session = MeasurementIntakeSession(**_session_kwargs())
    assert session.session_id == "sess-001"
    assert session.unresolved_questions == []
    assert session.warnings == []
    assert session.blocking_reasons == []


def test_measurement_intake_session_rejects_empty_business_question() -> None:
    with pytest.raises(ValidationError, match="business_question"):
        MeasurementIntakeSession(**_session_kwargs(business_question="   "))


def test_mmm_intake_session_accepts_optional_fields() -> None:
    session = MMMIntakeSession(
        **_session_kwargs(requires_calibration=True, model_goal="diagnostic mix review")
    )
    assert session.requires_calibration is True
    assert session.model_goal == "diagnostic mix review"


def test_geox_intake_session_accepts_experiment_fields() -> None:
    session = GeoXIntakeSession(
        **_session_kwargs(
            workflow_kind=MeasurementWorkflowKind.GEOX,
            intended_use=IntakeIntendedUse.GEO_EXPERIMENT_DESIGN,
            experiment_goal="Measure lift in test geos",
            requires_power=True,
        )
    )
    assert session.requires_power is True


def test_blocked_recommendation_requires_blocking_reasons() -> None:
    with pytest.raises(ValidationError, match="blocking_reasons"):
        IntakePathRecommendation(
            recommendation_id="rec-001",
            session_id="sess-001",
            status=IntakeRecommendationStatus.BLOCKED,
            recommended_path=IntakeCandidatePath.BLOCKED_NEEDS_MORE_DATA,
            workflow_kind=MeasurementWorkflowKind.MMM,
            why_this_path="Blocked path.",
            created_at=_NOW,
        )


def test_needs_clarification_requires_next_questions() -> None:
    with pytest.raises(ValidationError, match="required_next_questions"):
        IntakePathRecommendation(
            recommendation_id="rec-001",
            session_id="sess-001",
            status=IntakeRecommendationStatus.NEEDS_CLARIFICATION,
            recommended_path=IntakeCandidatePath.BLOCKED_NEEDS_MORE_DATA,
            workflow_kind=MeasurementWorkflowKind.MMM,
            why_this_path="Needs more detail.",
            created_at=_NOW,
        )


def test_recommendation_rejects_forbidden_claim_fragments() -> None:
    with pytest.raises(ValidationError, match="forbidden claim"):
        IntakePathRecommendation(
            recommendation_id="rec-001",
            session_id="sess-001",
            status=IntakeRecommendationStatus.RECOMMENDED,
            recommended_path=IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM,
            workflow_kind=MeasurementWorkflowKind.MMM,
            why_this_path="The causal effect is confirmed for this channel.",
            created_at=_NOW,
        )


def test_intake_path_recommendation_serializes() -> None:
    rec = IntakePathRecommendation(
        recommendation_id="rec-001",
        session_id="sess-001",
        status=IntakeRecommendationStatus.RECOMMENDED,
        recommended_path=IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM,
        workflow_kind=MeasurementWorkflowKind.MMM,
        why_this_path="Weekly national diagnostic path.",
        created_at=_NOW,
    )
    payload = rec.model_dump()
    assert payload["recommended_path"] == "national_diagnostic_mmm"
    assert payload["status"] == "recommended"
