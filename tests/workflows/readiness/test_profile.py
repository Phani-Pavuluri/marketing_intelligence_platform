"""Tests for dataset profiling."""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from mip.workflows.readiness.profile import (
    DetectedTimeGrain,
    profile_from_records,
    profile_to_availability,
)


def _weekly_rows(
    count: int = 12,
    *,
    start: date | None = None,
    **extra: object,
) -> list[dict[str, object]]:
    base = start or date(2025, 1, 1)
    rows: list[dict[str, object]] = []
    for index in range(count):
        row: dict[str, object] = {
            "date": (base + timedelta(days=7 * index)).isoformat(),
            "spend": 100 + index,
            "conversions": 10 + index,
        }
        row.update(extra)
        rows.append(row)
    return rows


def test_empty_records_raise_value_error() -> None:
    with pytest.raises(ValueError, match="records cannot be empty"):
        profile_from_records([])


def test_field_names_normalize_lowercase_stripped() -> None:
    profile = profile_from_records([{" Spend ": 1, "DATE": "2025-01-01"}])
    assert profile.available_fields == {"spend", "date"}


def test_row_count_computed() -> None:
    profile = profile_from_records(_weekly_rows(12))
    assert profile.row_count == 12


def test_date_field_detected_from_date() -> None:
    profile = profile_from_records(_weekly_rows(3))
    assert profile.date_field == "date"


def test_date_field_detected_from_week() -> None:
    rows = [
        {"week": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(), "spend": 1}
        for index in range(3)
    ]
    profile = profile_from_records(rows)
    assert profile.date_field == "week"


def test_geo_field_detected_from_dma() -> None:
    profile = profile_from_records([{"date": "2025-01-01", "dma": "nyc", "spend": 1}])
    assert profile.geo_field == "dma"


def test_channel_field_detected_from_channel() -> None:
    profile = profile_from_records([{"date": "2025-01-01", "channel": "search", "spend": 1}])
    assert profile.channel_field == "channel"


def test_product_field_detected_from_product() -> None:
    profile = profile_from_records([{"date": "2025-01-01", "product": "saas", "spend": 1}])
    assert profile.product_field == "product"


def test_campaign_field_detected_from_campaign() -> None:
    profile = profile_from_records([{"date": "2025-01-01", "campaign": "q1", "spend": 1}])
    assert profile.campaign_field == "campaign"


def test_missingness_computed_for_none_and_empty_string() -> None:
    rows: list[dict[str, object]] = [
        {"date": "2025-01-01", "spend": 100, "conversions": 10},
        {"date": "2025-01-08", "spend": None, "conversions": ""},
    ]
    profile = profile_from_records(rows)
    assert profile.missingness_by_field["spend"] == 0.5
    assert profile.missingness_by_field["conversions"] == 0.5


def test_distinct_counts_computed() -> None:
    rows = [
        {"date": "2025-01-01", "channel": "search"},
        {"date": "2025-01-08", "channel": "social"},
        {"date": "2025-01-15", "channel": "search"},
    ]
    profile = profile_from_records(rows)
    assert profile.distinct_counts["channel"] == 2


def test_breakdown_flags_true_only_when_distinct_count_gt_one() -> None:
    single = profile_from_records([{"date": "2025-01-01", "channel": "search"}])
    assert single.has_channel_breakdown is False

    multi = profile_from_records(
        [
            {"date": "2025-01-01", "channel": "search"},
            {"date": "2025-01-08", "channel": "social"},
        ]
    )
    assert multi.has_channel_breakdown is True


def test_weekly_time_grain_inferred_from_weekly_dates() -> None:
    profile = profile_from_records(_weekly_rows(6))
    assert profile.time_grain == DetectedTimeGrain.WEEKLY


def test_daily_time_grain_inferred_from_daily_dates() -> None:
    rows = [
        {"date": (date(2025, 1, 1) + timedelta(days=index)).isoformat(), "spend": 1}
        for index in range(6)
    ]
    profile = profile_from_records(rows)
    assert profile.time_grain == DetectedTimeGrain.DAILY


def test_unknown_time_grain_when_no_parseable_date() -> None:
    profile = profile_from_records(
        [
            {"spend": 1, "conversions": 2},
            {"spend": 2, "conversions": 3},
        ]
    )
    assert profile.time_grain == DetectedTimeGrain.UNKNOWN
    assert profile.date_field is None


def test_profile_to_availability_maps_fields_and_flags() -> None:
    profile = profile_from_records(
        [
            {"date": "2025-01-01", "channel": "search", "geo": "us", "spend": 1},
            {"date": "2025-01-08", "channel": "social", "geo": "uk", "spend": 2},
        ]
    )
    availability = profile_to_availability(profile)
    assert "spend" in availability.available_fields
    assert availability.has_channel_breakdown is True
    assert availability.has_geo_breakdown is True


def test_profile_rejects_invalid_missingness() -> None:
    from mip.workflows.readiness.profile import DatasetProfile

    with pytest.raises(ValidationError, match="missingness values"):
        DatasetProfile(
            available_fields={"date"},
            row_count=1,
            missingness_by_field={"date": 1.5},
        )
