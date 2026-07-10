"""Tests for MMM runtime result ingestion workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.mmm_runtime_adapter import (
    MMMRuntimeArtifactHandoff,
    MMMRuntimeCallDecision,
    MMMRuntimeCallResult,
    MMMRuntimeCallStatus,
    MMMRuntimeFailurePacket,
)
from mip.contracts.mmm_runtime_result_ingestion import (
    MMMRuntimeDiagnosticsMetadataStatus,
    MMMRuntimeGovernanceRoutingStatus,
    MMMRuntimeResultIngestionIssueCode,
    MMMRuntimeResultIngestionRequest,
    MMMRuntimeResultIngestionResult,
    MMMRuntimeResultIngestionStatus,
)
from mip.workflows.mmm_runtime_result_ingestion import (
    ingest_mmm_runtime_result_metadata,
    summarize_mmm_runtime_result_ingestion,
)

_WORKFLOW_SOURCE = Path("src/mip/workflows/mmm_runtime_result_ingestion.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/mmm_runtime_result_ingestion.py")


def _handoff(
    *,
    external_run_id: str = "ext-run-1",
    model_artifact_uri: str | None = "s3://bucket/model.bin",
    manifest_uri: str | None = "s3://bucket/manifest.json",
    diagnostics_uri: str | None = "s3://bucket/diagnostics.json",
    runtime_logs_uri: str | None = "s3://bucket/logs.txt",
) -> MMMRuntimeArtifactHandoff:
    return MMMRuntimeArtifactHandoff(
        handoff_id="handoff-1",
        request_id="runtime-req-1",
        external_run_id=external_run_id,
        artifact_uris=["s3://bucket/output.json"],
        manifest_uri=manifest_uri,
        diagnostics_uri=diagnostics_uri,
        model_artifact_uri=model_artifact_uri,
        runtime_logs_uri=runtime_logs_uri,
    )


def _runtime_result(
    *,
    handoff: MMMRuntimeArtifactHandoff | None = _handoff(),
    status: MMMRuntimeCallStatus = MMMRuntimeCallStatus.EXTERNAL_RUNTIME_CALL_RECORDED,
    decision: MMMRuntimeCallDecision = MMMRuntimeCallDecision.RECORD_EXTERNAL_RUNTIME_RESULT,
    external_run_id: str | None = "ext-run-1",
    runtime_called: bool = True,
    failure_packet: MMMRuntimeFailurePacket | None = None,
) -> MMMRuntimeCallResult:
    return MMMRuntimeCallResult(
        request_id="runtime-req-1",
        status=status,
        decision=decision,
        runtime_called=runtime_called,
        external_run_id=external_run_id,
        artifact_handoff=handoff,
        failure_packet=failure_packet,
        lineage={"runtime_stage": "adapter"},
    )


def _ingest(
    *,
    runtime_result: MMMRuntimeCallResult | None = _runtime_result(),
    require_model_artifact_uri: bool = True,
    require_manifest_uri: bool = True,
    require_diagnostics_uri: bool = False,
    require_runtime_logs_uri: bool = False,
    create_governance_routing_reference: bool = True,
) -> MMMRuntimeResultIngestionResult:
    return ingest_mmm_runtime_result_metadata(
        MMMRuntimeResultIngestionRequest(
            request_id="ingest-req-1",
            runtime_call_result=runtime_result,
            require_model_artifact_uri=require_model_artifact_uri,
            require_manifest_uri=require_manifest_uri,
            require_diagnostics_uri=require_diagnostics_uri,
            require_runtime_logs_uri=require_runtime_logs_uri,
            create_governance_routing_reference=create_governance_routing_reference,
            lineage={"upstream": "runtime_adapter"},
        )
    )


def test_missing_runtime_result_blocks() -> None:
    result = _ingest(runtime_result=None)
    assert result.status == MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_RUNTIME_RESULT
    assert result.ready_for_governance_review is False


def test_runtime_failed_preserves_failure_packet_and_blocks_governance_review() -> None:
    packet = MMMRuntimeFailurePacket(
        failure_id="fail-1",
        request_id="runtime-req-1",
        status=MMMRuntimeCallStatus.EXTERNAL_RUNTIME_FAILED,
        error_code="runtime_failed",
        message="external runtime failed",
        blocked_reasons=["engine error"],
    )
    runtime = _runtime_result(
        handoff=None,
        status=MMMRuntimeCallStatus.EXTERNAL_RUNTIME_FAILED,
        decision=MMMRuntimeCallDecision.BLOCK_RUNTIME_CALL,
        runtime_called=False,
        failure_packet=packet,
    )
    result = _ingest(runtime_result=runtime)
    assert result.status == MMMRuntimeResultIngestionStatus.INGESTION_RUNTIME_FAILED
    assert result.failure_packet is packet
    assert result.ready_for_governance_review is False


def test_missing_artifact_handoff_blocks() -> None:
    runtime = MMMRuntimeCallResult(
        request_id="runtime-req-1",
        status=MMMRuntimeCallStatus.READY_TO_CALL_EXTERNAL_RUNTIME,
        decision=MMMRuntimeCallDecision.PREPARE_EXTERNAL_NEW_MODEL_RUN,
        artifact_handoff=None,
    )
    result = _ingest(runtime_result=runtime)
    assert result.status == (
        MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_ARTIFACT_HANDOFF
    )


def test_missing_external_run_id_blocks() -> None:
    handoff = MMMRuntimeArtifactHandoff.model_construct(
        handoff_id="handoff-1",
        request_id="runtime-req-1",
        external_run_id="",
        model_artifact_uri="s3://bucket/model.bin",
        manifest_uri="s3://bucket/manifest.json",
    )
    runtime = MMMRuntimeCallResult(
        request_id="runtime-req-1",
        status=MMMRuntimeCallStatus.READY_TO_CALL_EXTERNAL_RUNTIME,
        decision=MMMRuntimeCallDecision.PREPARE_EXTERNAL_NEW_MODEL_RUN,
        runtime_called=False,
        external_run_id=None,
        artifact_handoff=handoff,
        lineage={"runtime_stage": "adapter"},
    )
    result = _ingest(runtime_result=runtime)
    assert result.status == (
        MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_EXTERNAL_RUN_ID
    )


def test_missing_required_model_artifact_uri_blocks() -> None:
    runtime = _runtime_result(handoff=_handoff(model_artifact_uri=None))
    result = _ingest(runtime_result=runtime)
    assert result.status == (
        MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_MODEL_ARTIFACT_URI
    )


def test_missing_required_manifest_uri_blocks() -> None:
    runtime = _runtime_result(handoff=_handoff(manifest_uri=None))
    result = _ingest(runtime_result=runtime)
    assert result.status == MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_MANIFEST_URI


def test_missing_optional_diagnostics_uri_warns() -> None:
    runtime = _runtime_result(handoff=_handoff(diagnostics_uri=None))
    result = _ingest(runtime_result=runtime)
    assert result.status == MMMRuntimeResultIngestionStatus.INGESTION_READY_WITH_WARNINGS
    assert any("diagnostics URI" in warning for warning in result.warnings)


def test_missing_required_diagnostics_uri_blocks() -> None:
    runtime = _runtime_result(handoff=_handoff(diagnostics_uri=None))
    result = _ingest(runtime_result=runtime, require_diagnostics_uri=True)
    assert result.status == MMMRuntimeResultIngestionStatus.INGESTION_DIAGNOSTICS_METADATA_MISSING
    assert result.diagnostics_metadata_status == (
        MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_MISSING
    )


def test_missing_optional_runtime_logs_uri_warns() -> None:
    runtime = _runtime_result(handoff=_handoff(runtime_logs_uri=None))
    result = _ingest(runtime_result=runtime)
    assert result.status == MMMRuntimeResultIngestionStatus.INGESTION_READY_WITH_WARNINGS
    assert any("runtime logs URI" in warning for warning in result.warnings)


def test_successful_ingestion_ready_for_governance_review() -> None:
    result = _ingest()
    assert result.status == MMMRuntimeResultIngestionStatus.INGESTION_READY_FOR_GOVERNANCE_REVIEW
    assert result.ready_for_governance_review is True


def test_successful_ingestion_with_warnings() -> None:
    runtime = _runtime_result(
        handoff=_handoff(diagnostics_uri=None, runtime_logs_uri=None),
    )
    result = _ingest(runtime_result=runtime)
    assert result.status == MMMRuntimeResultIngestionStatus.INGESTION_READY_WITH_WARNINGS
    assert result.ready_for_governance_review is True


def test_diagnostics_metadata_created_uri_only() -> None:
    result = _ingest()
    assert result.diagnostics_metadata is not None
    assert result.diagnostics_metadata.diagnostics_uri == "s3://bucket/diagnostics.json"
    assert result.diagnostics_metadata.metadata.get("uri_metadata_only") is True


def test_governance_routing_reference_created_metadata_only() -> None:
    result = _ingest()
    assert result.governance_routing_reference is not None
    assert result.governance_routing_reference.trust_report_candidate_reference == (
        "trust_report:candidate:ext-run-1"
    )
    assert result.governance_routing_reference.metadata.get(
        "metadata_only_candidate_reference"
    ) is True


def test_governance_routing_disabled_does_not_create_reference() -> None:
    result = _ingest(create_governance_routing_reference=False)
    assert result.governance_routing_reference is None
    assert result.ready_for_governance_review is False
    assert result.governance_routing_status == MMMRuntimeGovernanceRoutingStatus.DEFERRED


def test_lineage_preserved() -> None:
    result = _ingest()
    assert result.lineage.get("upstream") == "runtime_adapter"
    assert result.lineage.get("runtime_stage") == "adapter"
    assert result.lineage.get("ingestion_stage") == "mmm_runtime_result_ingestion"


def test_no_artifact_loading_in_sources() -> None:
    forbidden = (
        "open(",
        "read_text",
        "read_bytes",
        "json.load",
        "pandas",
        "pd.read",
        "import requests",
        "import httpx",
        "import urllib",
        "import socket",
        "import pickle",
        "import joblib",
        "mlflow.pyfunc.load_model",
        "load_model(",
        ".fit(",
        ".predict(",
        ".sample(",
        "DecisionSurface(",
        "RecommendationContract(",
        "TrustReport(",
    )
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("#"):
                continue
            for token in forbidden:
                assert token not in line, f"{token} in {path}: {line}"


def test_boundary_issue_codes_present() -> None:
    result = _ingest()
    assert MMMRuntimeResultIngestionIssueCode.NO_ARTIFACT_LOADING in result.issues
    assert MMMRuntimeResultIngestionIssueCode.NO_DIAGNOSTICS_PARSING in result.issues
    assert MMMRuntimeResultIngestionIssueCode.NO_TRUST_REPORT_CONSTRUCTION in result.issues
    assert MMMRuntimeResultIngestionIssueCode.NO_CLAIM_AUTHORIZATION in result.issues


def test_summarize_returns_metadata_only() -> None:
    result = _ingest()
    summary = summarize_mmm_runtime_result_ingestion(result)
    assert summary["ready_for_governance_review"] is True
    assert "recommendation" not in summary
