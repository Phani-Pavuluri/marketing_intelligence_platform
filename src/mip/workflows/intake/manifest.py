"""Deterministic intake manifest assembly (P3 / I5)."""

from collections.abc import Sequence
from typing import Any

from mip.contracts.intake import (
    IntakePathRecommendation,
    IntakeRecommendationStatus,
    MeasurementIntakeSession,
    MeasurementWorkflowKind,
)
from mip.contracts.intake_assets import DataAssetType, IntakePlan
from mip.contracts.intake_sources import (
    DataSourceRef,
    GeoXIntakeManifest,
    IntakeManifestStatus,
    MMMIntakeManifest,
)

_MEDIA_ASSET_TYPES = frozenset(
    {
        DataAssetType.MEDIA_SPEND_DATA,
        DataAssetType.MEDIA_EXPOSURE_DATA,
        "media_spend_data",
        "media_exposure_data",
    }
)
_CONTROL_ASSET_TYPES = frozenset(
    {
        DataAssetType.CONTROL_DATA,
        DataAssetType.CALENDAR_SEASONALITY_DATA,
        DataAssetType.PRICING_PROMO_DATA,
        "control_data",
        "calendar_seasonality_data",
        "pricing_promo_data",
    }
)
_MAPPING_ASSET_TYPES = frozenset(
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
_CALIBRATION_ASSET_TYPES = frozenset(
    {
        DataAssetType.CALIBRATION_SIGNAL_DATA,
        "calibration_signal_data",
    }
)
_EXPERIMENT_ASSET_TYPES = frozenset(
    {
        DataAssetType.EXPERIMENT_EXPORT_DATA,
        "experiment_export_data",
    }
)
_OUTCOME_ASSET_TYPES = frozenset(
    {
        DataAssetType.OUTCOME_KPI_DATA,
        "outcome_kpi_data",
    }
)
_GEO_MAPPING_ASSET_TYPES = frozenset(
    {
        DataAssetType.GEO_MAPPING,
        "geo_mapping",
    }
)
_BLOCKED_PATHS = frozenset(
    {
        "blocked_needs_more_data",
    }
)


def _asset_slug(asset_type: object) -> str:
    if isinstance(asset_type, DataAssetType):
        return asset_type.value
    return str(asset_type)


def _required_asset_types(plan: IntakePlan) -> set[str]:
    return {_asset_slug(asset.asset_type) for asset in plan.required_assets}


def _provided_asset_types(data_sources: Sequence[DataSourceRef]) -> set[str]:
    return {_asset_slug(source.asset_type) for source in data_sources}


def _is_blocked(recommendation: IntakePathRecommendation, plan: IntakePlan) -> bool:
    if recommendation.status in {
        IntakeRecommendationStatus.BLOCKED,
        IntakeRecommendationStatus.NEEDS_CLARIFICATION,
        "blocked",
        "needs_clarification",
    }:
        return True
    if plan.blocking_reasons and not plan.required_assets:
        return True
    path = recommendation.recommended_path
    path_slug = path.value if hasattr(path, "value") else str(path)
    return path_slug in _BLOCKED_PATHS


def _manifest_status(
    *,
    blocked: bool,
    missing_required: set[str],
    data_sources: Sequence[DataSourceRef],
) -> IntakeManifestStatus:
    if blocked:
        return IntakeManifestStatus.BLOCKED
    if missing_required:
        return IntakeManifestStatus.NEEDS_DATA_SOURCES
    if data_sources:
        return IntakeManifestStatus.READY_FOR_VALIDATION
    return IntakeManifestStatus.DRAFT


def _missing_source_warnings(missing_required: set[str]) -> list[str]:
    return [
        f"Missing data source for required asset type: {asset_type}"
        for asset_type in sorted(missing_required)
    ]


def _base_manifest_fields(
    session: MeasurementIntakeSession,
    recommendation: IntakePathRecommendation,
    plan: IntakePlan,
) -> dict[str, Any]:
    return {
        "manifest_id": f"{session.session_id}-manifest",
        "session_id": session.session_id,
        "recommendation_id": recommendation.recommendation_id,
        "plan_id": plan.plan_id,
        "business_question": session.business_question,
        "intended_use": session.intended_use,
        "recommended_path": recommendation.recommended_path,
        "metric_id": session.metric_id,
        "estimand_id": session.estimand_id,
        "time_grain": session.time_grain,
        "geo_grain": session.geo_grain,
        "reporting_window_start": session.reporting_window_start,
        "reporting_window_end": session.reporting_window_end,
        "created_by": session.created_by,
        "created_at": session.created_at,
    }


def _bucket_mmm_sources(
    data_sources: Sequence[DataSourceRef],
) -> dict[str, Any]:
    outcome_source: DataSourceRef | None = None
    media_sources: list[DataSourceRef] = []
    control_sources: list[DataSourceRef] = []
    mapping_sources: list[DataSourceRef] = []
    calibration_signal_sources: list[DataSourceRef] = []
    experiment_export_sources: list[DataSourceRef] = []

    for source in data_sources:
        asset_type = _asset_slug(source.asset_type)
        if asset_type in _OUTCOME_ASSET_TYPES:
            if outcome_source is None:
                outcome_source = source
            continue
        if asset_type in _MEDIA_ASSET_TYPES:
            media_sources.append(source)
            continue
        if asset_type in _CONTROL_ASSET_TYPES:
            control_sources.append(source)
            continue
        if asset_type in _MAPPING_ASSET_TYPES:
            mapping_sources.append(source)
            continue
        if asset_type in _CALIBRATION_ASSET_TYPES:
            calibration_signal_sources.append(source)
            continue
        if asset_type in _EXPERIMENT_ASSET_TYPES:
            experiment_export_sources.append(source)

    return {
        "outcome_source": outcome_source,
        "media_sources": media_sources,
        "control_sources": control_sources,
        "mapping_sources": mapping_sources,
        "calibration_signal_sources": calibration_signal_sources,
        "experiment_export_sources": experiment_export_sources,
    }


def _bucket_geox_sources(
    data_sources: Sequence[DataSourceRef],
) -> dict[str, Any]:
    outcome_source: DataSourceRef | None = None
    geo_mapping_source: DataSourceRef | None = None
    media_sources: list[DataSourceRef] = []
    experiment_export_sources: list[DataSourceRef] = []

    for source in data_sources:
        asset_type = _asset_slug(source.asset_type)
        if asset_type in _OUTCOME_ASSET_TYPES:
            if outcome_source is None:
                outcome_source = source
            continue
        if asset_type in _GEO_MAPPING_ASSET_TYPES:
            if geo_mapping_source is None:
                geo_mapping_source = source
            continue
        if asset_type in _MEDIA_ASSET_TYPES:
            media_sources.append(source)
            continue
        if asset_type in _EXPERIMENT_ASSET_TYPES:
            experiment_export_sources.append(source)

    return {
        "outcome_source": outcome_source,
        "geo_mapping_source": geo_mapping_source,
        "media_sources": media_sources,
        "experiment_export_sources": experiment_export_sources,
    }


def build_intake_manifest(
    session: MeasurementIntakeSession,
    recommendation: IntakePathRecommendation,
    plan: IntakePlan,
    data_sources: Sequence[DataSourceRef],
) -> MMMIntakeManifest | GeoXIntakeManifest:
    """Build a workflow-specific intake manifest from session, plan, and sources."""

    blocked = _is_blocked(recommendation, plan)
    required_types = _required_asset_types(plan)
    provided_types = _provided_asset_types(data_sources)
    missing_required = required_types - provided_types if not blocked else set()

    warnings = list(plan.warnings)
    blocking_reasons = list(plan.blocking_reasons) or list(recommendation.blocking_reasons)
    if missing_required:
        warnings.extend(_missing_source_warnings(missing_required))

    status = _manifest_status(
        blocked=blocked,
        missing_required=missing_required,
        data_sources=data_sources,
    )

    base = _base_manifest_fields(session, recommendation, plan)
    manifest_kwargs: dict[str, Any] = {
        **base,
        "status": status,
        "warnings": warnings,
        "blocking_reasons": blocking_reasons if blocked else [],
    }

    workflow_kind = session.workflow_kind
    workflow_slug = (
        workflow_kind.value if hasattr(workflow_kind, "value") else str(workflow_kind)
    )

    if workflow_slug == MeasurementWorkflowKind.GEOX.value:
        return GeoXIntakeManifest(
            **_bucket_geox_sources(data_sources),
            **manifest_kwargs,
        )

    return MMMIntakeManifest(
        **_bucket_mmm_sources(data_sources),
        **manifest_kwargs,
    )
