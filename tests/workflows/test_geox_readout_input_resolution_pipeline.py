"""Tests for GeoX readout inspection-to-resolution pipeline (Stage 2C)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from mip.contracts.deterministic_report import (
    ArtifactReference,
    EvidenceMode,
    GovernanceStatus,
    default_package_version_label,
)
from mip.contracts.geox_readout_input_resolution import (
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    GeoXExperimentMetadataRef,
    GeoXMissingInputReason,
    GeoXReadoutInputResolutionRequest,
    GeoXReadoutIntent,
    GeoXReadoutResolutionStatus,
    KPIColumnMapping,
    MappingConfirmationStatus,
)
from mip.workflows.geox_readout_input_resolution import resolve_geox_readout_inputs
from mip.workflows.geox_readout_input_resolution_pipeline import (
    build_column_mappings_from_inspection,
    enrich_dataset_reference_from_inspection,
    prepare_resolver_request_from_inspection,
    resolve_geox_readout_inputs_with_source_inspection,
)
from mip.workflows.geox_readout_source_inspection import inspect_dataset_reference

_PIPELINE_SOURCE = Path("src/mip/workflows/geox_readout_input_resolution_pipeline.py")
_NOW = datetime(2026, 7, 9, 12, 0, tzinfo=UTC)


def _artifact_ref() -> ArtifactReference:
    return ArtifactReference(
        artifact_id="geox-design:exp-1",
        artifact_type="geox_design",
        source_workflow="panel_exp.design",
        source_fixture_id_or_payload_ref="exp-1",
        source_commit_or_version=default_package_version_label(),
        created_at=_NOW,
        governance_status=GovernanceStatus.CANDIDATE,
        evidence_mode=EvidenceMode.DIAGNOSTIC_CANDIDATE,
        allowed_downstream_uses=["geox_readout"],
        forbidden_downstream_uses=[],
    )


def _metadata() -> GeoXExperimentMetadataRef:
    return GeoXExperimentMetadataRef(
        experiment_id="exp-1",
        design_artifact_ref=_artifact_ref(),
        assignment_artifact_ref=_artifact_ref(),
        test_start_date="2026-01-01",
        test_end_date="2026-03-01",
        post_period_start="2026-03-02",
        post_period_end="2026-04-01",
    )


def _raw_ref(
    dataset_ref_id: str,
    columns: list[str],
) -> DatasetReference:
    return DatasetReference(
        dataset_ref_id=dataset_ref_id,
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.UNKNOWN_DATASET,
        source_uri_or_handle=f"file://{dataset_ref_id}.csv",
        file_name_or_table_name=f"{dataset_ref_id}.csv",
        declared_or_detected_columns=columns,
        classification_confidence=0.0,
    )


def test_pipeline_lift_readout_from_unknown_dataset_refs() -> None:
    request = GeoXReadoutInputResolutionRequest(
        request_id="pipeline-lift",
        requested_intent=GeoXReadoutIntent.READOUT_WITH_LIFT,
        dataset_refs=[_raw_ref("kpi-raw", ["week", "dma", "conversions"])],
        experiment_metadata=_metadata(),
        geox_runtime_available=True,
    )
    pipeline = resolve_geox_readout_inputs_with_source_inspection(request)
    enriched = pipeline.enriched_dataset_refs[0]
    assert enriched.semantic_type == DatasetSemanticType.KPI_PANEL
    kpi_mapping = pipeline.enriched_resolution_request.kpi_column_mapping
    assert kpi_mapping is not None
    assert kpi_mapping.kpi_metric_column == "conversions"
    assert pipeline.resolution_result.resolution_status in {
        GeoXReadoutResolutionStatus.READY_FOR_LIFT_ONLY_READOUT,
        GeoXReadoutResolutionStatus.READY_FOR_GEOX_READOUT,
    }
    assert pipeline.resolution_result.handoff is not None


def test_pipeline_cost_per_partial_without_spend_ref() -> None:
    request = GeoXReadoutInputResolutionRequest(
        request_id="pipeline-partial",
        requested_intent=GeoXReadoutIntent.READOUT_WITH_COST_PER,
        dataset_refs=[_raw_ref("kpi-raw", ["week", "dma", "conversions"])],
        experiment_metadata=_metadata(),
        geox_runtime_available=True,
    )
    pipeline = resolve_geox_readout_inputs_with_source_inspection(request)
    assert GeoXMissingInputReason.MISSING_SPEND_FOR_EFFICIENCY in (
        pipeline.resolution_result.missing_inputs
    )
    assert pipeline.resolution_result.resolution_status in {
        GeoXReadoutResolutionStatus.PARTIAL_READOUT_ALLOWED,
        GeoXReadoutResolutionStatus.BLOCKED_MISSING_SPEND_FOR_EFFICIENCY,
    }


def test_pipeline_cost_per_ready_with_inferred_spend_mapping() -> None:
    request = GeoXReadoutInputResolutionRequest(
        request_id="pipeline-cost-per",
        requested_intent=GeoXReadoutIntent.READOUT_WITH_COST_PER,
        dataset_refs=[
            _raw_ref("kpi-raw", ["week", "dma", "conversions"]),
            _raw_ref("spend-raw", ["week_start", "market", "spend", "currency"]),
        ],
        experiment_metadata=_metadata(),
        geox_runtime_available=True,
    )
    pipeline = resolve_geox_readout_inputs_with_source_inspection(request)
    assert pipeline.enriched_resolution_request.spend_column_mapping is not None
    assert pipeline.enriched_resolution_request.spend_column_mapping.spend_amount_column == "spend"
    assert pipeline.resolution_result.resolution_status in {
        GeoXReadoutResolutionStatus.READY_FOR_COST_PER_READOUT,
        GeoXReadoutResolutionStatus.READY_FOR_GEOX_READOUT,
    }


def test_user_provided_mappings_override_inferred() -> None:
    request = GeoXReadoutInputResolutionRequest(
        request_id="pipeline-override",
        requested_intent=GeoXReadoutIntent.READOUT_WITH_LIFT,
        dataset_refs=[_raw_ref("kpi-raw", ["week", "dma", "conversions"])],
        kpi_column_mapping=KPIColumnMapping(
            date_week_column="week",
            geo_unit_column="dma",
            kpi_metric_column="conversions",
            kpi_metric_name="orders",
            confirmation_status=MappingConfirmationStatus.USER_CONFIRMED,
        ),
        experiment_metadata=_metadata(),
        geox_runtime_available=True,
    )
    pipeline = resolve_geox_readout_inputs_with_source_inspection(request)
    assert pipeline.enriched_resolution_request.kpi_column_mapping is not None
    assert pipeline.enriched_resolution_request.kpi_column_mapping.kpi_metric_name == "orders"


def test_ambiguous_dataset_blocks_mapping_confirmation() -> None:
    request = GeoXReadoutInputResolutionRequest(
        request_id="pipeline-ambiguous",
        requested_intent=GeoXReadoutIntent.READOUT_WITH_LIFT,
        dataset_refs=[
            _raw_ref("ambiguous", ["date", "dma", "spend", "conversions"]),
        ],
        experiment_metadata=_metadata(),
        geox_runtime_available=True,
    )
    pipeline = resolve_geox_readout_inputs_with_source_inspection(request)
    assert pipeline.resolution_result.resolution_status == (
        GeoXReadoutResolutionStatus.BLOCKED_MAPPING_CONFIRMATION_REQUIRED
    )
    assert pipeline.resolution_result.mapping_confirmation_required is True


def test_prepare_resolver_request_preserves_lineage() -> None:
    ref = _raw_ref("kpi-raw", ["week", "dma", "conversions"])
    inspection = inspect_dataset_reference(ref)
    request = GeoXReadoutInputResolutionRequest(
        request_id="lineage",
        dataset_refs=[ref],
        lineage={"session_id": "sess-1"},
    )
    from mip.contracts.geox_readout_source_inspection import GeoXReadoutSourceInspectionResult

    inspection_result = GeoXReadoutSourceInspectionResult(
        request_id="lineage:inspection",
        dataset_results=[inspection],
        inspected_dataset_count=1,
    )
    enriched = prepare_resolver_request_from_inspection(request, inspection_result)
    assert enriched.lineage["session_id"] == "sess-1"
    assert enriched.lineage["source_inspection_applied"] == "true"


def test_build_column_mappings_from_single_inspection() -> None:
    inspection = inspect_dataset_reference(
        _raw_ref("assignment", ["dma", "cell", "treatment"]),
    )
    enriched = enrich_dataset_reference_from_inspection(inspection)
    assert enriched.semantic_type == DatasetSemanticType.ASSIGNMENT_TABLE
    _, _, assignment_mapping, _ = build_column_mappings_from_inspection([inspection])
    assert assignment_mapping is not None
    assert assignment_mapping.geo_unit_column == "dma"


def test_stage_2a_resolver_left_intact_when_called_directly() -> None:
    request = GeoXReadoutInputResolutionRequest(request_id="direct-2a")
    result = resolve_geox_readout_inputs(request)
    assert result.resolution_status == GeoXReadoutResolutionStatus.BLOCKED_UNCLEAR_USER_INTENT


def test_pipeline_does_not_import_panel_exp() -> None:
    source = _PIPELINE_SOURCE.read_text(encoding="utf-8")
    assert "import panel_exp" not in source
    assert "from panel_exp" not in source


def test_pipeline_result_has_no_metric_computation_fields() -> None:
    request = GeoXReadoutInputResolutionRequest(
        request_id="pipeline-no-metrics",
        requested_intent=GeoXReadoutIntent.READOUT_WITH_LIFT,
        dataset_refs=[_raw_ref("kpi-raw", ["week", "dma", "conversions"])],
        experiment_metadata=_metadata(),
        geox_runtime_available=True,
    )
    pipeline = resolve_geox_readout_inputs_with_source_inspection(request)
    payload = pipeline.model_dump_json().lower()
    assert "spend_delta" not in payload
    assert "delta_mu" not in payload
    assert "roi_value" not in payload
