"""Tests for readiness checks."""

from datetime import date, timedelta

from mip.workflows.intake import (
    BusinessObjective,
    BusinessObjectiveType,
    DataAvailabilityProfile,
    FeasibilityStatus,
    evaluate_objective_feasibility,
)
from mip.workflows.readiness.checks import ReadinessCheckCode, run_readiness_checks
from mip.workflows.readiness.profile import DatasetProfile, DetectedTimeGrain, profile_from_records


def _weekly_rows(count: int = 12, **extra: object) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(count):
        row: dict[str, object] = {
            "date": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "spend": 100,
            "conversions": 10,
        }
        row.update(extra)
        rows.append(row)
    return rows


def _healthy_profile(**extra: object) -> DatasetProfile:
    return profile_from_records(_weekly_rows(12, **extra))


def test_too_few_rows_emits_blocker() -> None:
    profile = profile_from_records(_weekly_rows(3))
    results = run_readiness_checks(profile)
    assert any(result.code == ReadinessCheckCode.TOO_FEW_ROWS for result in results)


def test_missing_date_emits_blocker() -> None:
    profile = profile_from_records([{"spend": 1, "conversions": 2}] * 12)
    results = run_readiness_checks(profile)
    assert any(result.code == ReadinessCheckCode.MISSING_DATE_FIELD for result in results)


def test_unknown_time_grain_emits_warning() -> None:
    profile = profile_from_records(
        [{"date": "not-a-date", "spend": 1, "conversions": 2}] * 12
    )
    results = run_readiness_checks(profile)
    assert any(result.code == ReadinessCheckCode.UNKNOWN_TIME_GRAIN for result in results)


def test_irregular_time_grain_emits_warning() -> None:
    irregular_dates = [
        "2025-01-01",
        "2025-01-02",
        "2025-01-05",
        "2025-01-20",
        "2025-01-22",
        "2025-02-10",
        "2025-02-12",
        "2025-03-01",
        "2025-03-04",
        "2025-03-18",
        "2025-03-20",
        "2025-04-02",
    ]
    rows = [
        {"date": date_value, "spend": 1, "conversions": 2}
        for date_value in irregular_dates
    ]
    profile = profile_from_records(rows)
    assert profile.time_grain == DetectedTimeGrain.IRREGULAR
    results = run_readiness_checks(profile)
    assert any(result.code == ReadinessCheckCode.IRREGULAR_TIME_GRAIN for result in results)


def test_short_history_emits_warning() -> None:
    profile = _healthy_profile()
    profile = profile.model_copy(update={"history_weeks": 20})
    results = run_readiness_checks(profile)
    assert any(result.code == ReadinessCheckCode.TOO_SHORT_HISTORY for result in results)


def test_high_missingness_emits_warning() -> None:
    rows = _weekly_rows(10)
    for index in range(8):
        rows[index]["conversions"] = None
    profile = profile_from_records(rows)
    results = run_readiness_checks(profile)
    assert any(
        result.code == ReadinessCheckCode.MISSING_VALUES and result.field_name == "conversions"
        for result in results
    )


def test_missing_required_fields_from_feasibility_emit_blockers() -> None:
    profile = _healthy_profile()
    feasibility = evaluate_objective_feasibility(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        DataAvailabilityProfile(available_fields={"date", "spend"}),
    )
    results = run_readiness_checks(profile, feasibility)
    assert any(result.code == ReadinessCheckCode.MISSING_REQUIRED_FIELD for result in results)


def test_missing_recommended_fields_from_feasibility_emit_warnings() -> None:
    profile = _healthy_profile()
    feasibility = evaluate_objective_feasibility(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        DataAvailabilityProfile(available_fields={"date", "spend", "conversions"}),
    )
    results = run_readiness_checks(profile, feasibility)
    assert any(
        result.code == ReadinessCheckCode.MISSING_RECOMMENDED_FIELD for result in results
    )


def test_blocked_feasibility_emits_objective_not_feasible_blocker() -> None:
    profile = _healthy_profile()
    feasibility = evaluate_objective_feasibility(
        BusinessObjective(objective_type=BusinessObjectiveType.AWARENESS),
        DataAvailabilityProfile(available_fields={"date", "spend", "conversions"}),
    )
    results = run_readiness_checks(profile, feasibility)
    assert any(result.code == ReadinessCheckCode.OBJECTIVE_NOT_FEASIBLE for result in results)


def test_diagnostic_only_feasibility_emits_diagnostic_only_warning() -> None:
    profile = _healthy_profile()
    feasibility = evaluate_objective_feasibility(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        DataAvailabilityProfile(available_fields={"date", "conversions"}),
    )
    assert feasibility.status == FeasibilityStatus.DIAGNOSTIC_ONLY
    results = run_readiness_checks(profile, feasibility)
    assert any(result.code == ReadinessCheckCode.DIAGNOSTIC_ONLY for result in results)


def test_ready_dataset_emits_ready_info() -> None:
    profile = _healthy_profile(channel="search")
    profile = profile.model_copy(
        update={
            "history_weeks": 60,
            "time_grain": DetectedTimeGrain.WEEKLY,
            "has_channel_breakdown": True,
        }
    )
    results = run_readiness_checks(profile)
    assert any(result.code == ReadinessCheckCode.READY for result in results)
