"""GeoX governed DecisionSurface handoff workflow.

Prepares evidence for governed DecisionSurface review from trust-routing metadata only.
No DecisionSurface execution, metric recomputation, or claim authorization.
"""

from __future__ import annotations

from mip.contracts.geox_governed_decision_surface_handoff import (
    GeoXDecisionSurfaceEvidenceReference,
    GeoXDecisionSurfaceHandoffIssueCode,
    GeoXDecisionSurfaceHandoffStatus,
    GeoXDecisionSurfaceHandoffTarget,
    GeoXDecisionSurfaceReviewReadiness,
    GeoXGovernedDecisionSurfaceHandoff,
    GeoXGovernedDecisionSurfaceHandoffRequest,
    GeoXGovernedDecisionSurfaceHandoffResult,
)
from mip.contracts.geox_panel_exp_runtime_call import CLAIM_AUTHORIZATION_OWNER
from mip.contracts.geox_readout_trust_routing import (
    GeoXReadoutTrustRoute,
    GeoXReadoutTrustRoutingEnvelope,
)


def build_geox_governed_decision_surface_handoff(
    request: GeoXGovernedDecisionSurfaceHandoffRequest,
) -> GeoXGovernedDecisionSurfaceHandoffResult:
    """Build a governed DecisionSurface handoff from a trust-routing envelope."""
    lineage = {
        **request.lineage,
        "handoff_stage": "governed_decision_surface_handoff",
        "requested_target": str(request.requested_target),
        "trust_report_review_complete": str(request.trust_report_review_complete).lower(),
    }
    warnings = list(dict.fromkeys(request.warnings))
    issues: list[GeoXDecisionSurfaceHandoffIssueCode] = [
        GeoXDecisionSurfaceHandoffIssueCode.ROI_ROAS_NOT_COMPUTED_IN_MIP,
        GeoXDecisionSurfaceHandoffIssueCode.LIFT_NOT_COMPUTED_IN_MIP,
        GeoXDecisionSurfaceHandoffIssueCode.CLAIM_AUTHORIZATION_DELEGATED,
        GeoXDecisionSurfaceHandoffIssueCode.NO_BUSINESS_RECOMMENDATION_AUTHORIZED,
        GeoXDecisionSurfaceHandoffIssueCode.DECISION_SURFACE_REVIEW_REQUIRED,
        GeoXDecisionSurfaceHandoffIssueCode.RECOMMENDATION_CONTRACT_BLOCKED,
    ]

    if request.trust_routing_envelope is None:
        return _blocked(
            request.request_id,
            GeoXDecisionSurfaceHandoffStatus.BLOCKED_MISSING_TRUST_ROUTING_ENVELOPE,
            issues + [GeoXDecisionSurfaceHandoffIssueCode.MISSING_TRUST_ROUTING_ENVELOPE],
            warnings,
            lineage,
        )

    routing = request.trust_routing_envelope
    validation_error = _validate_trust_routing_envelope(routing)
    if validation_error is not None:
        return _blocked(
            request.request_id,
            GeoXDecisionSurfaceHandoffStatus.BLOCKED_TRUST_ROUTING_MALFORMED,
            issues + [GeoXDecisionSurfaceHandoffIssueCode.TRUST_ROUTING_ENVELOPE_MALFORMED],
            warnings + [validation_error],
            lineage,
        )

    claim_status, claim_issues, claim_block = _resolve_claim_boundary(routing)
    issues.extend(claim_issues)
    if claim_block is not None:
        return _blocked(
            request.request_id,
            claim_block,
            issues,
            warnings,
            lineage,
        )

    package_warnings = list(dict.fromkeys(routing.warnings))
    if package_warnings:
        issues.append(GeoXDecisionSurfaceHandoffIssueCode.PACKAGE_WARNINGS_PRESENT)
        warnings.extend(package_warnings)

    if "package_computed_spend_delta" in routing.package_output_summary:
        issues.append(GeoXDecisionSurfaceHandoffIssueCode.SPEND_DELTA_PACKAGE_COMPUTED)

    if request.requested_target == GeoXDecisionSurfaceHandoffTarget.RECOMMENDATION_CONTRACT_BLOCKED:
        return _build_recommendation_blocked(
            request, routing, claim_status, issues, warnings, lineage
        )

    if _is_diagnostic_only(routing):
        issues.append(GeoXDecisionSurfaceHandoffIssueCode.PACKAGE_RESULT_DIAGNOSTIC_ONLY)
        return _build_diagnostic_blocked(
            request, routing, claim_status, issues, warnings, lineage
        )

    if _is_package_not_ready(routing):
        issues.append(GeoXDecisionSurfaceHandoffIssueCode.PACKAGE_RESULT_NOT_READY)
        return _build_package_not_ready(
            request, routing, claim_status, issues, warnings, lineage
        )

    trust_complete = _trust_report_complete(request, routing)
    if not trust_complete:
        issues.append(GeoXDecisionSurfaceHandoffIssueCode.TRUST_REPORT_NOT_COMPLETE)
        issues.append(GeoXDecisionSurfaceHandoffIssueCode.TRUST_REPORT_REQUIRED)
        return _build_pending_trust_report(
            request, routing, claim_status, issues, warnings, lineage
        )

    return _build_ready_for_decision_surface(
        request, routing, claim_status, issues, warnings, lineage
    )


def build_governed_decision_surface_handoff_summary(
    *,
    review_readiness: GeoXDecisionSurfaceReviewReadiness,
    trust_report_review_complete: bool,
    package_readiness: str,
) -> str:
    """Produce a safe handoff summary without business recommendations."""
    if review_readiness == GeoXDecisionSurfaceReviewReadiness.READY:
        return (
            "GeoX readout evidence is ready for governed DecisionSurface review "
            "after TrustReport review completion."
        )
    if review_readiness == GeoXDecisionSurfaceReviewReadiness.PENDING_TRUST_REPORT:
        return (
            "DecisionSurface review is pending because TrustReport review has not "
            "completed."
        )
    if review_readiness == GeoXDecisionSurfaceReviewReadiness.BLOCKED_DIAGNOSTIC_ONLY:
        return (
            f"Package result ({package_readiness}) is diagnostic-only and cannot "
            "support governed DecisionSurface review."
        )
    if review_readiness == GeoXDecisionSurfaceReviewReadiness.BLOCKED_RESULT_NOT_READY:
        return (
            f"Package result ({package_readiness}) is not ready for DecisionSurface "
            "handoff."
        )
    return "Governed DecisionSurface handoff recorded; governance review required."


def _validate_trust_routing_envelope(routing: GeoXReadoutTrustRoutingEnvelope) -> str | None:
    if not routing.routing_id.strip():
        return "trust routing envelope missing routing_id"
    if not routing.experiment_id.strip():
        return "trust routing envelope missing experiment_id"
    if not routing.source_result_id.strip():
        return "trust routing envelope missing source_result_id"
    if not routing.source_package_readiness_status.strip():
        return "trust routing envelope missing source_package_readiness_status"
    if not routing.claim_authorization_owner.strip():
        return "trust routing envelope missing claim_authorization_owner"
    return None


def _resolve_claim_boundary(
    routing: GeoXReadoutTrustRoutingEnvelope,
) -> tuple[str, list[GeoXDecisionSurfaceHandoffIssueCode], GeoXDecisionSurfaceHandoffStatus | None]:
    issues: list[GeoXDecisionSurfaceHandoffIssueCode] = []
    owner = routing.claim_authorization_owner
    status = routing.claim_authorization_status

    if owner == CLAIM_AUTHORIZATION_OWNER:
        claim_status = status if status else "DELEGATED"
        if claim_status == "NOT_EVALUATED":
            issues.append(GeoXDecisionSurfaceHandoffIssueCode.CLAIM_AUTHORIZATION_NOT_EVALUATED)
        return claim_status, issues, None

    if status == "NOT_EVALUATED" or not owner.strip():
        issues.append(GeoXDecisionSurfaceHandoffIssueCode.CLAIM_AUTHORIZATION_NOT_EVALUATED)
        return "NOT_EVALUATED", issues, (
            GeoXDecisionSurfaceHandoffStatus.BLOCKED_CLAIM_AUTHORIZATION_NOT_EVALUATED
        )
    return "NOT_AUTHORIZED", issues, None


def _trust_report_complete(
    request: GeoXGovernedDecisionSurfaceHandoffRequest,
    routing: GeoXReadoutTrustRoutingEnvelope,
) -> bool:
    if request.trust_report_review_complete:
        return True
    if routing.lineage.get("trust_report_review_complete") == "true":
        return True
    return routing.decision_surface_route.ready_for_boundary


def _is_package_not_ready(routing: GeoXReadoutTrustRoutingEnvelope) -> bool:
    if routing.primary_route == GeoXReadoutTrustRoute.NO_ROUTE_BLOCKED:
        return True
    status = routing.source_package_readiness_status.strip().upper()
    return status.startswith("BLOCKED_")


def _is_diagnostic_only(routing: GeoXReadoutTrustRoutingEnvelope) -> bool:
    if routing.primary_route == GeoXReadoutTrustRoute.DIAGNOSTIC_ONLY_REVIEW:
        return True
    status = routing.source_package_readiness_status.strip().upper()
    return status in {"PARTIAL_DIAGNOSTIC_ONLY"}


def _evidence_reference(
    routing: GeoXReadoutTrustRoutingEnvelope,
) -> GeoXDecisionSurfaceEvidenceReference:
    return GeoXDecisionSurfaceEvidenceReference(
        source_result_id=routing.source_result_id,
        source_routing_id=routing.routing_id,
        experiment_id=routing.experiment_id,
        package_readiness_status=routing.source_package_readiness_status,
        claim_authorization_owner=routing.claim_authorization_owner,
        package_output_summary=dict(routing.package_output_summary),
        package_warnings=list(routing.warnings),
        source_lineage=dict(routing.lineage),
    )


def _build_ready_for_decision_surface(
    request: GeoXGovernedDecisionSurfaceHandoffRequest,
    routing: GeoXReadoutTrustRoutingEnvelope,
    claim_status: str,
    issues: list[GeoXDecisionSurfaceHandoffIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXGovernedDecisionSurfaceHandoffResult:
    summary = build_governed_decision_surface_handoff_summary(
        review_readiness=GeoXDecisionSurfaceReviewReadiness.READY,
        trust_report_review_complete=True,
        package_readiness=routing.source_package_readiness_status,
    )
    handoff = GeoXGovernedDecisionSurfaceHandoff(
        handoff_id=f"geox-ds-handoff:{routing.experiment_id}:{request.request_id}",
        experiment_id=routing.experiment_id,
        source_routing_id=routing.routing_id,
        target=GeoXDecisionSurfaceHandoffTarget.DECISION_SURFACE_REVIEW,
        review_readiness=GeoXDecisionSurfaceReviewReadiness.READY,
        trust_report_review_complete=True,
        evidence_reference=_evidence_reference(routing),
        handoff_summary=summary,
        required_next_action=(
            "Pass this handoff to governed DecisionSurface review. "
            "This is not an approved decision or recommendation."
        ),
        claim_authorization_owner=routing.claim_authorization_owner,
        claim_authorization_status=claim_status,
        recommendation_authorized=False,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={**lineage, **routing.lineage, "trust_report_review_complete": "true"},
    )
    return GeoXGovernedDecisionSurfaceHandoffResult(
        request_id=request.request_id,
        status=GeoXDecisionSurfaceHandoffStatus.READY_FOR_DECISION_SURFACE_REVIEW,
        handoff=handoff,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _build_pending_trust_report(
    request: GeoXGovernedDecisionSurfaceHandoffRequest,
    routing: GeoXReadoutTrustRoutingEnvelope,
    claim_status: str,
    issues: list[GeoXDecisionSurfaceHandoffIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXGovernedDecisionSurfaceHandoffResult:
    summary = build_governed_decision_surface_handoff_summary(
        review_readiness=GeoXDecisionSurfaceReviewReadiness.PENDING_TRUST_REPORT,
        trust_report_review_complete=False,
        package_readiness=routing.source_package_readiness_status,
    )
    handoff = GeoXGovernedDecisionSurfaceHandoff(
        handoff_id=f"geox-ds-handoff:{routing.experiment_id}:{request.request_id}",
        experiment_id=routing.experiment_id,
        source_routing_id=routing.routing_id,
        target=GeoXDecisionSurfaceHandoffTarget.TRUST_REPORT_REVIEW,
        review_readiness=GeoXDecisionSurfaceReviewReadiness.PENDING_TRUST_REPORT,
        trust_report_review_complete=False,
        evidence_reference=_evidence_reference(routing),
        handoff_summary=summary,
        required_next_action="Complete TrustReport review before DecisionSurface review.",
        claim_authorization_owner=routing.claim_authorization_owner,
        claim_authorization_status=claim_status,
        recommendation_authorized=False,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={**lineage, **routing.lineage},
    )
    return GeoXGovernedDecisionSurfaceHandoffResult(
        request_id=request.request_id,
        status=GeoXDecisionSurfaceHandoffStatus.PENDING_TRUST_REPORT_REVIEW,
        handoff=handoff,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _build_package_not_ready(
    request: GeoXGovernedDecisionSurfaceHandoffRequest,
    routing: GeoXReadoutTrustRoutingEnvelope,
    claim_status: str,
    issues: list[GeoXDecisionSurfaceHandoffIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXGovernedDecisionSurfaceHandoffResult:
    summary = build_governed_decision_surface_handoff_summary(
        review_readiness=GeoXDecisionSurfaceReviewReadiness.BLOCKED_RESULT_NOT_READY,
        trust_report_review_complete=False,
        package_readiness=routing.source_package_readiness_status,
    )
    handoff = GeoXGovernedDecisionSurfaceHandoff(
        handoff_id=f"geox-ds-handoff:{routing.experiment_id}:{request.request_id}",
        experiment_id=routing.experiment_id,
        source_routing_id=routing.routing_id,
        target=GeoXDecisionSurfaceHandoffTarget.NO_HANDOFF,
        review_readiness=GeoXDecisionSurfaceReviewReadiness.BLOCKED_RESULT_NOT_READY,
        evidence_reference=_evidence_reference(routing),
        handoff_summary=summary,
        required_next_action="Resolve package blockers before governance handoff.",
        claim_authorization_owner=routing.claim_authorization_owner,
        claim_authorization_status=claim_status,
        recommendation_authorized=False,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={**lineage, **routing.lineage},
    )
    return GeoXGovernedDecisionSurfaceHandoffResult(
        request_id=request.request_id,
        status=GeoXDecisionSurfaceHandoffStatus.BLOCKED_PACKAGE_RESULT_NOT_READY,
        handoff=handoff,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _build_diagnostic_blocked(
    request: GeoXGovernedDecisionSurfaceHandoffRequest,
    routing: GeoXReadoutTrustRoutingEnvelope,
    claim_status: str,
    issues: list[GeoXDecisionSurfaceHandoffIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXGovernedDecisionSurfaceHandoffResult:
    summary = build_governed_decision_surface_handoff_summary(
        review_readiness=GeoXDecisionSurfaceReviewReadiness.BLOCKED_DIAGNOSTIC_ONLY,
        trust_report_review_complete=False,
        package_readiness=routing.source_package_readiness_status,
    )
    handoff = GeoXGovernedDecisionSurfaceHandoff(
        handoff_id=f"geox-ds-handoff:{routing.experiment_id}:{request.request_id}",
        experiment_id=routing.experiment_id,
        source_routing_id=routing.routing_id,
        target=GeoXDecisionSurfaceHandoffTarget.TRUST_REPORT_REVIEW,
        review_readiness=GeoXDecisionSurfaceReviewReadiness.BLOCKED_DIAGNOSTIC_ONLY,
        evidence_reference=_evidence_reference(routing),
        handoff_summary=summary,
        required_next_action=(
            "Diagnostic-only package output cannot support production DecisionSurface review."
        ),
        claim_authorization_owner=routing.claim_authorization_owner,
        claim_authorization_status=claim_status,
        recommendation_authorized=False,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={**lineage, **routing.lineage},
    )
    return GeoXGovernedDecisionSurfaceHandoffResult(
        request_id=request.request_id,
        status=GeoXDecisionSurfaceHandoffStatus.BLOCKED_DIAGNOSTIC_ONLY,
        handoff=handoff,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _build_recommendation_blocked(
    request: GeoXGovernedDecisionSurfaceHandoffRequest,
    routing: GeoXReadoutTrustRoutingEnvelope,
    claim_status: str,
    issues: list[GeoXDecisionSurfaceHandoffIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXGovernedDecisionSurfaceHandoffResult:
    issues.append(
        GeoXDecisionSurfaceHandoffIssueCode.RECOMMENDATION_REQUIRES_GOVERNED_DECISION_SURFACE
    )
    handoff = GeoXGovernedDecisionSurfaceHandoff(
        handoff_id=f"geox-ds-handoff:{routing.experiment_id}:{request.request_id}",
        experiment_id=routing.experiment_id,
        source_routing_id=routing.routing_id,
        target=GeoXDecisionSurfaceHandoffTarget.RECOMMENDATION_CONTRACT_BLOCKED,
        review_readiness=GeoXDecisionSurfaceReviewReadiness.NOT_AUTHORIZED,
        evidence_reference=_evidence_reference(routing),
        handoff_summary=(
            "RecommendationContract requires governed DecisionSurface output, "
            "not just a handoff envelope."
        ),
        required_next_action=(
            "Complete governed DecisionSurface review before RecommendationContract assembly."
        ),
        claim_authorization_owner=routing.claim_authorization_owner,
        claim_authorization_status=claim_status,
        recommendation_authorized=False,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage={**lineage, **routing.lineage},
    )
    return GeoXGovernedDecisionSurfaceHandoffResult(
        request_id=request.request_id,
        status=GeoXDecisionSurfaceHandoffStatus.BLOCKED_RECOMMENDATION_CONTRACT,
        handoff=handoff,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _blocked(
    request_id: str,
    status: GeoXDecisionSurfaceHandoffStatus,
    issues: list[GeoXDecisionSurfaceHandoffIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
) -> GeoXGovernedDecisionSurfaceHandoffResult:
    return GeoXGovernedDecisionSurfaceHandoffResult(
        request_id=request_id,
        status=status,
        handoff=None,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
        lineage=lineage,
    )


def _dedupe_issues(
    issues: list[GeoXDecisionSurfaceHandoffIssueCode],
) -> list[GeoXDecisionSurfaceHandoffIssueCode]:
    seen: set[GeoXDecisionSurfaceHandoffIssueCode] = set()
    ordered: list[GeoXDecisionSurfaceHandoffIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
