"""Agent answerability state machine and decision contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.deterministic_report import (
    ArtifactReference,
    DeterministicReportEnvelope,
)


class AgentAnswerabilityState(StrEnum):
    """Top-level answerability classification for a user request."""

    ANSWERABLE_FROM_REGISTERED_ARTIFACT = "answerable_from_registered_artifact"
    ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT = (
        "answerable_from_deterministic_tool_output"
    )
    NEEDS_CORE_DIAGNOSTIC_OR_ML = "needs_core_diagnostic_or_ml"
    NEEDS_USER_INPUT_OR_DATA = "needs_user_input_or_data"
    BLOCKED_BY_CLAIM_BOUNDARY = "blocked_by_claim_boundary"


class AgentAnswerMode(StrEnum):
    """Secondary response mode derived from answerability state."""

    DIRECT_REPORT_EXPLANATION = "direct_report_explanation"
    DETERMINISTIC_TOOL_REPORT = "deterministic_tool_report"
    ADVISORY_ONLY_GUIDANCE = "advisory_only_guidance"
    MISSING_DATA_REQUEST = "missing_data_request"
    ROUTE_TO_MMM = "route_to_mmm"
    ROUTE_TO_GEOX = "route_to_geox"
    ROUTE_TO_CALIBRATION = "route_to_calibration"
    ROUTE_TO_READINESS = "route_to_readiness"
    ROUTE_TO_DECISION_SURFACE = "route_to_decision_surface"
    BLOCKED_UNSUPPORTED_CLAIM = "blocked_unsupported_claim"
    TOOL_UNAVAILABLE_FALLBACK = "tool_unavailable_fallback"
    OUT_OF_SCOPE = "out_of_scope"


class AnswerabilityEvidenceLevel(StrEnum):
    """Evidence tier required or available for an answerability decision."""

    GENERAL_KNOWLEDGE = "general_knowledge"
    BUSINESS_PROFILE_ONLY = "business_profile_only"
    SYNTHETIC_FIXTURE = "synthetic_fixture"
    DETERMINISTIC_WORKFLOW_REPORT = "deterministic_workflow_report"
    CALIBRATION_CANDIDATE = "calibration_candidate"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    CORE_MMM_REQUIRED = "core_mmm_required"
    CORE_GEOX_REQUIRED = "core_geox_required"
    CERTIFIED_DECISION_SURFACE_REQUIRED = "certified_decision_surface_required"
    UNSUPPORTED = "unsupported"


class RequestedClaimType(StrEnum):
    """Governed claim categories for answerability evaluation."""

    GENERAL_MARKETING_ADVICE = "general_marketing_advice"
    TRACKING_OR_DATA_READINESS = "tracking_or_data_readiness"
    COLD_START_ADVISORY = "cold_start_advisory"
    MEASUREMENT_READINESS = "measurement_readiness"
    EXPERIMENT_CALIBRATION = "experiment_calibration"
    CAUSAL_LIFT = "causal_lift"
    ROI = "roi"
    BUDGET_OPTIMIZATION = "budget_optimization"
    SCENARIO_PLANNING = "scenario_planning"
    RESPONSE_CURVE = "response_curve"
    MATCHED_MARKET_DESIGN = "matched_market_design"
    POWER_MDE = "power_mde"
    TREATMENT_ASSIGNMENT = "treatment_assignment"
    PRODUCTION_RECOMMENDATION = "production_recommendation"


class RoutingConfidence(StrEnum):
    """Confidence that the answerability state routing is correct — not claim truth."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ToolAvailabilityStatus(ContractBaseModel):
    """Availability snapshot for a deterministic or core tool."""

    tool_name: str
    tool_type: str
    available: bool = True
    supports_claim_types: list[str] = Field(default_factory=list)
    unsupported_claim_types: list[str] = Field(default_factory=list)
    required_input_contract: str | None = None
    failure_mode: str | None = None
    fallback_answer_mode: str | None = None

    @field_validator("tool_name", "tool_type")
    @classmethod
    def required_strings_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "tool_name and tool_type cannot be empty"
            raise ValueError(msg)
        return value


class AvailableReportSummary(ContractBaseModel):
    """Governed report snapshot for answerability evaluation."""

    report_id: str
    report_type: str
    governance_status: str
    evidence_mode: str
    blocked_claims: list[str] = Field(default_factory=list)
    allowed_downstream_uses: list[str] = Field(default_factory=list)
    forbidden_downstream_uses: list[str] = Field(default_factory=list)
    missing_data: list[str] = Field(default_factory=list)

    @field_validator("report_id", "report_type", "governance_status", "evidence_mode")
    @classmethod
    def summary_fields_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "report summary identity fields cannot be empty"
            raise ValueError(msg)
        return value


class AgentAnswerabilityRequest(ContractBaseModel):
    """Structured evaluator input — must not rely on natural-language question matching."""

    requested_claim_type: RequestedClaimType
    user_intent: str = ""
    available_reports: list[AvailableReportSummary] = Field(default_factory=list)
    available_tools: list[ToolAvailabilityStatus] = Field(default_factory=list)
    missing_inputs: list[str] = Field(default_factory=list)
    assert_claim_authorized_by_available_artifacts: bool = False

    @field_validator("user_intent")
    @classmethod
    def user_intent_is_metadata_only(cls, value: str) -> str:
        return value


class AgentAnswerabilityDecision(ContractBaseModel):
    """Typed answerability outcome for agents and future LLM explanation gates."""

    decision_id: str
    state: AgentAnswerabilityState
    user_intent: str
    requested_claim_type: RequestedClaimType
    answer_mode: AgentAnswerMode | None = None
    evidence_level: AnswerabilityEvidenceLevel
    source_artifact_ids: list[str] = Field(default_factory=list)
    available_report_ids: list[str] = Field(default_factory=list)
    required_tool: str | None = None
    required_core_engine: str | None = None
    missing_inputs: list[str] = Field(default_factory=list)
    blocked_claims: list[str] = Field(default_factory=list)
    allowed_response_scope: list[str] = Field(default_factory=list)
    forbidden_response_scope: list[str] = Field(default_factory=list)
    fallback_message: str | None = None
    confidence_in_routing: RoutingConfidence = RoutingConfidence.HIGH
    artifact_refs: list[ArtifactReference] = Field(default_factory=list)

    @field_validator("decision_id")
    @classmethod
    def decision_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "decision_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def blocked_state_requires_scope(self) -> AgentAnswerabilityDecision:
        if self.state == AgentAnswerabilityState.BLOCKED_BY_CLAIM_BOUNDARY:
            if not (self.blocked_claims or self.forbidden_response_scope):
                msg = (
                    "blocked_by_claim_boundary decisions require blocked_claims "
                    "or forbidden_response_scope"
                )
                raise ValueError(msg)
        return self


class AgentCapabilityEvalCase(ContractBaseModel):
    """Structured eval fixture — user_question is documentation only."""

    case_id: str
    user_question: str
    request: AgentAnswerabilityRequest
    expected_state: AgentAnswerabilityState
    expected_answer_mode: AgentAnswerMode | None = None
    expected_evidence_level: AnswerabilityEvidenceLevel | None = None
    expected_blocked_claims: list[str] = Field(default_factory=list)
    forbidden_phrases: list[str] = Field(default_factory=list)
    expected_safe_fallback: str | None = None

    @field_validator("case_id", "user_question")
    @classmethod
    def eval_case_fields_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "case_id and user_question cannot be empty"
            raise ValueError(msg)
        return value


def available_report_from_envelope(
    envelope: DeterministicReportEnvelope,
) -> AvailableReportSummary:
    """Build a governed report summary from a deterministic report envelope."""
    return AvailableReportSummary(
        report_id=envelope.report_id,
        report_type=str(envelope.report_type),
        governance_status=str(envelope.governance_status),
        evidence_mode=str(envelope.evidence_mode),
        blocked_claims=list(envelope.blocked_claims),
        allowed_downstream_uses=list(envelope.allowed_downstream_uses),
        forbidden_downstream_uses=list(envelope.forbidden_downstream_uses),
        missing_data=list(envelope.missing_data),
    )


__all__ = [
    "AgentAnswerabilityDecision",
    "AgentAnswerabilityRequest",
    "AgentAnswerabilityState",
    "AgentAnswerMode",
    "AgentCapabilityEvalCase",
    "AnswerabilityEvidenceLevel",
    "AvailableReportSummary",
    "RequestedClaimType",
    "RoutingConfidence",
    "ToolAvailabilityStatus",
    "available_report_from_envelope",
]
