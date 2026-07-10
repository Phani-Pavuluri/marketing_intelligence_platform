"""Tests for Planning/MMM uploaded CSV adapter contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from mip.contracts import (
    RECOMMENDED_NEXT_PLANNING_MMM_UPLOADED_CSV_INPUT_PLAN_ARTIFACT,
    PlanningMMMUploadedCSVAdapterIssueCode,
    PlanningMMMUploadedCSVAdapterRequest,
    PlanningMMMUploadedCSVAdapterResult,
    PlanningMMMUploadedCSVAdapterStatus,
    PlanningMMMUploadedCSVRole,
    PlanningMMMUploadedCSVRoleMapping,
    PlanningMMMUploadedCSVRoleSource,
)
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import (
    DataSourceMode,
    DataSourceRef,
    DataSourceStatus,
    DataSourceType,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationResult,
    UploadedCSVMaterializationStatus,
)

_SHARED_CORE = Path("src/mip/contracts/uploaded_csv_materialization.py")
_GEOX_ADAPTER = Path("src/mip/contracts/geox_uploaded_csv_adapter.py")
_FORBIDDEN_TOP_LEVEL = (
    "spend_delta",
    "delta_mu",
    "lift",
    "roi",
    "roas",
    "optimal_budget",
    "marginal_roi",
    "recommendation",
)


def test_required_enums_exist() -> None:
    assert PlanningMMMUploadedCSVRole.HISTORICAL_SPEND in PlanningMMMUploadedCSVRole
    assert PlanningMMMUploadedCSVAdapterStatus.ADAPTED in PlanningMMMUploadedCSVAdapterStatus
    assert PlanningMMMUploadedCSVAdapterIssueCode.CSV_REPARSE_AVOIDED in (
        PlanningMMMUploadedCSVAdapterIssueCode
    )


def test_planning_mmm_roles_not_in_shared_core() -> None:
    shared_source = _SHARED_CORE.read_text(encoding="utf-8")
    for role in (
        "HISTORICAL_SPEND",
        "HISTORICAL_OUTCOME",
        "CHANNEL_TAXONOMY",
        "BUDGET_CONSTRAINTS",
        "CALIBRATION_SIGNALS",
    ):
        assert role not in shared_source
    assert "PlanningMMMUploadedCSVRole" not in shared_source
    assert "historical_spend" not in shared_source


def test_geox_adapter_not_modified() -> None:
    geox_source = _GEOX_ADAPTER.read_text(encoding="utf-8")
    assert "HISTORICAL_SPEND" not in geox_source
    assert "CHANNEL_TAXONOMY" not in geox_source


def test_models_serialize() -> None:
    request = PlanningMMMUploadedCSVAdapterRequest(request_id="req-1")
    assert request.explicit_role_by_source_id == {}
    result = PlanningMMMUploadedCSVAdapterResult(
        request_id="req-1",
        status=PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MISSING_MATERIALIZATION_RESULT,
    )
    assert result.availability is None


def test_role_mapping_with_data_source_ref() -> None:
    source_ref = DataSourceRef(
        source_id="spend-1",
        source_mode=DataSourceMode.LOCAL_FILE_PATH_MANIFEST,
        source_type=DataSourceType.FILE,
        asset_type=DataAssetType.MEDIA_SPEND_DATA,
        uri_or_table_ref="/tmp/spend.csv",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=DataSourceStatus.DECLARED,
    )
    mapping = PlanningMMMUploadedCSVRoleMapping(
        source_id="spend-1",
        dataset_id="materialized:spend-1",
        role=PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
        role_source=PlanningMMMUploadedCSVRoleSource.EXPLICIT,
        data_source_ref=source_ref,
    )
    assert mapping.role == PlanningMMMUploadedCSVRole.HISTORICAL_SPEND


def test_result_no_top_level_metric_fields() -> None:
    schema = PlanningMMMUploadedCSVAdapterResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_PLANNING_MMM_UPLOADED_CSV_INPUT_PLAN_ARTIFACT == (
        "MIP_PLANNING_MMM_UPLOADED_CSV_INPUT_PLAN_001"
    )


def test_materialization_result_attachment() -> None:
    request = PlanningMMMUploadedCSVAdapterRequest(
        request_id="req-1",
        materialization_result=UploadedCSVMaterializationResult(
            request_id="mat-1",
            status=UploadedCSVMaterializationStatus.MATERIALIZED,
        ),
    )
    assert request.materialization_result is not None
