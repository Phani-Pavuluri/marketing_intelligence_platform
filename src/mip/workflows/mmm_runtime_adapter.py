"""MMM runtime adapter workflow (metadata-only handoff; no execution)."""

from __future__ import annotations

from mip.contracts.mmm_runtime_adapter import (
    DEFAULT_ADAPTER_PLACEHOLDER_REFERENCE,
    DEFAULT_GOVERNANCE_ADAPTER_REFERENCE,
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
from mip.contracts.planning_mmm_trusted_input_model_run_eligibility import (
    PlanningMMMModelRunEligibilityDecision,
    PlanningMMMModelRunEligibilityResult,
)

_REQUESTED_RUN_TYPE_NEW_MODEL_RUN = "new_model_run"
_REQUESTED_RUN_TYPE_MODEL_REFRESH = "model_refresh"
_REQUESTED_RUN_TYPE_NO_RUNTIME_CALL = "no_runtime_call_existing_model"
_REQUESTED_RUN_TYPE_DEFERRED = "deferred"
_REQUESTED_RUN_TYPE_BLOCKED = "blocked"

_BOUNDARY_ISSUES = (
    MMMRuntimeCallIssueCode.NO_MODEL_EXECUTION,
    MMMRuntimeCallIssueCode.NO_MODEL_ARTIFACT_LOADING,
    MMMRuntimeCallIssueCode.NO_MMM_FITTING,
    MMMRuntimeCallIssueCode.NO_BAYESIAN_FITTING,
    MMMRuntimeCallIssueCode.NO_PRIOR_APPLICATION,
    MMMRuntimeCallIssueCode.NO_LIKELIHOOD_CONSTRUCTION,
    MMMRuntimeCallIssueCode.NO_POSTERIOR_CALCULATION,
    MMMRuntimeCallIssueCode.NO_OPTIMIZER_EXECUTION,
    MMMRuntimeCallIssueCode.NO_SIMULATOR_EXECUTION,
    MMMRuntimeCallIssueCode.NO_RECOMMENDATION_GENERATED,
    MMMRuntimeCallIssueCode.NO_DECISION_SURFACE_EXECUTION,
    MMMRuntimeCallIssueCode.NO_TRUST_REPORT_CONSTRUCTION,
    MMMRuntimeCallIssueCode.NO_CLAIM_AUTHORIZATION,
)


def prepare_mmm_runtime_call(request: MMMRuntimeCallRequest) -> MMMRuntimeCallResult:
    """Prepare or record a metadata-only external MMM runtime handoff."""
    lineage = {
        **request.lineage,
        "runtime_adapter_stage": "mmm_runtime_adapter",
    }
    warnings: list[str] = []
    issues: list[MMMRuntimeCallIssueCode] = list(_BOUNDARY_ISSUES)
    issues.append(MMMRuntimeCallIssueCode.RUNTIME_NOT_CALLED)

    runtime_reference = request.runtime_reference or _default_runtime_reference(request.request_id)
    issues.append(MMMRuntimeCallIssueCode.EXTERNAL_RUNTIME_REFERENCE_CREATED)
    issues.append(MMMRuntimeCallIssueCode.ADAPTER_PLACEHOLDER_REFERENCE_PRESERVED)
    issues.append(MMMRuntimeCallIssueCode.GOVERNANCE_ADAPTER_REFERENCE_PRESERVED)
    issues.append(MMMRuntimeCallIssueCode.LINEAGE_PRESERVED)

    if request.eligibility_result is None:
        return _blocked(
            request=request,
            status=MMMRuntimeCallStatus.BLOCKED_BY_ELIGIBILITY,
            decision=MMMRuntimeCallDecision.BLOCK_RUNTIME_CALL,
            runtime_reference=runtime_reference,
            blocked_reasons=["eligibility result is missing"],
            warnings=warnings,
            issues=issues
            + [
                MMMRuntimeCallIssueCode.ELIGIBILITY_RESULT_MISSING,
                MMMRuntimeCallIssueCode.FAILURE_PACKET_CREATED,
            ],
            lineage=lineage,
            error_code="eligibility_result_missing",
            message="eligibility result is missing",
        )

    eligibility = request.eligibility_result
    issues.append(MMMRuntimeCallIssueCode.ELIGIBILITY_RESULT_PRESENT)
    warnings.extend(eligibility.warnings)
    lineage = {**lineage, **eligibility.lineage}

    if request.supplied_failure_packet is not None:
        return _record_external_failure(
            request=request,
            runtime_reference=runtime_reference,
            failure_packet=request.supplied_failure_packet,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
        )

    if request.supplied_artifact_handoff is not None and request.external_run_id:
        return _record_external_success(
            request=request,
            runtime_reference=runtime_reference,
            artifact_handoff=request.supplied_artifact_handoff,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
        )

    decision = eligibility.decision

    if decision == PlanningMMMModelRunEligibilityDecision.USE_EXISTING_MODEL:
        issues.append(MMMRuntimeCallIssueCode.ELIGIBILITY_USE_EXISTING_MODEL)
        if eligibility.trusted_input_package is not None:
            issues.append(MMMRuntimeCallIssueCode.TRUSTED_INPUT_PACKAGE_PRESENT)
            issues.append(MMMRuntimeCallIssueCode.TRUSTED_INPUT_REFERENCE_PRESERVED)
        if eligibility.use_existing_model:
            issues.append(MMMRuntimeCallIssueCode.EXISTING_MODEL_REFERENCE_PRESERVED)
        return _result(
            request=request,
            status=MMMRuntimeCallStatus.NOT_CALLED_EXISTING_MODEL_SELECTED,
            decision=MMMRuntimeCallDecision.USE_EXISTING_MODEL_NO_RUNTIME_CALL,
            runtime_reference=runtime_reference,
            requested_run_type=_REQUESTED_RUN_TYPE_NO_RUNTIME_CALL,
            trusted_input_package_id=_trusted_input_package_id(request, eligibility),
            warnings=warnings,
            issues=issues + [MMMRuntimeCallIssueCode.RUNTIME_REQUEST_CREATED],
            lineage=lineage,
        )

    if decision == PlanningMMMModelRunEligibilityDecision.DEFER:
        issues.append(MMMRuntimeCallIssueCode.ELIGIBILITY_DEFERRED)
        return _result(
            request=request,
            status=MMMRuntimeCallStatus.DEFERRED,
            decision=MMMRuntimeCallDecision.DEFER_RUNTIME_CALL,
            runtime_reference=runtime_reference,
            requested_run_type=_REQUESTED_RUN_TYPE_DEFERRED,
            blocked_reasons=list(eligibility.blocked_reasons),
            warnings=warnings,
            issues=issues,
            lineage=lineage,
        )

    if decision == PlanningMMMModelRunEligibilityDecision.BLOCK:
        issues.append(MMMRuntimeCallIssueCode.ELIGIBILITY_BLOCKED)
        return _blocked(
            request=request,
            status=MMMRuntimeCallStatus.BLOCKED_BY_ELIGIBILITY,
            decision=MMMRuntimeCallDecision.BLOCK_RUNTIME_CALL,
            runtime_reference=runtime_reference,
            blocked_reasons=list(eligibility.blocked_reasons) or ["eligibility decision is block"],
            warnings=warnings,
            issues=issues + [MMMRuntimeCallIssueCode.FAILURE_PACKET_CREATED],
            lineage=lineage,
            error_code="eligibility_blocked",
            message="eligibility decision blocked runtime call",
        )

    if decision == PlanningMMMModelRunEligibilityDecision.REQUEST_MODEL_REFRESH:
        issues.append(MMMRuntimeCallIssueCode.ELIGIBILITY_REQUEST_MODEL_REFRESH)
        return _prepare_external_run(
            request=request,
            eligibility=eligibility,
            runtime_reference=runtime_reference,
            decision=MMMRuntimeCallDecision.PREPARE_EXTERNAL_MODEL_REFRESH,
            requested_run_type=_REQUESTED_RUN_TYPE_MODEL_REFRESH,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
        )

    if decision == PlanningMMMModelRunEligibilityDecision.REQUEST_NEW_MODEL_RUN:
        issues.append(MMMRuntimeCallIssueCode.ELIGIBILITY_REQUEST_NEW_MODEL_RUN)
        return _prepare_external_run(
            request=request,
            eligibility=eligibility,
            runtime_reference=runtime_reference,
            decision=MMMRuntimeCallDecision.PREPARE_EXTERNAL_NEW_MODEL_RUN,
            requested_run_type=_REQUESTED_RUN_TYPE_NEW_MODEL_RUN,
            warnings=warnings,
            issues=issues,
            lineage=lineage,
        )

    return _blocked(
        request=request,
        status=MMMRuntimeCallStatus.BLOCKED_BY_ELIGIBILITY,
        decision=MMMRuntimeCallDecision.BLOCK_RUNTIME_CALL,
        runtime_reference=runtime_reference,
        blocked_reasons=[f"unsupported eligibility decision: {decision}"],
        warnings=warnings,
        issues=issues + [MMMRuntimeCallIssueCode.FAILURE_PACKET_CREATED],
        lineage=lineage,
        error_code="unsupported_eligibility_decision",
        message=f"unsupported eligibility decision: {decision}",
    )


def summarize_mmm_runtime_call(result: MMMRuntimeCallResult) -> dict[str, object]:
    """Summarize runtime adapter outcome without recommendation language."""
    return {
        "status": str(result.status),
        "decision": str(result.decision),
        "runtime_called": result.runtime_called,
        "runtime_id": result.runtime_reference.runtime_id if result.runtime_reference else None,
        "external_run_id": result.external_run_id,
        "artifact_handoff_present": result.artifact_handoff is not None,
        "failure_packet_present": result.failure_packet is not None,
        "blocked_reasons": list(result.blocked_reasons),
        "warnings": list(result.warnings),
    }


def _prepare_external_run(
    *,
    request: MMMRuntimeCallRequest,
    eligibility: PlanningMMMModelRunEligibilityResult,
    runtime_reference: MMMRuntimeReference,
    decision: MMMRuntimeCallDecision,
    requested_run_type: str,
    warnings: list[str],
    issues: list[MMMRuntimeCallIssueCode],
    lineage: dict[str, str],
) -> MMMRuntimeCallResult:
    package = eligibility.trusted_input_package
    if package is None:
        return _blocked(
            request=request,
            status=MMMRuntimeCallStatus.BLOCKED_MISSING_TRUSTED_INPUT_PACKAGE,
            decision=MMMRuntimeCallDecision.BLOCK_RUNTIME_CALL,
            runtime_reference=runtime_reference,
            blocked_reasons=["trusted input package is required for external model run"],
            warnings=warnings,
            issues=issues
            + [
                MMMRuntimeCallIssueCode.TRUSTED_INPUT_PACKAGE_MISSING,
                MMMRuntimeCallIssueCode.FAILURE_PACKET_CREATED,
            ],
            lineage=lineage,
            error_code="trusted_input_package_missing",
            message="trusted input package is required for external model run",
        )

    issues.append(MMMRuntimeCallIssueCode.TRUSTED_INPUT_PACKAGE_PRESENT)
    issues.append(MMMRuntimeCallIssueCode.TRUSTED_INPUT_REFERENCE_PRESERVED)

    model_config_id = request.model_config_id or package.model_config_id
    if not model_config_id and not package.model_config_present:
        return _blocked(
            request=request,
            status=MMMRuntimeCallStatus.BLOCKED_MISSING_MODEL_CONFIG,
            decision=MMMRuntimeCallDecision.BLOCK_RUNTIME_CALL,
            runtime_reference=runtime_reference,
            blocked_reasons=["model config reference is required for external model run"],
            warnings=warnings,
            issues=issues
            + [
                MMMRuntimeCallIssueCode.MODEL_CONFIG_REFERENCE_MISSING,
                MMMRuntimeCallIssueCode.FAILURE_PACKET_CREATED,
            ],
            lineage=lineage,
            error_code="model_config_missing",
            message="model config reference is required for external model run",
        )

    issues.append(MMMRuntimeCallIssueCode.MODEL_CONFIG_REFERENCE_PRESENT)
    issues.append(MMMRuntimeCallIssueCode.RUNTIME_REQUEST_CREATED)

    return _result(
        request=request,
        status=MMMRuntimeCallStatus.READY_TO_CALL_EXTERNAL_RUNTIME,
        decision=decision,
        runtime_reference=runtime_reference,
        requested_run_type=requested_run_type,
        model_config_id=model_config_id,
        trusted_input_package_id=package.package_id,
        warnings=warnings,
        issues=issues,
        lineage=lineage,
    )


def _record_external_success(
    *,
    request: MMMRuntimeCallRequest,
    runtime_reference: MMMRuntimeReference,
    artifact_handoff: MMMRuntimeArtifactHandoff,
    warnings: list[str],
    issues: list[MMMRuntimeCallIssueCode],
    lineage: dict[str, str],
) -> MMMRuntimeCallResult:
    issues.append(MMMRuntimeCallIssueCode.RUNTIME_STATUS_RECORDED)
    return MMMRuntimeCallResult(
        request_id=request.request_id,
        status=MMMRuntimeCallStatus.EXTERNAL_RUNTIME_CALL_RECORDED,
        decision=MMMRuntimeCallDecision.RECORD_EXTERNAL_RUNTIME_RESULT,
        runtime_reference=runtime_reference,
        runtime_called=True,
        external_run_id=request.external_run_id,
        artifact_handoff=artifact_handoff,
        warnings=warnings,
        issues=issues,
        lineage={
            **lineage,
            "record_mode": "external_runtime_result_supplied",
        },
        metadata={
            **request.metadata,
            "artifact_uris_metadata_only": True,
        },
    )


def _record_external_failure(
    *,
    request: MMMRuntimeCallRequest,
    runtime_reference: MMMRuntimeReference,
    failure_packet: MMMRuntimeFailurePacket,
    warnings: list[str],
    issues: list[MMMRuntimeCallIssueCode],
    lineage: dict[str, str],
) -> MMMRuntimeCallResult:
    issues.append(MMMRuntimeCallIssueCode.FAILURE_PACKET_CREATED)
    issues.append(MMMRuntimeCallIssueCode.RUNTIME_STATUS_RECORDED)
    return MMMRuntimeCallResult(
        request_id=request.request_id,
        status=MMMRuntimeCallStatus.EXTERNAL_RUNTIME_FAILED,
        decision=MMMRuntimeCallDecision.BLOCK_RUNTIME_CALL,
        runtime_reference=runtime_reference,
        runtime_called=False,
        failure_packet=failure_packet,
        blocked_reasons=list(failure_packet.blocked_reasons) or [failure_packet.message],
        warnings=warnings,
        issues=issues,
        lineage={
            **lineage,
            "record_mode": "external_runtime_failure_supplied",
        },
        metadata=dict(request.metadata),
    )


def _blocked(
    *,
    request: MMMRuntimeCallRequest,
    status: MMMRuntimeCallStatus,
    decision: MMMRuntimeCallDecision,
    runtime_reference: MMMRuntimeReference,
    blocked_reasons: list[str],
    warnings: list[str],
    issues: list[MMMRuntimeCallIssueCode],
    lineage: dict[str, str],
    error_code: str,
    message: str,
) -> MMMRuntimeCallResult:
    failure_packet = MMMRuntimeFailurePacket(
        failure_id=f"mmm-runtime-failure:{request.request_id}",
        request_id=request.request_id,
        status=status,
        error_code=error_code,
        message=message,
        retryable=False,
        blocked_reasons=blocked_reasons,
    )
    return MMMRuntimeCallResult(
        request_id=request.request_id,
        status=status,
        decision=decision,
        runtime_reference=runtime_reference,
        runtime_called=False,
        failure_packet=failure_packet,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        issues=issues,
        lineage=lineage,
        metadata={
            **request.metadata,
            "requested_run_type": _REQUESTED_RUN_TYPE_BLOCKED,
            "adapter_placeholder_reference": request.adapter_placeholder_reference,
            "governance_adapter_reference": request.governance_adapter_reference,
        },
    )


def _result(
    *,
    request: MMMRuntimeCallRequest,
    status: MMMRuntimeCallStatus,
    decision: MMMRuntimeCallDecision,
    runtime_reference: MMMRuntimeReference,
    requested_run_type: str,
    model_config_id: str | None = None,
    trusted_input_package_id: str | None = None,
    blocked_reasons: list[str] | None = None,
    warnings: list[str],
    issues: list[MMMRuntimeCallIssueCode],
    lineage: dict[str, str],
) -> MMMRuntimeCallResult:
    return MMMRuntimeCallResult(
        request_id=request.request_id,
        status=status,
        decision=decision,
        runtime_reference=runtime_reference,
        runtime_called=False,
        blocked_reasons=blocked_reasons or [],
        warnings=warnings,
        issues=issues,
        lineage=lineage,
        metadata={
            **request.metadata,
            "requested_run_type": requested_run_type,
            "model_config_id": model_config_id or "",
            "trusted_input_package_id": trusted_input_package_id or "",
            "adapter_placeholder_reference": (
                request.adapter_placeholder_reference or DEFAULT_ADAPTER_PLACEHOLDER_REFERENCE
            ),
            "governance_adapter_reference": (
                request.governance_adapter_reference or DEFAULT_GOVERNANCE_ADAPTER_REFERENCE
            ),
        },
    )


def _default_runtime_reference(request_id: str) -> MMMRuntimeReference:
    return MMMRuntimeReference(
        runtime_id=f"mmm-runtime:{request_id}",
        runtime_kind=MMMRuntimeEngineKind.EXTERNAL_MMM_ENGINE,
        runtime_name="external_mmm_runtime",
        runtime_version="unspecified",
        environment="external",
        owner="mmm_engine_operator",
        metadata={"metadata_only": True},
    )


def _trusted_input_package_id(
    request: MMMRuntimeCallRequest,
    eligibility: PlanningMMMModelRunEligibilityResult,
) -> str | None:
    if request.trusted_input_package_id:
        return request.trusted_input_package_id
    if eligibility.trusted_input_package is not None:
        return eligibility.trusted_input_package.package_id
    return None
