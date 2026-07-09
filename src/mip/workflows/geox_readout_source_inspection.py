"""Deterministic GeoX readout source inspection (Stage 2B — metadata only)."""

from __future__ import annotations

import re

from mip.contracts.geox_readout_input_resolution import (
    ColumnMappingCandidate,
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    MappingConfirmationStatus,
    MappingInferenceStatus,
)
from mip.contracts.geox_readout_source_inspection import (
    ColumnInspectionHint,
    ColumnSemanticHint,
    DatasetSemanticInspectionHint,
    DatasetSourceInspectionResult,
    GeoXReadoutSourceInspectionRequest,
    GeoXReadoutSourceInspectionResult,
    SourceInspectionIssueCode,
    SourceInspectionStatus,
)

_LOCAL_FILE_SOURCE_TYPES = frozenset(
    {
        DatasetSourceType.UPLOADED_CSV,
        DatasetSourceType.UPLOADED_EXCEL,
        DatasetSourceType.UPLOADED_PARQUET,
    }
)

_REFERENCE_RESOLVABLE_SOURCE_TYPES = frozenset(
    {
        DatasetSourceType.WAREHOUSE_TABLE,
        DatasetSourceType.API_REFERENCE,
        DatasetSourceType.REGISTERED_ARTIFACT,
        DatasetSourceType.MANUAL_USER_ENTRY,
        DatasetSourceType.UPLOADED_CSV,
        DatasetSourceType.UPLOADED_EXCEL,
        DatasetSourceType.UPLOADED_PARQUET,
    }
)

_COLUMN_HINT_RULES: tuple[tuple[ColumnSemanticHint, tuple[str, ...], list[str]], ...] = (
    (
        ColumnSemanticHint.DATE_OR_WEEK,
        ("date", "week", "week_start", "period", "ds", "event_date", "start_date"),
        ["date_week_column"],
    ),
    (
        ColumnSemanticHint.GEO_OR_UNIT,
        ("geo", "dma", "market", "region", "country", "state", "unit", "location"),
        ["geo_unit_column"],
    ),
    (
        ColumnSemanticHint.KPI_METRIC,
        (
            "kpi",
            "metric",
            "sales",
            "orders",
            "conversions",
            "revenue",
            "arr",
            "gnarr",
            "trials",
            "visits",
            "visitors",
            "installs",
            "units",
        ),
        ["kpi_metric_column", "kpi_metric_name"],
    ),
    (
        ColumnSemanticHint.SPEND_AMOUNT,
        ("spend", "cost", "media_cost", "investment", "budget", "amount"),
        ["spend_amount_column"],
    ),
    (
        ColumnSemanticHint.CURRENCY,
        ("currency", "currency_code"),
        ["currency_column", "currency"],
    ),
    (
        ColumnSemanticHint.CHANNEL,
        ("channel",),
        ["channel_column"],
    ),
    (
        ColumnSemanticHint.PLATFORM,
        ("platform", "ad_network", "publisher"),
        ["platform_column"],
    ),
    (
        ColumnSemanticHint.CAMPAIGN,
        ("campaign", "campaign_id"),
        ["campaign_column", "treatment_cell_join_key"],
    ),
    (
        ColumnSemanticHint.TREATMENT_OR_CELL,
        ("cell", "variant", "group", "experiment_group"),
        ["cell_column", "treatment_cell_join_key"],
    ),
    (
        ColumnSemanticHint.ASSIGNMENT_LABEL,
        ("treatment", "control", "assignment"),
        ["treatment_control_label_column"],
    ),
    (
        ColumnSemanticHint.EXPERIMENT_ID,
        ("experiment_id", "test_id", "geo_test_id", "design_id"),
        ["experiment_id_column", "experiment_id"],
    ),
    (
        ColumnSemanticHint.VALUE_OR_REVENUE,
        ("value", "value_per", "ltv", "aov"),
        ["value_per_incremental_kpi", "revenue_mapping_source"],
    ),
    (
        ColumnSemanticHint.MARGIN_OR_PROFIT,
        ("margin", "profit", "margin_rate"),
        ["margin_profit_mapping_source"],
    ),
)

_SEMANTIC_SCORERS: dict[DatasetSemanticType, tuple[frozenset[ColumnSemanticHint], ...]] = {
    DatasetSemanticType.KPI_PANEL: (
        frozenset({ColumnSemanticHint.DATE_OR_WEEK, ColumnSemanticHint.GEO_OR_UNIT}),
        frozenset({ColumnSemanticHint.KPI_METRIC}),
    ),
    DatasetSemanticType.SPEND_PANEL: (
        frozenset({ColumnSemanticHint.DATE_OR_WEEK, ColumnSemanticHint.GEO_OR_UNIT}),
        frozenset({ColumnSemanticHint.SPEND_AMOUNT}),
    ),
    DatasetSemanticType.ASSIGNMENT_TABLE: (
        frozenset({ColumnSemanticHint.GEO_OR_UNIT}),
        frozenset(
            {
                ColumnSemanticHint.TREATMENT_OR_CELL,
                ColumnSemanticHint.ASSIGNMENT_LABEL,
            }
        ),
    ),
    DatasetSemanticType.VALUE_MAPPING: (
        frozenset({ColumnSemanticHint.VALUE_OR_REVENUE}),
    ),
    DatasetSemanticType.MARGIN_MAPPING: (
        frozenset({ColumnSemanticHint.MARGIN_OR_PROFIT}),
    ),
    DatasetSemanticType.EXPERIMENT_METADATA: (
        frozenset({ColumnSemanticHint.EXPERIMENT_ID, ColumnSemanticHint.DATE_OR_WEEK}),
    ),
}


def inspect_geox_readout_sources(
    request: GeoXReadoutSourceInspectionRequest,
) -> GeoXReadoutSourceInspectionResult:
    """Inspect declared dataset references and emit metadata hints."""
    dataset_results = [
        inspect_dataset_reference(
            dataset_ref,
            allow_local_file_metadata_inspection=request.allow_local_file_metadata_inspection,
        )
        for dataset_ref in request.dataset_refs
    ]
    inspected = sum(
        1
        for result in dataset_results
        if result.inspection_status
        in {
            SourceInspectionStatus.INSPECTED,
            SourceInspectionStatus.DECLARED_COLUMNS_VALIDATED,
        }
    )
    unresolved = sum(1 for result in dataset_results if not result.source_resolvable)
    all_issues: list[SourceInspectionIssueCode] = []
    all_warnings = list(request.warnings)
    for result in dataset_results:
        all_issues.extend(result.issues)
        all_warnings.extend(result.warnings)

    return GeoXReadoutSourceInspectionResult(
        request_id=request.request_id,
        dataset_results=dataset_results,
        inspected_dataset_count=inspected,
        unresolved_dataset_count=unresolved,
        issues=_dedupe_issues(all_issues),
        warnings=all_warnings,
        lineage=dict(request.lineage),
    )


def inspect_dataset_reference(
    dataset_ref: DatasetReference,
    *,
    allow_local_file_metadata_inspection: bool = False,
) -> DatasetSourceInspectionResult:
    """Inspect one declared dataset reference using column-name heuristics only."""
    issues: list[SourceInspectionIssueCode] = []
    warnings = list(dataset_ref.warnings)
    lineage = {
        "dataset_ref_id": dataset_ref.dataset_ref_id,
        "source_type": str(dataset_ref.source_type),
        **dataset_ref.lineage,
    }

    if dataset_ref.source_type == DatasetSourceType.UNKNOWN:
        return _result(
            dataset_ref,
            SourceInspectionStatus.SOURCE_TYPE_NOT_SUPPORTED,
            source_resolvable=False,
            issues=[SourceInspectionIssueCode.SOURCE_TYPE_UNSUPPORTED],
            warnings=warnings,
            lineage=lineage,
        )

    if not dataset_ref.source_uri_or_handle.strip():
        issues.append(SourceInspectionIssueCode.SOURCE_URI_MISSING)
        return _result(
            dataset_ref,
            SourceInspectionStatus.SOURCE_NOT_RESOLVABLE,
            source_resolvable=False,
            issues=issues,
            warnings=warnings,
            lineage=lineage,
        )

    source_resolvable = dataset_ref.source_type in _REFERENCE_RESOLVABLE_SOURCE_TYPES

    if (
        allow_local_file_metadata_inspection
        and dataset_ref.source_type in _LOCAL_FILE_SOURCE_TYPES
    ):
        warnings.append(
            "Local file header inspection is not implemented in Stage 2B; "
            "using declared columns only."
        )

    declared = list(dataset_ref.declared_or_detected_columns)
    if not declared:
        issues.append(SourceInspectionIssueCode.DECLARED_COLUMNS_EMPTY)
        return _result(
            dataset_ref,
            SourceInspectionStatus.NO_COLUMNS_AVAILABLE,
            source_resolvable=source_resolvable,
            declared_columns=[],
            available_columns=[],
            issues=issues,
            warnings=warnings,
            lineage=lineage,
        )

    normalized_declared = [_normalize_column(name) for name in declared]
    if len(normalized_declared) != len(set(normalized_declared)):
        issues.append(SourceInspectionIssueCode.DUPLICATE_COLUMNS)

    available_columns = list(declared)
    missing_declared: list[str] = []

    column_hints = [_hint_for_column(column) for column in declared]
    mapping_candidates = _build_mapping_candidates(column_hints)
    semantic_hints, semantic_issues, semantic_warnings = _infer_semantic_hints(
        dataset_ref,
        column_hints,
    )
    issues.extend(semantic_issues)
    warnings.extend(semantic_warnings)

    issues.extend(_missing_family_issues(column_hints, semantic_hints))

    status = SourceInspectionStatus.INSPECTED
    if missing_declared:
        status = SourceInspectionStatus.DECLARED_COLUMNS_MISSING
    elif issues and not semantic_hints:
        status = SourceInspectionStatus.DECLARED_COLUMNS_VALIDATED

    return _result(
        dataset_ref,
        status,
        source_resolvable=source_resolvable,
        declared_columns=declared,
        available_columns=available_columns,
        missing_declared_columns=missing_declared,
        semantic_hints=semantic_hints,
        column_hints=column_hints,
        mapping_candidates=mapping_candidates,
        issues=_dedupe_issues(issues),
        warnings=warnings,
        lineage=lineage,
    )


def _hint_for_column(column: str) -> ColumnInspectionHint:
    normalized = _normalize_column(column)
    for hint, tokens, targets in _COLUMN_HINT_RULES:
        if _matches_any(normalized, tokens):
            confidence = 0.85 if hint != ColumnSemanticHint.SPEND_AMOUNT else 0.75
            if hint == ColumnSemanticHint.KPI_METRIC and normalized == "amount":
                continue
            return ColumnInspectionHint(
                source_column=column,
                semantic_hint=hint,
                confidence=confidence,
                candidate_target_fields=list(targets),
            )
    return ColumnInspectionHint(
        source_column=column,
        semantic_hint=ColumnSemanticHint.UNKNOWN,
        confidence=0.2,
        candidate_target_fields=[],
        notes="No heuristic match",
    )


def _build_mapping_candidates(
    column_hints: list[ColumnInspectionHint],
) -> list[ColumnMappingCandidate]:
    candidates: list[ColumnMappingCandidate] = []
    target_counts: dict[str, int] = {}
    for hint in column_hints:
        if hint.semantic_hint == ColumnSemanticHint.UNKNOWN:
            continue
        for target_field in hint.candidate_target_fields:
            target_counts[target_field] = target_counts.get(target_field, 0) + 1
            inference = (
                MappingInferenceStatus.INFERRED_HIGH_CONFIDENCE
                if hint.confidence >= 0.8
                else MappingInferenceStatus.INFERRED_LOW_CONFIDENCE
            )
            confirmation = (
                MappingConfirmationStatus.CONFIRMATION_REQUIRED
                if target_counts[target_field] > 1
                else MappingConfirmationStatus.NOT_REQUIRED
            )
            candidates.append(
                ColumnMappingCandidate(
                    source_column=hint.source_column,
                    target_field=target_field,
                    inference_status=inference,
                    confirmation_status=confirmation,
                    confidence=hint.confidence,
                    notes=hint.notes,
                )
            )
    return candidates


def _infer_semantic_hints(
    dataset_ref: DatasetReference,
    column_hints: list[ColumnInspectionHint],
) -> tuple[list[DatasetSemanticInspectionHint], list[SourceInspectionIssueCode], list[str]]:
    if dataset_ref.semantic_type == DatasetSemanticType.DESIGN_ARTIFACT:
        return (
            [
                DatasetSemanticInspectionHint(
                    semantic_type=DatasetSemanticType.DESIGN_ARTIFACT,
                    confidence=max(dataset_ref.classification_confidence, 0.9),
                    evidence=["declared_semantic_type=design_artifact"],
                )
            ],
            [],
            [],
        )

    hint_set = {hint.semantic_hint for hint in column_hints}
    scored: list[tuple[DatasetSemanticType, float, list[str]]] = []
    for semantic_type, requirement_groups in _SEMANTIC_SCORERS.items():
        evidence: list[str] = []
        group_scores: list[float] = []
        for group in requirement_groups:
            matched = hint_set.intersection(group)
            if matched:
                group_scores.append(1.0)
                evidence.append(
                    f"{semantic_type.value}:matched={','.join(m.value for m in matched)}"
                )
            else:
                group_scores.append(0.0)
        if not group_scores:
            continue
        score = sum(group_scores) / len(group_scores)
        if score > 0:
            scored.append((semantic_type, score, evidence))

    scored.sort(key=lambda item: item[1], reverse=True)
    issues: list[SourceInspectionIssueCode] = []
    warnings: list[str] = []

    if not scored:
        warnings.append("Could not infer dataset semantic type from declared columns.")
        return (
            [
                DatasetSemanticInspectionHint(
                    semantic_type=DatasetSemanticType.UNKNOWN_DATASET,
                    confidence=0.2,
                    evidence=["insufficient_column_evidence"],
                    warnings=["Could not infer dataset semantic type from columns."],
                )
            ],
            [],
            warnings,
        )

    top_type, top_score, top_evidence = scored[0]
    confidence = _conservative_confidence(top_score, len(scored))
    hints = [
        DatasetSemanticInspectionHint(
            semantic_type=top_type,
            confidence=confidence,
            evidence=top_evidence,
        )
    ]

    if len(scored) > 1 and scored[1][1] >= top_score - 0.15:
        issues.append(SourceInspectionIssueCode.AMBIGUOUS_SEMANTIC_TYPE)
        warnings.append(
            f"Ambiguous semantic type: {top_type.value} vs {scored[1][0].value}"
        )
        hints.append(
            DatasetSemanticInspectionHint(
                semantic_type=scored[1][0],
                confidence=_conservative_confidence(scored[1][1], len(scored)),
                evidence=scored[1][2],
                warnings=["secondary_semantic_candidate"],
            )
        )

    declared_type = _as_semantic_type(dataset_ref.semantic_type)
    if declared_type != DatasetSemanticType.UNKNOWN_DATASET:
        if declared_type != top_type and confidence < 0.85:
            warnings.append(
                f"Declared semantic_type={declared_type.value} "
                f"differs from inferred={top_type.value}"
            )

    return hints, issues, warnings


def _missing_family_issues(
    column_hints: list[ColumnInspectionHint],
    semantic_hints: list[DatasetSemanticInspectionHint],
) -> list[SourceInspectionIssueCode]:
    if not semantic_hints:
        return []
    primary = semantic_hints[0].semantic_type
    hints = {hint.semantic_hint for hint in column_hints}
    issues: list[SourceInspectionIssueCode] = []

    if primary == DatasetSemanticType.KPI_PANEL:
        if ColumnSemanticHint.DATE_OR_WEEK not in hints:
            issues.append(SourceInspectionIssueCode.NO_DATE_COLUMN_CANDIDATE)
        if ColumnSemanticHint.GEO_OR_UNIT not in hints:
            issues.append(SourceInspectionIssueCode.NO_GEO_COLUMN_CANDIDATE)
        if ColumnSemanticHint.KPI_METRIC not in hints:
            issues.append(SourceInspectionIssueCode.NO_KPI_COLUMN_CANDIDATE)
    elif primary == DatasetSemanticType.SPEND_PANEL:
        if ColumnSemanticHint.SPEND_AMOUNT not in hints:
            issues.append(SourceInspectionIssueCode.NO_SPEND_COLUMN_CANDIDATE)
    elif primary == DatasetSemanticType.ASSIGNMENT_TABLE:
        if ColumnSemanticHint.GEO_OR_UNIT not in hints:
            issues.append(SourceInspectionIssueCode.NO_GEO_COLUMN_CANDIDATE)
        if not hints.intersection(
            {ColumnSemanticHint.TREATMENT_OR_CELL, ColumnSemanticHint.ASSIGNMENT_LABEL}
        ):
            issues.append(SourceInspectionIssueCode.NO_ASSIGNMENT_COLUMN_CANDIDATE)
    elif primary == DatasetSemanticType.VALUE_MAPPING:
        if ColumnSemanticHint.VALUE_OR_REVENUE not in hints:
            issues.append(SourceInspectionIssueCode.NO_VALUE_MAPPING_CANDIDATE)

    return issues


def _conservative_confidence(score: float, candidate_count: int) -> float:
    base = min(max(score * 0.85, 0.2), 0.95)
    if candidate_count > 1:
        return min(base, 0.7)
    return base


def _as_semantic_type(value: DatasetSemanticType | str) -> DatasetSemanticType:
    if isinstance(value, DatasetSemanticType):
        return value
    return DatasetSemanticType(value)


def _normalize_column(column: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", column.strip().lower()).strip("_")


def _matches_any(normalized: str, tokens: tuple[str, ...]) -> bool:
    if normalized in tokens:
        return True
    return any(
        normalized.endswith(f"_{token}") or normalized.startswith(f"{token}_")
        for token in tokens
    )


def _dedupe_issues(
    issues: list[SourceInspectionIssueCode],
) -> list[SourceInspectionIssueCode]:
    seen: set[SourceInspectionIssueCode] = set()
    ordered: list[SourceInspectionIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered


def _result(
    dataset_ref: DatasetReference,
    status: SourceInspectionStatus,
    *,
    source_resolvable: bool,
    declared_columns: list[str] | None = None,
    available_columns: list[str] | None = None,
    missing_declared_columns: list[str] | None = None,
    semantic_hints: list[DatasetSemanticInspectionHint] | None = None,
    column_hints: list[ColumnInspectionHint] | None = None,
    mapping_candidates: list[ColumnMappingCandidate] | None = None,
    issues: list[SourceInspectionIssueCode] | None = None,
    warnings: list[str] | None = None,
    lineage: dict[str, str] | None = None,
) -> DatasetSourceInspectionResult:
    return DatasetSourceInspectionResult(
        dataset_ref=dataset_ref,
        inspection_status=status,
        source_resolvable=source_resolvable,
        declared_columns=declared_columns or [],
        available_columns=available_columns or [],
        missing_declared_columns=missing_declared_columns or [],
        semantic_hints=semantic_hints or [],
        column_hints=column_hints or [],
        mapping_candidates=mapping_candidates or [],
        issues=issues or [],
        warnings=warnings or [],
        lineage=lineage or {},
    )
