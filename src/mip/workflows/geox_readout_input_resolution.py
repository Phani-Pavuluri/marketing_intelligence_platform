"""Deterministic GeoX readout input resolution (Stage 2A — no file parsing, no panel_exp)."""

from __future__ import annotations

from mip.contracts.geox_readout_input_resolution import (
    AssignmentColumnMapping,
    DatasetReference,
    DatasetSemanticType,
    GeoXExperimentMetadataRef,
    GeoXMissingInputReason,
    GeoXReadoutInputHandoff,
    GeoXReadoutInputResolutionRequest,
    GeoXReadoutInputResolutionResult,
    GeoXReadoutIntent,
    GeoXReadoutResolutionStatus,
    KPIColumnMapping,
    MappingConfirmationStatus,
    SpendColumnMapping,
    ValueMapping,
)

MSG_MISSING_KPI = (
    "Please provide the post-test KPI panel or a data-source reference with "
    "geo/unit, date/week, and KPI columns."
)
MSG_MISSING_SPEND_FOR_EFFICIENCY = (
    "I can run increment/lift readout with KPI data, but cost-per/ROI/ROAS "
    "requires post-test spend data or a spend-source reference aligned to the "
    "experiment geos and test window."
)
MSG_MISSING_VALUE_MAPPING = (
    "I can compute incremental KPI and spend efficiency if spend is provided, "
    "but ROAS/profit ROI requires revenue/value or margin mapping."
)
MSG_MISSING_ASSIGNMENT = (
    "Please provide the treatment/control/cell assignment or the experiment "
    "design artifact used for this test."
)
MSG_MISSING_DATES = (
    "Please provide test start/end dates and the post-period window for readout."
)
MSG_MAPPING_CONFIRMATION = (
    "I inferred the likely geo/date/KPI/spend column mappings. Please confirm "
    "these mappings before I prepare the GeoX handoff."
)
MSG_DECISION_RECOMMENDATION = (
    "Budget reallocation and production spend decisions require a governed "
    "recommendation path. I can help with GeoX readout metrics first, then "
    "route certified outputs through decision review."
)
MSG_RUNTIME_UNAVAILABLE = (
    "GeoX readout inputs are ready, but panel_exp runtime is not available yet."
)
MSG_UNCLEAR_INTENT = (
    "Please clarify whether you need incremental lift only, cost-per "
    "efficiency, ROAS, or profit ROI so I can request the right datasets."
)
MSG_PARTIAL_READOUT = (
    "KPI/lift readout can proceed, but efficiency metrics are blocked until "
    "missing inputs are resolved."
)

_EFFICIENCY_INTENTS = frozenset(
    {
        GeoXReadoutIntent.READOUT_WITH_COST_PER,
        GeoXReadoutIntent.READOUT_WITH_ROAS,
        GeoXReadoutIntent.READOUT_WITH_PROFIT_ROI,
    }
)

_METRIC_INTENT_MAP: dict[str, GeoXReadoutIntent] = {
    "kpi": GeoXReadoutIntent.READOUT_KPI_ONLY,
    "kpi_only": GeoXReadoutIntent.READOUT_KPI_ONLY,
    "lift": GeoXReadoutIntent.READOUT_WITH_LIFT,
    "incremental_lift": GeoXReadoutIntent.READOUT_WITH_LIFT,
    "increment": GeoXReadoutIntent.READOUT_WITH_LIFT,
    "cost_per": GeoXReadoutIntent.READOUT_WITH_COST_PER,
    "cpa": GeoXReadoutIntent.READOUT_WITH_COST_PER,
    "media_efficiency": GeoXReadoutIntent.READOUT_WITH_COST_PER,
    "roas": GeoXReadoutIntent.READOUT_WITH_ROAS,
    "profit_roi": GeoXReadoutIntent.READOUT_WITH_PROFIT_ROI,
    "profit": GeoXReadoutIntent.READOUT_WITH_PROFIT_ROI,
    "roi": GeoXReadoutIntent.READOUT_WITH_COST_PER,
    "decision_recommendation": (
        GeoXReadoutIntent.READOUT_WITH_DECISION_RECOMMENDATION_REQUEST
    ),
    "budget_reallocation": (
        GeoXReadoutIntent.READOUT_WITH_DECISION_RECOMMENDATION_REQUEST
    ),
}

_CONFIRMATION_BLOCKING = frozenset(
    {
        MappingConfirmationStatus.CONFIRMATION_REQUIRED,
        MappingConfirmationStatus.AMBIGUOUS,
    }
)


def resolve_geox_readout_inputs(
    request: GeoXReadoutInputResolutionRequest,
) -> GeoXReadoutInputResolutionResult:
    """Resolve declared GeoX readout inputs into status, messages, and handoff."""
    intent = _resolve_intent(request)
    missing: list[GeoXMissingInputReason] = []
    warnings = list(request.warnings)

    if intent == GeoXReadoutIntent.READOUT_UNCLEAR_METRIC_REQUEST:
        missing.append(GeoXMissingInputReason.UNCLEAR_USER_INTENT)
        return _result(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_UNCLEAR_USER_INTENT,
            missing,
            [MSG_UNCLEAR_INTENT],
            warnings,
        )

    if intent == GeoXReadoutIntent.READOUT_WITH_DECISION_RECOMMENDATION_REQUEST:
        missing.append(
            GeoXMissingInputReason.DECISION_RECOMMENDATION_REQUIRES_DECISION_SURFACE
        )
        return _result(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_DECISION_RECOMMENDATION_REQUIRES_DECISION_SURFACE,
            missing,
            [MSG_DECISION_RECOMMENDATION],
            warnings,
        )

    if _mapping_confirmation_required(request):
        missing.append(GeoXMissingInputReason.MAPPING_CONFIRMATION_REQUIRED)
        handoff = _build_handoff(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_MAPPING_CONFIRMATION_REQUIRED,
            missing,
            warnings,
        )
        return _result(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_MAPPING_CONFIRMATION_REQUIRED,
            missing,
            [MSG_MAPPING_CONFIRMATION],
            warnings,
            mapping_confirmation_required=True,
            handoff=handoff,
        )

    datasets = _inventory_datasets(request.dataset_refs)
    kpi_ref = datasets.get(DatasetSemanticType.KPI_PANEL)
    spend_ref = datasets.get(DatasetSemanticType.SPEND_PANEL)

    if kpi_ref is None:
        missing.append(GeoXMissingInputReason.MISSING_KPI_DATA)
        return _blocked(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_MISSING_KPI_DATA,
            missing,
            [MSG_MISSING_KPI],
            warnings,
        )

    metadata = request.experiment_metadata
    if metadata is None or not metadata.experiment_id.strip():
        missing.append(GeoXMissingInputReason.MISSING_EXPERIMENT_METADATA)
        return _blocked(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_MISSING_EXPERIMENT_METADATA,
            missing,
            ["Experiment metadata is required for GeoX readout."],
            warnings,
        )

    if not _has_assignment(request, datasets):
        missing.append(GeoXMissingInputReason.MISSING_ASSIGNMENT)
        return _blocked(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_MISSING_ASSIGNMENT,
            missing,
            [MSG_MISSING_ASSIGNMENT],
            warnings,
        )

    if not _has_dates(metadata):
        missing.append(GeoXMissingInputReason.MISSING_DATES)
        return _blocked(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_MISSING_DATES,
            missing,
            [MSG_MISSING_DATES],
            warnings,
        )

    kpi_mapping_ok = _kpi_mapping_complete(request.kpi_column_mapping)
    if not kpi_mapping_ok:
        missing.append(GeoXMissingInputReason.MISSING_KPI_DATA)
        return _blocked(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_MISSING_KPI_DATA,
            missing,
            [MSG_MISSING_KPI],
            warnings,
        )

    spend_required = intent in _EFFICIENCY_INTENTS
    spend_present = spend_ref is not None
    spend_mapping_ok = _spend_mapping_complete(request.spend_column_mapping)

    if spend_required and not spend_present:
        missing.append(GeoXMissingInputReason.MISSING_SPEND_FOR_EFFICIENCY)
        if _can_partial_readout(intent):
            handoff = _build_handoff(
                request,
                intent,
                GeoXReadoutResolutionStatus.PARTIAL_READOUT_ALLOWED,
                missing,
                warnings,
                kpi_ref=kpi_ref,
                spend_ref=None,
            )
            return _result(
                request,
                intent,
                GeoXReadoutResolutionStatus.PARTIAL_READOUT_ALLOWED,
                missing,
                [MSG_MISSING_SPEND_FOR_EFFICIENCY, MSG_PARTIAL_READOUT],
                warnings,
                handoff=handoff,
            )
        return _blocked(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_MISSING_SPEND_FOR_EFFICIENCY,
            missing,
            [MSG_MISSING_SPEND_FOR_EFFICIENCY],
            warnings,
        )

    if spend_required and spend_present and not spend_mapping_ok:
        missing.append(GeoXMissingInputReason.MISSING_SPEND_FOR_EFFICIENCY)
        return _blocked(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_MISSING_SPEND_FOR_EFFICIENCY,
            missing,
            ["Spend dataset is present but spend column mapping is incomplete."],
            warnings,
        )

    value_missing = _missing_value_mapping(request, intent)
    if value_missing == GeoXMissingInputReason.MISSING_VALUE_MAPPING_FOR_ROAS:
        missing.append(value_missing)
        status = GeoXReadoutResolutionStatus.BLOCKED_MISSING_VALUE_MAPPING_FOR_ROAS
        handoff = _build_handoff(
            request,
            intent,
            status,
            missing,
            warnings,
            kpi_ref=kpi_ref,
            spend_ref=spend_ref,
        )
        return _result(
            request,
            intent,
            status,
            missing,
            [MSG_MISSING_VALUE_MAPPING],
            warnings,
            handoff=handoff,
        )

    if value_missing == GeoXMissingInputReason.MISSING_MARGIN_MAPPING_FOR_PROFIT_ROI:
        missing.append(value_missing)
        status = GeoXReadoutResolutionStatus.BLOCKED_MISSING_MARGIN_MAPPING_FOR_PROFIT_ROI
        handoff = _build_handoff(
            request,
            intent,
            status,
            missing,
            warnings,
            kpi_ref=kpi_ref,
            spend_ref=spend_ref,
        )
        return _result(
            request,
            intent,
            status,
            missing,
            [MSG_MISSING_VALUE_MAPPING],
            warnings,
            handoff=handoff,
        )

    ready_status = _ready_status(intent, spend_present)
    handoff = _build_handoff(
        request,
        intent,
        ready_status,
        missing,
        warnings,
        kpi_ref=kpi_ref,
        spend_ref=spend_ref if spend_present else None,
    )

    if not request.geox_runtime_available:
        missing.append(GeoXMissingInputReason.NO_GEOX_RUNTIME_AVAILABLE)
        return _result(
            request,
            intent,
            GeoXReadoutResolutionStatus.BLOCKED_NO_GEOX_RUNTIME_AVAILABLE,
            missing,
            [MSG_RUNTIME_UNAVAILABLE],
            warnings,
            handoff=handoff,
        )

    return _result(
        request,
        intent,
        ready_status,
        missing,
        [],
        warnings,
        handoff=handoff,
    )


def _resolve_intent(request: GeoXReadoutInputResolutionRequest) -> GeoXReadoutIntent:
    if request.requested_intent is not None:
        return request.requested_intent
    if not request.requested_metrics:
        return GeoXReadoutIntent.READOUT_UNCLEAR_METRIC_REQUEST
    normalized = [metric.strip().lower() for metric in request.requested_metrics if metric.strip()]
    if not normalized:
        return GeoXReadoutIntent.READOUT_UNCLEAR_METRIC_REQUEST
    for metric in normalized:
        if metric in _METRIC_INTENT_MAP:
            return _METRIC_INTENT_MAP[metric]
    return GeoXReadoutIntent.READOUT_UNCLEAR_METRIC_REQUEST


def _inventory_datasets(
    dataset_refs: list[DatasetReference],
) -> dict[DatasetSemanticType, DatasetReference]:
    inventory: dict[DatasetSemanticType, DatasetReference] = {}
    for ref in dataset_refs:
        if ref.semantic_type not in inventory:
            inventory[ref.semantic_type] = ref
    return inventory


def _mapping_confirmation_required(request: GeoXReadoutInputResolutionRequest) -> bool:
    mappings = (
        request.kpi_column_mapping,
        request.spend_column_mapping,
        request.assignment_column_mapping,
        request.value_mapping,
    )
    for mapping in mappings:
        if mapping is not None and _object_needs_confirmation(mapping):
            return True
    return False


def _object_needs_confirmation(
    mapping: KPIColumnMapping | SpendColumnMapping | AssignmentColumnMapping | ValueMapping,
) -> bool:
    if mapping.confirmation_status in _CONFIRMATION_BLOCKING:
        return True
    return any(
        candidate.confirmation_status in _CONFIRMATION_BLOCKING
        for candidate in mapping.candidates
    )


def _has_assignment(
    request: GeoXReadoutInputResolutionRequest,
    datasets: dict[DatasetSemanticType, DatasetReference],
) -> bool:
    if request.assignment_column_mapping is not None:
        assignment = request.assignment_column_mapping
        if assignment.geo_unit_column and assignment.treatment_control_label_column:
            return True
    metadata = request.experiment_metadata
    if metadata is not None and metadata.assignment_artifact_ref is not None:
        return True
    if metadata is not None and metadata.design_artifact_ref is not None:
        return True
    if DatasetSemanticType.ASSIGNMENT_TABLE in datasets:
        return True
    if DatasetSemanticType.DESIGN_ARTIFACT in datasets:
        return True
    return False


def _has_dates(metadata: GeoXExperimentMetadataRef) -> bool:
    return bool(
        metadata.test_start_date
        and metadata.test_end_date
        and metadata.post_period_start
        and metadata.post_period_end
    )


def _kpi_mapping_complete(mapping: KPIColumnMapping | None) -> bool:
    if mapping is None:
        return False
    return bool(
        mapping.date_week_column
        and mapping.geo_unit_column
        and mapping.kpi_metric_column
        and mapping.kpi_metric_name
    )


def _spend_mapping_complete(mapping: SpendColumnMapping | None) -> bool:
    if mapping is None:
        return False
    return bool(
        mapping.date_week_column
        and mapping.geo_unit_column
        and mapping.spend_amount_column
    )


def _missing_value_mapping(
    request: GeoXReadoutInputResolutionRequest,
    intent: GeoXReadoutIntent,
) -> GeoXMissingInputReason | None:
    kpi = request.kpi_column_mapping
    value = request.value_mapping

    if intent == GeoXReadoutIntent.READOUT_WITH_ROAS:
        if kpi is not None and kpi.kpi_is_revenue_denominator:
            return None
        if value is not None and (
            value.revenue_mapping_source or value.value_per_incremental_kpi is not None
        ):
            return None
        return GeoXMissingInputReason.MISSING_VALUE_MAPPING_FOR_ROAS

    if intent == GeoXReadoutIntent.READOUT_WITH_PROFIT_ROI:
        if kpi is not None and kpi.kpi_is_profit_denominator:
            return None
        if value is not None and value.margin_profit_mapping_source:
            return None
        return GeoXMissingInputReason.MISSING_MARGIN_MAPPING_FOR_PROFIT_ROI

    return None


def _can_partial_readout(intent: GeoXReadoutIntent) -> bool:
    return intent in {
        GeoXReadoutIntent.READOUT_WITH_COST_PER,
        GeoXReadoutIntent.READOUT_WITH_ROAS,
        GeoXReadoutIntent.READOUT_WITH_PROFIT_ROI,
    }


def _ready_status(
    intent: GeoXReadoutIntent,
    spend_present: bool,
) -> GeoXReadoutResolutionStatus:
    if intent == GeoXReadoutIntent.READOUT_KPI_ONLY:
        return GeoXReadoutResolutionStatus.READY_FOR_KPI_ONLY_READOUT
    if intent == GeoXReadoutIntent.READOUT_WITH_LIFT:
        return GeoXReadoutResolutionStatus.READY_FOR_LIFT_ONLY_READOUT
    if intent == GeoXReadoutIntent.READOUT_WITH_COST_PER and spend_present:
        return GeoXReadoutResolutionStatus.READY_FOR_COST_PER_READOUT
    return GeoXReadoutResolutionStatus.READY_FOR_GEOX_READOUT


def _build_handoff(
    request: GeoXReadoutInputResolutionRequest,
    intent: GeoXReadoutIntent,
    status: GeoXReadoutResolutionStatus,
    missing: list[GeoXMissingInputReason],
    warnings: list[str],
    *,
    kpi_ref: DatasetReference | None = None,
    spend_ref: DatasetReference | None = None,
) -> GeoXReadoutInputHandoff | None:
    metadata = request.experiment_metadata
    if metadata is None or kpi_ref is None:
        return None
    if not _has_assignment(request, _inventory_datasets(request.dataset_refs)):
        return None

    return GeoXReadoutInputHandoff(
        request_id=request.request_id,
        user_request=request.user_request,
        readout_intent=intent,
        experiment_id=metadata.experiment_id,
        design_artifact_ref=metadata.design_artifact_ref,
        assignment_artifact_ref=metadata.assignment_artifact_ref,
        kpi_dataset_ref=kpi_ref,
        kpi_column_mapping=request.kpi_column_mapping,
        spend_dataset_ref_optional=spend_ref,
        spend_column_mapping_optional=request.spend_column_mapping,
        spend_baseline_definition_optional=request.spend_baseline_definition_optional,
        value_mapping_optional=request.value_mapping,
        requested_metrics=list(request.requested_metrics),
        missing_inputs=list(missing),
        mip_resolution_status=status,
        lineage={**request.lineage, **metadata.lineage},
        warnings=warnings,
    )


def _blocked(
    request: GeoXReadoutInputResolutionRequest,
    intent: GeoXReadoutIntent,
    status: GeoXReadoutResolutionStatus,
    missing: list[GeoXMissingInputReason],
    messages: list[str],
    warnings: list[str],
) -> GeoXReadoutInputResolutionResult:
    return _result(request, intent, status, missing, messages, warnings)


def _result(
    request: GeoXReadoutInputResolutionRequest,
    intent: GeoXReadoutIntent,
    status: GeoXReadoutResolutionStatus,
    missing: list[GeoXMissingInputReason],
    messages: list[str],
    warnings: list[str],
    *,
    mapping_confirmation_required: bool = False,
    handoff: GeoXReadoutInputHandoff | None = None,
) -> GeoXReadoutInputResolutionResult:
    return GeoXReadoutInputResolutionResult(
        request_id=request.request_id,
        readout_intent=intent,
        resolution_status=status,
        missing_inputs=missing,
        dataset_refs_used=list(request.dataset_refs),
        mapping_confirmation_required=mapping_confirmation_required,
        handoff=handoff,
        user_messages=messages,
        warnings=warnings,
    )
