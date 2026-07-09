"""GeoX readout trust-routing contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.geox_panel_exp_runtime_call import CLAIM_AUTHORIZATION_OWNER
from mip.contracts.geox_readout_result_ingestion import GeoXReadoutResultEnvelope

RECOMMENDED_NEXT_DECISION_SURFACE_HANDOFF_ARTIFACT = (
    "MIP_GEOX_READOUT_GOVERNED_DECISION_SURFACE_HANDOFF_001"
)

TRUST_REPORT_CONTRACT_NAME = "TrustReport"
DECISION_SURFACE_CONTRACT_NAME = "DecisionSurface"
RECOMMENDATION_CONTRACT_NAME = "RecommendationContract"


class GeoXReadoutTrustRoutingStatus(StrEnum):
    """Outcome of routing a GeoX readout result to governance boundaries."""

    ROUTED_TO_TRUST_REPORT_REVIEW = "routed_to_trust_report_review"
    ROUTED_TO_DECISION_SURFACE_REVIEW = "routed_to_decision_surface_review"
    ROUTED_TO_RECOMMENDATION_CONTRACT_BLOCKED = "routed_to_recommendation_contract_blocked"
    ROUTED_TO_DIAGNOSTIC_ONLY_REVIEW = "routed_to_diagnostic_only_review"
    BLOCKED_MISSING_RESULT_ENVELOPE = "blocked_missing_result_envelope"
    BLOCKED_RESULT_NOT_READY = "blocked_result_not_ready"
    BLOCKED_RESULT_DIAGNOSTIC_ONLY = "blocked_result_diagnostic_only"
    BLOCKED_RESULT_MALFORMED = "blocked_result_malformed"
    BLOCKED_CLAIM_AUTHORIZATION_NOT_EVALUATED = "blocked_claim_authorization_not_evaluated"


class GeoXReadoutTrustRoute(StrEnum):
    """Governance route targets for GeoX readout results."""

    TRUST_REPORT_REVIEW = "trust_report_review"
    DECISION_SURFACE_REVIEW = "decision_surface_review"
    RECOMMENDATION_CONTRACT_BLOCKED = "recommendation_contract_blocked"
    DIAGNOSTIC_ONLY_REVIEW = "diagnostic_only_review"
    NO_ROUTE_BLOCKED = "no_route_blocked"


class GeoXReadoutTrustRoutingIssueCode(StrEnum):
    """Typed trust-routing issue codes."""

    MISSING_RESULT_ENVELOPE = "missing_result_envelope"
    RESULT_ENVELOPE_MALFORMED = "result_envelope_malformed"
    PACKAGE_RESULT_BLOCKED = "package_result_blocked"
    PACKAGE_RESULT_DIAGNOSTIC_ONLY = "package_result_diagnostic_only"
    PACKAGE_WARNINGS_PRESENT = "package_warnings_present"
    CLAIM_AUTHORIZATION_DELEGATED = "claim_authorization_delegated"
    CLAIM_AUTHORIZATION_NOT_EVALUATED = "claim_authorization_not_evaluated"
    TRUST_REPORT_REQUIRED = "trust_report_required"
    DECISION_SURFACE_REQUIRED = "decision_surface_required"
    RECOMMENDATION_CONTRACT_BLOCKED = "recommendation_contract_blocked"
    RECOMMENDATION_REQUIRES_GOVERNED_DECISION_SURFACE = (
        "recommendation_requires_governed_decision_surface"
    )
    ROI_ROAS_NOT_COMPUTED_IN_MIP = "roi_roas_not_computed_in_mip"
    LIFT_NOT_COMPUTED_IN_MIP = "lift_not_computed_in_mip"
    SPEND_DELTA_PACKAGE_COMPUTED = "spend_delta_package_computed"
    NO_BUSINESS_RECOMMENDATION_AUTHORIZED = "no_business_recommendation_authorized"


class GeoXReadoutRecommendationReadiness(StrEnum):
    """Recommendation boundary readiness — blocked by default in trust routing."""

    BLOCKED_PENDING_TRUST_REPORT = "blocked_pending_trust_report"
    BLOCKED_PENDING_DECISION_SURFACE = "blocked_pending_decision_surface"
    BLOCKED_DIAGNOSTIC_ONLY = "blocked_diagnostic_only"
    BLOCKED_PACKAGE_RESULT_NOT_READY = "blocked_package_result_not_ready"
    NOT_AUTHORIZED = "not_authorized"


class GeoXReadoutTrustRoutingRequest(ContractBaseModel):
    """Request to route a GeoX readout result envelope to governance boundaries."""

    request_id: str
    result_envelope: GeoXReadoutResultEnvelope | None = None
    requested_route: GeoXReadoutTrustRoute = GeoXReadoutTrustRoute.TRUST_REPORT_REVIEW
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXReadoutTrustRouteTarget(ContractBaseModel):
    """Routing metadata for one governance boundary target."""

    route: GeoXReadoutTrustRoute
    target_contract_name: str
    ready_for_boundary: bool = False
    blocked_reason: str | None = None
    required_next_action: str
    lineage: dict[str, str] = Field(default_factory=dict)


class GeoXReadoutTrustRoutingEnvelope(ContractBaseModel):
    """Trust-routing envelope preserving package outputs and governance routes."""

    routing_id: str
    experiment_id: str
    source_result_id: str
    source_package_readiness_status: str
    primary_route: GeoXReadoutTrustRoute
    trust_report_route: GeoXReadoutTrustRouteTarget
    decision_surface_route: GeoXReadoutTrustRouteTarget
    recommendation_contract_route: GeoXReadoutTrustRouteTarget
    recommendation_readiness: GeoXReadoutRecommendationReadiness
    claim_authorization_owner: str = CLAIM_AUTHORIZATION_OWNER
    claim_authorization_status: str = "NOT_EVALUATED"
    package_output_summary: dict[str, str | float | int | bool | None] = Field(
        default_factory=dict
    )
    routing_summary: str
    issues: list[GeoXReadoutTrustRoutingIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class GeoXReadoutTrustRoutingResult(ContractBaseModel):
    """Result of routing a GeoX readout result to governance boundaries."""

    request_id: str
    status: GeoXReadoutTrustRoutingStatus
    routing_envelope: GeoXReadoutTrustRoutingEnvelope | None = None
    issues: list[GeoXReadoutTrustRoutingIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
