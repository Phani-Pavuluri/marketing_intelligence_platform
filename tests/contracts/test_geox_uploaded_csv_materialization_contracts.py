"""Tests for GeoX uploaded CSV materialization contracts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd  # type: ignore[import-untyped]

from mip.contracts import (
    DEFAULT_MAX_UPLOAD_FILE_SIZE_BYTES,
    DEFAULT_MAX_UPLOAD_ROWS,
    RECOMMENDED_NEXT_UPLOADED_CSV_RUNTIME_BRIDGE_ARTIFACT,
    GeoXUploadedCSVDataset,
    GeoXUploadedCSVIssueCode,
    GeoXUploadedCSVMaterializationRequest,
    GeoXUploadedCSVMaterializationResult,
    GeoXUploadedCSVMaterializationStatus,
    GeoXUploadedCSVPolicy,
    GeoXUploadedCSVRole,
    GeoXUploadedCSVSource,
)
from mip.contracts.geox_uploaded_csv_materialization import GeoXUploadedCSVInspection

_REQUIRED_STATUSES = {
    GeoXUploadedCSVMaterializationStatus.MATERIALIZED,
    GeoXUploadedCSVMaterializationStatus.MATERIALIZED_WITH_WARNINGS,
    GeoXUploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD,
    GeoXUploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_FILE_TYPE,
    GeoXUploadedCSVMaterializationStatus.BLOCKED_FILE_TOO_LARGE,
    GeoXUploadedCSVMaterializationStatus.BLOCKED_ROW_LIMIT_EXCEEDED,
    GeoXUploadedCSVMaterializationStatus.BLOCKED_EMPTY_FILE,
    GeoXUploadedCSVMaterializationStatus.BLOCKED_MALFORMED_CSV,
    GeoXUploadedCSVMaterializationStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
    GeoXUploadedCSVMaterializationStatus.BLOCKED_AMBIGUOUS_ROLE,
    GeoXUploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_SOURCE_TYPE,
}

_REQUIRED_ISSUES = {
    GeoXUploadedCSVIssueCode.MISSING_UPLOAD,
    GeoXUploadedCSVIssueCode.UNSUPPORTED_FILE_TYPE,
    GeoXUploadedCSVIssueCode.FILE_TOO_LARGE,
    GeoXUploadedCSVIssueCode.ROW_LIMIT_EXCEEDED,
    GeoXUploadedCSVIssueCode.EMPTY_FILE,
    GeoXUploadedCSVIssueCode.MALFORMED_CSV,
    GeoXUploadedCSVIssueCode.MISSING_REQUIRED_COLUMNS,
    GeoXUploadedCSVIssueCode.AMBIGUOUS_ROLE,
    GeoXUploadedCSVIssueCode.UNSUPPORTED_SOURCE_TYPE,
    GeoXUploadedCSVIssueCode.DUPLICATE_ROLE,
    GeoXUploadedCSVIssueCode.HEADER_ONLY_FILE,
    GeoXUploadedCSVIssueCode.COLUMN_NAME_NORMALIZED,
    GeoXUploadedCSVIssueCode.OPTIONAL_METADATA_MISSING,
    GeoXUploadedCSVIssueCode.LINEAGE_RECORDED,
}

_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi", "roas")
_FORBIDDEN_RUNTIME = (
    "PostTestSpendInput",
    "PostTestSpendEvidence",
    "build_post_test_spend_evidence",
    "build_trusted_readout_spend_handoff",
)


def test_required_enums_exist() -> None:
    assert _REQUIRED_STATUSES.issubset(set(GeoXUploadedCSVMaterializationStatus))
    assert _REQUIRED_ISSUES.issubset(set(GeoXUploadedCSVIssueCode))
    assert GeoXUploadedCSVRole.KPI_PANEL in GeoXUploadedCSVRole
    assert GeoXUploadedCSVPolicy.STRICT_UPLOADED_CSV_ONLY in GeoXUploadedCSVPolicy


def test_models_serialize() -> None:
    request = GeoXUploadedCSVMaterializationRequest(request_id="req-1")
    assert request.policy == GeoXUploadedCSVPolicy.STRICT_UPLOADED_CSV_ONLY
    assert request.max_file_size_bytes == DEFAULT_MAX_UPLOAD_FILE_SIZE_BYTES
    assert request.max_rows == DEFAULT_MAX_UPLOAD_ROWS
    result = GeoXUploadedCSVMaterializationResult(
        request_id="req-1",
        status=GeoXUploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD,
    )
    assert result.datasets == []


def test_dataframe_bearing_dataset_can_be_created() -> None:
    dataset = GeoXUploadedCSVDataset(
        source_id="kpi-1",
        role=GeoXUploadedCSVRole.KPI_PANEL,
        dataframe=pd.DataFrame({"date": ["2026-01-06"], "dma": ["501"], "conversions": [1]}),
        columns=["date", "dma", "conversions"],
        row_count=1,
        column_count=3,
    )
    assert dataset.row_count == 1


def test_result_no_top_level_metric_fields() -> None:
    schema = GeoXUploadedCSVMaterializationResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_no_runtime_fields_in_contract_module() -> None:
    source = Path("src/mip/contracts/geox_uploaded_csv_materialization.py").read_text(
        encoding="utf-8"
    )
    for token in _FORBIDDEN_RUNTIME:
        assert token not in source


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_UPLOADED_CSV_RUNTIME_BRIDGE_ARTIFACT == (
        "MIP_GEOX_READOUT_UPLOADED_CSV_RUNTIME_BRIDGE_001"
    )


def test_inspection_model_fields() -> None:
    inspection = GeoXUploadedCSVInspection(
        source_id="src-1",
        role=GeoXUploadedCSVRole.SPEND_PANEL,
        columns=["date", "dma", "spend"],
        row_count=4,
        column_count=3,
        file_size_bytes=128,
    )
    assert inspection.column_count == 3


def test_uploaded_source_defaults() -> None:
    source = GeoXUploadedCSVSource(
        source_id="src-1",
        role=GeoXUploadedCSVRole.KPI_PANEL,
        path="/tmp/kpi.csv",
        original_filename="kpi.csv",
    )
    assert source.source_type == "uploaded_csv"
