"""MMM runtime result ingestion workflow (metadata only; no artifact loading)."""

from __future__ import annotations

from mip.contracts.mmm_runtime_adapter import (
    MMMRuntimeArtifactHandoff,
    MMMRuntimeCallResult,
    MMMRuntimeCallStatus,
    MMMRuntimeFailurePacket,
)
from mip.contracts.mmm_runtime_result_ingestion import (
    MMMRuntimeDiagnosticsMetadata,
    MMMRuntimeDiagnosticsMetadataStatus,
    MMMRuntimeGovernanceRoutingReference,
    MMMRuntimeGovernanceRoutingStatus,
    MMMRuntimeResultIngestionIssueCode,
    MMMRuntimeResultIngestionRequest,
    MMMRuntimeResultIngestionResult,
    MMMRuntimeResultIngestionStatus,
)

_BOUNDARY_ISSUES = (
    MMMRuntimeResultIngestionIssueCode.NO_ARTIFACT_LOADING,
    MMMRuntimeResultIngestionIssueCode.NO_DIAGNOSTICS_PARSING,
    MMMRuntimeResultIngestionIssueCode.NO_DIAGNOSTICS_CALCULATION,
    MMMRuntimeResultIngestionIssueCode.NO_MODEL_LOADING,
    MMMRuntimeResultIngestionIssueCode.NO_MODEL_EXECUTION,
    MMMRuntimeResultIngestionIssueCode.NO_MMM_FITTING,
    MMMRuntimeResultIngestionIssueCode.NO_BAYESIAN_FITTING,
    MMMRuntimeResultIngestionIssueCode.NO_PRIOR_APPLICATION,
    MMMRuntimeResultIngestionIssueCode.NO_LIKELIHOOD_CONSTRUCTION,
    MMMRuntimeResultIngestionIssueCode.NO_POSTERIOR_CALCULATION,
    MMMRuntimeResultIngestionIssueCode.NO_OPTIMIZER_EXECUTION,
    MMMRuntimeResultIngestionIssueCode.NO_SIMULATOR_EXECUTION,
    MMMRuntimeResultIngestionIssueCode.NO_RECOMMENDATION_GENERATED,
    MMMRuntimeResultIngestionIssueCode.NO_DECISION_SURFACE_CONSTRUCTION,
    MMMRuntimeResultIngestionIssueCode.NO_DECISION_SURFACE_EXECUTION,
    MMMRuntimeResultIngestionIssueCode.NO_TRUST_REPORT_CONSTRUCTION,
    MMMRuntimeResultIngestionIssueCode.NO_CLAIM_AUTHORIZATION,
)


def ingest_mmm_runtime_result_metadata(
    request: MMMRuntimeResultIngestionRequest,
) -> MMMRuntimeResultIngestionResult:
    """Ingest external MMM runtime result metadata without loading artifacts."""
    lineage = {
        **request.lineage,
        "ingestion_stage": "mmm_runtime_result_ingestion",
    }
    warnings: list[str] = []
    issues: list[MMMRuntimeResultIngestionIssueCode] = list(_BOUNDARY_ISSUES)
    issues.append(MMMRuntimeResultIngestionIssueCode.LINEAGE_PRESERVED)

    if request.runtime_call_result is None:
        return _blocked(
            request=request,
            status=MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_RUNTIME_RESULT,
            diagnostics_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_DEFERRED,
            governance_status=MMMRuntimeGovernanceRoutingStatus.BLOCKED_MISSING_REQUIRED_ARTIFACTS,
            blocked_reasons=["runtime call result is missing"],
            warnings=warnings,
            issues=issues
            + [
                MMMRuntimeResultIngestionIssueCode.RUNTIME_RESULT_MISSING,
                MMMRuntimeResultIngestionIssueCode.GOVERNANCE_REVIEW_BLOCKED,
            ],
            lineage=lineage,
        )

    runtime_result = request.runtime_call_result
    issues.append(MMMRuntimeResultIngestionIssueCode.RUNTIME_RESULT_PRESENT)
    issues.append(MMMRuntimeResultIngestionIssueCode.RUNTIME_STATUS_RECORDED)
    warnings.extend(runtime_result.warnings)
    lineage = {**lineage, **runtime_result.lineage}

    if runtime_result.status == MMMRuntimeCallStatus.EXTERNAL_RUNTIME_FAILED:
        issues.append(MMMRuntimeResultIngestionIssueCode.RUNTIME_FAILED)
        if runtime_result.failure_packet is not None:
            issues.append(MMMRuntimeResultIngestionIssueCode.FAILURE_PACKET_PRESENT)
        else:
            issues.append(MMMRuntimeResultIngestionIssueCode.FAILURE_PACKET_ABSENT)
        return _failed(
            request=request,
            runtime_result=runtime_result,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
        )

    if runtime_result.failure_packet is not None:
        issues.append(MMMRuntimeResultIngestionIssueCode.FAILURE_PACKET_PRESENT)
        issues.append(MMMRuntimeResultIngestionIssueCode.RUNTIME_FAILED)
        return _failed(
            request=request,
            runtime_result=runtime_result,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
        )

    issues.append(MMMRuntimeResultIngestionIssueCode.FAILURE_PACKET_ABSENT)
    handoff = runtime_result.artifact_handoff
    if handoff is None:
        return _blocked(
            request=request,
            status=MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_ARTIFACT_HANDOFF,
            diagnostics_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_DEFERRED,
            governance_status=MMMRuntimeGovernanceRoutingStatus.BLOCKED_MISSING_REQUIRED_ARTIFACTS,
            blocked_reasons=["artifact handoff is missing"],
            warnings=warnings,
            issues=issues
            + [
                MMMRuntimeResultIngestionIssueCode.ARTIFACT_HANDOFF_MISSING,
                MMMRuntimeResultIngestionIssueCode.GOVERNANCE_REVIEW_BLOCKED,
            ],
            lineage=lineage,
            failure_packet=runtime_result.failure_packet,
        )

    issues.append(MMMRuntimeResultIngestionIssueCode.ARTIFACT_HANDOFF_PRESENT)
    issues.append(MMMRuntimeResultIngestionIssueCode.ARTIFACT_URI_METADATA_PRESERVED)

    external_run_id = runtime_result.external_run_id or handoff.external_run_id
    if not external_run_id or not external_run_id.strip():
        return _blocked(
            request=request,
            status=MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_EXTERNAL_RUN_ID,
            diagnostics_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_DEFERRED,
            governance_status=MMMRuntimeGovernanceRoutingStatus.BLOCKED_MISSING_REQUIRED_ARTIFACTS,
            blocked_reasons=["external run id is missing"],
            warnings=warnings,
            issues=issues
            + [
                MMMRuntimeResultIngestionIssueCode.EXTERNAL_RUN_ID_MISSING,
                MMMRuntimeResultIngestionIssueCode.GOVERNANCE_REVIEW_BLOCKED,
            ],
            lineage=lineage,
            artifact_handoff=handoff,
        )

    issues.append(MMMRuntimeResultIngestionIssueCode.EXTERNAL_RUN_ID_PRESENT)

    if request.require_model_artifact_uri and not handoff.model_artifact_uri:
        return _blocked(
            request=request,
            status=MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_MODEL_ARTIFACT_URI,
            diagnostics_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_DEFERRED,
            governance_status=MMMRuntimeGovernanceRoutingStatus.BLOCKED_MISSING_REQUIRED_ARTIFACTS,
            blocked_reasons=["model artifact URI is required but missing"],
            warnings=warnings,
            issues=issues
            + [
                MMMRuntimeResultIngestionIssueCode.MODEL_ARTIFACT_URI_MISSING,
                MMMRuntimeResultIngestionIssueCode.GOVERNANCE_REVIEW_BLOCKED,
            ],
            lineage=lineage,
            artifact_handoff=handoff,
            external_run_id=external_run_id,
        )

    if handoff.model_artifact_uri:
        issues.append(MMMRuntimeResultIngestionIssueCode.MODEL_ARTIFACT_URI_PRESENT)

    if request.require_manifest_uri and not handoff.manifest_uri:
        return _blocked(
            request=request,
            status=MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_MANIFEST_URI,
            diagnostics_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_DEFERRED,
            governance_status=MMMRuntimeGovernanceRoutingStatus.BLOCKED_MISSING_REQUIRED_ARTIFACTS,
            blocked_reasons=["manifest URI is required but missing"],
            warnings=warnings,
            issues=issues
            + [
                MMMRuntimeResultIngestionIssueCode.MANIFEST_URI_MISSING,
                MMMRuntimeResultIngestionIssueCode.GOVERNANCE_REVIEW_BLOCKED,
            ],
            lineage=lineage,
            artifact_handoff=handoff,
            external_run_id=external_run_id,
        )

    if handoff.manifest_uri:
        issues.append(MMMRuntimeResultIngestionIssueCode.MANIFEST_URI_PRESENT)

    diagnostics_missing = not handoff.diagnostics_uri
    if request.require_diagnostics_uri and diagnostics_missing:
        return _blocked(
            request=request,
            status=MMMRuntimeResultIngestionStatus.INGESTION_DIAGNOSTICS_METADATA_MISSING,
            diagnostics_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_MISSING,
            governance_status=MMMRuntimeGovernanceRoutingStatus.BLOCKED_MISSING_REQUIRED_ARTIFACTS,
            blocked_reasons=["diagnostics URI is required but missing"],
            warnings=warnings,
            issues=issues
            + [
                MMMRuntimeResultIngestionIssueCode.DIAGNOSTICS_URI_MISSING,
                MMMRuntimeResultIngestionIssueCode.GOVERNANCE_REVIEW_BLOCKED,
            ],
            lineage=lineage,
            artifact_handoff=handoff,
            external_run_id=external_run_id,
        )

    if diagnostics_missing:
        warnings.append("diagnostics URI is missing")
        issues.append(MMMRuntimeResultIngestionIssueCode.DIAGNOSTICS_URI_MISSING)
    else:
        issues.append(MMMRuntimeResultIngestionIssueCode.DIAGNOSTICS_URI_PRESENT)

    logs_missing = not handoff.runtime_logs_uri
    if request.require_runtime_logs_uri and logs_missing:
        return _blocked(
            request=request,
            status=MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_ARTIFACT_HANDOFF,
            diagnostics_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_MISSING,
            governance_status=MMMRuntimeGovernanceRoutingStatus.BLOCKED_MISSING_REQUIRED_ARTIFACTS,
            blocked_reasons=["runtime logs URI is required but missing"],
            warnings=warnings,
            issues=issues
            + [
                MMMRuntimeResultIngestionIssueCode.RUNTIME_LOGS_URI_MISSING,
                MMMRuntimeResultIngestionIssueCode.GOVERNANCE_REVIEW_BLOCKED,
            ],
            lineage=lineage,
            artifact_handoff=handoff,
            external_run_id=external_run_id,
        )

    if logs_missing:
        warnings.append("runtime logs URI is missing")
        issues.append(MMMRuntimeResultIngestionIssueCode.RUNTIME_LOGS_URI_MISSING)
    else:
        issues.append(MMMRuntimeResultIngestionIssueCode.RUNTIME_LOGS_URI_PRESENT)

    diagnostics_status, diagnostics_metadata = _build_diagnostics_metadata(
        request_id=request.request_id,
        external_run_id=external_run_id,
        handoff=handoff,
        warnings=warnings,
        diagnostics_missing=diagnostics_missing,
        logs_missing=logs_missing,
    )
    if diagnostics_metadata is not None:
        issues.append(MMMRuntimeResultIngestionIssueCode.DIAGNOSTICS_METADATA_READY)

    governance_reference: MMMRuntimeGovernanceRoutingReference | None = None
    governance_status = MMMRuntimeGovernanceRoutingStatus.DEFERRED

    if request.create_governance_routing_reference:
        governance_reference = _build_governance_routing_reference(
            request_id=request.request_id,
            external_run_id=external_run_id,
            handoff=handoff,
            warnings=warnings,
            has_warnings=bool(warnings),
        )
        governance_status = governance_reference.governance_routing_status
        issues.append(MMMRuntimeResultIngestionIssueCode.TRUST_ROUTING_REFERENCE_CREATED)
        issues.append(MMMRuntimeResultIngestionIssueCode.DECISION_SURFACE_ROUTING_REFERENCE_CREATED)
        issues.append(MMMRuntimeResultIngestionIssueCode.GOVERNANCE_REVIEW_READY)
    else:
        issues.append(MMMRuntimeResultIngestionIssueCode.DIAGNOSTICS_METADATA_DEFERRED)
        governance_status = MMMRuntimeGovernanceRoutingStatus.DEFERRED

    if warnings:
        ingestion_status = MMMRuntimeResultIngestionStatus.INGESTION_READY_WITH_WARNINGS
        if governance_status == MMMRuntimeGovernanceRoutingStatus.DEFERRED:
            ready_for_review = False
        else:
            governance_status = (
                MMMRuntimeGovernanceRoutingStatus.READY_FOR_GOVERNANCE_REVIEW_WITH_WARNINGS
            )
            if governance_reference is not None:
                governance_reference = governance_reference.model_copy(
                    update={"governance_routing_status": governance_status}
                )
            ready_for_review = request.create_governance_routing_reference
    else:
        ingestion_status = MMMRuntimeResultIngestionStatus.INGESTION_READY_FOR_GOVERNANCE_REVIEW
        if governance_status != MMMRuntimeGovernanceRoutingStatus.DEFERRED:
            governance_status = MMMRuntimeGovernanceRoutingStatus.READY_FOR_GOVERNANCE_REVIEW
            if governance_reference is not None:
                governance_reference = governance_reference.model_copy(
                    update={"governance_routing_status": governance_status}
                )
        ready_for_review = (
            governance_status != MMMRuntimeGovernanceRoutingStatus.DEFERRED
            and request.create_governance_routing_reference
        )

    return MMMRuntimeResultIngestionResult(
        request_id=request.request_id,
        status=ingestion_status,
        diagnostics_metadata_status=diagnostics_status,
        governance_routing_status=governance_status,
        external_run_id=external_run_id,
        artifact_handoff=handoff,
        diagnostics_metadata=diagnostics_metadata,
        governance_routing_reference=governance_reference,
        failure_packet=runtime_result.failure_packet,
        ready_for_governance_review=ready_for_review,
        warnings=warnings,
        issues=issues,
        lineage=lineage,
        metadata={
            **request.metadata,
            "runtime_call_status": str(runtime_result.status),
            "artifact_uris_metadata_only": True,
        },
    )


def summarize_mmm_runtime_result_ingestion(
    result: MMMRuntimeResultIngestionResult,
) -> dict[str, object]:
    """Summarize runtime result ingestion outcome without recommendation language."""
    return {
        "status": str(result.status),
        "diagnostics_metadata_status": str(result.diagnostics_metadata_status),
        "governance_routing_status": str(result.governance_routing_status),
        "external_run_id": result.external_run_id,
        "ready_for_governance_review": result.ready_for_governance_review,
        "artifact_handoff_present": result.artifact_handoff is not None,
        "diagnostics_metadata_present": result.diagnostics_metadata is not None,
        "governance_routing_reference_present": result.governance_routing_reference is not None,
        "failure_packet_present": result.failure_packet is not None,
        "blocked_reasons": list(result.blocked_reasons),
        "warnings": list(result.warnings),
    }


def _build_diagnostics_metadata(
    *,
    request_id: str,
    external_run_id: str,
    handoff: MMMRuntimeArtifactHandoff,
    warnings: list[str],
    diagnostics_missing: bool,
    logs_missing: bool,
) -> tuple[MMMRuntimeDiagnosticsMetadataStatus, MMMRuntimeDiagnosticsMetadata | None]:
    if diagnostics_missing and logs_missing:
        status = MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_MISSING
    elif warnings:
        status = MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_PRESENT_WITH_WARNINGS
    else:
        status = MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_PRESENT

    diagnostic_artifact_uris = list(handoff.artifact_uris)
    if handoff.diagnostics_uri:
        diagnostic_artifact_uris.append(handoff.diagnostics_uri)

    metadata = MMMRuntimeDiagnosticsMetadata(
        diagnostics_metadata_id=f"mmm-diagnostics-metadata:{request_id}",
        external_run_id=external_run_id,
        diagnostics_uri=handoff.diagnostics_uri,
        manifest_uri=handoff.manifest_uri,
        runtime_logs_uri=handoff.runtime_logs_uri,
        diagnostics_status=status,
        diagnostics_summary_reference=(
            f"diagnostics_summary_ref:{external_run_id}" if handoff.diagnostics_uri else None
        ),
        diagnostic_artifact_uris=diagnostic_artifact_uris,
        warnings=list(warnings),
        metadata={"uri_metadata_only": True},
    )
    return status, metadata


def _build_governance_routing_reference(
    *,
    request_id: str,
    external_run_id: str,
    handoff: MMMRuntimeArtifactHandoff,
    warnings: list[str],
    has_warnings: bool,
) -> MMMRuntimeGovernanceRoutingReference:
    routing_status = (
        MMMRuntimeGovernanceRoutingStatus.READY_FOR_GOVERNANCE_REVIEW_WITH_WARNINGS
        if has_warnings
        else MMMRuntimeGovernanceRoutingStatus.READY_FOR_GOVERNANCE_REVIEW
    )
    return MMMRuntimeGovernanceRoutingReference(
        routing_id=f"mmm-governance-routing:{request_id}",
        external_run_id=external_run_id,
        model_artifact_uri=handoff.model_artifact_uri,
        manifest_uri=handoff.manifest_uri,
        diagnostics_uri=handoff.diagnostics_uri,
        trust_report_candidate_reference=f"trust_report:candidate:{external_run_id}",
        decision_surface_candidate_reference=f"decision_surface:candidate:{external_run_id}",
        governance_routing_status=routing_status,
        warnings=list(warnings),
        metadata={
            "metadata_only_candidate_reference": True,
            "governance_adapter_reference": (
                "mip.adapters.governance:trust_report_for_adapter_output"
            ),
        },
    )


def _failed(
    *,
    request: MMMRuntimeResultIngestionRequest,
    runtime_result: MMMRuntimeCallResult,
    warnings: list[str],
    issues: list[MMMRuntimeResultIngestionIssueCode],
    lineage: dict[str, str],
) -> MMMRuntimeResultIngestionResult:    return MMMRuntimeResultIngestionResult(
        request_id=request.request_id,
        status=MMMRuntimeResultIngestionStatus.INGESTION_RUNTIME_FAILED,
        diagnostics_metadata_status=MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_FAILED,
        governance_routing_status=MMMRuntimeGovernanceRoutingStatus.BLOCKED_RUNTIME_FAILED,
        external_run_id=runtime_result.external_run_id,
        artifact_handoff=runtime_result.artifact_handoff,
        failure_packet=runtime_result.failure_packet,
        ready_for_governance_review=False,
        blocked_reasons=list(runtime_result.blocked_reasons)
        or ["external MMM runtime call failed"],
        warnings=warnings,
        issues=issues + [MMMRuntimeResultIngestionIssueCode.GOVERNANCE_REVIEW_BLOCKED],
        lineage=lineage,
        metadata=dict(request.metadata),
    )


def _blocked(
    *,
    request: MMMRuntimeResultIngestionRequest,
    status: MMMRuntimeResultIngestionStatus,
    diagnostics_status: MMMRuntimeDiagnosticsMetadataStatus,
    governance_status: MMMRuntimeGovernanceRoutingStatus,
    blocked_reasons: list[str],
    warnings: list[str],
    issues: list[MMMRuntimeResultIngestionIssueCode],
    lineage: dict[str, str],
    artifact_handoff: MMMRuntimeArtifactHandoff | None = None,
    external_run_id: str | None = None,
    failure_packet: MMMRuntimeFailurePacket | None = None,
) -> MMMRuntimeResultIngestionResult:
    return MMMRuntimeResultIngestionResult(
        request_id=request.request_id,
        status=status,
        diagnostics_metadata_status=diagnostics_status,
        governance_routing_status=governance_status,
        external_run_id=external_run_id,
        artifact_handoff=artifact_handoff,
        failure_packet=failure_packet,
        ready_for_governance_review=False,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        issues=issues,
        lineage=lineage,
        metadata=dict(request.metadata),
    )
