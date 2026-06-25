"""Deterministic common intake workbench helpers (P4c / I6c)."""

from collections.abc import Sequence
from datetime import UTC, datetime

from mip.contracts.common_intake import (
    CommonDataProfileSummary,
    CommonIntakeStatus,
    CommonIntakeWorkbench,
    DataSnapshot,
    LLMAnswerGroundingContext,
    SourceIngestionRecord,
    WorkflowSupportAssessment,
    WorkflowSupportRoute,
    WorkflowSupportStatus,
)
from mip.contracts.intake import (
    GeoGrain,
    IntakeCandidatePath,
    IntakePathRecommendation,
    IntakeRecommendationStatus,
    MeasurementIntakeSession,
)
from mip.contracts.intake_assets import DataAssetType, IntakePlan
from mip.contracts.intake_sources import GeoXIntakeManifest, IntakeManifestStatus, MMMIntakeManifest

_GEO_LEVEL_GRAINS = frozenset(
    {
        GeoGrain.GEO,
        GeoGrain.DMA,
        GeoGrain.REGION,
        GeoGrain.MARKET,
        "geo",
        "dma",
        "region",
        "market",
    }
)
_MEDIA_ASSETS = frozenset(
    {
        DataAssetType.MEDIA_SPEND_DATA,
        DataAssetType.MEDIA_EXPOSURE_DATA,
        "media_spend_data",
        "media_exposure_data",
    }
)
_MAPPING_ASSETS = frozenset(
    {
        DataAssetType.CHANNEL_MAPPING,
        DataAssetType.GEO_MAPPING,
        DataAssetType.PRODUCT_MAPPING,
        DataAssetType.METRIC_MAPPING,
        "channel_mapping",
        "geo_mapping",
        "product_mapping",
        "metric_mapping",
    }
)

_DEFAULT_BLOCKED_TOPICS = [
    "causal_lift",
    "roi",
    "budget_recommendation",
    "final_test_duration",
    "mde_power_result",
    "matched_markets",
    "treatment_control_assignment",
    "production_decision",
]

_DEFAULT_ALLOWED_TOPICS = [
    "data_coverage",
    "missing_data",
    "grain_mismatch",
    "workflow_support_status",
    "next_required_inputs",
    "workflow_blocked_explanation",
]


def _slug(value: object) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _asset_type(profile: CommonDataProfileSummary) -> str:
    return _slug(profile.asset_type)


def _geo_grain(profile: CommonDataProfileSummary) -> str:
    if profile.geo_coverage is not None:
        return _slug(profile.geo_coverage.geo_grain)
    return GeoGrain.UNKNOWN.value


def _has_asset(profiles: Sequence[CommonDataProfileSummary], asset_type: DataAssetType) -> bool:
    target = _slug(asset_type)
    return any(_asset_type(profile) == target for profile in profiles)


def _profiles_for_asset(
    profiles: Sequence[CommonDataProfileSummary],
    asset_type: DataAssetType,
) -> list[CommonDataProfileSummary]:
    target = _slug(asset_type)
    return [profile for profile in profiles if _asset_type(profile) == target]


def _is_geo_level_grain(grain: str) -> bool:
    return grain in _GEO_LEVEL_GRAINS


def _has_geo_level_outcome(profiles: Sequence[CommonDataProfileSummary]) -> bool:
    for profile in _profiles_for_asset(profiles, DataAssetType.OUTCOME_KPI_DATA):
        if _is_geo_level_grain(_geo_grain(profile)):
            return True
    return False


def _has_geo_level_media(profiles: Sequence[CommonDataProfileSummary]) -> bool:
    for profile in profiles:
        if _asset_type(profile) not in {_slug(a) for a in _MEDIA_ASSETS}:
            continue
        if _is_geo_level_grain(_geo_grain(profile)):
            return True
        if profile.media_coverage and profile.media_coverage.spend_present:
            if _is_geo_level_grain(_geo_grain(profile)):
                return True
    return False


def _has_mapping_coverage(profiles: Sequence[CommonDataProfileSummary]) -> bool:
    present = {_asset_type(profile) for profile in profiles}
    mapping_slugs = {_slug(asset) for asset in _MAPPING_ASSETS}
    return bool(present.intersection(mapping_slugs))


def _has_geo_mapping(profiles: Sequence[CommonDataProfileSummary]) -> bool:
    return _has_asset(profiles, DataAssetType.GEO_MAPPING)


def _has_calibration_uncertainty(profiles: Sequence[CommonDataProfileSummary]) -> bool:
    if not _has_asset(profiles, DataAssetType.CALIBRATION_SIGNAL_DATA):
        return False
    for profile in _profiles_for_asset(profiles, DataAssetType.CALIBRATION_SIGNAL_DATA):
        metrics = profile.metric_availability
        if metrics and metrics.metric_ids and not metrics.missing_metric_ids:
            return True
        if metrics and metrics.primary_metric_candidates:
            return True
    return False


def _manifest_id(manifest: MMMIntakeManifest | GeoXIntakeManifest) -> str:
    return manifest.manifest_id


def _manifest_blocked(manifest: MMMIntakeManifest | GeoXIntakeManifest) -> bool:
    return _slug(manifest.status) == _slug(IntakeManifestStatus.BLOCKED)


def build_workflow_support_assessment(
    session: MeasurementIntakeSession,
    recommendation: IntakePathRecommendation,
    plan: IntakePlan,
    manifest: MMMIntakeManifest | GeoXIntakeManifest,
    profiles: Sequence[CommonDataProfileSummary],
) -> WorkflowSupportAssessment:
    """Assess structural workflow support from governed profile summaries only."""
    path = _slug(recommendation.recommended_path)
    supported: list[WorkflowSupportRoute] = []
    blocked: list[WorkflowSupportRoute] = []
    route_reasons: list[str] = []
    missing: list[str] = []
    warnings: list[str] = []
    blocking_reasons: list[str] = []
    allowed_next: list[str] = []
    blocked_next: list[str] = ["claim_design_feasibility", "claim_power_or_mde"]

    has_outcome = _has_asset(profiles, DataAssetType.OUTCOME_KPI_DATA)
    has_media = _has_asset(profiles, DataAssetType.MEDIA_SPEND_DATA) or _has_asset(
        profiles, DataAssetType.MEDIA_EXPOSURE_DATA
    )
    has_mapping = _has_mapping_coverage(profiles)
    geo_outcome = _has_geo_level_outcome(profiles)
    geo_media = _has_geo_level_media(profiles)
    geo_mapping = _has_geo_mapping(profiles)
    has_calibration = _has_calibration_uncertainty(profiles)
    has_experiment_export = _has_asset(profiles, DataAssetType.EXPERIMENT_EXPORT_DATA)

    if not profiles:
        return WorkflowSupportAssessment(
            assessment_id=f"{session.session_id}-wsa",
            session_id=session.session_id,
            recommendation_id=recommendation.recommendation_id,
            plan_id=plan.plan_id,
            manifest_id=_manifest_id(manifest),
            profile_ids=[],
            supported_routes=[],
            blocked_routes=list(WorkflowSupportRoute),
            support_status=WorkflowSupportStatus.NOT_ASSESSED,
            route_reasons=["profiles_not_provided"],
            missing_data_requirements=["common_data_profile_summaries"],
            warnings=["No profile summaries supplied for workflow support assessment."],
            allowed_next_steps=["declare_sources_and_build_profiles"],
            blocked_next_steps=blocked_next,
            created_at=datetime.now(tz=UTC),
        )

    profile_ids = [profile.profile_id for profile in profiles]

    if path == _slug(IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM):
        if has_outcome and has_media and has_mapping:
            supported.append(WorkflowSupportRoute.NATIONAL_MMM)
            route_reasons.append("supports_national_mmm")
        else:
            missing.append("outcome_kpi_data")
            if not has_media:
                missing.append("media_spend_or_exposure")
            if not has_mapping:
                missing.append("mapping_sources")
        if not geo_outcome:
            blocked.extend(
                [
                    WorkflowSupportRoute.GEO_LEVEL_MMM,
                    WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS,
                ]
            )
            route_reasons.extend(
                [
                    "blocked_needs_geo_level_outcome",
                    "blocked_needs_geo_level_media",
                ]
            )
        if not geo_media:
            if WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS not in blocked:
                blocked.append(WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS)
            if "blocked_needs_geo_level_media" not in route_reasons:
                route_reasons.append("blocked_needs_geo_level_media")

    elif path == _slug(IntakeCandidatePath.GEO_LEVEL_MMM):
        if geo_outcome and geo_media and has_mapping:
            supported.append(WorkflowSupportRoute.GEO_LEVEL_MMM)
            route_reasons.append("supports_geo_level_mmm")
        else:
            if not geo_outcome:
                route_reasons.append("blocked_needs_geo_level_outcome")
                missing.append("geo_level_outcome_kpi")
            if not geo_media:
                route_reasons.append("blocked_needs_geo_level_media")
                missing.append("geo_level_media")
            blocked.append(WorkflowSupportRoute.GEO_LEVEL_MMM)

    elif path in {
        _slug(IntakeCandidatePath.CALIBRATED_MMM),
        _slug(IntakeCandidatePath.DECISION_SURFACE_CERTIFICATION),
    }:
        if has_calibration and has_outcome:
            supported.append(WorkflowSupportRoute.CALIBRATED_MMM)
            supported.append(WorkflowSupportRoute.CALIBRATION_SIGNAL_INTAKE)
            route_reasons.append("supports_calibration_signal_intake")
        else:
            if not has_calibration:
                route_reasons.append("blocked_needs_calibration_uncertainty")
                missing.append("calibration_signal_uncertainty")
            blocked.append(WorkflowSupportRoute.CALIBRATED_MMM)
            blocked.append(WorkflowSupportRoute.CALIBRATION_SIGNAL_INTAKE)

    elif path == _slug(IntakeCandidatePath.GEO_EXPERIMENT_DESIGN):
        if geo_outcome and geo_mapping and geo_media:
            supported.append(WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS)
            route_reasons.append("supports_geox_design_diagnostics")
            warnings.append(
                "Structural GeoX design support only; panel_exp must assess feasibility."
            )
        else:
            if not geo_outcome:
                route_reasons.append("blocked_needs_geo_level_outcome")
                missing.append("geo_level_outcome_kpi")
            if not geo_media:
                route_reasons.append("blocked_needs_geo_level_media")
                missing.append("geo_level_media_or_exposure")
            if not geo_mapping:
                missing.append("geo_mapping")
            blocked.append(WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS)

    elif path == _slug(IntakeCandidatePath.GEO_EXPERIMENT_READOUT):
        if has_experiment_export and has_outcome:
            supported.append(WorkflowSupportRoute.GEOX_READOUT)
            route_reasons.append("supports_geox_readout_structurally")
        else:
            missing.append("experiment_export_and_outcome")
            blocked.append(WorkflowSupportRoute.GEOX_READOUT)

    elif path == _slug(IntakeCandidatePath.EXPERIMENT_CALIBRATION_INTAKE):
        if has_calibration or has_experiment_export:
            supported.append(WorkflowSupportRoute.CALIBRATION_SIGNAL_INTAKE)
            route_reasons.append("supports_calibration_signal_intake")
        else:
            route_reasons.append("blocked_needs_calibration_uncertainty")
            missing.append("calibration_signal_or_experiment_export")
            blocked.append(WorkflowSupportRoute.CALIBRATION_SIGNAL_INTAKE)

    elif path == _slug(IntakeCandidatePath.DECISION_REVIEW_PACKET):
        supported.append(WorkflowSupportRoute.DECISION_REVIEW)
        route_reasons.append("decision_review_route_declared")

    if not has_mapping and has_outcome:
        route_reasons.append("blocked_needs_metric_mapping")
        warnings.append("Metric mapping not represented in profile summaries.")

    support_status = WorkflowSupportStatus.SUPPORTED
    if _manifest_blocked(manifest) or recommendation.status == IntakeRecommendationStatus.BLOCKED:
        support_status = WorkflowSupportStatus.BLOCKED
        blocking_reasons.extend(manifest.blocking_reasons or [])
        blocking_reasons.extend(recommendation.blocking_reasons or [])
    elif not supported:
        support_status = WorkflowSupportStatus.NEEDS_MORE_DATA
    elif warnings:
        support_status = WorkflowSupportStatus.SUPPORTED_WITH_WARNINGS
    elif blocked:
        support_status = WorkflowSupportStatus.SUPPORTED_WITH_WARNINGS

    if supported:
        allowed_next.append("review_workflow_support_assessment")
        allowed_next.append("prepare_workflow_specific_readiness")

    return WorkflowSupportAssessment(
        assessment_id=f"{session.session_id}-wsa",
        session_id=session.session_id,
        recommendation_id=recommendation.recommendation_id,
        plan_id=plan.plan_id,
        manifest_id=_manifest_id(manifest),
        profile_ids=profile_ids,
        supported_routes=supported,
        blocked_routes=blocked,
        support_status=support_status,
        route_reasons=route_reasons,
        missing_data_requirements=missing,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        allowed_next_steps=allowed_next,
        blocked_next_steps=blocked_next,
        created_at=datetime.now(tz=UTC),
    )


def build_llm_answer_grounding_context(
    session: MeasurementIntakeSession,
    profiles: Sequence[CommonDataProfileSummary],
    assessment: WorkflowSupportAssessment,
) -> LLMAnswerGroundingContext:
    """Build LLM-safe grounding context from governed summaries only."""
    allowed_sources = [profile.profile_id for profile in profiles]
    allowed_sources.append(assessment.assessment_id)

    return LLMAnswerGroundingContext(
        context_id=f"{session.session_id}-llm-grounding",
        session_id=session.session_id,
        allowed_sources=allowed_sources,
        profile_summaries=[profile.profile_id for profile in profiles],
        workflow_support_assessment=assessment.assessment_id,
        allowed_answer_topics=list(_DEFAULT_ALLOWED_TOPICS),
        blocked_answer_topics=list(_DEFAULT_BLOCKED_TOPICS),
        warnings=list(assessment.warnings),
        blocking_reasons=list(assessment.blocking_reasons),
        created_at=datetime.now(tz=UTC),
    )


def build_common_intake_workbench(
    session: MeasurementIntakeSession,
    recommendation: IntakePathRecommendation,
    plan: IntakePlan,
    manifest: MMMIntakeManifest | GeoXIntakeManifest,
    ingestion_records: Sequence[SourceIngestionRecord],
    snapshots: Sequence[DataSnapshot],
    profiles: Sequence[CommonDataProfileSummary],
) -> CommonIntakeWorkbench:
    """Assemble the shared common intake workbench."""
    warnings: list[str] = []
    blocking_reasons: list[str] = []

    if _manifest_blocked(manifest):
        blocking_reasons.extend(manifest.blocking_reasons or [])
    if recommendation.status == IntakeRecommendationStatus.BLOCKED:
        blocking_reasons.extend(recommendation.blocking_reasons or [])

    assessment = build_workflow_support_assessment(
        session,
        recommendation,
        plan,
        manifest,
        profiles,
    )
    grounding = build_llm_answer_grounding_context(session, profiles, assessment)

    status = CommonIntakeStatus.DRAFT
    if blocking_reasons or assessment.support_status == WorkflowSupportStatus.BLOCKED:
        status = CommonIntakeStatus.BLOCKED
    elif assessment.support_status != WorkflowSupportStatus.NOT_ASSESSED:
        status = CommonIntakeStatus.SUPPORT_ASSESSED
    elif profiles:
        status = CommonIntakeStatus.PROFILED
    elif ingestion_records or snapshots:
        status = CommonIntakeStatus.SOURCES_DECLARED
    else:
        status = CommonIntakeStatus.COLLECTING_SOURCES

    if not ingestion_records and not snapshots:
        warnings.append("No ingestion records or snapshots declared yet.")

    return CommonIntakeWorkbench(
        workbench_id=f"{session.session_id}-workbench",
        session_id=session.session_id,
        recommendation_id=recommendation.recommendation_id,
        plan_id=plan.plan_id,
        manifest_id=_manifest_id(manifest),
        ingestion_records=list(ingestion_records),
        snapshots=list(snapshots),
        profile_summaries=list(profiles),
        workflow_support_assessment=assessment,
        llm_grounding_context=grounding,
        status=status,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        created_at=datetime.now(tz=UTC),
    )
