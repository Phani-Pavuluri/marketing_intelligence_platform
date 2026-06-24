"""Tests for deterministic config drafting."""

from datetime import date, timedelta

from mip.workflows.configs import (
    DraftConfigStatus,
    GeoXConfigDraft,
    MMMConfigDraft,
    draft_config_for_objective,
    draft_geox_config,
    draft_mmm_config,
)
from mip.workflows.configs.geox import PRE_PERIOD_PLACEHOLDER
from mip.workflows.intake import (
    BusinessObjective,
    BusinessObjectiveType,
    evaluate_objective_feasibility,
)
from mip.workflows.intake.feasibility import ObjectiveFeasibilityReport
from mip.workflows.readiness.profile import profile_to_availability
from mip.workflows.readiness.report import (
    DataReadinessReport,
    DataReadinessStatus,
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
            "geo": "us" if index % 2 == 0 else "uk",
        }
        for index in range(60)
    ]


def _experiment_rows() -> list[dict[str, object]]:
    return [
        {
            "date": (date(2024, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "geo": "dma_a" if index % 2 == 0 else "dma_b",
            "outcome": 100 + index,
            "spend": 50,
        }
        for index in range(60)
    ]


def _objective(objective_type: BusinessObjectiveType) -> BusinessObjective:
    return BusinessObjective(objective_type=objective_type)


def _pipeline(
    objective_type: BusinessObjectiveType,
    records: list[dict[str, object]],
) -> tuple[DataReadinessReport, ObjectiveFeasibilityReport]:
    readiness = build_readiness_from_records(records, _objective(objective_type))
    availability = profile_to_availability(readiness.profile)
    feasibility = evaluate_objective_feasibility(_objective(objective_type), availability)
    return readiness, feasibility


def test_blocked_feasibility_produces_blocked_config() -> None:
    readiness, feasibility = _pipeline(
        BusinessObjectiveType.AWARENESS,
        _weekly_rows(12),
    )
    draft = draft_mmm_config(_objective(BusinessObjectiveType.AWARENESS), feasibility, readiness)
    assert draft.metadata.status == DraftConfigStatus.BLOCKED
    assert not draft.metadata.production_eligible


def _draft_conversion_roi(
    feasibility: ObjectiveFeasibilityReport,
    readiness: DataReadinessReport,
) -> MMMConfigDraft:
    objective = _objective(BusinessObjectiveType.CONVERSION_ROI)
    return draft_mmm_config(objective, feasibility, readiness)


def test_blocked_readiness_produces_blocked_config() -> None:
    readiness = build_readiness_from_records(_weekly_rows(3))
    availability = profile_to_availability(readiness.profile)
    feasibility = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.CONVERSION_ROI),
        availability,
    )
    draft = _draft_conversion_roi(feasibility, readiness)
    assert draft.metadata.status == DraftConfigStatus.BLOCKED


def test_readiness_warnings_produce_draftable_with_warnings() -> None:
    readiness, feasibility = _pipeline(
        BusinessObjectiveType.CONVERSION_ROI,
        _weekly_rows(12),
    )
    draft = _draft_conversion_roi(feasibility, readiness)
    assert draft.metadata.status == DraftConfigStatus.DRAFTABLE_WITH_WARNINGS


def test_clean_conversion_roi_produces_mmm_draft() -> None:
    readiness, feasibility = _pipeline(
        BusinessObjectiveType.CONVERSION_ROI,
        _long_history_rows(),
    )
    draft = _draft_conversion_roi(feasibility, readiness)
    assert isinstance(draft, MMMConfigDraft)
    assert draft.outcome_field == "conversions"
    assert draft.spend_field == "spend"
    assert draft.date_field == "date"
    assert draft.metadata.status in (
        DraftConfigStatus.DRAFTABLE,
        DraftConfigStatus.DRAFTABLE_WITH_WARNINGS,
    )
    assert draft.metadata.production_eligible is True


def test_experiment_design_produces_geox_draft() -> None:
    readiness, feasibility = _pipeline(
        BusinessObjectiveType.EXPERIMENT_DESIGN,
        _experiment_rows(),
    )
    draft = draft_geox_config(
        _objective(BusinessObjectiveType.EXPERIMENT_DESIGN),
        feasibility,
        readiness,
    )
    assert isinstance(draft, GeoXConfigDraft)
    assert draft.treatment_unit_field == "geo"
    assert draft.pre_period_field == PRE_PERIOD_PLACEHOLDER


def test_awareness_without_awareness_kpi_does_not_produce_production_mmm_config() -> None:
    readiness, feasibility = _pipeline(
        BusinessObjectiveType.AWARENESS,
        _weekly_rows(12),
    )
    draft = draft_mmm_config(_objective(BusinessObjectiveType.AWARENESS), feasibility, readiness)
    assert draft.metadata.status == DraftConfigStatus.BLOCKED
    assert draft.metadata.production_eligible is False


def test_missing_geo_warns_for_geox_draft() -> None:
    rows = [
        {
            "date": (date(2024, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "geo": "dma_a",
            "outcome": 100,
        }
        for index in range(60)
    ]
    readiness, feasibility = _pipeline(BusinessObjectiveType.EXPERIMENT_DESIGN, rows)
    draft = draft_geox_config(
        _objective(BusinessObjectiveType.EXPERIMENT_DESIGN),
        feasibility,
        readiness,
    )
    assert any("geo breakdown" in warning.lower() for warning in draft.metadata.warnings)


def test_draft_config_for_objective_routes_to_geox_for_experiment_design() -> None:
    readiness, feasibility = _pipeline(
        BusinessObjectiveType.EXPERIMENT_DESIGN,
        _experiment_rows(),
    )
    draft = draft_config_for_objective(
        _objective(BusinessObjectiveType.EXPERIMENT_DESIGN),
        feasibility,
        readiness,
    )
    assert isinstance(draft, GeoXConfigDraft)


def test_draft_config_for_objective_routes_to_mmm_for_conversion_roi() -> None:
    readiness, feasibility = _pipeline(
        BusinessObjectiveType.CONVERSION_ROI,
        _long_history_rows(),
    )
    draft = draft_config_for_objective(
        _objective(BusinessObjectiveType.CONVERSION_ROI),
        feasibility,
        readiness,
    )
    assert isinstance(draft, MMMConfigDraft)


def test_diagnostic_only_readiness_produces_diagnostic_only_config() -> None:
    readiness = build_readiness_from_records(
        [{"date": "2025-01-01", "conversions": 1}] * 12,
        _objective(BusinessObjectiveType.CONVERSION_ROI),
    )
    availability = profile_to_availability(readiness.profile)
    feasibility = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.CONVERSION_ROI),
        availability,
    )
    draft = _draft_conversion_roi(feasibility, readiness)
    assert draft.metadata.status in (
        DraftConfigStatus.DIAGNOSTIC_ONLY,
        DraftConfigStatus.BLOCKED,
        DraftConfigStatus.DRAFTABLE_WITH_WARNINGS,
    )
    if readiness.status == DataReadinessStatus.DIAGNOSTIC_ONLY:
        assert draft.metadata.production_eligible is False
