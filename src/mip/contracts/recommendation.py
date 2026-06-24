"""Recommendation contract for explainable, gated actions."""

from datetime import datetime

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.enums import ConfidenceTier, RecommendationType
from mip.contracts.evidence import DiagnosticSummary


class RecommendationContract(ContractBaseModel):
    """Structured recommendation with evidence pointers and explicit limits."""

    recommendation_id: str
    recommendation_type: RecommendationType
    action: dict[str, str | float | int | bool]
    expected_impact: dict[str, float | int | str] = Field(default_factory=dict)
    uncertainty: dict[str, float | int | str] = Field(default_factory=dict)
    evidence_ids: list[str] = Field(default_factory=list)
    calibration_ids: list[str] = Field(default_factory=list)
    decision_surface_ids: list[str] = Field(default_factory=list)
    diagnostics_summary: DiagnosticSummary
    confidence_tier: ConfidenceTier
    risks: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    required_approvals: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    created_at: datetime

    @field_validator("recommendation_id")
    @classmethod
    def recommendation_id_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "recommendation_id cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def recommendation_rules(self) -> "RecommendationContract":
        if self.confidence_tier == ConfidenceTier.DECISION_READY:
            if not self.evidence_ids and not self.decision_surface_ids:
                msg = (
                    "decision_ready recommendation requires at least one "
                    "evidence_id or decision_surface_id"
                )
                raise ValueError(msg)

        if self.recommendation_type == RecommendationType.BUDGET_SHIFT:
            if not self.decision_surface_ids:
                msg = "budget_shift recommendation requires at least one decision_surface_id"
                raise ValueError(msg)

        if self.recommendation_type == RecommendationType.BLOCK_ACTION:
            if self.confidence_tier != ConfidenceTier.BLOCKED:
                msg = "block_action recommendation requires blocked confidence tier"
                raise ValueError(msg)

        if self.confidence_tier == ConfidenceTier.BLOCKED:
            if not self.risks and not self.unsupported_claims:
                msg = "blocked recommendation requires risks or unsupported_claims"
                raise ValueError(msg)

        return self
