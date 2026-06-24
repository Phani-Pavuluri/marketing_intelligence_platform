"""Workflow intent types for LLM safety classification."""

from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel

_PRODUCTION_ACTIONS = frozenset(
    {
        "production_automation",
        "execute_production",
        "recommend_production",
        "publish_production",
    }
)


class WorkflowIntent(StrEnum):
    """Classified user request intent for orchestration routing."""

    EXPLAIN_TRUST_REPORT = "explain_trust_report"
    EXPLAIN_EXPERIMENT_EVIDENCE = "explain_experiment_evidence"
    EXPLAIN_CALIBRATION_READINESS = "explain_calibration_readiness"
    EXPLAIN_DECISION_SURFACE = "explain_decision_surface"
    PLAN_MEASUREMENT_WORKFLOW = "plan_measurement_workflow"
    ANSWER_REGISTRY_QUESTION = "answer_registry_question"
    DRAFT_MMM_CONFIG = "draft_mmm_config"
    DRAFT_EXPERIMENT_CONFIG = "draft_experiment_config"
    EVALUATE_DATA_READINESS = "evaluate_data_readiness"
    SURFACE_MEASUREMENT_GAP = "surface_measurement_gap"
    EXPLORE_SCENARIO = "explore_scenario"
    GENERATE_REPORT = "generate_report"
    UNSUPPORTED = "unsupported"


class IntentRiskLevel(StrEnum):
    """Risk tier for a classified workflow intent."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


class IntentClassification(ContractBaseModel):
    """Deterministic safety classification for a user request."""

    intent: WorkflowIntent
    risk_level: IntentRiskLevel
    requires_human_review: bool
    allowed_actions: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    reason: str

    @field_validator("reason")
    @classmethod
    def reason_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "reason cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def review_and_block_rules(self) -> "IntentClassification":
        if self.risk_level == IntentRiskLevel.BLOCKED and not self.blocked_actions:
            msg = "blocked risk level requires blocked_actions"
            raise ValueError(msg)

        if self.requires_human_review:
            forbidden = _PRODUCTION_ACTIONS.intersection(self.allowed_actions)
            if forbidden:
                msg = "human review intents cannot allow production execution actions"
                raise ValueError(msg)

        return self
