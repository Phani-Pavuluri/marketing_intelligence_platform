"""Shared config draft types and validation."""

from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.workflows.intake.objectives import BusinessObjectiveType
from mip.workflows.intake.requirements import WorkflowType


class DraftConfigStatus(StrEnum):
    """Whether a config draft may be handed to an engine adapter."""

    DRAFTABLE = "draftable"
    DRAFTABLE_WITH_WARNINGS = "draftable_with_warnings"
    DIAGNOSTIC_ONLY = "diagnostic_only"
    BLOCKED = "blocked"


class ConfigDraftValidationReport(ContractBaseModel):
    """Validation summary for a generated config draft."""

    status: DraftConfigStatus
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    production_eligible: bool = False

    @field_validator("warnings", "blocking_reasons")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "warnings and blocking_reasons cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def blocked_requires_reasons(self) -> "ConfigDraftValidationReport":
        if self.status == DraftConfigStatus.BLOCKED and not self.blocking_reasons:
            msg = "blocked status requires blocking_reasons"
            raise ValueError(msg)
        return self


class ConfigDraftMetadata(ContractBaseModel):
    """Shared metadata attached to every config draft."""

    objective_type: BusinessObjectiveType
    workflow_type: WorkflowType
    status: DraftConfigStatus
    warnings: list[str] = Field(default_factory=list)
    blocking_reasons: list[str] = Field(default_factory=list)
    source_fields: list[str] = Field(default_factory=list)
    generated_marker: str
    production_eligible: bool = False
    validation: ConfigDraftValidationReport

    @field_validator("generated_marker")
    @classmethod
    def marker_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "generated_marker cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("warnings", "blocking_reasons")
    @classmethod
    def string_lists_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "warnings and blocking_reasons cannot contain empty strings"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def metadata_consistency(self) -> "ConfigDraftMetadata":
        if self.status == DraftConfigStatus.BLOCKED and not self.blocking_reasons:
            msg = "blocked draft requires blocking_reasons"
            raise ValueError(msg)
        if self.validation.status != self.status:
            msg = "validation status must match draft status"
            raise ValueError(msg)
        return self
