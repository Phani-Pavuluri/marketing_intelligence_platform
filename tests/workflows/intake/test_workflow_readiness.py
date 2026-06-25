"""Tests for workflow-specific readiness report helpers."""

from datetime import UTC, datetime
from typing import Any

from mip.contracts.common_intake import (
    CommonDataProfileSummary,
    GeoCoverageSummary,
    LLMAnswerGroundingContext,
    MediaCoverageSummary,
    MetricAvailabilitySummary,
    TimeCoverageSummary,
    WorkflowSupportRoute,
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
    MMMIntakeManifest,
)
from mip.contracts.workflow_readiness import (
    CalibrationSignalReadinessReport,
    DecisionReviewReadinessReport,
    MMMDataReadinessReport,
    WorkflowReadinessReportType,
    WorkflowReadinessStatus,
)
from mip.workflows.intake.common_workbench import build_common_intake_workbench
from mip.workflows.intake.readiness import (
    build_calibration_signal_readiness_report,
    build_decision_review_readiness_report,
    build_geox_design_readiness_report,
    build_mmm_data_readiness_report,
    build_workflow_readiness_reports,
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
        "session_id": "sess-rdy-001",
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
        recommendation_id="rec-rdy-001",
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
        plan_id="plan-rdy-001",
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
        manifest_id="man-rdy-001",
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
        manifest_id="man-geox-rdy-001",
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
    spend_present: bool = False,
    impressions_present: bool = False,
    calibration_metrics: list[str] | None = None,
    with_time: bool = False,
) -> CommonDataProfileSummary:
    geo = GeoCoverageSummary(
        summary_id=f"{profile_id}-geo",
        source_id=profile_id,
        geo_grain=geo_grain,
        geo_count=210 if geo_grain == GeoGrain.DMA else 1,
    )
    media = None
    if asset_type in {DataAssetType.MEDIA_SPEND_DATA, DataAssetType.MEDIA_EXPOSURE_DATA}:
        media = MediaCoverageSummary(
            summary_id=f"{profile_id}-media",
            source_id=profile_id,
            spend_present=spend_present,
            impressions_present=impressions_present,
        )
    metrics = None
    if calibration_metrics is not None:
        metrics = MetricAvailabilitySummary(
            summary_id=f"{profile_id}-met",
            source_id=profile_id,
            metric_ids=calibration_metrics,
        )
    time_cov = None
    if with_time:
        time_cov = TimeCoverageSummary(
            summary_id=f"{profile_id}-time",
            source_id=profile_id,
            time_grain=DataGrain.WEEKLY,
            period_count=52,
        )
    return CommonDataProfileSummary(
        profile_id=profile_id,
        snapshot_id=f"snap-{profile_id}",
        source_id=profile_id,
        asset_type=asset_type,
        geo_coverage=geo,
        media_coverage=media,
        metric_availability=metrics,
        time_coverage=time_cov,
        created_at=_NOW,
    )


def _national_profiles() -> list[CommonDataProfileSummary]:
    return [
        _profile(
            profile_id="out-nat",
            asset_type=DataAssetType.OUTCOME_KPI_DATA,
            geo_grain=GeoGrain.NATIONAL,
            with_time=True,
        ),
        _profile(
            profile_id="media-nat",
            asset_type=DataAssetType.MEDIA_SPEND_DATA,
            geo_grain=GeoGrain.NATIONAL,
            spend_present=True,
        ),
        _profile(
            profile_id="map-nat",
            asset_type=DataAssetType.CHANNEL_MAPPING,
            geo_grain=GeoGrain.NATIONAL,
        ),
    ]


def _dma_profiles() -> list[CommonDataProfileSummary]:
    return [
        _profile(
            profile_id="out-dma",
            asset_type=DataAssetType.OUTCOME_KPI_DATA,
            geo_grain=GeoGrain.DMA,
            with_time=True,
        ),
        _profile(
            profile_id="media-dma",
            asset_type=DataAssetType.MEDIA_EXPOSURE_DATA,
            geo_grain=GeoGrain.DMA,
            spend_present=True,
            impressions_present=True,
        ),
        _profile(
            profile_id="geo-map",
            asset_type=DataAssetType.GEO_MAPPING,
            geo_grain=GeoGrain.DMA,
        ),
        _profile(
            profile_id="chan-map",
            asset_type=DataAssetType.CHANNEL_MAPPING,
            geo_grain=GeoGrain.DMA,
        ),
    ]


def _workbench(
    path: IntakeCandidatePath,
    profiles: list[CommonDataProfileSummary],
    *,
    workflow_kind: MeasurementWorkflowKind = MeasurementWorkflowKind.MMM,
) -> Any:
    session = _session(workflow_kind=workflow_kind)
    rec = _recommendation(session, path)
    plan = _plan(session, rec)
    if workflow_kind == MeasurementWorkflowKind.GEOX:
        manifest: GeoXIntakeManifest | MMMIntakeManifest = _geox_manifest(session, rec, plan)
    else:
        manifest = _mmm_manifest(session, rec, plan)
    return build_common_intake_workbench(session, rec, plan, manifest, [], [], profiles)


def _assert_no_forbidden_claims(*objects: Any) -> None:
    combined = " ".join(str(obj.model_dump()) for obj in objects).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in combined


def test_mmm_national_readiness_ready_when_national_mmm_supported() -> None:
    workbench = _workbench(IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM, _national_profiles())
    report = build_mmm_data_readiness_report(workbench)
    assert isinstance(report, MMMDataReadinessReport)
    assert report.status == WorkflowReadinessStatus.READY
    assert report.mmm_route == WorkflowSupportRoute.NATIONAL_MMM
    assert report.has_outcome_data is True
    assert report.has_media_data is True
    _assert_no_forbidden_claims(report)


def test_mmm_geo_readiness_needs_data_when_geo_level_blocked() -> None:
    workbench = _workbench(IntakeCandidatePath.GEO_LEVEL_MMM, _national_profiles())
    report = build_mmm_data_readiness_report(workbench)
    assert report.status == WorkflowReadinessStatus.NEEDS_MORE_DATA
    assert report.mmm_route == WorkflowSupportRoute.GEO_LEVEL_MMM


def test_calibrated_mmm_needs_data_without_calibration_uncertainty() -> None:
    workbench = _workbench(IntakeCandidatePath.CALIBRATED_MMM, _national_profiles())
    report = build_mmm_data_readiness_report(workbench)
    assert report.calibration_required is True
    assert report.status == WorkflowReadinessStatus.NEEDS_MORE_DATA
    assert "missing_calibration_uncertainty" in report.blocking_reasons


def test_geox_design_ready_when_route_supported() -> None:
    workbench = _workbench(
        IntakeCandidatePath.GEO_EXPERIMENT_DESIGN,
        _dma_profiles(),
        workflow_kind=MeasurementWorkflowKind.GEOX,
    )
    report = build_geox_design_readiness_report(workbench)
    assert report.status in {
        WorkflowReadinessStatus.READY,
        WorkflowReadinessStatus.READY_WITH_WARNINGS,
    }
    assert report.requires_panel_exp_diagnostics is True
    assert report.requires_power_diagnostic is True
    _assert_no_forbidden_claims(report)


def test_geox_design_needs_data_when_geo_outcome_missing() -> None:
    profiles = [
        _profile(
            profile_id="media-only",
            asset_type=DataAssetType.MEDIA_SPEND_DATA,
            geo_grain=GeoGrain.DMA,
            spend_present=True,
        ),
        _profile(
            profile_id="geo-map-only",
            asset_type=DataAssetType.GEO_MAPPING,
            geo_grain=GeoGrain.DMA,
        ),
    ]
    workbench = _workbench(
        IntakeCandidatePath.GEO_EXPERIMENT_DESIGN,
        profiles,
        workflow_kind=MeasurementWorkflowKind.GEOX,
    )
    report = build_geox_design_readiness_report(workbench)
    assert report.status == WorkflowReadinessStatus.NEEDS_MORE_DATA
    assert report.has_geo_level_outcome is False


def test_geox_design_needs_data_when_geo_media_missing() -> None:
    profiles = [
        _profile(
            profile_id="out-only",
            asset_type=DataAssetType.OUTCOME_KPI_DATA,
            geo_grain=GeoGrain.DMA,
        ),
        _profile(
            profile_id="geo-map-2",
            asset_type=DataAssetType.GEO_MAPPING,
            geo_grain=GeoGrain.DMA,
        ),
    ]
    workbench = _workbench(
        IntakeCandidatePath.GEO_EXPERIMENT_DESIGN,
        profiles,
        workflow_kind=MeasurementWorkflowKind.GEOX,
    )
    report = build_geox_design_readiness_report(workbench)
    assert report.status == WorkflowReadinessStatus.NEEDS_MORE_DATA
    assert report.has_geo_level_media is False


def test_calibration_signal_readiness_structural_fields() -> None:
    profiles = _national_profiles() + [
        _profile(
            profile_id="cal-signal",
            asset_type=DataAssetType.CALIBRATION_SIGNAL_DATA,
            geo_grain=GeoGrain.NATIONAL,
            calibration_metrics=["effect_estimate", "standard_error"],
        ),
        _profile(
            profile_id="metric-map",
            asset_type=DataAssetType.METRIC_MAPPING,
            geo_grain=GeoGrain.NATIONAL,
        ),
    ]
    workbench = _workbench(IntakeCandidatePath.EXPERIMENT_CALIBRATION_INTAKE, profiles)
    report = build_calibration_signal_readiness_report(workbench)
    assert isinstance(report, CalibrationSignalReadinessReport)
    assert report.has_effect_estimate is True
    assert report.has_uncertainty is True
    assert report.has_metric_mapping is True
    _assert_no_forbidden_claims(report)


def test_decision_review_needs_trust_report() -> None:
    workbench = _workbench(IntakeCandidatePath.DECISION_REVIEW_PACKET, _national_profiles())
    report = build_decision_review_readiness_report(workbench)
    assert isinstance(report, DecisionReviewReadinessReport)
    assert report.requires_human_approval is True
    assert report.has_trust_report is False
    assert report.status == WorkflowReadinessStatus.NEEDS_MORE_DATA
    assert "missing_trust_report" in report.blocking_reasons


def test_decision_review_structural_with_trust_report() -> None:
    workbench = _workbench(IntakeCandidatePath.DECISION_REVIEW_PACKET, _national_profiles())
    grounding = LLMAnswerGroundingContext(
        context_id="ctx-trust",
        session_id=workbench.session_id,
        trust_report_ids=["trust-001"],
        created_at=_NOW,
    )
    workbench = workbench.model_copy(
        update={
            "llm_grounding_context": grounding,
            "ingestion_records": workbench.ingestion_records,
        }
    )
    from mip.contracts.common_intake import IngestionMode, SourceIngestionRecord

    workbench = workbench.model_copy(
        update={
            "ingestion_records": [
                SourceIngestionRecord(
                    ingestion_id="ing-001",
                    source_id="src-001",
                    asset_type=DataAssetType.OUTCOME_KPI_DATA,
                    source_mode=DataSourceMode.SAMPLE_DEMO_DATA,
                    ingestion_mode=IngestionMode.SAMPLE_DEMO_DATA,
                    declared_uri_or_ref="demo://outcome",
                    ingested_at=_NOW,
                ),
            ],
            "profile_summaries": _national_profiles()
            + [
                _profile(
                    profile_id="metric-map",
                    asset_type=DataAssetType.METRIC_MAPPING,
                    geo_grain=GeoGrain.NATIONAL,
                ),
            ],
        }
    )
    report = build_decision_review_readiness_report(workbench)
    assert report.has_trust_report is True
    assert report.has_supported_artifacts is True


def test_build_workflow_readiness_reports_from_national_assessment() -> None:
    workbench = _workbench(IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM, _national_profiles())
    reports = build_workflow_readiness_reports(workbench)
    types = {report.report_type for report in reports}
    assert WorkflowReadinessReportType.MMM_DATA_READINESS in types
    mmm_report = next(
        report
        for report in reports
        if report.report_type == WorkflowReadinessReportType.MMM_DATA_READINESS
    )
    assert mmm_report.status == WorkflowReadinessStatus.READY
    geox_reports = [
        report
        for report in reports
        if report.report_type == WorkflowReadinessReportType.GEOX_DESIGN_READINESS
    ]
    if geox_reports:
        assert geox_reports[0].status == WorkflowReadinessStatus.NEEDS_MORE_DATA


def test_build_workflow_readiness_reports_includes_geox_and_mmm_for_dma() -> None:
    session = _session(geo_grain=GeoGrain.DMA)
    rec = _recommendation(session, IntakeCandidatePath.GEO_LEVEL_MMM)
    plan = _plan(session, rec)
    manifest = _mmm_manifest(session, rec, plan)
    profiles = _dma_profiles()
    workbench_mmm = build_common_intake_workbench(session, rec, plan, manifest, [], [], profiles)
    reports_mmm = build_workflow_readiness_reports(workbench_mmm)
    assert any(
        report.report_type == WorkflowReadinessReportType.MMM_DATA_READINESS
        for report in reports_mmm
    )

    rec_geox = _recommendation(
        _session(workflow_kind=MeasurementWorkflowKind.GEOX),
        IntakeCandidatePath.GEO_EXPERIMENT_DESIGN,
    )
    manifest_geox = _geox_manifest(session, rec_geox, plan)
    workbench_geox = build_common_intake_workbench(
        session, rec_geox, plan, manifest_geox, [], [], profiles
    )
    reports_geox = build_workflow_readiness_reports(workbench_geox)
    assert any(
        report.report_type == WorkflowReadinessReportType.GEOX_DESIGN_READINESS
        for report in reports_geox
    )
