"""MMM artifact governance and use-readiness gate contracts (metadata only)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.mmm_existing_model_availability import MMMModelArtifact
from mip.contracts.mmm_runtime_result_ingestion import MMMRuntimeResultIngestionResult

RECOMMENDED_NEXT_MMM_RUNTIME_ORCHESTRATION_LANE_COMPLETION_AUDIT_ARTIFACT = (
    "MIP_MMM_RUNTIME_ORCHESTRATION_LANE_COMPLETION_AUDIT_001"
)

_FORBIDDEN_RESULT_FIELD_NAMES = frozenset(
    {
        "spend_delta",
        "delta_mu",
        "roi",
        "roas",
        "lift",
        "incrementality",
        "optimal_budget",
        "marginal_roi",
        "recommendation",
        "budget_recommendation",
    }
)


class MMMArtifactGovernanceUseReadinessStatus(StrEnum):
    """Outcome of MMM artifact governance and use-readiness evaluation."""

    READY_FOR_GOVERNANCE_REVIEW = "ready_for_governance_review"
    READY_FOR_GOVERNANCE_REVIEW_WITH_WARNINGS = "ready_for_governance_review_with_warnings"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    BLOCKED = "blocked"
    DEFERRED = "deferred"
    RUNTIME_FAILED = "runtime_failed"
    MISSING_RUNTIME_INGESTION_RESULT = "missing_runtime_ingestion_result"
    MISSING_REQUIRED_ARTIFACT_METADATA = "missing_required_artifact_metadata"


class MMMArtifactGovernanceRoute(StrEnum):
    """Governance route targets for ingested MMM runtime results."""

    TRUST_REPORT_REVIEW = "trust_report_review"
    DECISION_SURFACE_REVIEW = "decision_surface_review"
    DIAGNOSTIC_REVIEW = "diagnostic_review"
    NO_ROUTE_BLOCKED = "no_route_blocked"
    NO_ROUTE_DEFERRED = "no_route_deferred"


class MMMArtifactUseReadiness(StrEnum):
    """Downstream use readiness for an ingested MMM runtime result."""

    PLANNING_READY = "planning_ready"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    NOT_PLANNING_READY = "not_planning_ready"
    BLOCKED = "blocked"
    DEFERRED = "deferred"
    UNKNOWN = "unknown"


class MMMArtifactGovernanceUseReadinessIssueCode(StrEnum):
    """Typed issue codes for MMM artifact governance and use-readiness."""

    RUNTIME_INGESTION_RESULT_PRESENT = "runtime_ingestion_result_present"
    RUNTIME_INGESTION_RESULT_MISSING = "runtime_ingestion_result_missing"
    RUNTIME_RESULT_READY_FOR_GOVERNANCE = "runtime_result_ready_for_governance"
    RUNTIME_RESULT_NOT_READY_FOR_GOVERNANCE = "runtime_result_not_ready_for_governance"
    RUNTIME_FAILED = "runtime_failed"
    MODEL_ARTIFACT_PRESENT = "model_artifact_present"
    MODEL_ARTIFACT_MISSING = "model_artifact_missing"
    MODEL_ARTIFACT_URI_PRESENT = "model_artifact_uri_present"
    MODEL_ARTIFACT_URI_MISSING = "model_artifact_uri_missing"
    DIAGNOSTICS_URI_PRESENT = "diagnostics_uri_present"
    DIAGNOSTICS_URI_MISSING = "diagnostics_uri_missing"
    MANIFEST_URI_PRESENT = "manifest_uri_present"
    MANIFEST_URI_MISSING = "manifest_uri_missing"
    PROMOTION_STATUS_PRESENT = "promotion_status_present"
    PROMOTION_STATUS_MISSING = "promotion_status_missing"
    DIAGNOSTIC_STATUS_PRESENT = "diagnostic_status_present"
    DIAGNOSTIC_STATUS_MISSING = "diagnostic_status_missing"
    ALLOWED_USES_PRESENT = "allowed_uses_present"
    ALLOWED_USES_MISSING = "allowed_uses_missing"
    TRUST_REVIEW_ROUTE_READY = "trust_review_route_ready"
    DECISION_SURFACE_REVIEW_ROUTE_READY = "decision_surface_review_route_ready"
    DIAGNOSTIC_REVIEW_ROUTE_READY = "diagnostic_review_route_ready"
    PLANNING_USE_ALLOWED = "planning_use_allowed"
    PLANNING_USE_NOT_ALLOWED = "planning_use_not_allowed"
    DIAGNOSTIC_ONLY_USE = "diagnostic_only_use"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    BLOCKED_MISSING_METADATA = "blocked_missing_metadata"
    BLOCKED_BY_PROMOTION_STATUS = "blocked_by_promotion_status"
    BLOCKED_BY_DIAGNOSTIC_STATUS = "blocked_by_diagnostic_status"
    BLOCKED_BY_RUNTIME_INGESTION = "blocked_by_runtime_ingestion"
    DEFERRED_BY_RUNTIME_INGESTION = "deferred_by_runtime_ingestion"
    LINEAGE_PRESERVED = "lineage_preserved"
    REUSED_MODEL_ARTIFACT_METADATA = "reused_model_artifact_metadata"
    NO_MODEL_PROMOTION_IMPLEMENTED = "no_model_promotion_implemented"
    NO_TRUST_REPORT_CONSTRUCTION = "no_trust_report_construction"
    NO_DECISION_SURFACE_CONSTRUCTION = "no_decision_surface_construction"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_RECOMMENDATION_GENERATION = "no_recommendation_generation"
    NO_ARTIFACT_LOADING = "no_artifact_loading"
    NO_DIAGNOSTICS_PARSING = "no_diagnostics_parsing"
    NO_DIAGNOSTICS_CALCULATION = "no_diagnostics_calculation"
    NO_MODEL_LOADING = "no_model_loading"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_MMM_FITTING = "no_mmm_fitting"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"  # must not execute optimizer
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"  # must not execute simulator
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"


class MMMArtifactGovernanceRouteDecision(ContractBaseModel):
    """Metadata-only decision for one governance route target."""

    route: MMMArtifactGovernanceRoute
    enabled: bool = False
    reason: str
    candidate_reference: str | None = None
    blocked_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("reason")
    @classmethod
    def reason_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "route decision reason cannot be empty"
            raise ValueError(msg)
        return value


class MMMArtifactGovernanceUseReadinessRequest(ContractBaseModel):
    """Request to evaluate governance routing and use readiness for an ingested MMM result."""

    request_id: str
    runtime_ingestion_result: MMMRuntimeResultIngestionResult | None = None
    model_artifact: MMMModelArtifact | None = None
    require_model_artifact: bool = False
    require_model_artifact_uri: bool = True
    require_diagnostics_uri: bool = False
    require_manifest_uri: bool = True
    allow_diagnostic_only_route: bool = True
    allow_decision_surface_route: bool = True
    allow_trust_report_route: bool = True
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


class MMMArtifactGovernanceUseReadinessResult(ContractBaseModel):
    """Result of MMM artifact governance routing and use-readiness evaluation."""

    request_id: str
    status: MMMArtifactGovernanceUseReadinessStatus
    use_readiness: MMMArtifactUseReadiness
    route_decisions: list[MMMArtifactGovernanceRouteDecision] = Field(default_factory=list)
    ready_for_trust_report_review: bool = False
    ready_for_decision_surface_review: bool = False
    ready_for_diagnostic_review: bool = False
    planning_ready: bool = False
    diagnostic_only: bool = False
    human_review_required: bool = False
    blocked_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    issues: list[MMMArtifactGovernanceUseReadinessIssueCode] = Field(default_factory=list)
    runtime_ingestion_result_id: str | None = None
    external_run_id: str | None = None
    model_artifact_id: str | None = None
    model_artifact_uri: str | None = None
    diagnostics_uri: str | None = None
    manifest_uri: str | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


FORBIDDEN_MMM_ARTIFACT_GOVERNANCE_USE_READINESS_RESULT_FIELD_NAMES = _FORBIDDEN_RESULT_FIELD_NAMES
