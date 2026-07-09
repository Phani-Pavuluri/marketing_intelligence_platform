"""Tests for GeoX readout trust-routing workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.geox_panel_exp_runtime_call import (
    CLAIM_AUTHORIZATION_OWNER,
    GeoXPostTestSpendEvidenceArtifact,
    GeoXTrustedReadoutSpendHandoffArtifact,
)
from mip.contracts.geox_readout_result_ingestion import (
    GeoXReadoutClaimReadiness,
    GeoXReadoutResultEnvelope,
    GeoXReadoutResultExplanation,
    GeoXReadoutResultIngestionRequest,
    GeoXReadoutResultStatus,
)
from mip.contracts.geox_readout_trust_routing import (
    DECISION_SURFACE_CONTRACT_NAME,
    RECOMMENDATION_CONTRACT_NAME,
    TRUST_REPORT_CONTRACT_NAME,
    GeoXReadoutRecommendationReadiness,
    GeoXReadoutTrustRoute,
    GeoXReadoutTrustRoutingIssueCode,
    GeoXReadoutTrustRoutingRequest,
    GeoXReadoutTrustRoutingStatus,
)
from mip.workflows.geox_readout_result_ingestion import (
    ingest_geox_readout_result_for_explanation,
)
from mip.workflows.geox_readout_trust_routing import (
    route_geox_readout_result_to_trust_boundaries,
)

_ROUTING_SOURCE = Path("src/mip/workflows/geox_readout_trust_routing.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/geox_readout_trust_routing.py")
_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi_value", "roas_value")


def _explanation(*, summary: str = "Package readiness explained.") -> GeoXReadoutResultExplanation:
    return GeoXReadoutResultExplanation(
        summary=summary,
        readiness_explanation="readiness",
        blocker_explanation="blockers",
        warning_explanation="warnings",
        claim_boundary_explanation="delegated",
        next_action="next",
        business_safe_summary="safe summary",
    )


def _result_envelope(
    *,
    status: GeoXReadoutResultStatus = GeoXReadoutResultStatus.EXPLAINED_READY_PACKAGE_RESULT,
    package_readiness_status: str = "READY",
    blocking_reasons: list[str] | None = None,
    warnings: list[str] | None = None,
    package_output_summary: dict[str, str | float | int | bool | None] | None = None,
    claim_owner: str = CLAIM_AUTHORIZATION_OWNER,
    lineage: dict[str, str] | None = None,
) -> GeoXReadoutResultEnvelope:
    return GeoXReadoutResultEnvelope(
        result_id="geox-readout-result:exp-1:ingest-1",
        experiment_id="exp-1",
        status=status,
        package_readiness_status=package_readiness_status,
        package_blocking_reasons=blocking_reasons or [],
        package_warnings=warnings or [],
        package_output_summary=package_output_summary
        or {"readiness_status": package_readiness_status},
        trusted_handoff_summary={"roi_claim_authorization_status": "NOT_EVALUATED"},
        claim_readiness=GeoXReadoutClaimReadiness.READY_FOR_TRUST_REPORT_REVIEW,
        claim_authorization_owner=claim_owner,
        explanation=_explanation(),
        lineage=lineage or {},
    )


def _route_request(
    envelope: GeoXReadoutResultEnvelope | None,
    *,
    requested_route: GeoXReadoutTrustRoute = GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
    lineage: dict[str, str] | None = None,
) -> GeoXReadoutTrustRoutingRequest:
    return GeoXReadoutTrustRoutingRequest(
        request_id="route-1",
        result_envelope=envelope,
        requested_route=requested_route,
        lineage=lineage or {},
    )


def test_missing_result_envelope_blocked() -> None:
    result = route_geox_readout_result_to_trust_boundaries(_route_request(None))
    assert result.status == GeoXReadoutTrustRoutingStatus.BLOCKED_MISSING_RESULT_ENVELOPE
    assert GeoXReadoutTrustRoutingIssueCode.MISSING_RESULT_ENVELOPE in result.issues
    assert result.routing_envelope is None


def test_malformed_result_envelope_blocked() -> None:
    envelope = _result_envelope()
    envelope = envelope.model_copy(update={"experiment_id": ""})
    result = route_geox_readout_result_to_trust_boundaries(_route_request(envelope))
    assert result.status == GeoXReadoutTrustRoutingStatus.BLOCKED_RESULT_MALFORMED
    assert result.routing_envelope is None


def test_ready_package_result_routes_to_trust_report() -> None:
    result = route_geox_readout_result_to_trust_boundaries(
        _route_request(_result_envelope())
    )
    assert result.status == GeoXReadoutTrustRoutingStatus.ROUTED_TO_TRUST_REPORT_REVIEW
    routing = result.routing_envelope
    assert routing is not None
    assert routing.primary_route == GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW
    assert routing.trust_report_route.ready_for_boundary is True
    assert routing.trust_report_route.target_contract_name == TRUST_REPORT_CONTRACT_NAME
    assert routing.decision_surface_route.ready_for_boundary is False
    assert routing.recommendation_contract_route.ready_for_boundary is False
    assert routing.recommendation_readiness == (
        GeoXReadoutRecommendationReadiness.BLOCKED_PENDING_TRUST_REPORT
    )
    assert "trustreport" in routing.routing_summary.lower()
    assert "recommendationcontract remain blocked" in routing.routing_summary.lower()
    assert GeoXReadoutTrustRoutingIssueCode.NO_BUSINESS_RECOMMENDATION_AUTHORIZED in result.issues


def test_blocked_package_result_does_not_route_forward() -> None:
    envelope = _result_envelope(
        status=GeoXReadoutResultStatus.EXPLAINED_BLOCKED_PACKAGE_RESULT,
        package_readiness_status="BLOCKED_MISSING_SPEND_BASELINE",
        blocking_reasons=["missing_baseline_or_counterfactual_spend"],
    )
    result = route_geox_readout_result_to_trust_boundaries(_route_request(envelope))
    assert result.status == GeoXReadoutTrustRoutingStatus.BLOCKED_RESULT_NOT_READY
    routing = result.routing_envelope
    assert routing is not None
    assert routing.primary_route == GeoXReadoutTrustRoute.NO_ROUTE_BLOCKED
    assert routing.trust_report_route.ready_for_boundary is False
    assert routing.recommendation_readiness == (
        GeoXReadoutRecommendationReadiness.BLOCKED_PACKAGE_RESULT_NOT_READY
    )
    assert GeoXReadoutTrustRoutingIssueCode.PACKAGE_RESULT_BLOCKED in result.issues


def test_diagnostic_only_package_result_routes_diagnostic_only() -> None:
    envelope = _result_envelope(
        status=GeoXReadoutResultStatus.EXPLAINED_DIAGNOSTIC_ONLY_PACKAGE_RESULT,
        package_readiness_status="PARTIAL_DIAGNOSTIC_ONLY",
    )
    result = route_geox_readout_result_to_trust_boundaries(_route_request(envelope))
    assert result.status == GeoXReadoutTrustRoutingStatus.ROUTED_TO_DIAGNOSTIC_ONLY_REVIEW
    routing = result.routing_envelope
    assert routing is not None
    assert routing.primary_route == GeoXReadoutTrustRoute.DIAGNOSTIC_ONLY_REVIEW
    assert routing.recommendation_readiness == (
        GeoXReadoutRecommendationReadiness.BLOCKED_DIAGNOSTIC_ONLY
    )


def test_requested_decision_surface_before_trust_report_pending() -> None:
    result = route_geox_readout_result_to_trust_boundaries(
        _route_request(
            _result_envelope(),
            requested_route=GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW,
        )
    )
    assert result.status == GeoXReadoutTrustRoutingStatus.ROUTED_TO_TRUST_REPORT_REVIEW
    routing = result.routing_envelope
    assert routing is not None
    assert routing.decision_surface_route.ready_for_boundary is False
    blocked_reason = routing.decision_surface_route.blocked_reason or ""
    assert "TrustReport" in blocked_reason


def test_requested_decision_surface_after_trust_report_complete() -> None:
    result = route_geox_readout_result_to_trust_boundaries(
        _route_request(
            _result_envelope(lineage={"trust_report_review_complete": "true"}),
            requested_route=GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW,
            lineage={"trust_report_review_complete": "true"},
        )
    )
    assert result.status == GeoXReadoutTrustRoutingStatus.ROUTED_TO_DECISION_SURFACE_REVIEW
    routing = result.routing_envelope
    assert routing is not None
    assert routing.decision_surface_route.ready_for_boundary is True
    assert routing.decision_surface_route.target_contract_name == DECISION_SURFACE_CONTRACT_NAME
    assert routing.recommendation_contract_route.ready_for_boundary is False


def test_requested_recommendation_contract_blocked() -> None:
    result = route_geox_readout_result_to_trust_boundaries(
        _route_request(
            _result_envelope(),
            requested_route=GeoXReadoutTrustRoute.RECOMMENDATION_CONTRACT_BLOCKED,
        )
    )
    assert result.status == (
        GeoXReadoutTrustRoutingStatus.ROUTED_TO_RECOMMENDATION_CONTRACT_BLOCKED
    )
    routing = result.routing_envelope
    assert routing is not None
    assert routing.recommendation_contract_route.target_contract_name == (
        RECOMMENDATION_CONTRACT_NAME
    )
    assert routing.recommendation_readiness == GeoXReadoutRecommendationReadiness.NOT_AUTHORIZED
    assert (
        GeoXReadoutTrustRoutingIssueCode.RECOMMENDATION_REQUIRES_GOVERNED_DECISION_SURFACE
        in result.issues
    )


def test_claim_authorization_delegated_not_authorized() -> None:
    result = route_geox_readout_result_to_trust_boundaries(
        _route_request(_result_envelope())
    )
    routing = result.routing_envelope
    assert routing is not None
    assert routing.claim_authorization_owner == CLAIM_AUTHORIZATION_OWNER
    assert routing.claim_authorization_status == "DELEGATED"
    assert GeoXReadoutTrustRoutingIssueCode.CLAIM_AUTHORIZATION_NOT_EVALUATED in result.issues
    assert GeoXReadoutTrustRoutingIssueCode.NO_BUSINESS_RECOMMENDATION_AUTHORIZED in result.issues


def test_package_warnings_preserved() -> None:
    envelope = _result_envelope(warnings=["spend_window_partial"])
    result = route_geox_readout_result_to_trust_boundaries(_route_request(envelope))
    routing = result.routing_envelope
    assert routing is not None
    assert "spend_window_partial" in routing.warnings
    assert GeoXReadoutTrustRoutingIssueCode.PACKAGE_WARNINGS_PRESENT in result.issues


def test_package_computed_spend_delta_preserved_in_summary_only() -> None:
    envelope = _result_envelope(
        package_output_summary={
            "readiness_status": "READY",
            "package_computed_spend_delta": 749.0,
        }
    )
    result = route_geox_readout_result_to_trust_boundaries(_route_request(envelope))
    routing = result.routing_envelope
    assert routing is not None
    assert routing.package_output_summary["package_computed_spend_delta"] == 749.0
    payload = routing.model_dump()
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in payload
    assert GeoXReadoutTrustRoutingIssueCode.SPEND_DELTA_PACKAGE_COMPUTED in result.issues


def test_stage_result_ingestion_compatibility() -> None:
    ingestion = ingest_geox_readout_result_for_explanation(
        GeoXReadoutResultIngestionRequest(
            request_id="compat-ingest",
            evidence_artifact=GeoXPostTestSpendEvidenceArtifact(
                artifact_id="evidence:exp-compat",
                experiment_id="exp-compat",
                readiness_status="READY",
                package_output_summary={"readiness_status": "READY"},
            ),
            trusted_handoff_artifact=GeoXTrustedReadoutSpendHandoffArtifact(
                artifact_id="handoff:exp-compat",
                experiment_id="exp-compat",
                spend_readiness_summary={"readiness_status": "READY"},
                package_handoff_summary={"roi_claim_authorization_status": "NOT_EVALUATED"},
            ),
        )
    )
    assert ingestion.result_envelope is not None
    result = route_geox_readout_result_to_trust_boundaries(
        GeoXReadoutTrustRoutingRequest(
            request_id="compat-route",
            result_envelope=ingestion.result_envelope,
        )
    )
    assert result.status == GeoXReadoutTrustRoutingStatus.ROUTED_TO_TRUST_REPORT_REVIEW
    assert result.routing_envelope is not None


def test_no_panel_exp_import_in_routing_modules() -> None:
    for path in (_ROUTING_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "import panel_exp" not in source
        assert "from panel_exp" not in source


def test_no_metric_recomputation_fields() -> None:
    result = route_geox_readout_result_to_trust_boundaries(
        _route_request(_result_envelope())
    )
    payload = result.model_dump_json().lower()
    assert "mip_computed" not in payload
    assert GeoXReadoutTrustRoutingIssueCode.ROI_ROAS_NOT_COMPUTED_IN_MIP in result.issues
    assert GeoXReadoutTrustRoutingIssueCode.LIFT_NOT_COMPUTED_IN_MIP in result.issues
