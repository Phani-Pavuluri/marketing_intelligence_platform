"""Tests for GeoX adapter contracts."""

from datetime import date, timedelta

import pytest

from mip.adapters.base import AdapterRunKind, AdapterRunStatus
from mip.adapters.geox import (
    build_geox_adapter_input,
    build_geox_adapter_output_placeholder,
)
from mip.workflows.configs import DraftConfigStatus, draft_geox_config
from mip.workflows.configs.geox import GeoXConfigDraft
from mip.workflows.intake import (
    BusinessObjective,
    BusinessObjectiveType,
    evaluate_objective_feasibility,
)
from mip.workflows.readiness.profile import profile_to_availability
from mip.workflows.readiness.report import build_readiness_from_records


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


def _weekly_rows(count: int = 12) -> list[dict[str, object]]:
    return [
        {
            "date": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "spend": 100,
            "conversions": 10,
        }
        for index in range(count)
    ]


def _draft_experiment_design() -> GeoXConfigDraft:
    objective = BusinessObjective(objective_type=BusinessObjectiveType.EXPERIMENT_DESIGN)
    readiness = build_readiness_from_records(_experiment_rows(), objective)
    feasibility = evaluate_objective_feasibility(
        objective,
        profile_to_availability(readiness.profile),
    )
    return draft_geox_config(objective, feasibility, readiness)


def _blocked_geox_draft() -> GeoXConfigDraft:
    objective = BusinessObjective(objective_type=BusinessObjectiveType.EXPERIMENT_DESIGN)
    readiness = build_readiness_from_records(_weekly_rows(3), objective)
    feasibility = evaluate_objective_feasibility(
        objective,
        profile_to_availability(readiness.profile),
    )
    return draft_geox_config(objective, feasibility, readiness)


def test_geox_input_can_be_built_from_draftable_config() -> None:
    draft = _draft_experiment_design()
    bundle = build_geox_adapter_input(draft)
    assert bundle.kind == AdapterRunKind.GEOX
    assert bundle.status == AdapterRunStatus.VALIDATED
    assert bundle.source_config_marker == draft.metadata.generated_marker
    assert bundle.geox_input is not None
    assert bundle.geox_input.treatment_unit_field == "geo"


def test_blocked_geox_config_cannot_build_executable_input() -> None:
    draft = _blocked_geox_draft()
    assert draft.metadata.status == DraftConfigStatus.BLOCKED
    with pytest.raises(ValueError, match="blocked config draft cannot produce"):
        build_geox_adapter_input(draft)


def test_geox_output_placeholder_includes_source_marker() -> None:
    draft = _draft_experiment_design()
    output = build_geox_adapter_output_placeholder(draft)
    assert output.source_config_marker == draft.metadata.generated_marker
    assert output.geox_output is not None
    assert output.geox_output.config_marker == draft.metadata.generated_marker
