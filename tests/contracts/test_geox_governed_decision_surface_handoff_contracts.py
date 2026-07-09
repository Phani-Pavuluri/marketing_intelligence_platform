"""Tests for GeoX governed DecisionSurface handoff contracts."""

from __future__ import annotations

from mip.contracts import (
    CLAIM_AUTHORIZATION_OWNER,
    DECISION_SURFACE_CONTRACT_NAME,
    RECOMMENDATION_CONTRACT_NAME,
    RECOMMENDED_NEXT_RECOMMENDATION_BLOCKER_ARTIFACT,
    TRUST_REPORT_CONTRACT_NAME,
    GeoXDecisionSurfaceEvidenceReference,
    GeoXDecisionSurfaceHandoffIssueCode,
    GeoXDecisionSurfaceHandoffStatus,
    GeoXDecisionSurfaceHandoffTarget,
    GeoXDecisionSurfaceReviewReadiness,
    GeoXGovernedDecisionSurfaceHandoff,
    GeoXGovernedDecisionSurfaceHandoffRequest,
    GeoXGovernedDecisionSurfaceHandoffResult,
)
from mip.contracts.geox_readout_trust_routing import (
    GeoXReadoutRecommendationReadiness,
    GeoXReadoutTrustRoute,
    GeoXReadoutTrustRouteTarget,
    GeoXReadoutTrustRoutingEnvelope,
)

_REQUIRED_STATUSES = {
    GeoXDecisionSurfaceHandoffStatus.READY_FOR_DECISION_SURFACE_REVIEW,
    GeoXDecisionSurfaceHandoffStatus.PENDING_TRUST_REPORT_REVIEW,
    GeoXDecisionSurfaceHandoffStatus.BLOCKED_MISSING_TRUST_ROUTING_ENVELOPE,
    GeoXDecisionSurfaceHandoffStatus.BLOCKED_TRUST_ROUTING_MALFORMED,
    GeoXDecisionSurfaceHandoffStatus.BLOCKED_TRUST_REPORT_NOT_COMPLETE,
    GeoXDecisionSurfaceHandoffStatus.BLOCKED_PACKAGE_RESULT_NOT_READY,
    GeoXDecisionSurfaceHandoffStatus.BLOCKED_DIAGNOSTIC_ONLY,
    GeoXDecisionSurfaceHandoffStatus.BLOCKED_RECOMMENDATION_CONTRACT,
    GeoXDecisionSurfaceHandoffStatus.BLOCKED_CLAIM_AUTHORIZATION_NOT_EVALUATED,
}

_REQUIRED_ISSUES = {
    GeoXDecisionSurfaceHandoffIssueCode.MISSING_TRUST_ROUTING_ENVELOPE,
    GeoXDecisionSurfaceHandoffIssueCode.TRUST_ROUTING_ENVELOPE_MALFORMED,
    GeoXDecisionSurfaceHandoffIssueCode.TRUST_REPORT_REQUIRED,
    GeoXDecisionSurfaceHandoffIssueCode.TRUST_REPORT_NOT_COMPLETE,
    GeoXDecisionSurfaceHandoffIssueCode.PACKAGE_RESULT_NOT_READY,
    GeoXDecisionSurfaceHandoffIssueCode.PACKAGE_RESULT_DIAGNOSTIC_ONLY,
    GeoXDecisionSurfaceHandoffIssueCode.PACKAGE_WARNINGS_PRESENT,
    GeoXDecisionSurfaceHandoffIssueCode.CLAIM_AUTHORIZATION_DELEGATED,
    GeoXDecisionSurfaceHandoffIssueCode.CLAIM_AUTHORIZATION_NOT_EVALUATED,
    GeoXDecisionSurfaceHandoffIssueCode.DECISION_SURFACE_REVIEW_REQUIRED,
    GeoXDecisionSurfaceHandoffIssueCode.RECOMMENDATION_CONTRACT_BLOCKED,
    GeoXDecisionSurfaceHandoffIssueCode.RECOMMENDATION_REQUIRES_GOVERNED_DECISION_SURFACE,
    GeoXDecisionSurfaceHandoffIssueCode.ROI_ROAS_NOT_COMPUTED_IN_MIP,
    GeoXDecisionSurfaceHandoffIssueCode.LIFT_NOT_COMPUTED_IN_MIP,
    GeoXDecisionSurfaceHandoffIssueCode.SPEND_DELTA_PACKAGE_COMPUTED,
    GeoXDecisionSurfaceHandoffIssueCode.NO_BUSINESS_RECOMMENDATION_AUTHORIZED,
}

_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi", "roas")


def _route_target(contract_name: str) -> GeoXReadoutTrustRouteTarget:
    return GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
        target_contract_name=contract_name,
        ready_for_boundary=True,
        required_next_action="review",
    )


def test_required_enums_exist() -> None:
    assert _REQUIRED_STATUSES.issubset(set(GeoXDecisionSurfaceHandoffStatus))
    assert _REQUIRED_ISSUES.issubset(set(GeoXDecisionSurfaceHandoffIssueCode))
    assert GeoXDecisionSurfaceReviewReadiness.READY in GeoXDecisionSurfaceReviewReadiness
    assert GeoXDecisionSurfaceHandoffTarget.DECISION_SURFACE_REVIEW in (
        GeoXDecisionSurfaceHandoffTarget
    )


def test_models_serialize() -> None:
    request = GeoXGovernedDecisionSurfaceHandoffRequest(request_id="req-1")
    assert request.trust_report_review_complete is False
    assert request.requested_target == GeoXDecisionSurfaceHandoffTarget.DECISION_SURFACE_REVIEW
    result = GeoXGovernedDecisionSurfaceHandoffResult(
        request_id="req-1",
        status=GeoXDecisionSurfaceHandoffStatus.BLOCKED_MISSING_TRUST_ROUTING_ENVELOPE,
    )
    assert result.handoff is None


def test_handoff_no_top_level_metric_fields() -> None:
    schema = GeoXGovernedDecisionSurfaceHandoff.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_evidence_reference_package_output_summary_only() -> None:
    evidence = GeoXDecisionSurfaceEvidenceReference(
        source_result_id="result-1",
        source_routing_id="route-1",
        experiment_id="exp-1",
        package_readiness_status="READY",
        package_output_summary={"package_computed_spend_delta": 1200.0},
    )
    assert evidence.package_output_summary["package_computed_spend_delta"] == 1200.0
    schema = GeoXDecisionSurfaceEvidenceReference.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_recommendation_authorized_defaults_false() -> None:
    handoff = GeoXGovernedDecisionSurfaceHandoff(
        handoff_id="handoff-1",
        experiment_id="exp-1",
        source_routing_id="route-1",
        target=GeoXDecisionSurfaceHandoffTarget.DECISION_SURFACE_REVIEW,
        review_readiness=GeoXDecisionSurfaceReviewReadiness.READY,
        evidence_reference=GeoXDecisionSurfaceEvidenceReference(
            source_result_id="result-1",
            source_routing_id="route-1",
            experiment_id="exp-1",
            package_readiness_status="READY",
        ),
        handoff_summary="ready for review",
        required_next_action="review",
    )
    assert handoff.recommendation_authorized is False


def test_contract_names_are_metadata_only() -> None:
    handoff = GeoXGovernedDecisionSurfaceHandoff(
        handoff_id="handoff-1",
        experiment_id="exp-1",
        source_routing_id="route-1",
        target=GeoXDecisionSurfaceHandoffTarget.DECISION_SURFACE_REVIEW,
        review_readiness=GeoXDecisionSurfaceReviewReadiness.READY,
        evidence_reference=GeoXDecisionSurfaceEvidenceReference(
            source_result_id="result-1",
            source_routing_id="route-1",
            experiment_id="exp-1",
            package_readiness_status="READY",
        ),
        handoff_summary="ready for review",
        required_next_action="review",
    )
    assert handoff.decision_surface_contract_name == DECISION_SURFACE_CONTRACT_NAME
    assert handoff.trust_report_contract_name == TRUST_REPORT_CONTRACT_NAME
    assert handoff.recommendation_contract_name == RECOMMENDATION_CONTRACT_NAME
    assert handoff.claim_authorization_owner == CLAIM_AUTHORIZATION_OWNER


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_RECOMMENDATION_BLOCKER_ARTIFACT == (
        "MIP_GEOX_READOUT_RECOMMENDATION_CONTRACT_BLOCKER_001"
    )


def test_routing_envelope_compatibility_schema() -> None:
    envelope = GeoXReadoutTrustRoutingEnvelope(
        routing_id="route-1",
        experiment_id="exp-1",
        source_result_id="result-1",
        source_package_readiness_status="READY",
        primary_route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
        trust_report_route=_route_target(TRUST_REPORT_CONTRACT_NAME),
        decision_surface_route=_route_target(DECISION_SURFACE_CONTRACT_NAME),
        recommendation_contract_route=_route_target(RECOMMENDATION_CONTRACT_NAME),
        recommendation_readiness=GeoXReadoutRecommendationReadiness.NOT_AUTHORIZED,
        routing_summary="summary",
    )
    request = GeoXGovernedDecisionSurfaceHandoffRequest(
        request_id="req-1",
        trust_routing_envelope=envelope,
    )
    assert request.trust_routing_envelope is not None
