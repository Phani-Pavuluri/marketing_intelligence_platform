"""Tests for MMM runtime result ingestion contracts."""

from __future__ import annotations

from mip.contracts import (
    FORBIDDEN_MMM_RUNTIME_RESULT_INGESTION_RESULT_FIELD_NAMES,
    RECOMMENDED_NEXT_MMM_ARTIFACT_GOVERNANCE_ROUTING_GATE_AUDIT_ARTIFACT,
    MMMRuntimeDiagnosticsMetadata,
    MMMRuntimeDiagnosticsMetadataStatus,
    MMMRuntimeGovernanceRoutingReference,
    MMMRuntimeGovernanceRoutingStatus,
    MMMRuntimeResultIngestionIssueCode,
    MMMRuntimeResultIngestionRequest,
    MMMRuntimeResultIngestionResult,
    MMMRuntimeResultIngestionStatus,
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
    "budget_recommendation",
)


def test_required_enums_exist() -> None:
    assert (
        MMMRuntimeResultIngestionStatus.INGESTION_READY_FOR_GOVERNANCE_REVIEW
        in MMMRuntimeResultIngestionStatus
    )
    assert (
        MMMRuntimeGovernanceRoutingStatus.READY_FOR_GOVERNANCE_REVIEW
        in MMMRuntimeGovernanceRoutingStatus
    )
    assert MMMRuntimeResultIngestionIssueCode.NO_ARTIFACT_LOADING in (
        MMMRuntimeResultIngestionIssueCode
    )


def test_request_and_result_models_serialize() -> None:
    request = MMMRuntimeResultIngestionRequest(request_id="ingest-req-1")
    assert request.require_model_artifact_uri is True
    assert request.require_manifest_uri is True
    assert request.require_diagnostics_uri is False
    assert request.create_governance_routing_reference is True
    result = MMMRuntimeResultIngestionResult(
        request_id="ingest-req-1",
        status=MMMRuntimeResultIngestionStatus.INGESTION_DEFERRED,
        diagnostics_metadata_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_DEFERRED,
        governance_routing_status=MMMRuntimeGovernanceRoutingStatus.DEFERRED,
    )
    assert result.ready_for_governance_review is False


def test_diagnostics_metadata_stores_uris_only() -> None:
    metadata = MMMRuntimeDiagnosticsMetadata(
        diagnostics_metadata_id="diag-meta-1",
        external_run_id="ext-run-1",
        diagnostics_uri="s3://bucket/diagnostics.json",
        manifest_uri="s3://bucket/manifest.json",
        runtime_logs_uri="s3://bucket/logs.txt",
        diagnostics_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_PRESENT,
        diagnostic_artifact_uris=["s3://bucket/diagnostics.json"],
    )
    assert metadata.diagnostics_uri == "s3://bucket/diagnostics.json"
    assert metadata.metadata == {}


def test_governance_routing_reference_stores_candidate_references_only() -> None:
    reference = MMMRuntimeGovernanceRoutingReference(
        routing_id="routing-1",
        external_run_id="ext-run-1",
        model_artifact_uri="s3://bucket/model.bin",
        trust_report_candidate_reference="trust_report:candidate:ext-run-1",
        decision_surface_candidate_reference="decision_surface:candidate:ext-run-1",
        governance_routing_status=MMMRuntimeGovernanceRoutingStatus.READY_FOR_GOVERNANCE_REVIEW,
    )
    assert reference.trust_report_candidate_reference is not None
    assert reference.trust_report_candidate_reference.startswith("trust_report:candidate:")


def test_failure_packet_metadata_preserved_on_result() -> None:
    from mip.contracts.mmm_runtime_adapter import (
        MMMRuntimeCallStatus,
        MMMRuntimeFailurePacket,
    )

    packet = MMMRuntimeFailurePacket(
        failure_id="fail-1",
        request_id="ingest-req-2",
        status=MMMRuntimeCallStatus.EXTERNAL_RUNTIME_FAILED,
        error_code="runtime_failed",
        message="failed",
    )
    result = MMMRuntimeResultIngestionResult(
        request_id="ingest-req-2",
        status=MMMRuntimeResultIngestionStatus.INGESTION_RUNTIME_FAILED,
        diagnostics_metadata_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_FAILED,
        governance_routing_status=MMMRuntimeGovernanceRoutingStatus.BLOCKED_RUNTIME_FAILED,
        failure_packet=packet,
    )
    assert result.failure_packet is packet


def test_no_forbidden_top_level_fields() -> None:
    for field_name in MMMRuntimeResultIngestionResult.model_fields:
        assert field_name not in _FORBIDDEN_TOP_LEVEL
    assert "roi" in FORBIDDEN_MMM_RUNTIME_RESULT_INGESTION_RESULT_FIELD_NAMES


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_MMM_ARTIFACT_GOVERNANCE_ROUTING_GATE_AUDIT_ARTIFACT == (
        "MIP_MMM_ARTIFACT_GOVERNANCE_ROUTING_GATE_AUDIT_001"
    )
