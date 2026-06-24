"""Declared data availability profiles for feasibility checks."""

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.workflows.intake.requirements import DataFieldRequirement


def _normalize_field_name(value: str) -> str:
    return value.strip().lower()


class DataAvailabilityProfile(ContractBaseModel):
    """Declared fields and metadata available from user-provided data."""

    available_fields: set[str]
    time_grain: str | None = None
    geo_grain: str | None = None
    history_weeks: int | None = None
    has_channel_breakdown: bool | None = None
    has_geo_breakdown: bool | None = None
    has_product_breakdown: bool | None = None
    has_campaign_breakdown: bool | None = None
    notes: list[str] = Field(default_factory=list)

    @field_validator("available_fields", mode="before")
    @classmethod
    def normalize_available_fields(cls, value: set[str] | list[str]) -> set[str]:
        if not value:
            msg = "available_fields cannot be empty"
            raise ValueError(msg)
        normalized = {_normalize_field_name(field) for field in value}
        if any(not field for field in normalized):
            msg = "available_fields cannot contain empty field names"
            raise ValueError(msg)
        return normalized

    @field_validator("time_grain", "geo_grain")
    @classmethod
    def optional_grain_not_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            msg = "time_grain and geo_grain must be non-empty when provided"
            raise ValueError(msg)
        return value

    @field_validator("history_weeks")
    @classmethod
    def history_weeks_positive(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            msg = "history_weeks must be positive when provided"
            raise ValueError(msg)
        return value

    @field_validator("notes")
    @classmethod
    def notes_not_empty(cls, value: list[str]) -> list[str]:
        if any(not note.strip() for note in value):
            msg = "notes cannot contain empty strings"
            raise ValueError(msg)
        return value


def has_field_or_alias(profile: DataAvailabilityProfile, requirement: DataFieldRequirement) -> bool:
    """Return whether a required field is present directly or via accepted alias."""
    candidates = {_normalize_field_name(requirement.field_name), *(
        _normalize_field_name(alias) for alias in requirement.accepted_aliases
    )}
    return bool(candidates.intersection(profile.available_fields))
