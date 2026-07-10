"""Tests for Planning/MMM tabular source adapter compatibility contracts."""

from __future__ import annotations

from datetime import UTC, datetime

from mip.contracts import (
    PlanningMMMTabularSourceAdapterIssueCode,
    PlanningMMMTabularSourceAdapterRequest,
    PlanningMMMTabularSourceAdapterResult,
    PlanningMMMTabularSourceAdapterStatus,
    PlanningMMMTabularSourceRoleMapping,
    PlanningMMMTabularSourceRoleSource,
    PlanningMMMUploadedCSVRole,
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
from mip.contracts.tabular_source_reference import (
    TabularSourceAccessMode,
    TabularSourceMaterializationMode,
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
    assert PlanningMMMTabularSourceAdapterStatus.ADAPTED in (
        PlanningMMMTabularSourceAdapterStatus
    )
    assert PlanningMMMTabularSourceAdapterIssueCode.NO_MODEL_EXECUTION in (
        PlanningMMMTabularSourceAdapterIssueCode
    )
    assert PlanningMMMTabularSourceRoleSource.EXPLICIT in PlanningMMMTabularSourceRoleSource


def test_models_serialize() -> None:
    request = PlanningMMMTabularSourceAdapterRequest(request_id="req-1")
    assert request.tabular_source_result is None
    result = PlanningMMMTabularSourceAdapterResult(
        request_id="req-1",
        status=PlanningMMMTabularSourceAdapterStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT,
    )
    assert result.availability is None


def test_planning_mmm_role_enum_reused() -> None:
    mapping = PlanningMMMTabularSourceRoleMapping(
        source_id="spend",
        source_type=TabularSourceType.UPLOADED_CSV,
        role=PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
        role_source=PlanningMMMTabularSourceRoleSource.EXPLICIT,
    )
    assert mapping.role == PlanningMMMUploadedCSVRole.HISTORICAL_SPEND


def test_result_can_include_data_source_refs_and_tabular_references() -> None:
    source_ref = DataSourceRef(
        source_id="spend",
        source_mode=DataSourceMode.LOCAL_FILE_PATH_MANIFEST,
        source_type=DataSourceType.FILE,
        asset_type=DataAssetType.MEDIA_SPEND_DATA,
        uri_or_table_ref="/tmp/spend.csv",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=DataSourceStatus.DECLARED,
    )
    tabular_ref = TabularSourceReference(
        source_id="spend",
        source_type=TabularSourceType.UPLOADED_CSV,
        access_mode=TabularSourceAccessMode.LOCAL_FILE,
        materialization_mode=TabularSourceMaterializationMode.MATERIALIZED_IN_MEMORY,
        data_source_ref=source_ref,
    )
    result = PlanningMMMTabularSourceAdapterResult(
        request_id="req-1",
        status=PlanningMMMTabularSourceAdapterStatus.ADAPTED,
        data_source_refs=[source_ref],
        tabular_source_references=[tabular_ref],
    )
    assert result.data_source_refs[0].source_id == "spend"
    assert result.tabular_source_references[0].source_id == "spend"


def test_result_no_top_level_metric_fields() -> None:
    schema = PlanningMMMTabularSourceAdapterResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_exports_from_mip_contracts() -> None:
    assert PlanningMMMTabularSourceAdapterStatus.BLOCKED_AMBIGUOUS_ROLE in (
        PlanningMMMTabularSourceAdapterStatus
    )
