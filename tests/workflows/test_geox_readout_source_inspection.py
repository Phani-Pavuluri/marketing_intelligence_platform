"""Tests for deterministic GeoX readout source inspection (Stage 2B)."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.geox_readout_input_resolution import (
    ColumnMappingCandidate,
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    MappingConfirmationStatus,
)
from mip.contracts.geox_readout_source_inspection import (
    ColumnSemanticHint,
    GeoXReadoutSourceInspectionRequest,
    SourceInspectionIssueCode,
    SourceInspectionStatus,
)
from mip.workflows.geox_readout_source_inspection import (
    inspect_dataset_reference,
    inspect_geox_readout_sources,
)

_INSPECTION_SOURCE = Path("src/mip/workflows/geox_readout_source_inspection.py")


def _ref(
    *,
    dataset_ref_id: str,
    source_type: DatasetSourceType,
    semantic_type: DatasetSemanticType,
    columns: list[str],
    uri: str = "file://local.csv",
) -> DatasetReference:
    return DatasetReference(
        dataset_ref_id=dataset_ref_id,
        source_type=source_type,
        semantic_type=semantic_type,
        source_uri_or_handle=uri,
        file_name_or_table_name=f"{dataset_ref_id}.csv",
        declared_or_detected_columns=columns,
        classification_confidence=0.9,
        user_confirmation_status=MappingConfirmationStatus.NOT_REQUIRED,
    )


def test_kpi_panel_declared_columns() -> None:
    ref = _ref(
        dataset_ref_id="kpi-panel",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        columns=["date", "dma", "conversions"],
    )
    result = inspect_dataset_reference(ref)
    assert result.inspection_status == SourceInspectionStatus.INSPECTED
    assert result.semantic_hints[0].semantic_type == DatasetSemanticType.KPI_PANEL
    hints = {hint.semantic_hint for hint in result.column_hints}
    assert ColumnSemanticHint.DATE_OR_WEEK in hints
    assert ColumnSemanticHint.GEO_OR_UNIT in hints
    assert ColumnSemanticHint.KPI_METRIC in hints


def test_spend_panel_declared_columns() -> None:
    ref = _ref(
        dataset_ref_id="spend-panel",
        source_type=DatasetSourceType.WAREHOUSE_TABLE,
        semantic_type=DatasetSemanticType.SPEND_PANEL,
        columns=["week_start", "market", "spend", "currency"],
        uri="warehouse://spend_table",
    )
    result = inspect_dataset_reference(ref)
    assert result.semantic_hints[0].semantic_type == DatasetSemanticType.SPEND_PANEL
    hints = {hint.semantic_hint for hint in result.column_hints}
    assert ColumnSemanticHint.DATE_OR_WEEK in hints
    assert ColumnSemanticHint.GEO_OR_UNIT in hints
    assert ColumnSemanticHint.SPEND_AMOUNT in hints
    assert ColumnSemanticHint.CURRENCY in hints


def test_assignment_table_declared_columns() -> None:
    ref = _ref(
        dataset_ref_id="assignment",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.ASSIGNMENT_TABLE,
        columns=["dma", "cell", "treatment"],
    )
    result = inspect_dataset_reference(ref)
    assert result.semantic_hints[0].semantic_type == DatasetSemanticType.ASSIGNMENT_TABLE
    hints = {hint.semantic_hint for hint in result.column_hints}
    assert ColumnSemanticHint.GEO_OR_UNIT in hints
    assert ColumnSemanticHint.TREATMENT_OR_CELL in hints
    assert ColumnSemanticHint.ASSIGNMENT_LABEL in hints


def test_value_mapping_declared_columns() -> None:
    ref = _ref(
        dataset_ref_id="value-map",
        source_type=DatasetSourceType.MANUAL_USER_ENTRY,
        semantic_type=DatasetSemanticType.VALUE_MAPPING,
        columns=["metric", "value_per_conversion", "currency"],
    )
    result = inspect_dataset_reference(ref)
    assert result.semantic_hints[0].semantic_type == DatasetSemanticType.VALUE_MAPPING
    hints = {hint.semantic_hint for hint in result.column_hints}
    assert ColumnSemanticHint.VALUE_OR_REVENUE in hints


def test_margin_mapping_declared_columns() -> None:
    ref = _ref(
        dataset_ref_id="margin-map",
        source_type=DatasetSourceType.MANUAL_USER_ENTRY,
        semantic_type=DatasetSemanticType.MARGIN_MAPPING,
        columns=["metric", "margin_rate", "profit"],
    )
    result = inspect_dataset_reference(ref)
    assert result.semantic_hints[0].semantic_type == DatasetSemanticType.MARGIN_MAPPING
    hints = {hint.semantic_hint for hint in result.column_hints}
    assert ColumnSemanticHint.MARGIN_OR_PROFIT in hints


def test_unknown_dataset_low_confidence() -> None:
    ref = _ref(
        dataset_ref_id="unknown",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.UNKNOWN_DATASET,
        columns=["foo", "bar"],
    )
    result = inspect_dataset_reference(ref)
    assert result.semantic_hints[0].semantic_type == DatasetSemanticType.UNKNOWN_DATASET
    assert result.semantic_hints[0].confidence <= 0.5
    assert any(h.semantic_hint == ColumnSemanticHint.UNKNOWN for h in result.column_hints)
    assert result.warnings or result.issues


def test_empty_declared_columns() -> None:
    ref = _ref(
        dataset_ref_id="empty",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        columns=[],
    )
    result = inspect_dataset_reference(ref)
    assert result.inspection_status == SourceInspectionStatus.NO_COLUMNS_AVAILABLE
    assert SourceInspectionIssueCode.DECLARED_COLUMNS_EMPTY in result.issues


def test_unsupported_source_type() -> None:
    ref = _ref(
        dataset_ref_id="bad-source",
        source_type=DatasetSourceType.UNKNOWN,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        columns=["date", "dma", "conversions"],
    )
    result = inspect_dataset_reference(ref)
    assert result.inspection_status == SourceInspectionStatus.SOURCE_TYPE_NOT_SUPPORTED
    assert SourceInspectionIssueCode.SOURCE_TYPE_UNSUPPORTED in result.issues


def test_warehouse_ref_resolvable_without_live_call() -> None:
    ref = _ref(
        dataset_ref_id="warehouse",
        source_type=DatasetSourceType.WAREHOUSE_TABLE,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        columns=["date", "dma", "conversions"],
        uri="warehouse://project.dataset.kpi_panel",
    )
    result = inspect_dataset_reference(ref)
    assert result.source_resolvable is True
    assert result.inspection_status == SourceInspectionStatus.INSPECTED
    source = _INSPECTION_SOURCE.read_text(encoding="utf-8")
    assert "requests." not in source
    assert "boto3" not in source


def test_ambiguous_semantic_type_handled_conservatively() -> None:
    ref = _ref(
        dataset_ref_id="ambiguous",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.UNKNOWN_DATASET,
        columns=["date", "dma", "spend", "conversions"],
    )
    result = inspect_dataset_reference(ref)
    assert SourceInspectionIssueCode.AMBIGUOUS_SEMANTIC_TYPE in result.issues
    assert len(result.semantic_hints) >= 2
    assert result.semantic_hints[0].confidence <= 0.7


def test_mapping_candidates_emitted() -> None:
    ref = _ref(
        dataset_ref_id="mapped",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        columns=["date", "dma", "conversions"],
    )
    result = inspect_dataset_reference(ref)
    assert result.mapping_candidates
    assert all(isinstance(c, ColumnMappingCandidate) for c in result.mapping_candidates)
    targets = {c.target_field for c in result.mapping_candidates}
    assert "date_week_column" in targets
    assert "geo_unit_column" in targets
    assert "kpi_metric_column" in targets


def test_no_file_parsing_by_default() -> None:
    ref = _ref(
        dataset_ref_id="local-file",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        columns=["date", "dma", "conversions"],
        uri="file:///tmp/kpi_panel.csv",
    )
    result = inspect_dataset_reference(
        ref,
        allow_local_file_metadata_inspection=False,
    )
    assert result.available_columns == ref.declared_or_detected_columns
    source = _INSPECTION_SOURCE.read_text(encoding="utf-8")
    assert "read_csv" not in source
    assert "pandas" not in source


def test_inspector_does_not_import_panel_exp() -> None:
    source = _INSPECTION_SOURCE.read_text(encoding="utf-8")
    assert "import panel_exp" not in source
    assert "from panel_exp" not in source


def test_batch_inspection_preserves_lineage() -> None:
    ref = _ref(
        dataset_ref_id="batch-1",
        source_type=DatasetSourceType.API_REFERENCE,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        columns=["date", "dma", "conversions"],
        uri="api://kpi",
    )
    request = GeoXReadoutSourceInspectionRequest(
        request_id="batch-req",
        dataset_refs=[ref],
        lineage={"lane": "geox_readout"},
        warnings=["seed-warning"],
    )
    result = inspect_geox_readout_sources(request)
    assert result.request_id == "batch-req"
    assert result.lineage["lane"] == "geox_readout"
    assert result.inspected_dataset_count >= 1
    assert "seed-warning" in result.warnings


def test_inspection_output_can_feed_stage_2a_resolution() -> None:
    ref = _ref(
        dataset_ref_id="handoff-prep",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        columns=["date", "dma", "conversions"],
    )
    inspection = inspect_dataset_reference(ref)
    assert inspection.dataset_ref.semantic_type == DatasetSemanticType.KPI_PANEL
    assert inspection.mapping_candidates
    assert inspection.semantic_hints[0].semantic_type == DatasetSemanticType.KPI_PANEL
