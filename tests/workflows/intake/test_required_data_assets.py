"""Tests for deterministic required data asset planning."""

from datetime import UTC, datetime
from typing import Any

from mip.contracts.intake import (
    DataGrain,
    GeoGrain,
    IntakeCandidatePath,
    IntakePathRecommendation,
    IntakeRecommendationStatus,
    MeasurementWorkflowKind,
)
from mip.contracts.intake_assets import DataAssetType, SampleColumnRole
from mip.workflows.intake.assets import build_intake_plan
from mip.workflows.intake.recommendation import recommend_intake_path

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

_FORBIDDEN_FRAGMENTS = (
    "roi is",
    "lift estimate",
    "budget allocation",
    "coefficient",
    "causal effect",
)


def _session(**overrides: Any) -> Any:
    from mip.contracts.intake import IntakeIntendedUse, MeasurementIntakeSession

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


def _recommendation(**session_overrides: Any) -> IntakePathRecommendation:
    return recommend_intake_path(_session(**session_overrides))


def _asset_types(plan: Any) -> set[str]:
    types: set[str] = set()
    for asset in plan.required_assets:
        asset_type = asset.asset_type
        types.add(asset_type.value if isinstance(asset_type, DataAssetType) else asset_type)
    return types


def _assert_no_forbidden_claims(plan: Any) -> None:
    text_parts = [
        *plan.warnings,
        *plan.blocking_reasons,
        *plan.next_user_actions,
    ]
    for asset in (
        *plan.required_assets,
        *plan.recommended_assets,
        *plan.optional_assets,
        *plan.blocked_assets,
    ):
        text_parts.append(asset.description)
        text_parts.extend(asset.warnings)
    combined = " ".join(text_parts).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in combined


def test_national_diagnostic_plan_required_assets() -> None:
    plan = build_intake_plan(_recommendation())
    assert DataAssetType.OUTCOME_KPI_DATA.value in _asset_types(plan)
    assert DataAssetType.MEDIA_SPEND_DATA.value in _asset_types(plan)
    assert DataAssetType.CHANNEL_MAPPING.value in _asset_types(plan)
    assert DataAssetType.CALENDAR_SEASONALITY_DATA.value in _asset_types(plan)
    _assert_no_forbidden_claims(plan)


def test_national_diagnostic_plan_includes_sample_rows() -> None:
    plan = build_intake_plan(_recommendation())
    outcome = next(
        asset
        for asset in plan.required_assets
        if asset.asset_type == DataAssetType.OUTCOME_KPI_DATA
    )
    assert outcome.sample_schema is not None
    assert outcome.sample_schema.sample_rows
    assert outcome.sample_schema.sample_rows[0].values["metric_value"] == 12450
    media = next(
        asset
        for asset in plan.required_assets
        if asset.asset_type == DataAssetType.MEDIA_SPEND_DATA
    )
    assert media.sample_schema is not None
    assert any(col.role == SampleColumnRole.SPEND for col in media.sample_schema.required_columns)


def test_geo_level_plan_warns_about_geo_requirements() -> None:
    plan = build_intake_plan(_recommendation(geo_grain=GeoGrain.DMA))
    assert any("geo-level" in warning.lower() for warning in plan.warnings)
    outcome = next(
        asset
        for asset in plan.required_assets
        if asset.asset_type == DataAssetType.OUTCOME_KPI_DATA
    )
    assert outcome.sample_schema is not None
    assert any(col.name == "geo" for col in outcome.sample_schema.required_columns)
    _assert_no_forbidden_claims(plan)


def test_calibrated_mmm_requires_calibration_signal() -> None:
    from mip.contracts.intake import IntakeIntendedUse

    plan = build_intake_plan(
        _recommendation(
            intended_use=IntakeIntendedUse.CALIBRATED_MMM,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    assert DataAssetType.CALIBRATION_SIGNAL_DATA.value in _asset_types(plan)
    calibration = next(
        asset
        for asset in plan.required_assets
        if asset.asset_type == DataAssetType.CALIBRATION_SIGNAL_DATA
    )
    assert calibration.sample_schema is not None
    assert any(
        col.role == SampleColumnRole.EFFECT_ESTIMATE
        for col in calibration.sample_schema.required_columns
    )
    assert any(
        col.role == SampleColumnRole.STANDARD_ERROR
        for col in calibration.sample_schema.required_columns
    )
    _assert_no_forbidden_claims(plan)


def test_geox_design_plan_requires_geo_mapping_and_history() -> None:
    from mip.contracts.intake import IntakeIntendedUse

    plan = build_intake_plan(
        _recommendation(
            workflow_kind=MeasurementWorkflowKind.GEOX,
            intended_use=IntakeIntendedUse.GEO_EXPERIMENT_DESIGN,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    assert DataAssetType.GEO_MAPPING.value in _asset_types(plan)
    assert DataAssetType.OUTCOME_KPI_DATA.value in _asset_types(plan)
    assert any("design quality" in warning.lower() for warning in plan.warnings)
    _assert_no_forbidden_claims(plan)


def test_geox_readout_plan_requires_experiment_export() -> None:
    from mip.contracts.intake import IntakeIntendedUse

    plan = build_intake_plan(
        _recommendation(
            workflow_kind=MeasurementWorkflowKind.GEOX,
            intended_use=IntakeIntendedUse.GEO_EXPERIMENT_READOUT,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    assert DataAssetType.EXPERIMENT_EXPORT_DATA.value in _asset_types(plan)
    assert any("governed experiment export" in warning.lower() for warning in plan.warnings)
    _assert_no_forbidden_claims(plan)


def test_blocked_optimizer_plan_has_no_executable_upload_plan() -> None:
    from mip.contracts.intake import IntakeIntendedUse

    plan = build_intake_plan(
        _recommendation(
            intended_use=IntakeIntendedUse.OPTIMIZER_CANDIDATE,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    assert plan.required_assets == []
    assert plan.blocking_reasons
    assert plan.blocked_assets
    _assert_no_forbidden_claims(plan)


def test_calibration_intake_plan_includes_mapping_assets() -> None:
    plan = build_intake_plan(
        IntakePathRecommendation(
            recommendation_id="sess-001-path-rec",
            session_id="sess-001",
            status=IntakeRecommendationStatus.RECOMMENDED_WITH_WARNINGS,
            recommended_path=IntakeCandidatePath.EXPERIMENT_CALIBRATION_INTAKE,
            workflow_kind=MeasurementWorkflowKind.CALIBRATION_INTAKE,
            why_this_path="Calibration intake path.",
            created_at=_NOW,
        )
    )
    assert DataAssetType.METRIC_MAPPING.value in _asset_types(plan)
    assert DataAssetType.CHANNEL_MAPPING.value in _asset_types(plan)
    _assert_no_forbidden_claims(plan)
