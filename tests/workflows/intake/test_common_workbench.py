"""Tests for common intake workbench helpers."""

from datetime import UTC, datetime
from typing import Any

from mip.contracts.common_intake import (
    CommonDataProfileSummary,
    CommonIntakeStatus,
    CommonIntakeWorkbench,
    DataSnapshot,
    GeoCoverageSummary,
    IngestionMode,
    MediaCoverageSummary,
    MetricAvailabilitySummary,
    SourceIngestionRecord,
    WorkflowSupportRoute,
    WorkflowSupportStatus,
)
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
from mip.contracts.intake_assets import DataAssetType, IntakePlan
from mip.contracts.intake_sources import (
    DataSourceMode,
    GeoXIntakeManifest,
    IntakeManifestStatus,
    MMMIntakeManifest,
)
from mip.workflows.intake.common_workbench import (
    build_common_intake_workbench,
    build_llm_answer_grounding_context,
    build_workflow_support_assessment,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

_FORBIDDEN_FRAGMENTS = (
    "lift estimate",
    "roi is",
    "budget allocation",
    "mde result",
    "power result",
    "matched markets",
    "treatment assignment",
    "control assignment",
    "causal effect",
)


def _session(**overrides: Any) -> MeasurementIntakeSession:
    base: dict[str, Any] = {
        "session_id": "sess-wb-001",
        "business_question": "How should we measure channel impact?",
        "intended_use": IntakeIntendedUse.DIAGNOSTIC_ONLY,
        "workflow_kind": MeasurementWorkflowKind.MMM,
        "time_grain": DataGrain.WEEKLY,
        "geo_grain": GeoGrain.NATIONAL,
        "created_at": _NOW,
    }
    base.update(overrides)
    return MeasurementIntakeSession(**base)


def _recommendation(
    session: MeasurementIntakeSession,
    path: IntakeCandidatePath,
) -> IntakePathRecommendation:
    return IntakePathRecommendation(
        recommendation_id="rec-wb-001",
        session_id=session.session_id,
        status=IntakeRecommendationStatus.RECOMMENDED,
        recommended_path=path,
        workflow_kind=session.workflow_kind,
        why_this_path=f"Recommended path {path.value}.",
        created_at=_NOW,
    )


def _plan(
    session: MeasurementIntakeSession,
    recommendation: IntakePathRecommendation,
) -> IntakePlan:
    return IntakePlan(
        plan_id="plan-wb-001",
        session_id=session.session_id,
        recommendation_id=recommendation.recommendation_id,
        recommended_path=recommendation.recommended_path,
        required_assets=[],
        blocking_reasons=["placeholder_for_blocked_path_only"],
    )


def _mmm_manifest(
    session: MeasurementIntakeSession,
    recommendation: IntakePathRecommendation,
    plan: IntakePlan,
) -> MMMIntakeManifest:
    return MMMIntakeManifest(
        manifest_id="man-wb-001",
        session_id=session.session_id,
        recommendation_id=recommendation.recommendation_id,
        plan_id=plan.plan_id,
        business_question=session.business_question,
        intended_use=session.intended_use,
        recommended_path=recommendation.recommended_path,
        created_at=_NOW,
    )


def _geox_manifest(
    session: MeasurementIntakeSession,
    recommendation: IntakePathRecommendation,
    plan: IntakePlan,
) -> GeoXIntakeManifest:
    return GeoXIntakeManifest(
        manifest_id="man-geox-001",
        session_id=session.session_id,
        recommendation_id=recommendation.recommendation_id,
        plan_id=plan.plan_id,
        business_question=session.business_question,
        intended_use=session.intended_use,
        recommended_path=recommendation.recommended_path,
        created_at=_NOW,
    )


def _profile(
    *,
    profile_id: str,
    asset_type: DataAssetType,
    geo_grain: GeoGrain,
    source_id: str | None = None,
    spend_present: bool = False,
    impressions_present: bool = False,
    calibration_metrics: list[str] | None = None,
) -> CommonDataProfileSummary:
    geo = GeoCoverageSummary(
        summary_id=f"{profile_id}-geo",
        source_id=source_id or profile_id,
        geo_grain=geo_grain,
        geo_count=210 if geo_grain == GeoGrain.DMA else 1,
        geo_values_sample=["US-501"] if geo_grain == GeoGrain.DMA else ["US"],
    )
    media = None
    if asset_type in {DataAssetType.MEDIA_SPEND_DATA, DataAssetType.MEDIA_EXPOSURE_DATA}:
        media = MediaCoverageSummary(
            summary_id=f"{profile_id}-media",
            source_id=source_id or profile_id,
            spend_present=spend_present,
            impressions_present=impressions_present,
            platforms=["Meta"],
        )
    metrics = None
    if calibration_metrics is not None:
        metrics = MetricAvailabilitySummary(
            summary_id=f"{profile_id}-met",
            source_id=source_id or profile_id,
            metric_ids=calibration_metrics,
        )
    return CommonDataProfileSummary(
        profile_id=profile_id,
        snapshot_id=f"snap-{profile_id}",
        source_id=source_id or profile_id,
        asset_type=asset_type,
        geo_coverage=geo,
        media_coverage=media,
        metric_availability=metrics,
        created_at=_NOW,
    )


def _national_weekly_profiles() -> list[CommonDataProfileSummary]:
    return [
        _profile(
            profile_id="prof-outcome-national",
            asset_type=DataAssetType.OUTCOME_KPI_DATA,
            geo_grain=GeoGrain.NATIONAL,
        ),
        _profile(
            profile_id="prof-media-national",
            asset_type=DataAssetType.MEDIA_SPEND_DATA,
            geo_grain=GeoGrain.NATIONAL,
            spend_present=True,
        ),
        _profile(
            profile_id="prof-channel-map",
            asset_type=DataAssetType.CHANNEL_MAPPING,
            geo_grain=GeoGrain.NATIONAL,
        ),
    ]


def _dma_week_profiles() -> list[CommonDataProfileSummary]:
    return [
        _profile(
            profile_id="prof-outcome-dma",
            asset_type=DataAssetType.OUTCOME_KPI_DATA,
            geo_grain=GeoGrain.DMA,
        ),
        _profile(
            profile_id="prof-media-dma",
            asset_type=DataAssetType.MEDIA_EXPOSURE_DATA,
            geo_grain=GeoGrain.DMA,
            spend_present=True,
            impressions_present=True,
        ),
        _profile(
            profile_id="prof-geo-map",
            asset_type=DataAssetType.GEO_MAPPING,
            geo_grain=GeoGrain.DMA,
        ),
        _profile(
            profile_id="prof-channel-map-dma",
            asset_type=DataAssetType.CHANNEL_MAPPING,
            geo_grain=GeoGrain.DMA,
        ),
    ]


def _assert_no_forbidden_claims(*objects: Any) -> None:
    combined = " ".join(str(obj.model_dump()) for obj in objects).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in combined


def test_national_weekly_supports_national_mmm_blocks_geox() -> None:
    session = _session()
    rec = _recommendation(session, IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM)
    plan = _plan(session, rec)
    manifest = _mmm_manifest(session, rec, plan)
    profiles = _national_weekly_profiles()

    assessment = build_workflow_support_assessment(session, rec, plan, manifest, profiles)
    assert WorkflowSupportRoute.NATIONAL_MMM in assessment.supported_routes
    assert "supports_national_mmm" in assessment.route_reasons
    assert WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS in assessment.blocked_routes
    assert "blocked_needs_geo_level_outcome" in assessment.route_reasons
    _assert_no_forbidden_claims(assessment)


def test_dma_week_supports_geox_design_and_geo_level_mmm() -> None:
    session = _session(geo_grain=GeoGrain.DMA)
    rec_mmm = _recommendation(session, IntakeCandidatePath.GEO_LEVEL_MMM)
    plan = _plan(session, rec_mmm)
    manifest = _mmm_manifest(session, rec_mmm, plan)
    profiles = _dma_week_profiles()

    assessment_mmm = build_workflow_support_assessment(session, rec_mmm, plan, manifest, profiles)
    assert WorkflowSupportRoute.GEO_LEVEL_MMM in assessment_mmm.supported_routes
    assert "supports_geo_level_mmm" in assessment_mmm.route_reasons

    rec_geox = _recommendation(
        _session(workflow_kind=MeasurementWorkflowKind.GEOX),
        IntakeCandidatePath.GEO_EXPERIMENT_DESIGN,
    )
    manifest_geox = _geox_manifest(session, rec_geox, plan)
    assessment_geox = build_workflow_support_assessment(
        session, rec_geox, plan, manifest_geox, profiles
    )
    assert WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS in assessment_geox.supported_routes
    assert "supports_geox_design_diagnostics" in assessment_geox.route_reasons


def test_geox_design_blocks_missing_geo_level_outcome() -> None:
    session = _session(workflow_kind=MeasurementWorkflowKind.GEOX)
    rec = _recommendation(session, IntakeCandidatePath.GEO_EXPERIMENT_DESIGN)
    plan = _plan(session, rec)
    manifest = _geox_manifest(session, rec, plan)
    profiles = [
        _profile(
            profile_id="prof-media-only",
            asset_type=DataAssetType.MEDIA_SPEND_DATA,
            geo_grain=GeoGrain.DMA,
            spend_present=True,
        ),
        _profile(
            profile_id="prof-geo-map-only",
            asset_type=DataAssetType.GEO_MAPPING,
            geo_grain=GeoGrain.DMA,
        ),
    ]
    assessment = build_workflow_support_assessment(session, rec, plan, manifest, profiles)
    assert WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS in assessment.blocked_routes
    assert "blocked_needs_geo_level_outcome" in assessment.route_reasons


def test_geox_design_blocks_missing_geo_level_media() -> None:
    session = _session(workflow_kind=MeasurementWorkflowKind.GEOX)
    rec = _recommendation(session, IntakeCandidatePath.GEO_EXPERIMENT_DESIGN)
    plan = _plan(session, rec)
    manifest = _geox_manifest(session, rec, plan)
    profiles = [
        _profile(
            profile_id="prof-outcome-dma-only",
            asset_type=DataAssetType.OUTCOME_KPI_DATA,
            geo_grain=GeoGrain.DMA,
        ),
        _profile(
            profile_id="prof-geo-map-2",
            asset_type=DataAssetType.GEO_MAPPING,
            geo_grain=GeoGrain.DMA,
        ),
    ]
    assessment = build_workflow_support_assessment(session, rec, plan, manifest, profiles)
    assert WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS in assessment.blocked_routes
    assert "blocked_needs_geo_level_media" in assessment.route_reasons


def test_calibrated_mmm_needs_calibration_uncertainty() -> None:
    session = _session()
    rec = _recommendation(session, IntakeCandidatePath.CALIBRATED_MMM)
    plan = _plan(session, rec)
    manifest = _mmm_manifest(session, rec, plan)
    profiles = _national_weekly_profiles()

    assessment = build_workflow_support_assessment(session, rec, plan, manifest, profiles)
    assert "blocked_needs_calibration_uncertainty" in assessment.route_reasons
    assert WorkflowSupportStatus.NEEDS_MORE_DATA in {
        assessment.support_status,
        WorkflowSupportStatus.SUPPORTED_WITH_WARNINGS,
    }

    profiles_with_cal = profiles + [
        _profile(
            profile_id="prof-calibration",
            asset_type=DataAssetType.CALIBRATION_SIGNAL_DATA,
            geo_grain=GeoGrain.NATIONAL,
            calibration_metrics=["effect_estimate", "standard_error"],
        ),
    ]
    assessment_ok = build_workflow_support_assessment(
        session, rec, plan, manifest, profiles_with_cal
    )
    assert "supports_calibration_signal_intake" in assessment_ok.route_reasons


def test_llm_grounding_allows_coverage_blocks_lift_roi_budget() -> None:
    session = _session()
    rec = _recommendation(session, IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM)
    plan = _plan(session, rec)
    manifest = _mmm_manifest(session, rec, plan)
    profiles = _national_weekly_profiles()
    assessment = build_workflow_support_assessment(session, rec, plan, manifest, profiles)
    context = build_llm_answer_grounding_context(session, profiles, assessment)

    assert "data_coverage" in context.allowed_answer_topics
    assert "missing_data" in context.allowed_answer_topics
    blocked = set(context.blocked_answer_topics)
    assert "causal_lift" in blocked
    assert "roi" in blocked
    assert "budget_recommendation" in blocked
    assert "mde_power_result" in blocked
    assert "matched_markets" in blocked
    assert "treatment_control_assignment" in blocked


def test_common_intake_workbench_shared_not_split_mmm_geox() -> None:
    session = _session()
    rec = _recommendation(session, IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM)
    plan = _plan(session, rec)
    manifest = _mmm_manifest(session, rec, plan)
    profiles = _national_weekly_profiles()
    ingestion = [
        SourceIngestionRecord(
            ingestion_id="ing-001",
            source_id="src-outcome",
            asset_type=DataAssetType.OUTCOME_KPI_DATA,
            source_mode=DataSourceMode.SAMPLE_DEMO_DATA,
            ingestion_mode=IngestionMode.SAMPLE_DEMO_DATA,
            declared_uri_or_ref="demo://outcome",
            ingested_at=_NOW,
        ),
    ]
    snapshots = [
        DataSnapshot(
            snapshot_id="snap-001",
            source_id="src-outcome",
            asset_type=DataAssetType.OUTCOME_KPI_DATA,
            geo_grain=GeoGrain.NATIONAL,
            time_grain=DataGrain.WEEKLY,
            created_at=_NOW,
        ),
    ]

    workbench = build_common_intake_workbench(
        session,
        rec,
        plan,
        manifest,
        ingestion,
        snapshots,
        profiles,
    )
    assert isinstance(workbench, CommonIntakeWorkbench)
    assert workbench.workbench_id.endswith("-workbench")
    assert workbench.workflow_support_assessment is not None
    assert workbench.llm_grounding_context is not None
    assert workbench.status == CommonIntakeStatus.SUPPORT_ASSESSED
    dumped = workbench.model_dump()
    assert "mmm_upload_workbench" not in str(dumped).lower()
    assert "geox_upload_workbench" not in str(dumped).lower()
    _assert_no_forbidden_claims(workbench, workbench.workflow_support_assessment)


def test_workbench_collecting_sources_without_ingestion() -> None:
    session = _session()
    rec = _recommendation(session, IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM)
    plan = _plan(session, rec)
    manifest = _mmm_manifest(session, rec, plan)

    workbench = build_common_intake_workbench(session, rec, plan, manifest, [], [], [])
    assert workbench.status == CommonIntakeStatus.COLLECTING_SOURCES


def test_workbench_blocked_when_manifest_blocked() -> None:
    session = _session()
    rec = _recommendation(session, IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM)
    plan = _plan(session, rec)
    manifest = _mmm_manifest(session, rec, plan).model_copy(
        update={
            "status": IntakeManifestStatus.BLOCKED,
            "blocking_reasons": ["manifest blocked for test"],
        }
    )
    workbench = build_common_intake_workbench(
        session,
        rec,
        plan,
        manifest,
        [],
        [],
        _national_weekly_profiles(),
    )
    assert workbench.status == CommonIntakeStatus.BLOCKED
    assert workbench.blocking_reasons
