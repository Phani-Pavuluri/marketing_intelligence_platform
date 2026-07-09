"""GeoX readout result ingestion and explanation contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.geox_panel_exp_runtime_call import (
    CLAIM_AUTHORIZATION_OWNER,
    GeoXPostTestSpendEvidenceArtifact,
    GeoXTrustedReadoutSpendHandoffArtifact,
)

RECOMMENDED_NEXT_TRUST_ROUTING_ARTIFACT = "MIP_GEOX_READOUT_TRUST_ROUTING_001"


class GeoXReadoutResultStatus(StrEnum):
    """Outcome of ingesting package readiness artifacts for MIP explanation."""

    READY_FOR_EXPLANATION = "ready_for_explanation"
    EXPLAINED_READY_PACKAGE_RESULT = "explained_ready_package_result"
    EXPLAINED_BLOCKED_PACKAGE_RESULT = "explained_blocked_package_result"
    EXPLAINED_DIAGNOSTIC_ONLY_PACKAGE_RESULT = "explained_diagnostic_only_package_result"
    BLOCKED_MISSING_EVIDENCE_ARTIFACT = "blocked_missing_evidence_artifact"
    BLOCKED_MISSING_TRUSTED_HANDOFF_ARTIFACT = "blocked_missing_trusted_handoff_artifact"
    BLOCKED_MALFORMED_PACKAGE_ARTIFACT = "blocked_malformed_package_artifact"
    BLOCKED_CLAIM_AUTHORIZATION_NOT_EVALUATED = "blocked_claim_authorization_not_evaluated"


class GeoXReadoutResultIssueCode(StrEnum):
    """Typed result-ingestion issue codes."""

    MISSING_EVIDENCE_ARTIFACT = "missing_evidence_artifact"
    MISSING_TRUSTED_HANDOFF_ARTIFACT = "missing_trusted_handoff_artifact"
    MALFORMED_PACKAGE_ARTIFACT = "malformed_package_artifact"
    PACKAGE_READINESS_BLOCKED = "package_readiness_blocked"
    PACKAGE_READINESS_DIAGNOSTIC_ONLY = "package_readiness_diagnostic_only"
    PACKAGE_WARNINGS_PRESENT = "package_warnings_present"
    CLAIM_AUTHORIZATION_DELEGATED = "claim_authorization_delegated"
    CLAIM_AUTHORIZATION_NOT_EVALUATED = "claim_authorization_not_evaluated"
    ROI_ROAS_NOT_COMPUTED_IN_MIP = "roi_roas_not_computed_in_mip"
    LIFT_NOT_COMPUTED_IN_MIP = "lift_not_computed_in_mip"
    SPEND_DELTA_PACKAGE_COMPUTED = "spend_delta_package_computed"
    RECOMMENDATION_REQUIRES_DECISION_SURFACE = "recommendation_requires_decision_surface"
    TRUST_REPORT_REQUIRED_FOR_CLAIMS = "trust_report_required_for_claims"


class GeoXReadoutExplanationAudience(StrEnum):
    """Audience for MIP-facing readout explanations."""

    TECHNICAL = "technical"
    BUSINESS = "business"
    GOVERNANCE = "governance"


class GeoXReadoutClaimReadiness(StrEnum):
    """MIP-side claim readiness — explanation only, not authorization."""

    NOT_AUTHORIZED = "not_authorized"
    NOT_EVALUATED = "not_evaluated"
    DELEGATED_TO_CLAIM_AUTHORIZATION_RUNTIME = "delegated_to_claim_authorization_runtime"
    READY_FOR_TRUST_REPORT_REVIEW = "ready_for_trust_report_review"
    READY_FOR_DECISION_SURFACE_REVIEW = "ready_for_decision_surface_review"


class GeoXReadoutResultIngestionRequest(ContractBaseModel):
    """Request to ingest Stage 3B package artifacts into a MIP explanation envelope."""

    request_id: str
    evidence_artifact: GeoXPostTestSpendEvidenceArtifact | None = None
    trusted_handoff_artifact: GeoXTrustedReadoutSpendHandoffArtifact | None = None
    audience: GeoXReadoutExplanationAudience = GeoXReadoutExplanationAudience.TECHNICAL
    include_package_output_summary: bool = True
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXReadoutResultExplanation(ContractBaseModel):
    """MIP-facing explanation of package readiness artifacts."""

    summary: str
    readiness_explanation: str
    blocker_explanation: str
    warning_explanation: str
    claim_boundary_explanation: str
    next_action: str
    technical_details: list[str] = Field(default_factory=list)
    business_safe_summary: str
    governance_notes: list[str] = Field(default_factory=list)


class GeoXReadoutResultEnvelope(ContractBaseModel):
    """MIP-facing readout result envelope preserving package outputs."""

    result_id: str
    experiment_id: str
    status: GeoXReadoutResultStatus
    package_readiness_status: str
    package_blocking_reasons: list[str] = Field(default_factory=list)
    package_warnings: list[str] = Field(default_factory=list)
    package_output_summary: dict[str, str | float | int | bool | None] = Field(
        default_factory=dict
    )
    trusted_handoff_summary: dict[str, str | bool] = Field(default_factory=dict)
    claim_readiness: GeoXReadoutClaimReadiness
    claim_authorization_owner: str = CLAIM_AUTHORIZATION_OWNER
    explanation: GeoXReadoutResultExplanation
    issues: list[GeoXReadoutResultIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)


class GeoXReadoutResultIngestionResult(ContractBaseModel):
    """Result of ingesting package artifacts for MIP explanation."""

    request_id: str
    status: GeoXReadoutResultStatus
    result_envelope: GeoXReadoutResultEnvelope | None = None
    registered_artifact_ref_optional: str | None = None
    issues: list[GeoXReadoutResultIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
