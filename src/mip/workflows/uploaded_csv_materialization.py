"""Shared uploaded CSV materialization workflow (lane-neutral)."""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd  # type: ignore[import-untyped]

from mip.contracts.geox_readout_input_resolution import (
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    MappingConfirmationStatus,
)
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import (
    DataSourceMode,
    DataSourceRef,
    DataSourceStatus,
    DataSourceType,
)
from mip.contracts.uploaded_csv_materialization import (
    ALLOWED_FILE_EXTENSIONS,
    MaterializedTabularDataset,
    UploadedCSVInspection,
    UploadedCSVIssueCode,
    UploadedCSVMaterializationRequest,
    UploadedCSVMaterializationResult,
    UploadedCSVMaterializationStatus,
    UploadedCSVSource,
    UploadedCSVSourceType,
)

_ALLOWED_SOURCE_TYPES = {
    UploadedCSVSourceType.UPLOADED_CSV,
    UploadedCSVSourceType.LOCAL_UPLOADED_CSV,
}


def materialize_uploaded_csvs(
    request: UploadedCSVMaterializationRequest,
) -> UploadedCSVMaterializationResult:
    """Materialize uploaded CSVs under shared policy limits."""
    lineage = {
        **request.lineage,
        "materialization_mode": "shared_uploaded_csv_core",
        "policy": str(request.policy),
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[UploadedCSVIssueCode] = []
    inspections: list[UploadedCSVInspection] = []
    datasets: list[MaterializedTabularDataset] = []

    if not request.sources:
        return _blocked(
            request.request_id,
            UploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD,
            [UploadedCSVIssueCode.MISSING_UPLOAD],
            warnings,
            lineage,
        )

    status = UploadedCSVMaterializationStatus.MATERIALIZED
    for source in request.sources:
        single_status, inspection, dataset, source_issues, source_warnings = (
            _materialize_single_source(source, request)
        )
        inspections.append(inspection)
        issues.extend(source_issues)
        warnings.extend(source_warnings)
        if single_status != UploadedCSVMaterializationStatus.MATERIALIZED:
            status = single_status
            continue
        if dataset is not None:
            datasets.append(dataset)

    if status == UploadedCSVMaterializationStatus.MATERIALIZED and warnings:
        status = UploadedCSVMaterializationStatus.MATERIALIZED_WITH_WARNINGS

    issues.append(UploadedCSVIssueCode.LINEAGE_RECORDED)
    return UploadedCSVMaterializationResult(
        request_id=request.request_id,
        status=status,
        datasets=datasets,
        inspections=inspections,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def build_dataset_reference_from_uploaded_csv_inspection(
    source: UploadedCSVSource,
    inspection: UploadedCSVInspection,
) -> DatasetReference:
    """Build a lane-neutral DatasetReference from shared inspection metadata."""
    return DatasetReference(
        dataset_ref_id=source.source_id,
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.UNKNOWN_DATASET,
        source_uri_or_handle=source.path,
        file_name_or_table_name=source.original_filename,
        declared_or_detected_columns=list(inspection.normalized_columns),
        classification_confidence=0.5 if source.declared_role_hint else 0.0,
        user_confirmation_status=MappingConfirmationStatus.NOT_REQUIRED,
        lineage={
            **source.lineage,
            **inspection.lineage,
            "declared_role_hint": source.declared_role_hint or "",
            "shared_materialization": "uploaded_csv_core",
        },
        warnings=list(inspection.warnings),
    )


def build_data_source_ref_from_uploaded_csv_inspection(
    source: UploadedCSVSource,
    inspection: UploadedCSVInspection,
    *,
    asset_type: DataAssetType,
    created_at: datetime | None = None,
    source_mode: DataSourceMode = DataSourceMode.LOCAL_FILE_PATH_MANIFEST,
) -> DataSourceRef:
    """Build a lane-neutral DataSourceRef from shared inspection metadata."""
    timestamp = created_at or datetime.now(tz=UTC)
    return DataSourceRef(
        source_id=source.source_id,
        source_mode=source_mode,
        source_type=DataSourceType.FILE,
        asset_type=asset_type,
        uri_or_table_ref=source.path,
        checksum_or_version=str(inspection.file_size_bytes),
        created_at=timestamp,
        declared_scope={
            "declared_role_hint": source.declared_role_hint or "",
            "original_filename": source.original_filename,
            "shared_materialization": "uploaded_csv_core",
        },
        status=DataSourceStatus.DECLARED,
        warnings=list(inspection.warnings),
    )


def get_materialized_dataset_by_source_id(
    result: UploadedCSVMaterializationResult,
    source_id: str,
) -> MaterializedTabularDataset | None:
    """Return the materialized dataset for a source_id, if present."""
    for dataset in result.datasets:
        if dataset.source_id == source_id:
            return dataset
    return None


def get_materialized_datasets_by_role_hint(
    result: UploadedCSVMaterializationResult,
    role_hint: str,
) -> list[MaterializedTabularDataset]:
    """Return datasets whose declared_role_hint matches exactly (string lookup only)."""
    return [
        dataset
        for dataset in result.datasets
        if dataset.declared_role_hint == role_hint
    ]


def _materialize_single_source(
    source: UploadedCSVSource,
    request: UploadedCSVMaterializationRequest,
) -> tuple[
    UploadedCSVMaterializationStatus,
    UploadedCSVInspection,
    MaterializedTabularDataset | None,
    list[UploadedCSVIssueCode],
    list[str],
]:
    issues: list[UploadedCSVIssueCode] = []
    warnings: list[str] = []

    if not source.path.strip():
        inspection = _empty_inspection(source)
        issues.append(UploadedCSVIssueCode.MISSING_UPLOAD)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD,
            inspection,
            None,
            issues,
            warnings,
        )

    if str(source.source_type) not in {item.value for item in _ALLOWED_SOURCE_TYPES}:
        inspection = UploadedCSVInspection(
            source_id=source.source_id,
            source_type=UploadedCSVSourceType.UPLOADED_CSV,
            original_filename=source.original_filename,
            declared_role_hint=source.declared_role_hint,
            issues=[UploadedCSVIssueCode.UNSUPPORTED_SOURCE_TYPE],
            lineage={
                **dict(source.lineage),
                "invalid_source_type": str(source.source_type),
            },
        )
        issues.append(UploadedCSVIssueCode.UNSUPPORTED_SOURCE_TYPE)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_SOURCE_TYPE,
            inspection,
            None,
            issues,
            warnings,
        )

    file_path = Path(source.path)
    if file_path.suffix.lower() not in ALLOWED_FILE_EXTENSIONS:
        inspection = _empty_inspection(source)
        issues.append(UploadedCSVIssueCode.UNSUPPORTED_FILE_TYPE)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_FILE_TYPE,
            inspection,
            None,
            issues,
            warnings,
        )

    if not file_path.is_file():
        inspection = _empty_inspection(source)
        issues.append(UploadedCSVIssueCode.MISSING_UPLOAD)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD,
            inspection,
            None,
            issues,
            warnings,
        )

    file_size_bytes = file_path.stat().st_size
    if file_size_bytes > request.max_file_size_bytes:
        inspection = UploadedCSVInspection(
            source_id=source.source_id,
            source_type=source.source_type,
            original_filename=source.original_filename,
            declared_role_hint=source.declared_role_hint,
            file_size_bytes=file_size_bytes,
            issues=[UploadedCSVIssueCode.FILE_TOO_LARGE],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(UploadedCSVIssueCode.FILE_TOO_LARGE)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_FILE_TOO_LARGE,
            inspection,
            None,
            issues,
            warnings,
        )

    try:
        raw_columns = _read_csv_header_columns(file_path)
    except (OSError, UnicodeDecodeError):
        inspection = UploadedCSVInspection(
            source_id=source.source_id,
            source_type=source.source_type,
            original_filename=source.original_filename,
            declared_role_hint=source.declared_role_hint,
            file_size_bytes=file_size_bytes,
            issues=[UploadedCSVIssueCode.MALFORMED_CSV],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(UploadedCSVIssueCode.MALFORMED_CSV)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_MALFORMED_CSV,
            inspection,
            None,
            issues,
            warnings,
        )

    normalized_header_columns, column_normalized = _normalize_columns(raw_columns)
    duplicate_columns = _duplicate_normalized_columns(normalized_header_columns)
    if duplicate_columns:
        inspection = UploadedCSVInspection(
            source_id=source.source_id,
            source_type=source.source_type,
            original_filename=source.original_filename,
            declared_role_hint=source.declared_role_hint,
            columns=raw_columns,
            normalized_columns=normalized_header_columns,
            file_size_bytes=file_size_bytes,
            issues=[UploadedCSVIssueCode.DUPLICATE_COLUMN_NAME],
            warnings=[f"Duplicate normalized column names: {', '.join(duplicate_columns)}"],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(UploadedCSVIssueCode.DUPLICATE_COLUMN_NAME)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_MALFORMED_CSV,
            inspection,
            None,
            issues,
            warnings,
        )

    try:
        dataframe = pd.read_csv(file_path)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError):
        inspection = UploadedCSVInspection(
            source_id=source.source_id,
            source_type=source.source_type,
            original_filename=source.original_filename,
            declared_role_hint=source.declared_role_hint,
            file_size_bytes=file_size_bytes,
            issues=[UploadedCSVIssueCode.MALFORMED_CSV],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(UploadedCSVIssueCode.MALFORMED_CSV)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_MALFORMED_CSV,
            inspection,
            None,
            issues,
            warnings,
        )

    raw_columns = [str(column) for column in dataframe.columns]
    normalized_columns = normalized_header_columns
    if column_normalized:
        issues.append(UploadedCSVIssueCode.COLUMN_NAME_NORMALIZED)
        warnings.append("Column names normalized by stripping whitespace.")
        dataframe.columns = normalized_columns

    row_count = len(dataframe)
    column_count = len(normalized_columns)

    if column_count == 0:
        inspection = UploadedCSVInspection(
            source_id=source.source_id,
            source_type=source.source_type,
            original_filename=source.original_filename,
            declared_role_hint=source.declared_role_hint,
            columns=raw_columns,
            normalized_columns=normalized_columns,
            row_count=row_count,
            column_count=column_count,
            file_size_bytes=file_size_bytes,
            issues=[UploadedCSVIssueCode.EMPTY_FILE],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(UploadedCSVIssueCode.EMPTY_FILE)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_EMPTY_FILE,
            inspection,
            None,
            issues,
            warnings,
        )

    if row_count == 0:
        inspection = UploadedCSVInspection(
            source_id=source.source_id,
            source_type=source.source_type,
            original_filename=source.original_filename,
            declared_role_hint=source.declared_role_hint,
            columns=raw_columns,
            normalized_columns=normalized_columns,
            row_count=row_count,
            column_count=column_count,
            file_size_bytes=file_size_bytes,
            issues=[UploadedCSVIssueCode.HEADER_ONLY_FILE],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(UploadedCSVIssueCode.HEADER_ONLY_FILE)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_HEADER_ONLY_FILE,
            inspection,
            None,
            issues,
            warnings,
        )

    if row_count > request.max_rows:
        inspection = UploadedCSVInspection(
            source_id=source.source_id,
            source_type=source.source_type,
            original_filename=source.original_filename,
            declared_role_hint=source.declared_role_hint,
            columns=raw_columns,
            normalized_columns=normalized_columns,
            row_count=row_count,
            column_count=column_count,
            file_size_bytes=file_size_bytes,
            issues=[UploadedCSVIssueCode.ROW_LIMIT_EXCEEDED],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(UploadedCSVIssueCode.ROW_LIMIT_EXCEEDED)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_ROW_LIMIT_EXCEEDED,
            inspection,
            None,
            issues,
            warnings,
        )

    missing_required = [
        column for column in source.required_columns if column not in normalized_columns
    ]
    if missing_required:
        inspection = UploadedCSVInspection(
            source_id=source.source_id,
            source_type=source.source_type,
            original_filename=source.original_filename,
            declared_role_hint=source.declared_role_hint,
            columns=raw_columns,
            normalized_columns=normalized_columns,
            row_count=row_count,
            column_count=column_count,
            file_size_bytes=file_size_bytes,
            issues=[UploadedCSVIssueCode.MISSING_REQUIRED_COLUMNS],
            warnings=[f"Missing required columns: {', '.join(missing_required)}"],
            lineage=_base_lineage(source, file_path, file_size_bytes),
        )
        issues.append(UploadedCSVIssueCode.MISSING_REQUIRED_COLUMNS)
        return (
            UploadedCSVMaterializationStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
            inspection,
            None,
            issues,
            warnings,
        )

    if source.required_columns:
        issues.append(UploadedCSVIssueCode.REQUIRED_COLUMNS_VALIDATED)

    source_lineage = _base_lineage(source, file_path, file_size_bytes)
    source_lineage.update(
        {
            "row_count": str(row_count),
            "column_count": str(column_count),
            "columns": ",".join(normalized_columns),
            **source.lineage,
        }
    )
    inspection = UploadedCSVInspection(
        source_id=source.source_id,
        source_type=source.source_type,
        original_filename=source.original_filename,
        declared_role_hint=source.declared_role_hint,
        columns=raw_columns,
        normalized_columns=normalized_columns,
        row_count=row_count,
        column_count=column_count,
        file_size_bytes=file_size_bytes,
        issues=list(issues),
        warnings=list(warnings),
        lineage=dict(source_lineage),
    )
    dataset = MaterializedTabularDataset(
        dataset_id=f"materialized:{source.source_id}",
        source_id=source.source_id,
        source_type=source.source_type,
        declared_role_hint=source.declared_role_hint,
        dataframe=dataframe,
        columns=raw_columns,
        normalized_columns=normalized_columns,
        row_count=row_count,
        column_count=column_count,
        lineage=dict(source_lineage),
    )
    issues.append(UploadedCSVIssueCode.DATAFRAME_MATERIALIZED)
    return (
        UploadedCSVMaterializationStatus.MATERIALIZED,
        inspection,
        dataset,
        issues,
        warnings,
    )


def _empty_inspection(source: UploadedCSVSource) -> UploadedCSVInspection:
    return UploadedCSVInspection(
        source_id=source.source_id,
        source_type=source.source_type,
        original_filename=source.original_filename,
        declared_role_hint=source.declared_role_hint,
        lineage=dict(source.lineage),
    )


def _base_lineage(
    source: UploadedCSVSource,
    file_path: Path,
    file_size_bytes: int,
) -> dict[str, str]:
    return {
        "source_id": source.source_id,
        "uploaded_path": str(file_path),
        "original_filename": source.original_filename,
        "source_type": str(source.source_type),
        "declared_role_hint": source.declared_role_hint or "",
        "file_size_bytes": str(file_size_bytes),
    }


def _read_csv_header_columns(file_path: Path) -> list[str]:
    with file_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header_row = next(reader, [])
    return [str(column) for column in header_row]


def _normalize_columns(columns: list[str]) -> tuple[list[str], bool]:
    normalized = [column.strip() for column in columns]
    return normalized, normalized != columns


def _duplicate_normalized_columns(columns: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for column in columns:
        if column in seen and column not in duplicates:
            duplicates.append(column)
        seen.add(column)
    return duplicates


def _blocked(
    request_id: str,
    status: UploadedCSVMaterializationStatus,
    issues: list[UploadedCSVIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> UploadedCSVMaterializationResult:
    return UploadedCSVMaterializationResult(
        request_id=request_id,
        status=status,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[UploadedCSVIssueCode],
) -> list[UploadedCSVIssueCode]:
    seen: set[UploadedCSVIssueCode] = set()
    ordered: list[UploadedCSVIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
