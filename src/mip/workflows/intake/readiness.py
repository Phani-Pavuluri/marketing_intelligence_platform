"""Deterministic workflow-specific readiness report helpers (P5 / I7–I8)."""

from datetime import UTC, datetime

from mip.contracts.common_intake import (
    CommonDataProfileSummary,
    CommonIntakeWorkbench,
    ProfileFindingSeverity,
    WorkflowSupportAssessment,
    WorkflowSupportRoute,
    WorkflowSupportStatus,
)
from mip.contracts.intake import GeoGrain
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.workflow_readiness import (
    BaseWorkflowReadinessReport,
    CalibrationSignalReadinessReport,
    DecisionReviewReadinessReport,
    GeoXDesignReadinessReport,
    MMMDataReadinessReport,
    ReadinessBlockingReason,
    ReadinessWarningCode,
    WorkflowReadinessFinding,
    WorkflowReadinessStatus,
)

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
_BLOCKED_NEXT_DEFAULT = [
    "claim_design_feasibility",
    "claim_power_or_mde",
    "claim_matched_markets",
    "claim_lift_or_roi",
    "claim_final_decision",
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


def _has_asset(profiles: list[CommonDataProfileSummary], asset_type: DataAssetType) -> bool:
    target = _slug(asset_type)
    return any(_asset_type(profile) == target for profile in profiles)


def _profiles_for_asset(
    profiles: list[CommonDataProfileSummary],
    asset_type: DataAssetType,
) -> list[CommonDataProfileSummary]:
    target = _slug(asset_type)
    return [profile for profile in profiles if _asset_type(profile) == target]


def _is_geo_level_grain(grain: str) -> bool:
    return grain in _GEO_LEVEL_GRAINS


def _has_geo_level_outcome(profiles: list[CommonDataProfileSummary]) -> bool:
    for profile in _profiles_for_asset(profiles, DataAssetType.OUTCOME_KPI_DATA):
        if _is_geo_level_grain(_geo_grain(profile)):
            return True
    return False


def _has_geo_level_media(profiles: list[CommonDataProfileSummary]) -> bool:
    for profile in profiles:
        if _asset_type(profile) not in {
            _slug(DataAssetType.MEDIA_SPEND_DATA),
            _slug(DataAssetType.MEDIA_EXPOSURE_DATA),
        }:
            continue
        if _is_geo_level_grain(_geo_grain(profile)):
            return True
    return False


def _has_time_coverage(profiles: list[CommonDataProfileSummary]) -> bool:
    return any(
        profile.time_coverage is not None
        and (
            profile.time_coverage.period_count is not None
            or profile.time_coverage.time_min is not None
        )
        for profile in profiles
    )


def _has_channel_mapping(profiles: list[CommonDataProfileSummary]) -> bool:
    return _has_asset(profiles, DataAssetType.CHANNEL_MAPPING)


def _has_geo_mapping(profiles: list[CommonDataProfileSummary]) -> bool:
    return _has_asset(profiles, DataAssetType.GEO_MAPPING)


def _has_metric_mapping(profiles: list[CommonDataProfileSummary]) -> bool:
    return _has_asset(profiles, DataAssetType.METRIC_MAPPING)


def _has_calibration_signal_data(profiles: list[CommonDataProfileSummary]) -> bool:
    return _has_asset(profiles, DataAssetType.CALIBRATION_SIGNAL_DATA)


def _has_calibration_uncertainty(profiles: list[CommonDataProfileSummary]) -> bool:
    for profile in _profiles_for_asset(profiles, DataAssetType.CALIBRATION_SIGNAL_DATA):
        metrics = profile.metric_availability
        if not metrics:
            continue
        metric_ids = {mid.lower() for mid in metrics.metric_ids}
        if "effect_estimate" in metric_ids and (
            "standard_error" in metric_ids or "uncertainty" in metric_ids
        ):
            return True
        if metrics.primary_metric_candidates:
            lowered = {value.lower() for value in metrics.primary_metric_candidates}
            if "effect_estimate" in lowered and (
                "standard_error" in lowered or "uncertainty" in lowered
            ):
                return True
    return False


def _assessment(workbench: CommonIntakeWorkbench) -> WorkflowSupportAssessment:
    if workbench.workflow_support_assessment is None:
        msg = "workbench requires workflow_support_assessment for readiness reports"
        raise ValueError(msg)
    return workbench.workflow_support_assessment


def _route_supported(assessment: WorkflowSupportAssessment, route: WorkflowSupportRoute) -> bool:
    return any(_slug(item) == _slug(route) for item in assessment.supported_routes)


def _route_blocked(assessment: WorkflowSupportAssessment, route: WorkflowSupportRoute) -> bool:
    return any(_slug(item) == _slug(route) for item in assessment.blocked_routes)


def _reason_present(assessment: WorkflowSupportAssessment, reason: str) -> bool:
    return reason in assessment.route_reasons


def _profile_flags(
    profiles: list[CommonDataProfileSummary],
) -> dict[str, bool]:
    return {
        "has_outcome_data": _has_asset(profiles, DataAssetType.OUTCOME_KPI_DATA),
        "has_media_data": _has_asset(profiles, DataAssetType.MEDIA_SPEND_DATA)
        or _has_asset(profiles, DataAssetType.MEDIA_EXPOSURE_DATA),
        "has_time_coverage": _has_time_coverage(profiles),
        "has_channel_mapping": _has_channel_mapping(profiles),
        "has_geo_level_data": _has_geo_level_outcome(profiles) and _has_geo_level_media(profiles),
        "has_geo_level_outcome": _has_geo_level_outcome(profiles),
        "has_geo_level_media": _has_geo_level_media(profiles),
        "has_geo_mapping": _has_geo_mapping(profiles),
        "has_metric_mapping": _has_metric_mapping(profiles),
        "has_calibration_signal_data": _has_calibration_signal_data(profiles),
        "has_calibration_uncertainty": _has_calibration_uncertainty(profiles),
    }


def _finding(
    *,
    finding_id: str,
    severity: ProfileFindingSeverity,
    code: str,
    message: str,
    related_route: WorkflowSupportRoute | None = None,
    related_profile_ids: list[str] | None = None,
) -> WorkflowReadinessFinding:
    return WorkflowReadinessFinding(
        finding_id=finding_id,
        severity=severity,
        code=code,
        message=message,
        related_route=related_route,
        related_profile_ids=related_profile_ids or [],
    )


def _primary_mmm_route(assessment: WorkflowSupportAssessment) -> WorkflowSupportRoute | None:
    for route in (
        WorkflowSupportRoute.CALIBRATED_MMM,
        WorkflowSupportRoute.GEO_LEVEL_MMM,
        WorkflowSupportRoute.NATIONAL_MMM,
    ):
        if _route_supported(assessment, route):
            return route
    for route in (
        WorkflowSupportRoute.CALIBRATED_MMM,
        WorkflowSupportRoute.GEO_LEVEL_MMM,
        WorkflowSupportRoute.NATIONAL_MMM,
    ):
        if _route_blocked(assessment, route):
            return route
    return None


def build_mmm_data_readiness_report(workbench: CommonIntakeWorkbench) -> MMMDataReadinessReport:
    """Build MMM structural data readiness from common intake workbench."""
    assessment = _assessment(workbench)
    profiles = list(workbench.profile_summaries)
    flags = _profile_flags(profiles)
    mmm_route = _primary_mmm_route(assessment)
    findings: list[WorkflowReadinessFinding] = []
    warnings: list[str] = list(assessment.warnings)
    blocking_reasons: list[str] = []
    required_next: list[str] = []
    allowed_next: list[str] = []
    blocked_next = list(_BLOCKED_NEXT_DEFAULT)
    status = WorkflowReadinessStatus.NOT_APPLICABLE
    calibration_required = mmm_route == WorkflowSupportRoute.CALIBRATED_MMM

    if mmm_route is None:
        status = WorkflowReadinessStatus.NOT_APPLICABLE
        findings.append(
            _finding(
                finding_id=f"{workbench.session_id}-mmm-na",
                severity=ProfileFindingSeverity.INFO,
                code=ReadinessBlockingReason.UNSUPPORTED_ROUTE.value,
                message="No MMM workflow route referenced by workflow support assessment.",
            )
        )
    elif mmm_route == WorkflowSupportRoute.NATIONAL_MMM:
        if _route_supported(assessment, WorkflowSupportRoute.NATIONAL_MMM):
            status = WorkflowReadinessStatus.READY
            allowed_next.append("prepare_mmm_diagnostic_request")
        else:
            status = WorkflowReadinessStatus.NEEDS_MORE_DATA
        if not flags["has_outcome_data"]:
            status = WorkflowReadinessStatus.NEEDS_MORE_DATA
            blocking_reasons.append(ReadinessBlockingReason.MISSING_OUTCOME_DATA.value)
            required_next.append("outcome_kpi_data")
        if not flags["has_media_data"]:
            status = WorkflowReadinessStatus.NEEDS_MORE_DATA
            blocking_reasons.append(ReadinessBlockingReason.MISSING_MEDIA_DATA.value)
            required_next.append("media_spend_or_exposure")
    elif mmm_route == WorkflowSupportRoute.GEO_LEVEL_MMM:
        if _route_supported(assessment, WorkflowSupportRoute.GEO_LEVEL_MMM):
            status = WorkflowReadinessStatus.READY
            allowed_next.append("prepare_mmm_diagnostic_request")
        else:
            status = WorkflowReadinessStatus.NEEDS_MORE_DATA
            if not flags["has_geo_level_outcome"]:
                blocking_reasons.append(ReadinessBlockingReason.MISSING_GEO_LEVEL_DATA.value)
                required_next.append("geo_level_outcome_kpi")
            if not flags["has_geo_level_media"]:
                blocking_reasons.append(ReadinessBlockingReason.MISSING_MEDIA_DATA.value)
                required_next.append("geo_level_media")
    elif mmm_route == WorkflowSupportRoute.CALIBRATED_MMM:
        calibration_required = True
        if _route_supported(assessment, WorkflowSupportRoute.CALIBRATED_MMM):
            status = WorkflowReadinessStatus.READY
            allowed_next.append("prepare_calibrated_mmm_candidate")
        else:
            status = WorkflowReadinessStatus.NEEDS_MORE_DATA
            blocking_reasons.append(ReadinessBlockingReason.MISSING_CALIBRATION_UNCERTAINTY.value)
            required_next.append("calibration_signal_uncertainty")
            findings.append(
                _finding(
                    finding_id=f"{workbench.session_id}-mmm-cal-blocked",
                    severity=ProfileFindingSeverity.ERROR,
                    code=ReadinessBlockingReason.MISSING_CALIBRATION_UNCERTAINTY.value,
                    message=(
                        "Calibrated MMM requires calibration uncertainty in governed summaries."
                    ),
                    related_route=WorkflowSupportRoute.CALIBRATED_MMM,
                )
            )

    if _reason_present(assessment, "blocked_needs_metric_mapping"):
        warnings.append(ReadinessWarningCode.INCOMPLETE_MEDIA_COVERAGE.value)
        if status == WorkflowReadinessStatus.READY:
            status = WorkflowReadinessStatus.READY_WITH_WARNINGS

    if assessment.support_status == WorkflowSupportStatus.BLOCKED:
        status = WorkflowReadinessStatus.BLOCKED
        blocking_reasons.extend(assessment.blocking_reasons)

    if warnings and status == WorkflowReadinessStatus.READY:
        status = WorkflowReadinessStatus.READY_WITH_WARNINGS

    return MMMDataReadinessReport(
        report_id=f"{workbench.session_id}-mmm-readiness",
        session_id=workbench.session_id,
        recommendation_id=workbench.recommendation_id,
        manifest_id=workbench.manifest_id,
        assessment_id=assessment.assessment_id,
        status=status,
        supported_route=mmm_route,
        mmm_route=mmm_route,
        has_outcome_data=flags["has_outcome_data"],
        has_media_data=flags["has_media_data"],
        has_time_coverage=flags["has_time_coverage"],
        has_channel_mapping=flags["has_channel_mapping"],
        has_geo_level_data=flags["has_geo_level_data"],
        has_calibration_signal_data=flags["has_calibration_signal_data"],
        calibration_required=calibration_required,
        findings=findings,
        required_next_inputs=required_next,
        allowed_next_steps=allowed_next,
        blocked_next_steps=blocked_next,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        created_at=datetime.now(tz=UTC),
    )


def build_geox_design_readiness_report(
    workbench: CommonIntakeWorkbench,
) -> GeoXDesignReadinessReport:
    """Build GeoX design structural readiness from common intake workbench."""
    assessment = _assessment(workbench)
    profiles = list(workbench.profile_summaries)
    flags = _profile_flags(profiles)
    findings: list[WorkflowReadinessFinding] = []
    warnings: list[str] = []
    blocking_reasons: list[str] = []
    required_next: list[str] = []
    allowed_next: list[str] = []
    blocked_next = list(_BLOCKED_NEXT_DEFAULT)

    route = WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS
    if not _route_supported(assessment, route) and not _route_blocked(assessment, route):
        status = WorkflowReadinessStatus.NOT_APPLICABLE
    elif _route_supported(assessment, route):
        status = WorkflowReadinessStatus.READY
        allowed_next.append("prepare_panel_exp_diagnostic_request")
        if assessment.warnings:
            status = WorkflowReadinessStatus.READY_WITH_WARNINGS
            warnings.extend(assessment.warnings)
        warnings.append(ReadinessWarningCode.DIAGNOSTIC_REQUIRED_NEXT.value)
    else:
        status = WorkflowReadinessStatus.NEEDS_MORE_DATA
        if _reason_present(assessment, "blocked_needs_geo_level_outcome"):
            blocking_reasons.append(ReadinessBlockingReason.MISSING_GEO_LEVEL_DATA.value)
            required_next.append("geo_level_outcome_kpi")
            findings.append(
                _finding(
                    finding_id=f"{workbench.session_id}-geox-outcome",
                    severity=ProfileFindingSeverity.ERROR,
                    code=ReadinessBlockingReason.MISSING_GEO_LEVEL_DATA.value,
                    message="GeoX design requires geo-level outcome data in governed summaries.",
                    related_route=route,
                )
            )
        if _reason_present(assessment, "blocked_needs_geo_level_media"):
            blocking_reasons.append(ReadinessBlockingReason.MISSING_MEDIA_DATA.value)
            required_next.append("geo_level_media_or_exposure")
            findings.append(
                _finding(
                    finding_id=f"{workbench.session_id}-geox-media",
                    severity=ProfileFindingSeverity.ERROR,
                    code=ReadinessBlockingReason.MISSING_MEDIA_DATA.value,
                    message="GeoX design requires geo-level media or exposure data.",
                    related_route=route,
                )
            )
        if not flags["has_geo_mapping"]:
            required_next.append("geo_mapping")

    structurally_ready = status in {
        WorkflowReadinessStatus.READY,
        WorkflowReadinessStatus.READY_WITH_WARNINGS,
    }

    return GeoXDesignReadinessReport(
        report_id=f"{workbench.session_id}-geox-readiness",
        session_id=workbench.session_id,
        recommendation_id=workbench.recommendation_id,
        manifest_id=workbench.manifest_id,
        assessment_id=assessment.assessment_id,
        status=status,
        supported_route=route if structurally_ready else None,
        has_geo_level_outcome=flags["has_geo_level_outcome"],
        has_geo_level_media=flags["has_geo_level_media"],
        has_geo_mapping=flags["has_geo_mapping"],
        has_time_coverage=flags["has_time_coverage"],
        has_objective_kpi_alignment=flags["has_metric_mapping"],
        requires_panel_exp_diagnostics=structurally_ready,
        requires_power_diagnostic=structurally_ready,
        requires_matchability_diagnostic=structurally_ready and flags["has_geo_level_outcome"],
        requires_duration_sensitivity=structurally_ready,
        findings=findings,
        required_next_inputs=required_next,
        allowed_next_steps=allowed_next,
        blocked_next_steps=blocked_next,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        created_at=datetime.now(tz=UTC),
    )


def build_calibration_signal_readiness_report(
    workbench: CommonIntakeWorkbench,
) -> CalibrationSignalReadinessReport:
    """Build CalibrationSignal intake structural readiness."""
    assessment = _assessment(workbench)
    profiles = list(workbench.profile_summaries)
    flags = _profile_flags(profiles)
    route = WorkflowSupportRoute.CALIBRATION_SIGNAL_INTAKE

    has_effect = flags["has_calibration_uncertainty"] or any(
        profile.metric_availability is not None
        and "effect_estimate" in {m.lower() for m in profile.metric_availability.metric_ids}
        for profile in profiles
    )
    has_uncertainty = flags["has_calibration_uncertainty"]
    has_metric_mapping = flags["has_metric_mapping"]
    has_estimand_mapping = _has_asset(profiles, DataAssetType.METRIC_MAPPING)
    has_scope_mapping = flags["has_geo_mapping"] or _has_channel_mapping(profiles)
    has_time_window = _has_time_coverage(profiles)

    status = WorkflowReadinessStatus.NOT_APPLICABLE
    blocking_reasons: list[str] = []
    required_next: list[str] = []
    allowed_next: list[str] = []
    findings: list[WorkflowReadinessFinding] = []

    if _route_supported(assessment, route):
        status = WorkflowReadinessStatus.READY
        allowed_next.append("prepare_calibration_signal_mapping")
    elif _route_blocked(assessment, route):
        status = WorkflowReadinessStatus.NEEDS_MORE_DATA
        if not has_effect:
            blocking_reasons.append(ReadinessBlockingReason.MISSING_OUTCOME_DATA.value)
            required_next.append("effect_estimate")
        if not has_uncertainty:
            blocking_reasons.append(ReadinessBlockingReason.MISSING_CALIBRATION_UNCERTAINTY.value)
            required_next.append("uncertainty_or_standard_error")
        if not has_metric_mapping:
            blocking_reasons.append(ReadinessBlockingReason.MISSING_METRIC_MAPPING.value)
            required_next.append("metric_mapping")

    calibration_signal_ready = (
        status == WorkflowReadinessStatus.READY
        and has_effect
        and has_uncertainty
        and has_metric_mapping
    )

    return CalibrationSignalReadinessReport(
        report_id=f"{workbench.session_id}-cal-readiness",
        session_id=workbench.session_id,
        recommendation_id=workbench.recommendation_id,
        manifest_id=workbench.manifest_id,
        assessment_id=assessment.assessment_id,
        status=status,
        supported_route=route if calibration_signal_ready else None,
        has_effect_estimate=has_effect,
        has_uncertainty=has_uncertainty,
        has_metric_mapping=has_metric_mapping,
        has_estimand_mapping=has_estimand_mapping,
        has_scope_mapping=has_scope_mapping,
        has_time_window=has_time_window,
        calibration_signal_ready=calibration_signal_ready,
        findings=findings,
        required_next_inputs=required_next,
        allowed_next_steps=allowed_next,
        blocked_next_steps=list(_BLOCKED_NEXT_DEFAULT),
        warnings=list(assessment.warnings),
        blocking_reasons=blocking_reasons,
        created_at=datetime.now(tz=UTC),
    )


def build_decision_review_readiness_report(
    workbench: CommonIntakeWorkbench,
) -> DecisionReviewReadinessReport:
    """Build decision-review structural readiness."""
    assessment = _assessment(workbench)
    grounding = workbench.llm_grounding_context
    route = WorkflowSupportRoute.DECISION_REVIEW

    has_trust_report = bool(grounding and grounding.trust_report_ids)
    has_artifacts = bool(workbench.profile_summaries) and bool(workbench.ingestion_records)
    has_metric_estimand_scope = _has_metric_mapping(list(workbench.profile_summaries))
    has_freshness_context = any(
        profile.time_coverage is not None for profile in workbench.profile_summaries
    )

    status = WorkflowReadinessStatus.NOT_APPLICABLE
    blocking_reasons: list[str] = []
    required_next: list[str] = []
    allowed_next: list[str] = []

    if _route_supported(assessment, route):
        status = WorkflowReadinessStatus.READY_WITH_WARNINGS
        if not has_trust_report:
            status = WorkflowReadinessStatus.NEEDS_MORE_DATA
            blocking_reasons.append(ReadinessBlockingReason.MISSING_TRUST_REPORT.value)
            required_next.append("trust_report")
        if not has_artifacts:
            status = WorkflowReadinessStatus.NEEDS_MORE_DATA
            required_next.append("supported_artifacts")
        if not has_metric_estimand_scope:
            required_next.append("metric_estimand_scope")
        if status == WorkflowReadinessStatus.READY_WITH_WARNINGS:
            allowed_next.append("assemble_decision_review_packet_draft")
    elif _route_blocked(assessment, route):
        status = WorkflowReadinessStatus.BLOCKED
        blocking_reasons.append(ReadinessBlockingReason.UNSUPPORTED_ROUTE.value)

    decision_review_ready = status == WorkflowReadinessStatus.READY_WITH_WARNINGS and all(
        [has_trust_report, has_artifacts, has_metric_estimand_scope]
    )

    return DecisionReviewReadinessReport(
        report_id=f"{workbench.session_id}-decision-readiness",
        session_id=workbench.session_id,
        recommendation_id=workbench.recommendation_id,
        manifest_id=workbench.manifest_id,
        assessment_id=assessment.assessment_id,
        status=status,
        supported_route=route if decision_review_ready else None,
        has_trust_report=has_trust_report,
        has_supported_artifacts=has_artifacts,
        has_metric_estimand_scope=has_metric_estimand_scope,
        has_freshness_context=has_freshness_context,
        requires_human_approval=True,
        decision_review_ready=decision_review_ready,
        required_next_inputs=required_next,
        allowed_next_steps=allowed_next,
        blocked_next_steps=list(_BLOCKED_NEXT_DEFAULT) + ["approve_final_decision"],
        warnings=list(assessment.warnings),
        blocking_reasons=blocking_reasons,
        created_at=datetime.now(tz=UTC),
    )


def _route_referenced(
    assessment: WorkflowSupportAssessment,
    route: WorkflowSupportRoute,
) -> bool:
    return _route_supported(assessment, route) or _route_blocked(assessment, route)


def build_workflow_readiness_reports(
    workbench: CommonIntakeWorkbench,
) -> list[BaseWorkflowReadinessReport]:
    """Build workflow-specific readiness reports for routes in the assessment."""
    assessment = _assessment(workbench)
    reports: list[BaseWorkflowReadinessReport] = []

    if any(
        _route_referenced(assessment, route)
        for route in (
            WorkflowSupportRoute.NATIONAL_MMM,
            WorkflowSupportRoute.GEO_LEVEL_MMM,
            WorkflowSupportRoute.CALIBRATED_MMM,
        )
    ):
        reports.append(build_mmm_data_readiness_report(workbench))

    if _route_referenced(assessment, WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS):
        reports.append(build_geox_design_readiness_report(workbench))

    if _route_referenced(assessment, WorkflowSupportRoute.CALIBRATION_SIGNAL_INTAKE):
        reports.append(build_calibration_signal_readiness_report(workbench))

    if _route_referenced(assessment, WorkflowSupportRoute.DECISION_REVIEW):
        reports.append(build_decision_review_readiness_report(workbench))

    return reports
