"""Tests for GeoX tabular source adapter compatibility contracts."""

from __future__ import annotations

from mip.contracts import (
    RECOMMENDED_NEXT_GEOX_READOUT_RESULT_ROUTING_FROM_TABULAR_SOURCE_ARTIFACT,
    RECOMMENDED_NEXT_TABULAR_SOURCE_REUSE_COMPLETION_AUDIT_ARTIFACT,
    GeoXTabularSourceAdapterIssueCode,
    GeoXTabularSourceAdapterRequest,
    GeoXTabularSourceAdapterResult,
    GeoXTabularSourceAdapterStatus,
    GeoXTabularSourceInputAvailability,
    GeoXTabularSourceRoleMapping,
    GeoXTabularSourceRoleSource,
    GeoXUploadedCSVRole,
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
    "recommendation",
    "DecisionSurface",
    "TrustReport",
    "claim_authorization",
)


def test_required_enums_exist() -> None:
    assert GeoXTabularSourceAdapterStatus.ADAPTED in GeoXTabularSourceAdapterStatus
    assert GeoXTabularSourceRoleSource.EXPLICIT in GeoXTabularSourceRoleSource
    assert GeoXTabularSourceAdapterIssueCode.NO_PANEL_EXP_RUNTIME_EXECUTION in (
        GeoXTabularSourceAdapterIssueCode
    )


def test_models_serialize() -> None:
    request = GeoXTabularSourceAdapterRequest(request_id="req-1")
    assert request.explicit_role_by_source_id == {}
    result = GeoXTabularSourceAdapterResult(
        request_id="req-1",
        status=GeoXTabularSourceAdapterStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT,
    )
    assert result.availability is None


def test_geox_role_enum_reused() -> None:
    mapping = GeoXTabularSourceRoleMapping(
        source_id="kpi",
        source_type=TabularSourceType.UPLOADED_CSV,
        role=GeoXUploadedCSVRole.KPI_PANEL,
        role_source=GeoXTabularSourceRoleSource.EXPLICIT,
    )
    assert mapping.role == GeoXUploadedCSVRole.KPI_PANEL


def test_result_can_include_data_source_refs_and_tabular_refs() -> None:
    from datetime import UTC, datetime

    source_ref = DataSourceRef(
        source_id="kpi",
        source_mode=DataSourceMode.LOCAL_FILE_PATH_MANIFEST,
        source_type=DataSourceType.FILE,
        asset_type=DataAssetType.OUTCOME_KPI_DATA,
        uri_or_table_ref="/tmp/kpi.csv",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=DataSourceStatus.DECLARED,
    )
    tabular_ref = TabularSourceReference(
        source_id="kpi",
        source_type=TabularSourceType.UPLOADED_CSV,
        access_mode=TabularSourceAccessMode.LOCAL_FILE,
        materialization_mode=TabularSourceMaterializationMode.MATERIALIZED_IN_MEMORY,
        data_source_ref=source_ref,
    )
    availability = GeoXTabularSourceInputAvailability(
        has_kpi_panel=True,
        kpi_panel_source_id="kpi",
        data_source_refs=[source_ref],
        tabular_source_references=[tabular_ref],
    )
    result = GeoXTabularSourceAdapterResult(
        request_id="req-1",
        status=GeoXTabularSourceAdapterStatus.ADAPTED,
        availability=availability,
        data_source_refs=[source_ref],
        tabular_source_references=[tabular_ref],
    )
    assert result.data_source_refs[0].source_id == "kpi"
    assert result.tabular_source_references[0].source_id == "kpi"


def test_result_no_forbidden_top_level_fields() -> None:
    schema = GeoXTabularSourceAdapterResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_TABULAR_SOURCE_REUSE_COMPLETION_AUDIT_ARTIFACT == (
        "MIP_TABULAR_SOURCE_REUSE_COMPLETION_AUDIT_001"
    )
    assert RECOMMENDED_NEXT_GEOX_READOUT_RESULT_ROUTING_FROM_TABULAR_SOURCE_ARTIFACT == (
        "MIP_GEOX_READOUT_RESULT_ROUTING_FROM_TABULAR_SOURCE_001"
    )
