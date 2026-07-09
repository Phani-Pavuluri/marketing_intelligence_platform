"""GeoX governed DecisionSurface handoff contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.geox_panel_exp_runtime_call import CLAIM_AUTHORIZATION_OWNER
from mip.contracts.geox_readout_trust_routing import (
    DECISION_SURFACE_CONTRACT_NAME,
    RECOMMENDATION_CONTRACT_NAME,
    TRUST_REPORT_CONTRACT_NAME,
    GeoXReadoutTrustRoutingEnvelope,
)

RECOMMENDED_NEXT_RECOMMENDATION_BLOCKER_ARTIFACT = (
    "MIP_GEOX_READOUT_RECOMMENDATION_CONTRACT_BLOCKER_001"
)


class GeoXDecisionSurfaceHandoffStatus(StrEnum):
    """Outcome of building a governed DecisionSurface handoff."""

    READY_FOR_DECISION_SURFACE_REVIEW = "ready_for_decision_surface_review"
    PENDING_TRUST_REPORT_REVIEW = "pending_trust_report_review"
    BLOCKED_MISSING_TRUST_ROUTING_ENVELOPE = "blocked_missing_trust_routing_envelope"
    BLOCKED_TRUST_ROUTING_MALFORMED = "blocked_trust_routing_malformed"
    BLOCKED_TRUST_REPORT_NOT_COMPLETE = "blocked_trust_report_not_complete"
    BLOCKED_PACKAGE_RESULT_NOT_READY = "blocked_package_result_not_ready"
    BLOCKED_DIAGNOSTIC_ONLY = "blocked_diagnostic_only"
    BLOCKED_RECOMMENDATION_CONTRACT = "blocked_recommendation_contract"
    BLOCKED_CLAIM_AUTHORIZATION_NOT_EVALUATED = "blocked_claim_authorization_not_evaluated"


class GeoXDecisionSurfaceHandoffIssueCode(StrEnum):
    """Typed DecisionSurface handoff issue codes."""

    MISSING_TRUST_ROUTING_ENVELOPE = "missing_trust_routing_envelope"
    TRUST_ROUTING_ENVELOPE_MALFORMED = "trust_routing_envelope_malformed"
    TRUST_REPORT_REQUIRED = "trust_report_required"
    TRUST_REPORT_NOT_COMPLETE = "trust_report_not_complete"
    PACKAGE_RESULT_NOT_READY = "package_result_not_ready"
    PACKAGE_RESULT_DIAGNOSTIC_ONLY = "package_result_diagnostic_only"
    PACKAGE_WARNINGS_PRESENT = "package_warnings_present"
    CLAIM_AUTHORIZATION_DELEGATED = "claim_authorization_delegated"
    CLAIM_AUTHORIZATION_NOT_EVALUATED = "claim_authorization_not_evaluated"
    DECISION_SURFACE_REVIEW_REQUIRED = "decision_surface_review_required"
    RECOMMENDATION_CONTRACT_BLOCKED = "recommendation_contract_blocked"
    RECOMMENDATION_REQUIRES_GOVERNED_DECISION_SURFACE = (
        "recommendation_requires_governed_decision_surface"
    )
    ROI_ROAS_NOT_COMPUTED_IN_MIP = "roi_roas_not_computed_in_mip"
    LIFT_NOT_COMPUTED_IN_MIP = "lift_not_computed_in_mip"
    SPEND_DELTA_PACKAGE_COMPUTED = "spend_delta_package_computed"
    NO_BUSINESS_RECOMMENDATION_AUTHORIZED = "no_business_recommendation_authorized"


class GeoXDecisionSurfaceReviewReadiness(StrEnum):
    """DecisionSurface review readiness for handoff."""

    READY = "ready"
    PENDING_TRUST_REPORT = "pending_trust_report"
    BLOCKED_RESULT_NOT_READY = "blocked_result_not_ready"
    BLOCKED_DIAGNOSTIC_ONLY = "blocked_diagnostic_only"
    BLOCKED_MALFORMED = "blocked_malformed"
    NOT_AUTHORIZED = "not_authorized"


class GeoXDecisionSurfaceHandoffTarget(StrEnum):
    """Governed handoff target boundary."""

    DECISION_SURFACE_REVIEW = "decision_surface_review"
    TRUST_REPORT_REVIEW = "trust_report_review"
    RECOMMENDATION_CONTRACT_BLOCKED = "recommendation_contract_blocked"
    NO_HANDOFF = "no_handoff"


class GeoXGovernedDecisionSurfaceHandoffRequest(ContractBaseModel):
    """Request to build a governed DecisionSurface handoff from trust routing."""

    request_id: str
    trust_routing_envelope: GeoXReadoutTrustRoutingEnvelope | None = None
    trust_report_review_complete: bool = False
    requested_target: GeoXDecisionSurfaceHandoffTarget = (
        GeoXDecisionSurfaceHandoffTarget.DECISION_SURFACE_REVIEW
    )
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXDecisionSurfaceEvidenceReference(ContractBaseModel):
    """Evidence reference carried into DecisionSurface review boundary."""

    source_result_id: str
    source_routing_id: str
    experiment_id: str
    package_readiness_status: str
    claim_authorization_owner: str = CLAIM_AUTHORIZATION_OWNER
    package_output_summary: dict[str, str | float | int | bool | None] = Field(
        default_factory=dict
    )
    package_warnings: list[str] = Field(default_factory=list)
    source_lineage: dict[str, str] = Field(default_factory=dict)


class GeoXGovernedDecisionSurfaceHandoff(ContractBaseModel):
    """Governed handoff envelope for DecisionSurface review — not a decision result."""

    handoff_id: str
    experiment_id: str
    source_routing_id: str
    target: GeoXDecisionSurfaceHandoffTarget
    review_readiness: GeoXDecisionSurfaceReviewReadiness
    trust_report_review_complete: bool = False
    decision_surface_contract_name: str = DECISION_SURFACE_CONTRACT_NAME
    trust_report_contract_name: str = TRUST_REPORT_CONTRACT_NAME
    recommendation_contract_name: str = RECOMMENDATION_CONTRACT_NAME
    evidence_reference: GeoXDecisionSurfaceEvidenceReference
    handoff_summary: str
    required_next_action: str
    claim_authorization_owner: str = CLAIM_AUTHORIZATION_OWNER
    claim_authorization_status: str = "NOT_EVALUATED"
    recommendation_authorized: bool = False
    issues: list[GeoXDecisionSurfaceHandoffIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class GeoXGovernedDecisionSurfaceHandoffResult(ContractBaseModel):
    """Result of building a governed DecisionSurface handoff."""

    request_id: str
    status: GeoXDecisionSurfaceHandoffStatus
    handoff: GeoXGovernedDecisionSurfaceHandoff | None = None
    issues: list[GeoXDecisionSurfaceHandoffIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
