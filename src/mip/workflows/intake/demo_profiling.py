"""Local/demo tabular profiling helpers (P8)."""

from __future__ import annotations

import uuid
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime

from mip.contracts.advisory import WebsiteTrafficSourceProfile
from mip.contracts.calibration_intake import CalibrationEvidenceInput
from mip.contracts.common_intake import (
    CommonDataProfileSummary,
    GeoCoverageSummary,
    MediaCoverageSummary,
    MetricAvailabilitySummary,
    TimeCoverageSummary,
    WorkflowSupportRoute,
)
from mip.contracts.demo_profile import (
    MAX_DEMO_COLUMN_SAMPLE_VALUES,
    MAX_DEMO_PROFILE_ROWS,
    DemoColumnProfile,
    DemoColumnSemanticRole,
    DemoDatasetKind,
    DemoDatasetProfile,
    DemoProfileStatus,
    DemoProfileToWorkflowSummary,
)
from mip.contracts.intake import DataGrain, GeoGrain
from mip.contracts.intake_assets import DataAssetType

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

DEMO_DATASET_WEBSITE_TRAFFIC = "website_traffic"
DEMO_DATASET_NATIONAL_MEDIA_OUTCOME = "national_media_outcome"
DEMO_DATASET_DMA_WEEK = "dma_week_media_outcome"
DEMO_DATASET_EXPERIMENT_READOUT = "experiment_readout"
DEMO_DATASET_READOUT_MISSING_UNCERTAINTY = "readout_missing_uncertainty"

DEMO_DATASET_LABELS: dict[str, str] = {
    DEMO_DATASET_WEBSITE_TRAFFIC: "Website traffic (sessions, sources, conversions)",
    DEMO_DATASET_NATIONAL_MEDIA_OUTCOME: "National weekly media and outcome",
    DEMO_DATASET_DMA_WEEK: "DMA-week media and outcome",
    DEMO_DATASET_EXPERIMENT_READOUT: "Experiment readout with uncertainty",
    DEMO_DATASET_READOUT_MISSING_UNCERTAINTY: "Experiment readout missing uncertainty",
}

_ROLE_KEYWORDS: list[tuple[tuple[str, ...], DemoColumnSemanticRole]] = [
    (("standard_error", "std_error", "stderr"), DemoColumnSemanticRole.STANDARD_ERROR),
    (
        ("confidence_interval_low", "ci_low", "lower_bound", "lower"),
        DemoColumnSemanticRole.CONFIDENCE_INTERVAL_LOW,
    ),
    (
        ("confidence_interval_high", "ci_high", "upper_bound", "upper"),
        DemoColumnSemanticRole.CONFIDENCE_INTERVAL_HIGH,
    ),
    (("effect_estimate", "effect", "lift", "incremental"), DemoColumnSemanticRole.EFFECT_ESTIMATE),
    (("engaged_sessions", "engaged_visits"), DemoColumnSemanticRole.ENGAGED_SESSIONS),
    (("landing_page", "landingpage", "landing"), DemoColumnSemanticRole.LANDING_PAGE),
    (("time_window_start", "window_start", "start_date"), DemoColumnSemanticRole.DATE),
    (("time_window_end", "window_end", "end_date"), DemoColumnSemanticRole.DATE),
    (("week", "date", "day", "month", "period"), DemoColumnSemanticRole.DATE),
    (("dma", "state", "region", "country", "geo", "market"), DemoColumnSemanticRole.GEO),
    (("platform",), DemoColumnSemanticRole.CHANNEL),
    (("channel",), DemoColumnSemanticRole.CHANNEL),
    (("source",), DemoColumnSemanticRole.SOURCE),
    (("medium",), DemoColumnSemanticRole.MEDIUM),
    (("campaign",), DemoColumnSemanticRole.CAMPAIGN),
    (("device",), DemoColumnSemanticRole.DEVICE),
    (("sessions", "visits", "users"), DemoColumnSemanticRole.SESSIONS),
    (("conversions", "orders", "leads", "signups"), DemoColumnSemanticRole.CONVERSIONS),
    (("revenue", "sales", "arr"), DemoColumnSemanticRole.REVENUE),
    (("spend", "cost"), DemoColumnSemanticRole.SPEND),
    (("impressions",), DemoColumnSemanticRole.IMPRESSIONS),
    (("clicks",), DemoColumnSemanticRole.CLICKS),
    (("outcome",), DemoColumnSemanticRole.OUTCOME),
    (("metric",), DemoColumnSemanticRole.METRIC),
    (("estimand",), DemoColumnSemanticRole.ESTIMAND),
]


def infer_demo_column_role(column_name: str) -> DemoColumnSemanticRole:
    """Infer semantic role from column name using deterministic keyword matching."""
    normalized = column_name.strip().lower().replace("-", "_").replace(" ", "_")
    for keywords, role in _ROLE_KEYWORDS:
        if any(keyword in normalized for keyword in keywords):
            return role
    return DemoColumnSemanticRole.UNKNOWN


def _slug(value: object) -> str:
    return str(value).strip().lower()


def _dtype_summary(values: list[object]) -> str:
    non_null = [value for value in values if value is not None and str(value).strip() != ""]
    if not non_null:
        return "empty"
    types = {type(value).__name__ for value in non_null}
    if types == {"str"}:
        return "string"
    if types <= {"int", "float"}:
        return "numeric"
    if types == {"bool"}:
        return "boolean"
    if len(types) == 1:
        return next(iter(types))
    return "mixed"


def _cap_sample_values(values: list[object]) -> list[str]:
    seen: list[str] = []
    for value in values:
        if value is None:
            continue
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.append(text)
        if len(seen) >= MAX_DEMO_COLUMN_SAMPLE_VALUES:
            break
    return seen


def _column_values(rows: Sequence[Mapping[str, object]], column: str) -> list[object]:
    return [row.get(column) for row in rows]


def _distinct_non_null(values: list[object]) -> list[str]:
    distinct: list[str] = []
    for value in values:
        if value is None or str(value).strip() == "":
            continue
        text = str(value).strip()
        if text not in distinct:
            distinct.append(text)
    return distinct


def _parse_datetime(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.replace(tzinfo=UTC)
        except ValueError:
            continue
    return None


def _column_by_name(profile: DemoDatasetProfile, column_name: str) -> DemoColumnProfile | None:
    for column in profile.columns:
        if column.column_name == column_name:
            return column
    return None


def _sample_for_role(profile: DemoDatasetProfile, role: DemoColumnSemanticRole) -> str | None:
    for column in profile.columns:
        if column.semantic_role == role and column.sample_values:
            return column.sample_values[0]
    return None


def _sample_for_column(profile: DemoDatasetProfile, column_name: str) -> str | None:
    column = _column_by_name(profile, column_name)
    if column and column.sample_values:
        return column.sample_values[0]
    return None


def _float_value(value: object | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def build_demo_dataset_profile(
    rows: Sequence[Mapping[str, object]],
    dataset_kind: DemoDatasetKind,
    profile_id: str | None = None,
) -> DemoDatasetProfile:
    """Build a governed demo dataset profile from small in-memory rows."""
    resolved_id = profile_id or f"demo-profile-{uuid.uuid4().hex[:12]}"
    warnings: list[str] = []
    blocking_reasons: list[str] = []
    status = DemoProfileStatus.CREATED

    row_count = len(rows)
    if row_count == 0:
        blocking_reasons.append("demo_dataset_empty")
        status = DemoProfileStatus.BLOCKED
        return DemoDatasetProfile(
            profile_id=resolved_id,
            dataset_kind=dataset_kind,
            status=status,
            row_count=0,
            column_count=0,
            warnings=warnings,
            blocking_reasons=blocking_reasons,
            created_at=_NOW,
        )

    if row_count > MAX_DEMO_PROFILE_ROWS:
        blocking_reasons.append(
            f"demo_row_cap_exceeded:{MAX_DEMO_PROFILE_ROWS}:received={row_count}"
        )
        status = DemoProfileStatus.BLOCKED
        return DemoDatasetProfile(
            profile_id=resolved_id,
            dataset_kind=dataset_kind,
            status=status,
            row_count=0,
            column_count=0,
            warnings=warnings,
            blocking_reasons=blocking_reasons,
            created_at=_NOW,
        )

    column_names = list(rows[0].keys())
    if not column_names:
        blocking_reasons.append("demo_dataset_has_no_columns")
        status = DemoProfileStatus.UNSUPPORTED
        return DemoDatasetProfile(
            profile_id=resolved_id,
            dataset_kind=dataset_kind,
            status=status,
            row_count=row_count,
            column_count=0,
            warnings=warnings,
            blocking_reasons=blocking_reasons,
            created_at=_NOW,
        )

    columns: list[DemoColumnProfile] = []
    roles_present: set[DemoColumnSemanticRole] = set()
    for column_name in column_names:
        values = _column_values(rows, column_name)
        non_null = [value for value in values if value is not None and str(value).strip() != ""]
        null_count = row_count - len(non_null)
        role = infer_demo_column_role(column_name)
        roles_present.add(role)
        column_warnings: list[str] = []
        column_blocking: list[str] = []
        if role == DemoColumnSemanticRole.UNKNOWN:
            column_warnings.append("column_role_unknown")
        columns.append(
            DemoColumnProfile(
                column_name=column_name,
                semantic_role=role,
                dtype_summary=_dtype_summary(values),
                non_null_count=len(non_null),
                null_count=null_count,
                distinct_count=len(_distinct_non_null(values)),
                sample_values=_cap_sample_values(non_null),
                warnings=column_warnings,
                blocking_reasons=column_blocking,
            )
        )

    has_time_data = DemoColumnSemanticRole.DATE in roles_present
    has_geo_data = DemoColumnSemanticRole.GEO in roles_present
    has_media_data = bool(
        roles_present
        & {
            DemoColumnSemanticRole.SPEND,
            DemoColumnSemanticRole.IMPRESSIONS,
            DemoColumnSemanticRole.CLICKS,
            DemoColumnSemanticRole.CHANNEL,
        }
    )
    has_outcome_data = bool(
        roles_present
        & {
            DemoColumnSemanticRole.CONVERSIONS,
            DemoColumnSemanticRole.REVENUE,
            DemoColumnSemanticRole.OUTCOME,
            DemoColumnSemanticRole.SESSIONS,
        }
    )
    has_uncertainty_data = bool(
        roles_present
        & {
            DemoColumnSemanticRole.STANDARD_ERROR,
            DemoColumnSemanticRole.CONFIDENCE_INTERVAL_LOW,
            DemoColumnSemanticRole.CONFIDENCE_INTERVAL_HIGH,
        }
    )

    detected_sources = sorted(
        {
            str(value).strip()
            for column in columns
            if column.semantic_role == DemoColumnSemanticRole.SOURCE
            for value in _column_values(rows, column.column_name)
            if value is not None and str(value).strip()
        }
    )

    detected_channels = sorted(
        {
            str(value).strip()
            for column in columns
            if column.semantic_role == DemoColumnSemanticRole.CHANNEL
            for value in _column_values(rows, column.column_name)
            if value is not None and str(value).strip()
        }
    )

    detected_metrics = sorted(
        {
            str(value).strip()
            for column in columns
            if column.semantic_role == DemoColumnSemanticRole.METRIC
            for value in _column_values(rows, column.column_name)
            if value is not None and str(value).strip()
        }
    )

    date_values: list[datetime] = []
    for column in columns:
        if column.semantic_role != DemoColumnSemanticRole.DATE:
            continue
        for value in _column_values(rows, column.column_name):
            parsed = _parse_datetime(value)
            if parsed is not None:
                date_values.append(parsed)
    detected_time_coverage: str | None = None
    if date_values:
        date_values.sort()
        detected_time_coverage = (
            f"{len(_distinct_non_null(_column_values(rows, columns[0].column_name)))} "
            f"periods from {date_values[0].date()} to {date_values[-1].date()}"
        )
    elif has_time_data:
        detected_time_coverage = "time-like column detected; parse coverage incomplete"

    detected_geo_coverage: str | None = None
    if has_geo_data:
        geo_column = next(
            (
                column.column_name
                for column in columns
                if column.semantic_role == DemoColumnSemanticRole.GEO
            ),
            None,
        )
        if geo_column:
            geo_values = _distinct_non_null(_column_values(rows, geo_column))
            detected_geo_coverage = f"{len(geo_values)} geo units sampled"
        else:
            detected_geo_coverage = "geo column detected"

    if any(column.semantic_role == DemoColumnSemanticRole.UNKNOWN for column in columns):
        warnings.append("some_columns_need_semantic_mapping")
        if status == DemoProfileStatus.CREATED:
            status = DemoProfileStatus.NEEDS_MAPPING

    if dataset_kind == DemoDatasetKind.EXPERIMENT_READOUT:
        if DemoColumnSemanticRole.EFFECT_ESTIMATE in roles_present and not has_uncertainty_data:
            warnings.append("experiment_readout_missing_uncertainty")
            blocking_reasons.append("calibration_requires_uncertainty_fields")
            status = DemoProfileStatus.NEEDS_MAPPING

    if status == DemoProfileStatus.CREATED:
        status = DemoProfileStatus.PROFILED

    return DemoDatasetProfile(
        profile_id=resolved_id,
        dataset_kind=dataset_kind,
        status=status,
        row_count=row_count,
        column_count=len(columns),
        columns=columns,
        detected_time_coverage=detected_time_coverage,
        detected_geo_coverage=detected_geo_coverage,
        detected_channels=detected_channels,
        detected_sources=detected_sources,
        detected_metrics=detected_metrics,
        has_outcome_data=has_outcome_data,
        has_media_data=has_media_data,
        has_geo_data=has_geo_data,
        has_time_data=has_time_data,
        has_uncertainty_data=has_uncertainty_data,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        created_at=_NOW,
    )


def build_website_traffic_profile_from_demo_profile(
    profile: DemoDatasetProfile,
) -> WebsiteTrafficSourceProfile:
    """Build governed website traffic summary from a demo profile."""
    source_text = (
        f"Detected sources: {', '.join(profile.detected_sources)}"
        if profile.detected_sources
        else "No source column values summarized."
    )
    channel_text = (
        f"Detected channels: {', '.join(profile.detected_channels)}"
        if profile.detected_channels
        else "No channel column values summarized."
    )
    conversion_roles = {
        DemoColumnSemanticRole.CONVERSIONS,
        DemoColumnSemanticRole.REVENUE,
        DemoColumnSemanticRole.SESSIONS,
        DemoColumnSemanticRole.ENGAGED_SESSIONS,
    }
    conversion_columns = [
        column.column_name for column in profile.columns if column.semantic_role in conversion_roles
    ]
    conversion_text = (
        f"Outcome/session columns present: {', '.join(conversion_columns)}"
        if conversion_columns
        else "No conversion or session columns detected."
    )
    warnings = list(profile.warnings)
    blocking = list(profile.blocking_reasons)
    if profile.dataset_kind != DemoDatasetKind.WEBSITE_TRAFFIC:
        warnings.append("profile_not_website_traffic_kind")

    return WebsiteTrafficSourceProfile(
        traffic_profile_id=f"traffic-{profile.profile_id}",
        source_summary=source_text,
        channel_group_summary=channel_text,
        landing_page_summary=(
            "Landing-page column detected."
            if any(
                column.semantic_role == DemoColumnSemanticRole.LANDING_PAGE
                for column in profile.columns
            )
            else None
        ),
        device_summary=(
            "Device column detected."
            if any(
                column.semantic_role == DemoColumnSemanticRole.DEVICE for column in profile.columns
            )
            else None
        ),
        conversion_summary=conversion_text,
        utm_coverage_summary=(
            "Source and medium columns detected for UTM-like grouping."
            if any(
                column.semantic_role == DemoColumnSemanticRole.MEDIUM for column in profile.columns
            )
            else "Limited UTM-like coverage in demo profile."
        ),
        warnings=warnings,
        blocking_reasons=blocking,
        created_at=_NOW,
    )


def _asset_type_for_demo_kind(kind: DemoDatasetKind) -> DataAssetType:
    if kind == DemoDatasetKind.EXPERIMENT_READOUT:
        return DataAssetType.CALIBRATION_SIGNAL_DATA
    if kind == DemoDatasetKind.WEBSITE_TRAFFIC:
        return DataAssetType.OUTCOME_KPI_DATA
    return DataAssetType.OUTCOME_KPI_DATA


def _geo_grain_for_profile(profile: DemoDatasetProfile) -> GeoGrain:
    if profile.has_geo_data:
        return GeoGrain.DMA
    return GeoGrain.NATIONAL


def build_common_profile_summary_from_demo_profile(
    profile: DemoDatasetProfile,
) -> CommonDataProfileSummary:
    """Map demo profile flags into a governed CommonDataProfileSummary."""
    source_id = f"demo-source-{profile.profile_id}"
    asset_type = _asset_type_for_demo_kind(profile.dataset_kind)
    geo_grain = _geo_grain_for_profile(profile)

    geo_values: list[str] = []
    for column in profile.columns:
        if column.semantic_role == DemoColumnSemanticRole.GEO:
            geo_values = column.sample_values
            break

    metric_ids = list(profile.detected_metrics)
    if not metric_ids:
        metric_ids = [
            column.column_name
            for column in profile.columns
            if column.semantic_role
            in {
                DemoColumnSemanticRole.CONVERSIONS,
                DemoColumnSemanticRole.REVENUE,
                DemoColumnSemanticRole.SESSIONS,
                DemoColumnSemanticRole.OUTCOME,
            }
        ]

    time_min: datetime | None = None
    time_max: datetime | None = None
    for column in profile.columns:
        if column.semantic_role != DemoColumnSemanticRole.DATE:
            continue
        for sample in column.sample_values:
            parsed = _parse_datetime(sample)
            if parsed is None:
                continue
            time_min = parsed if time_min is None else min(time_min, parsed)
            time_max = parsed if time_max is None else max(time_max, parsed)

    media_channels = profile.detected_channels
    spend_present = any(
        column.semantic_role == DemoColumnSemanticRole.SPEND for column in profile.columns
    )
    impressions_present = any(
        column.semantic_role == DemoColumnSemanticRole.IMPRESSIONS for column in profile.columns
    )
    clicks_present = any(
        column.semantic_role == DemoColumnSemanticRole.CLICKS for column in profile.columns
    )

    return CommonDataProfileSummary(
        profile_id=f"common-{profile.profile_id}",
        snapshot_id=f"snapshot-{profile.profile_id}",
        source_id=source_id,
        asset_type=asset_type,
        metric_availability=MetricAvailabilitySummary(
            summary_id=f"metric-{profile.profile_id}",
            source_id=source_id,
            metric_ids=metric_ids,
            primary_metric_candidates=metric_ids[:3],
            missing_metric_ids=[],
            warnings=[],
            blocking_reasons=[],
        )
        if metric_ids or profile.has_outcome_data
        else None,
        geo_coverage=GeoCoverageSummary(
            summary_id=f"geo-{profile.profile_id}",
            source_id=source_id,
            geo_grain=geo_grain,
            geo_count=len(geo_values)
            if geo_values
            else (1 if geo_grain == GeoGrain.NATIONAL else None),
            geo_values_sample=geo_values,
            warnings=[],
            blocking_reasons=[],
        )
        if profile.has_geo_data or geo_grain == GeoGrain.NATIONAL
        else None,
        time_coverage=TimeCoverageSummary(
            summary_id=f"time-{profile.profile_id}",
            source_id=source_id,
            time_grain=DataGrain.WEEKLY
            if "week" in (profile.detected_time_coverage or "").lower()
            else DataGrain.DAILY,
            period_count=profile.row_count,
            time_min=time_min,
            time_max=time_max,
            warnings=[],
            blocking_reasons=[],
        )
        if profile.has_time_data
        else None,
        media_coverage=MediaCoverageSummary(
            summary_id=f"media-{profile.profile_id}",
            source_id=source_id,
            channels=media_channels,
            spend_present=spend_present,
            impressions_present=impressions_present,
            clicks_present=clicks_present,
            warnings=[],
            blocking_reasons=[],
        )
        if profile.has_media_data
        else None,
        warnings=list(profile.warnings),
        blocking_reasons=list(profile.blocking_reasons),
        created_at=_NOW,
    )


def build_calibration_evidence_input_from_demo_profile(
    profile: DemoDatasetProfile,
) -> CalibrationEvidenceInput | None:
    """Build CalibrationEvidenceInput when required readout fields are present."""
    if profile.dataset_kind != DemoDatasetKind.EXPERIMENT_READOUT:
        return None
    if profile.status == DemoProfileStatus.BLOCKED:
        return None

    effect = _float_value(_sample_for_role(profile, DemoColumnSemanticRole.EFFECT_ESTIMATE))
    standard_error = _float_value(_sample_for_role(profile, DemoColumnSemanticRole.STANDARD_ERROR))
    metric = _sample_for_role(profile, DemoColumnSemanticRole.METRIC)
    estimand = _sample_for_role(profile, DemoColumnSemanticRole.ESTIMAND)
    channel = _sample_for_column(profile, "channel") or _sample_for_role(
        profile, DemoColumnSemanticRole.CHANNEL
    )
    platform = _sample_for_column(profile, "platform")
    geo_scope = _sample_for_column(profile, "geo_scope") or _sample_for_role(
        profile, DemoColumnSemanticRole.GEO
    )
    time_start = _parse_datetime(_sample_for_column(profile, "time_window_start"))
    time_end = _parse_datetime(_sample_for_column(profile, "time_window_end"))
    ci_low = _float_value(_sample_for_role(profile, DemoColumnSemanticRole.CONFIDENCE_INTERVAL_LOW))
    ci_high = _float_value(
        _sample_for_role(profile, DemoColumnSemanticRole.CONFIDENCE_INTERVAL_HIGH)
    )

    warnings: list[str] = []
    blocking: list[str] = []
    if effect is None:
        blocking.append("missing_effect_estimate")
    if metric is None:
        blocking.append("missing_metric")
    if estimand is None:
        blocking.append("missing_estimand")
    if time_start is None or time_end is None:
        blocking.append("missing_time_window")
    if standard_error is None and ci_low is None and ci_high is None:
        blocking.append("missing_uncertainty")

    if blocking:
        return CalibrationEvidenceInput(
            input_id=f"calib-in-{profile.profile_id}",
            source_readout_id=profile.profile_id,
            metric_id=metric,
            estimand_id=estimand,
            channel=channel,
            platform=platform,
            geo_scope=geo_scope,
            time_window_start=time_start,
            time_window_end=time_end,
            effect_estimate=effect,
            standard_error=standard_error,
            confidence_interval_low=ci_low,
            confidence_interval_high=ci_high,
            evidence_type="experiment_readout_demo",
            warnings=warnings,
            blocking_reasons=blocking,
            created_at=_NOW,
        )

    return CalibrationEvidenceInput(
        input_id=f"calib-in-{profile.profile_id}",
        source_readout_id=profile.profile_id,
        metric_id=metric,
        estimand_id=estimand,
        channel=channel,
        platform=platform,
        geo_scope=geo_scope,
        time_window_start=time_start,
        time_window_end=time_end,
        effect_estimate=effect,
        standard_error=standard_error,
        confidence_interval_low=ci_low,
        confidence_interval_high=ci_high,
        evidence_type="experiment_readout_demo",
        warnings=warnings,
        blocking_reasons=[],
        created_at=_NOW,
    )


def build_demo_profile_to_workflow_summary(
    profile: DemoDatasetProfile,
) -> DemoProfileToWorkflowSummary:
    """Link demo profile to governed workflow objects and route hints."""
    supported: list[WorkflowSupportRoute] = []
    blocked: list[WorkflowSupportRoute] = []
    warnings = list(profile.warnings)
    blocking = list(profile.blocking_reasons)

    common_summary: CommonDataProfileSummary | None = None
    traffic_profile: WebsiteTrafficSourceProfile | None = None
    calibration_input: CalibrationEvidenceInput | None = None

    if profile.status not in {DemoProfileStatus.BLOCKED, DemoProfileStatus.UNSUPPORTED}:
        common_summary = build_common_profile_summary_from_demo_profile(profile)

    if (
        profile.dataset_kind == DemoDatasetKind.WEBSITE_TRAFFIC
        and profile.status == DemoProfileStatus.PROFILED
    ):
        traffic_profile = build_website_traffic_profile_from_demo_profile(profile)
        blocked.extend(
            [
                WorkflowSupportRoute.NATIONAL_MMM,
                WorkflowSupportRoute.GEO_LEVEL_MMM,
                WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS,
            ]
        )
        warnings.append("website_traffic_demo_supports_advisory_not_mmm_execution")

    if profile.dataset_kind in {
        DemoDatasetKind.MEDIA_SPEND,
        DemoDatasetKind.GEO_OUTCOME,
        DemoDatasetKind.UNKNOWN,
    }:
        if (
            profile.has_time_data
            and profile.has_media_data
            and profile.has_outcome_data
            and not profile.has_geo_data
        ):
            supported.append(WorkflowSupportRoute.NATIONAL_MMM)
            blocked.extend(
                [
                    WorkflowSupportRoute.GEO_LEVEL_MMM,
                    WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS,
                    WorkflowSupportRoute.GEOX_READOUT,
                ]
            )
            warnings.append("national_demo_profile_missing_mapping_assets_for_full_readiness")

        if (
            profile.has_geo_data
            and profile.has_time_data
            and profile.has_media_data
            and profile.has_outcome_data
        ):
            supported.extend(
                [
                    WorkflowSupportRoute.GEO_LEVEL_MMM,
                    WorkflowSupportRoute.GEOX_DESIGN_DIAGNOSTICS,
                ]
            )
            blocked.append(WorkflowSupportRoute.NATIONAL_MMM)
            warnings.append("dma_demo_profile_missing_mapping_assets_for_full_readiness")

    if profile.dataset_kind == DemoDatasetKind.EXPERIMENT_READOUT:
        calibration_input = build_calibration_evidence_input_from_demo_profile(profile)
        if calibration_input and not calibration_input.blocking_reasons:
            supported.append(WorkflowSupportRoute.CALIBRATION_SIGNAL_INTAKE)
        else:
            blocked.append(WorkflowSupportRoute.CALIBRATION_SIGNAL_INTAKE)
            if calibration_input and calibration_input.blocking_reasons:
                blocking.extend(calibration_input.blocking_reasons)

    return DemoProfileToWorkflowSummary(
        summary_id=f"demo-wf-{profile.profile_id}",
        profile_id=profile.profile_id,
        dataset_kind=profile.dataset_kind,
        common_profile_summary_id=common_summary.profile_id if common_summary else None,
        traffic_profile_id=traffic_profile.traffic_profile_id if traffic_profile else None,
        calibration_evidence_input_id=calibration_input.input_id if calibration_input else None,
        supported_workflow_routes=supported,
        blocked_workflow_routes=blocked,
        warnings=warnings,
        blocking_reasons=blocking,
        created_at=_NOW,
    )


def website_traffic_demo_rows() -> list[dict[str, object]]:
    """Synthetic website traffic rows for local demo profiling."""
    sources = ["organic", "search", "social", "email", "direct", "referral"]
    rows: list[dict[str, object]] = []
    for week in range(1, 9):
        for idx, source in enumerate(sources):
            rows.append(
                {
                    "date": f"2025-01-{week + idx:02d}",
                    "source": source,
                    "medium": "cpc" if source == "search" else "organic",
                    "channel": "paid_search" if source == "search" else source,
                    "landing_page": f"/landing/{source}",
                    "device": "mobile" if idx % 2 == 0 else "desktop",
                    "sessions": 100 + week * 10 + idx,
                    "engaged_sessions": 60 + week * 5 + idx,
                    "conversions": 5 + week + (idx % 3),
                    "revenue": 250.0 + week * 20 + idx * 10,
                }
            )
    return rows


def national_media_outcome_demo_rows() -> list[dict[str, object]]:
    """Synthetic national weekly media/outcome rows."""
    channels = ["search", "social", "display", "video"]
    rows: list[dict[str, object]] = []
    for week in range(1, 13):
        for channel in channels:
            rows.append(
                {
                    "week": f"2025-W{week:02d}",
                    "channel": channel,
                    "spend": 1000.0 + week * 50,
                    "impressions": 50000 + week * 1000,
                    "clicks": 1200 + week * 20,
                    "conversions": 80 + week,
                    "revenue": 4000.0 + week * 100,
                }
            )
    return rows


def dma_week_media_outcome_demo_rows() -> list[dict[str, object]]:
    """Synthetic DMA-week media/outcome rows."""
    dmas = ["NYC", "LA", "CHI", "DFW", "ATL"]
    channels = ["search", "social", "tv"]
    rows: list[dict[str, object]] = []
    for week in range(1, 9):
        for dma in dmas:
            for channel in channels:
                rows.append(
                    {
                        "week": f"2025-W{week:02d}",
                        "dma": dma,
                        "channel": channel,
                        "spend": 500.0 + week * 25,
                        "conversions": 20 + week,
                        "revenue": 900.0 + week * 40,
                    }
                )
    return rows


def experiment_readout_demo_rows() -> list[dict[str, object]]:
    """Synthetic experiment readout with uncertainty fields."""
    return [
        {
            "metric": "weekly_orders",
            "estimand": "attributed_incremental_orders",
            "effect_estimate": 0.12,
            "standard_error": 0.03,
            "confidence_interval_low": 0.06,
            "confidence_interval_high": 0.18,
            "geo_scope": "US-national",
            "time_window_start": "2025-01-01",
            "time_window_end": "2025-03-31",
            "channel": "paid_search",
            "platform": "google_ads",
        }
    ]


def experiment_readout_missing_uncertainty_demo_rows() -> list[dict[str, object]]:
    """Synthetic experiment readout missing uncertainty fields."""
    return [
        {
            "metric": "weekly_orders",
            "estimand": "attributed_incremental_orders",
            "effect_estimate": 0.12,
            "geo_scope": "US-national",
            "time_window_start": "2025-01-01",
            "time_window_end": "2025-03-31",
            "channel": "paid_search",
            "platform": "google_ads",
        }
    ]


_DEMO_KIND_BY_KEY: dict[str, DemoDatasetKind] = {
    DEMO_DATASET_WEBSITE_TRAFFIC: DemoDatasetKind.WEBSITE_TRAFFIC,
    DEMO_DATASET_NATIONAL_MEDIA_OUTCOME: DemoDatasetKind.MEDIA_SPEND,
    DEMO_DATASET_DMA_WEEK: DemoDatasetKind.GEO_OUTCOME,
    DEMO_DATASET_EXPERIMENT_READOUT: DemoDatasetKind.EXPERIMENT_READOUT,
    DEMO_DATASET_READOUT_MISSING_UNCERTAINTY: DemoDatasetKind.EXPERIMENT_READOUT,
}


def demo_rows_for_key(dataset_key: str) -> list[dict[str, object]]:
    """Return in-memory demo rows for a known dataset key."""
    builders: dict[str, Callable[[], list[dict[str, object]]]] = {
        DEMO_DATASET_WEBSITE_TRAFFIC: website_traffic_demo_rows,
        DEMO_DATASET_NATIONAL_MEDIA_OUTCOME: national_media_outcome_demo_rows,
        DEMO_DATASET_DMA_WEEK: dma_week_media_outcome_demo_rows,
        DEMO_DATASET_EXPERIMENT_READOUT: experiment_readout_demo_rows,
        DEMO_DATASET_READOUT_MISSING_UNCERTAINTY: experiment_readout_missing_uncertainty_demo_rows,
    }
    builder = builders.get(dataset_key)
    if builder is None:
        msg = f"unknown demo dataset key: {dataset_key}"
        raise KeyError(msg)
    return builder()


def build_demo_dataset_profile_for_key(dataset_key: str) -> DemoDatasetProfile:
    """Build a demo dataset profile for a known fixture key."""
    kind = _DEMO_KIND_BY_KEY[dataset_key]
    return build_demo_dataset_profile(demo_rows_for_key(dataset_key), kind)


def demo_profiling_sample_labels() -> dict[str, str]:
    """Human-readable labels for demo profiling dataset keys."""
    return dict(DEMO_DATASET_LABELS)
