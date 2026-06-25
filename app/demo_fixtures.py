"""Deterministic sample fixtures for the P7 local workflow UI shell."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from mip.contracts.advisory import (
    AdvisoryClaimType,
    AdvisoryEvidenceMode,
    ColdStartAdvisoryPlan,
    ColdStartMediaObjective,
    WebsiteTrafficSourceProfile,
)
from mip.contracts.calibration import CalibrationSignal
from mip.contracts.calibration_intake import (
    CalibrationEvidenceInput,
    CalibrationIntakeStatus,
    CalibrationMappingReport,
    CalibrationMappingRequirement,
)
from mip.contracts.common_intake import (
    CommonDataProfileSummary,
    GeoCoverageSummary,
    MediaCoverageSummary,
    MetricAvailabilitySummary,
    TimeCoverageSummary,
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
from mip.contracts.intake_sources import GeoXIntakeManifest, MMMIntakeManifest
from mip.contracts.workflow_readiness import (
    BaseWorkflowReadinessReport,
    WorkflowReadinessStatus,
)
from mip.workflows.intake.advisory import (
    build_cold_start_advisory_plan,
    build_cold_start_business_profile,
)
from mip.workflows.intake.calibration_mapping import map_evidence_to_calibration_signal
from mip.workflows.intake.common_workbench import build_common_intake_workbench
from mip.workflows.intake.readiness import (
    build_geox_design_readiness_report,
    build_mmm_data_readiness_report,
    build_workflow_readiness_reports,
)
from mip.workflows.intake.recommendation import recommend_intake_path

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)
_WINDOW_START = datetime(2025, 1, 1, tzinfo=UTC)
_WINDOW_END = datetime(2025, 6, 1, tzinfo=UTC)

ADVISORY_SAMPLE_DTC_SKINCARE = "dtc_skincare_ecommerce"
ADVISORY_SAMPLE_LOCAL_FITNESS = "local_fitness_studio"
ADVISORY_SAMPLE_TRAFFIC_INFORMED = "traffic_informed_advisory"

READINESS_SAMPLE_NATIONAL_BLOCKED = "national_mmm_ready_geox_blocked"
READINESS_SAMPLE_DMA_READY = "dma_week_structurally_ready"

CALIBRATION_SAMPLE_VALID = "valid_governed_evidence"
CALIBRATION_SAMPLE_MISSING_UNCERTAINTY = "missing_uncertainty"
CALIBRATION_SAMPLE_METRIC_MISMATCH = "metric_mismatch"


@dataclass(frozen=True)
class CalibrationFixtureResult:
    """Calibration mapping fixture output for UI display."""

    evidence: CalibrationEvidenceInput
    requirement: CalibrationMappingRequirement
    signal: CalibrationSignal | None
    report: CalibrationMappingReport


@dataclass(frozen=True)
class IntakeOverviewExample:
    """Simple intake path recommendation example."""

    label: str
    session: MeasurementIntakeSession
    recommendation: IntakePathRecommendation


def build_dtc_skincare_advisory_plan() -> ColdStartAdvisoryPlan:
    """DTC skincare ecommerce with partial tracking and no paid history."""
    profile = build_cold_start_business_profile(
        profile_id="fixture-dtc-skincare",
        created_at=_NOW,
        business_type="ecommerce retail",
        product_or_service="DTC handmade skincare ecommerce",
        b2b_or_b2c="b2c",
        target_audience="Women 25-45 interested in clean beauty",
        monthly_budget="$2000",
        primary_objective=ColdStartMediaObjective.SALES,
        existing_website=True,
        existing_tracking=False,
        creative_assets_available=True,
        geography="United States",
    )
    return build_cold_start_advisory_plan(profile)


def build_local_fitness_advisory_plan() -> ColdStartAdvisoryPlan:
    """Local fitness studio with lead-generation objective."""
    profile = build_cold_start_business_profile(
        profile_id="fixture-local-fitness",
        created_at=_NOW,
        business_type="local service",
        product_or_service="local fitness studio memberships",
        b2b_or_b2c="b2c",
        target_audience="Adults within 10 miles of studio",
        monthly_budget="$1500",
        primary_objective=ColdStartMediaObjective.LEAD_GENERATION,
        geography="Austin, TX",
        existing_website=True,
        existing_tracking=False,
    )
    return build_cold_start_advisory_plan(profile)


def build_traffic_informed_advisory_plan() -> ColdStartAdvisoryPlan:
    """Advisory plan informed by governed website traffic summaries."""
    profile = build_cold_start_business_profile(
        profile_id="fixture-traffic-informed",
        created_at=_NOW,
        product_or_service="Handmade skincare ecommerce",
        target_audience="Women 25-45",
        monthly_budget="$2000",
        primary_objective=ColdStartMediaObjective.SALES,
        existing_website=True,
        existing_tracking=False,
    )
    traffic = WebsiteTrafficSourceProfile(
        traffic_profile_id="fixture-traffic-001",
        source_summary=(
            "organic search converts well; instagram referral has traffic but weak conversion; "
            "direct traffic attribution unclear"
        ),
        channel_group_summary="email traffic converts well",
        conversion_summary="organic search converts well on product pages",
        utm_coverage_summary="partial UTM coverage on paid links",
        created_at=_NOW,
    )
    return build_cold_start_advisory_plan(profile, traffic)


def build_advisory_plan(sample_key: str) -> ColdStartAdvisoryPlan:
    """Resolve an advisory fixture by sample key."""
    builders = {
        ADVISORY_SAMPLE_DTC_SKINCARE: build_dtc_skincare_advisory_plan,
        ADVISORY_SAMPLE_LOCAL_FITNESS: build_local_fitness_advisory_plan,
        ADVISORY_SAMPLE_TRAFFIC_INFORMED: build_traffic_informed_advisory_plan,
    }
    builder = builders.get(sample_key)
    if builder is None:
        msg = f"unknown advisory sample: {sample_key}"
        raise ValueError(msg)
    return builder()


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


def _session(**overrides: Any) -> MeasurementIntakeSession:
    base: dict[str, Any] = {
        "session_id": "sess-fixture-001",
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
        recommendation_id="rec-fixture-001",
        session_id=session.session_id,
        status=IntakeRecommendationStatus.RECOMMENDED,
        recommended_path=path,
        workflow_kind=session.workflow_kind,
        why_this_path=f"Fixture path {path.value}.",
        created_at=_NOW,
    )


def _plan(
    session: MeasurementIntakeSession,
    recommendation: IntakePathRecommendation,
) -> IntakePlan:
    return IntakePlan(
        plan_id="plan-fixture-001",
        session_id=session.session_id,
        recommendation_id=recommendation.recommendation_id,
        recommended_path=recommendation.recommended_path,
        required_assets=[],
        blocking_reasons=["placeholder_for_blocked_path_only"],
    )


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
        manifest: GeoXIntakeManifest | MMMIntakeManifest = GeoXIntakeManifest(
            manifest_id="man-geox-fixture-001",
            session_id=session.session_id,
            recommendation_id=rec.recommendation_id,
            plan_id=plan.plan_id,
            business_question=session.business_question,
            intended_use=session.intended_use,
            recommended_path=rec.recommended_path,
            created_at=_NOW,
        )
    else:
        manifest = MMMIntakeManifest(
            manifest_id="man-mmm-fixture-001",
            session_id=session.session_id,
            recommendation_id=rec.recommendation_id,
            plan_id=plan.plan_id,
            business_question=session.business_question,
            intended_use=session.intended_use,
            recommended_path=rec.recommended_path,
            created_at=_NOW,
        )
    return build_common_intake_workbench(session, rec, plan, manifest, [], [], profiles)


def build_national_blocked_readiness_reports() -> list[BaseWorkflowReadinessReport]:
    """National weekly data: MMM ready; GeoX and geo-level MMM blocked or need more data."""
    national = _national_profiles()
    mmm_workbench = _workbench(IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM, national)
    reports = list(build_workflow_readiness_reports(mmm_workbench))
    geo_level_mmm = build_mmm_data_readiness_report(
        _workbench(IntakeCandidatePath.GEO_LEVEL_MMM, national)
    )
    geox = build_geox_design_readiness_report(
        _workbench(
            IntakeCandidatePath.GEO_EXPERIMENT_DESIGN,
            national,
            workflow_kind=MeasurementWorkflowKind.GEOX,
        )
    )
    existing_types = {report.report_type for report in reports}
    if geo_level_mmm.report_type not in existing_types:
        reports.append(geo_level_mmm)
    if geox.report_type not in existing_types:
        reports.append(geox)
    return reports


def build_dma_readiness_reports() -> list[BaseWorkflowReadinessReport]:
    """DMA-week profiles structurally ready for geo workflows."""
    session = _session(geo_grain=GeoGrain.DMA)
    rec = _recommendation(session, IntakeCandidatePath.GEO_LEVEL_MMM)
    plan = _plan(session, rec)
    manifest = MMMIntakeManifest(
        manifest_id="man-dma-fixture-001",
        session_id=session.session_id,
        recommendation_id=rec.recommendation_id,
        plan_id=plan.plan_id,
        business_question=session.business_question,
        intended_use=session.intended_use,
        recommended_path=rec.recommended_path,
        created_at=_NOW,
    )
    workbench = build_common_intake_workbench(
        session, rec, plan, manifest, [], [], _dma_profiles()
    )
    return build_workflow_readiness_reports(workbench)


def build_readiness_reports(sample_key: str) -> list[BaseWorkflowReadinessReport]:
    """Resolve a readiness fixture by sample key."""
    if sample_key == READINESS_SAMPLE_NATIONAL_BLOCKED:
        return build_national_blocked_readiness_reports()
    if sample_key == READINESS_SAMPLE_DMA_READY:
        return build_dma_readiness_reports()
    msg = f"unknown readiness sample: {sample_key}"
    raise ValueError(msg)


def _calibration_evidence(**overrides: Any) -> CalibrationEvidenceInput:
    base: dict[str, Any] = {
        "input_id": "fixture-evidence-001",
        "metric_id": "revenue",
        "estimand_id": "incremental_revenue",
        "channel": "search",
        "platform": "google",
        "product_scope": "all_products",
        "geo_scope": "us",
        "time_window_start": _WINDOW_START,
        "time_window_end": _WINDOW_END,
        "effect_estimate": 0.12,
        "standard_error": 0.03,
        "lift_scale": "absolute",
        "evidence_type": "geox_readout",
        "is_causal": True,
        "freshness_status": "fresh",
        "source_artifact_id": "artifact-fixture-001",
        "source_experiment_id": "exp-fixture-001",
        "source_readout_id": "readout-fixture-001",
        "created_at": _NOW,
    }
    base.update(overrides)
    return CalibrationEvidenceInput(**base)


def _calibration_requirement(**overrides: Any) -> CalibrationMappingRequirement:
    base: dict[str, Any] = {
        "requirement_id": "fixture-req-001",
        "target_model_id": "mmm-fixture-001",
        "required_metric_id": "revenue",
        "required_estimand_id": "incremental_revenue",
        "required_channel": "search",
        "required_platform": "google",
        "required_product_scope": "all_products",
        "required_geo_scope": "us",
        "required_time_window_start": _WINDOW_START,
        "required_time_window_end": _WINDOW_END,
        "required_lift_scale": "absolute",
    }
    base.update(overrides)
    return CalibrationMappingRequirement(**base)


def build_valid_calibration_fixture() -> CalibrationFixtureResult:
    """Valid governed evidence maps to CalibrationSignal."""
    evidence = _calibration_evidence()
    requirement = _calibration_requirement()
    signal, report = map_evidence_to_calibration_signal(evidence, requirement)
    return CalibrationFixtureResult(
        evidence=evidence,
        requirement=requirement,
        signal=signal,
        report=report,
    )


def build_missing_uncertainty_calibration_fixture() -> CalibrationFixtureResult:
    """Evidence without uncertainty does not map to CalibrationSignal."""
    evidence = _calibration_evidence(
        standard_error=None,
        confidence_interval_low=None,
        confidence_interval_high=None,
    )
    requirement = _calibration_requirement()
    signal, report = map_evidence_to_calibration_signal(evidence, requirement)
    return CalibrationFixtureResult(
        evidence=evidence,
        requirement=requirement,
        signal=signal,
        report=report,
    )


def build_metric_mismatch_calibration_fixture() -> CalibrationFixtureResult:
    """Metric mismatch yields incompatible mapping report."""
    evidence = _calibration_evidence(metric_id="visits")
    requirement = _calibration_requirement()
    signal, report = map_evidence_to_calibration_signal(evidence, requirement)
    return CalibrationFixtureResult(
        evidence=evidence,
        requirement=requirement,
        signal=signal,
        report=report,
    )


def build_calibration_fixture(sample_key: str) -> CalibrationFixtureResult:
    """Resolve a calibration fixture by sample key."""
    builders = {
        CALIBRATION_SAMPLE_VALID: build_valid_calibration_fixture,
        CALIBRATION_SAMPLE_MISSING_UNCERTAINTY: build_missing_uncertainty_calibration_fixture,
        CALIBRATION_SAMPLE_METRIC_MISMATCH: build_metric_mismatch_calibration_fixture,
    }
    builder = builders.get(sample_key)
    if builder is None:
        msg = f"unknown calibration sample: {sample_key}"
        raise ValueError(msg)
    return builder()


def build_intake_overview_examples() -> list[IntakeOverviewExample]:
    """Simple intake path recommendation examples for optional overview tab."""
    national_session = _session(
        session_id="sess-overview-national",
        business_question="Can we run national MMM on weekly channel spend?",
        workflow_kind=MeasurementWorkflowKind.MMM,
        geo_grain=GeoGrain.NATIONAL,
    )
    geox_session = _session(
        session_id="sess-overview-geox",
        business_question="We need DMA-level GeoX design diagnostics.",
        workflow_kind=MeasurementWorkflowKind.GEOX,
        geo_grain=GeoGrain.DMA,
    )
    return [
        IntakeOverviewExample(
            label="National MMM diagnostic intake",
            session=national_session,
            recommendation=recommend_intake_path(national_session),
        ),
        IntakeOverviewExample(
            label="GeoX experiment design intake",
            session=geox_session,
            recommendation=recommend_intake_path(geox_session),
        ),
    ]


def advisory_sample_labels() -> dict[str, str]:
    """Human-readable labels for advisory fixture keys."""
    return {
        ADVISORY_SAMPLE_DTC_SKINCARE: "DTC skincare ecommerce",
        ADVISORY_SAMPLE_LOCAL_FITNESS: "Local fitness studio",
        ADVISORY_SAMPLE_TRAFFIC_INFORMED: "Traffic-informed advisory",
    }


def readiness_sample_labels() -> dict[str, str]:
    """Human-readable labels for readiness fixture keys."""
    return {
        READINESS_SAMPLE_NATIONAL_BLOCKED: "National-only MMM-ready but GeoX-blocked",
        READINESS_SAMPLE_DMA_READY: "DMA-week structurally ready",
    }


def calibration_sample_labels() -> dict[str, str]:
    """Human-readable labels for calibration fixture keys."""
    return {
        CALIBRATION_SAMPLE_VALID: "Valid governed evidence",
        CALIBRATION_SAMPLE_MISSING_UNCERTAINTY: "Missing uncertainty",
        CALIBRATION_SAMPLE_METRIC_MISMATCH: "Metric mismatch",
    }


def expected_advisory_evidence_mode(sample_key: str) -> AdvisoryEvidenceMode:
    """Expected evidence mode for advisory fixture assertions."""
    mapping = {
        ADVISORY_SAMPLE_DTC_SKINCARE: AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY,
        ADVISORY_SAMPLE_LOCAL_FITNESS: AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY,
        ADVISORY_SAMPLE_TRAFFIC_INFORMED: AdvisoryEvidenceMode.DATA_INFORMED_ADVISORY,
    }
    return mapping[sample_key]


def expected_advisory_claim_type(sample_key: str) -> AdvisoryClaimType:
    """Primary expected claim type for advisory fixture assertions."""
    if sample_key == ADVISORY_SAMPLE_TRAFFIC_INFORMED:
        return AdvisoryClaimType.DATA_INFORMED_HYPOTHESIS
    return AdvisoryClaimType.HYPOTHESIS_TO_TEST


def readiness_has_ready_report(reports: list[BaseWorkflowReadinessReport]) -> bool:
    """Whether any readiness report is structurally ready."""
    ready_statuses = {
        WorkflowReadinessStatus.READY,
        WorkflowReadinessStatus.READY_WITH_WARNINGS,
    }
    return any(report.status in ready_statuses for report in reports)


def calibration_maps_signal(result: CalibrationFixtureResult) -> bool:
    """Whether calibration fixture produced a mapped signal."""
    return (
        result.signal is not None
        and result.report.status == CalibrationIntakeStatus.MAPPED
    )
