"""Tests for deterministic intake path recommendation."""

from datetime import UTC, datetime
from typing import Any

from mip.contracts.intake import (
    DataGrain,
    GeoGrain,
    IntakeCandidatePath,
    IntakeIntendedUse,
    IntakeRecommendationStatus,
    MeasurementIntakeSession,
    MeasurementWorkflowKind,
)
from mip.workflows.intake.recommendation import recommend_intake_path

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

_FORBIDDEN_FRAGMENTS = (
    "roi is",
    "lift estimate",
    "budget allocation",
    "coefficient",
    "causal effect",
)


def _session(**overrides: Any) -> MeasurementIntakeSession:
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
    return MeasurementIntakeSession(**base)


def _assert_no_forbidden_claims(rec: object) -> None:
    from mip.contracts.intake import IntakePathRecommendation

    assert isinstance(rec, IntakePathRecommendation)
    text_parts = [
        rec.why_this_path,
        *rec.why_other_paths_blocked,
        *rec.warnings,
        *rec.allowed_next_steps,
        *rec.blocked_next_steps,
    ]
    combined = " ".join(text_parts).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in combined


def test_mmm_weekly_national_diagnostic_path() -> None:
    rec = recommend_intake_path(_session())
    assert rec.recommended_path == IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM
    assert rec.status == IntakeRecommendationStatus.RECOMMENDED
    _assert_no_forbidden_claims(rec)


def test_mmm_geo_grain_recommends_geo_level_with_warning() -> None:
    rec = recommend_intake_path(_session(geo_grain=GeoGrain.DMA))
    assert rec.recommended_path == IntakeCandidatePath.GEO_LEVEL_MMM
    assert rec.status == IntakeRecommendationStatus.RECOMMENDED_WITH_WARNINGS
    assert any("geo-level" in warning.lower() for warning in rec.warnings)
    _assert_no_forbidden_claims(rec)


def test_mmm_calibrated_use_warns_on_calibration_signal() -> None:
    rec = recommend_intake_path(
        _session(
            intended_use=IntakeIntendedUse.CALIBRATED_MMM,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    assert rec.recommended_path == IntakeCandidatePath.CALIBRATED_MMM
    assert any("CalibrationSignal" in warning for warning in rec.warnings)
    _assert_no_forbidden_claims(rec)


def test_mmm_decision_surface_candidate_blocks_optimizer_next_steps() -> None:
    rec = recommend_intake_path(
        _session(
            intended_use=IntakeIntendedUse.DECISION_SURFACE_CANDIDATE,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    assert rec.recommended_path == IntakeCandidatePath.DECISION_SURFACE_CERTIFICATION
    assert rec.status == IntakeRecommendationStatus.RECOMMENDED_WITH_WARNINGS
    assert "optimizer recommendation" in rec.blocked_next_steps
    assert "budget recommendation" in rec.blocked_next_steps
    _assert_no_forbidden_claims(rec)


def test_mmm_optimizer_candidate_is_blocked() -> None:
    rec = recommend_intake_path(
        _session(
            intended_use=IntakeIntendedUse.OPTIMIZER_CANDIDATE,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    assert rec.recommended_path == IntakeCandidatePath.BLOCKED_NEEDS_MORE_DATA
    assert rec.status == IntakeRecommendationStatus.BLOCKED
    assert rec.blocking_reasons
    _assert_no_forbidden_claims(rec)


def test_geox_design_path() -> None:
    rec = recommend_intake_path(
        _session(
            workflow_kind=MeasurementWorkflowKind.GEOX,
            intended_use=IntakeIntendedUse.GEO_EXPERIMENT_DESIGN,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    assert rec.recommended_path == IntakeCandidatePath.GEO_EXPERIMENT_DESIGN
    assert rec.status == IntakeRecommendationStatus.RECOMMENDED
    _assert_no_forbidden_claims(rec)


def test_geox_readout_path_warns_on_evidence() -> None:
    rec = recommend_intake_path(
        _session(
            workflow_kind=MeasurementWorkflowKind.GEOX,
            intended_use=IntakeIntendedUse.GEO_EXPERIMENT_READOUT,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    assert rec.recommended_path == IntakeCandidatePath.GEO_EXPERIMENT_READOUT
    assert any("governed experiment export" in warning.lower() for warning in rec.warnings)
    _assert_no_forbidden_claims(rec)


def test_calibration_intake_warns_on_calibration_signal() -> None:
    rec = recommend_intake_path(
        _session(
            workflow_kind=MeasurementWorkflowKind.CALIBRATION_INTAKE,
            intended_use=IntakeIntendedUse.CALIBRATED_MMM,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    assert rec.recommended_path == IntakeCandidatePath.EXPERIMENT_CALIBRATION_INTAKE
    assert any("CalibrationSignal" in warning for warning in rec.warnings)
    _assert_no_forbidden_claims(rec)


def test_decision_review_packet_warns_on_trust_and_approval() -> None:
    rec = recommend_intake_path(
        _session(
            workflow_kind=MeasurementWorkflowKind.DECISION_REVIEW,
            intended_use=IntakeIntendedUse.DECISION_REVIEW_PACKET,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    assert rec.recommended_path == IntakeCandidatePath.DECISION_REVIEW_PACKET
    assert any("TrustReport" in warning for warning in rec.warnings)
    assert any("approval" in warning.lower() for warning in rec.warnings)
    _assert_no_forbidden_claims(rec)


def test_missing_required_fields_needs_clarification() -> None:
    session = MeasurementIntakeSession.model_construct(
        session_id="sess-002",
        business_question="",
        intended_use=IntakeIntendedUse.DIAGNOSTIC_ONLY,
        workflow_kind=MeasurementWorkflowKind.MMM,
        created_at=_NOW,
    )
    rec = recommend_intake_path(session)
    assert rec.status == IntakeRecommendationStatus.NEEDS_CLARIFICATION
    assert rec.recommended_path == IntakeCandidatePath.BLOCKED_NEEDS_MORE_DATA
    assert rec.required_next_questions
    _assert_no_forbidden_claims(rec)


def test_missing_metric_and_estimand_add_warnings_not_block() -> None:
    rec = recommend_intake_path(_session())
    assert rec.status == IntakeRecommendationStatus.RECOMMENDED
    assert any("metric_id" in question for question in rec.required_next_questions)
    assert any("estimand_id" in question for question in rec.required_next_questions)
    _assert_no_forbidden_claims(rec)
