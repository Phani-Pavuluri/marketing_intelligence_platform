"""Tests for MMM runtime adapter contracts."""

from __future__ import annotations

from mip.contracts import (
    FORBIDDEN_MMM_RUNTIME_CALL_RESULT_FIELD_NAMES,
    RECOMMENDED_NEXT_MMM_RUNTIME_RESULT_INGESTION_AND_DIAGNOSTICS_AUDIT_ARTIFACT,
    MMMRuntimeArtifactHandoff,
    MMMRuntimeCallDecision,
    MMMRuntimeCallIssueCode,
    MMMRuntimeCallRequest,
    MMMRuntimeCallResult,
    MMMRuntimeCallStatus,
    MMMRuntimeEngineKind,
    MMMRuntimeFailurePacket,
    MMMRuntimeReference,
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
    assert MMMRuntimeCallStatus.READY_TO_CALL_EXTERNAL_RUNTIME in MMMRuntimeCallStatus
    assert MMMRuntimeCallDecision.PREPARE_EXTERNAL_NEW_MODEL_RUN in MMMRuntimeCallDecision
    assert MMMRuntimeEngineKind.EXTERNAL_MMM_ENGINE in MMMRuntimeEngineKind
    assert MMMRuntimeCallIssueCode.NO_MODEL_EXECUTION in MMMRuntimeCallIssueCode


def test_request_and_result_models_serialize() -> None:
    request = MMMRuntimeCallRequest(request_id="runtime-req-1")
    assert request.requested_run_type == "blocked"
    result = MMMRuntimeCallResult(
        request_id="runtime-req-1",
        status=MMMRuntimeCallStatus.DEFERRED,
        decision=MMMRuntimeCallDecision.DEFER_RUNTIME_CALL,
    )
    assert result.runtime_called is False


def test_runtime_reference_serializes() -> None:
    reference = MMMRuntimeReference(
        runtime_id="mmm-runtime:1",
        runtime_kind=MMMRuntimeEngineKind.EXTERNAL_BAYESIAN_MMM_ENGINE,
        runtime_name="bayesian_mmm",
    )
    assert reference.runtime_kind == MMMRuntimeEngineKind.EXTERNAL_BAYESIAN_MMM_ENGINE


def test_failure_packet_serializes() -> None:
    packet = MMMRuntimeFailurePacket(
        failure_id="fail-1",
        request_id="runtime-req-2",
        status=MMMRuntimeCallStatus.BLOCKED_BY_ELIGIBILITY,
        error_code="eligibility_blocked",
        message="blocked",
        blocked_reasons=["eligibility blocked"],
    )
    assert packet.retryable is False


def test_artifact_handoff_stores_uris_only() -> None:
    handoff = MMMRuntimeArtifactHandoff(
        handoff_id="handoff-1",
        request_id="runtime-req-3",
        external_run_id="ext-run-1",
        artifact_uris=["s3://bucket/model.json"],
        manifest_uri="s3://bucket/manifest.json",
        diagnostics_uri="s3://bucket/diagnostics.json",
        model_artifact_uri="s3://bucket/model.bin",
        runtime_logs_uri="s3://bucket/logs.txt",
    )
    assert handoff.artifact_uris == ["s3://bucket/model.json"]
    assert handoff.model_artifact_uri == "s3://bucket/model.bin"


def test_no_forbidden_top_level_fields() -> None:
    for field_name in MMMRuntimeCallResult.model_fields:
        assert field_name not in _FORBIDDEN_TOP_LEVEL
    assert "roi" in FORBIDDEN_MMM_RUNTIME_CALL_RESULT_FIELD_NAMES


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_MMM_RUNTIME_RESULT_INGESTION_AND_DIAGNOSTICS_AUDIT_ARTIFACT == (
        "MIP_MMM_RUNTIME_RESULT_INGESTION_AND_DIAGNOSTICS_AUDIT_001"
    )
