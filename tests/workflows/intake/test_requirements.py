"""Tests for objective data requirement catalog."""

import pytest
from pydantic import ValidationError

from mip.workflows.intake.objectives import BusinessObjectiveType
from mip.workflows.intake.requirements import (
    DataFieldRequirement,
    DataFieldRole,
    WorkflowType,
    requirement_for_objective,
)


@pytest.mark.parametrize("objective_type", list(BusinessObjectiveType))
def test_every_objective_type_has_requirement(objective_type: BusinessObjectiveType) -> None:
    requirement = requirement_for_objective(objective_type)
    assert requirement.objective_type == objective_type
    assert requirement.required_fields
    assert requirement.supported_workflows


def test_requirement_has_required_fields_and_workflows() -> None:
    requirement = requirement_for_objective(BusinessObjectiveType.CONVERSION_ROI)
    assert all(field.role == DataFieldRole.REQUIRED for field in requirement.required_fields)
    assert WorkflowType.MMM_CHANNEL_ROI in requirement.supported_workflows


def test_awareness_requirement_includes_aliases() -> None:
    requirement = requirement_for_objective(BusinessObjectiveType.AWARENESS)
    awareness_field = next(
        field for field in requirement.required_fields if field.field_name == "awareness_kpi"
    )
    assert "brand_search" in awareness_field.accepted_aliases
    assert "Conversions-only data is not sufficient" in requirement.notes[0]


def test_conversion_roi_supports_mmm_workflows() -> None:
    requirement = requirement_for_objective(BusinessObjectiveType.CONVERSION_ROI)
    assert WorkflowType.MMM_CHANNEL_ROI in requirement.supported_workflows
    assert WorkflowType.MMM_BUDGET_ALLOCATION in requirement.supported_workflows


def test_experiment_design_supports_geox_design() -> None:
    requirement = requirement_for_objective(BusinessObjectiveType.EXPERIMENT_DESIGN)
    assert requirement.supported_workflows == [WorkflowType.GEOX_EXPERIMENT_DESIGN]


def test_data_field_requirement_rejects_empty_alias() -> None:
    with pytest.raises(ValidationError, match="accepted_aliases"):
        DataFieldRequirement(
            field_name="spend",
            role=DataFieldRole.REQUIRED,
            description="Marketing spend",
            accepted_aliases=[""],
        )


def test_unsupported_objective_raises() -> None:
    from mip.workflows.intake import requirements as req_mod

    objective = BusinessObjectiveType.CONVERSION_ROI
    original = req_mod._REQUIREMENTS.pop(objective)
    try:
        with pytest.raises(ValueError, match="unsupported objective type"):
            requirement_for_objective(objective)
    finally:
        req_mod._REQUIREMENTS[objective] = original
