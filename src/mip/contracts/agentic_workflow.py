"""Governed agentic workflow metadata contracts (P8b)."""

from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel

MAX_AGENT_RETRY_ATTEMPTS = 3

_FORBIDDEN_MODEL_FIELD_NAMES = frozenset(
    {
        "api_key",
        "secret",
        "raw_rows",
        "generated_answer",
        "final_response",
        "autonomous_execution_result",
    }
)

_DEFAULT_FORBIDDEN_CLAIM_TOPICS = (
    "roi",
    "causal_lift",
    "optimal_mix",
    "budget_optimization",
    "power_mde",
    "matched_markets",
    "treatment_control_assignment",
    "decision_approval",
    "model_promotion",
)

_FORBIDDEN_CLAIM_FRAGMENTS = (
    "roi is",
    "highest roi",
    "causal lift",
    "lift estimate",
    "optimal mix",
    "budget recommendation",
    "budget optimization",
    "power result",
    "mde result",
    "matched markets",
    "treatment assignment",
    "control assignment",
    "decision approval",
    "model promotion",
    "autonomous execution",
)


class AgentRole(StrEnum):
    """Governed specialist agent roles."""

    INTAKE_ROUTING = "intake_routing"
    DATA_READINESS = "data_readiness"
    COLD_START_ADVISORY = "cold_start_advisory"
    MMM_SPECIALIST = "mmm_specialist"
    GEOX_EXPERIMENT_SPECIALIST = "geox_experiment_specialist"
    CALIBRATION_SIGNAL_SPECIALIST = "calibration_signal_specialist"
    FAILURE_RECOVERY = "failure_recovery"
    EVALUATOR_VALIDATOR = "evaluator_validator"
    FEATURE_STORE_EXPLORER_DEFERRED = "feature_store_explorer_deferred"
    ML_ENGINEERING_DEFERRED = "ml_engineering_deferred"
    RESEARCH_SCOUT_DEFERRED = "research_scout_deferred"
    DATA_CONNECTOR_DEFERRED = "data_connector_deferred"
    PRIVACY_SECURITY_DEFERRED = "privacy_security_deferred"
    PRODUCT_UX_GUIDE_DEFERRED = "product_ux_guide_deferred"


class AgentLifecycleStatus(StrEnum):
    """Lifecycle status for an agent role definition."""

    PLANNED = "planned"
    AVAILABLE = "available"
    DEFERRED = "deferred"
    BLOCKED = "blocked"
    RETIRED = "retired"


class AgentAuthorityLevel(StrEnum):
    """Authority level for an agent role."""

    EXPLAIN_ONLY = "explain_only"
    DIAGNOSE_AND_RECOMMEND = "diagnose_and_recommend"
    VALIDATE_AND_BLOCK = "validate_and_block"
    EXECUTE_SAFE_DETERMINISTIC_STEP_LATER = "execute_safe_deterministic_step_later"
    HUMAN_APPROVAL_REQUIRED = "human_approval_required"


class AgentWorkflowType(StrEnum):
    """Workflow types agents may reason about."""

    INTAKE = "intake"
    DATA_PROFILING = "data_profiling"
    COLD_START_ADVISORY = "cold_start_advisory"
    MMM_READINESS = "mmm_readiness"
    GEOX_READINESS = "geox_readiness"
    CALIBRATION_MAPPING = "calibration_mapping"
    DECISION_REVIEW = "decision_review"
    LLM_EXPLANATION = "llm_explanation"
    FAILURE_RECOVERY = "failure_recovery"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


class AgentRunStatus(StrEnum):
    """Status for an agent run manifest."""

    NOT_STARTED = "not_started"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"
    NEEDS_USER_INPUT = "needs_user_input"
    NEEDS_HUMAN_APPROVAL = "needs_human_approval"
    CANCELLED = "cancelled"


class AgentFailureSeverity(StrEnum):
    """Severity for an agent failure packet."""

    INFO = "info"
    WARNING = "warning"
    RECOVERABLE = "recoverable"
    BLOCKING = "blocking"
    CRITICAL = "critical"


class AgentRetryEligibility(StrEnum):
    """Whether and how a failed step may be retried."""

    NOT_RETRYABLE = "not_retryable"
    RETRY_AFTER_USER_INPUT = "retry_after_user_input"
    RETRY_AFTER_CONFIG_FIX = "retry_after_config_fix"
    RETRY_SAME_STEP_SAFE = "retry_same_step_safe"
    RETRY_REQUIRES_HUMAN_APPROVAL = "retry_requires_human_approval"
    FUTURE_RUNTIME_ONLY = "future_runtime_only"


class AgentActionType(StrEnum):
    """Controlled action types agents may recommend."""

    ASK_USER_FOR_MISSING_DATA = "ask_user_for_missing_data"
    ASK_USER_TO_CONFIRM_MAPPING = "ask_user_to_confirm_mapping"
    ASK_USER_TO_CONFIRM_ASSUMPTION = "ask_user_to_confirm_assumption"
    ROUTE_TO_ALTERNATIVE_WORKFLOW = "route_to_alternative_workflow"
    RERUN_READINESS = "rerun_readiness"
    RERUN_VALIDATION = "rerun_validation"
    RETRY_SAME_STEP = "retry_same_step"
    ESCALATE_TO_HUMAN = "escalate_to_human"
    CREATE_ISSUE_LATER = "create_issue_later"
    BLOCKED_ACTION = "blocked_action"


class AgentValidationStatus(StrEnum):
    """Result of evaluator/validator checks."""

    PASSED = "passed"
    WARNING = "warning"
    BLOCKED = "blocked"
    NEEDS_REVISION = "needs_revision"
    NOT_APPLICABLE = "not_applicable"


def default_forbidden_claim_topics() -> tuple[str, ...]:
    """Default forbidden claim topics for agent permission boundaries."""
    return _DEFAULT_FORBIDDEN_CLAIM_TOPICS


def _assert_no_forbidden_claims(*text_fields: str) -> None:
    combined = " ".join(text_fields).lower()
    for fragment in _FORBIDDEN_CLAIM_FRAGMENTS:
        if fragment in combined:
            msg = f"agentic workflow contract must not contain forbidden claim: {fragment}"
            raise ValueError(msg)


def _collect_text(*groups: list[str] | None) -> list[str]:
    collected: list[str] = []
    for group in groups:
        if group:
            collected.extend(group)
    return collected


def _reject_forbidden_field_names(model: ContractBaseModel) -> None:
    for name in type(model).model_fields:
        if name in _FORBIDDEN_MODEL_FIELD_NAMES:
            msg = f"forbidden field name on agentic contract: {name}"
            raise ValueError(msg)


def _enum_value(value: object) -> str:
    if hasattr(value, "value"):
        return str(getattr(value, "value"))
    return str(value)


class AgentCapability(ContractBaseModel):
    """Describes what an agent may do without granting runtime execution authority."""

    capability_id: str
    name: str
    description: str | None = None
    allowed_workflow_types: list[AgentWorkflowType] = Field(default_factory=list)
    allowed_actions: list[AgentActionType] = Field(default_factory=list)
    blocked_actions: list[AgentActionType] = Field(default_factory=list)
    requires_human_approval: bool = False
    warnings: list[str] = Field(default_factory=list)

    @field_validator("capability_id", "name")
    @classmethod
    def capability_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "capability_id and name cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def capability_rules(self) -> "AgentCapability":
        _reject_forbidden_field_names(self)
        _assert_no_forbidden_claims(
            self.name,
            self.description or "",
            *_collect_text(self.warnings),
        )
        return self


class AgentPermissionBoundary(ContractBaseModel):
    """Explicit allow/deny boundaries for an agent role."""

    boundary_id: str
    agent_role: AgentRole
    authority_level: AgentAuthorityLevel
    allowed_inputs: list[str] = Field(default_factory=list)
    blocked_inputs: list[str] = Field(default_factory=list)
    allowed_outputs: list[str] = Field(default_factory=list)
    blocked_outputs: list[str] = Field(default_factory=list)
    forbidden_claim_topics: list[str] = Field(
        default_factory=lambda: list(_DEFAULT_FORBIDDEN_CLAIM_TOPICS)
    )
    requires_trust_report_for_decision_claims: bool = True
    requires_human_approval_for_execution: bool = False
    warnings: list[str] = Field(default_factory=list)

    @field_validator("boundary_id")
    @classmethod
    def boundary_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "boundary_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def boundary_rules(self) -> "AgentPermissionBoundary":
        _reject_forbidden_field_names(self)
        _assert_no_forbidden_claims(*_collect_text(self.warnings))
        return self


class AgentRoleDefinition(ContractBaseModel):
    """Governed definition for a specialist agent role."""

    role_id: str
    role: AgentRole
    display_name: str
    status: AgentLifecycleStatus = AgentLifecycleStatus.PLANNED
    purpose: str
    capabilities: list[AgentCapability] = Field(default_factory=list)
    permission_boundary: AgentPermissionBoundary
    deferred_trigger_conditions: list[str] = Field(default_factory=list)
    owns_execution: bool = False
    authoritative_for_measurement: bool = False
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("role_id", "display_name", "purpose")
    @classmethod
    def role_definition_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "role_id, display_name, and purpose cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def role_definition_rules(self) -> "AgentRoleDefinition":
        _reject_forbidden_field_names(self)
        if self.owns_execution:
            msg = "agent roles must not own execution in P8b"
            raise ValueError(msg)
        if self.authoritative_for_measurement:
            msg = "agent roles must not be authoritative_for_measurement in P8b"
            raise ValueError(msg)
        role_value = str(self.role.value) if hasattr(self.role, "value") else str(self.role)
        if (
            role_value.endswith("_deferred")
            and str(self.status) != AgentLifecycleStatus.DEFERRED.value
        ):
            msg = "deferred agent roles must have deferred lifecycle status"
            raise ValueError(msg)
        if (
            str(self.status) == AgentLifecycleStatus.DEFERRED.value
            and not self.deferred_trigger_conditions
        ):
            msg = "deferred agent roles require deferred_trigger_conditions"
            raise ValueError(msg)
        _assert_no_forbidden_claims(
            self.display_name,
            self.purpose,
            *_collect_text(self.warnings, self.deferred_trigger_conditions),
        )
        return self


class AgentTask(ContractBaseModel):
    """Planned controlled task for an agent (not autonomous execution)."""

    task_id: str
    role: AgentRole
    workflow_type: AgentWorkflowType
    user_request_summary: str
    input_reference_ids: list[str] = Field(default_factory=list)
    expected_output_type: str = "governed_summary"
    allowed_actions: list[AgentActionType] = Field(default_factory=list)
    blocked_actions: list[AgentActionType] = Field(default_factory=list)
    requires_human_approval: bool = False
    created_at: datetime

    @field_validator("task_id", "user_request_summary")
    @classmethod
    def task_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "task_id and user_request_summary cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def task_rules(self) -> "AgentTask":
        _reject_forbidden_field_names(self)
        _assert_no_forbidden_claims(self.user_request_summary)
        return self


class AgentStepManifest(ContractBaseModel):
    """Single step record within an agent run manifest."""

    step_id: str
    task_id: str
    workflow_type: AgentWorkflowType
    step_name: str
    status: AgentRunStatus = AgentRunStatus.NOT_STARTED
    input_reference_ids: list[str] = Field(default_factory=list)
    artifact_reference_ids: list[str] = Field(default_factory=list)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("step_id", "task_id", "step_name")
    @classmethod
    def step_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "step identifiers and step_name cannot be empty"
            raise ValueError(msg)
        return value


class AgentRunManifest(ContractBaseModel):
    """Records what an agent run attempted without raw rows by default."""

    run_id: str
    task_id: str
    role: AgentRole
    workflow_type: AgentWorkflowType
    status: AgentRunStatus = AgentRunStatus.NOT_STARTED
    steps: list[AgentStepManifest] = Field(default_factory=list)
    input_reference_ids: list[str] = Field(default_factory=list)
    artifact_reference_ids: list[str] = Field(default_factory=list)
    package_metadata: dict[str, str] = Field(default_factory=dict)
    started_at: datetime | None = None
    ended_at: datetime | None = None
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)

    @field_validator("run_id", "task_id")
    @classmethod
    def run_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "run_id and task_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def run_manifest_rules(self) -> "AgentRunManifest":
        _reject_forbidden_field_names(self)
        if "raw_rows" in self.package_metadata:
            msg = "run manifest must not store raw_rows in package_metadata"
            raise ValueError(msg)
        return self


class AgentFailurePacket(ContractBaseModel):
    """Structured failure capture for recovery planning."""

    failure_id: str
    run_id: str
    task_id: str
    step_id: str | None = None
    role: AgentRole
    workflow_type: AgentWorkflowType
    severity: AgentFailureSeverity = AgentFailureSeverity.BLOCKING
    error_type: str
    error_message: str
    stack_trace: str | None = None
    typed_validation_failures: list[str] = Field(default_factory=list)
    safe_context: str | None = None
    allowed_retry_actions: list[AgentActionType] = Field(default_factory=list)
    blocked_retry_actions: list[AgentActionType] = Field(default_factory=list)
    affected_artifact_ids: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("failure_id", "run_id", "task_id", "error_type", "error_message")
    @classmethod
    def failure_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "failure identifiers and error fields cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def failure_packet_rules(self) -> "AgentFailurePacket":
        _reject_forbidden_field_names(self)
        _assert_no_forbidden_claims(
            self.error_type,
            self.error_message,
            self.safe_context or "",
            self.stack_trace or "",
            *_collect_text(self.typed_validation_failures),
        )
        return self


class AgentResolutionPlan(ContractBaseModel):
    """Proposed safe recovery plan (does not execute recovery)."""

    resolution_plan_id: str
    failure_id: str
    diagnosis: str
    recommended_user_questions: list[str] = Field(default_factory=list)
    safe_next_steps: list[str] = Field(default_factory=list)
    blocked_next_steps: list[str] = Field(default_factory=list)
    retry_eligibility: AgentRetryEligibility = AgentRetryEligibility.NOT_RETRYABLE
    requires_human_approval: bool = False
    expected_downstream_impact: str | None = None
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("resolution_plan_id", "failure_id", "diagnosis")
    @classmethod
    def resolution_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "resolution identifiers and diagnosis cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def resolution_plan_rules(self) -> "AgentResolutionPlan":
        _reject_forbidden_field_names(self)
        _assert_no_forbidden_claims(
            self.diagnosis,
            self.expected_downstream_impact or "",
            *_collect_text(
                self.recommended_user_questions,
                self.safe_next_steps,
                self.blocked_next_steps,
                self.warnings,
            ),
        )
        return self


class AgentValidationReport(ContractBaseModel):
    """Evaluator/validator output before user-facing decision-supporting delivery."""

    validation_report_id: str
    task_id: str
    run_id: str | None = None
    role: AgentRole = AgentRole.EVALUATOR_VALIDATOR
    validation_status: AgentValidationStatus = AgentValidationStatus.NOT_APPLICABLE
    claim_compliance_findings: list[str] = Field(default_factory=list)
    forbidden_claim_findings: list[str] = Field(default_factory=list)
    missing_evidence_labels: list[str] = Field(default_factory=list)
    trust_report_requirement_status: str = "unknown"
    readiness_consistency_status: str = "not_checked"
    calibration_consistency_status: str = "not_checked"
    final_allowed_outputs: list[str] = Field(default_factory=list)
    final_blocked_outputs: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("validation_report_id", "task_id")
    @classmethod
    def validation_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "validation_report_id and task_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def validation_report_rules(self) -> "AgentValidationReport":
        _reject_forbidden_field_names(self)
        _assert_no_forbidden_claims(
            *_collect_text(
                self.claim_compliance_findings,
                self.forbidden_claim_findings,
                self.final_allowed_outputs,
                self.final_blocked_outputs,
                self.warnings,
            ),
        )
        return self


class AgentHandoffPacket(ContractBaseModel):
    """Typed handoff between governed agent roles."""

    handoff_id: str
    from_role: AgentRole
    to_role: AgentRole
    task_id: str
    reason: str
    summary: str
    input_reference_ids: list[str] = Field(default_factory=list)
    artifact_reference_ids: list[str] = Field(default_factory=list)
    allowed_actions: list[AgentActionType] = Field(default_factory=list)
    blocked_actions: list[AgentActionType] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("handoff_id", "task_id", "reason", "summary")
    @classmethod
    def handoff_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "handoff identifiers, reason, and summary cannot be empty"
            raise ValueError(msg)
        return value


class AgentRetryPolicy(ContractBaseModel):
    """Safe retry rules for a workflow type (no infinite retries)."""

    retry_policy_id: str
    workflow_type: AgentWorkflowType
    retry_eligibility: AgentRetryEligibility = AgentRetryEligibility.NOT_RETRYABLE
    max_retry_attempts: int = 0
    allowed_retry_actions: list[AgentActionType] = Field(default_factory=list)
    blocked_retry_actions: list[AgentActionType] = Field(default_factory=list)
    requires_user_confirmation: bool = True
    requires_human_approval: bool = False
    warnings: list[str] = Field(default_factory=list)

    @field_validator("retry_policy_id")
    @classmethod
    def retry_policy_id_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "retry_policy_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def retry_policy_rules(self) -> "AgentRetryPolicy":
        if self.max_retry_attempts > MAX_AGENT_RETRY_ATTEMPTS:
            msg = f"max_retry_attempts cannot exceed {MAX_AGENT_RETRY_ATTEMPTS}"
            raise ValueError(msg)
        if self.max_retry_attempts < 0:
            msg = "max_retry_attempts cannot be negative"
            raise ValueError(msg)
        return self


class AgentEscalationPolicy(ContractBaseModel):
    """When to escalate to human review for a workflow type."""

    escalation_policy_id: str
    workflow_type: AgentWorkflowType
    trigger_conditions: list[str] = Field(default_factory=list)
    escalation_target: str = "human_reviewer"
    requires_human_approval: bool = True
    blocked_until_resolved: bool = True
    warnings: list[str] = Field(default_factory=list)

    @field_validator("escalation_policy_id", "escalation_target")
    @classmethod
    def escalation_ids_not_blank(cls, value: str) -> str:
        if not value.strip():
            msg = "escalation identifiers cannot be empty"
            raise ValueError(msg)
        return value
