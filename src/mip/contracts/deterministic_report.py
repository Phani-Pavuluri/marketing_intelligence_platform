"""Deterministic report envelope contracts for governed workflow summaries."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel

DETERMINISTIC_REPORT_SCHEMA_VERSION = "deterministic_report_v1"

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "channel_roi",
    "response_curve",
    "optimizer_output",
    "matched_markets",
    "treatment_assignment",
    "causal_lift",
    "power_mde",
    "budget_optimization_result",
    "mmm_fitted",
)


class ReportType(StrEnum):
    """Deterministic report categories."""

    COLD_START_ADVISORY = "cold_start_advisory"
    READINESS_ASSESSMENT = "readiness_assessment"
    CALIBRATION_MAPPING = "calibration_mapping"
    INTAKE_ROUTING = "intake_routing"
    GOVERNANCE_BLOCKED_CLAIM = "governance_blocked_claim"
    FIXTURE_INVENTORY = "fixture_inventory"


class EvidenceMode(StrEnum):
    """Evidence tier carried by a deterministic report."""

    BUSINESS_PROFILE_ONLY = "business_profile_only"
    READINESS_ONLY = "readiness_only"
    DIAGNOSTIC_CANDIDATE = "diagnostic_candidate"
    ROUTING_ONLY = "routing_only"
    EDUCATIONAL_ONLY = "educational_only"
    UNSUPPORTED = "unsupported"


class GovernanceStatus(StrEnum):
    """Governed outcome status for a deterministic report."""

    ADVISORY_ONLY = "advisory_only"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    CANDIDATE = "candidate"
    NEEDS_MORE_DATA = "needs_more_data"
    BLOCKED = "blocked"
    INCOMPATIBLE = "incompatible"
    UNSUPPORTED = "unsupported"


class FindingSeverity(StrEnum):
    """Severity for structured report findings."""

    INFO = "info"
    WARNING = "warning"
    BLOCKING = "blocking"


class ReportFinding(ContractBaseModel):
    """Structured finding within a deterministic report."""

    finding_id: str
    severity: FindingSeverity
    message: str
    field_ref: str | None = None


class ArtifactReference(ContractBaseModel):
    """Provenance reference for fixtures, workflow outputs, or reports."""

    artifact_id: str
    artifact_type: str
    source_workflow: str
    source_fixture_id_or_payload_ref: str
    source_commit_or_version: str
    created_at: datetime
    governance_status: GovernanceStatus
    evidence_mode: EvidenceMode
    allowed_downstream_uses: list[str] = Field(default_factory=list)
    forbidden_downstream_uses: list[str] = Field(default_factory=list)
    content_hash_optional: str | None = None
    path_or_uri_optional: str | None = None

    @field_validator("artifact_id", "artifact_type", "source_workflow")
    @classmethod
    def artifact_fields_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "artifact reference fields cannot be empty"
            raise ValueError(msg)
        return value


class DeterministicReportEnvelope(ContractBaseModel):
    """Stable envelope wrapping governed deterministic workflow outputs."""

    report_id: str
    report_type: ReportType
    schema_version: str = DETERMINISTIC_REPORT_SCHEMA_VERSION
    source_workflow: str
    source_input_ref: ArtifactReference
    generated_at: datetime
    evidence_mode: EvidenceMode
    governance_status: GovernanceStatus
    summary: str
    findings: list[ReportFinding] = Field(default_factory=list)
    recommended_next_steps: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)
    blocked_claims: list[str] = Field(default_factory=list)
    allowed_downstream_uses: list[str] = Field(default_factory=list)
    forbidden_downstream_uses: list[str] = Field(default_factory=list)
    artifact_refs: list[ArtifactReference] = Field(default_factory=list)
    workflow_payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("report_id", "summary", "source_workflow")
    @classmethod
    def required_text_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "report_id, summary, and source_workflow cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("schema_version")
    @classmethod
    def schema_version_must_match(cls, value: str) -> str:
        if value != DETERMINISTIC_REPORT_SCHEMA_VERSION:
            msg = f"schema_version must be {DETERMINISTIC_REPORT_SCHEMA_VERSION}"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def envelope_governance_rules(self) -> DeterministicReportEnvelope:
        combined = " ".join(
            [
                self.summary,
                " ".join(self.forbidden_downstream_uses),
                " ".join(finding.message for finding in self.findings),
            ]
        ).lower()
        for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
            if fragment in combined:
                msg = (
                    f"deterministic report envelope must not contain "
                    f"forbidden claim fragment: {fragment}"
                )
                raise ValueError(msg)
        if self.governance_status in {
            GovernanceStatus.BLOCKED,
            GovernanceStatus.INCOMPATIBLE,
            GovernanceStatus.NEEDS_MORE_DATA,
        } and not (self.blocked_claims or self.missing_data or self.findings):
            msg = (
                "blocked, incompatible, or needs_more_data reports require "
                "blocked_claims, missing_data, or findings"
            )
            raise ValueError(msg)
        return self


def default_package_version_label() -> str:
    """Return a stable package label for artifact provenance."""
    return "mip-local-dev"


def utc_now() -> datetime:
    """Return current UTC time for report envelopes."""
    return datetime.now(tz=UTC)
