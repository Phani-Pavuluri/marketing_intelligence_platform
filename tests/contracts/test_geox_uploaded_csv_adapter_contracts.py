"""Tests for GeoX uploaded CSV adapter contracts."""

from __future__ import annotations

from pathlib import Path

from mip.contracts import (
    RECOMMENDED_NEXT_GEOX_UPLOADED_CSV_RUNTIME_BRIDGE_ARTIFACT,
    GeoXUploadedCSVAdapterIssueCode,
    GeoXUploadedCSVAdapterRequest,
    GeoXUploadedCSVAdapterResult,
    GeoXUploadedCSVAdapterStatus,
    GeoXUploadedCSVRole,
    GeoXUploadedCSVRoleMapping,
    GeoXUploadedCSVRoleSource,
)
from mip.contracts.geox_readout_input_resolution import (
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationResult,
    UploadedCSVMaterializationStatus,
)

_SHARED_CORE = Path("src/mip/contracts/uploaded_csv_materialization.py")
_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi", "roas")

_REQUIRED_ROLES = {
    GeoXUploadedCSVRole.KPI_PANEL,
    GeoXUploadedCSVRole.SPEND_PANEL,
    GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    GeoXUploadedCSVRole.EXPERIMENT_METADATA,
    GeoXUploadedCSVRole.UNKNOWN,
}


def test_required_enums_exist() -> None:
    assert _REQUIRED_ROLES.issubset(set(GeoXUploadedCSVRole))
    assert GeoXUploadedCSVAdapterStatus.ADAPTED in GeoXUploadedCSVAdapterStatus
    assert GeoXUploadedCSVAdapterIssueCode.SOURCE_INSPECTION_COMPATIBLE in (
        GeoXUploadedCSVAdapterIssueCode
    )


def test_geox_roles_not_in_shared_core() -> None:
    shared_source = _SHARED_CORE.read_text(encoding="utf-8")
    for role in ("KPI_PANEL", "SPEND_PANEL", "ASSIGNMENT_TABLE", "EXPERIMENT_METADATA"):
        assert role not in shared_source


def test_models_serialize() -> None:
    request = GeoXUploadedCSVAdapterRequest(request_id="req-1")
    assert request.explicit_role_by_source_id == {}
    result = GeoXUploadedCSVAdapterResult(
        request_id="req-1",
        status=GeoXUploadedCSVAdapterStatus.BLOCKED_MISSING_MATERIALIZATION_RESULT,
    )
    assert result.availability is None


def test_role_mapping_with_dataset_reference() -> None:
    dataset_ref = DatasetReference(
        dataset_ref_id="kpi-1",
        source_type=DatasetSourceType.UPLOADED_CSV,
        semantic_type=DatasetSemanticType.KPI_PANEL,
        source_uri_or_handle="/tmp/kpi.csv",
        file_name_or_table_name="kpi.csv",
        declared_or_detected_columns=["date", "dma", "conversions"],
        classification_confidence=1.0,
    )
    mapping = GeoXUploadedCSVRoleMapping(
        source_id="kpi-1",
        dataset_id="materialized:kpi-1",
        role=GeoXUploadedCSVRole.KPI_PANEL,
        role_source=GeoXUploadedCSVRoleSource.EXPLICIT,
        dataset_reference=dataset_ref,
    )
    assert mapping.role == GeoXUploadedCSVRole.KPI_PANEL


def test_result_no_top_level_metric_fields() -> None:
    schema = GeoXUploadedCSVAdapterResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_GEOX_UPLOADED_CSV_RUNTIME_BRIDGE_ARTIFACT == (
        "MIP_GEOX_READOUT_UPLOADED_CSV_RUNTIME_BRIDGE_001"
    )


def test_materialization_result_attachment() -> None:
    request = GeoXUploadedCSVAdapterRequest(
        request_id="req-1",
        materialization_result=UploadedCSVMaterializationResult(
            request_id="mat-1",
            status=UploadedCSVMaterializationStatus.MATERIALIZED,
        ),
    )
    assert request.materialization_result is not None
