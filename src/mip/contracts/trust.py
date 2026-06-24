"""Trust report contract for tiered, auditable outputs."""

from datetime import datetime

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.enums import ConfidenceTier
from mip.contracts.evidence import DiagnosticSummary


class TrustReport(ContractBaseModel):
    """Trust envelope attached to engine or recommendation outputs."""

    trust_report_id: str
    output_id: str
    output_type: str
    confidence_tier: ConfidenceTier
    evidence_quality: dict[str, float | int | str | bool] = Field(default_factory=dict)
    model_quality: dict[str, float | int | str | bool] = Field(default_factory=dict)
    experiment_quality: dict[str, float | int | str | bool] = Field(default_factory=dict)
    calibration_quality: dict[str, float | int | str | bool] = Field(default_factory=dict)
    optimizer_quality: dict[str, float | int | str | bool] = Field(default_factory=dict)
    uncertainty_summary: dict[str, float | int | str | bool] = Field(default_factory=dict)
    diagnostics: DiagnosticSummary
    assumptions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    trace_uri: str | None = None
    created_at: datetime

    @field_validator("trust_report_id", "output_id", "output_type")
    @classmethod
    def ids_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "ID and output_type fields cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def tier_rules(self) -> "TrustReport":
        if self.confidence_tier == ConfidenceTier.DECISION_READY and not self.diagnostics.passed:
            msg = "decision_ready trust report requires passing diagnostics"
            raise ValueError(msg)

        if self.confidence_tier == ConfidenceTier.BLOCKED:
            if not self.warnings and not self.unsupported_claims:
                msg = "blocked trust report requires warnings or unsupported_claims"
                raise ValueError(msg)

        return self
