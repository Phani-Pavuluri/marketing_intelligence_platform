"""GeoX readout trust-routing workflow.

Routes GeoXReadoutResultEnvelope to governance boundary metadata only. No panel_exp
import, metric recomputation, or claim authorization.
"""

from __future__ import annotations

from mip.contracts.geox_panel_exp_runtime_call import CLAIM_AUTHORIZATION_OWNER
from mip.contracts.geox_readout_result_ingestion import (
    GeoXReadoutResultEnvelope,
    GeoXReadoutResultStatus,
)
from mip.contracts.geox_readout_trust_routing import (
    DECISION_SURFACE_CONTRACT_NAME,
    RECOMMENDATION_CONTRACT_NAME,
    TRUST_REPORT_CONTRACT_NAME,
    GeoXReadoutRecommendationReadiness,
    GeoXReadoutTrustRoute,
    GeoXReadoutTrustRouteTarget,
    GeoXReadoutTrustRoutingEnvelope,
    GeoXReadoutTrustRoutingIssueCode,
    GeoXReadoutTrustRoutingRequest,
    GeoXReadoutTrustRoutingResult,
    GeoXReadoutTrustRoutingStatus,
)

_READY_ENVELOPE_STATUSES = frozenset(
    {
        GeoXReadoutResultStatus.EXPLAINED_READY_PACKAGE_RESULT,
    }
)
_BLOCKED_ENVELOPE_STATUSES = frozenset(
    {
        GeoXReadoutResultStatus.EXPLAINED_BLOCKED_PACKAGE_RESULT,
    }
)
_DIAGNOSTIC_ENVELOPE_STATUSES = frozenset(
    {
        GeoXReadoutResultStatus.EXPLAINED_DIAGNOSTIC_ONLY_PACKAGE_RESULT,
    }
)
_READY_PACKAGE_STATUSES = frozenset({"READY", "ready"})
_BLOCKED_PACKAGE_PREFIXES = ("BLOCKED_", "blocked_")
_DIAGNOSTIC_PACKAGE_STATUSES = frozenset(
    {"PARTIAL_DIAGNOSTIC_ONLY", "partial_diagnostic_only"}
)


def route_geox_readout_result_to_trust_boundaries(
    request: GeoXReadoutTrustRoutingRequest,
) -> GeoXReadoutTrustRoutingResult:
    """Route a GeoX readout result envelope to governance boundary readiness metadata."""
    lineage = {
        **request.lineage,
        "routing_stage": "geox_readout_trust_routing",
        "requested_route": str(request.requested_route),
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[GeoXReadoutTrustRoutingIssueCode] = [
        GeoXReadoutTrustRoutingIssueCode.ROI_ROAS_NOT_COMPUTED_IN_MIP,
        GeoXReadoutTrustRoutingIssueCode.LIFT_NOT_COMPUTED_IN_MIP,
        GeoXReadoutTrustRoutingIssueCode.CLAIM_AUTHORIZATION_DELEGATED,
        GeoXReadoutTrustRoutingIssueCode.NO_BUSINESS_RECOMMENDATION_AUTHORIZED,
        GeoXReadoutTrustRoutingIssueCode.TRUST_REPORT_REQUIRED,
        GeoXReadoutTrustRoutingIssueCode.DECISION_SURFACE_REQUIRED,
        GeoXReadoutTrustRoutingIssueCode.RECOMMENDATION_CONTRACT_BLOCKED,
    ]

    if request.result_envelope is None:
        return _blocked(
            request.request_id,
            GeoXReadoutTrustRoutingStatus.BLOCKED_MISSING_RESULT_ENVELOPE,
            issues + [GeoXReadoutTrustRoutingIssueCode.MISSING_RESULT_ENVELOPE],
            warnings,
            lineage,
        )

    envelope = request.result_envelope
    validation_error = _validate_result_envelope(envelope)
    if validation_error is not None:
        return _blocked(
            request.request_id,
            GeoXReadoutTrustRoutingStatus.BLOCKED_RESULT_MALFORMED,
            issues + [GeoXReadoutTrustRoutingIssueCode.RESULT_ENVELOPE_MALFORMED],
            warnings + [validation_error],
            lineage,
        )

    claim_status, claim_issues, claim_block_status = _resolve_claim_boundary(envelope)
    issues.extend(claim_issues)
    if claim_block_status is not None:
        return _blocked(
            request.request_id,
            claim_block_status,
            issues,
            warnings,
            lineage,
        )

    package_warnings = list(dict.fromkeys(envelope.package_warnings + envelope.warnings))
    if package_warnings:
        issues.append(GeoXReadoutTrustRoutingIssueCode.PACKAGE_WARNINGS_PRESENT)
        warnings.extend(package_warnings)

    if "package_computed_spend_delta" in envelope.package_output_summary:
        issues.append(GeoXReadoutTrustRoutingIssueCode.SPEND_DELTA_PACKAGE_COMPUTED)

    result_class = _classify_result_envelope(envelope)
    trust_report_complete = _trust_report_review_complete(envelope, request.lineage)

    if result_class == "blocked":
        return _route_blocked_package(
            request, envelope, claim_status, package_warnings, issues, warnings, lineage
        )
    if result_class == "diagnostic":
        return _route_diagnostic_only(
            request, envelope, claim_status, package_warnings, issues, warnings, lineage
        )

    if request.requested_route == GeoXReadoutTrustRoute.RECOMMENDATION_CONTRACT_BLOCKED:
        return _route_recommendation_blocked(
            request, envelope, claim_status, package_warnings, issues, warnings, lineage
        )

    if request.requested_route == GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW:
        return _route_decision_surface_requested(
            request,
            envelope,
            claim_status,
            package_warnings,
            issues,
            warnings,
            lineage,
            trust_report_complete=trust_report_complete,
        )

    return _route_ready_to_trust_report(
        request, envelope, claim_status, package_warnings, issues, warnings, lineage
    )


def build_geox_readout_trust_route_summary(
    *,
    primary_route: GeoXReadoutTrustRoute,
    trust_ready: bool,
    decision_surface_ready: bool,
    recommendation_blocked: bool,
    package_readiness: str,
) -> str:
    """Produce a short governance routing summary without business recommendations."""
    if primary_route == GeoXReadoutTrustRoute.NO_ROUTE_BLOCKED:
        return (
            f"Package result ({package_readiness}) is blocked. "
            "No TrustReport, DecisionSurface, or RecommendationContract route is open."
        )
    if primary_route == GeoXReadoutTrustRoute.DIAGNOSTIC_ONLY_REVIEW:
        return (
            "Package result is diagnostic-only. "
            "RecommendationContract remains blocked for production claims."
        )
    if primary_route == GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW and decision_surface_ready:
        return (
            "Package result completed TrustReport review and is ready for "
            "DecisionSurface review. RecommendationContract remains blocked."
        )
    if trust_ready:
        return (
            "Package result is ready for TrustReport review. "
            "DecisionSurface and RecommendationContract remain blocked until "
            "governed review completes."
        )
    if recommendation_blocked:
        return (
            "RecommendationContract remains blocked. Governed DecisionSurface review "
            "is required before any recommendation assembly."
        )
    return "GeoX readout result trust routing recorded; governance review required."


def _validate_result_envelope(envelope: GeoXReadoutResultEnvelope) -> str | None:
    if not envelope.experiment_id.strip():
        return "result envelope missing experiment_id"
    if not envelope.result_id.strip():
        return "result envelope missing result_id"
    if not envelope.package_readiness_status.strip():
        return "result envelope missing package_readiness_status"
    if not envelope.claim_authorization_owner.strip():
        return "result envelope missing claim_authorization_owner"
    if not envelope.explanation.summary.strip():
        return "result envelope missing explanation summary"
    return None


def _resolve_claim_boundary(
    envelope: GeoXReadoutResultEnvelope,
) -> tuple[str, list[GeoXReadoutTrustRoutingIssueCode], GeoXReadoutTrustRoutingStatus | None]:
    issues: list[GeoXReadoutTrustRoutingIssueCode] = []
    roi_status = str(
        envelope.trusted_handoff_summary.get("roi_claim_authorization_status", "NOT_EVALUATED")
    )
    owner = envelope.claim_authorization_owner

    if owner == CLAIM_AUTHORIZATION_OWNER:
        claim_status = "DELEGATED"
        if roi_status == "NOT_EVALUATED":
            issues.append(GeoXReadoutTrustRoutingIssueCode.CLAIM_AUTHORIZATION_NOT_EVALUATED)
        return claim_status, issues, None

    if roi_status == "NOT_EVALUATED" or not owner.strip():
        issues.append(GeoXReadoutTrustRoutingIssueCode.CLAIM_AUTHORIZATION_NOT_EVALUATED)
        return "NOT_EVALUATED", issues, (
            GeoXReadoutTrustRoutingStatus.BLOCKED_CLAIM_AUTHORIZATION_NOT_EVALUATED
        )
    return "NOT_AUTHORIZED", issues, None


def _classify_result_envelope(envelope: GeoXReadoutResultEnvelope) -> str:
    if envelope.status in _BLOCKED_ENVELOPE_STATUSES:
        return "blocked"
    if envelope.status in _DIAGNOSTIC_ENVELOPE_STATUSES:
        return "diagnostic"
    if envelope.status in _READY_ENVELOPE_STATUSES:
        return "ready"

    package_status = envelope.package_readiness_status.strip()
    upper = package_status.upper()
    if upper in _DIAGNOSTIC_PACKAGE_STATUSES:
        return "diagnostic"
    if upper.startswith("BLOCKED_"):
        return "blocked"
    if upper in _READY_PACKAGE_STATUSES:
        return "ready"
    return "blocked"


def _trust_report_review_complete(
    envelope: GeoXReadoutResultEnvelope,
    request_lineage: dict[str, str],
) -> bool:
    merged = {**envelope.lineage, **request_lineage}
    return merged.get("trust_report_review_complete") == "true"


def _route_ready_to_trust_report(
    request: GeoXReadoutTrustRoutingRequest,
    envelope: GeoXReadoutResultEnvelope,
    claim_status: str,
    package_warnings: list[str],
    issues: list[GeoXReadoutTrustRoutingIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXReadoutTrustRoutingResult:
    trust_route = GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
        target_contract_name=TRUST_REPORT_CONTRACT_NAME,
        ready_for_boundary=True,
        blocked_reason=None,
        required_next_action="Submit package readout result for TrustReport review.",
    )
    decision_route = GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW,
        target_contract_name=DECISION_SURFACE_CONTRACT_NAME,
        ready_for_boundary=False,
        blocked_reason="TrustReport review must complete before DecisionSurface review.",
        required_next_action="Complete TrustReport review, then route to DecisionSurface.",
    )
    recommendation_route = _recommendation_route_blocked(
        reason="RecommendationContract requires governed TrustReport and DecisionSurface review.",
        readiness=GeoXReadoutRecommendationReadiness.BLOCKED_PENDING_TRUST_REPORT,
    )
    routing_summary = build_geox_readout_trust_route_summary(
        primary_route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
        trust_ready=True,
        decision_surface_ready=False,
        recommendation_blocked=True,
        package_readiness=envelope.package_readiness_status,
    )
    routing_envelope = _build_routing_envelope(
        request,
        envelope,
        primary_route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
        status=GeoXReadoutTrustRoutingStatus.ROUTED_TO_TRUST_REPORT_REVIEW,
        trust_route=trust_route,
        decision_route=decision_route,
        recommendation_route=recommendation_route,
        recommendation_readiness=GeoXReadoutRecommendationReadiness.BLOCKED_PENDING_TRUST_REPORT,
        claim_status=claim_status,
        routing_summary=routing_summary,
        issues=issues,
        warnings=warnings,
        lineage=lineage,
    )
    return GeoXReadoutTrustRoutingResult(
        request_id=request.request_id,
        status=GeoXReadoutTrustRoutingStatus.ROUTED_TO_TRUST_REPORT_REVIEW,
        routing_envelope=routing_envelope,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _route_decision_surface_requested(
    request: GeoXReadoutTrustRoutingRequest,
    envelope: GeoXReadoutResultEnvelope,
    claim_status: str,
    package_warnings: list[str],
    issues: list[GeoXReadoutTrustRoutingIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
    *,
    trust_report_complete: bool,
) -> GeoXReadoutTrustRoutingResult:
    recommendation_route = _recommendation_route_blocked(
        reason="RecommendationContract requires governed DecisionSurface review.",
        readiness=GeoXReadoutRecommendationReadiness.BLOCKED_PENDING_DECISION_SURFACE,
    )
    if not trust_report_complete:
        trust_route = GeoXReadoutTrustRouteTarget(
            route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
            target_contract_name=TRUST_REPORT_CONTRACT_NAME,
            ready_for_boundary=True,
            blocked_reason=None,
            required_next_action="Complete TrustReport review before DecisionSurface routing.",
        )
        decision_route = GeoXReadoutTrustRouteTarget(
            route=GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW,
            target_contract_name=DECISION_SURFACE_CONTRACT_NAME,
            ready_for_boundary=False,
            blocked_reason="DecisionSurface routing requested before TrustReport review completed.",
            required_next_action="Complete TrustReport review first.",
        )
        routing_summary = build_geox_readout_trust_route_summary(
            primary_route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
            trust_ready=True,
            decision_surface_ready=False,
            recommendation_blocked=True,
            package_readiness=envelope.package_readiness_status,
        )
        routing_envelope = _build_routing_envelope(
            request,
            envelope,
            primary_route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
            status=GeoXReadoutTrustRoutingStatus.ROUTED_TO_TRUST_REPORT_REVIEW,
            trust_route=trust_route,
            decision_route=decision_route,
            recommendation_route=recommendation_route,
            recommendation_readiness=GeoXReadoutRecommendationReadiness.BLOCKED_PENDING_TRUST_REPORT,
            claim_status=claim_status,
            routing_summary=routing_summary,
            issues=issues,
            warnings=warnings,
            lineage=lineage,
        )
        return GeoXReadoutTrustRoutingResult(
            request_id=request.request_id,
            status=GeoXReadoutTrustRoutingStatus.ROUTED_TO_TRUST_REPORT_REVIEW,
            routing_envelope=routing_envelope,
            issues=_dedupe_issues(issues),
            warnings=list(dict.fromkeys(warnings)),
            lineage=lineage,
        )

    trust_route = GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
        target_contract_name=TRUST_REPORT_CONTRACT_NAME,
        ready_for_boundary=False,
        blocked_reason=None,
        required_next_action="TrustReport review complete.",
        lineage={"trust_report_review_complete": "true"},
    )
    decision_route = GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW,
        target_contract_name=DECISION_SURFACE_CONTRACT_NAME,
        ready_for_boundary=True,
        blocked_reason=None,
        required_next_action="Submit package readout result for DecisionSurface review.",
        lineage={"trust_report_review_complete": "true"},
    )
    issues.append(GeoXReadoutTrustRoutingIssueCode.RECOMMENDATION_REQUIRES_GOVERNED_DECISION_SURFACE)
    routing_summary = build_geox_readout_trust_route_summary(
        primary_route=GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW,
        trust_ready=False,
        decision_surface_ready=True,
        recommendation_blocked=True,
        package_readiness=envelope.package_readiness_status,
    )
    routing_envelope = _build_routing_envelope(
        request,
        envelope,
        primary_route=GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW,
        status=GeoXReadoutTrustRoutingStatus.ROUTED_TO_DECISION_SURFACE_REVIEW,
        trust_route=trust_route,
        decision_route=decision_route,
        recommendation_route=recommendation_route,
        recommendation_readiness=GeoXReadoutRecommendationReadiness.BLOCKED_PENDING_DECISION_SURFACE,
        claim_status=claim_status,
        routing_summary=routing_summary,
        issues=issues,
        warnings=warnings,
        lineage={**lineage, "trust_report_review_complete": "true"},
    )
    return GeoXReadoutTrustRoutingResult(
        request_id=request.request_id,
        status=GeoXReadoutTrustRoutingStatus.ROUTED_TO_DECISION_SURFACE_REVIEW,
        routing_envelope=routing_envelope,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={**lineage, "trust_report_review_complete": "true"},
    )


def _route_recommendation_blocked(
    request: GeoXReadoutTrustRoutingRequest,
    envelope: GeoXReadoutResultEnvelope,
    claim_status: str,
    package_warnings: list[str],
    issues: list[GeoXReadoutTrustRoutingIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXReadoutTrustRoutingResult:
    issues.append(GeoXReadoutTrustRoutingIssueCode.RECOMMENDATION_REQUIRES_GOVERNED_DECISION_SURFACE)
    trust_route = GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
        target_contract_name=TRUST_REPORT_CONTRACT_NAME,
        ready_for_boundary=envelope.status in _READY_ENVELOPE_STATUSES,
        blocked_reason=None if envelope.status in _READY_ENVELOPE_STATUSES else (
            "Package result must be ready before governance routing."
        ),
        required_next_action="Complete TrustReport and DecisionSurface review first.",
    )
    decision_route = GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW,
        target_contract_name=DECISION_SURFACE_CONTRACT_NAME,
        ready_for_boundary=False,
        blocked_reason="DecisionSurface review required before RecommendationContract.",
        required_next_action="Complete governed DecisionSurface review.",
    )
    recommendation_route = _recommendation_route_blocked(
        reason="RecommendationContract assembly is blocked in this routing slice.",
        readiness=GeoXReadoutRecommendationReadiness.NOT_AUTHORIZED,
    )
    routing_summary = build_geox_readout_trust_route_summary(
        primary_route=GeoXReadoutTrustRoute.RECOMMENDATION_CONTRACT_BLOCKED,
        trust_ready=False,
        decision_surface_ready=False,
        recommendation_blocked=True,
        package_readiness=envelope.package_readiness_status,
    )
    routing_envelope = _build_routing_envelope(
        request,
        envelope,
        primary_route=GeoXReadoutTrustRoute.RECOMMENDATION_CONTRACT_BLOCKED,
        status=GeoXReadoutTrustRoutingStatus.ROUTED_TO_RECOMMENDATION_CONTRACT_BLOCKED,
        trust_route=trust_route,
        decision_route=decision_route,
        recommendation_route=recommendation_route,
        recommendation_readiness=GeoXReadoutRecommendationReadiness.NOT_AUTHORIZED,
        claim_status=claim_status,
        routing_summary=routing_summary,
        issues=issues,
        warnings=warnings,
        lineage=lineage,
    )
    return GeoXReadoutTrustRoutingResult(
        request_id=request.request_id,
        status=GeoXReadoutTrustRoutingStatus.ROUTED_TO_RECOMMENDATION_CONTRACT_BLOCKED,
        routing_envelope=routing_envelope,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _route_blocked_package(
    request: GeoXReadoutTrustRoutingRequest,
    envelope: GeoXReadoutResultEnvelope,
    claim_status: str,
    package_warnings: list[str],
    issues: list[GeoXReadoutTrustRoutingIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXReadoutTrustRoutingResult:
    issues.append(GeoXReadoutTrustRoutingIssueCode.PACKAGE_RESULT_BLOCKED)
    trust_route = _no_route_target(
        TRUST_REPORT_CONTRACT_NAME,
        "Package result is blocked; TrustReport review is not available.",
    )
    decision_route = _no_route_target(
        DECISION_SURFACE_CONTRACT_NAME,
        "Package result is blocked; DecisionSurface review is not available.",
    )
    recommendation_route = _recommendation_route_blocked(
        reason="Package result is not ready for RecommendationContract.",
        readiness=GeoXReadoutRecommendationReadiness.BLOCKED_PACKAGE_RESULT_NOT_READY,
    )
    routing_summary = build_geox_readout_trust_route_summary(
        primary_route=GeoXReadoutTrustRoute.NO_ROUTE_BLOCKED,
        trust_ready=False,
        decision_surface_ready=False,
        recommendation_blocked=True,
        package_readiness=envelope.package_readiness_status,
    )
    routing_envelope = _build_routing_envelope(
        request,
        envelope,
        primary_route=GeoXReadoutTrustRoute.NO_ROUTE_BLOCKED,
        status=GeoXReadoutTrustRoutingStatus.BLOCKED_RESULT_NOT_READY,
        trust_route=trust_route,
        decision_route=decision_route,
        recommendation_route=recommendation_route,
        recommendation_readiness=GeoXReadoutRecommendationReadiness.BLOCKED_PACKAGE_RESULT_NOT_READY,
        claim_status=claim_status,
        routing_summary=routing_summary,
        issues=issues,
        warnings=warnings,
        lineage=lineage,
    )
    return GeoXReadoutTrustRoutingResult(
        request_id=request.request_id,
        status=GeoXReadoutTrustRoutingStatus.BLOCKED_RESULT_NOT_READY,
        routing_envelope=routing_envelope,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _route_diagnostic_only(
    request: GeoXReadoutTrustRoutingRequest,
    envelope: GeoXReadoutResultEnvelope,
    claim_status: str,
    package_warnings: list[str],
    issues: list[GeoXReadoutTrustRoutingIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXReadoutTrustRoutingResult:
    issues.append(GeoXReadoutTrustRoutingIssueCode.PACKAGE_RESULT_DIAGNOSTIC_ONLY)
    trust_route = GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.DIAGNOSTIC_ONLY_REVIEW,
        target_contract_name=TRUST_REPORT_CONTRACT_NAME,
        ready_for_boundary=True,
        blocked_reason=None,
        required_next_action="Use diagnostic-only package output; not for production claims.",
    )
    decision_route = GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.DIAGNOSTIC_ONLY_REVIEW,
        target_contract_name=DECISION_SURFACE_CONTRACT_NAME,
        ready_for_boundary=False,
        blocked_reason="Diagnostic-only results cannot proceed to DecisionSurface review.",
        required_next_action="Obtain production-ready package result before DecisionSurface.",
    )
    recommendation_route = _recommendation_route_blocked(
        reason="Diagnostic-only package results cannot support recommendations.",
        readiness=GeoXReadoutRecommendationReadiness.BLOCKED_DIAGNOSTIC_ONLY,
    )
    routing_summary = build_geox_readout_trust_route_summary(
        primary_route=GeoXReadoutTrustRoute.DIAGNOSTIC_ONLY_REVIEW,
        trust_ready=False,
        decision_surface_ready=False,
        recommendation_blocked=True,
        package_readiness=envelope.package_readiness_status,
    )
    routing_envelope = _build_routing_envelope(
        request,
        envelope,
        primary_route=GeoXReadoutTrustRoute.DIAGNOSTIC_ONLY_REVIEW,
        status=GeoXReadoutTrustRoutingStatus.ROUTED_TO_DIAGNOSTIC_ONLY_REVIEW,
        trust_route=trust_route,
        decision_route=decision_route,
        recommendation_route=recommendation_route,
        recommendation_readiness=GeoXReadoutRecommendationReadiness.BLOCKED_DIAGNOSTIC_ONLY,
        claim_status=claim_status,
        routing_summary=routing_summary,
        issues=issues,
        warnings=warnings,
        lineage=lineage,
    )
    return GeoXReadoutTrustRoutingResult(
        request_id=request.request_id,
        status=GeoXReadoutTrustRoutingStatus.ROUTED_TO_DIAGNOSTIC_ONLY_REVIEW,
        routing_envelope=routing_envelope,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _recommendation_route_blocked(
    *,
    reason: str,
    readiness: GeoXReadoutRecommendationReadiness,
) -> GeoXReadoutTrustRouteTarget:
    return GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.RECOMMENDATION_CONTRACT_BLOCKED,
        target_contract_name=RECOMMENDATION_CONTRACT_NAME,
        ready_for_boundary=False,
        blocked_reason=reason,
        required_next_action="Do not authorize business recommendations in trust routing.",
        lineage={"recommendation_readiness": readiness.value},
    )


def _no_route_target(contract_name: str, reason: str) -> GeoXReadoutTrustRouteTarget:
    return GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.NO_ROUTE_BLOCKED,
        target_contract_name=contract_name,
        ready_for_boundary=False,
        blocked_reason=reason,
        required_next_action="Resolve package blockers before governance routing.",
    )


def _build_routing_envelope(
    request: GeoXReadoutTrustRoutingRequest,
    envelope: GeoXReadoutResultEnvelope,
    *,
    primary_route: GeoXReadoutTrustRoute,
    status: GeoXReadoutTrustRoutingStatus,
    trust_route: GeoXReadoutTrustRouteTarget,
    decision_route: GeoXReadoutTrustRouteTarget,
    recommendation_route: GeoXReadoutTrustRouteTarget,
    recommendation_readiness: GeoXReadoutRecommendationReadiness,
    claim_status: str,
    routing_summary: str,
    issues: list[GeoXReadoutTrustRoutingIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXReadoutTrustRoutingEnvelope:
    return GeoXReadoutTrustRoutingEnvelope(
        routing_id=f"geox-trust-routing:{envelope.experiment_id}:{request.request_id}",
        experiment_id=envelope.experiment_id,
        source_result_id=envelope.result_id,
        source_package_readiness_status=envelope.package_readiness_status,
        primary_route=primary_route,
        trust_report_route=trust_route,
        decision_surface_route=decision_route,
        recommendation_contract_route=recommendation_route,
        recommendation_readiness=recommendation_readiness,
        claim_authorization_owner=envelope.claim_authorization_owner,
        claim_authorization_status=claim_status,
        package_output_summary=dict(envelope.package_output_summary),
        routing_summary=routing_summary,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={
            **lineage,
            **envelope.lineage,
            "source_result_status": str(envelope.status),
            "routing_status": str(status),
        },
    )


def _blocked(
    request_id: str,
    status: GeoXReadoutTrustRoutingStatus,
    issues: list[GeoXReadoutTrustRoutingIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXReadoutTrustRoutingResult:
    return GeoXReadoutTrustRoutingResult(
        request_id=request_id,
        status=status,
        routing_envelope=None,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[GeoXReadoutTrustRoutingIssueCode],
) -> list[GeoXReadoutTrustRoutingIssueCode]:
    seen: set[GeoXReadoutTrustRoutingIssueCode] = set()
    ordered: list[GeoXReadoutTrustRoutingIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
