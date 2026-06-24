"""Tests for MMM adapter contracts."""

from datetime import date, timedelta

import pytest

from mip.adapters.base import AdapterRunKind, AdapterRunStatus
from mip.adapters.mmm import (
    build_mmm_adapter_input,
    build_mmm_adapter_output_placeholder,
)
from mip.workflows.configs import DraftConfigStatus, draft_mmm_config
from mip.workflows.configs.mmm import MMMConfigDraft
from mip.workflows.intake import (
    BusinessObjective,
    BusinessObjectiveType,
    evaluate_objective_feasibility,
)
from mip.workflows.readiness.profile import profile_to_availability
from mip.workflows.readiness.report import build_readiness_from_records


def _weekly_rows(count: int = 12, **extra: object) -> list[dict[str, object]]:
    return [
        {
            "date": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "spend": 100,
            "conversions": 10,
            **extra,
        }
        for index in range(count)
    ]


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


def _draft_conversion_roi() -> MMMConfigDraft:
    objective = BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI)
    readiness = build_readiness_from_records(_long_history_rows(), objective)
    feasibility = evaluate_objective_feasibility(
        objective,
        profile_to_availability(readiness.profile),
    )
    return draft_mmm_config(objective, feasibility, readiness)


def _blocked_draft() -> MMMConfigDraft:
    objective = BusinessObjective(objective_type=BusinessObjectiveType.AWARENESS)
    readiness = build_readiness_from_records(_weekly_rows(12), objective)
    feasibility = evaluate_objective_feasibility(
        objective,
        profile_to_availability(readiness.profile),
    )
    return draft_mmm_config(objective, feasibility, readiness)


def test_mmm_input_can_be_built_from_draftable_config() -> None:
    draft = _draft_conversion_roi()
    bundle = build_mmm_adapter_input(draft)
    assert bundle.kind == AdapterRunKind.MMM
    assert bundle.status == AdapterRunStatus.VALIDATED
    assert bundle.source_config_marker == draft.metadata.generated_marker
    assert bundle.mmm_input is not None
    assert bundle.mmm_input.outcome_field == "conversions"


def test_blocked_config_cannot_build_executable_input() -> None:
    draft = _blocked_draft()
    assert draft.metadata.status == DraftConfigStatus.BLOCKED
    with pytest.raises(ValueError, match="blocked config draft cannot produce"):
        build_mmm_adapter_input(draft)


def test_mmm_output_placeholder_includes_source_marker() -> None:
    draft = _draft_conversion_roi()
    output = build_mmm_adapter_output_placeholder(draft)
    assert output.source_config_marker == draft.metadata.generated_marker
    assert output.mmm_output is not None
    assert output.mmm_output.config_marker == draft.metadata.generated_marker
