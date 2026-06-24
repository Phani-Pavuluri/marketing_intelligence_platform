"""Tests for declared data availability profiles."""

import pytest
from pydantic import ValidationError

from mip.workflows.intake.availability import DataAvailabilityProfile, has_field_or_alias
from mip.workflows.intake.requirements import DataFieldRequirement, DataFieldRole


def test_profile_normalizes_field_names() -> None:
    profile = DataAvailabilityProfile(available_fields={" Spend ", "DATE", "Conversions"})
    assert profile.available_fields == {"spend", "date", "conversions"}


def test_profile_rejects_empty_available_fields() -> None:
    with pytest.raises(ValidationError, match="available_fields cannot be empty"):
        DataAvailabilityProfile(available_fields=set())


def test_profile_rejects_empty_field_name() -> None:
    with pytest.raises(ValidationError, match="empty field names"):
        DataAvailabilityProfile(available_fields={"spend", "  "})


def test_history_weeks_must_be_positive() -> None:
    with pytest.raises(ValidationError, match="history_weeks must be positive"):
        DataAvailabilityProfile(available_fields={"date"}, history_weeks=0)


def test_has_field_or_alias_matches_canonical_field() -> None:
    profile = DataAvailabilityProfile(available_fields={"revenue"})
    requirement = DataFieldRequirement(
        field_name="revenue",
        role=DataFieldRole.REQUIRED,
        description="Revenue outcome",
    )
    assert has_field_or_alias(profile, requirement) is True


def test_has_field_or_alias_matches_alias_case_insensitively() -> None:
    profile = DataAvailabilityProfile(available_fields={"brand_search"})
    requirement = DataFieldRequirement(
        field_name="awareness_kpi",
        role=DataFieldRole.REQUIRED,
        description="Awareness KPI",
        accepted_aliases=["Brand_Search", "reach"],
    )
    assert has_field_or_alias(profile, requirement) is True
