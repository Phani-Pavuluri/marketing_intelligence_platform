"""GeoX experiment config draft schema."""

from pydantic import field_validator

from mip.contracts.base import ContractBaseModel
from mip.workflows.configs.base import ConfigDraftMetadata

PRE_PERIOD_PLACEHOLDER = "TBD: pre_period"
TEST_PERIOD_PLACEHOLDER = "TBD: test_period"
CONTROLS_PLACEHOLDER = "TBD: controls"
EXCLUSIONS_PLACEHOLDER = "TBD: geo_exclusions"


class GeoXConfigDraft(ContractBaseModel):
    """Governed draft configuration for GeoX experiment workflows."""

    metadata: ConfigDraftMetadata
    outcome_field: str | None = None
    date_field: str | None = None
    pre_period_field: str = PRE_PERIOD_PLACEHOLDER
    test_period_field: str = TEST_PERIOD_PLACEHOLDER
    treatment_unit_field: str | None = None
    spend_field: str | None = None
    channel_field: str | None = None
    controls_placeholder: str = CONTROLS_PLACEHOLDER
    exclusions_placeholder: str = EXCLUSIONS_PLACEHOLDER

    @field_validator(
        "pre_period_field",
        "test_period_field",
        "controls_placeholder",
        "exclusions_placeholder",
    )
    @classmethod
    def placeholders_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "placeholder fields cannot be empty"
            raise ValueError(msg)
        return value
