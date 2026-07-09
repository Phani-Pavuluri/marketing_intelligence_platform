"""Tests for GeoX readout trust-routing contracts."""

from __future__ import annotations

from mip.contracts import (
    CLAIM_AUTHORIZATION_OWNER,
    DECISION_SURFACE_CONTRACT_NAME,
    RECOMMENDATION_CONTRACT_NAME,
    TRUST_REPORT_CONTRACT_NAME,
    GeoXReadoutRecommendationReadiness,
    GeoXReadoutResultExplanation,
    GeoXReadoutTrustRoute,
    GeoXReadoutTrustRouteTarget,
    GeoXReadoutTrustRoutingEnvelope,
    GeoXReadoutTrustRoutingRequest,
    GeoXReadoutTrustRoutingResult,
    GeoXReadoutTrustRoutingStatus,
)

_REQUIRED_STATUSES = {
    GeoXReadoutTrustRoutingStatus.ROUTED_TO_TRUST_REPORT_REVIEW,
    GeoXReadoutTrustRoutingStatus.ROUTED_TO_DECISION_SURFACE_REVIEW,
    GeoXReadoutTrustRoutingStatus.ROUTED_TO_RECOMMENDATION_CONTRACT_BLOCKED,
    GeoXReadoutTrustRoutingStatus.ROUTED_TO_DIAGNOSTIC_ONLY_REVIEW,
    GeoXReadoutTrustRoutingStatus.BLOCKED_MISSING_RESULT_ENVELOPE,
    GeoXReadoutTrustRoutingStatus.BLOCKED_RESULT_NOT_READY,
    GeoXReadoutTrustRoutingStatus.BLOCKED_RESULT_DIAGNOSTIC_ONLY,
    GeoXReadoutTrustRoutingStatus.BLOCKED_RESULT_MALFORMED,
    GeoXReadoutTrustRoutingStatus.BLOCKED_CLAIM_AUTHORIZATION_NOT_EVALUATED,
}

_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi", "roas")


def _explanation() -> GeoXReadoutResultExplanation:
    return GeoXReadoutResultExplanation(
        summary="summary",
        readiness_explanation="ready",
        blocker_explanation="none",
        warning_explanation="none",
        claim_boundary_explanation="delegated",
        next_action="review",
        business_safe_summary="safe",
    )


def test_required_enums_exist() -> None:
    assert _REQUIRED_STATUSES.issubset(set(GeoXReadoutTrustRoutingStatus))
    assert GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW in GeoXReadoutTrustRoute
    assert GeoXReadoutRecommendationReadiness.NOT_AUTHORIZED in (
        GeoXReadoutRecommendationReadiness
    )


def test_models_serialize() -> None:
    request = GeoXReadoutTrustRoutingRequest(request_id="req-1")
    assert request.requested_route == GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW
    result = GeoXReadoutTrustRoutingResult(
        request_id="req-1",
        status=GeoXReadoutTrustRoutingStatus.BLOCKED_MISSING_RESULT_ENVELOPE,
    )
    assert result.routing_envelope is None


def test_envelope_no_top_level_metric_fields() -> None:
    schema = GeoXReadoutTrustRoutingEnvelope.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_package_computed_spend_delta_allowed_in_summary_only() -> None:
    envelope = GeoXReadoutTrustRoutingEnvelope(
        routing_id="route-1",
        experiment_id="exp-1",
        source_result_id="result-1",
        source_package_readiness_status="READY",
        primary_route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
        trust_report_route=_route_target(TRUST_REPORT_CONTRACT_NAME),
        decision_surface_route=_route_target(DECISION_SURFACE_CONTRACT_NAME),
        recommendation_contract_route=_route_target(RECOMMENDATION_CONTRACT_NAME),
        recommendation_readiness=GeoXReadoutRecommendationReadiness.BLOCKED_PENDING_TRUST_REPORT,
        package_output_summary={"package_computed_spend_delta": 749.0},
        routing_summary="ready for TrustReport review",
    )
    assert envelope.package_output_summary["package_computed_spend_delta"] == 749.0
    assert "spend_delta" not in envelope.model_dump()


def test_recommendation_readiness_defaults_blocked() -> None:
    request = GeoXReadoutTrustRoutingRequest(request_id="req-1")
    assert request.result_envelope is None
    readiness_values = set(GeoXReadoutRecommendationReadiness)
    assert GeoXReadoutRecommendationReadiness.NOT_AUTHORIZED in readiness_values
    assert GeoXReadoutRecommendationReadiness.BLOCKED_PENDING_TRUST_REPORT in readiness_values


def test_contracts_exported_from_mip_contracts() -> None:
    from mip import contracts

    assert hasattr(contracts, "GeoXReadoutTrustRoutingRequest")
    assert hasattr(contracts, "GeoXReadoutTrustRoutingEnvelope")
    assert hasattr(contracts, "GeoXReadoutTrustRoutingStatus")


def _route_target(contract_name: str) -> GeoXReadoutTrustRouteTarget:
    return GeoXReadoutTrustRouteTarget(
        route=GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
        target_contract_name=contract_name,
        ready_for_boundary=False,
        required_next_action="review",
    )


def test_route_target_contract_names() -> None:
    assert TRUST_REPORT_CONTRACT_NAME == "TrustReport"
    assert DECISION_SURFACE_CONTRACT_NAME == "DecisionSurface"
    assert RECOMMENDATION_CONTRACT_NAME == "RecommendationContract"


def test_claim_owner_default_delegated_runtime() -> None:
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
        claim_authorization_status="DELEGATED",
        routing_summary="summary",
    )
    assert envelope.claim_authorization_owner == CLAIM_AUTHORIZATION_OWNER
