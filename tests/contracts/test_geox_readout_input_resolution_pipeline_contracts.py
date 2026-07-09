"""Tests for GeoX readout input resolution pipeline contracts (Stage 2C)."""

from __future__ import annotations

import pytest

from mip.contracts import (
    RECOMMENDED_NEXT_STAGE_3_ARTIFACT,
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    GeoXReadoutInputResolutionPipelineResult,
    GeoXReadoutInputResolutionRequest,
    GeoXReadoutInputResolutionResult,
    GeoXReadoutIntent,
    GeoXReadoutResolutionStatus,
    GeoXReadoutSourceInspectionResult,
)
from mip.contracts.geox_readout_source_inspection import (
    DatasetSourceInspectionResult,
    SourceInspectionStatus,
)

_FORBIDDEN_OUTPUT_FIELD_FRAGMENTS = (
    "spend_delta",
    "delta_mu",
    "roi_value",
    "roas_value",
    "incremental_roi",
    "computed_lift",
    "lift_value",
)


def test_pipeline_result_serializes() -> None:
    ref = DatasetReference(
        dataset_ref_id="kpi-1",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        source_uri_or_handle="file://kpi.csv",
        file_name_or_table_name="kpi.csv",
        declared_or_detected_columns=["week", "dma", "conversions"],
        classification_confidence=0.9,
    )
    request = GeoXReadoutInputResolutionRequest(
        request_id="req-1",
        requested_intent=GeoXReadoutIntent.READOUT_WITH_LIFT,
        dataset_refs=[ref],
    )
    result = GeoXReadoutInputResolutionPipelineResult(
        request_id="req-1",
        inspection_result=GeoXReadoutSourceInspectionResult(
            request_id="req-1:inspection",
            dataset_results=[
                DatasetSourceInspectionResult(
                    dataset_ref=ref,
                    inspection_status=SourceInspectionStatus.INSPECTED,
                    source_resolvable=True,
                )
            ],
        ),
        enriched_dataset_refs=[ref],
        enriched_resolution_request=request,
        resolution_result=GeoXReadoutInputResolutionResult(
            request_id="req-1",
            readout_intent=GeoXReadoutIntent.READOUT_WITH_LIFT,
            resolution_status=GeoXReadoutResolutionStatus.BLOCKED_MISSING_EXPERIMENT_METADATA,
        ),
    )
    restored = GeoXReadoutInputResolutionPipelineResult.model_validate(result.model_dump())
    assert restored.request_id == "req-1"
    assert restored.enriched_dataset_refs[0].dataset_ref_id == "kpi-1"


def test_no_forbidden_metric_output_fields_on_pipeline_models() -> None:
    for model in (GeoXReadoutInputResolutionPipelineResult,):
        field_names = " ".join(model.model_fields).lower()
        for fragment in _FORBIDDEN_OUTPUT_FIELD_FRAGMENTS:
            assert fragment not in field_names, f"{model.__name__} has forbidden field {fragment}"


def test_pipeline_contract_exported_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_STAGE_3_ARTIFACT == "MIP_GEOX_READOUT_PANEL_EXP_INTEGRATION_001"
    assert GeoXReadoutInputResolutionPipelineResult is not None


def test_pipeline_result_requires_nested_models() -> None:
    with pytest.raises(ValueError):
        GeoXReadoutInputResolutionPipelineResult(
            request_id="bad",
            inspection_result=None,  # type: ignore[arg-type]
            enriched_resolution_request=None,  # type: ignore[arg-type]
            resolution_result=None,  # type: ignore[arg-type]
        )
