"""Tests for GeoX uploaded CSV runtime bridge contracts."""

from __future__ import annotations

from mip.contracts import (
    RECOMMENDED_NEXT_PLANNING_UPLOADED_CSV_ADAPTER_ARTIFACT,
    GeoXUploadedCSVRuntimeBridgeIssueCode,
    GeoXUploadedCSVRuntimeBridgeRequest,
    GeoXUploadedCSVRuntimeBridgeResult,
    GeoXUploadedCSVRuntimeBridgeStatus,
    GeoXUploadedCSVRuntimeColumnMapping,
)
from mip.contracts.geox_panel_exp_runtime_call import (
    GeoXPostTestSpendEvidenceArtifact,
    GeoXTrustedReadoutSpendHandoffArtifact,
)
from mip.contracts.geox_uploaded_csv_adapter import (
    GeoXUploadedCSVAdapterResult,
    GeoXUploadedCSVAdapterStatus,
)

_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi", "roas")


def test_required_enums_exist() -> None:
    assert GeoXUploadedCSVRuntimeBridgeStatus.RUNTIME_COMPLETED in (
        GeoXUploadedCSVRuntimeBridgeStatus
    )
    assert GeoXUploadedCSVRuntimeBridgeIssueCode.CSV_REPARSE_AVOIDED in (
        GeoXUploadedCSVRuntimeBridgeIssueCode
    )


def test_models_serialize() -> None:
    request = GeoXUploadedCSVRuntimeBridgeRequest(
        request_id="req-1",
        experiment_id="exp-1",
        experiment_type="holdout",
        post_period_start="2026-01-01",
        post_period_end="2026-01-31",
        column_mapping=GeoXUploadedCSVRuntimeColumnMapping(
            spend_date_column="date",
            spend_geo_column="dma",
            spend_amount_column="spend",
        ),
    )
    assert request.assignment_mapping == {}
    result = GeoXUploadedCSVRuntimeBridgeResult(
        request_id="req-1",
        status=GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_ADAPTER_RESULT,
    )
    assert result.evidence_artifact is None


def test_artifact_fields_compatible_with_runtime_call_contracts() -> None:
    evidence = GeoXPostTestSpendEvidenceArtifact(
        artifact_id="evidence:exp-1",
        experiment_id="exp-1",
        readiness_status="READY",
        package_output_summary={"package_computed_spend_delta": 100.0},
    )
    handoff = GeoXTrustedReadoutSpendHandoffArtifact(
        artifact_id="handoff:exp-1",
        experiment_id="exp-1",
        spend_readiness_summary={"readiness_status": "READY"},
    )
    result = GeoXUploadedCSVRuntimeBridgeResult(
        request_id="req-1",
        status=GeoXUploadedCSVRuntimeBridgeStatus.RUNTIME_COMPLETED,
        evidence_artifact=evidence,
        trusted_handoff_artifact=handoff,
        package_output_summary=dict(evidence.package_output_summary),
    )
    assert isinstance(result.evidence_artifact, GeoXPostTestSpendEvidenceArtifact)
    assert isinstance(result.trusted_handoff_artifact, GeoXTrustedReadoutSpendHandoffArtifact)


def test_result_no_top_level_metric_fields() -> None:
    schema = GeoXUploadedCSVRuntimeBridgeResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_PLANNING_UPLOADED_CSV_ADAPTER_ARTIFACT == (
        "MIP_PLANNING_MMM_UPLOADED_CSV_ADAPTER_001"
    )


def test_adapter_result_attachment() -> None:
    request = GeoXUploadedCSVRuntimeBridgeRequest(
        request_id="req-1",
        adapter_result=GeoXUploadedCSVAdapterResult(
            request_id="adapt-1",
            status=GeoXUploadedCSVAdapterStatus.ADAPTED,
        ),
        experiment_id="exp-1",
        experiment_type="holdout",
        post_period_start="2026-01-01",
        post_period_end="2026-01-31",
        column_mapping=GeoXUploadedCSVRuntimeColumnMapping(
            spend_date_column="date",
            spend_geo_column="dma",
            spend_amount_column="spend",
        ),
    )
    assert request.adapter_result is not None
