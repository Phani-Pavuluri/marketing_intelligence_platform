"""Generic tabular source inspection helpers.

Provides source-neutral reference/inspection builders and an uploaded-CSV
compatibility view. Does not re-read CSVs, call connectors, or mutate lanes.
"""

from __future__ import annotations

from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import DataSourceRef
from mip.contracts.tabular_source_reference import (
    TabularSourceAccessMode,
    TabularSourceAvailability,
    TabularSourceColumn,
    TabularSourceInspection,
    TabularSourceInspectionResult,
    TabularSourceInspectionStatus,
    TabularSourceIssueCode,
    TabularSourceLineage,
    TabularSourceMaterializationMode,
    TabularSourceReference,
    TabularSourceSchema,
    TabularSourceType,
)
from mip.contracts.uploaded_csv_materialization import (
    MaterializedTabularDataset,
    UploadedCSVInspection,
    UploadedCSVMaterializationResult,
    UploadedCSVMaterializationStatus,
    UploadedCSVSource,
)
from mip.workflows.uploaded_csv_materialization import (
    build_data_source_ref_from_uploaded_csv_inspection,
    get_materialized_dataset_by_source_id,
)

_READY_MATERIALIZATION_STATUSES = {
    UploadedCSVMaterializationStatus.MATERIALIZED,
    UploadedCSVMaterializationStatus.MATERIALIZED_WITH_WARNINGS,
}
_BLOCKED_MATERIALIZATION_TO_INSPECTION: dict[
    UploadedCSVMaterializationStatus, TabularSourceInspectionStatus
] = {
    UploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD: (
        TabularSourceInspectionStatus.BLOCKED_MISSING_SOURCE
    ),
    UploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_FILE_TYPE: (
        TabularSourceInspectionStatus.BLOCKED_UNSUPPORTED_SOURCE_TYPE
    ),
    UploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_SOURCE_TYPE: (
        TabularSourceInspectionStatus.BLOCKED_UNSUPPORTED_SOURCE_TYPE
    ),
    UploadedCSVMaterializationStatus.BLOCKED_MALFORMED_CSV: (
        TabularSourceInspectionStatus.BLOCKED_SCHEMA_UNAVAILABLE
    ),
    UploadedCSVMaterializationStatus.BLOCKED_MISSING_REQUIRED_COLUMNS: (
        TabularSourceInspectionStatus.BLOCKED_SCHEMA_UNAVAILABLE
    ),
    UploadedCSVMaterializationStatus.BLOCKED_EMPTY_FILE: (
        TabularSourceInspectionStatus.BLOCKED_MATERIALIZATION_UNAVAILABLE
    ),
    UploadedCSVMaterializationStatus.BLOCKED_HEADER_ONLY_FILE: (
        TabularSourceInspectionStatus.BLOCKED_MATERIALIZATION_UNAVAILABLE
    ),
    UploadedCSVMaterializationStatus.BLOCKED_FILE_TOO_LARGE: (
        TabularSourceInspectionStatus.BLOCKED_MATERIALIZATION_UNAVAILABLE
    ),
    UploadedCSVMaterializationStatus.BLOCKED_ROW_LIMIT_EXCEEDED: (
        TabularSourceInspectionStatus.BLOCKED_MATERIALIZATION_UNAVAILABLE
    ),
}


def build_tabular_source_reference(
    *,
    source_id: str,
    source_type: TabularSourceType,
    access_mode: TabularSourceAccessMode,
    materialization_mode: TabularSourceMaterializationMode,
    source_uri: str = "",
    source_name: str = "",
    declared_role_hint: str | None = None,
    schema: TabularSourceSchema | None = None,
    lineage: TabularSourceLineage | None = None,
    data_source_ref: DataSourceRef | None = None,
    metadata: dict[str, str] | None = None,
) -> TabularSourceReference:
    """Build a generic tabular source reference (metadata only)."""
    return TabularSourceReference(
        source_id=source_id,
        source_type=source_type,
        access_mode=access_mode,
        materialization_mode=materialization_mode,
        declared_role_hint=declared_role_hint,
        source_uri=source_uri,
        source_name=source_name,
        schema=schema,
        lineage=lineage,
        data_source_ref=data_source_ref,
        metadata=dict(metadata or {}),
    )


def build_tabular_source_schema_from_columns(
    columns: list[str],
    *,
    normalized_columns: list[str] | None = None,
    row_count: int | None = None,
    estimated_row_count: int | None = None,
    schema_source: str = "",
    metadata: dict[str, str] | None = None,
) -> TabularSourceSchema:
    """Build tabular source schema metadata from column names."""
    normalized = normalized_columns or list(columns)
    tabular_columns = [
        TabularSourceColumn(
            name=name,
            normalized_name=normalized[idx] if idx < len(normalized) else name,
        )
        for idx, name in enumerate(columns)
    ]
    return TabularSourceSchema(
        columns=tabular_columns,
        column_names=list(columns),
        normalized_column_names=list(normalized),
        row_count=row_count,
        estimated_row_count=estimated_row_count,
        schema_source=schema_source,
        metadata=dict(metadata or {}),
    )


def build_tabular_source_inspection_result(
    *,
    request_id: str,
    status: TabularSourceInspectionStatus,
    inspections: list[TabularSourceInspection] | None = None,
    issues: list[TabularSourceIssueCode] | None = None,
    warnings: list[str] | None = None,
    lineage: dict[str, str] | None = None,
) -> TabularSourceInspectionResult:
    """Assemble a tabular source inspection batch result."""
    inspection_list = list(inspections or [])
    return TabularSourceInspectionResult(
        request_id=request_id,
        status=status,
        inspections=inspection_list,
        source_references=[inspection.source_reference for inspection in inspection_list],
        issues=_dedupe_issues(issues or []),
        warnings=list(dict.fromkeys(warnings or [])),
        lineage={
            **(lineage or {}),
            "inspection_stage": "tabular_source_inspection",
        },
    )


def build_tabular_source_inspection_from_uploaded_csv_materialization(
    *,
    request_id: str,
    materialization_result: UploadedCSVMaterializationResult | None,
) -> TabularSourceInspectionResult:
    """Convert uploaded CSV materialization output into generic tabular inspections."""
    base_issues: list[TabularSourceIssueCode] = [
        TabularSourceIssueCode.UPLOADED_CSV_COMPATIBILITY_CREATED,
        TabularSourceIssueCode.NO_CONNECTOR_RUNTIME,
        TabularSourceIssueCode.NO_NETWORK_CALLS,
        TabularSourceIssueCode.NO_SQL_EXECUTION,
        TabularSourceIssueCode.NO_MODEL_EXECUTION,
        TabularSourceIssueCode.NO_OPTIMIZER_EXECUTION,
        TabularSourceIssueCode.NO_RECOMMENDATION_GENERATED,
    ]
    lineage = {"compatibility_view": "uploaded_csv_materialization"}

    if materialization_result is None:
        return build_tabular_source_inspection_result(
            request_id=request_id,
            status=TabularSourceInspectionStatus.BLOCKED_MISSING_SOURCE,
            issues=base_issues + [TabularSourceIssueCode.MISSING_SOURCE],
            lineage=lineage,
        )

    lineage.update(materialization_result.lineage)
    warnings = list(materialization_result.warnings)
    ready = materialization_result.status in _READY_MATERIALIZATION_STATUSES

    if not ready:
        blocked_status = _BLOCKED_MATERIALIZATION_TO_INSPECTION.get(
            materialization_result.status,
            TabularSourceInspectionStatus.BLOCKED_MATERIALIZATION_UNAVAILABLE,
        )
        return build_tabular_source_inspection_result(
            request_id=request_id,
            status=blocked_status,
            inspections=_inspections_from_uploaded_csv(
                materialization_result,
                include_materialized=False,
            ),
            issues=base_issues + [TabularSourceIssueCode.MATERIALIZATION_UNAVAILABLE],
            warnings=warnings,
            lineage=lineage,
        )

    inspections = _inspections_from_uploaded_csv(
        materialization_result,
        include_materialized=True,
    )
    status = (
        TabularSourceInspectionStatus.INSPECTED_WITH_WARNINGS
        if warnings
        else TabularSourceInspectionStatus.INSPECTED
    )
    return build_tabular_source_inspection_result(
        request_id=request_id,
        status=status,
        inspections=inspections,
        issues=base_issues,
        warnings=warnings,
        lineage=lineage,
    )


def _inspections_from_uploaded_csv(
    materialization_result: UploadedCSVMaterializationResult,
    *,
    include_materialized: bool,
) -> list[TabularSourceInspection]:
    inspections: list[TabularSourceInspection] = []
    for csv_inspection in materialization_result.inspections:
        dataset = (
            get_materialized_dataset_by_source_id(materialization_result, csv_inspection.source_id)
            if include_materialized
            else None
        )
        inspections.append(
            _inspection_from_uploaded_csv(csv_inspection, dataset=dataset)
        )
    return inspections


def _inspection_from_uploaded_csv(
    csv_inspection: UploadedCSVInspection,
    *,
    dataset: MaterializedTabularDataset | None,
) -> TabularSourceInspection:
    schema = build_tabular_source_schema_from_columns(
        csv_inspection.columns,
        normalized_columns=csv_inspection.normalized_columns,
        row_count=csv_inspection.row_count or None,
        schema_source="uploaded_csv_inspection",
        metadata={"column_count": str(csv_inspection.column_count)},
    )
    source_uri = csv_inspection.lineage.get("uploaded_path", "")
    source_name = csv_inspection.original_filename
    lineage = TabularSourceLineage(
        source_id=csv_inspection.source_id,
        source_type=TabularSourceType.UPLOADED_CSV,
        source_uri=source_uri,
        source_name=source_name,
        created_from="uploaded_csv_materialization",
        upstream_lineage=dict(csv_inspection.lineage),
        metadata={"shared_materialization": "uploaded_csv_core"},
    )
    data_source_ref = _data_source_ref_from_uploaded_csv(csv_inspection, source_uri)
    reference = build_tabular_source_reference(
        source_id=csv_inspection.source_id,
        source_type=TabularSourceType.UPLOADED_CSV,
        access_mode=TabularSourceAccessMode.LOCAL_FILE,
        materialization_mode=(
            TabularSourceMaterializationMode.MATERIALIZED_IN_MEMORY
            if dataset is not None
            else TabularSourceMaterializationMode.NOT_MATERIALIZED
        ),
        source_uri=source_uri,
        source_name=source_name,
        declared_role_hint=csv_inspection.declared_role_hint,
        schema=schema,
        lineage=lineage,
        data_source_ref=data_source_ref,
        metadata={"original_filename": source_name},
    )
    availability = TabularSourceAvailability(
        has_schema=True,
        has_lineage=True,
        has_data_source_ref=data_source_ref is not None,
        has_materialized_dataset=dataset is not None,
        has_materialized_sample=False,
        is_reference_only=dataset is None,
        is_connector_runtime_required=False,
        materialized_dataset_id=dataset.dataset_id if dataset else None,
        warnings=list(csv_inspection.warnings),
        issues=[TabularSourceIssueCode.AVAILABILITY_CREATED],
    )
    issues = [
        TabularSourceIssueCode.SOURCE_REFERENCE_CREATED,
        TabularSourceIssueCode.SOURCE_INSPECTION_CREATED,
        TabularSourceIssueCode.SCHEMA_CREATED,
        TabularSourceIssueCode.LINEAGE_CREATED,
        TabularSourceIssueCode.AVAILABILITY_CREATED,
    ]
    if csv_inspection.declared_role_hint:
        issues.append(TabularSourceIssueCode.DECLARED_ROLE_HINT_PRESERVED)
    if data_source_ref is not None:
        issues.append(TabularSourceIssueCode.DATA_SOURCE_REF_COMPATIBLE)
    if dataset is not None:
        issues.append(TabularSourceIssueCode.MATERIALIZED_DATASET_ATTACHED)

    return TabularSourceInspection(
        source_reference=reference,
        schema=schema,
        lineage=lineage,
        availability=availability,
        materialized_dataset=dataset,
        warnings=list(csv_inspection.warnings),
        issues=_dedupe_issues(issues),
    )


def _data_source_ref_from_uploaded_csv(
    csv_inspection: UploadedCSVInspection,
    source_uri: str,
) -> DataSourceRef | None:
    if not source_uri.strip():
        return None
    source = UploadedCSVSource(
        source_id=csv_inspection.source_id,
        source_type=csv_inspection.source_type,
        path=source_uri,
        original_filename=csv_inspection.original_filename,
        declared_role_hint=csv_inspection.declared_role_hint,
        lineage=dict(csv_inspection.lineage),
    )
    return build_data_source_ref_from_uploaded_csv_inspection(
        source,
        csv_inspection,
        asset_type=DataAssetType.METRIC_MAPPING,
    )


def _dedupe_issues(
    issues: list[TabularSourceIssueCode],
) -> list[TabularSourceIssueCode]:
    seen: set[TabularSourceIssueCode] = set()
    ordered: list[TabularSourceIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
