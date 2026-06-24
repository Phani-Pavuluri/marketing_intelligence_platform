"""Tests for data readiness reports."""

from datetime import date, timedelta

import pytest
from pydantic import ValidationError

from mip.workflows.intake import (
    BusinessObjective,
    BusinessObjectiveType,
    FeasibilityStatus,
    WorkflowType,
    evaluate_objective_feasibility,
)
from mip.workflows.readiness.profile import profile_from_records, profile_to_availability
from mip.workflows.readiness.report import (
    DataReadinessReport,
    DataReadinessStatus,
    build_data_readiness_report,
    build_readiness_from_records,
)


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


def _long_history_rows() -> list[dict[str, object]]:
    return [
        {
            "date": (date(2024, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "spend": 100,
            "conversions": 10,
            "channel": "search" if index % 2 == 0 else "social",
        }
        for index in range(60)
    ]


def test_blockers_produce_blocked_report() -> None:
    report = build_readiness_from_records(_weekly_rows(3))
    assert report.status == DataReadinessStatus.BLOCKED
    assert report.blocking_reasons


def test_warnings_without_blockers_produce_ready_with_warnings() -> None:
    report = build_readiness_from_records(_weekly_rows(12))
    assert report.status == DataReadinessStatus.READY_WITH_WARNINGS
    assert report.warnings


def test_no_blockers_or_warnings_produce_ready() -> None:
    report = build_readiness_from_records(_long_history_rows())
    assert report.status == DataReadinessStatus.READY
    assert report.summary == "Dataset is ready for the requested workflow."


def test_diagnostic_only_feasibility_produces_diagnostic_only_when_no_blockers() -> None:
    profile = profile_from_records(_long_history_rows())
    availability = profile_to_availability(profile)
    manual_feasibility = evaluate_objective_feasibility(
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
        availability,
    )
    manual_feasibility = manual_feasibility.model_copy(
        update={
            "status": FeasibilityStatus.DIAGNOSTIC_ONLY,
            "missing_required_fields": [],
            "blocking_reasons": [],
            "recommended_workflows": [WorkflowType.DIAGNOSTIC_ONLY],
        }
    )
    report = build_data_readiness_report(profile, manual_feasibility)
    assert report.status == DataReadinessStatus.DIAGNOSTIC_ONLY
    assert report.summary == "Dataset is suitable for diagnostic use only."


def test_blocked_report_requires_blocking_reasons() -> None:
    profile = profile_from_records(_weekly_rows(12))
    with pytest.raises(ValidationError, match="blocking_reasons"):
        DataReadinessReport(
            profile=profile,
            status=DataReadinessStatus.BLOCKED,
            checks=build_data_readiness_report(profile).checks,
            summary="Dataset is blocked for the requested workflow.",
            blocking_reasons=[],
        )


def test_summary_text_is_deterministic() -> None:
    blocked = build_readiness_from_records(_weekly_rows(2))
    assert blocked.summary == "Dataset is blocked for the requested workflow."

    ready = build_readiness_from_records(_long_history_rows())
    assert ready.summary == "Dataset is ready for the requested workflow."


def test_recommended_fixes_include_date_fix() -> None:
    report = build_readiness_from_records([{"spend": 1, "conversions": 2}] * 12)
    assert "Provide a date/week/month field." in report.recommended_fixes


def test_recommended_fixes_include_row_count_fix() -> None:
    report = build_readiness_from_records(_weekly_rows(3))
    assert (
        "Provide more observations before running MMM or experiment workflows."
        in report.recommended_fixes
    )


def test_recommended_fixes_include_missing_required_field_fix() -> None:
    report = build_readiness_from_records(
        _weekly_rows(12),
        BusinessObjective(objective_type=BusinessObjectiveType.REVENUE_ROI),
    )
    assert any(fix.startswith("Provide required field:") for fix in report.recommended_fixes)


def test_recommended_fixes_include_missing_recommended_field_fix() -> None:
    report = build_readiness_from_records(
        _weekly_rows(12),
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
    )
    assert any(
        fix.startswith("Consider providing recommended field:") for fix in report.recommended_fixes
    )


def test_build_readiness_from_records_works_without_objective() -> None:
    report = build_readiness_from_records(_weekly_rows(12))
    assert report.profile.row_count == 12


def test_build_readiness_from_records_works_with_conversion_roi_objective() -> None:
    report = build_readiness_from_records(
        _long_history_rows(),
        BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI),
    )
    assert report.status in (
        DataReadinessStatus.READY,
        DataReadinessStatus.READY_WITH_WARNINGS,
    )


def test_awareness_with_conversions_only_produces_blocked_report() -> None:
    report = build_readiness_from_records(
        _weekly_rows(12),
        BusinessObjective(objective_type=BusinessObjectiveType.AWARENESS),
    )
    assert report.status == DataReadinessStatus.BLOCKED
