"""MMM artifact governance and use-readiness gate (metadata only)."""

from __future__ import annotations

from mip.contracts.mmm_artifact_governance_use_readiness import (
    MMMArtifactGovernanceRoute,
    MMMArtifactGovernanceRouteDecision,
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
from mip.contracts.mmm_runtime_result_ingestion import (
    MMMRuntimeResultIngestionResult,
    MMMRuntimeResultIngestionStatus,
)

_BOUNDARY_ISSUES = (
    MMMArtifactGovernanceUseReadinessIssueCode.NO_MODEL_PROMOTION_IMPLEMENTED,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_TRUST_REPORT_CONSTRUCTION,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_DECISION_SURFACE_CONSTRUCTION,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_DECISION_SURFACE_EXECUTION,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_RECOMMENDATION_GENERATION,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_ARTIFACT_LOADING,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_DIAGNOSTICS_PARSING,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_DIAGNOSTICS_CALCULATION,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_MODEL_LOADING,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_MODEL_EXECUTION,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_MMM_FITTING,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_OPTIMIZER_EXECUTION,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_SIMULATOR_EXECUTION,
    MMMArtifactGovernanceUseReadinessIssueCode.NO_CLAIM_AUTHORIZATION,
    MMMArtifactGovernanceUseReadinessIssueCode.LINEAGE_PRESERVED,
)

_PLANNING_ALLOWED_USES = frozenset(
    {
        MMMModelAllowedUse.BUDGET_PLANNING,
        MMMModelAllowedUse.BUDGET_OPTIMIZATION,
        MMMModelAllowedUse.SCENARIO_SIMULATION,
    }
)

_RUNTIME_FAILED_STATUSES = frozenset(
    {
        MMMRuntimeResultIngestionStatus.INGESTION_RUNTIME_FAILED,
    }
)

_RUNTIME_DEFERRED_STATUSES = frozenset(
    {
        MMMRuntimeResultIngestionStatus.INGESTION_DEFERRED,
    }
)

_RUNTIME_BLOCKED_STATUSES = frozenset(
    {
        MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_RUNTIME_RESULT,
        MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_ARTIFACT_HANDOFF,
        MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_EXTERNAL_RUN_ID,
        MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_MODEL_ARTIFACT_URI,
        MMMRuntimeResultIngestionStatus.INGESTION_BLOCKED_MISSING_MANIFEST_URI,
        MMMRuntimeResultIngestionStatus.INGESTION_DIAGNOSTICS_METADATA_MISSING,
    }
)


def evaluate_mmm_artifact_governance_and_use_readiness(
    request: MMMArtifactGovernanceUseReadinessRequest,
) -> MMMArtifactGovernanceUseReadinessResult:
    """Evaluate governance routes and use readiness for an ingested MMM runtime result."""
    lineage = {
        **request.lineage,
        "governance_use_readiness_stage": "mmm_artifact_governance_use_readiness",
    }
    warnings: list[str] = []
    issues: list[MMMArtifactGovernanceUseReadinessIssueCode] = list(_BOUNDARY_ISSUES)

    if request.runtime_ingestion_result is None:
        return _terminal(
            request=request,
            status=MMMArtifactGovernanceUseReadinessStatus.MISSING_RUNTIME_INGESTION_RESULT,
            use_readiness=MMMArtifactUseReadiness.UNKNOWN,
            route_decisions=[
                _disabled_route(
                    MMMArtifactGovernanceRoute.NO_ROUTE_BLOCKED,
                    "runtime ingestion result is missing",
                )
            ],
            blocked_reasons=["runtime ingestion result is missing"],
            warnings=warnings,
            issues=issues
            + [
                MMMArtifactGovernanceUseReadinessIssueCode.RUNTIME_INGESTION_RESULT_MISSING,
                MMMArtifactGovernanceUseReadinessIssueCode.BLOCKED_BY_RUNTIME_INGESTION,
            ],
            lineage=lineage,
        )

    ingestion = request.runtime_ingestion_result
    issues.append(MMMArtifactGovernanceUseReadinessIssueCode.RUNTIME_INGESTION_RESULT_PRESENT)
    warnings.extend(ingestion.warnings)
    lineage = {**lineage, **ingestion.lineage}

    model_artifact = request.model_artifact
    if model_artifact is not None:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.MODEL_ARTIFACT_PRESENT)
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.REUSED_MODEL_ARTIFACT_METADATA)
    else:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.MODEL_ARTIFACT_MISSING)
        if request.require_model_artifact:
            return _terminal(
                request=request,
                status=MMMArtifactGovernanceUseReadinessStatus.MISSING_REQUIRED_ARTIFACT_METADATA,
                use_readiness=MMMArtifactUseReadiness.BLOCKED,
                route_decisions=[
                    _disabled_route(
                        MMMArtifactGovernanceRoute.NO_ROUTE_BLOCKED,
                        "model artifact is required but missing",
                    )
                ],
                blocked_reasons=["model artifact is required but missing"],
                warnings=warnings,
                issues=issues
                + [MMMArtifactGovernanceUseReadinessIssueCode.BLOCKED_MISSING_METADATA],
                lineage=lineage,
                ingestion=ingestion,
            )

    if ingestion.status in _RUNTIME_FAILED_STATUSES:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.RUNTIME_FAILED)
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.BLOCKED_BY_RUNTIME_INGESTION)
        diagnostic_route = _diagnostic_route_if_allowed(
            request=request,
            ingestion=ingestion,
            enabled=request.allow_diagnostic_only_route,
            reason="runtime failed; diagnostic review only if diagnostics metadata exists",
            warnings=warnings,
        )
        return _terminal(
            request=request,
            status=MMMArtifactGovernanceUseReadinessStatus.RUNTIME_FAILED,
            use_readiness=MMMArtifactUseReadiness.BLOCKED,
            route_decisions=[
                _disabled_route(
                    MMMArtifactGovernanceRoute.TRUST_REPORT_REVIEW,
                    "runtime failed",
                ),
                _disabled_route(
                    MMMArtifactGovernanceRoute.DECISION_SURFACE_REVIEW,
                    "runtime failed",
                ),
                diagnostic_route,
            ],
            blocked_reasons=list(ingestion.blocked_reasons) or ["runtime ingestion failed"],
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            ingestion=ingestion,
            model_artifact=model_artifact,
            ready_for_diagnostic_review=diagnostic_route.enabled,
            diagnostic_only=diagnostic_route.enabled,
            human_review_required=diagnostic_route.enabled,
        )

    if ingestion.status in _RUNTIME_DEFERRED_STATUSES or (
        not ingestion.ready_for_governance_review
        and ingestion.status == MMMRuntimeResultIngestionStatus.INGESTION_DEFERRED
    ):
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.DEFERRED_BY_RUNTIME_INGESTION)
        issues.append(
            MMMArtifactGovernanceUseReadinessIssueCode.RUNTIME_RESULT_NOT_READY_FOR_GOVERNANCE
        )
        return _terminal(
            request=request,
            status=MMMArtifactGovernanceUseReadinessStatus.DEFERRED,
            use_readiness=MMMArtifactUseReadiness.DEFERRED,
            route_decisions=[
                _disabled_route(
                    MMMArtifactGovernanceRoute.NO_ROUTE_DEFERRED,
                    "runtime ingestion deferred",
                )
            ],
            blocked_reasons=list(ingestion.blocked_reasons) or ["runtime ingestion deferred"],
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            ingestion=ingestion,
            model_artifact=model_artifact,
        )

    if (
        not ingestion.ready_for_governance_review
        or ingestion.status in _RUNTIME_BLOCKED_STATUSES
    ):
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.BLOCKED_BY_RUNTIME_INGESTION)
        issues.append(
            MMMArtifactGovernanceUseReadinessIssueCode.RUNTIME_RESULT_NOT_READY_FOR_GOVERNANCE
        )
        return _terminal(
            request=request,
            status=MMMArtifactGovernanceUseReadinessStatus.BLOCKED,
            use_readiness=MMMArtifactUseReadiness.BLOCKED,
            route_decisions=[
                _disabled_route(
                    MMMArtifactGovernanceRoute.NO_ROUTE_BLOCKED,
                    "runtime ingestion not ready for governance review",
                )
            ],
            blocked_reasons=list(ingestion.blocked_reasons)
            or ["runtime ingestion not ready for governance review"],
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            ingestion=ingestion,
            model_artifact=model_artifact,
        )

    issues.append(MMMArtifactGovernanceUseReadinessIssueCode.RUNTIME_RESULT_READY_FOR_GOVERNANCE)

    model_artifact_uri, diagnostics_uri, manifest_uri = _resolve_uris(ingestion, model_artifact)
    missing_required: list[str] = []

    if request.require_model_artifact_uri and not model_artifact_uri:
        missing_required.append("model artifact URI")
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.MODEL_ARTIFACT_URI_MISSING)
    elif model_artifact_uri:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.MODEL_ARTIFACT_URI_PRESENT)

    if request.require_manifest_uri and not manifest_uri:
        missing_required.append("manifest URI")
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.MANIFEST_URI_MISSING)
    elif manifest_uri:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.MANIFEST_URI_PRESENT)

    if request.require_diagnostics_uri and not diagnostics_uri:
        missing_required.append("diagnostics URI")
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.DIAGNOSTICS_URI_MISSING)
    elif diagnostics_uri:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.DIAGNOSTICS_URI_PRESENT)
    else:
        warnings.append("diagnostics URI is missing")
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.DIAGNOSTICS_URI_MISSING)

    if missing_required:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.BLOCKED_MISSING_METADATA)
        diagnostic_route = _diagnostic_route_if_allowed(
            request=request,
            ingestion=ingestion,
            enabled=request.allow_diagnostic_only_route and bool(diagnostics_uri),
            reason="required artifact metadata missing",
            warnings=warnings,
        )
        return _terminal(
            request=request,
            status=MMMArtifactGovernanceUseReadinessStatus.MISSING_REQUIRED_ARTIFACT_METADATA,
            use_readiness=MMMArtifactUseReadiness.BLOCKED,
            route_decisions=[
                _disabled_route(
                    MMMArtifactGovernanceRoute.TRUST_REPORT_REVIEW,
                    "required artifact metadata missing",
                ),
                _disabled_route(
                    MMMArtifactGovernanceRoute.DECISION_SURFACE_REVIEW,
                    "required artifact metadata missing",
                ),
                diagnostic_route,
            ],
            blocked_reasons=[f"missing required metadata: {', '.join(missing_required)}"],
            warnings=warnings,
            issues=issues,
            lineage=lineage,
            ingestion=ingestion,
            model_artifact=model_artifact,
            ready_for_diagnostic_review=diagnostic_route.enabled,
            diagnostic_only=diagnostic_route.enabled,
            human_review_required=diagnostic_route.enabled,
        )

    planning_ready, diagnostic_only, use_readiness, model_issues, model_warnings = (
        _evaluate_model_use_readiness(model_artifact)
    )
    issues.extend(model_issues)
    warnings.extend(model_warnings)

    trust_candidate = _trust_candidate_reference(ingestion)
    surface_candidate = _decision_surface_candidate_reference(ingestion, model_artifact)
    diagnostic_candidate = _diagnostic_candidate_reference(ingestion)

    trust_enabled = request.allow_trust_report_route
    surface_enabled = (
        request.allow_decision_surface_route
        and planning_ready
        and not diagnostic_only
    )
    diagnostic_enabled = request.allow_diagnostic_only_route and (
        diagnostic_only or bool(warnings) or bool(diagnostics_uri)
    )

    if diagnostic_only:
        trust_enabled = request.allow_trust_report_route
        surface_enabled = False
        planning_ready = False
        if use_readiness != MMMArtifactUseReadiness.NOT_PLANNING_READY:
            use_readiness = MMMArtifactUseReadiness.DIAGNOSTIC_ONLY

    route_decisions = [
        MMMArtifactGovernanceRouteDecision(
            route=MMMArtifactGovernanceRoute.TRUST_REPORT_REVIEW,
            enabled=trust_enabled,
            reason=(
                "runtime result ready for TrustReport review"
                if trust_enabled
                else "TrustReport review route disabled or not allowed"
            ),
            candidate_reference=trust_candidate if trust_enabled else None,
            blocked_reasons=[] if trust_enabled else ["trust report route not enabled"],
            metadata={"metadata_only_candidate_reference": True},
        ),
        MMMArtifactGovernanceRouteDecision(
            route=MMMArtifactGovernanceRoute.DECISION_SURFACE_REVIEW,
            enabled=surface_enabled,
            reason=(
                "planning-ready metadata supports DecisionSurface review"
                if surface_enabled
                else "DecisionSurface review requires planning-ready metadata"
            ),
            candidate_reference=surface_candidate if surface_enabled else None,
            blocked_reasons=[] if surface_enabled else ["decision surface route not enabled"],
            metadata={"metadata_only_candidate_reference": True},
        ),
        MMMArtifactGovernanceRouteDecision(
            route=MMMArtifactGovernanceRoute.DIAGNOSTIC_REVIEW,
            enabled=diagnostic_enabled,
            reason=(
                "diagnostic review available from diagnostics metadata or warnings"
                if diagnostic_enabled
                else "diagnostic review not enabled"
            ),
            candidate_reference=diagnostic_candidate if diagnostic_enabled else None,
            blocked_reasons=[] if diagnostic_enabled else ["diagnostic route not enabled"],
            metadata={"metadata_only_candidate_reference": True},
        ),
    ]

    if trust_enabled:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.TRUST_REVIEW_ROUTE_READY)
    if surface_enabled:
        issues.append(
            MMMArtifactGovernanceUseReadinessIssueCode.DECISION_SURFACE_REVIEW_ROUTE_READY
        )
    if diagnostic_enabled:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.DIAGNOSTIC_REVIEW_ROUTE_READY)
    if planning_ready:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.PLANNING_USE_ALLOWED)
    else:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.PLANNING_USE_NOT_ALLOWED)
    if diagnostic_only:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.DIAGNOSTIC_ONLY_USE)

    human_review_required = bool(
        trust_enabled
        or surface_enabled
        or warnings
        or (
            model_artifact is not None
            and model_artifact.promotion_status
            in {MMMModelPromotionStatus.UNKNOWN, MMMModelPromotionStatus.NOT_PROMOTED}
            and (trust_enabled or surface_enabled)
        )
    )
    if human_review_required:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.HUMAN_REVIEW_REQUIRED)

    if diagnostic_only and not planning_ready:
        status = MMMArtifactGovernanceUseReadinessStatus.DIAGNOSTIC_ONLY
    elif warnings:
        status = MMMArtifactGovernanceUseReadinessStatus.READY_FOR_GOVERNANCE_REVIEW_WITH_WARNINGS
    else:
        status = MMMArtifactGovernanceUseReadinessStatus.READY_FOR_GOVERNANCE_REVIEW

    return _terminal(
        request=request,
        status=status,
        use_readiness=use_readiness,
        route_decisions=route_decisions,
        blocked_reasons=[],
        warnings=warnings,
        issues=issues,
        lineage=lineage,
        ingestion=ingestion,
        model_artifact=model_artifact,
        ready_for_trust_report_review=trust_enabled,
        ready_for_decision_surface_review=surface_enabled,
        ready_for_diagnostic_review=diagnostic_enabled,
        planning_ready=planning_ready,
        diagnostic_only=diagnostic_only,
        human_review_required=human_review_required,
    )


def summarize_mmm_artifact_governance_and_use_readiness(
    result: MMMArtifactGovernanceUseReadinessResult,
) -> dict[str, object]:
    """Summarize governance/use-readiness outcome without recommendation language."""
    return {
        "status": str(result.status),
        "use_readiness": str(result.use_readiness),
        "routes_enabled": [
            str(decision.route) for decision in result.route_decisions if decision.enabled
        ],
        "planning_ready": result.planning_ready,
        "diagnostic_only": result.diagnostic_only,
        "human_review_required": result.human_review_required,
        "external_run_id": result.external_run_id,
        "model_artifact_id": result.model_artifact_id,
        "blocked_reasons": list(result.blocked_reasons),
        "warnings": list(result.warnings),
    }


def _evaluate_model_use_readiness(
    model_artifact: MMMModelArtifact | None,
) -> tuple[
    bool,
    bool,
    MMMArtifactUseReadiness,
    list[MMMArtifactGovernanceUseReadinessIssueCode],
    list[str],
]:
    issues: list[MMMArtifactGovernanceUseReadinessIssueCode] = []
    warnings: list[str] = []

    if model_artifact is None:
        return True, False, MMMArtifactUseReadiness.PLANNING_READY, issues, warnings

    promotion = model_artifact.promotion_status
    diagnostic = model_artifact.diagnostic_status
    allowed_uses = list(model_artifact.allowed_uses)

    if promotion == MMMModelPromotionStatus.UNKNOWN:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.PROMOTION_STATUS_MISSING)
        warnings.append("model artifact promotion status is unknown")
    else:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.PROMOTION_STATUS_PRESENT)

    if diagnostic == MMMModelDiagnosticStatus.UNKNOWN:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.DIAGNOSTIC_STATUS_MISSING)
        warnings.append("model artifact diagnostic status is unknown")
    else:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.DIAGNOSTIC_STATUS_PRESENT)

    if allowed_uses:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.ALLOWED_USES_PRESENT)
    else:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.ALLOWED_USES_MISSING)
        warnings.append("model artifact allowed uses are missing")

    if promotion in {
        MMMModelPromotionStatus.NOT_PROMOTED,
        MMMModelPromotionStatus.REVOKED,
    }:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.BLOCKED_BY_PROMOTION_STATUS)
        return False, False, MMMArtifactUseReadiness.BLOCKED, issues, warnings

    if diagnostic == MMMModelDiagnosticStatus.FAILED:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.BLOCKED_BY_DIAGNOSTIC_STATUS)
        return False, True, MMMArtifactUseReadiness.DIAGNOSTIC_ONLY, issues, warnings

    if promotion == MMMModelPromotionStatus.PROMOTED_FOR_DIAGNOSTIC_ONLY:
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.DIAGNOSTIC_ONLY_USE)
        return False, True, MMMArtifactUseReadiness.DIAGNOSTIC_ONLY, issues, warnings

    if MMMModelAllowedUse.DIAGNOSTIC_ONLY in allowed_uses and not any(
        use in _PLANNING_ALLOWED_USES for use in allowed_uses
    ):
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.DIAGNOSTIC_ONLY_USE)
        return False, True, MMMArtifactUseReadiness.DIAGNOSTIC_ONLY, issues, warnings

    if allowed_uses and not any(use in _PLANNING_ALLOWED_USES for use in allowed_uses):
        issues.append(MMMArtifactGovernanceUseReadinessIssueCode.PLANNING_USE_NOT_ALLOWED)
        return False, False, MMMArtifactUseReadiness.NOT_PLANNING_READY, issues, warnings

    if diagnostic == MMMModelDiagnosticStatus.PASSED_WITH_WARNINGS:
        warnings.append("model artifact diagnostic status passed with warnings")

    if promotion == MMMModelPromotionStatus.PROMOTED_FOR_PLANNING or not allowed_uses:
        return True, False, MMMArtifactUseReadiness.PLANNING_READY, issues, warnings

    if any(use in _PLANNING_ALLOWED_USES for use in allowed_uses):
        return True, False, MMMArtifactUseReadiness.PLANNING_READY, issues, warnings

    return False, False, MMMArtifactUseReadiness.NOT_PLANNING_READY, issues, warnings


def _resolve_uris(
    ingestion: MMMRuntimeResultIngestionResult,
    model_artifact: MMMModelArtifact | None,
) -> tuple[str | None, str | None, str | None]:
    handoff = ingestion.artifact_handoff
    model_uri = None
    diagnostics_uri = None
    manifest_uri = None
    if handoff is not None:
        model_uri = handoff.model_artifact_uri
        diagnostics_uri = handoff.diagnostics_uri
        manifest_uri = handoff.manifest_uri
    if ingestion.diagnostics_metadata is not None:
        diagnostics_uri = diagnostics_uri or ingestion.diagnostics_metadata.diagnostics_uri
        manifest_uri = manifest_uri or ingestion.diagnostics_metadata.manifest_uri
    if ingestion.governance_routing_reference is not None:
        routing = ingestion.governance_routing_reference
        model_uri = model_uri or routing.model_artifact_uri
        diagnostics_uri = diagnostics_uri or routing.diagnostics_uri
        manifest_uri = manifest_uri or routing.manifest_uri
    if model_artifact is not None and model_artifact.artifact_uri:
        model_uri = model_uri or model_artifact.artifact_uri
    return model_uri, diagnostics_uri, manifest_uri


def _trust_candidate_reference(ingestion: MMMRuntimeResultIngestionResult) -> str | None:
    if ingestion.governance_routing_reference is not None:
        return ingestion.governance_routing_reference.trust_report_candidate_reference
    if ingestion.external_run_id:
        return f"trust_report:candidate:{ingestion.external_run_id}"
    return None


def _decision_surface_candidate_reference(
    ingestion: MMMRuntimeResultIngestionResult,
    model_artifact: MMMModelArtifact | None,
) -> str | None:
    if model_artifact is not None and model_artifact.decision_surface_id:
        return model_artifact.decision_surface_id
    if ingestion.governance_routing_reference is not None:
        return ingestion.governance_routing_reference.decision_surface_candidate_reference
    if ingestion.external_run_id:
        return f"decision_surface:candidate:{ingestion.external_run_id}"
    return None


def _diagnostic_candidate_reference(ingestion: MMMRuntimeResultIngestionResult) -> str | None:
    if ingestion.diagnostics_metadata is not None:
        return ingestion.diagnostics_metadata.diagnostics_summary_reference
    if ingestion.external_run_id:
        return f"diagnostics_summary_ref:{ingestion.external_run_id}"
    return None


def _diagnostic_route_if_allowed(
    *,
    request: MMMArtifactGovernanceUseReadinessRequest,
    ingestion: MMMRuntimeResultIngestionResult,
    enabled: bool,
    reason: str,
    warnings: list[str],
) -> MMMArtifactGovernanceRouteDecision:
    has_diagnostics = bool(
        (ingestion.artifact_handoff and ingestion.artifact_handoff.diagnostics_uri)
        or (
            ingestion.diagnostics_metadata
            and ingestion.diagnostics_metadata.diagnostics_uri
        )
    )
    route_enabled = enabled and has_diagnostics and request.allow_diagnostic_only_route
    return MMMArtifactGovernanceRouteDecision(
        route=MMMArtifactGovernanceRoute.DIAGNOSTIC_REVIEW,
        enabled=route_enabled,
        reason=reason if route_enabled else f"{reason}; diagnostic route not enabled",
        candidate_reference=_diagnostic_candidate_reference(ingestion) if route_enabled else None,
        blocked_reasons=[] if route_enabled else ["diagnostic route not enabled"],
        warnings=list(warnings),
        metadata={"metadata_only_candidate_reference": True},
    )


def _disabled_route(
    route: MMMArtifactGovernanceRoute,
    reason: str,
) -> MMMArtifactGovernanceRouteDecision:
    return MMMArtifactGovernanceRouteDecision(
        route=route,
        enabled=False,
        reason=reason,
        blocked_reasons=[reason],
        metadata={"metadata_only_candidate_reference": True},
    )


def _terminal(
    *,
    request: MMMArtifactGovernanceUseReadinessRequest,
    status: MMMArtifactGovernanceUseReadinessStatus,
    use_readiness: MMMArtifactUseReadiness,
    route_decisions: list[MMMArtifactGovernanceRouteDecision],
    blocked_reasons: list[str],
    warnings: list[str],
    issues: list[MMMArtifactGovernanceUseReadinessIssueCode],
    lineage: dict[str, str],
    ingestion: MMMRuntimeResultIngestionResult | None = None,
    model_artifact: MMMModelArtifact | None = None,
    ready_for_trust_report_review: bool = False,
    ready_for_decision_surface_review: bool = False,
    ready_for_diagnostic_review: bool = False,
    planning_ready: bool = False,
    diagnostic_only: bool = False,
    human_review_required: bool = False,
) -> MMMArtifactGovernanceUseReadinessResult:
    model_uri = None
    diagnostics_uri = None
    manifest_uri = None
    external_run_id = None
    ingestion_id = None
    if ingestion is not None:
        ingestion_id = ingestion.request_id
        external_run_id = ingestion.external_run_id
        model_uri, diagnostics_uri, manifest_uri = _resolve_uris(ingestion, model_artifact)
    elif model_artifact is not None:
        model_uri = model_artifact.artifact_uri

    return MMMArtifactGovernanceUseReadinessResult(
        request_id=request.request_id,
        status=status,
        use_readiness=use_readiness,
        route_decisions=route_decisions,
        ready_for_trust_report_review=ready_for_trust_report_review,
        ready_for_decision_surface_review=ready_for_decision_surface_review,
        ready_for_diagnostic_review=ready_for_diagnostic_review,
        planning_ready=planning_ready,
        diagnostic_only=diagnostic_only,
        human_review_required=human_review_required,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        issues=issues,
        runtime_ingestion_result_id=ingestion_id,
        external_run_id=external_run_id,
        model_artifact_id=model_artifact.model_id if model_artifact is not None else None,
        model_artifact_uri=model_uri,
        diagnostics_uri=diagnostics_uri,
        manifest_uri=manifest_uri,
        lineage=lineage,
        metadata={
            **request.metadata,
            "reused_model_artifact_metadata": model_artifact is not None,
            "separate_model_promotion_gate_added": False,
        },
    )
