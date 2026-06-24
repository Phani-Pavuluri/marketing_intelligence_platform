"""MMM workflow config draft schema."""

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.workflows.configs.base import ConfigDraftMetadata


class MMMConfigDraft(ContractBaseModel):
    """Governed draft configuration for MMM-oriented workflows."""

    metadata: ConfigDraftMetadata
    outcome_field: str | None = None
    spend_field: str | None = None
    date_field: str | None = None
    channel_field: str | None = None
    geo_field: str | None = None
    product_field: str | None = None
    campaign_field: str | None = None
    controls: list[str] = Field(default_factory=list)
    time_grain: str | None = None
    history_weeks: int | None = None

    @field_validator("controls")
    @classmethod
    def controls_not_empty_strings(cls, value: list[str]) -> list[str]:
        if any(not control.strip() for control in value):
            msg = "controls cannot contain empty strings"
            raise ValueError(msg)
        return value
