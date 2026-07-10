"""Tests for MMM artifact governance and use-readiness workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from mip.contracts.mmm_artifact_governance_use_readiness import (
    MMMArtifactGovernanceRoute,
    MMMArtifactGovernanceUseReadinessIssueCode,
    MMMArtifactGovernanceUseReadinessRequest,
    MMMArtifactGovernanceUseReadinessResult,
    MMMArtifactGovernanceUseReadinessStatus,
    MMMArtifactUseReadiness,
)
from mip.contracts.mmm_existing_model_availability import (
    MMMModelAllowedUse,
    MMMModelArtifact,
    MMMModelDiagnosticStatus,
    MMMModelPromotionStatus,
)
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
    MMMRuntimeResultIngestionRequest,
    MMMRuntimeResultIngestionResult,
    MMMRuntimeResultIngestionStatus,
)
from mip.workflows.mmm_artifact_governance_use_readiness import (
    evaluate_mmm_artifact_governance_and_use_readiness,
    summarize_mmm_artifact_governance_and_use_readiness,
)
from mip.workflows.mmm_runtime_result_ingestion import ingest_mmm_runtime_result_metadata

_WORKFLOW_SOURCE = Path("src/mip/workflows/mmm_artifact_governance_use_readiness.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/mmm_artifact_governance_use_readiness.py")


def _handoff(
    *,
    model_artifact_uri: str | None = "s3://bucket/model.bin",
    manifest_uri: str | None = "s3://bucket/manifest.json",
    diagnostics_uri: str | None = "s3://bucket/diagnostics.json",
) -> MMMRuntimeArtifactHandoff:
    return MMMRuntimeArtifactHandoff(
        handoff_id="handoff-1",
        request_id="runtime-req-1",
        external_run_id="ext-run-1",
        artifact_uris=["s3://bucket/output.json"],
        model_artifact_uri=model_artifact_uri,
        manifest_uri=manifest_uri,
        diagnostics_uri=diagnostics_uri,
        runtime_logs_uri="s3://bucket/logs.txt",
    )


def _ready_ingestion(
    *,
    model_artifact_uri: str | None = "s3://bucket/model.bin",
    manifest_uri: str | None = "s3://bucket/manifest.json",
    diagnostics_uri: str | None = "s3://bucket/diagnostics.json",
    require_model_artifact_uri: bool = True,
    require_manifest_uri: bool = True,
    require_diagnostics_uri: bool = False,
) -> MMMRuntimeResultIngestionResult:
    return ingest_mmm_runtime_result_metadata(
        MMMRuntimeResultIngestionRequest(
            request_id="ingest-req-1",
            runtime_call_result=MMMRuntimeCallResult(
                request_id="runtime-req-1",
                status=MMMRuntimeCallStatus.EXTERNAL_RUNTIME_CALL_RECORDED,
                decision=MMMRuntimeCallDecision.RECORD_EXTERNAL_RUNTIME_RESULT,
                runtime_called=True,
                external_run_id="ext-run-1",
                artifact_handoff=_handoff(
                    model_artifact_uri=model_artifact_uri,
                    manifest_uri=manifest_uri,
                    diagnostics_uri=diagnostics_uri,
                ),
                lineage={"runtime_stage": "adapter"},
            ),
            require_model_artifact_uri=require_model_artifact_uri,
            require_manifest_uri=require_manifest_uri,
            require_diagnostics_uri=require_diagnostics_uri,
            lineage={"upstream": "runtime_adapter"},
        )
    )


def _model_artifact(
    *,
    promotion_status: MMMModelPromotionStatus = MMMModelPromotionStatus.PROMOTED_FOR_PLANNING,
    diagnostic_status: MMMModelDiagnosticStatus = MMMModelDiagnosticStatus.PASSED,
    allowed_uses: list[MMMModelAllowedUse] | None = None,
    decision_surface_id: str | None = "surface-1",
) -> MMMModelArtifact:
    return MMMModelArtifact(
        model_id="mmm-model-1",
        artifact_fingerprint="fp-1",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        artifact_uri="s3://bucket/model.bin",
        promotion_status=promotion_status,
        diagnostic_status=diagnostic_status,
        allowed_uses=allowed_uses
        or [MMMModelAllowedUse.BUDGET_PLANNING, MMMModelAllowedUse.SCENARIO_SIMULATION],
        decision_surface_id=decision_surface_id,
        trust_report_id="trust-1",
    )


def _evaluate(
    *,
    ingestion: MMMRuntimeResultIngestionResult | None = None,
    model_artifact: MMMModelArtifact | None = None,
    require_model_artifact: bool = False,
    require_model_artifact_uri: bool = True,
    require_manifest_uri: bool = True,
    require_diagnostics_uri: bool = False,
) -> MMMArtifactGovernanceUseReadinessResult:
    return evaluate_mmm_artifact_governance_and_use_readiness(
        MMMArtifactGovernanceUseReadinessRequest(
            request_id="gov-req-1",
            runtime_ingestion_result=ingestion,
            model_artifact=model_artifact,
            require_model_artifact=require_model_artifact,
            require_model_artifact_uri=require_model_artifact_uri,
            require_manifest_uri=require_manifest_uri,
            require_diagnostics_uri=require_diagnostics_uri,
            lineage={"gate_stage": "governance_use_readiness"},
        )
    )


def test_missing_runtime_ingestion_result_blocks() -> None:
    result = _evaluate(ingestion=None)
    assert result.status == (
        MMMArtifactGovernanceUseReadinessStatus.MISSING_RUNTIME_INGESTION_RESULT
    )
    assert result.planning_ready is False


def test_runtime_failed_blocks_trust_and_surface_routes() -> None:
    packet = MMMRuntimeFailurePacket(
        failure_id="fail-1",
        request_id="runtime-req-1",
        status=MMMRuntimeCallStatus.EXTERNAL_RUNTIME_FAILED,
        error_code="runtime_failed",
        message="failed",
    )
    ingestion = ingest_mmm_runtime_result_metadata(
        MMMRuntimeResultIngestionRequest(
            request_id="ingest-failed",
            runtime_call_result=MMMRuntimeCallResult(
                request_id="runtime-req-1",
                status=MMMRuntimeCallStatus.EXTERNAL_RUNTIME_FAILED,
                decision=MMMRuntimeCallDecision.BLOCK_RUNTIME_CALL,
                runtime_called=False,
                failure_packet=packet,
            ),
        )
    )
    result = _evaluate(ingestion=ingestion)
    assert result.status == MMMArtifactGovernanceUseReadinessStatus.RUNTIME_FAILED
    assert result.ready_for_trust_report_review is False
    assert result.ready_for_decision_surface_review is False


def test_runtime_ingestion_not_ready_blocks() -> None:
    ingestion = MMMRuntimeResultIngestionResult(
        request_id="ingest-blocked",
        status=MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_ARTIFACT_HANDOFF,
        diagnostics_metadata_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_DEFERRED,
        governance_routing_status=(
            MMMRuntimeGovernanceRoutingStatus.BLOCKED_MISSING_REQUIRED_ARTIFACTS
        ),
        ready_for_governance_review=False,
        blocked_reasons=["artifact handoff is missing"],
    )
    result = _evaluate(ingestion=ingestion)
    assert result.status == MMMArtifactGovernanceUseReadinessStatus.BLOCKED
    assert result.planning_ready is False


def test_missing_required_model_artifact_uri_blocks() -> None:
    result = _evaluate(
        ingestion=_ready_ingestion(
            model_artifact_uri=None,
            require_model_artifact_uri=False,
        )
    )
    assert result.status == (
        MMMArtifactGovernanceUseReadinessStatus.MISSING_REQUIRED_ARTIFACT_METADATA
    )


def test_missing_required_manifest_uri_blocks() -> None:
    result = _evaluate(
        ingestion=_ready_ingestion(
            manifest_uri=None,
            require_manifest_uri=False,
        )
    )
    assert result.status == (
        MMMArtifactGovernanceUseReadinessStatus.MISSING_REQUIRED_ARTIFACT_METADATA
    )


def test_missing_optional_diagnostics_uri_warns() -> None:
    result = _evaluate(ingestion=_ready_ingestion(diagnostics_uri=None))
    assert result.status == (
        MMMArtifactGovernanceUseReadinessStatus.READY_FOR_GOVERNANCE_REVIEW_WITH_WARNINGS
    )
    assert any("diagnostics URI" in warning for warning in result.warnings)


def test_missing_required_diagnostics_uri_blocks() -> None:
    result = _evaluate(
        ingestion=_ready_ingestion(
            diagnostics_uri=None,
            require_diagnostics_uri=False,
        ),
        require_diagnostics_uri=True,
    )
    assert result.status == (
        MMMArtifactGovernanceUseReadinessStatus.MISSING_REQUIRED_ARTIFACT_METADATA
    )


def test_successful_ingestion_enables_trust_report_review() -> None:
    result = _evaluate(ingestion=_ready_ingestion())
    assert result.ready_for_trust_report_review is True
    assert any(
        d.route == MMMArtifactGovernanceRoute.TRUST_REPORT_REVIEW and d.enabled
        for d in result.route_decisions
    )


def test_successful_ingestion_with_model_artifact_enables_decision_surface_route() -> None:
    result = _evaluate(
        ingestion=_ready_ingestion(),
        model_artifact=_model_artifact(),
    )
    assert result.ready_for_decision_surface_review is True
    assert result.planning_ready is True


def test_model_artifact_absent_still_allows_trust_report_review() -> None:
    result = _evaluate(ingestion=_ready_ingestion(), model_artifact=None)
    assert result.ready_for_trust_report_review is True
    assert result.planning_ready is True


def test_model_artifact_diagnostic_only_routes_to_diagnostic_review() -> None:
    result = _evaluate(
        ingestion=_ready_ingestion(),
        model_artifact=_model_artifact(
            promotion_status=MMMModelPromotionStatus.PROMOTED_FOR_DIAGNOSTIC_ONLY,
            allowed_uses=[MMMModelAllowedUse.DIAGNOSTIC_ONLY],
        ),
    )
    assert result.status == MMMArtifactGovernanceUseReadinessStatus.DIAGNOSTIC_ONLY
    assert result.planning_ready is False
    assert result.diagnostic_only is True
    assert result.ready_for_decision_surface_review is False
    assert result.ready_for_diagnostic_review is True


def test_allowed_uses_exclude_planning_not_planning_ready() -> None:
    result = _evaluate(
        ingestion=_ready_ingestion(),
        model_artifact=_model_artifact(
            allowed_uses=[MMMModelAllowedUse.READ_ONLY_SUMMARY],
        ),
    )
    assert result.planning_ready is False
    assert result.use_readiness == MMMArtifactUseReadiness.NOT_PLANNING_READY


def test_promotion_status_not_promoted_blocks_planning_ready() -> None:
    result = _evaluate(
        ingestion=_ready_ingestion(),
        model_artifact=_model_artifact(
            promotion_status=MMMModelPromotionStatus.NOT_PROMOTED,
        ),
    )
    assert result.planning_ready is False
    assert result.use_readiness == MMMArtifactUseReadiness.BLOCKED


def test_diagnostic_status_failed_blocks_planning_ready() -> None:
    result = _evaluate(
        ingestion=_ready_ingestion(),
        model_artifact=_model_artifact(
            diagnostic_status=MMMModelDiagnosticStatus.FAILED,
        ),
    )
    assert result.planning_ready is False
    assert result.diagnostic_only is True


def test_planning_ready_true_with_required_metadata() -> None:
    result = _evaluate(
        ingestion=_ready_ingestion(),
        model_artifact=_model_artifact(),
    )
    assert result.planning_ready is True
    assert result.use_readiness == MMMArtifactUseReadiness.PLANNING_READY


def test_human_review_required_for_trust_surface_routing() -> None:
    result = _evaluate(
        ingestion=_ready_ingestion(),
        model_artifact=_model_artifact(),
    )
    assert result.human_review_required is True
    assert MMMArtifactGovernanceUseReadinessIssueCode.HUMAN_REVIEW_REQUIRED in result.issues


def test_candidate_references_reused_metadata_only() -> None:
    result = _evaluate(
        ingestion=_ready_ingestion(),
        model_artifact=_model_artifact(),
    )
    trust_route = next(
        d
        for d in result.route_decisions
        if d.route == MMMArtifactGovernanceRoute.TRUST_REPORT_REVIEW
    )
    surface_route = next(
        d
        for d in result.route_decisions
        if d.route == MMMArtifactGovernanceRoute.DECISION_SURFACE_REVIEW
    )
    assert trust_route.candidate_reference == "trust_report:candidate:ext-run-1"
    assert surface_route.candidate_reference == "surface-1"
    assert trust_route.metadata.get("metadata_only_candidate_reference") is True


def test_lineage_preserved() -> None:
    result = _evaluate(ingestion=_ready_ingestion())
    assert result.lineage.get("gate_stage") == "governance_use_readiness"
    assert result.lineage.get("upstream") == "runtime_adapter"
    assert result.lineage.get("governance_use_readiness_stage") == (
        "mmm_artifact_governance_use_readiness"
    )


def test_no_forbidden_construction_in_sources() -> None:
    # forbidden tokens must not appear in gate sources (string assert list)
    forbidden = (
        "TrustReport(",  # forbidden
        "DecisionSurface(",  # forbidden
        "RecommendationContract(",  # forbidden
        "open(",  # forbidden
        "read_text",  # forbidden
        "read_bytes",  # forbidden
        "json.load",  # forbidden
        "pandas",  # forbidden
        "pd.read",  # forbidden
        "import requests",  # forbidden
        "import httpx",  # forbidden
        "import pickle",  # forbidden
        "import joblib",  # forbidden
        "load_model(",  # forbidden
        ".fit(",  # forbidden
        ".predict(",  # forbidden
        ".sample(",  # forbidden
    )
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        for line in path.read_text(encoding="utf-8").splitlines():  # forbidden source scan
            if line.strip().startswith("#"):
                continue
            for token in forbidden:
                assert token not in line, f"{token} in {path}: {line}"


def test_boundary_issue_codes_present() -> None:
    result = _evaluate(ingestion=_ready_ingestion())
    assert MMMArtifactGovernanceUseReadinessIssueCode.NO_TRUST_REPORT_CONSTRUCTION in (
        result.issues
    )
    assert MMMArtifactGovernanceUseReadinessIssueCode.NO_MODEL_PROMOTION_IMPLEMENTED in (
        result.issues
    )
    assert MMMArtifactGovernanceUseReadinessIssueCode.NO_CLAIM_AUTHORIZATION in result.issues


def test_summarize_returns_metadata_only() -> None:
    result = _evaluate(ingestion=_ready_ingestion(), model_artifact=_model_artifact())
    summary = summarize_mmm_artifact_governance_and_use_readiness(result)
    assert summary["planning_ready"] is True
    assert "recommendation" not in summary
