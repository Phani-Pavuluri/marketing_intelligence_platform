"""Estimand and time-window contracts."""

from datetime import datetime

from pydantic import Field, ValidationInfo, field_validator

from mip.contracts.base import ContractBaseModel
from mip.contracts.enums import CausalQuantity


class TimeWindow(ContractBaseModel):
    """Inclusive analysis window with ordered bounds."""

    start: datetime
    end: datetime

    @field_validator("end")
    @classmethod
    def end_after_start(cls, end: datetime, info: ValidationInfo) -> datetime:
        start = info.data.get("start")
        if start is not None and end <= start:
            msg = "end must be after start"
            raise ValueError(msg)
        return end


class Estimand(ContractBaseModel):
    """Explicit target quantity for an engine output or evidence record."""

    target_metric: str
    causal_quantity: CausalQuantity
    unit: str
    time_window: TimeWindow
    treatment_definition: str
    control_definition: str | None = None
    aggregation_level: str
    scope: dict[str, str | list[str]] = Field(default_factory=dict)
    allowed_claims: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)

    @field_validator(
        "target_metric",
        "unit",
        "treatment_definition",
        "aggregation_level",
    )
    @classmethod
    def non_empty_required_strings(cls, value: str) -> str:
        if not value.strip():
            msg = "field cannot be empty"
            raise ValueError(msg)
        return value
