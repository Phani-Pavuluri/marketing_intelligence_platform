"""Tests for Planning/MMM readiness report adapter contracts."""

from __future__ import annotations

from datetime import UTC, datetime

from mip.contracts import (
    RECOMMENDED_NEXT_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_ARTIFACT,
    RECOMMENDED_NEXT_PLANNING_MMM_CALIBRATION_SIGNAL_INTAKE_ARTIFACT,
    PlanningMMMReadinessReportAdapterEnvelope,
    PlanningMMMReadinessReportAdapterIssueCode,
    PlanningMMMReadinessReportAdapterRequest,
    PlanningMMMReadinessReportAdapterResult,
    PlanningMMMReadinessReportAdapterStatus,
    PlanningMMMReadinessReportCompatibility,
    PlanningMMMReadinessReportCompatibilityMode,
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
    "lift",
    "roi",
    "roas",
    "incrementality",
    "optimal_budget",
    "marginal_roi",
    "recommendation",
)


def test_required_enums_exist() -> None:
    assert PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED in (
        PlanningMMMReadinessReportAdapterStatus
    )
    assert PlanningMMMReadinessReportCompatibilityMode.METADATA_COMPATIBLE in (
        PlanningMMMReadinessReportCompatibilityMode
    )
    assert PlanningMMMReadinessReportAdapterIssueCode.NO_MODEL_EXECUTION in (
        PlanningMMMReadinessReportAdapterIssueCode
    )


def test_models_serialize() -> None:
    request = PlanningMMMReadinessReportAdapterRequest(request_id="req-1")
    assert request.require_full_mmm_data_readiness_report is False
    result = PlanningMMMReadinessReportAdapterResult(
        request_id="req-1",
        status=PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_WORKFLOW_READINESS_RESULT,
    )
    assert result.envelope is None


def test_envelope_can_include_data_source_refs() -> None:
    source_ref = DataSourceRef(
        source_id="spend",
        source_mode=DataSourceMode.LOCAL_FILE_PATH_MANIFEST,
        source_type=DataSourceType.FILE,
        asset_type=DataAssetType.MEDIA_SPEND_DATA,
        uri_or_table_ref="/tmp/spend.csv",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=DataSourceStatus.DECLARED,
    )
    envelope = PlanningMMMReadinessReportAdapterEnvelope(
        envelope_id="env-1",
        source_workflow_readiness_status="ready_for_mmm_workflow_readiness",
        source_workflow_readiness_tier="ready_for_gated_workflow",
        readiness_report_status="ready_for_mmm_workflow_readiness",
        compatibility=PlanningMMMReadinessReportCompatibility(
            mode=PlanningMMMReadinessReportCompatibilityMode.METADATA_COMPATIBLE,
            metadata_compatible=True,
        ),
        data_source_refs=[source_ref],
    )
    assert envelope.data_source_refs[0].source_id == "spend"


def test_envelope_can_include_tabular_source_refs_metadata() -> None:
    envelope = PlanningMMMReadinessReportAdapterEnvelope(
        envelope_id="env-1",
        source_workflow_readiness_status="ready_for_mmm_workflow_readiness",
        source_workflow_readiness_tier="ready_for_gated_workflow",
        readiness_report_status="ready_for_mmm_workflow_readiness",
        compatibility=PlanningMMMReadinessReportCompatibility(
            mode=PlanningMMMReadinessReportCompatibilityMode.FULL_REPORT_CONSTRUCTION_DEFERRED,
            metadata_compatible=True,
        ),
        tabular_source_refs=[
            TabularSourceReference(
                source_id="spend",
                source_type=TabularSourceType.UPLOADED_CSV,
                access_mode=TabularSourceAccessMode.LOCAL_FILE,
                materialization_mode=TabularSourceMaterializationMode.MATERIALIZED_IN_MEMORY,
            )
        ],
    )
    assert envelope.tabular_source_refs[0].source_id == "spend"


def test_compatibility_metadata_and_deferred_modes() -> None:
    metadata = PlanningMMMReadinessReportCompatibility(
        mode=PlanningMMMReadinessReportCompatibilityMode.METADATA_COMPATIBLE,
        metadata_compatible=True,
        full_report_constructed=False,
        deferred_fields=["session_id", "manifest_id"],
    )
    deferred = PlanningMMMReadinessReportCompatibility(
        mode=PlanningMMMReadinessReportCompatibilityMode.FULL_REPORT_CONSTRUCTION_DEFERRED,
        metadata_compatible=True,
        full_report_deferred_reason="missing session context",
    )
    assert metadata.metadata_compatible is True
    assert deferred.mode == (
        PlanningMMMReadinessReportCompatibilityMode.FULL_REPORT_CONSTRUCTION_DEFERRED
    )


def test_result_no_top_level_metric_fields() -> None:
    schema = PlanningMMMReadinessReportAdapterResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_ARTIFACT == (
        "MIP_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001"
    )
    assert RECOMMENDED_NEXT_PLANNING_MMM_CALIBRATION_SIGNAL_INTAKE_ARTIFACT == (
        "MIP_PLANNING_MMM_CALIBRATION_SIGNAL_INTAKE_FROM_TABULAR_SOURCE_001"
    )
