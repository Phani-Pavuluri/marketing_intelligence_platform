"""Tests for shared uploaded CSV materialization contracts."""

from __future__ import annotations

from pathlib import Path

import pandas as pd  # type: ignore[import-untyped]

from mip.contracts import (
    ALLOWED_FILE_EXTENSIONS,
    DEFAULT_MAX_UPLOAD_FILE_SIZE_BYTES,
    DEFAULT_MAX_UPLOAD_ROWS,
    RECOMMENDED_NEXT_GEOX_UPLOADED_CSV_ADAPTER_ARTIFACT,
    MaterializedTabularDataset,
    UploadedCSVMaterializationRequest,
    UploadedCSVMaterializationResult,
    UploadedCSVMaterializationStatus,
    UploadedCSVPolicy,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.contracts.uploaded_csv_materialization import UploadedCSVInspection

_FORBIDDEN_GEOX_ROLES = (
    "KPI_PANEL",
    "SPEND_PANEL",
    "ASSIGNMENT_TABLE",
    "EXPERIMENT_METADATA",
)
_FORBIDDEN_PLANNING_ROLES = (
    "historical_spend",
    "budget_constraints",
    "channel_taxonomy",
    "calibration_priors",
)
_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi", "roas")
_REQUIRED_STATUSES = {
    UploadedCSVMaterializationStatus.MATERIALIZED,
    UploadedCSVMaterializationStatus.MATERIALIZED_WITH_WARNINGS,
    UploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD,
    UploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_FILE_TYPE,
    UploadedCSVMaterializationStatus.BLOCKED_FILE_TOO_LARGE,
    UploadedCSVMaterializationStatus.BLOCKED_ROW_LIMIT_EXCEEDED,
    UploadedCSVMaterializationStatus.BLOCKED_EMPTY_FILE,
    UploadedCSVMaterializationStatus.BLOCKED_HEADER_ONLY_FILE,
    UploadedCSVMaterializationStatus.BLOCKED_MALFORMED_CSV,
    UploadedCSVMaterializationStatus.BLOCKED_MISSING_REQUIRED_COLUMNS,
    UploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_SOURCE_TYPE,
}


def test_required_enums_exist() -> None:
    assert _REQUIRED_STATUSES.issubset(set(UploadedCSVMaterializationStatus))
    assert UploadedCSVSourceType.UPLOADED_CSV in UploadedCSVSourceType
    assert UploadedCSVPolicy.STRICT_UPLOADED_CSV_ONLY in UploadedCSVPolicy


def test_no_geox_role_enum_values_in_shared_contracts() -> None:
    contract_source = Path("src/mip/contracts/uploaded_csv_materialization.py").read_text(
        encoding="utf-8"
    )
    for role in _FORBIDDEN_GEOX_ROLES:
        assert role not in contract_source


def test_no_planning_role_enum_values_in_shared_contracts() -> None:
    contract_source = Path("src/mip/contracts/uploaded_csv_materialization.py").read_text(
        encoding="utf-8"
    )
    for role in _FORBIDDEN_PLANNING_ROLES:
        assert role not in contract_source


def test_models_serialize() -> None:
    request = UploadedCSVMaterializationRequest(request_id="req-1")
    assert request.policy == UploadedCSVPolicy.STRICT_UPLOADED_CSV_ONLY
    assert request.max_file_size_bytes == DEFAULT_MAX_UPLOAD_FILE_SIZE_BYTES
    assert request.max_rows == DEFAULT_MAX_UPLOAD_ROWS
    result = UploadedCSVMaterializationResult(
        request_id="req-1",
        status=UploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD,
    )
    assert result.datasets == []


def test_materialized_tabular_dataset_with_dataframe() -> None:
    dataset = MaterializedTabularDataset(
        dataset_id="dataset-1",
        source_id="source-1",
        source_type=UploadedCSVSourceType.UPLOADED_CSV,
        dataframe=pd.DataFrame({"date": ["2026-01-06"], "unit": ["501"], "value": [1]}),
        columns=["date", "unit", "value"],
        normalized_columns=["date", "unit", "value"],
        row_count=1,
        column_count=3,
    )
    assert dataset.row_count == 1


def test_result_no_top_level_metric_fields() -> None:
    schema = UploadedCSVMaterializationResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_declared_role_hint_is_optional_string() -> None:
    source = UploadedCSVSource(
        source_id="source-1",
        path="/tmp/table.csv",
        original_filename="table.csv",
        declared_role_hint="lane_adapter_hint",
    )
    assert source.declared_role_hint == "lane_adapter_hint"


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_GEOX_UPLOADED_CSV_ADAPTER_ARTIFACT == (
        "MIP_GEOX_READOUT_UPLOADED_CSV_ADAPTER_001"
    )
    assert ALLOWED_FILE_EXTENSIONS == (".csv",)


def test_inspection_tracks_normalized_columns() -> None:
    inspection = UploadedCSVInspection(
        source_id="source-1",
        source_type=UploadedCSVSourceType.UPLOADED_CSV,
        original_filename="table.csv",
        columns=["date ", "unit"],
        normalized_columns=["date", "unit"],
        row_count=2,
        column_count=2,
        file_size_bytes=64,
    )
    assert inspection.normalized_columns == ["date", "unit"]
