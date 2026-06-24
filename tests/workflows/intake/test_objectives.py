"""Tests for business objective models."""

import pytest
from pydantic import ValidationError

from mip.workflows.intake.objectives import (
    BusinessObjective,
    BusinessObjectiveType,
    DecisionHorizon,
    DecisionScope,
)


def test_business_objective_accepts_minimal_intake() -> None:
    objective = BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI)
    assert objective.decision_horizon == DecisionHorizon.UNKNOWN
    assert objective.primary_kpi is None


def test_business_objective_rejects_empty_primary_kpi() -> None:
    with pytest.raises(ValidationError, match="primary_kpi"):
        BusinessObjective(
            objective_type=BusinessObjectiveType.CONVERSION_ROI,
            primary_kpi="   ",
        )


def test_business_objective_rejects_empty_description() -> None:
    with pytest.raises(ValidationError, match="description"):
        BusinessObjective(
            objective_type=BusinessObjectiveType.CONVERSION_ROI,
            description="   ",
        )


def test_business_objective_accepts_optional_scope() -> None:
    objective = BusinessObjective(
        objective_type=BusinessObjectiveType.REVENUE_ROI,
        decision_scope=DecisionScope.CHANNEL,
        primary_kpi="revenue",
        description="Improve paid search ROI",
    )
    assert objective.decision_scope == DecisionScope.CHANNEL
