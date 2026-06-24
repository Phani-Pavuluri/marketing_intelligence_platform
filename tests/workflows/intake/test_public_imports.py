"""Tests for public mip.workflows.intake exports."""


def test_public_imports() -> None:
    from mip.workflows.intake import (
        BusinessObjective,
        BusinessObjectiveType,
        DataAvailabilityProfile,
        DataFieldRequirement,
        DataFieldRole,
        DecisionHorizon,
        DecisionScope,
        FeasibilityStatus,
        ObjectiveDataRequirement,
        ObjectiveFeasibilityReport,
        RiskTolerance,
        WorkflowType,
        evaluate_objective_feasibility,
        has_field_or_alias,
        recommended_next_questions,
        requirement_for_objective,
    )

    assert BusinessObjectiveType.CONVERSION_ROI.value == "conversion_roi"
    assert WorkflowType.MMM_CHANNEL_ROI.value == "mmm_channel_roi"
    assert DataFieldRole.REQUIRED.value == "required"
    assert FeasibilityStatus.FEASIBLE.value == "feasible"
    assert DecisionHorizon.UNKNOWN.value == "unknown"
    assert DecisionScope.CHANNEL.value == "channel"
    assert RiskTolerance.BALANCED.value == "balanced"
    assert callable(requirement_for_objective)
    assert callable(evaluate_objective_feasibility)
    assert callable(recommended_next_questions)
    assert callable(has_field_or_alias)
    assert BusinessObjective is not None
    assert DataAvailabilityProfile is not None
    assert DataFieldRequirement is not None
    assert ObjectiveDataRequirement is not None
    assert ObjectiveFeasibilityReport is not None
