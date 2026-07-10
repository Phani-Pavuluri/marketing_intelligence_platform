"""Tests for generic tabular source inspection workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.tabular_source_reference import (
    TabularSourceAccessMode,
    TabularSourceInspectionStatus,
    TabularSourceIssueCode,
    TabularSourceMaterializationMode,
    TabularSourceType,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationRequest,
    UploadedCSVMaterializationStatus,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.workflows.tabular_source_inspection import (
    build_tabular_source_inspection_from_uploaded_csv_materialization,
    build_tabular_source_inspection_result,
    build_tabular_source_reference,
    build_tabular_source_schema_from_columns,
)
from mip.workflows.uploaded_csv_materialization import materialize_uploaded_csvs

_FIXTURE_ROOT = Path("examples/fixtures/planning_mmm_uploaded_csv_adapter")
_SPEND_PATH = str(_FIXTURE_ROOT / "historical_spend.csv")
_OUTCOME_PATH = str(_FIXTURE_ROOT / "historical_outcome.csv")
_VALID_PATH = str(Path("examples/fixtures/uploaded_csv_materialization/valid_uploaded_table.csv"))
_HEADER_ONLY_PATH = str(
    Path("examples/fixtures/uploaded_csv_materialization/header_only_upload.csv")
)
_WORKFLOW_SOURCE = Path("src/mip/workflows/tabular_source_inspection.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/tabular_source_reference.py")
_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi_value", "roas_value")
_FORBIDDEN_RUNTIME_PATTERNS = (
    "databricks",
    "warehouse",
    "api_tabular_source",
    "registered_table_source",
    "spark",
    "jdbc",
    "odbc",
)


def _source(*, source_id: str, path: str) -> UploadedCSVSource:
    return UploadedCSVSource(
        source_id=source_id,
        source_type=UploadedCSVSourceType.UPLOADED_CSV,
        path=path,
        original_filename=Path(path).name,
    )


def test_uploaded_csv_compatibility_inspection_created() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-tab",
            sources=[
                _source(source_id="spend", path=_SPEND_PATH),
                _source(source_id="outcome", path=_OUTCOME_PATH),
            ],
        )
    )
    result = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="inspect-tab",
        materialization_result=materialization,
    )
    assert result.status in {
        TabularSourceInspectionStatus.INSPECTED,
        TabularSourceInspectionStatus.INSPECTED_WITH_WARNINGS,
    }
    assert len(result.inspections) == 2
    inspection = result.inspections[0]
    assert inspection.source_reference.source_type == TabularSourceType.UPLOADED_CSV
    assert inspection.source_reference.access_mode == TabularSourceAccessMode.LOCAL_FILE
    assert (
        inspection.source_reference.materialization_mode
        == TabularSourceMaterializationMode.MATERIALIZED_IN_MEMORY
    )
    assert inspection.materialized_dataset is not None
    assert inspection.source_schema is not None
    assert inspection.lineage is not None
    assert inspection.availability is not None
    assert TabularSourceIssueCode.UPLOADED_CSV_COMPATIBILITY_CREATED in result.issues
    assert TabularSourceIssueCode.MATERIALIZED_DATASET_ATTACHED in inspection.issues


def test_declared_role_hint_preserved() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-hint",
            sources=[
                UploadedCSVSource(
                    source_id="spend",
                    source_type=UploadedCSVSourceType.UPLOADED_CSV,
                    path=_SPEND_PATH,
                    original_filename=Path(_SPEND_PATH).name,
                    declared_role_hint="historical_spend",
                )
            ],
        )
    )
    result = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="inspect-hint",
        materialization_result=materialization,
    )
    inspection = result.inspections[0]
    assert inspection.source_reference.declared_role_hint == "historical_spend"
    assert TabularSourceIssueCode.DECLARED_ROLE_HINT_PRESERVED in inspection.issues


def test_missing_blocked_uploaded_csv_materialization() -> None:
    result = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="inspect-missing",
        materialization_result=None,
    )
    assert result.status == TabularSourceInspectionStatus.BLOCKED_MISSING_SOURCE
    assert TabularSourceIssueCode.MISSING_SOURCE in result.issues


def test_blocked_uploaded_csv_materialization_preserves_warnings() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-blocked",
            sources=[_source(source_id="header-only", path=_HEADER_ONLY_PATH)],
        )
    )
    assert materialization.status == UploadedCSVMaterializationStatus.BLOCKED_HEADER_ONLY_FILE
    result = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="inspect-blocked",
        materialization_result=materialization,
    )
    assert result.status == TabularSourceInspectionStatus.BLOCKED_MATERIALIZATION_UNAVAILABLE
    assert TabularSourceIssueCode.MATERIALIZATION_UNAVAILABLE in result.issues
    assert result.warnings == materialization.warnings


def test_reference_only_source_without_materialized_dataset() -> None:
    reference = build_tabular_source_reference(
        source_id="warehouse-1",
        source_type=TabularSourceType.WAREHOUSE_TABLE,
        access_mode=TabularSourceAccessMode.REFERENCE_ONLY,
        materialization_mode=TabularSourceMaterializationMode.REFERENCE_ONLY,
        source_uri="warehouse://analytics.fact_spend",
        source_name="fact_spend",
    )
    assert reference.materialization_mode == TabularSourceMaterializationMode.REFERENCE_ONLY
    assert reference.data_source_ref is None


def test_schema_only_source_from_columns() -> None:
    schema = build_tabular_source_schema_from_columns(
        ["date", "channel", "spend"],
        normalized_columns=["date", "channel", "spend"],
        schema_source="metadata_only",
    )
    assert schema.column_names == ["date", "channel", "spend"]
    assert schema.row_count is None


def test_data_source_ref_compatibility_preserved() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-ref",
            sources=[_source(source_id="valid", path=_VALID_PATH)],
        )
    )
    result = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="inspect-ref",
        materialization_result=materialization,
    )
    inspection = result.inspections[0]
    assert inspection.source_reference.data_source_ref is not None
    assert inspection.source_reference.data_source_ref.source_id == "valid"
    assert TabularSourceIssueCode.DATA_SOURCE_REF_COMPATIBLE in inspection.issues


def test_no_csv_reread_in_tabular_source_modules() -> None:
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "read_csv" not in source
        assert "import pandas" not in source


def test_no_connector_runtime_modules_added() -> None:
    src_root = Path("src/mip")
    for path in src_root.rglob("*.py"):
        stem = path.stem.lower()
        for pattern in _FORBIDDEN_RUNTIME_PATTERNS:
            assert pattern not in stem, f"unexpected runtime module: {path}"


def test_no_sql_network_spark_in_workflow() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8").lower()
    for term in ("requests", "httpx", "urllib", "spark", "sqlalchemy", "execute("):
        assert term not in source


def test_existing_uploaded_csv_materialization_regression() -> None:
    result = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="regression-mat",
            sources=[_source(source_id="valid", path=_VALID_PATH)],
        )
    )
    assert result.status == UploadedCSVMaterializationStatus.MATERIALIZED


def test_build_tabular_source_inspection_result_assembly() -> None:
    reference = build_tabular_source_reference(
        source_id="api-1",
        source_type=TabularSourceType.API_EXTRACT,
        access_mode=TabularSourceAccessMode.SCHEMA_ONLY,
        materialization_mode=TabularSourceMaterializationMode.NOT_MATERIALIZED,
        source_uri="api://extract/session-1",
    )
    result = build_tabular_source_inspection_result(
        request_id="batch-1",
        status=TabularSourceInspectionStatus.INSPECTED,
        inspections=[],
        issues=[TabularSourceIssueCode.SOURCE_REFERENCE_CREATED],
    )
    assert result.request_id == "batch-1"
    assert reference.source_type == TabularSourceType.API_EXTRACT


def test_no_metric_recomputation_fields() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-fields",
            sources=[_source(source_id="valid", path=_VALID_PATH)],
        )
    )
    result = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="inspect-fields",
        materialization_result=materialization,
    )
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in result.model_dump()
