"""Dataset profiling from tabular records."""

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from enum import StrEnum
from statistics import median

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.workflows.intake.availability import DataAvailabilityProfile

_DATE_CANDIDATES: tuple[str, ...] = ("date", "week", "day", "month", "ds")
_GEO_CANDIDATES: tuple[str, ...] = ("geo", "region", "dma", "state", "market", "country")
_CHANNEL_CANDIDATES: tuple[str, ...] = ("channel", "media_channel", "platform")
_PRODUCT_CANDIDATES: tuple[str, ...] = ("product", "business_unit", "segment")
_CAMPAIGN_CANDIDATES: tuple[str, ...] = ("campaign", "campaign_id", "strategy", "tactic")

_DATE_FORMATS: tuple[str, ...] = (
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%m/%d/%Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%dT%H:%M:%S",
)


def _normalize_field_name(value: str) -> str:
    return value.strip().lower()


class DetectedTimeGrain(StrEnum):
    """Inferred cadence of observations in a dataset."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    IRREGULAR = "irregular"
    UNKNOWN = "unknown"


class DatasetProfile(ContractBaseModel):
    """Structural profile of a tabular dataset."""

    available_fields: set[str]
    row_count: int
    date_field: str | None = None
    time_grain: DetectedTimeGrain = DetectedTimeGrain.UNKNOWN
    history_weeks: int | None = None
    geo_field: str | None = None
    channel_field: str | None = None
    product_field: str | None = None
    campaign_field: str | None = None
    has_geo_breakdown: bool = False
    has_channel_breakdown: bool = False
    has_product_breakdown: bool = False
    has_campaign_breakdown: bool = False
    missingness_by_field: dict[str, float] = Field(default_factory=dict)
    distinct_counts: dict[str, int] = Field(default_factory=dict)
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

    @field_validator("row_count")
    @classmethod
    def row_count_non_negative(cls, value: int) -> int:
        if value < 0:
            msg = "row_count must be non-negative"
            raise ValueError(msg)
        return value

    @field_validator(
        "date_field",
        "geo_field",
        "channel_field",
        "product_field",
        "campaign_field",
    )
    @classmethod
    def optional_field_names_normalized(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = _normalize_field_name(value)
        if not normalized:
            msg = "field names cannot be empty when provided"
            raise ValueError(msg)
        return normalized

    @field_validator("missingness_by_field")
    @classmethod
    def missingness_in_range(cls, value: dict[str, float]) -> dict[str, float]:
        for rate in value.values():
            if rate < 0 or rate > 1:
                msg = "missingness values must be between 0 and 1"
                raise ValueError(msg)
        return value

    @field_validator("distinct_counts")
    @classmethod
    def distinct_counts_non_negative(cls, value: dict[str, int]) -> dict[str, int]:
        if any(count < 0 for count in value.values()):
            msg = "distinct counts must be non-negative"
            raise ValueError(msg)
        return value

    @field_validator("notes")
    @classmethod
    def notes_not_empty(cls, value: list[str]) -> list[str]:
        if any(not note.strip() for note in value):
            msg = "notes cannot contain empty strings"
            raise ValueError(msg)
        return value


def profile_from_records(records: Sequence[Mapping[str, object]]) -> DatasetProfile:
    """Build a structural dataset profile from in-memory records."""
    if not records:
        msg = "records cannot be empty"
        raise ValueError(msg)

    normalized_records = [_normalize_record(record) for record in records]
    available_fields = set().union(*normalized_records)
    row_count = len(normalized_records)

    date_field = _detect_field(_DATE_CANDIDATES, available_fields)
    geo_field = _detect_field(_GEO_CANDIDATES, available_fields)
    channel_field = _detect_field(_CHANNEL_CANDIDATES, available_fields)
    product_field = _detect_field(_PRODUCT_CANDIDATES, available_fields)
    campaign_field = _detect_field(_CAMPAIGN_CANDIDATES, available_fields)

    missingness_by_field = _compute_missingness(normalized_records, available_fields)
    distinct_counts = _compute_distinct_counts(normalized_records, available_fields)

    time_grain, history_weeks = _infer_time_metadata(normalized_records, date_field)

    return DatasetProfile(
        available_fields=available_fields,
        row_count=row_count,
        date_field=date_field,
        time_grain=time_grain,
        history_weeks=history_weeks,
        geo_field=geo_field,
        channel_field=channel_field,
        product_field=product_field,
        campaign_field=campaign_field,
        has_geo_breakdown=_has_breakdown(geo_field, distinct_counts),
        has_channel_breakdown=_has_breakdown(channel_field, distinct_counts),
        has_product_breakdown=_has_breakdown(product_field, distinct_counts),
        has_campaign_breakdown=_has_breakdown(campaign_field, distinct_counts),
        missingness_by_field=missingness_by_field,
        distinct_counts=distinct_counts,
    )


def profile_to_availability(profile: DatasetProfile) -> DataAvailabilityProfile:
    """Map a dataset profile to a declared availability profile for feasibility."""
    grain = profile.time_grain
    time_grain = None if _grain_is_unknown(grain) else _grain_as_string(grain)
    return DataAvailabilityProfile(
        available_fields=set(profile.available_fields),
        time_grain=time_grain,
        geo_grain=profile.geo_field,
        history_weeks=profile.history_weeks,
        has_channel_breakdown=profile.has_channel_breakdown,
        has_geo_breakdown=profile.has_geo_breakdown,
        has_product_breakdown=profile.has_product_breakdown,
        has_campaign_breakdown=profile.has_campaign_breakdown,
        notes=list(profile.notes),
    )


def _normalize_record(record: Mapping[str, object]) -> dict[str, object]:
    return {_normalize_field_name(str(key)): value for key, value in record.items()}


def _detect_field(candidates: tuple[str, ...], fields: set[str]) -> str | None:
    for candidate in candidates:
        if candidate in fields:
            return candidate
    return None


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and not value.strip():
        return True
    return False


def _compute_missingness(
    records: Sequence[dict[str, object]],
    fields: set[str],
) -> dict[str, float]:
    if not records:
        return {}
    missingness: dict[str, float] = {}
    row_count = len(records)
    for field_name in sorted(fields):
        missing_count = sum(1 for record in records if _is_missing(record.get(field_name)))
        missingness[field_name] = missing_count / row_count
    return missingness


def _distinct_key(value: object) -> str:
    return repr(value)


def _compute_distinct_counts(
    records: Sequence[dict[str, object]],
    fields: set[str],
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for field_name in sorted(fields):
        seen: set[str] = set()
        for record in records:
            if field_name in record and not _is_missing(record[field_name]):
                seen.add(_distinct_key(record[field_name]))
        counts[field_name] = len(seen)
    return counts


def _has_breakdown(field_name: str | None, distinct_counts: dict[str, int]) -> bool:
    if field_name is None:
        return False
    return distinct_counts.get(field_name, 0) > 1


def _parse_date(value: object) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        for fmt in _DATE_FORMATS:
            try:
                return datetime.strptime(text, fmt).date()
            except ValueError:
                continue
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None
    return None


def _infer_time_metadata(
    records: Sequence[dict[str, object]],
    date_field: str | None,
) -> tuple[DetectedTimeGrain, int | None]:
    if date_field is None:
        return DetectedTimeGrain.UNKNOWN, None

    parsed_dates = sorted(
        {
            parsed
            for record in records
            if (parsed := _parse_date(record.get(date_field))) is not None
        }
    )
    if not parsed_dates:
        return DetectedTimeGrain.UNKNOWN, None

    if len(parsed_dates) == 1:
        return DetectedTimeGrain.UNKNOWN, 1

    span_days = (parsed_dates[-1] - parsed_dates[0]).days
    history_weeks = max(1, span_days // 7)

    diffs = [
        (parsed_dates[index + 1] - parsed_dates[index]).days
        for index in range(len(parsed_dates) - 1)
    ]
    median_diff = median(diffs)

    if 0 < median_diff <= 2:
        time_grain = DetectedTimeGrain.DAILY
    elif 5 <= median_diff <= 9:
        time_grain = DetectedTimeGrain.WEEKLY
    elif 25 <= median_diff <= 35:
        time_grain = DetectedTimeGrain.MONTHLY
    else:
        time_grain = DetectedTimeGrain.IRREGULAR

    return time_grain, history_weeks


def _grain_is_unknown(grain: DetectedTimeGrain | str) -> bool:
    return grain == DetectedTimeGrain.UNKNOWN or grain == DetectedTimeGrain.UNKNOWN.value


def _grain_as_string(grain: DetectedTimeGrain | str) -> str:
    if isinstance(grain, str):
        return grain
    return grain.value
