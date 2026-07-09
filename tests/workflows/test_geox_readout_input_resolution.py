"""Tests for deterministic GeoX readout input resolution (Stage 2A)."""

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
    AssignmentColumnMapping,
    ColumnMappingCandidate,
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
    MappingInferenceStatus,
    SpendColumnMapping,
    ValueMapping,
)
from mip.workflows.geox_readout_input_resolution import (
    MSG_MISSING_SPEND_FOR_EFFICIENCY,
    MSG_MISSING_VALUE_MAPPING,
    resolve_geox_readout_inputs,
)

_RESOLVER_SOURCE = Path("src/mip/workflows/geox_readout_input_resolution.py")
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


def _kpi_ref() -> DatasetReference:
    return DatasetReference(
        dataset_ref_id="kpi-panel-1",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        source_uri_or_handle="file://kpi.csv",
        file_name_or_table_name="kpi.csv",
        declared_or_detected_columns=["week", "dma", "conversions"],
        classification_confidence=0.99,
        user_confirmation_status=MappingConfirmationStatus.USER_CONFIRMED,
    )


def _spend_ref() -> DatasetReference:
    return DatasetReference(
        dataset_ref_id="spend-panel-1",
        source_type=DatasetSourceType.WAREHOUSE_TABLE,
        semantic_type=DatasetSemanticType.SPEND_PANEL,
        source_uri_or_handle="warehouse://spend_table",
        file_name_or_table_name="spend_table",
        declared_or_detected_columns=["week", "dma", "spend_usd"],
        classification_confidence=0.99,
        user_confirmation_status=MappingConfirmationStatus.USER_CONFIRMED,
    )


def _kpi_mapping(*, confirmed: bool = True) -> KPIColumnMapping:
    return KPIColumnMapping(
        date_week_column="week",
        geo_unit_column="dma",
        kpi_metric_column="conversions",
        kpi_metric_name="conversions",
        kpi_metric_unit="count",
        confirmation_status=(
            MappingConfirmationStatus.USER_CONFIRMED
            if confirmed
            else MappingConfirmationStatus.AMBIGUOUS
        ),
    )


def _spend_mapping(*, confirmed: bool = True) -> SpendColumnMapping:
    return SpendColumnMapping(
        date_week_column="week",
        geo_unit_column="dma",
        spend_amount_column="spend_usd",
        currency_column="currency",
        confirmation_status=(
            MappingConfirmationStatus.USER_CONFIRMED
            if confirmed
            else MappingConfirmationStatus.CONFIRMATION_REQUIRED
        ),
    )


def _assignment_mapping() -> AssignmentColumnMapping:
    return AssignmentColumnMapping(
        geo_unit_column="dma",
        treatment_control_label_column="cell",
        confirmation_status=MappingConfirmationStatus.USER_CONFIRMED,
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


def _base_request(
    *,
    metrics: list[str] | None = None,
    intent: GeoXReadoutIntent | None = None,
    include_spend: bool = False,
    runtime: bool = True,
    kpi_mapping: KPIColumnMapping | None = None,
    spend_mapping: SpendColumnMapping | None = None,
    value_mapping: ValueMapping | None = None,
) -> GeoXReadoutInputResolutionRequest:
    refs = [_kpi_ref()]
    if include_spend:
        refs.append(_spend_ref())
    return GeoXReadoutInputResolutionRequest(
        request_id="req-test",
        requested_intent=intent,
        requested_metrics=metrics or [],
        dataset_refs=refs,
        kpi_column_mapping=kpi_mapping or _kpi_mapping(),
        spend_column_mapping=spend_mapping,
        assignment_column_mapping=_assignment_mapping(),
        value_mapping=value_mapping,
        experiment_metadata=_metadata(),
        geox_runtime_available=runtime,
    )


def test_lift_readout_ready() -> None:
    result = resolve_geox_readout_inputs(
        _base_request(metrics=["lift"], intent=GeoXReadoutIntent.READOUT_WITH_LIFT),
    )
    assert result.resolution_status in {
        GeoXReadoutResolutionStatus.READY_FOR_LIFT_ONLY_READOUT,
        GeoXReadoutResolutionStatus.READY_FOR_GEOX_READOUT,
    }
    assert result.handoff is not None
    assert result.handoff.experiment_id == "exp-1"


def test_roi_requested_with_kpi_only_partial_readout() -> None:
    result = resolve_geox_readout_inputs(
        _base_request(metrics=["roi"], include_spend=False),
    )
    assert result.resolution_status in {
        GeoXReadoutResolutionStatus.PARTIAL_READOUT_ALLOWED,
        GeoXReadoutResolutionStatus.BLOCKED_MISSING_SPEND_FOR_EFFICIENCY,
    }
    assert GeoXMissingInputReason.MISSING_SPEND_FOR_EFFICIENCY in result.missing_inputs
    assert any(MSG_MISSING_SPEND_FOR_EFFICIENCY in msg for msg in result.user_messages)


def test_roi_with_spend_provided_does_not_ask_for_spend_again() -> None:
    result = resolve_geox_readout_inputs(
        _base_request(
            intent=GeoXReadoutIntent.READOUT_WITH_ROAS,
            include_spend=True,
            spend_mapping=_spend_mapping(),
            value_mapping=None,
        ),
    )
    assert result.resolution_status == (
        GeoXReadoutResolutionStatus.BLOCKED_MISSING_VALUE_MAPPING_FOR_ROAS
    )
    assert GeoXMissingInputReason.MISSING_VALUE_MAPPING_FOR_ROAS in result.missing_inputs
    assert any(MSG_MISSING_VALUE_MAPPING in msg for msg in result.user_messages)
    assert not any("requires post-test spend data" in msg for msg in result.user_messages)
    assert result.handoff is not None
    assert result.handoff.spend_dataset_ref_optional is not None


def test_cost_per_with_spend_ready() -> None:
    result = resolve_geox_readout_inputs(
        _base_request(
            intent=GeoXReadoutIntent.READOUT_WITH_COST_PER,
            include_spend=True,
            spend_mapping=_spend_mapping(),
        ),
    )
    assert result.resolution_status in {
        GeoXReadoutResolutionStatus.READY_FOR_COST_PER_READOUT,
        GeoXReadoutResolutionStatus.READY_FOR_GEOX_READOUT,
    }
    assert result.handoff is not None


def test_roas_with_kpi_spend_value_mapping_ready() -> None:
    result = resolve_geox_readout_inputs(
        _base_request(
            intent=GeoXReadoutIntent.READOUT_WITH_ROAS,
            include_spend=True,
            spend_mapping=_spend_mapping(),
            value_mapping=ValueMapping(
                revenue_mapping_source="finance://revenue_map",
                currency="USD",
                confirmation_status=MappingConfirmationStatus.USER_CONFIRMED,
            ),
        ),
    )
    assert result.resolution_status == GeoXReadoutResolutionStatus.READY_FOR_GEOX_READOUT
    assert result.handoff is not None
    assert "roi_value" not in result.model_dump_json().lower()
    assert "spend_delta" not in result.model_dump_json().lower()


def test_mapping_ambiguous_blocks_confirmation() -> None:
    result = resolve_geox_readout_inputs(
        _base_request(
            metrics=["lift"],
            kpi_mapping=_kpi_mapping(confirmed=False),
        ),
    )
    assert result.resolution_status == (
        GeoXReadoutResolutionStatus.BLOCKED_MAPPING_CONFIRMATION_REQUIRED
    )
    assert result.mapping_confirmation_required is True


def test_mapping_ambiguous_candidate_blocks() -> None:
    mapping = _kpi_mapping()
    mapping.candidates.append(
        ColumnMappingCandidate(
            source_column="market",
            target_field="geo_unit_column",
            inference_status=MappingInferenceStatus.INFERRED_LOW_CONFIDENCE,
            confirmation_status=MappingConfirmationStatus.AMBIGUOUS,
            confidence=0.3,
        )
    )
    result = resolve_geox_readout_inputs(_base_request(metrics=["lift"], kpi_mapping=mapping))
    assert result.resolution_status == (
        GeoXReadoutResolutionStatus.BLOCKED_MAPPING_CONFIRMATION_REQUIRED
    )


def test_missing_assignment() -> None:
    request = _base_request(metrics=["lift"])
    request.assignment_column_mapping = None
    request.experiment_metadata = GeoXExperimentMetadataRef(
        experiment_id="exp-1",
        test_start_date="2026-01-01",
        test_end_date="2026-03-01",
        post_period_start="2026-03-02",
        post_period_end="2026-04-01",
    )
    result = resolve_geox_readout_inputs(request)
    assert result.resolution_status == GeoXReadoutResolutionStatus.BLOCKED_MISSING_ASSIGNMENT


def test_missing_dates() -> None:
    request = _base_request(metrics=["lift"])
    request.experiment_metadata = GeoXExperimentMetadataRef(
        experiment_id="exp-1",
        design_artifact_ref=_artifact_ref(),
        assignment_artifact_ref=_artifact_ref(),
    )
    result = resolve_geox_readout_inputs(request)
    assert result.resolution_status == GeoXReadoutResolutionStatus.BLOCKED_MISSING_DATES


def test_decision_recommendation_routed_away() -> None:
    result = resolve_geox_readout_inputs(
        _base_request(intent=GeoXReadoutIntent.READOUT_WITH_DECISION_RECOMMENDATION_REQUEST),
    )
    assert result.resolution_status == (
        GeoXReadoutResolutionStatus.BLOCKED_DECISION_RECOMMENDATION_REQUIRES_DECISION_SURFACE
    )
    assert result.handoff is None


def test_runtime_unavailable_with_complete_inputs() -> None:
    result = resolve_geox_readout_inputs(
        _base_request(metrics=["lift"], runtime=False),
    )
    assert result.resolution_status == GeoXReadoutResolutionStatus.BLOCKED_NO_GEOX_RUNTIME_AVAILABLE
    assert result.handoff is not None


def test_unclear_intent_without_metrics() -> None:
    result = resolve_geox_readout_inputs(
        GeoXReadoutInputResolutionRequest(request_id="unclear"),
    )
    assert result.resolution_status == GeoXReadoutResolutionStatus.BLOCKED_UNCLEAR_USER_INTENT


def test_resolver_does_not_import_panel_exp() -> None:
    source = _RESOLVER_SOURCE.read_text(encoding="utf-8")
    assert "import panel_exp" not in source
    assert "from panel_exp" not in source
    assert "panel_exp." not in source
