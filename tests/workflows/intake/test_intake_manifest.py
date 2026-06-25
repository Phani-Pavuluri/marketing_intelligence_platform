"""Tests for deterministic intake manifest assembly."""

from datetime import UTC, datetime
from typing import Any

from mip.contracts.intake import (
    DataGrain,
    GeoGrain,
    IntakeCandidatePath,
    IntakeIntendedUse,
    IntakePathRecommendation,
    IntakeRecommendationStatus,
    MeasurementIntakeSession,
    MeasurementWorkflowKind,
)
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import (
    DataSourceMode,
    DataSourceType,
    GeoXIntakeManifest,
    IntakeManifestStatus,
    MMMIntakeManifest,
    UploadedFileSourceRef,
)
from mip.workflows.intake.assets import build_intake_plan
from mip.workflows.intake.manifest import build_intake_manifest
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
        "metric_id": "conversions",
        "estimand_id": "incremental_conversions",
        "created_at": _NOW,
    }
    base.update(overrides)
    return MeasurementIntakeSession(**base)


def _source(asset_type: DataAssetType, source_id: str) -> UploadedFileSourceRef:
    return UploadedFileSourceRef(
        source_id=source_id,
        source_mode=DataSourceMode.STREAMLIT_FILE_UPLOAD,
        source_type=DataSourceType.FILE,
        asset_type=asset_type,
        uri_or_table_ref=f"upload://sess-001/{source_id}.csv",
        created_at=_NOW,
    )


def _assert_no_forbidden_claims(manifest: MMMIntakeManifest | GeoXIntakeManifest) -> None:
    text_parts = [*manifest.warnings, *manifest.blocking_reasons]
    combined = " ".join(text_parts).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in combined


def test_mmm_manifest_groups_sources_by_asset_type() -> None:
    recommendation = recommend_intake_path(_session())
    plan = build_intake_plan(recommendation)
    sources = [
        _source(DataAssetType.OUTCOME_KPI_DATA, "outcome"),
        _source(DataAssetType.MEDIA_SPEND_DATA, "media"),
        _source(DataAssetType.CHANNEL_MAPPING, "channel-map"),
        _source(DataAssetType.CALENDAR_SEASONALITY_DATA, "calendar"),
    ]
    manifest = build_intake_manifest(_session(), recommendation, plan, sources)
    assert isinstance(manifest, MMMIntakeManifest)
    assert manifest.outcome_source is not None
    assert manifest.outcome_source.source_id == "outcome"
    assert len(manifest.media_sources) == 1
    assert len(manifest.mapping_sources) == 1
    assert len(manifest.control_sources) == 1
    _assert_no_forbidden_claims(manifest)


def test_geox_manifest_groups_sources() -> None:
    recommendation = recommend_intake_path(
        _session(
            workflow_kind=MeasurementWorkflowKind.GEOX,
            intended_use=IntakeIntendedUse.GEO_EXPERIMENT_READOUT,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    plan = build_intake_plan(recommendation)
    sources = [
        _source(DataAssetType.EXPERIMENT_EXPORT_DATA, "experiment"),
        _source(DataAssetType.OUTCOME_KPI_DATA, "outcome"),
        _source(DataAssetType.GEO_MAPPING, "geo-map"),
    ]
    manifest = build_intake_manifest(
        _session(
            workflow_kind=MeasurementWorkflowKind.GEOX,
            intended_use=IntakeIntendedUse.GEO_EXPERIMENT_READOUT,
        ),
        recommendation,
        plan,
        sources,
    )
    assert isinstance(manifest, GeoXIntakeManifest)
    assert manifest.experiment_export_sources[0].source_id == "experiment"
    assert manifest.geo_mapping_source is not None
    _assert_no_forbidden_claims(manifest)


def test_manifest_missing_required_sources_needs_data_sources() -> None:
    recommendation = recommend_intake_path(_session())
    plan = build_intake_plan(recommendation)
    manifest = build_intake_manifest(
        _session(),
        recommendation,
        plan,
        [_source(DataAssetType.OUTCOME_KPI_DATA, "outcome")],
    )
    assert manifest.status == IntakeManifestStatus.NEEDS_DATA_SOURCES
    assert any("missing data source" in warning.lower() for warning in manifest.warnings)
    _assert_no_forbidden_claims(manifest)


def test_manifest_with_all_required_sources_ready_for_validation() -> None:
    recommendation = recommend_intake_path(_session())
    plan = build_intake_plan(recommendation)
    sources = [
        _source(DataAssetType.OUTCOME_KPI_DATA, "outcome"),
        _source(DataAssetType.MEDIA_SPEND_DATA, "media"),
        _source(DataAssetType.CHANNEL_MAPPING, "channel-map"),
        _source(DataAssetType.CALENDAR_SEASONALITY_DATA, "calendar"),
    ]
    manifest = build_intake_manifest(_session(), recommendation, plan, sources)
    assert manifest.status == IntakeManifestStatus.READY_FOR_VALIDATION
    _assert_no_forbidden_claims(manifest)


def test_blocked_optimizer_manifest_is_blocked() -> None:
    recommendation = recommend_intake_path(
        _session(
            intended_use=IntakeIntendedUse.OPTIMIZER_CANDIDATE,
            geo_grain=GeoGrain.UNKNOWN,
            time_grain=DataGrain.UNKNOWN,
        )
    )
    plan = build_intake_plan(recommendation)
    manifest = build_intake_manifest(_session(), recommendation, plan, [])
    assert manifest.status == IntakeManifestStatus.BLOCKED
    assert manifest.blocking_reasons
    assert isinstance(manifest, MMMIntakeManifest)
    assert manifest.outcome_source is None
    _assert_no_forbidden_claims(manifest)


def test_manifest_preserves_session_recommendation_plan_ids() -> None:
    recommendation = recommend_intake_path(_session())
    plan = build_intake_plan(recommendation)
    manifest = build_intake_manifest(_session(), recommendation, plan, [])
    assert manifest.session_id == "sess-001"
    assert manifest.recommendation_id == recommendation.recommendation_id
    assert manifest.plan_id == plan.plan_id
    assert manifest.metric_id == "conversions"
    assert manifest.estimand_id == "incremental_conversions"
    assert manifest.recommended_path == IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM
    _assert_no_forbidden_claims(manifest)


def test_blocked_recommendation_produces_blocked_manifest() -> None:
    recommendation = IntakePathRecommendation(
        recommendation_id="sess-001-path-rec",
        session_id="sess-001",
        status=IntakeRecommendationStatus.BLOCKED,
        recommended_path=IntakeCandidatePath.BLOCKED_NEEDS_MORE_DATA,
        workflow_kind=MeasurementWorkflowKind.MMM,
        why_this_path="Blocked pending clarification.",
        blocking_reasons=["Insufficient scope detail."],
        created_at=_NOW,
    )
    plan = build_intake_plan(recommendation)
    manifest = build_intake_manifest(_session(), recommendation, plan, [])
    assert manifest.status == IntakeManifestStatus.BLOCKED
    assert manifest.blocking_reasons
