"""Decision surface contracts for MMM and planning."""

from datetime import datetime

from pydantic import Field, field_validator, model_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.enums import ArtifactStatus, CausalQuantity, DecisionSurfaceType
from mip.contracts.estimand import Estimand

_DIAGNOSTIC_SURFACE_TYPES = frozenset(
    {
        DecisionSurfaceType.DIAGNOSTIC_CURVE,
        DecisionSurfaceType.DECOMPOSITION,
    }
)


class DecisionSurface(ContractBaseModel):
    """Certified or diagnostic model surface for planning and optimization."""

    surface_id: str
    model_id: str
    surface_type: DecisionSurfaceType
    decision_estimand: Estimand
    supported_scenarios: list[str] = Field(default_factory=list)
    constraints_supported: list[str] = Field(default_factory=list)
    certification_status: ArtifactStatus
    reliability_scorecard_id: str | None = None
    artifact_fingerprint: str
    created_at: datetime
    warnings: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)

    @field_validator("surface_id", "model_id", "artifact_fingerprint")
    @classmethod
    def non_empty_ids(cls, value: str) -> str:
        if not value.strip():
            msg = "ID and fingerprint fields cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def surface_certification_rules(self) -> "DecisionSurface":
        if (
            self.surface_type == DecisionSurfaceType.FULL_PANEL_DELTA_MU
            and self.decision_estimand.causal_quantity != CausalQuantity.DELTA_MU
        ):
            msg = "full_panel_delta_mu surface requires delta_mu estimand"
            raise ValueError(msg)

        if self.certification_status == ArtifactStatus.CERTIFIED:
            if self.surface_type != DecisionSurfaceType.FULL_PANEL_DELTA_MU:
                msg = "certified surfaces must be full_panel_delta_mu"
                raise ValueError(msg)
            if not self.reliability_scorecard_id:
                msg = "certified surfaces require reliability_scorecard_id"
                raise ValueError(msg)

        if (
            self.surface_type in _DIAGNOSTIC_SURFACE_TYPES
            and self.certification_status == ArtifactStatus.CERTIFIED
        ):
            msg = "diagnostic curves and decomposition cannot be certified"
            raise ValueError(msg)

        return self
