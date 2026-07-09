"""Tests for GeoX uploaded CSV materialization workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.geox_readout_input_resolution import (
    DatasetSemanticType,
    DatasetSourceType,
)
from mip.contracts.geox_readout_source_inspection import SourceInspectionStatus
from mip.contracts.geox_uploaded_csv_materialization import (
    GeoXUploadedCSVIssueCode,
    GeoXUploadedCSVMaterializationRequest,
    GeoXUploadedCSVMaterializationStatus,
    GeoXUploadedCSVRole,
    GeoXUploadedCSVSource,
)
from mip.workflows.geox_readout_source_inspection import inspect_dataset_reference
from mip.workflows.geox_uploaded_csv_materialization import (
    build_dataset_reference_from_uploaded_csv_inspection,
    build_materialized_input_availability_from_uploaded_csv_result,
    materialize_geox_uploaded_csvs,
)

_FIXTURE_ROOT = Path("examples/fixtures/geox_uploaded_csv_materialization")
_KPI_PATH = str(_FIXTURE_ROOT / "uploaded_kpi_panel.csv")
_SPEND_PATH = str(_FIXTURE_ROOT / "uploaded_spend_panel.csv")
_ASSIGNMENT_PATH = str(_FIXTURE_ROOT / "uploaded_assignment_table.csv")
_METADATA_PATH = str(_FIXTURE_ROOT / "uploaded_experiment_metadata.csv")
_MALFORMED_PATH = str(_FIXTURE_ROOT / "malformed_upload.csv")
_HEADER_ONLY_PATH = str(_FIXTURE_ROOT / "header_only_upload.csv")
_WORKFLOW_SOURCE = Path("src/mip/workflows/geox_uploaded_csv_materialization.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/geox_uploaded_csv_materialization.py")
_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi_value", "roas_value")


def _source(
    *,
    source_id: str,
    role: GeoXUploadedCSVRole,
    path: str,
    required_columns: list[str] | None = None,
    source_type: str = "uploaded_csv",
) -> GeoXUploadedCSVSource:
    return GeoXUploadedCSVSource(
        source_id=source_id,
        role=role,
        path=path,
        original_filename=Path(path).name,
        source_type=source_type,
        required_columns=required_columns or [],
    )


def _core_sources(*, include_metadata: bool = True) -> list[GeoXUploadedCSVSource]:
    sources = [
        _source(
            source_id="uploaded-kpi",
            role=GeoXUploadedCSVRole.KPI_PANEL,
            path=_KPI_PATH,
            required_columns=["date", "dma", "conversions"],
        ),
        _source(
            source_id="uploaded-spend",
            role=GeoXUploadedCSVRole.SPEND_PANEL,
            path=_SPEND_PATH,
            required_columns=["date", "dma", "spend", "currency"],
        ),
        _source(
            source_id="uploaded-assignment",
            role=GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
            path=_ASSIGNMENT_PATH,
            required_columns=["dma", "cell", "treatment"],
        ),
    ]
    if include_metadata:
        sources.append(
            _source(
                source_id="uploaded-metadata",
                role=GeoXUploadedCSVRole.EXPERIMENT_METADATA,
                path=_METADATA_PATH,
                required_columns=["experiment_id", "test_start_date", "test_end_date"],
            )
        )
    return sources


def test_successful_materialization_of_core_uploaded_csvs() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="upload-1",
            sources=_core_sources(),
        )
    )
    assert result.status in {
        GeoXUploadedCSVMaterializationStatus.MATERIALIZED,
        GeoXUploadedCSVMaterializationStatus.MATERIALIZED_WITH_WARNINGS,
    }
    roles = {dataset.role for dataset in result.datasets}
    assert GeoXUploadedCSVRole.KPI_PANEL in roles
    assert GeoXUploadedCSVRole.SPEND_PANEL in roles
    assert GeoXUploadedCSVRole.ASSIGNMENT_TABLE in roles
    spend = next(d for d in result.datasets if d.role == GeoXUploadedCSVRole.SPEND_PANEL)
    assert spend.row_count >= 4
    assert spend.column_count >= 4
    assert spend.lineage["uploaded_path"] == _SPEND_PATH
    assert GeoXUploadedCSVIssueCode.LINEAGE_RECORDED in result.issues


def test_optional_metadata_missing_warning_only() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="upload-no-metadata",
            sources=_core_sources(include_metadata=False),
        )
    )
    assert result.status == GeoXUploadedCSVMaterializationStatus.MATERIALIZED_WITH_WARNINGS
    assert GeoXUploadedCSVIssueCode.OPTIONAL_METADATA_MISSING in result.issues
    assert any("metadata" in warning.lower() for warning in result.warnings)


def test_missing_upload_blocked() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(request_id="missing", sources=[])
    )
    assert result.status == GeoXUploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD
    assert GeoXUploadedCSVIssueCode.MISSING_UPLOAD in result.issues


def test_missing_file_path_blocked() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="missing-file",
            sources=[
                _source(
                    source_id="missing",
                    role=GeoXUploadedCSVRole.KPI_PANEL,
                    path="/tmp/does-not-exist.csv",
                )
            ],
        )
    )
    assert result.status == GeoXUploadedCSVMaterializationStatus.BLOCKED_MISSING_UPLOAD


def test_unsupported_file_type_blocked(tmp_path: Path) -> None:
    bad_file = tmp_path / "notes.txt"
    bad_file.write_text("not csv", encoding="utf-8")
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="bad-ext",
            sources=[
                _source(
                    source_id="bad-ext",
                    role=GeoXUploadedCSVRole.KPI_PANEL,
                    path=str(bad_file),
                )
            ],
        )
    )
    assert result.status == GeoXUploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_FILE_TYPE
    assert GeoXUploadedCSVIssueCode.UNSUPPORTED_FILE_TYPE in result.issues


def test_unsupported_source_type_blocked() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="bad-source-type",
            sources=[
                _source(
                    source_id="warehouse",
                    role=GeoXUploadedCSVRole.KPI_PANEL,
                    path=_KPI_PATH,
                    source_type="warehouse_table",
                )
            ],
        )
    )
    assert result.status == GeoXUploadedCSVMaterializationStatus.BLOCKED_UNSUPPORTED_SOURCE_TYPE
    assert GeoXUploadedCSVIssueCode.UNSUPPORTED_SOURCE_TYPE in result.issues


def test_file_too_large_blocked(tmp_path: Path) -> None:
    large_file = tmp_path / "large.csv"
    large_file.write_text("date,dma,conversions\n2026-01-06,501,1\n", encoding="utf-8")
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="too-large",
            sources=[
                _source(
                    source_id="large",
                    role=GeoXUploadedCSVRole.KPI_PANEL,
                    path=str(large_file),
                )
            ],
            max_file_size_bytes=10,
        )
    )
    assert result.status == GeoXUploadedCSVMaterializationStatus.BLOCKED_FILE_TOO_LARGE
    assert GeoXUploadedCSVIssueCode.FILE_TOO_LARGE in result.issues


def test_header_only_csv_blocked() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="header-only",
            sources=[
                _source(
                    source_id="header-only",
                    role=GeoXUploadedCSVRole.KPI_PANEL,
                    path=_HEADER_ONLY_PATH,
                )
            ],
        )
    )
    assert result.status == GeoXUploadedCSVMaterializationStatus.BLOCKED_EMPTY_FILE
    assert GeoXUploadedCSVIssueCode.HEADER_ONLY_FILE in result.issues


def test_malformed_csv_blocked() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="malformed",
            sources=[
                _source(
                    source_id="malformed",
                    role=GeoXUploadedCSVRole.SPEND_PANEL,
                    path=_MALFORMED_PATH,
                )
            ],
        )
    )
    assert result.status == GeoXUploadedCSVMaterializationStatus.BLOCKED_MALFORMED_CSV
    assert GeoXUploadedCSVIssueCode.MALFORMED_CSV in result.issues


def test_required_columns_missing_blocked() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="missing-cols",
            sources=[
                _source(
                    source_id="kpi",
                    role=GeoXUploadedCSVRole.KPI_PANEL,
                    path=_KPI_PATH,
                    required_columns=["date", "dma", "missing_metric"],
                )
            ],
        )
    )
    assert result.status == (
        GeoXUploadedCSVMaterializationStatus.BLOCKED_MISSING_REQUIRED_COLUMNS
    )
    assert GeoXUploadedCSVIssueCode.MISSING_REQUIRED_COLUMNS in result.issues


def test_duplicate_role_blocked() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="duplicate-role",
            sources=[
                _source(
                    source_id="kpi-1",
                    role=GeoXUploadedCSVRole.KPI_PANEL,
                    path=_KPI_PATH,
                ),
                _source(
                    source_id="kpi-2",
                    role=GeoXUploadedCSVRole.KPI_PANEL,
                    path=_KPI_PATH,
                ),
            ],
        )
    )
    assert result.status == GeoXUploadedCSVMaterializationStatus.BLOCKED_AMBIGUOUS_ROLE
    assert GeoXUploadedCSVIssueCode.DUPLICATE_ROLE in result.issues


def test_unknown_role_blocked() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="unknown-role",
            sources=[
                _source(
                    source_id="unknown",
                    role=GeoXUploadedCSVRole.UNKNOWN,
                    path=_KPI_PATH,
                )
            ],
        )
    )
    assert result.status == GeoXUploadedCSVMaterializationStatus.BLOCKED_AMBIGUOUS_ROLE
    assert GeoXUploadedCSVIssueCode.AMBIGUOUS_ROLE in result.issues


def test_row_limit_exceeded_blocked(tmp_path: Path) -> None:
    rows = ["date,dma,conversions"] + [f"2026-01-06,{idx},1" for idx in range(5)]
    csv_path = tmp_path / "many_rows.csv"
    csv_path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="row-limit",
            sources=[
                _source(
                    source_id="many-rows",
                    role=GeoXUploadedCSVRole.KPI_PANEL,
                    path=str(csv_path),
                )
            ],
            max_rows=3,
        )
    )
    assert result.status == GeoXUploadedCSVMaterializationStatus.BLOCKED_ROW_LIMIT_EXCEEDED
    assert GeoXUploadedCSVIssueCode.ROW_LIMIT_EXCEEDED in result.issues


def test_source_inspection_compatibility() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="inspect",
            sources=_core_sources(include_metadata=False),
        )
    )
    sources = _core_sources(include_metadata=False)
    kpi_dataset = next(d for d in result.datasets if d.role == GeoXUploadedCSVRole.KPI_PANEL)
    kpi_inspection = next(i for i in result.inspections if i.source_id == "uploaded-kpi")
    kpi_source = next(s for s in sources if s.source_id == "uploaded-kpi")
    dataset_ref = build_dataset_reference_from_uploaded_csv_inspection(kpi_source, kpi_inspection)
    assert dataset_ref.source_type == DatasetSourceType.UPLOADED_CSV
    assert dataset_ref.semantic_type == DatasetSemanticType.KPI_PANEL
    assert dataset_ref.declared_or_detected_columns == kpi_dataset.columns
    inspection = inspect_dataset_reference(dataset_ref)
    assert inspection.inspection_status == SourceInspectionStatus.INSPECTED


def test_materialized_input_availability_helper() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="availability",
            sources=_core_sources(include_metadata=False),
        )
    )
    availability = build_materialized_input_availability_from_uploaded_csv_result(result)
    assert availability.has_materialized_spend_df is True
    assert availability.has_materialized_assignment_df is True
    assert availability.materialized_spend_ref_optional == _SPEND_PATH
    assert availability.lineage["has_kpi_panel"] == "true"


def test_no_panel_exp_import_or_call() -> None:
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "import panel_exp" not in source
        assert "from panel_exp" not in source


def test_no_metric_recomputation_fields() -> None:
    result = materialize_geox_uploaded_csvs(
        GeoXUploadedCSVMaterializationRequest(
            request_id="metrics",
            sources=_core_sources(include_metadata=False),
        )
    )
    schema = result.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties
    for dataset in result.datasets:
        dataset_schema = dataset.model_json_schema()
        dataset_props = dataset_schema.get("properties", {})
        for field in _FORBIDDEN_TOP_LEVEL:
            assert field not in dataset_props
