"""Tests for shared uploaded CSV materialization workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from mip.contracts.geox_readout_input_resolution import (
    DatasetSemanticType,
    DatasetSourceType,
)
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import DataSourceMode, DataSourceType
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVIssueCode,
    UploadedCSVMaterializationRequest,
    UploadedCSVMaterializationStatus,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.workflows.uploaded_csv_materialization import (
    build_data_source_ref_from_uploaded_csv_inspection,
    build_dataset_reference_from_uploaded_csv_inspection,
    get_materialized_dataset_by_source_id,
    get_materialized_datasets_by_role_hint,
    materialize_uploaded_csvs,
)

_FIXTURE_ROOT = Path("examples/fixtures/uploaded_csv_materialization")
_VALID_PATH = str(_FIXTURE_ROOT / "valid_uploaded_table.csv")
_SPACED_HEADERS_PATH = str(_FIXTURE_ROOT / "valid_uploaded_table_with_spaced_headers.csv")
_HEADER_ONLY_PATH = str(_FIXTURE_ROOT / "header_only_upload.csv")
_MALFORMED_PATH = str(_FIXTURE_ROOT / "malformed_upload.csv")
_MISSING_COLS_PATH = str(_FIXTURE_ROOT / "missing_required_columns.csv")
_DUPLICATE_COLS_PATH = str(_FIXTURE_ROOT / "duplicate_normalized_columns.csv")
_WORKFLOW_SOURCE = Path("src/mip/workflows/uploaded_csv_materialization.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/uploaded_csv_materialization.py")
_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi_value", "roas_value")


def _source(
    *,
    source_id: str = "source-1",
    path: str = _VALID_PATH,
    required_columns: list[str] | None = None,
    declared_role_hint: str | None = None,
    source_type: UploadedCSVSourceType = UploadedCSVSourceType.UPLOADED_CSV,
) -> UploadedCSVSource:
    return UploadedCSVSource(
        source_id=source_id,
        source_type=source_type,
        path=path,
        original_filename=Path(path).name,
        required_columns=required_columns or [],
        declared_role_hint=declared_role_hint,
    )


def test_successful_materialization() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="ok-1",
            sources=[_source(required_columns=["date", "unit", "value"])],
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.MATERIALIZED
    assert len(result.datasets) == 1
    assert len(result.inspections) == 1
    dataset = result.datasets[0]
    assert dataset.row_count >= 2
    assert dataset.column_count == 3
    assert dataset.lineage["uploaded_path"] == _VALID_PATH
    assert UploadedCSVIssueCode.DATAFRAME_MATERIALIZED in result.issues
    assert UploadedCSVIssueCode.LINEAGE_RECORDED in result.issues


def test_materialized_with_warnings_for_spaced_headers() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="warn-1",
            sources=[
                _source(
                    path=_SPACED_HEADERS_PATH,
                    required_columns=["date", "unit", "value"],
                )
            ],
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.MATERIALIZED_WITH_WARNINGS
    assert UploadedCSVIssueCode.COLUMN_NAME_NORMALIZED in result.issues
    inspection = result.inspections[0]
    assert inspection.normalized_columns == ["date", "unit", "value"]


def test_missing_upload_blocked() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(request_id="missing", sources=[])
    )
    assert result.status == UploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD


def test_missing_file_path_blocked() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="missing-file",
            sources=[_source(path="/tmp/does-not-exist.csv")],
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD


def test_unsupported_file_type_blocked(tmp_path: Path) -> None:
    bad_file = tmp_path / "notes.txt"
    bad_file.write_text("not csv", encoding="utf-8")
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="bad-ext",
            sources=[_source(path=str(bad_file))],
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_FILE_TYPE


def test_unsupported_source_type_blocked() -> None:
    source = UploadedCSVSource.model_construct(
        source_id="bad",
        source_type="warehouse_table",
        path=_VALID_PATH,
        original_filename="valid_uploaded_table.csv",
    )
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="bad-source-type",
            sources=[source],
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_SOURCE_TYPE


def test_file_too_large_blocked(tmp_path: Path) -> None:
    csv_path = tmp_path / "small.csv"
    csv_path.write_text("date,unit,value\n2026-01-06,501,1\n", encoding="utf-8")
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="too-large",
            sources=[_source(path=str(csv_path))],
            max_file_size_bytes=10,
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.BLOCKED_FILE_TOO_LARGE


def test_header_only_csv_blocked() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="header-only",
            sources=[_source(path=_HEADER_ONLY_PATH)],
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.BLOCKED_HEADER_ONLY_FILE
    assert UploadedCSVIssueCode.HEADER_ONLY_FILE in result.issues


def test_empty_csv_blocked(tmp_path: Path) -> None:
    empty_path = tmp_path / "empty.csv"
    empty_path.write_text("", encoding="utf-8")
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="empty",
            sources=[_source(path=str(empty_path))],
        )
    )
    assert result.status in {
        UploadedCSVMaterializationStatus.BLOCKED_EMPTY_FILE,
        UploadedCSVMaterializationStatus.BLOCKED_MALFORMED_CSV,
    }


def test_malformed_csv_blocked() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="malformed",
            sources=[_source(path=_MALFORMED_PATH)],
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.BLOCKED_MALFORMED_CSV


def test_required_columns_missing_blocked() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="missing-cols",
            sources=[
                _source(
                    path=_MISSING_COLS_PATH,
                    required_columns=["date", "unit", "value"],
                )
            ],
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.BLOCKED_MISSING_REQUIRED_COLUMNS


def test_duplicate_normalized_columns_blocked() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="duplicate-cols",
            sources=[_source(path=_DUPLICATE_COLS_PATH)],
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.BLOCKED_MALFORMED_CSV
    assert UploadedCSVIssueCode.DUPLICATE_COLUMN_NAME in result.issues


def test_row_limit_exceeded_blocked(tmp_path: Path) -> None:
    rows = ["date,unit,value"] + [f"2026-01-06,{idx},1" for idx in range(5)]
    csv_path = tmp_path / "many_rows.csv"
    csv_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="row-limit",
            sources=[_source(path=str(csv_path))],
            max_rows=3,
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.BLOCKED_ROW_LIMIT_EXCEEDED


def test_dataset_reference_compatibility_helper() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="ds-ref",
            sources=[_source(declared_role_hint="adapter_hint")],
        )
    )
    source = _source(declared_role_hint="adapter_hint")
    inspection = result.inspections[0]
    dataset_ref = build_dataset_reference_from_uploaded_csv_inspection(source, inspection)
    assert dataset_ref.source_type == DatasetSourceType.UPLOADED_CSV
    assert dataset_ref.semantic_type == DatasetSemanticType.UNKNOWN_DATASET
    assert dataset_ref.declared_or_detected_columns == inspection.normalized_columns
    assert dataset_ref.lineage["declared_role_hint"] == "adapter_hint"


def test_data_source_ref_compatibility_helper() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="intake-ref",
            sources=[_source(declared_role_hint="planning_hint")],
        )
    )
    source = _source(declared_role_hint="planning_hint")
    inspection = result.inspections[0]
    created_at = datetime(2026, 1, 6, tzinfo=UTC)
    data_source_ref = build_data_source_ref_from_uploaded_csv_inspection(
        source,
        inspection,
        asset_type=DataAssetType.MEDIA_SPEND_DATA,
        created_at=created_at,
    )
    assert data_source_ref.source_type == DataSourceType.FILE
    assert data_source_ref.source_mode == DataSourceMode.LOCAL_FILE_PATH_MANIFEST
    assert data_source_ref.declared_scope["declared_role_hint"] == "planning_hint"


def test_role_hint_lookup_without_enum_interpretation() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="role-hint",
            sources=[
                _source(source_id="a", declared_role_hint="lane_a"),
                _source(source_id="b", declared_role_hint="lane_b"),
            ],
        )
    )
    lane_a = get_materialized_datasets_by_role_hint(result, "lane_a")
    assert len(lane_a) == 1
    assert lane_a[0].source_id == "a"
    assert get_materialized_dataset_by_source_id(result, "b") is not None


def test_no_panel_exp_import_or_call() -> None:
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "import panel_exp" not in source
        assert "from panel_exp" not in source


def test_no_geox_uploaded_csv_materialization_import() -> None:
    workflow_source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")
    assert "geox_uploaded_csv_materialization" not in workflow_source


def test_no_metric_recomputation_fields() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(request_id="metrics", sources=[_source()])
    )
    schema = result.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties
