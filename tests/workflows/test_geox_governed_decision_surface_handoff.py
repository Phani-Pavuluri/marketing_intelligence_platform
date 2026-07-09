"""Tests for GeoX governed DecisionSurface handoff workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.geox_governed_decision_surface_handoff import (
    GeoXDecisionSurfaceHandoffIssueCode,
    GeoXDecisionSurfaceHandoffStatus,
    GeoXDecisionSurfaceHandoffTarget,
    GeoXDecisionSurfaceReviewReadiness,
    GeoXGovernedDecisionSurfaceHandoffRequest,
)
from mip.contracts.geox_panel_exp_runtime_call import CLAIM_AUTHORIZATION_OWNER
from mip.contracts.geox_readout_result_ingestion import (
    GeoXReadoutClaimReadiness,
    GeoXReadoutResultEnvelope,
    GeoXReadoutResultExplanation,
    GeoXReadoutResultStatus,
)
from mip.contracts.geox_readout_trust_routing import (
    GeoXReadoutTrustRoute,
    GeoXReadoutTrustRoutingEnvelope,
    GeoXReadoutTrustRoutingRequest,
)
from mip.workflows.geox_governed_decision_surface_handoff import (
    build_geox_governed_decision_surface_handoff,
)
from mip.workflows.geox_readout_trust_routing import (
    route_geox_readout_result_to_trust_boundaries,
)

_WORKFLOW_SOURCE = Path("src/mip/workflows/geox_governed_decision_surface_handoff.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/geox_governed_decision_surface_handoff.py")
_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi_value", "roas_value")
_FORBIDDEN_WORDING = (
    "increase spend",
    "decrease spend",
    "recommend budget",
    "approve ROI",
    "approved ROI",
    "campaign is profitable",
    "budget shift",
)


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


def _result_envelope(
    *,
    status: GeoXReadoutResultStatus = GeoXReadoutResultStatus.EXPLAINED_READY_PACKAGE_RESULT,
    package_readiness_status: str = "READY",
    blocking_reasons: list[str] | None = None,
    warnings: list[str] | None = None,
    package_output_summary: dict[str, str | float | int | bool | None] | None = None,
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
        claim_authorization_owner=CLAIM_AUTHORIZATION_OWNER,
        explanation=_explanation(),
        lineage=lineage or {},
    )


def _routing_envelope(
    *,
    status: GeoXReadoutResultStatus = GeoXReadoutResultStatus.EXPLAINED_READY_PACKAGE_RESULT,
    package_readiness_status: str = "READY",
    blocking_reasons: list[str] | None = None,
    warnings: list[str] | None = None,
    package_output_summary: dict[str, str | float | int | bool | None] | None = None,
    lineage: dict[str, str] | None = None,
    requested_route: GeoXReadoutTrustRoute = GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW,
) -> GeoXReadoutTrustRoutingEnvelope:
    route_result = route_geox_readout_result_to_trust_boundaries(
        GeoXReadoutTrustRoutingRequest(
            request_id="route-1",
            result_envelope=_result_envelope(
                status=status,
                package_readiness_status=package_readiness_status,
                blocking_reasons=blocking_reasons,
                warnings=warnings,
                package_output_summary=package_output_summary,
                lineage=lineage,
            ),
            requested_route=requested_route,
            lineage=lineage or {},
        )
    )
    assert route_result.routing_envelope is not None
    return route_result.routing_envelope


def _handoff_request(
    routing_envelope: GeoXReadoutTrustRoutingEnvelope,
    *,
    trust_report_review_complete: bool = False,
    requested_target: GeoXDecisionSurfaceHandoffTarget = (
        GeoXDecisionSurfaceHandoffTarget.DECISION_SURFACE_REVIEW
    ),
) -> GeoXGovernedDecisionSurfaceHandoffRequest:
    return GeoXGovernedDecisionSurfaceHandoffRequest(
        request_id="handoff-1",
        trust_routing_envelope=routing_envelope,
        trust_report_review_complete=trust_report_review_complete,
        requested_target=requested_target,
    )


def test_missing_trust_routing_envelope_blocked() -> None:
    result = build_geox_governed_decision_surface_handoff(
        GeoXGovernedDecisionSurfaceHandoffRequest(request_id="handoff-1")
    )
    assert result.status == (
        GeoXDecisionSurfaceHandoffStatus.BLOCKED_MISSING_TRUST_ROUTING_ENVELOPE
    )
    assert GeoXDecisionSurfaceHandoffIssueCode.MISSING_TRUST_ROUTING_ENVELOPE in result.issues
    assert result.handoff is None


def test_malformed_trust_routing_envelope_blocked() -> None:
    routing = _routing_envelope()
    routing = routing.model_copy(update={"routing_id": ""})
    result = build_geox_governed_decision_surface_handoff(_handoff_request(routing))
    assert result.status == GeoXDecisionSurfaceHandoffStatus.BLOCKED_TRUST_ROUTING_MALFORMED
    assert result.handoff is None


def test_ready_package_trust_report_incomplete_pending() -> None:
    result = build_geox_governed_decision_surface_handoff(_handoff_request(_routing_envelope()))
    assert result.status == GeoXDecisionSurfaceHandoffStatus.PENDING_TRUST_REPORT_REVIEW
    handoff = result.handoff
    assert handoff is not None
    assert handoff.target == GeoXDecisionSurfaceHandoffTarget.TRUST_REPORT_REVIEW
    assert handoff.review_readiness == GeoXDecisionSurfaceReviewReadiness.PENDING_TRUST_REPORT
    assert handoff.recommendation_authorized is False
    assert GeoXDecisionSurfaceHandoffIssueCode.TRUST_REPORT_NOT_COMPLETE in result.issues


def test_ready_package_trust_report_complete_ready() -> None:
    routing = _routing_envelope(
        lineage={"trust_report_review_complete": "true"},
        requested_route=GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW,
    )
    result = build_geox_governed_decision_surface_handoff(
        _handoff_request(routing, trust_report_review_complete=True)
    )
    assert result.status == GeoXDecisionSurfaceHandoffStatus.READY_FOR_DECISION_SURFACE_REVIEW
    handoff = result.handoff
    assert handoff is not None
    assert handoff.target == GeoXDecisionSurfaceHandoffTarget.DECISION_SURFACE_REVIEW
    assert handoff.review_readiness == GeoXDecisionSurfaceReviewReadiness.READY
    assert handoff.recommendation_authorized is False


def test_blocked_package_result_blocked() -> None:
    routing = _routing_envelope(
        status=GeoXReadoutResultStatus.EXPLAINED_BLOCKED_PACKAGE_RESULT,
        package_readiness_status="BLOCKED_MISSING_SPEND_BASELINE",
        blocking_reasons=["missing_baseline_or_counterfactual_spend"],
    )
    result = build_geox_governed_decision_surface_handoff(_handoff_request(routing))
    assert result.status == GeoXDecisionSurfaceHandoffStatus.BLOCKED_PACKAGE_RESULT_NOT_READY
    handoff = result.handoff
    assert handoff is not None
    assert handoff.target == GeoXDecisionSurfaceHandoffTarget.NO_HANDOFF
    assert handoff.recommendation_authorized is False


def test_diagnostic_only_blocked() -> None:
    routing = _routing_envelope(
        status=GeoXReadoutResultStatus.EXPLAINED_DIAGNOSTIC_ONLY_PACKAGE_RESULT,
        package_readiness_status="PARTIAL_DIAGNOSTIC_ONLY",
    )
    result = build_geox_governed_decision_surface_handoff(_handoff_request(routing))
    assert result.status == GeoXDecisionSurfaceHandoffStatus.BLOCKED_DIAGNOSTIC_ONLY
    handoff = result.handoff
    assert handoff is not None
    assert handoff.review_readiness == GeoXDecisionSurfaceReviewReadiness.BLOCKED_DIAGNOSTIC_ONLY
    assert handoff.recommendation_authorized is False


def test_requested_recommendation_contract_blocked() -> None:
    routing = _routing_envelope(
        lineage={"trust_report_review_complete": "true"},
        requested_route=GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW,
    )
    result = build_geox_governed_decision_surface_handoff(
        _handoff_request(
            routing,
            trust_report_review_complete=True,
            requested_target=GeoXDecisionSurfaceHandoffTarget.RECOMMENDATION_CONTRACT_BLOCKED,
        )
    )
    assert result.status == GeoXDecisionSurfaceHandoffStatus.BLOCKED_RECOMMENDATION_CONTRACT
    handoff = result.handoff
    assert handoff is not None
    assert handoff.target == GeoXDecisionSurfaceHandoffTarget.RECOMMENDATION_CONTRACT_BLOCKED
    assert handoff.recommendation_authorized is False
    assert (
        GeoXDecisionSurfaceHandoffIssueCode.RECOMMENDATION_REQUIRES_GOVERNED_DECISION_SURFACE
        in result.issues
    )


def test_claim_authorization_delegated_not_authorized() -> None:
    result = build_geox_governed_decision_surface_handoff(_handoff_request(_routing_envelope()))
    handoff = result.handoff
    assert handoff is not None
    assert handoff.claim_authorization_owner == CLAIM_AUTHORIZATION_OWNER
    assert handoff.recommendation_authorized is False
    assert GeoXDecisionSurfaceHandoffIssueCode.CLAIM_AUTHORIZATION_DELEGATED in result.issues


def test_package_warnings_preserved() -> None:
    routing = _routing_envelope(warnings=["spend_baseline_partial"])
    result = build_geox_governed_decision_surface_handoff(_handoff_request(routing))
    assert "spend_baseline_partial" in result.warnings
    handoff = result.handoff
    assert handoff is not None
    assert "spend_baseline_partial" in handoff.warnings
    assert GeoXDecisionSurfaceHandoffIssueCode.PACKAGE_WARNINGS_PRESENT in result.issues


def test_package_computed_spend_delta_only_in_summary() -> None:
    routing = _routing_envelope(
        package_output_summary={
            "readiness_status": "READY",
            "package_computed_spend_delta": 1500.0,
        }
    )
    result = build_geox_governed_decision_surface_handoff(_handoff_request(routing))
    handoff = result.handoff
    assert handoff is not None
    assert handoff.evidence_reference.package_output_summary["package_computed_spend_delta"] == (
        1500.0
    )
    assert GeoXDecisionSurfaceHandoffIssueCode.SPEND_DELTA_PACKAGE_COMPUTED in result.issues
    dumped = handoff.model_dump()
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in dumped


def test_trust_routing_compatibility() -> None:
    routing = _routing_envelope()
    result = build_geox_governed_decision_surface_handoff(_handoff_request(routing))
    handoff = result.handoff
    assert handoff is not None
    assert handoff.source_routing_id == routing.routing_id
    assert handoff.evidence_reference.source_result_id == routing.source_result_id


def test_no_panel_exp_import_or_call() -> None:
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "import panel_exp" not in source
        assert "from panel_exp" not in source


def test_no_metric_recomputation_fields() -> None:
    result = build_geox_governed_decision_surface_handoff(_handoff_request(_routing_envelope()))
    handoff = result.handoff
    assert handoff is not None
    schema = handoff.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_no_recommendation_wording_in_summaries() -> None:
    routing = _routing_envelope(
        lineage={"trust_report_review_complete": "true"},
        requested_route=GeoXReadoutTrustRoute.DECISION_SURFACE_REVIEW,
    )
    result = build_geox_governed_decision_surface_handoff(
        _handoff_request(routing, trust_report_review_complete=True)
    )
    handoff = result.handoff
    assert handoff is not None
    summary_lower = handoff.handoff_summary.lower()
    for phrase in _FORBIDDEN_WORDING:
        assert phrase not in summary_lower
