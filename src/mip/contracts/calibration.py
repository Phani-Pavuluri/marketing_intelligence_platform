"""Calibration signal contracts linking experiment evidence to models."""

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.enums import CompatibilityStatus, ConfidenceTier
from mip.contracts.evidence import DiagnosticSummary


class CalibrationSignal(ContractBaseModel):
    """Explicit mapping from experiment evidence to an MMM calibration target."""

    calibration_id: str
    source_evidence_id: str
    target_model_id: str
    compatibility_status: CompatibilityStatus
    mapping_type: str
    lift_scale: str
    channel_mapping: dict[str, str] = Field(default_factory=dict)
    geography_mapping: dict[str, str] = Field(default_factory=dict)
    time_mapping: dict[str, str] = Field(default_factory=dict)
    weight: float = Field(ge=0.0, le=1.0)
    uncertainty: float | None = Field(default=None, ge=0.0)
    freshness_decay: float = Field(default=1.0, ge=0.0, le=1.0)
    allowed_usage: list[str] = Field(default_factory=list)
    blocked_usage: list[str] = Field(default_factory=list)
    diagnostics: DiagnosticSummary
    confidence_tier: ConfidenceTier

    @field_validator("calibration_id", "source_evidence_id", "target_model_id")
    @classmethod
    def ids_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "ID fields cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def compatibility_and_tier_rules(self) -> "CalibrationSignal":
        if self.compatibility_status == CompatibilityStatus.INCOMPATIBLE and self.weight != 0:
            msg = "incompatible calibration signal must have weight 0"
            raise ValueError(msg)

        if self.confidence_tier == ConfidenceTier.DECISION_READY:
            if self.compatibility_status != CompatibilityStatus.COMPATIBLE:
                msg = "decision_ready calibration requires compatible status"
                raise ValueError(msg)
            if not self.diagnostics.passed:
                msg = "decision_ready calibration requires passing diagnostics"
                raise ValueError(msg)
            if self.weight <= 0:
                msg = "decision_ready calibration requires weight > 0"
                raise ValueError(msg)

        return self
