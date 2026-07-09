"""GeoX readout input resolution pipeline (Stage 2C — inspect then resolve)."""

from __future__ import annotations

from mip.contracts.geox_readout_input_resolution import (
    AssignmentColumnMapping,
    ColumnMappingCandidate,
    DatasetReference,
    DatasetSemanticType,
    GeoXReadoutInputResolutionRequest,
    KPIColumnMapping,
    MappingConfirmationStatus,
    SpendColumnMapping,
    ValueMapping,
)
from mip.contracts.geox_readout_input_resolution_pipeline import (
    GeoXReadoutInputResolutionPipelineResult,
)
from mip.contracts.geox_readout_source_inspection import (
    DatasetSourceInspectionResult,
    GeoXReadoutSourceInspectionRequest,
    GeoXReadoutSourceInspectionResult,
    SourceInspectionIssueCode,
)
from mip.workflows.geox_readout_input_resolution import resolve_geox_readout_inputs
from mip.workflows.geox_readout_source_inspection import (
    inspect_dataset_reference,
    inspect_geox_readout_sources,
)

_CONFIRMATION_BLOCKING = frozenset(
    {
        MappingConfirmationStatus.CONFIRMATION_REQUIRED,
        MappingConfirmationStatus.AMBIGUOUS,
    }
)


def resolve_geox_readout_inputs_with_source_inspection(
    request: GeoXReadoutInputResolutionRequest,
    *,
    allow_local_file_metadata_inspection: bool = False,
) -> GeoXReadoutInputResolutionPipelineResult:
    """Run source inspection, enrich refs/mappings, then resolve readout inputs."""
    inspection = inspect_geox_readout_sources(
        GeoXReadoutSourceInspectionRequest(
            request_id=f"{request.request_id}:inspection",
            dataset_refs=list(request.dataset_refs),
            allow_local_file_metadata_inspection=allow_local_file_metadata_inspection,
            lineage=dict(request.lineage),
            warnings=list(request.warnings),
        )
    )
    enriched_request = prepare_resolver_request_from_inspection(request, inspection)
    resolution = resolve_geox_readout_inputs(enriched_request)
    pipeline_warnings = list(
        dict.fromkeys(
            request.warnings
            + inspection.warnings
            + enriched_request.warnings
            + resolution.warnings
        )
    )
    return GeoXReadoutInputResolutionPipelineResult(
        request_id=request.request_id,
        inspection_result=inspection,
        enriched_dataset_refs=list(enriched_request.dataset_refs),
        enriched_resolution_request=enriched_request,
        resolution_result=resolution,
        lineage={
            **request.lineage,
            "pipeline_stage": "2c_inspection_to_resolution",
            "inspection_request_id": inspection.request_id,
        },
        warnings=pipeline_warnings,
    )


def prepare_resolver_request_from_inspection(
    request: GeoXReadoutInputResolutionRequest,
    inspection_result: GeoXReadoutSourceInspectionResult,
) -> GeoXReadoutInputResolutionRequest:
    """Transform inspection output into a resolver-ready request."""
    enriched_refs = [
        enrich_dataset_reference_from_inspection(result)
        for result in inspection_result.dataset_results
    ]
    kpi_mapping, spend_mapping, assignment_mapping, value_mapping = (
        build_column_mappings_from_inspection(inspection_result.dataset_results)
    )
    warnings = list(request.warnings)
    for result in inspection_result.dataset_results:
        if _semantic_ambiguity_requires_confirmation(result):
            warnings.append(
                f"Ambiguous semantic classification for dataset {result.dataset_ref.dataset_ref_id}"
            )

    return request.model_copy(
        update={
            "dataset_refs": enriched_refs,
            "kpi_column_mapping": request.kpi_column_mapping or kpi_mapping,
            "spend_column_mapping": request.spend_column_mapping or spend_mapping,
            "assignment_column_mapping": (
                request.assignment_column_mapping or assignment_mapping
            ),
            "value_mapping": request.value_mapping or value_mapping,
            "warnings": warnings,
            "lineage": {
                **request.lineage,
                "source_inspection_applied": "true",
                "inspected_dataset_count": str(inspection_result.inspected_dataset_count),
            },
        }
    )


def enrich_dataset_reference_from_inspection(
    inspection_result: DatasetSourceInspectionResult,
) -> DatasetReference:
    """Preserve the original ref while applying inspection-derived metadata."""
    ref = inspection_result.dataset_ref
    lineage = {
        **ref.lineage,
        **inspection_result.lineage,
        "inspection_status": str(inspection_result.inspection_status),
    }
    warnings = list(dict.fromkeys(ref.warnings + inspection_result.warnings))
    updates: dict[str, object] = {
        "lineage": lineage,
        "warnings": warnings,
        "declared_or_detected_columns": (
            inspection_result.available_columns or ref.declared_or_detected_columns
        ),
    }
    if inspection_result.semantic_hints:
        top_hint = inspection_result.semantic_hints[0]
        if ref.semantic_type == DatasetSemanticType.UNKNOWN_DATASET:
            updates["semantic_type"] = top_hint.semantic_type
            updates["classification_confidence"] = top_hint.confidence
        elif top_hint.confidence > ref.classification_confidence:
            updates["classification_confidence"] = top_hint.confidence
    return ref.model_copy(update=updates)


def build_column_mappings_from_inspection(
    dataset_results: list[DatasetSourceInspectionResult],
) -> tuple[
    KPIColumnMapping | None,
    SpendColumnMapping | None,
    AssignmentColumnMapping | None,
    ValueMapping | None,
]:
    """Build resolver column mappings from per-dataset inspection candidates."""
    by_semantic: dict[DatasetSemanticType, DatasetSourceInspectionResult] = {}
    for result in dataset_results:
        semantic = _semantic_type_for_result(result)
        if semantic not in by_semantic:
            by_semantic[semantic] = result

    kpi_mapping = _build_kpi_mapping(by_semantic.get(DatasetSemanticType.KPI_PANEL))
    spend_mapping = _build_spend_mapping(by_semantic.get(DatasetSemanticType.SPEND_PANEL))
    assignment_mapping = _build_assignment_mapping(
        by_semantic.get(DatasetSemanticType.ASSIGNMENT_TABLE)
    )
    value_mapping = _build_value_mapping(
        by_semantic.get(DatasetSemanticType.VALUE_MAPPING),
        by_semantic.get(DatasetSemanticType.MARGIN_MAPPING),
    )
    return kpi_mapping, spend_mapping, assignment_mapping, value_mapping


def inspect_and_prepare_dataset_reference(
    dataset_ref: DatasetReference,
    *,
    allow_local_file_metadata_inspection: bool = False,
) -> DatasetReference:
    """Inspect one dataset ref and return the resolver-ready enriched reference."""
    inspection = inspect_dataset_reference(
        dataset_ref,
        allow_local_file_metadata_inspection=allow_local_file_metadata_inspection,
    )
    return enrich_dataset_reference_from_inspection(inspection)


def _semantic_type_for_result(
    result: DatasetSourceInspectionResult,
) -> DatasetSemanticType:
    if result.semantic_hints:
        return result.semantic_hints[0].semantic_type
    return result.dataset_ref.semantic_type


def _build_kpi_mapping(
    result: DatasetSourceInspectionResult | None,
) -> KPIColumnMapping | None:
    if result is None:
        return None
    candidates = list(result.mapping_candidates)
    date_col = _pick_source_column(candidates, "date_week_column")
    geo_col = _pick_source_column(candidates, "geo_unit_column")
    kpi_col = _pick_source_column(candidates, "kpi_metric_column")
    if not (date_col and geo_col and kpi_col):
        return None
    used = _candidates_for_fields(
        candidates,
        ("date_week_column", "geo_unit_column", "kpi_metric_column"),
    )
    return KPIColumnMapping(
        date_week_column=date_col,
        geo_unit_column=geo_col,
        kpi_metric_column=kpi_col,
        kpi_metric_name=kpi_col,
        confirmation_status=_mapping_confirmation_from_candidates(used, result),
        candidates=used,
    )


def _build_spend_mapping(
    result: DatasetSourceInspectionResult | None,
) -> SpendColumnMapping | None:
    if result is None:
        return None
    candidates = list(result.mapping_candidates)
    date_col = _pick_source_column(candidates, "date_week_column")
    geo_col = _pick_source_column(candidates, "geo_unit_column")
    spend_col = _pick_source_column(candidates, "spend_amount_column")
    if not (date_col and geo_col and spend_col):
        return None
    fields = ("date_week_column", "geo_unit_column", "spend_amount_column")
    used = _candidates_for_fields(candidates, fields)
    currency_col = _pick_source_column(candidates, "currency_column")
    if currency_col:
        used.extend(_candidates_for_fields(candidates, ("currency_column",)))
    return SpendColumnMapping(
        date_week_column=date_col,
        geo_unit_column=geo_col,
        spend_amount_column=spend_col,
        currency_column=currency_col,
        confirmation_status=_mapping_confirmation_from_candidates(used, result),
        candidates=used,
    )


def _build_assignment_mapping(
    result: DatasetSourceInspectionResult | None,
) -> AssignmentColumnMapping | None:
    if result is None:
        return None
    candidates = list(result.mapping_candidates)
    geo_col = _pick_source_column(candidates, "geo_unit_column")
    cell_col = _pick_source_column(candidates, "cell_column")
    label_col = _pick_source_column(candidates, "treatment_control_label_column")
    if not geo_col:
        return None
    if not (cell_col or label_col):
        return None
    fields: list[str] = ["geo_unit_column"]
    if cell_col:
        fields.append("cell_column")
    if label_col:
        fields.append("treatment_control_label_column")
    used = _candidates_for_fields(candidates, tuple(fields))
    return AssignmentColumnMapping(
        geo_unit_column=geo_col,
        cell_column=cell_col,
        treatment_control_label_column=label_col,
        confirmation_status=_mapping_confirmation_from_candidates(used, result),
        candidates=used,
    )


def _build_value_mapping(
    value_result: DatasetSourceInspectionResult | None,
    margin_result: DatasetSourceInspectionResult | None,
) -> ValueMapping | None:
    if value_result is None and margin_result is None:
        return None
    result = value_result or margin_result
    assert result is not None
    candidates = list(result.mapping_candidates)
    revenue_source = _pick_source_column(candidates, "revenue_mapping_source")
    margin_source = _pick_source_column(candidates, "margin_profit_mapping_source")
    currency = _pick_source_column(candidates, "currency")
    if not (revenue_source or margin_source):
        return None
    fields: list[str] = []
    if revenue_source:
        fields.append("revenue_mapping_source")
    if margin_source:
        fields.append("margin_profit_mapping_source")
    if currency:
        fields.append("currency")
    used = _candidates_for_fields(candidates, tuple(fields))
    return ValueMapping(
        revenue_mapping_source=revenue_source,
        margin_profit_mapping_source=margin_source,
        currency=currency,
        confirmation_status=_mapping_confirmation_from_candidates(used, result),
        candidates=used,
    )


def _pick_source_column(
    candidates: list[ColumnMappingCandidate],
    target_field: str,
) -> str | None:
    matches = [c for c in candidates if c.target_field == target_field]
    if not matches:
        return None
    best = max(matches, key=lambda candidate: candidate.confidence)
    return best.source_column


def _candidates_for_fields(
    candidates: list[ColumnMappingCandidate],
    target_fields: tuple[str, ...],
) -> list[ColumnMappingCandidate]:
    selected: list[ColumnMappingCandidate] = []
    seen: set[tuple[str, str]] = set()
    for target_field in target_fields:
        matches = [c for c in candidates if c.target_field == target_field]
        if not matches:
            continue
        best = max(matches, key=lambda candidate: candidate.confidence)
        key = (best.source_column, best.target_field)
        if key not in seen:
            seen.add(key)
            selected.append(best)
    return selected


def _mapping_confirmation_from_candidates(
    candidates: list[ColumnMappingCandidate],
    inspection_result: DatasetSourceInspectionResult,
) -> MappingConfirmationStatus:
    if _semantic_ambiguity_requires_confirmation(inspection_result):
        return MappingConfirmationStatus.CONFIRMATION_REQUIRED
    if any(candidate.confirmation_status in _CONFIRMATION_BLOCKING for candidate in candidates):
        for candidate in candidates:
            if candidate.confirmation_status == MappingConfirmationStatus.AMBIGUOUS:
                return MappingConfirmationStatus.AMBIGUOUS
            if candidate.confirmation_status == MappingConfirmationStatus.CONFIRMATION_REQUIRED:
                return MappingConfirmationStatus.CONFIRMATION_REQUIRED
    if candidates and all(
        candidate.confirmation_status == MappingConfirmationStatus.USER_CONFIRMED
        for candidate in candidates
    ):
        return MappingConfirmationStatus.USER_CONFIRMED
    return MappingConfirmationStatus.NOT_REQUIRED


_PANEL_SEMANTIC_TYPES = frozenset(
    {
        DatasetSemanticType.KPI_PANEL,
        DatasetSemanticType.SPEND_PANEL,
        DatasetSemanticType.ASSIGNMENT_TABLE,
        DatasetSemanticType.VALUE_MAPPING,
        DatasetSemanticType.MARGIN_MAPPING,
    }
)


def _semantic_ambiguity_requires_confirmation(
    inspection_result: DatasetSourceInspectionResult,
) -> bool:
    if SourceInspectionIssueCode.AMBIGUOUS_SEMANTIC_TYPE not in inspection_result.issues:
        return False
    if len(inspection_result.semantic_hints) < 2:
        return False
    primary = inspection_result.semantic_hints[0].semantic_type
    secondary = inspection_result.semantic_hints[1].semantic_type
    return primary in _PANEL_SEMANTIC_TYPES and secondary in _PANEL_SEMANTIC_TYPES
