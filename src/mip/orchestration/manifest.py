"""Workflow run manifest contracts and safety checks."""

from __future__ import annotations

import re
from datetime import datetime
from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel

_FORBIDDEN_CLAIM_PHRASES = (
    "actual roi",
    "true roi",
    "incremental lift",
    "causal impact",
    "model result",
    "budget recommendation",
    "autonomous agent executed",
    "llm chose this step",
)

_ALLOWED_ACTION_TYPES = frozenset(
    {
        "parse_input",
        "classify_intent",
        "profile_data",
        "evaluate_feasibility",
        "build_readiness_report",
        "draft_config",
        "build_adapter_input",
        "build_adapter_output_fixture",
        "map_to_governance_artifact",
        "build_trust_report",
        "render_report",
        "request_human_approval",
    }
)


class WorkflowStepStatus(StrEnum):
    """Execution status for a single workflow step."""

    PLANNED = "planned"
    RUNNING = "running"
    COMPLETED = "completed"
    WARNING = "warning"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    REQUIRES_APPROVAL = "requires_approval"


class WorkflowActionType(StrEnum):
    """Deterministic workflow action identifiers."""

    PARSE_INPUT = "parse_input"
    CLASSIFY_INTENT = "classify_intent"
    PROFILE_DATA = "profile_data"
    EVALUATE_FEASIBILITY = "evaluate_feasibility"
    BUILD_READINESS_REPORT = "build_readiness_report"
    DRAFT_CONFIG = "draft_config"
    BUILD_ADAPTER_INPUT = "build_adapter_input"
    BUILD_ADAPTER_OUTPUT_FIXTURE = "build_adapter_output_fixture"
    MAP_TO_GOVERNANCE_ARTIFACT = "map_to_governance_artifact"
    BUILD_TRUST_REPORT = "build_trust_report"
    RENDER_REPORT = "render_report"
    REQUEST_HUMAN_APPROVAL = "request_human_approval"


class HumanApprovalRequirement(StrEnum):
    """Whether a step requires human approval before downstream automation."""

    NOT_REQUIRED = "not_required"
    RECOMMENDED = "recommended"
    REQUIRED = "required"
    BLOCKED_UNTIL_APPROVED = "blocked_until_approved"


class WorkflowBlockReason(ContractBaseModel):
    """Structured reason a workflow step or run was blocked."""

    code: str
    message: str

    @field_validator("code", "message")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "block reason fields cannot be empty"
            raise ValueError(msg)
        return value


class WorkflowArtifactRef(ContractBaseModel):
    """Reference to a governed artifact produced during a workflow run."""

    artifact_type: str
    artifact_id: str
    lineage_marker: str | None = None
    notes: str | None = None

    @field_validator("artifact_type", "artifact_id")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "artifact reference fields cannot be empty"
            raise ValueError(msg)
        return value


class WorkflowStep(ContractBaseModel):
    """Single planned or executed workflow step."""

    step_id: str
    action_type: WorkflowActionType
    status: WorkflowStepStatus
    human_approval_requirement: HumanApprovalRequirement = HumanApprovalRequirement.NOT_REQUIRED
    block_reason: WorkflowBlockReason | None = None
    output_artifacts: list[WorkflowArtifactRef] = Field(default_factory=list)
    completion_note: str | None = None
    warnings: list[str] = Field(default_factory=list)

    @field_validator("step_id")
    @classmethod
    def step_id_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "step_id cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("warnings")
    @classmethod
    def warnings_not_empty_strings(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "warnings cannot contain empty strings"
            raise ValueError(msg)
        return value

    @field_validator("action_type")
    @classmethod
    def action_type_allowed(cls, value: WorkflowActionType) -> WorkflowActionType:
        action = _enum_value(value)
        if action not in _ALLOWED_ACTION_TYPES:
            msg = f"unsupported workflow action type: {action}"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def step_consistency(self) -> WorkflowStep:
        if self.status == WorkflowStepStatus.COMPLETED:
            has_note = self.completion_note and self.completion_note.strip()
            if not self.output_artifacts and not has_note:
                msg = "completed steps require output artifacts or a completion note"
                raise ValueError(msg)
        if self.status == WorkflowStepStatus.BLOCKED and self.block_reason is None:
            msg = "blocked steps require a block reason"
            raise ValueError(msg)
        if self.status == WorkflowStepStatus.REQUIRES_APPROVAL:
            if self.human_approval_requirement == HumanApprovalRequirement.NOT_REQUIRED:
                msg = "requires_approval steps must declare human approval requirement"
                raise ValueError(msg)
        if self.human_approval_requirement in (
            HumanApprovalRequirement.REQUIRED,
            HumanApprovalRequirement.BLOCKED_UNTIL_APPROVED,
        ):
            if self.status not in (
                WorkflowStepStatus.REQUIRES_APPROVAL,
                WorkflowStepStatus.BLOCKED,
                WorkflowStepStatus.WARNING,
                WorkflowStepStatus.COMPLETED,
            ):
                msg = "approval-gated steps must reflect approval state in status"
                raise ValueError(msg)
        return self


def step_requires_approval_gate(step: WorkflowStep) -> bool:
    """Return whether a workflow step is gated by human approval."""
    if step.status == WorkflowStepStatus.REQUIRES_APPROVAL:
        return True
    return step.human_approval_requirement in (
        HumanApprovalRequirement.REQUIRED,
        HumanApprovalRequirement.BLOCKED_UNTIL_APPROVED,
        HumanApprovalRequirement.RECOMMENDED,
    )


class WorkflowPlan(ContractBaseModel):
    """Deterministic workflow plan over governed local steps."""

    plan_id: str
    objective_type: str
    source_config_marker: str | None = None
    planning_mode: str = "deterministic_local"
    steps: list[WorkflowStep]

    @field_validator("plan_id", "objective_type", "planning_mode")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "plan identifier fields cannot be empty"
            raise ValueError(msg)
        return value


class WorkflowRunManifest(ContractBaseModel):
    """Durable record of a governed local workflow run."""

    run_id: str
    created_at: datetime
    source: str
    objective_marker: str
    execution_mode: str = "deterministic_local_no_agent"
    agentic_planning_enabled: bool = False
    plan: WorkflowPlan
    artifact_refs: list[WorkflowArtifactRef] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    completion_note: str = (
        "Deterministic local workflow manifest. No autonomous agent execution occurred."
    )

    @field_validator("run_id", "source", "objective_marker", "execution_mode", "completion_note")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "manifest fields cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("warnings", "blockers")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "warnings and blockers cannot contain empty strings"
            raise ValueError(msg)
        return value


def assert_safe_workflow_manifest(manifest: WorkflowRunManifest) -> None:
    """Raise if manifest text claims forbidden causal, model, or agentic execution."""
    combined = manifest.model_dump_json().lower()
    for phrase in _FORBIDDEN_CLAIM_PHRASES:
        if phrase in combined:
            msg = f"workflow manifest must not include forbidden phrase: {phrase}"
            raise ValueError(msg)
    if _contains_false_production_ready_claim(combined):
        msg = "workflow manifest must not claim production-ready status"
        raise ValueError(msg)


def _contains_false_production_ready_claim(text: str) -> bool:
    for match in re.finditer(r"production[- ]ready", text):
        start = match.start()
        prefix = text[max(0, start - 4) : start]
        if not prefix.endswith("not "):
            return True
    return False


def _enum_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))
