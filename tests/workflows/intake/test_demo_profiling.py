"""Tests for P8 local/demo profiling helpers."""

from datetime import UTC, datetime

from mip.contracts.calibration_intake import CalibrationEvidenceInput
from mip.contracts.common_intake import WorkflowSupportRoute
from mip.contracts.demo_profile import (
    MAX_DEMO_COLUMN_SAMPLE_VALUES,
    MAX_DEMO_PROFILE_ROWS,
    DemoColumnSemanticRole,
    DemoDatasetKind,
    DemoProfileStatus,
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
from mip.contracts.intake_sources import MMMIntakeManifest
from mip.workflows.intake.common_workbench import build_workflow_support_assessment
from mip.workflows.intake.demo_profiling import (
    DEMO_DATASET_DMA_WEEK,
    DEMO_DATASET_EXPERIMENT_READOUT,
    DEMO_DATASET_NATIONAL_MEDIA_OUTCOME,
    DEMO_DATASET_READOUT_MISSING_UNCERTAINTY,
    DEMO_DATASET_WEBSITE_TRAFFIC,
    build_calibration_evidence_input_from_demo_profile,
    build_common_profile_summary_from_demo_profile,
    build_demo_dataset_profile,
    build_demo_dataset_profile_for_key,
    build_demo_profile_to_workflow_summary,
    build_website_traffic_profile_from_demo_profile,
    demo_rows_for_key,
    infer_demo_column_role,
    national_media_outcome_demo_rows,
    website_traffic_demo_rows,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def test_infer_demo_column_role_maps_common_names() -> None:
    assert infer_demo_column_role("event_date") == DemoColumnSemanticRole.DATE
    assert infer_demo_column_role("dma_code") == DemoColumnSemanticRole.GEO
    assert infer_demo_column_role("utm_source") == DemoColumnSemanticRole.SOURCE
    assert infer_demo_column_role("utm_medium") == DemoColumnSemanticRole.MEDIUM
    assert infer_demo_column_role("paid_channel") == DemoColumnSemanticRole.CHANNEL
    assert infer_demo_column_role("total_sessions") == DemoColumnSemanticRole.SESSIONS
    assert infer_demo_column_role("orders") == DemoColumnSemanticRole.CONVERSIONS
    assert infer_demo_column_role("net_revenue") == DemoColumnSemanticRole.REVENUE
    assert infer_demo_column_role("media_spend") == DemoColumnSemanticRole.SPEND
    assert infer_demo_column_role("impressions") == DemoColumnSemanticRole.IMPRESSIONS
    assert infer_demo_column_role("clicks") == DemoColumnSemanticRole.CLICKS
    assert infer_demo_column_role("effect_estimate") == DemoColumnSemanticRole.EFFECT_ESTIMATE
    assert infer_demo_column_role("std_error") == DemoColumnSemanticRole.STANDARD_ERROR
    assert infer_demo_column_role("ci_low") == DemoColumnSemanticRole.CONFIDENCE_INTERVAL_LOW
    assert infer_demo_column_role("ci_high") == DemoColumnSemanticRole.CONFIDENCE_INTERVAL_HIGH
    assert infer_demo_column_role("metric") == DemoColumnSemanticRole.METRIC
    assert infer_demo_column_role("estimand") == DemoColumnSemanticRole.ESTIMAND


def test_empty_rows_are_blocked() -> None:
    profile = build_demo_dataset_profile([], DemoDatasetKind.WEBSITE_TRAFFIC)
    assert profile.status == DemoProfileStatus.BLOCKED
    assert "demo_dataset_empty" in profile.blocking_reasons


def test_row_cap_blocks_oversized_demo_profile() -> None:
    rows = [{"value": index} for index in range(MAX_DEMO_PROFILE_ROWS + 1)]
    profile = build_demo_dataset_profile(rows, DemoDatasetKind.UNKNOWN)
    assert profile.status == DemoProfileStatus.BLOCKED
    assert any("demo_row_cap_exceeded" in reason for reason in profile.blocking_reasons)
    assert profile.row_count == 0


def test_website_traffic_demo_profile_detects_coverage() -> None:
    profile = build_demo_dataset_profile_for_key(DEMO_DATASET_WEBSITE_TRAFFIC)
    assert profile.dataset_kind == DemoDatasetKind.WEBSITE_TRAFFIC
    assert profile.has_time_data is True
    assert profile.has_outcome_data is True
    assert {"organic", "search", "social"}.issubset(set(profile.detected_sources))
    assert profile.detected_channels


def test_website_traffic_demo_profile_builds_traffic_summary() -> None:
    profile = build_demo_dataset_profile_for_key(DEMO_DATASET_WEBSITE_TRAFFIC)
    traffic = build_website_traffic_profile_from_demo_profile(profile)
    assert traffic.traffic_profile_id.startswith("traffic-")
    assert traffic.source_summary
    assert traffic.conversion_summary


def test_national_media_outcome_profile_flags() -> None:
    profile = build_demo_dataset_profile_for_key(DEMO_DATASET_NATIONAL_MEDIA_OUTCOME)
    assert profile.has_time_data is True
    assert profile.has_media_data is True
    assert profile.has_outcome_data is True
    assert profile.has_geo_data is False


def test_dma_week_profile_flags() -> None:
    profile = build_demo_dataset_profile_for_key(DEMO_DATASET_DMA_WEEK)
    assert profile.has_geo_data is True
    assert profile.has_time_data is True
    assert profile.has_media_data is True
    assert profile.has_outcome_data is True


def test_experiment_readout_profile_detects_effect_and_uncertainty() -> None:
    profile = build_demo_dataset_profile_for_key(DEMO_DATASET_EXPERIMENT_READOUT)
    assert profile.has_uncertainty_data is True
    assert profile.detected_metrics == ["weekly_orders"]
    roles = {column.semantic_role for column in profile.columns}
    assert DemoColumnSemanticRole.EFFECT_ESTIMATE in roles
    assert DemoColumnSemanticRole.STANDARD_ERROR in roles
    assert DemoColumnSemanticRole.METRIC in roles
    assert DemoColumnSemanticRole.ESTIMAND in roles


def test_valid_experiment_readout_builds_calibration_evidence_input() -> None:
    profile = build_demo_dataset_profile_for_key(DEMO_DATASET_EXPERIMENT_READOUT)
    evidence = build_calibration_evidence_input_from_demo_profile(profile)
    assert isinstance(evidence, CalibrationEvidenceInput)
    assert evidence.effect_estimate == 0.12
    assert evidence.standard_error == 0.03
    assert not evidence.blocking_reasons


def test_missing_uncertainty_readout_blocks_calibration_input() -> None:
    profile = build_demo_dataset_profile_for_key(DEMO_DATASET_READOUT_MISSING_UNCERTAINTY)
    evidence = build_calibration_evidence_input_from_demo_profile(profile)
    assert evidence is not None
    assert "missing_uncertainty" in evidence.blocking_reasons


def test_no_raw_rows_stored_in_demo_dataset_profile() -> None:
    profile = build_demo_dataset_profile_for_key(DEMO_DATASET_WEBSITE_TRAFFIC)
    dumped = profile.model_dump()
    assert "rows" not in dumped
    for column in profile.columns:
        assert len(column.sample_values) <= MAX_DEMO_COLUMN_SAMPLE_VALUES


def test_sample_values_capped_in_column_profiles() -> None:
    rows = [{"tag": f"value-{index}"} for index in range(20)]
    profile = build_demo_dataset_profile(rows, DemoDatasetKind.UNKNOWN)
    tag_column = next(column for column in profile.columns if column.column_name == "tag")
    assert len(tag_column.sample_values) <= MAX_DEMO_COLUMN_SAMPLE_VALUES


def test_national_workflow_summary_supports_national_mmm_route() -> None:
    profile = build_demo_dataset_profile_for_key(DEMO_DATASET_NATIONAL_MEDIA_OUTCOME)
    summary = build_demo_profile_to_workflow_summary(profile)
    assert WorkflowSupportRoute.NATIONAL_MMM in summary.supported_workflow_routes
    assert WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS in summary.blocked_workflow_routes


def test_dma_workflow_summary_supports_geo_routes() -> None:
    profile = build_demo_dataset_profile_for_key(DEMO_DATASET_DMA_WEEK)
    summary = build_demo_profile_to_workflow_summary(profile)
    assert WorkflowSupportRoute.GEO_LEVEL_MMM in summary.supported_workflow_routes
    assert WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS in summary.supported_workflow_routes
    assert WorkflowSupportRoute.NATIONAL_MMM in summary.blocked_workflow_routes


def test_common_profile_from_national_demo_through_readiness_helper() -> None:
    profile = build_demo_dataset_profile_for_key(DEMO_DATASET_NATIONAL_MEDIA_OUTCOME)
    common = build_common_profile_summary_from_demo_profile(profile)
    session = MeasurementIntakeSession(
        session_id="sess-demo-nat",
        business_question="How did media perform nationally?",
        intended_use=IntakeIntendedUse.DIAGNOSTIC_ONLY,
        workflow_kind=MeasurementWorkflowKind.MMM,
        time_grain=DataGrain.WEEKLY,
        geo_grain=GeoGrain.NATIONAL,
        created_at=_NOW,
    )
    recommendation = IntakePathRecommendation(
        recommendation_id="rec-nat",
        session_id=session.session_id,
        status=IntakeRecommendationStatus.RECOMMENDED,
        recommended_path=IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM,
        workflow_kind=session.workflow_kind,
        why_this_path="National diagnostic MMM path.",
        created_at=_NOW,
    )
    plan = IntakePlan(
        plan_id="plan-nat",
        session_id=session.session_id,
        recommendation_id=recommendation.recommendation_id,
        recommended_path=recommendation.recommended_path,
        required_assets=[],
        blocking_reasons=["demo_profile_readiness_probe"],
    )
    manifest = MMMIntakeManifest(
        manifest_id="man-nat",
        session_id=session.session_id,
        recommendation_id=recommendation.recommendation_id,
        plan_id=plan.plan_id,
        business_question=session.business_question,
        intended_use=session.intended_use,
        recommended_path=recommendation.recommended_path,
        created_at=_NOW,
    )
    assessment = build_workflow_support_assessment(
        session,
        recommendation,
        plan,
        manifest,
        [common],
    )
    assert WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS in assessment.blocked_routes
    assert common.asset_type == DataAssetType.OUTCOME_KPI_DATA


def test_demo_rows_for_key_returns_website_traffic_rows() -> None:
    rows = demo_rows_for_key(DEMO_DATASET_WEBSITE_TRAFFIC)
    assert rows == website_traffic_demo_rows()
    assert "source" in rows[0]
    assert "sessions" in rows[0]


def test_national_demo_rows_match_builder() -> None:
    profile = build_demo_dataset_profile(
        national_media_outcome_demo_rows(),
        DemoDatasetKind.MEDIA_SPEND,
    )
    assert profile.row_count == len(national_media_outcome_demo_rows())
