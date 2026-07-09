"""Tests for GeoX readout input resolution contracts."""

from __future__ import annotations

import pytest

from mip.contracts import (
    PANEL_EXP_EXPECTED_RUNTIME,
    PANEL_EXP_TARGET_CONTRACT,
    AssignmentColumnMapping,
    ColumnMappingCandidate,
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    GeoXExperimentMetadataRef,
    GeoXMissingInputReason,
    GeoXReadoutInputHandoff,
    GeoXReadoutInputResolutionRequest,
    GeoXReadoutIntent,
    GeoXReadoutResolutionStatus,
    KPIColumnMapping,
    MappingConfirmationStatus,
    MappingInferenceStatus,
    SpendColumnMapping,
    ValueMapping,
)

_FORBIDDEN_OUTPUT_FIELD_FRAGMENTS = (
    "spend_delta",
    "delta_mu",
    "roi_value",
    "roas_value",
    "incremental_roi",
    "computed_lift",
)

_INTENTS = tuple(GeoXReadoutIntent)
_SOURCE_TYPES = tuple(DatasetSourceType)
_SEMANTIC_TYPES = tuple(DatasetSemanticType)
_RESOLUTION_STATUSES = tuple(GeoXReadoutResolutionStatus)


def test_required_enums_exported_from_mip_contracts() -> None:
    assert len(_INTENTS) == 7
    assert GeoXReadoutIntent.READOUT_WITH_LIFT in _INTENTS
    assert DatasetSourceType.WAREHOUSE_TABLE in _SOURCE_TYPES
    assert DatasetSemanticType.KPI_PANEL in _SEMANTIC_TYPES
    assert MappingInferenceStatus.INFERRED_HIGH_CONFIDENCE in MappingInferenceStatus
    assert MappingConfirmationStatus.USER_CONFIRMED in MappingConfirmationStatus
    assert GeoXReadoutResolutionStatus.PARTIAL_READOUT_ALLOWED in _RESOLUTION_STATUSES
    assert GeoXMissingInputReason.MAPPING_CONFIRMATION_REQUIRED in GeoXMissingInputReason


def test_model_serialization_round_trip() -> None:
    ref = DatasetReference(
        dataset_ref_id="kpi-1",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        source_uri_or_handle="file://kpi.csv",
        file_name_or_table_name="kpi.csv",
        declared_or_detected_columns=["week", "dma", "conversions"],
        classification_confidence=0.95,
    )
    request = GeoXReadoutInputResolutionRequest(
        request_id="req-1",
        requested_metrics=["lift"],
        dataset_refs=[ref],
    )
    payload = request.model_dump()
    restored = GeoXReadoutInputResolutionRequest.model_validate(payload)
    assert restored.request_id == "req-1"
    assert restored.dataset_refs[0].semantic_type == DatasetSemanticType.KPI_PANEL


def test_confidence_validation_rejects_out_of_range() -> None:
    with pytest.raises(ValueError):
        DatasetReference(
            dataset_ref_id="bad",
            source_type=DatasetSourceType.UNKNOWN,
            semantic_type=DatasetSemanticType.UNKNOWN_DATASET,
            source_uri_or_handle="x",
            file_name_or_table_name="x",
            classification_confidence=1.5,
        )


def test_handoff_defaults_target_contract_and_runtime() -> None:
    handoff = GeoXReadoutInputHandoff(
        request_id="h-1",
        readout_intent=GeoXReadoutIntent.READOUT_WITH_LIFT,
        experiment_id="exp-1",
        mip_resolution_status=GeoXReadoutResolutionStatus.READY_FOR_LIFT_ONLY_READOUT,
    )
    assert handoff.panel_exp_target_contract == PANEL_EXP_TARGET_CONTRACT
    assert handoff.panel_exp_expected_runtime == PANEL_EXP_EXPECTED_RUNTIME


def test_no_numeric_roi_roas_delta_output_fields_on_models() -> None:
    from mip.contracts.geox_readout_input_resolution import (
        GeoXReadoutInputHandoff as HandoffDirect,
    )
    from mip.contracts.geox_readout_input_resolution import (
        GeoXReadoutInputResolutionRequest,
        GeoXReadoutInputResolutionResult,
    )

    models = (
        GeoXReadoutInputHandoff,
        GeoXReadoutInputResolutionResult,
        GeoXReadoutInputResolutionRequest,
        HandoffDirect,
    )
    for model in models:
        field_names = " ".join(model.model_fields).lower()
        for fragment in _FORBIDDEN_OUTPUT_FIELD_FRAGMENTS:
            assert fragment not in field_names, f"{model.__name__} has forbidden field {fragment}"


def test_dataset_reference_supports_source_types() -> None:
    for source_type in (
        DatasetSourceType.UPLOADED_CSV,
        DatasetSourceType.WAREHOUSE_TABLE,
        DatasetSourceType.API_REFERENCE,
        DatasetSourceType.REGISTERED_ARTIFACT,
    ):
        ref = DatasetReference(
            dataset_ref_id=f"ref-{source_type.value}",
            source_type=source_type,
            semantic_type=DatasetSemanticType.KPI_PANEL,
            source_uri_or_handle="uri",
            file_name_or_table_name="name",
            classification_confidence=1.0,
        )
        assert ref.source_type == source_type


def test_column_mapping_candidate_and_statuses() -> None:
    candidate = ColumnMappingCandidate(
        source_column="dma_code",
        target_field="geo_unit_column",
        inference_status=MappingInferenceStatus.INFERRED_LOW_CONFIDENCE,
        confirmation_status=MappingConfirmationStatus.AMBIGUOUS,
        confidence=0.4,
    )
    mapping = KPIColumnMapping(
        geo_unit_column="dma_code",
        confirmation_status=MappingConfirmationStatus.AMBIGUOUS,
        candidates=[candidate],
    )
    assert mapping.confirmation_status == MappingConfirmationStatus.AMBIGUOUS


def test_value_mapping_rejects_negative_value_per_kpi() -> None:
    with pytest.raises(ValueError):
        ValueMapping(value_per_incremental_kpi=-1.0)


def test_spend_and_assignment_mapping_models() -> None:
    spend = SpendColumnMapping(
        date_week_column="week",
        geo_unit_column="dma",
        spend_amount_column="spend",
        currency_column="currency",
    )
    assignment = AssignmentColumnMapping(
        geo_unit_column="dma",
        treatment_control_label_column="cell",
    )
    assert spend.spend_amount_column == "spend"
    assert assignment.treatment_control_label_column == "cell"


def test_experiment_metadata_ref_optional_pre_period() -> None:
    meta = GeoXExperimentMetadataRef(
        experiment_id="exp-42",
        test_start_date="2026-01-01",
        test_end_date="2026-03-01",
        post_period_start="2026-03-02",
        post_period_end="2026-04-01",
    )
    assert meta.pre_period_start is None
