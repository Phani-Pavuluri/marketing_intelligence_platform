"""MMM runtime result ingestion and diagnostics-reference contracts (metadata only)."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.mmm_runtime_adapter import (
    MMMRuntimeArtifactHandoff,
    MMMRuntimeCallResult,
    MMMRuntimeFailurePacket,
)

RECOMMENDED_NEXT_MMM_ARTIFACT_GOVERNANCE_ROUTING_GATE_AUDIT_ARTIFACT = (
    "MIP_MMM_ARTIFACT_GOVERNANCE_ROUTING_GATE_AUDIT_001"
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


class MMMRuntimeResultIngestionStatus(StrEnum):
    """Outcome of ingesting external MMM runtime result metadata."""

    INGESTION_READY_FOR_GOVERNANCE_REVIEW = "ingestion_ready_for_governance_review"
    INGESTION_READY_WITH_WARNINGS = "ingestion_ready_with_warnings"
    INGESTION_DIAGNOSTICS_METADATA_MISSING = "ingestion_diagnostics_metadata_missing"
    INGESTION_RUNTIME_FAILED = "ingestion_runtime_failed"
    INGESTION_BLOCKED_MISSING_RUNTIME_RESULT = "ingestion_blocked_missing_runtime_result"
    INGESTION_BLOCKED_MISSING_ARTIFACT_HANDOFF = "ingestion_blocked_missing_artifact_handoff"
    INGESTION_BLOCKED_MISSING_EXTERNAL_RUN_ID = "ingestion_blocked_missing_external_run_id"
    INGESTION_BLOCKED_MISSING_MODEL_ARTIFACT_URI = "ingestion_blocked_missing_model_artifact_uri"
    INGESTION_BLOCKED_MISSING_MANIFEST_URI = "ingestion_blocked_missing_manifest_uri"
    INGESTION_DEFERRED = "ingestion_deferred"


class MMMRuntimeDiagnosticsMetadataStatus(StrEnum):
    """Diagnostics metadata availability for an ingested runtime result."""

    DIAGNOSTICS_METADATA_PRESENT = "diagnostics_metadata_present"
    DIAGNOSTICS_METADATA_PRESENT_WITH_WARNINGS = "diagnostics_metadata_present_with_warnings"
    DIAGNOSTICS_METADATA_MISSING = "diagnostics_metadata_missing"
    DIAGNOSTICS_METADATA_FAILED = "diagnostics_metadata_failed"
    DIAGNOSTICS_METADATA_DEFERRED = "diagnostics_metadata_deferred"


class MMMRuntimeGovernanceRoutingStatus(StrEnum):
    """Governance routing readiness for ingested runtime result metadata."""

    READY_FOR_GOVERNANCE_REVIEW = "ready_for_governance_review"
    READY_FOR_GOVERNANCE_REVIEW_WITH_WARNINGS = "ready_for_governance_review_with_warnings"
    BLOCKED_MISSING_REQUIRED_ARTIFACTS = "blocked_missing_required_artifacts"
    BLOCKED_RUNTIME_FAILED = "blocked_runtime_failed"
    DEFERRED = "deferred"


class MMMRuntimeResultIngestionIssueCode(StrEnum):
    """Typed issue codes for MMM runtime result ingestion."""

    RUNTIME_RESULT_PRESENT = "runtime_result_present"
    RUNTIME_RESULT_MISSING = "runtime_result_missing"
    ARTIFACT_HANDOFF_PRESENT = "artifact_handoff_present"
    ARTIFACT_HANDOFF_MISSING = "artifact_handoff_missing"
    EXTERNAL_RUN_ID_PRESENT = "external_run_id_present"
    EXTERNAL_RUN_ID_MISSING = "external_run_id_missing"
    MODEL_ARTIFACT_URI_PRESENT = "model_artifact_uri_present"
    MODEL_ARTIFACT_URI_MISSING = "model_artifact_uri_missing"
    MANIFEST_URI_PRESENT = "manifest_uri_present"
    MANIFEST_URI_MISSING = "manifest_uri_missing"
    DIAGNOSTICS_URI_PRESENT = "diagnostics_uri_present"
    DIAGNOSTICS_URI_MISSING = "diagnostics_uri_missing"
    RUNTIME_LOGS_URI_PRESENT = "runtime_logs_uri_present"
    RUNTIME_LOGS_URI_MISSING = "runtime_logs_uri_missing"
    FAILURE_PACKET_PRESENT = "failure_packet_present"
    FAILURE_PACKET_ABSENT = "failure_packet_absent"
    RUNTIME_FAILED = "runtime_failed"
    RUNTIME_STATUS_RECORDED = "runtime_status_recorded"
    DIAGNOSTICS_METADATA_READY = "diagnostics_metadata_ready"
    DIAGNOSTICS_METADATA_DEFERRED = "diagnostics_metadata_deferred"
    GOVERNANCE_REVIEW_READY = "governance_review_ready"
    GOVERNANCE_REVIEW_BLOCKED = "governance_review_blocked"
    TRUST_ROUTING_REFERENCE_CREATED = "trust_routing_reference_created"
    DECISION_SURFACE_ROUTING_REFERENCE_CREATED = "decision_surface_routing_reference_created"
    ARTIFACT_URI_METADATA_PRESERVED = "artifact_uri_metadata_preserved"
    LINEAGE_PRESERVED = "lineage_preserved"
    NO_ARTIFACT_LOADING = "no_artifact_loading"
    NO_DIAGNOSTICS_PARSING = "no_diagnostics_parsing"
    NO_DIAGNOSTICS_CALCULATION = "no_diagnostics_calculation"
    NO_MODEL_LOADING = "no_model_loading"
    NO_MODEL_EXECUTION = "no_model_execution"
    NO_MMM_FITTING = "no_mmm_fitting"
    NO_BAYESIAN_FITTING = "no_bayesian_fitting"
    NO_PRIOR_APPLICATION = "no_prior_application"
    NO_LIKELIHOOD_CONSTRUCTION = "no_likelihood_construction"
    NO_POSTERIOR_CALCULATION = "no_posterior_calculation"
    NO_OPTIMIZER_EXECUTION = "no_optimizer_execution"
    NO_SIMULATOR_EXECUTION = "no_simulator_execution"
    NO_RECOMMENDATION_GENERATED = "no_recommendation_generated"
    NO_DECISION_SURFACE_CONSTRUCTION = "no_decision_surface_construction"
    NO_DECISION_SURFACE_EXECUTION = "no_decision_surface_execution"
    NO_TRUST_REPORT_CONSTRUCTION = "no_trust_report_construction"
    NO_CLAIM_AUTHORIZATION = "no_claim_authorization"


class MMMRuntimeDiagnosticsMetadata(ContractBaseModel):
    """Metadata-only diagnostics references from an external MMM runtime result."""

    diagnostics_metadata_id: str
    external_run_id: str
    diagnostics_uri: str | None = None
    manifest_uri: str | None = None
    runtime_logs_uri: str | None = None
    diagnostics_status: MMMRuntimeDiagnosticsMetadataStatus = (
        MMMRuntimeDiagnosticsMetadataStatus.DIAGNOSTICS_METADATA_DEFERRED
    )
    diagnostics_summary_reference: str | None = None
    diagnostic_artifact_uris: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    issues: list[MMMRuntimeResultIngestionIssueCode] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("diagnostics_metadata_id", "external_run_id")
    @classmethod
    def non_empty_ids(cls, value: str) -> str:
        if not value.strip():
            msg = "diagnostics metadata id fields cannot be empty"
            raise ValueError(msg)
        return value


class MMMRuntimeGovernanceRoutingReference(ContractBaseModel):
    """Metadata-only governance routing candidate references for ingested runtime results."""

    routing_id: str
    external_run_id: str
    model_artifact_uri: str | None = None
    manifest_uri: str | None = None
    diagnostics_uri: str | None = None
    trust_report_candidate_reference: str | None = None
    decision_surface_candidate_reference: str | None = None
    governance_routing_status: MMMRuntimeGovernanceRoutingStatus = (
        MMMRuntimeGovernanceRoutingStatus.DEFERRED
    )
    warnings: list[str] = Field(default_factory=list)
    issues: list[MMMRuntimeResultIngestionIssueCode] = Field(default_factory=list)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("routing_id", "external_run_id")
    @classmethod
    def non_empty_ids(cls, value: str) -> str:
        if not value.strip():
            msg = "governance routing id fields cannot be empty"
            raise ValueError(msg)
        return value


class MMMRuntimeResultIngestionRequest(ContractBaseModel):
    """Request to ingest external MMM runtime result metadata."""

    request_id: str
    runtime_call_result: MMMRuntimeCallResult | None = None
    require_model_artifact_uri: bool = True
    require_manifest_uri: bool = True
    require_diagnostics_uri: bool = False
    require_runtime_logs_uri: bool = False
    create_governance_routing_reference: bool = True
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


class MMMRuntimeResultIngestionResult(ContractBaseModel):
    """Result of ingesting external MMM runtime result metadata."""

    request_id: str
    status: MMMRuntimeResultIngestionStatus
    diagnostics_metadata_status: MMMRuntimeDiagnosticsMetadataStatus
    governance_routing_status: MMMRuntimeGovernanceRoutingStatus
    external_run_id: str | None = None
    artifact_handoff: MMMRuntimeArtifactHandoff | None = None
    diagnostics_metadata: MMMRuntimeDiagnosticsMetadata | None = None
    governance_routing_reference: MMMRuntimeGovernanceRoutingReference | None = None
    failure_packet: MMMRuntimeFailurePacket | None = None
    ready_for_governance_review: bool = False
    blocked_reasons: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    issues: list[MMMRuntimeResultIngestionIssueCode] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("request_id")
    @classmethod
    def request_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "request_id cannot be empty"
            raise ValueError(msg)
        return value


FORBIDDEN_MMM_RUNTIME_RESULT_INGESTION_RESULT_FIELD_NAMES = _FORBIDDEN_RESULT_FIELD_NAMES
