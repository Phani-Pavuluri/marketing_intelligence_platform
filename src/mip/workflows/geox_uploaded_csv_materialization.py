"""GeoX uploaded CSV materialization workflow (narrow local uploads only)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd  # type: ignore[import-untyped]

from mip.contracts.geox_panel_exp_integration import GeoXMaterializedInputAvailability
from mip.contracts.geox_readout_input_resolution import (
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    MappingConfirmationStatus,
)
from mip.contracts.geox_uploaded_csv_materialization import (
    ALLOWED_FILE_EXTENSIONS,
    ALLOWED_UPLOADED_SOURCE_TYPES,
    GeoXUploadedCSVDataset,
    GeoXUploadedCSVInspection,
    GeoXUploadedCSVIssueCode,
    GeoXUploadedCSVMaterializationRequest,
    GeoXUploadedCSVMaterializationResult,
    GeoXUploadedCSVMaterializationStatus,
    GeoXUploadedCSVRole,
    GeoXUploadedCSVSource,
)

_REQUIRED_ROLES = {
    GeoXUploadedCSVRole.KPI_PANEL,
    GeoXUploadedCSVRole.SPEND_PANEL,
    GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
}
_ROLE_TO_SEMANTIC: dict[GeoXUploadedCSVRole, DatasetSemanticType] = {
    GeoXUploadedCSVRole.KPI_PANEL: DatasetSemanticType.KPI_PANEL,
    GeoXUploadedCSVRole.SPEND_PANEL: DatasetSemanticType.SPEND_PANEL,
    GeoXUploadedCSVRole.ASSIGNMENT_TABLE: DatasetSemanticType.ASSIGNMENT_TABLE,
    GeoXUploadedCSVRole.EXPERIMENT_METADATA: DatasetSemanticType.EXPERIMENT_METADATA,
    GeoXUploadedCSVRole.UNKNOWN: DatasetSemanticType.UNKNOWN_DATASET,
}


def materialize_geox_uploaded_csvs(
    request: GeoXUploadedCSVMaterializationRequest,
) -> GeoXUploadedCSVMaterializationResult:
    """Materialize user-uploaded GeoX readout CSVs under strict policy limits."""
    lineage = {
        **request.lineage,
        "materialization_mode": "uploaded_csv_only",
        "policy": str(request.policy),
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[GeoXUploadedCSVIssueCode] = []
    inspections: list[GeoXUploadedCSVInspection] = []
    datasets: list[GeoXUploadedCSVDataset] = []

    if not request.sources:
        return _blocked(
            request.request_id,
            GeoXUploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD,
            [GeoXUploadedCSVIssueCode.MISSING_UPLOAD],
            warnings,
            lineage,
        )

    role_counts: dict[GeoXUploadedCSVRole, int] = {}
    for source in request.sources:
        role_counts[source.role] = role_counts.get(source.role, 0) + 1

    for role, count in role_counts.items():
        if role in _REQUIRED_ROLES and count > 1:
            return _blocked(
                request.request_id,
                GeoXUploadedCSVMaterializationStatus.BLOCKED_AMBIGUOUS_ROLE,
                [
                    GeoXUploadedCSVIssueCode.DUPLICATE_ROLE,
                    GeoXUploadedCSVIssueCode.AMBIGUOUS_ROLE,
                ],
                warnings + [f"Duplicate uploaded CSV role: {role}"],
                lineage,
            )

    if GeoXUploadedCSVRole.EXPERIMENT_METADATA not in role_counts:
        warnings.append("Optional experiment metadata CSV not provided.")
        issues.append(GeoXUploadedCSVIssueCode.OPTIONAL_METADATA_MISSING)

    status = GeoXUploadedCSVMaterializationStatus.MATERIALIZED
    for source in request.sources:
        single_status, inspection, dataset, source_issues, source_warnings = (
            _materialize_single_source(source, request)
        )
        inspections.append(inspection)
        issues.extend(source_issues)
        warnings.extend(source_warnings)
        if single_status != GeoXUploadedCSVMaterializationStatus.MATERIALIZED:
            status = single_status
            continue
        if dataset is not None:
            datasets.append(dataset)

    if status == GeoXUploadedCSVMaterializationStatus.MATERIALIZED and warnings:
        status = GeoXUploadedCSVMaterializationStatus.MATERIALIZED_WITH_WARNINGS

    issues.append(GeoXUploadedCSVIssueCode.LINEAGE_RECORDED)
    return GeoXUploadedCSVMaterializationResult(
        request_id=request.request_id,
        status=status,
        datasets=datasets,
        inspections=inspections,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def build_materialized_input_availability_from_uploaded_csv_result(
    result: GeoXUploadedCSVMaterializationResult,
) -> GeoXMaterializedInputAvailability:
    """Map uploaded CSV materialization output to Stage 3A availability indicators."""
    spend_dataset = _dataset_for_role(result, GeoXUploadedCSVRole.SPEND_PANEL)
    assignment_dataset = _dataset_for_role(result, GeoXUploadedCSVRole.ASSIGNMENT_TABLE)
    kpi_dataset = _dataset_for_role(result, GeoXUploadedCSVRole.KPI_PANEL)
    metadata_dataset = _dataset_for_role(result, GeoXUploadedCSVRole.EXPERIMENT_METADATA)
    return GeoXMaterializedInputAvailability(
        has_materialized_spend_df=spend_dataset is not None,
        has_materialized_assignment_df=assignment_dataset is not None,
        has_assignment_mapping=assignment_dataset is not None,
        materialized_spend_ref_optional=(
            spend_dataset.lineage.get("uploaded_path") if spend_dataset else None
        ),
        materialized_assignment_ref_optional=(
            assignment_dataset.lineage.get("uploaded_path") if assignment_dataset else None
        ),
        lineage={
            **result.lineage,
            "materialization_status": str(result.status),
            "materialized_dataset_count": str(len(result.datasets)),
            "has_kpi_panel": str(kpi_dataset is not None).lower(),
            "has_experiment_metadata": str(metadata_dataset is not None).lower(),
        },
        warnings=list(result.warnings),
    )


def build_dataset_reference_from_uploaded_csv_inspection(
    source: GeoXUploadedCSVSource,
    inspection: GeoXUploadedCSVInspection,
) -> DatasetReference:
    """Align uploaded CSV inspection metadata with DatasetReference conventions."""
    semantic_type = _ROLE_TO_SEMANTIC.get(source.role, DatasetSemanticType.UNKNOWN_DATASET)
    return DatasetReference(
        dataset_ref_id=source.source_id,
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=semantic_type,
        source_uri_or_handle=source.path,
        file_name_or_table_name=source.original_filename,
        declared_or_detected_columns=list(inspection.columns),
        classification_confidence=1.0 if source.role != GeoXUploadedCSVRole.UNKNOWN else 0.0,
        user_confirmation_status=MappingConfirmationStatus.USER_CONFIRMED,
        lineage={
            **source.lineage,
            **inspection.lineage,
            "uploaded_csv_role": str(source.role),
            "row_count": str(inspection.row_count),
            "column_count": str(inspection.column_count),
        },
        warnings=list(inspection.warnings),
    )


def _materialize_single_source(
    source: GeoXUploadedCSVSource,
    request: GeoXUploadedCSVMaterializationRequest,
) -> tuple[
    GeoXUploadedCSVMaterializationStatus,
    GeoXUploadedCSVInspection,
    GeoXUploadedCSVDataset | None,
    list[GeoXUploadedCSVIssueCode],
    list[str],
]:
    issues: list[GeoXUploadedCSVIssueCode] = []
    warnings: list[str] = []

    if source.role == GeoXUploadedCSVRole.UNKNOWN:
        inspection = _empty_inspection(source)
        issues.append(GeoXUploadedCSVIssueCode.AMBIGUOUS_ROLE)
        return (
            GeoXUploadedCSVMaterializationStatus.BLOCKED_AMBIGUOUS_ROLE,
            inspection,
            None,
            issues,
            warnings,
        )

    if not source.path.strip():
        inspection = _empty_inspection(source)
        issues.append(GeoXUploadedCSVIssueCode.MISSING_UPLOAD)
        return (
            GeoXUploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD,
            inspection,
            None,
            issues,
            warnings,
        )

    if source.source_type not in ALLOWED_UPLOADED_SOURCE_TYPES:
        inspection = _empty_inspection(source)
        issues.append(GeoXUploadedCSVIssueCode.UNSUPPORTED_SOURCE_TYPE)
        return (
            GeoXUploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_SOURCE_TYPE,
            inspection,
            None,
            issues,
            warnings,
        )

    file_path = Path(source.path)
    if file_path.suffix.lower() not in ALLOWED_FILE_EXTENSIONS:
        inspection = _empty_inspection(source)
        issues.append(GeoXUploadedCSVIssueCode.UNSUPPORTED_FILE_TYPE)
        return (
            GeoXUploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_FILE_TYPE,
            inspection,
            None,
            issues,
            warnings,
        )

    if not file_path.is_file():
        inspection = _empty_inspection(source)
        issues.append(GeoXUploadedCSVIssueCode.MISSING_UPLOAD)
        return (
            GeoXUploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD,
            inspection,
            None,
            issues,
            warnings,
        )

    file_size_bytes = file_path.stat().st_size
    if file_size_bytes > request.max_file_size_bytes:
        inspection = GeoXUploadedCSVInspection(
            source_id=source.source_id,
            role=source.role,
            file_size_bytes=file_size_bytes,
            issues=[GeoXUploadedCSVIssueCode.FILE_TOO_LARGE],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(GeoXUploadedCSVIssueCode.FILE_TOO_LARGE)
        return (
            GeoXUploadedCSVMaterializationStatus.BLOCKED_FILE_TOO_LARGE,
            inspection,
            None,
            issues,
            warnings,
        )

    try:
        dataframe = pd.read_csv(file_path)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError):
        inspection = GeoXUploadedCSVInspection(
            source_id=source.source_id,
            role=source.role,
            file_size_bytes=file_size_bytes,
            issues=[GeoXUploadedCSVIssueCode.MALFORMED_CSV],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(GeoXUploadedCSVIssueCode.MALFORMED_CSV)
        return (
            GeoXUploadedCSVMaterializationStatus.BLOCKED_MALFORMED_CSV,
            inspection,
            None,
            issues,
            warnings,
        )

    raw_columns = [str(column) for column in dataframe.columns]
    normalized_columns, column_normalized = _normalize_columns(raw_columns)
    if column_normalized:
        issues.append(GeoXUploadedCSVIssueCode.COLUMN_NAME_NORMALIZED)
        warnings.append("Column names normalized by stripping whitespace.")
        dataframe.columns = normalized_columns

    row_count = len(dataframe)
    column_count = len(normalized_columns)

    if column_count == 0:
        inspection = GeoXUploadedCSVInspection(
            source_id=source.source_id,
            role=source.role,
            columns=normalized_columns,
            row_count=row_count,
            column_count=column_count,
            file_size_bytes=file_size_bytes,
            issues=[GeoXUploadedCSVIssueCode.EMPTY_FILE],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(GeoXUploadedCSVIssueCode.EMPTY_FILE)
        return (
            GeoXUploadedCSVMaterializationStatus.BLOCKED_EMPTY_FILE,
            inspection,
            None,
            issues,
            warnings,
        )

    if row_count == 0:
        inspection = GeoXUploadedCSVInspection(
            source_id=source.source_id,
            role=source.role,
            columns=normalized_columns,
            row_count=row_count,
            column_count=column_count,
            file_size_bytes=file_size_bytes,
            issues=[
                GeoXUploadedCSVIssueCode.EMPTY_FILE,
                GeoXUploadedCSVIssueCode.HEADER_ONLY_FILE,
            ],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.extend(
            [
                GeoXUploadedCSVIssueCode.EMPTY_FILE,
                GeoXUploadedCSVIssueCode.HEADER_ONLY_FILE,
            ]
        )
        return (
            GeoXUploadedCSVMaterializationStatus.BLOCKED_EMPTY_FILE,
            inspection,
            None,
            issues,
            warnings,
        )

    if row_count > request.max_rows:
        inspection = GeoXUploadedCSVInspection(
            source_id=source.source_id,
            role=source.role,
            columns=normalized_columns,
            row_count=row_count,
            column_count=column_count,
            file_size_bytes=file_size_bytes,
            issues=[GeoXUploadedCSVIssueCode.ROW_LIMIT_EXCEEDED],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(GeoXUploadedCSVIssueCode.ROW_LIMIT_EXCEEDED)
        return (
            GeoXUploadedCSVMaterializationStatus.BLOCKED_ROW_LIMIT_EXCEEDED,
            inspection,
            None,
            issues,
            warnings,
        )

    missing_required = [
        column
        for column in source.required_columns
        if column not in normalized_columns
    ]
    if missing_required:
        inspection = GeoXUploadedCSVInspection(
            source_id=source.source_id,
            role=source.role,
            columns=normalized_columns,
            row_count=row_count,
            column_count=column_count,
            file_size_bytes=file_size_bytes,
            issues=[GeoXUploadedCSVIssueCode.MISSING_REQUIRED_COLUMNS],
            warnings=[f"Missing required columns: {', '.join(missing_required)}"],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(GeoXUploadedCSVIssueCode.MISSING_REQUIRED_COLUMNS)
        return (
            GeoXUploadedCSVMaterializationStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
            inspection,
            None,
            issues,
            warnings,
        )

    source_lineage = _base_lineage(source, file_path, file_size_bytes)
    source_lineage.update(
        {
            "row_count": str(row_count),
            "column_count": str(column_count),
            "columns": ",".join(normalized_columns),
            **source.lineage,
        }
    )
    inspection = GeoXUploadedCSVInspection(
        source_id=source.source_id,
        role=source.role,
        columns=normalized_columns,
        row_count=row_count,
        column_count=column_count,
        file_size_bytes=file_size_bytes,
        issues=list(issues),
        warnings=list(warnings),
        lineage=dict(source_lineage),
    )
    dataset = GeoXUploadedCSVDataset(
        source_id=source.source_id,
        role=source.role,
        dataframe=dataframe,
        columns=normalized_columns,
        row_count=row_count,
        column_count=column_count,
        lineage=dict(source_lineage),
    )
    return (
        GeoXUploadedCSVMaterializationStatus.MATERIALIZED,
        inspection,
        dataset,
        issues,
        warnings,
    )


def _dataset_for_role(
    result: GeoXUploadedCSVMaterializationResult,
    role: GeoXUploadedCSVRole,
) -> GeoXUploadedCSVDataset | None:
    for dataset in result.datasets:
        if dataset.role == role:
            return dataset
    return None


def _empty_inspection(source: GeoXUploadedCSVSource) -> GeoXUploadedCSVInspection:
    return GeoXUploadedCSVInspection(
        source_id=source.source_id,
        role=source.role,
        lineage=dict(source.lineage),
    )


def _base_lineage(
    source: GeoXUploadedCSVSource,
    file_path: Path,
    file_size_bytes: int,
) -> dict[str, str]:
    return {
        "source_id": source.source_id,
        "uploaded_path": str(file_path),
        "original_filename": source.original_filename,
        "source_type": source.source_type,
        "role": str(source.role),
        "file_size_bytes": str(file_size_bytes),
    }


def _normalize_columns(columns: list[str]) -> tuple[list[str], bool]:
    normalized = [column.strip() for column in columns]
    return normalized, normalized != columns


def _blocked(
    request_id: str,
    status: GeoXUploadedCSVMaterializationStatus,
    issues: list[GeoXUploadedCSVIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXUploadedCSVMaterializationResult:
    return GeoXUploadedCSVMaterializationResult(
        request_id=request_id,
        status=status,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[GeoXUploadedCSVIssueCode],
) -> list[GeoXUploadedCSVIssueCode]:
    seen: set[GeoXUploadedCSVIssueCode] = set()
    ordered: list[GeoXUploadedCSVIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
