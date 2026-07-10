"""Tests for Planning/MMM calibration-signal tabular intake contracts."""

from __future__ import annotations

from datetime import UTC, datetime

from mip.contracts import (
    RECOMMENDED_NEXT_GEOX_READOUT_RESULT_ROUTING_FROM_TABULAR_SOURCE_ARTIFACT,
    RECOMMENDED_NEXT_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AUDIT_ARTIFACT,
    PlanningMMMCalibrationSignalColumnMapping,
    PlanningMMMCalibrationSignalColumnRole,
    PlanningMMMCalibrationSignalConstructionMode,
    PlanningMMMCalibrationSignalDeferredMapping,
    PlanningMMMCalibrationSignalTabularIntakeEnvelope,
    PlanningMMMCalibrationSignalTabularIntakeIssueCode,
    PlanningMMMCalibrationSignalTabularIntakeRequest,
    PlanningMMMCalibrationSignalTabularIntakeResult,
    PlanningMMMCalibrationSignalTabularIntakeStatus,
    TabularSourceAccessMode,
    TabularSourceMaterializationMode,
    TabularSourceReference,
    TabularSourceType,
)
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import (
    DataSourceMode,
    DataSourceRef,
    DataSourceStatus,
    DataSourceType,
)

_FORBIDDEN_TOP_LEVEL = (
    "spend_delta",
    "delta_mu",
    "roi",
    "roas",
    "incrementality",
    "optimal_budget",
    "marginal_roi",
    "recommendation",
)


def test_required_enums_exist() -> None:
    assert PlanningMMMCalibrationSignalTabularIntakeStatus.INTAKE_READY in (
        PlanningMMMCalibrationSignalTabularIntakeStatus
    )
    assert PlanningMMMCalibrationSignalConstructionMode.METADATA_ONLY in (
        PlanningMMMCalibrationSignalConstructionMode
    )
    assert PlanningMMMCalibrationSignalColumnRole.LIFT in PlanningMMMCalibrationSignalColumnRole
    assert PlanningMMMCalibrationSignalTabularIntakeIssueCode.NO_MODEL_EXECUTION in (
        PlanningMMMCalibrationSignalTabularIntakeIssueCode
    )


def test_models_serialize() -> None:
    request = PlanningMMMCalibrationSignalTabularIntakeRequest(request_id="req-1")
    assert request.require_full_calibration_signal_construction is False
    result = PlanningMMMCalibrationSignalTabularIntakeResult(
        request_id="req-1",
        status=PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT,
    )
    assert result.envelope is None


def test_envelope_can_include_data_source_refs_and_tabular_refs() -> None:
    source_ref = DataSourceRef(
        source_id="calibration",
        source_mode=DataSourceMode.LOCAL_FILE_PATH_MANIFEST,
        source_type=DataSourceType.FILE,
        asset_type=DataAssetType.CALIBRATION_SIGNAL_DATA,
        uri_or_table_ref="/tmp/calibration.csv",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=DataSourceStatus.DECLARED,
    )
    tabular_ref = TabularSourceReference(
        source_id="calibration",
        source_type=TabularSourceType.UPLOADED_CSV,
        access_mode=TabularSourceAccessMode.LOCAL_FILE,
        materialization_mode=TabularSourceMaterializationMode.MATERIALIZED_IN_MEMORY,
        data_source_ref=source_ref,
    )
    envelope = PlanningMMMCalibrationSignalTabularIntakeEnvelope(
        envelope_id="env-1",
        status=PlanningMMMCalibrationSignalTabularIntakeStatus.INTAKE_READY,
        construction_mode=PlanningMMMCalibrationSignalConstructionMode.METADATA_ONLY,
        data_source_refs=[source_ref],
        tabular_source_references=[tabular_ref],
    )
    assert envelope.data_source_refs[0].source_id == "calibration"
    assert envelope.tabular_source_references[0].source_id == "calibration"


def test_deferred_mapping_metadata_and_deferred_modes() -> None:
    metadata = PlanningMMMCalibrationSignalDeferredMapping(
        mapping_id="map-1",
        source_id="calibration",
        construction_mode=PlanningMMMCalibrationSignalConstructionMode.METADATA_ONLY,
        metadata_compatible=True,
    )
    deferred = PlanningMMMCalibrationSignalDeferredMapping(
        mapping_id="map-2",
        source_id="calibration",
        construction_mode=(
            PlanningMMMCalibrationSignalConstructionMode.CALIBRATION_SIGNAL_CONSTRUCTION_DEFERRED
        ),
        metadata_compatible=True,
        full_construction_deferred_reason="missing target_model_id",
    )
    assert metadata.metadata_compatible is True
    assert (
        deferred.construction_mode
        == PlanningMMMCalibrationSignalConstructionMode.CALIBRATION_SIGNAL_CONSTRUCTION_DEFERRED
    )


def test_lift_is_column_role_not_computation() -> None:
    mapping = PlanningMMMCalibrationSignalColumnMapping(
        column_name="prior_lift",
        normalized_column_name="prior_lift",
        column_role=PlanningMMMCalibrationSignalColumnRole.LIFT,
        present=True,
    )
    assert mapping.column_role == PlanningMMMCalibrationSignalColumnRole.LIFT


def test_result_no_forbidden_top_level_fields() -> None:
    schema = PlanningMMMCalibrationSignalTabularIntakeResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AUDIT_ARTIFACT == (
        "MIP_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AUDIT_FROM_TABULAR_INTAKE_001"
    )
    assert RECOMMENDED_NEXT_GEOX_READOUT_RESULT_ROUTING_FROM_TABULAR_SOURCE_ARTIFACT == (
        "MIP_GEOX_READOUT_RESULT_ROUTING_FROM_TABULAR_SOURCE_001"
    )
