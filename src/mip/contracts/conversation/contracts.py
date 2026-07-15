"""Typed, provider-free contracts for the conversational control plane."""
# ruff: noqa: E501

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import ConfigDict, Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel

SCHEMA_VERSION = "conversation_control_plane_v1"


class EventType(StrEnum):
    USER_MESSAGE = "user_message"
    STARTER_PROMPT_SELECTED = "starter_prompt_selected"
    SAMPLE_USE_CASE_SELECTED = "sample_use_case_selected"
    ANALYZE_MY_DATA_SELECTED = "analyze_my_data_selected"
    FILE_UPLOADED = "file_uploaded"
    COLUMN_MAPPING_CONFIRMED = "column_mapping_confirmed"
    BUSINESS_GOAL_CONFIRMED = "business_goal_confirmed"
    WORKFLOW_ACTION_SELECTED = "workflow_action_selected"
    ARTIFACT_OPENED = "artifact_opened"
    DASHBOARD_FILTER_CHANGED = "dashboard_filter_changed"
    REPORT_OPENED = "report_opened"
    CAPABILITY_EXECUTION_REQUESTED = "capability_execution_requested"
    RESET_REQUESTED = "reset_requested"
    ASSISTANT_RESPONSE = "assistant_response"
    SYSTEM_RESULT = "system_result"


class InterpretationSource(StrEnum):
    TYPED_UI_ACTION = "typed_ui_action"
    DETERMINISTIC_RULE = "deterministic_rule"
    PENDING_CLARIFICATION = "pending_clarification"
    CONSTRAINED_LLM = "constrained_llm"


class EntryMode(StrEnum):
    EMPTY = "empty"
    SAMPLE = "sample"
    UPLOAD = "upload"
    LIVE = "live"


class DialogueResolutionStatus(StrEnum):
    NONE = "none"
    PENDING = "pending"
    PARTIALLY_RESOLVED = "partially_resolved"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"
    SUPERSEDED = "superseded"


class CapabilityStatus(StrEnum):
    AVAILABLE = "available"
    FIXTURE_BACKED = "fixture_backed"
    READINESS_ONLY = "readiness_only"
    EXTERNAL_EXECUTION = "external_execution"
    BLOCKED = "blocked"
    FUTURE_INTEGRATION = "future_integration"


class ExecutionMode(StrEnum):
    FIXTURE = "fixture"
    UPLOADED_SESSION = "uploaded_session"
    EXTERNAL = "external"
    FUTURE_ENGINE = "future_engine"


class VerificationStatus(StrEnum):
    PASSED = "passed"
    BLOCKED = "blocked"
    REWRITTEN = "rewritten"
    REQUIRES_CLARIFICATION = "requires_clarification"
    REQUIRES_HUMAN_REVIEW = "requires_human_review"


class JsonContract(ContractBaseModel):
    model_config = ConfigDict(extra="forbid", use_enum_values=True, validate_assignment=True)

    @field_validator("schema_version")
    @classmethod
    def version_is_current(cls, value: str) -> str:
        if value != SCHEMA_VERSION:
            raise ValueError(f"schema_version must be {SCHEMA_VERSION}")
        return value

    schema_version: str = SCHEMA_VERSION


class InteractionEvent(JsonContract):
    event_id: str
    session_id: str
    conversation_id: str
    workspace_id: str
    event_type: EventType
    timestamp: datetime
    source_view: str
    source_component: str
    requested_action: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    active_artifact_id: str | None = None
    correlation_id: str | None = None
    causation_id: str | None = None

    @field_validator(
        "event_id",
        "session_id",
        "conversation_id",
        "workspace_id",
        "source_view",
        "source_component",
    )
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("identity values must not be empty")
        return value

    @field_validator("timestamp")
    @classmethod
    def timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")
        return value.astimezone(UTC)


class IntentEnvelope(JsonContract):
    domain: str
    user_goal: str
    intent: str
    requested_action: str | None = None
    candidate_capability_id: str | None = None
    entities: dict[str, str] = Field(default_factory=dict)
    known_inputs: dict[str, Any] = Field(default_factory=dict)
    missing_or_unknown_inputs: list[str] = Field(default_factory=list)
    confidence: float
    clarification_required: bool = False
    clarification_targets: list[str] = Field(default_factory=list)
    interpretation_source: InterpretationSource

    @field_validator("confidence")
    @classmethod
    def bounded_confidence(cls, value: float) -> float:
        if not 0 <= value <= 1:
            raise ValueError("confidence must be between 0 and 1")
        return value

    @model_validator(mode="after")
    def clarification_targets_required(self) -> "IntentEnvelope":
        if self.clarification_required and not self.clarification_targets:
            raise ValueError("clarification targets are required")
        return self


class WorkspaceContext(JsonContract):
    session_id: str
    conversation_id: str
    workspace_id: str
    entry_mode: EntryMode = EntryMode.EMPTY
    business_goal: str | None = None
    planning_horizon: str | None = None
    active_domain: str | None = None
    active_capability_id: str | None = None
    active_view: str | None = None
    active_artifact_id: str | None = None
    active_dataset_id: str | None = None
    active_use_case_id: str | None = None
    active_workflow_node_id: str | None = None
    known_inputs: dict[str, Any] = Field(default_factory=dict)
    missing_inputs: list[str] = Field(default_factory=list)
    confirmed_inputs: dict[str, Any] = Field(default_factory=dict)
    inferred_inputs: dict[str, Any] = Field(default_factory=dict)
    confirmed_column_mappings: dict[str, str] = Field(default_factory=dict)
    uploaded_file_inventory: list[str] = Field(default_factory=list)
    session_artifact_ids: list[str] = Field(default_factory=list)
    available_artifact_ids: list[str] = Field(default_factory=list)
    completed_workflow_node_ids: list[str] = Field(default_factory=list)
    available_workflow_node_ids: list[str] = Field(default_factory=list)
    blocked_workflow_node_ids: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    conversation_summary: str | None = None
    recent_messages: list[str] = Field(default_factory=list)
    execution_mode: ExecutionMode | None = None
    claim_state: str = "unverified"

    @field_validator("session_id", "conversation_id", "workspace_id")
    @classmethod
    def identity_required(cls, value: str) -> str:
        if not value:
            raise ValueError("workspace identity is required")
        return value


class DialogueState(JsonContract):
    original_question: str | None = None
    pending_intent: str | None = None
    pending_capability_id: str | None = None
    selected_domain: str | None = None
    missing_fields: list[str] = Field(default_factory=list)
    clarification_question: str | None = None
    clarification_targets: list[str] = Field(default_factory=list)
    clarification_history: list[str] = Field(default_factory=list)
    resolution_status: DialogueResolutionStatus = DialogueResolutionStatus.NONE

    @model_validator(mode="after")
    def state_is_consistent(self) -> "DialogueState":
        if (
            self.resolution_status
            in {DialogueResolutionStatus.PENDING, DialogueResolutionStatus.PARTIALLY_RESOLVED}
            and not self.clarification_targets
        ):
            raise ValueError("unresolved dialogue requires clarification targets")
        if self.resolution_status == DialogueResolutionStatus.RESOLVED and self.missing_fields:
            raise ValueError("resolved dialogue cannot have missing fields")
        return self


class RequirementConflict(ContractBaseModel):
    field: str
    message: str
    values: list[str] = Field(min_length=1)


class ValidationIssue(ContractBaseModel):
    field: str
    code: str
    message: str


class RequirementGap(JsonContract):
    capability_id: str
    satisfied_requirements: list[str] = Field(default_factory=list)
    inferred_requirements: list[str] = Field(default_factory=list)
    unconfirmed_requirements: list[str] = Field(default_factory=list)
    missing_required_inputs: list[str] = Field(default_factory=list)
    missing_conditional_inputs: list[str] = Field(default_factory=list)
    conflicts: list[RequirementConflict] = Field(default_factory=list)
    invalid_inputs: list[ValidationIssue] = Field(default_factory=list)
    missing_artifacts: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    recommended_clarifications: list[str] = Field(default_factory=list)
    next_allowed_actions: list[str] = Field(default_factory=list)


class CapabilityDescriptor(JsonContract):
    capability_id: str
    capability_version: str
    owner: str
    domain: str
    status: CapabilityStatus
    supported_intents: list[str] = Field(min_length=1)
    supported_event_types: list[EventType] = Field(min_length=1)
    required_inputs: list[str] = Field(default_factory=list)
    conditional_inputs: list[str] = Field(default_factory=list)
    required_artifact_types: list[str] = Field(default_factory=list)
    produced_artifact_types: list[str] = Field(default_factory=list)
    allowed_claims: list[str] = Field(default_factory=list)
    blocked_claims: list[str] = Field(default_factory=list)
    execution_modes: list[ExecutionMode] = Field(min_length=1)
    next_capability_ids: list[str] = Field(default_factory=list)
    workflow_node_ids: list[str] = Field(default_factory=list)
    documentation_retrieval_filters: dict[str, str] = Field(default_factory=dict)
    release_gate: str | None = None


class WorkflowNode(JsonContract):
    node_id: str
    display_name: str
    business_purpose: str
    supported_user_questions: list[str] = Field(min_length=1)
    required_capability_ids: list[str] = Field(min_length=1)
    required_inputs: list[str] = Field(default_factory=list)
    required_artifact_types: list[str] = Field(default_factory=list)
    available_actions: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    display_artifact_types: list[str] = Field(default_factory=list)
    execution_mode: ExecutionMode
    next_valid_node_ids: list[str] = Field(default_factory=list)


class ResolvedArtifact(JsonContract):
    artifact_id: str
    artifact_type: str
    source: str
    execution_mode: ExecutionMode
    dataset_id: str | None = None
    kpi: str | None = None
    time_scope: str | None = None
    geographic_scope: str | None = None
    estimand: str | None = None
    freshness: str | None = None
    compatibility_status: str
    claim_eligibility: list[str] = Field(default_factory=list)
    lineage: list[str] = Field(default_factory=list)
    payload_reference: str | None = None

    @model_validator(mode="after")
    def demo_claim_safety(self) -> "ResolvedArtifact":
        if self.execution_mode == ExecutionMode.FIXTURE and any(
            "production" in claim.lower() for claim in self.claim_eligibility
        ):
            raise ValueError("fixture artifacts cannot claim production evidence")
        return self


class EvidencePacket(JsonContract):
    interaction_event: InteractionEvent
    intent: IntentEnvelope
    workspace_context: WorkspaceContext
    dialogue_state: DialogueState
    active_view: str | None = None
    active_artifact: ResolvedArtifact | None = None
    business_goal: str | None = None
    known_inputs: dict[str, Any] = Field(default_factory=dict)
    missing_inputs: list[str] = Field(default_factory=list)
    requirement_gap: RequirementGap
    selected_capability: CapabilityDescriptor | None = None
    execution_status: str
    resolved_artifacts: list[ResolvedArtifact] = Field(default_factory=list)
    artifact_summaries: list[str] = Field(default_factory=list)
    allowed_claims: list[str] = Field(default_factory=list)
    blocked_claims: list[str] = Field(default_factory=list)
    required_disclosures: list[str] = Field(default_factory=list)
    next_action: str | None = None
    clarification_questions: list[str] = Field(default_factory=list)
    retrieval_context: list[str] = Field(default_factory=list)


class NavigationTarget(ContractBaseModel):
    view: str
    artifact_id: str | None = None
    workflow_node_id: str | None = None


class ResponseContract(JsonContract):
    direct_answer: str
    relevant_context: list[str] = Field(default_factory=list)
    evidence_summary: list[str] = Field(default_factory=list)
    known_inputs: dict[str, Any] = Field(default_factory=dict)
    missing_inputs: list[str] = Field(default_factory=list)
    important_limitation: str | None = None
    next_action: str | None = None
    clarification_questions: list[str] = Field(default_factory=list)
    contextual_follow_ups: list[str] = Field(default_factory=list)
    navigation_target: NavigationTarget | None = None
    active_artifact_reference: str | None = None
    technical_details: list[str] = Field(default_factory=list)
    claim_status: str
    source_references: list[str] = Field(default_factory=list)
    execution_disclosure: str | None = None


class VerificationResult(JsonContract):
    status: VerificationStatus
    violations: list[str] = Field(default_factory=list)
    removed_claims: list[str] = Field(default_factory=list)
    rewritten_fields: list[str] = Field(default_factory=list)
    required_clarifications: list[str] = Field(default_factory=list)
    human_review_reason: str | None = None
    verified_source_references: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def status_requirements(self) -> "VerificationResult":
        if self.status == VerificationStatus.BLOCKED and not self.violations:
            raise ValueError("blocked verification requires violations")
        if self.status == VerificationStatus.REWRITTEN and not self.rewritten_fields:
            raise ValueError("rewritten verification requires rewritten fields")
        if (
            self.status == VerificationStatus.REQUIRES_CLARIFICATION
            and not self.required_clarifications
        ):
            raise ValueError("clarification verification requires targets")
        if self.status == VerificationStatus.REQUIRES_HUMAN_REVIEW and not self.human_review_reason:
            raise ValueError("human review requires a reason")
        return self
