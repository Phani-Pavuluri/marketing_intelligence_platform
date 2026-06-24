"""Experiment evidence contracts."""

from datetime import datetime

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.enums import (
    ArtifactStatus,
    ConfidenceTier,
    EvidenceRole,
    ExperimentType,
)
from mip.contracts.estimand import Estimand


class DiagnosticSummary(ContractBaseModel):
    """Structured pass/fail diagnostics from an analytical engine."""

    passed: bool
    warnings: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    metrics: dict[str, float | int | str | bool] = Field(default_factory=dict)

    @model_validator(mode="after")
    def failed_requires_detail(self) -> "DiagnosticSummary":
        if not self.passed and not self.warnings and not self.failures:
            msg = "failed diagnostics must include at least one warning or failure"
            raise ValueError(msg)
        return self


class ExperimentEvidence(ContractBaseModel):
    """Registered experiment result with quality, diagnostics, and tier."""

    evidence_id: str
    experiment_type: ExperimentType
    evidence_role: EvidenceRole
    estimand: Estimand
    estimate: float
    standard_error: float | None = None
    confidence_interval: tuple[float, float] | None = None
    p_value: float | None = None
    randomization_unit: str | None = None
    treatment_units: list[str] = Field(default_factory=list)
    control_units: list[str] = Field(default_factory=list)
    design_diagnostics: DiagnosticSummary
    execution_diagnostics: DiagnosticSummary
    inference_diagnostics: DiagnosticSummary
    quality_score: float = Field(ge=0.0, le=1.0)
    freshness_score: float = Field(ge=0.0, le=1.0)
    confidence_tier: ConfidenceTier
    status: ArtifactStatus = ArtifactStatus.DRAFT
    created_at: datetime
    artifact_uri: str | None = None

    @field_validator("evidence_id")
    @classmethod
    def evidence_id_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "evidence_id cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("confidence_interval")
    @classmethod
    def confidence_interval_ordered(
        cls, value: tuple[float, float] | None
    ) -> tuple[float, float] | None:
        if value is not None and value[0] > value[1]:
            msg = "confidence interval lower bound must be <= upper bound"
            raise ValueError(msg)
        return value

    @field_validator("p_value")
    @classmethod
    def p_value_in_unit_interval(cls, value: float | None) -> float | None:
        if value is not None and not 0.0 <= value <= 1.0:
            msg = "p_value must be between 0 and 1"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def tier_and_status_rules(self) -> "ExperimentEvidence":
        if self.confidence_tier == ConfidenceTier.DECISION_READY:
            for label, diag in (
                ("design", self.design_diagnostics),
                ("execution", self.execution_diagnostics),
                ("inference", self.inference_diagnostics),
            ):
                if not diag.passed:
                    msg = f"decision_ready evidence requires passing {label} diagnostics"
                    raise ValueError(msg)
            if self.status not in (ArtifactStatus.VALIDATED, ArtifactStatus.CERTIFIED):
                msg = (
                    "decision_ready evidence requires status validated or certified"
                )
                raise ValueError(msg)

        if self.status == ArtifactStatus.CERTIFIED and self.confidence_tier in (
            ConfidenceTier.RESEARCH_ONLY,
            ConfidenceTier.BLOCKED,
        ):
            msg = "certified evidence cannot have research_only or blocked confidence tier"
            raise ValueError(msg)

        return self
