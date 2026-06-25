"""Tests for P7 demo fixture builders."""

from app.demo_fixtures import (
    ADVISORY_SAMPLE_DTC_SKINCARE,
    ADVISORY_SAMPLE_LOCAL_FITNESS,
    ADVISORY_SAMPLE_TRAFFIC_INFORMED,
    CALIBRATION_SAMPLE_MISSING_UNCERTAINTY,
    CALIBRATION_SAMPLE_VALID,
    build_advisory_plan,
    build_calibration_fixture,
    build_demo_profiling_fixture,
    build_dtc_skincare_advisory_plan,
    build_local_fitness_advisory_plan,
    build_national_blocked_readiness_reports,
    build_traffic_informed_advisory_plan,
    calibration_maps_signal,
    demo_profiling_fixture_labels,
    demo_profiling_links_advisory,
    expected_advisory_claim_type,
    expected_advisory_evidence_mode,
    readiness_has_ready_report,
)
from mip.contracts.advisory import AdvisoryClaimType, AdvisoryEvidenceMode, ChannelCandidateName
from mip.contracts.calibration_intake import (
    CalibrationIntakeBlockingReason,
    CalibrationIntakeStatus,
)
from mip.contracts.workflow_readiness import (
    WorkflowReadinessReportType,
    WorkflowReadinessStatus,
)
from mip.workflows.intake.demo_profiling import DEMO_DATASET_WEBSITE_TRAFFIC


def test_demo_fixtures_build_cold_start_ecommerce_advisory_plan() -> None:
    plan = build_dtc_skincare_advisory_plan()
    assert plan.evidence_mode == AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY
    assert AdvisoryClaimType.HYPOTHESIS_TO_TEST in plan.claim_types
    assert str(plan.status) in {"needs_tracking_setup", "advisory_plan_ready"}
    channel_names = {hypothesis.channel_candidate for hypothesis in plan.channel_hypotheses}
    assert ChannelCandidateName.META_INSTAGRAM in channel_names
    assert ChannelCandidateName.TIKTOK in channel_names
    assert ChannelCandidateName.GOOGLE_SEARCH in channel_names


def test_demo_fixtures_build_local_service_advisory_plan() -> None:
    plan = build_local_fitness_advisory_plan()
    channel_names = {hypothesis.channel_candidate for hypothesis in plan.channel_hypotheses}
    assert ChannelCandidateName.GOOGLE_SEARCH in channel_names
    assert ChannelCandidateName.LOCAL_LISTINGS_MAPS in channel_names


def test_traffic_informed_fixture_produces_data_informed_advisory_mode() -> None:
    plan = build_traffic_informed_advisory_plan()
    assert plan.evidence_mode == AdvisoryEvidenceMode.DATA_INFORMED_ADVISORY
    assert AdvisoryClaimType.DATA_INFORMED_HYPOTHESIS in plan.claim_types
    assert expected_advisory_evidence_mode(ADVISORY_SAMPLE_TRAFFIC_INFORMED) == (
        AdvisoryEvidenceMode.DATA_INFORMED_ADVISORY
    )
    assert expected_advisory_claim_type(ADVISORY_SAMPLE_TRAFFIC_INFORMED) == (
        AdvisoryClaimType.DATA_INFORMED_HYPOTHESIS
    )


def test_advisory_fixture_keys_resolve() -> None:
    dtc = build_advisory_plan(ADVISORY_SAMPLE_DTC_SKINCARE)
    local = build_advisory_plan(ADVISORY_SAMPLE_LOCAL_FITNESS)
    traffic = build_advisory_plan(ADVISORY_SAMPLE_TRAFFIC_INFORMED)
    assert dtc.plan_id
    assert local.plan_id
    assert traffic.plan_id


def test_readiness_fixture_produces_at_least_one_readiness_report() -> None:
    reports = build_national_blocked_readiness_reports()
    assert reports
    assert readiness_has_ready_report(reports)
    mmm_reports = [
        report
        for report in reports
        if report.report_type == WorkflowReadinessReportType.MMM_DATA_READINESS
    ]
    assert mmm_reports
    assert mmm_reports[0].status == WorkflowReadinessStatus.READY
    geox_reports = [
        report
        for report in reports
        if report.report_type == WorkflowReadinessReportType.GEOX_DESIGN_READINESS
    ]
    if geox_reports:
        assert geox_reports[0].status == WorkflowReadinessStatus.NEEDS_MORE_DATA


def test_calibration_valid_fixture_maps_to_calibration_signal() -> None:
    result = build_calibration_fixture(CALIBRATION_SAMPLE_VALID)
    assert calibration_maps_signal(result)
    assert result.signal is not None
    assert result.report.status == CalibrationIntakeStatus.MAPPED


def test_calibration_missing_uncertainty_fixture_does_not_map() -> None:
    result = build_calibration_fixture(CALIBRATION_SAMPLE_MISSING_UNCERTAINTY)
    assert result.signal is None
    assert not calibration_maps_signal(result)
    assert result.report.status == CalibrationIntakeStatus.NEEDS_MORE_DATA
    blocking = result.report.blocking_reasons
    assert CalibrationIntakeBlockingReason.MISSING_UNCERTAINTY.value in blocking


def test_demo_profiling_fixture_labels_cover_builtin_datasets() -> None:
    labels = demo_profiling_fixture_labels()
    assert DEMO_DATASET_WEBSITE_TRAFFIC in labels
    assert len(labels) == 5


def test_website_traffic_demo_profiling_links_advisory() -> None:
    fixture = build_demo_profiling_fixture(DEMO_DATASET_WEBSITE_TRAFFIC)
    assert demo_profiling_links_advisory(DEMO_DATASET_WEBSITE_TRAFFIC)
    assert fixture.advisory_plan is not None
    assert fixture.traffic_profile is not None
    assert fixture.profile.row_count > 0
