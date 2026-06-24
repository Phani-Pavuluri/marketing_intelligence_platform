"""Workflow run status and summary artifacts."""

from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.workflows.configs.geox import GeoXConfigDraft
from mip.workflows.configs.mmm import MMMConfigDraft
from mip.workflows.intake.feasibility import ObjectiveFeasibilityReport
from mip.workflows.intake.objectives import BusinessObjective
from mip.workflows.readiness.profile import DatasetProfile
from mip.workflows.readiness.report import DataReadinessReport


class WorkflowRunStatus(StrEnum):
    """Overall outcome of a local deterministic workflow run."""

    COMPLETED = "completed"
    COMPLETED_WITH_WARNINGS = "completed_with_warnings"
    BLOCKED = "blocked"


class WorkflowRunSummary(ContractBaseModel):
    """Single summary bundle for a local workflow run."""

    objective: BusinessObjective
    profile: DatasetProfile
    feasibility: ObjectiveFeasibilityReport
    readiness: DataReadinessReport
    config_draft: MMMConfigDraft | GeoXConfigDraft
    status: WorkflowRunStatus
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    recommended_next_questions: list[str] = Field(default_factory=list)
    recommended_fixes: list[str] = Field(default_factory=list)
    narrative_summary: str

    @field_validator("narrative_summary")
    @classmethod
    def narrative_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "narrative_summary cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator(
        "warnings",
        "blocking_reasons",
        "recommended_next_questions",
        "recommended_fixes",
    )
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "summary string lists cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def blocked_requires_reasons(self) -> "WorkflowRunSummary":
        if self.status == WorkflowRunStatus.BLOCKED and not self.blocking_reasons:
            msg = "blocked workflow run requires blocking_reasons"
            raise ValueError(msg)
        return self
