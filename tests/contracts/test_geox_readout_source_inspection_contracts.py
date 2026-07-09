"""Tests for GeoX readout source inspection contracts (Stage 2B)."""

from __future__ import annotations

import pytest

from mip.contracts import (
    RECOMMENDED_NEXT_STAGE_2C_ARTIFACT,
    ColumnInspectionHint,
    ColumnSemanticHint,
    DatasetReference,
    DatasetSemanticInspectionHint,
    DatasetSemanticType,
    DatasetSourceInspectionResult,
    DatasetSourceType,
    GeoXReadoutSourceInspectionRequest,
    GeoXReadoutSourceInspectionResult,
    SourceInspectionIssueCode,
    SourceInspectionStatus,
)

_REQUIRED_INSPECTION_STATUSES = {
    SourceInspectionStatus.INSPECTED,
    SourceInspectionStatus.SOURCE_NOT_RESOLVABLE,
    SourceInspectionStatus.SOURCE_TYPE_NOT_SUPPORTED,
    SourceInspectionStatus.DECLARED_COLUMNS_VALIDATED,
    SourceInspectionStatus.DECLARED_COLUMNS_MISSING,
    SourceInspectionStatus.NO_COLUMNS_AVAILABLE,
    SourceInspectionStatus.INSPECTION_SKIPPED,
}

_REQUIRED_ISSUE_CODES = {
    SourceInspectionIssueCode.SOURCE_URI_MISSING,
    SourceInspectionIssueCode.SOURCE_NOT_FOUND,
    SourceInspectionIssueCode.SOURCE_TYPE_UNSUPPORTED,
    SourceInspectionIssueCode.DECLARED_COLUMNS_EMPTY,
    SourceInspectionIssueCode.DECLARED_COLUMNS_NOT_FOUND,
    SourceInspectionIssueCode.DUPLICATE_COLUMNS,
    SourceInspectionIssueCode.AMBIGUOUS_SEMANTIC_TYPE,
    SourceInspectionIssueCode.AMBIGUOUS_COLUMN_MAPPING,
    SourceInspectionIssueCode.NO_DATE_COLUMN_CANDIDATE,
    SourceInspectionIssueCode.NO_GEO_COLUMN_CANDIDATE,
    SourceInspectionIssueCode.NO_KPI_COLUMN_CANDIDATE,
    SourceInspectionIssueCode.NO_SPEND_COLUMN_CANDIDATE,
    SourceInspectionIssueCode.NO_ASSIGNMENT_COLUMN_CANDIDATE,
    SourceInspectionIssueCode.NO_VALUE_MAPPING_CANDIDATE,
}

_REQUIRED_COLUMN_HINTS = {
    ColumnSemanticHint.DATE_OR_WEEK,
    ColumnSemanticHint.GEO_OR_UNIT,
    ColumnSemanticHint.KPI_METRIC,
    ColumnSemanticHint.SPEND_AMOUNT,
    ColumnSemanticHint.CURRENCY,
    ColumnSemanticHint.CHANNEL,
    ColumnSemanticHint.PLATFORM,
    ColumnSemanticHint.CAMPAIGN,
    ColumnSemanticHint.TREATMENT_OR_CELL,
    ColumnSemanticHint.ASSIGNMENT_LABEL,
    ColumnSemanticHint.EXPERIMENT_ID,
    ColumnSemanticHint.VALUE_OR_REVENUE,
    ColumnSemanticHint.MARGIN_OR_PROFIT,
    ColumnSemanticHint.UNKNOWN,
}

_FORBIDDEN_OUTPUT_FIELD_FRAGMENTS = (
    "spend_delta",
    "delta_mu",
    "roi_value",
    "roas_value",
    "incremental_roi",
    "computed_lift",
    "lift_value",
)


def test_source_inspection_enums_contain_required_values() -> None:
    assert _REQUIRED_INSPECTION_STATUSES.issubset(set(SourceInspectionStatus))
    assert _REQUIRED_ISSUE_CODES.issubset(set(SourceInspectionIssueCode))
    assert _REQUIRED_COLUMN_HINTS.issubset(set(ColumnSemanticHint))


def test_models_serialize_round_trip() -> None:
    ref = DatasetReference(
        dataset_ref_id="kpi-1",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        source_uri_or_handle="file://kpi.csv",
        file_name_or_table_name="kpi.csv",
        declared_or_detected_columns=["date", "dma", "conversions"],
        classification_confidence=0.9,
    )
    request = GeoXReadoutSourceInspectionRequest(
        request_id="inspect-1",
        dataset_refs=[ref],
        lineage={"stage": "2b"},
    )
    payload = request.model_dump()
    restored = GeoXReadoutSourceInspectionRequest.model_validate(payload)
    assert restored.request_id == "inspect-1"
    assert restored.dataset_refs[0].dataset_ref_id == "kpi-1"


def test_confidence_validation_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        ColumnInspectionHint(
            source_column="date",
            semantic_hint=ColumnSemanticHint.DATE_OR_WEEK,
            confidence=1.2,
        )
    with pytest.raises(ValueError):
        DatasetSemanticInspectionHint(
            semantic_type=DatasetSemanticType.KPI_PANEL,
            confidence=-0.1,
        )


def test_inspection_result_preserves_dataset_reference() -> None:
    ref = DatasetReference(
        dataset_ref_id="preserve-me",
        source_type=DatasetSourceType.API_REFERENCE,
        semantic_type=DatasetSemanticType.SPEND_PANEL,
        source_uri_or_handle="api://spend",
        file_name_or_table_name="spend",
        declared_or_detected_columns=["week", "market", "spend"],
        classification_confidence=0.8,
    )
    result = DatasetSourceInspectionResult(
        dataset_ref=ref,
        inspection_status=SourceInspectionStatus.INSPECTED,
        source_resolvable=True,
        declared_columns=ref.declared_or_detected_columns,
        available_columns=ref.declared_or_detected_columns,
    )
    assert result.dataset_ref.dataset_ref_id == "preserve-me"
    assert result.dataset_ref is ref


def test_no_numeric_roi_roas_lift_delta_output_fields_on_models() -> None:
    models = (
        ColumnInspectionHint,
        DatasetSemanticInspectionHint,
        DatasetSourceInspectionResult,
        GeoXReadoutSourceInspectionRequest,
        GeoXReadoutSourceInspectionResult,
    )
    for model in models:
        field_names = " ".join(model.model_fields).lower()
        for fragment in _FORBIDDEN_OUTPUT_FIELD_FRAGMENTS:
            assert fragment not in field_names, f"{model.__name__} has forbidden field {fragment}"


def test_contracts_exported_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_STAGE_2C_ARTIFACT == (
        "MIP_GEOX_READOUT_INPUT_RESOLUTION_RUNTIME_001C"
    )
    assert SourceInspectionStatus.INSPECTED.value == "inspected"
    assert GeoXReadoutSourceInspectionResult is not None
