"""Tests for objective feasibility evaluation."""

import pytest
from pydantic import ValidationError

from mip.workflows.intake import (
    BusinessObjective,
    BusinessObjectiveType,
    DataAvailabilityProfile,
    DecisionScope,
    FeasibilityStatus,
    ObjectiveFeasibilityReport,
    WorkflowType,
    evaluate_objective_feasibility,
    recommended_next_questions,
)


def _objective(
    objective_type: BusinessObjectiveType,
    **kwargs: object,
) -> BusinessObjective:
    return BusinessObjective(objective_type=objective_type, **kwargs)  # type: ignore[arg-type]


def _profile(fields: set[str], **kwargs: object) -> DataAvailabilityProfile:
    return DataAvailabilityProfile(available_fields=fields, **kwargs)  # type: ignore[arg-type]


def test_conversion_roi_with_core_fields_is_feasible() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.CONVERSION_ROI),
        _profile({"date", "spend", "conversions", "channel", "geo"}),
    )
    assert report.status in (
        FeasibilityStatus.FEASIBLE,
        FeasibilityStatus.FEASIBLE_WITH_WARNINGS,
    )
    assert WorkflowType.MMM_CHANNEL_ROI in report.recommended_workflows


def test_awareness_with_conversions_only_is_blocked() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.AWARENESS),
        _profile({"date", "spend", "conversions"}),
    )
    assert report.status == FeasibilityStatus.BLOCKED
    assert any("Conversions-only" in reason for reason in report.blocking_reasons)
    assert BusinessObjectiveType.CONVERSION_ROI in report.fallback_objectives


def test_awareness_with_brand_search_alias_is_feasible() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.AWARENESS),
        _profile({"date", "spend", "brand_search"}),
    )
    assert report.status in (
        FeasibilityStatus.FEASIBLE,
        FeasibilityStatus.FEASIBLE_WITH_WARNINGS,
    )


def test_revenue_roi_without_revenue_blocked_with_conversion_fallback() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.REVENUE_ROI),
        _profile({"date", "spend", "conversions"}),
    )
    assert report.status == FeasibilityStatus.BLOCKED
    assert BusinessObjectiveType.CONVERSION_ROI in report.fallback_objectives


def test_new_customer_acquisition_without_new_customers_blocked() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.NEW_CUSTOMER_ACQUISITION),
        _profile({"date", "spend", "conversions"}),
    )
    assert report.status == FeasibilityStatus.BLOCKED
    assert BusinessObjectiveType.CONVERSION_ROI in report.fallback_objectives


def test_profit_without_margin_blocked_with_revenue_fallback() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.PROFIT),
        _profile({"date", "spend", "revenue"}),
    )
    assert report.status == FeasibilityStatus.BLOCKED
    assert BusinessObjectiveType.REVENUE_ROI in report.fallback_objectives


def test_missing_required_fields_populate_next_data_to_request() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.CONVERSION_ROI),
        _profile({"date", "spend"}),
    )
    assert "conversions" in report.next_data_to_request


def test_missing_recommended_fields_produce_feasible_with_warnings() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.CONVERSION_ROI),
        _profile({"date", "spend", "conversions"}),
    )
    assert report.status == FeasibilityStatus.FEASIBLE_WITH_WARNINGS
    assert "channel" in report.missing_recommended_fields


def test_limited_history_produces_warning_for_mmm_objective() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.CONVERSION_ROI),
        _profile(
            {"date", "spend", "conversions", "channel", "geo"},
            history_weeks=26,
        ),
    )
    assert report.status == FeasibilityStatus.FEASIBLE_WITH_WARNINGS
    assert any("Limited history" in warning for warning in report.warnings)


def test_geo_scope_without_geo_breakdown_produces_warning() -> None:
    report = evaluate_objective_feasibility(
        _objective(
            BusinessObjectiveType.CONVERSION_ROI,
            decision_scope=DecisionScope.GEO,
        ),
        _profile(
            {"date", "spend", "conversions", "channel", "geo"},
            has_geo_breakdown=False,
        ),
    )
    assert any("geo breakdown" in warning.lower() for warning in report.warnings)


def test_blocked_report_requires_blocking_reasons() -> None:
    with pytest.raises(ValidationError, match="blocking_reasons"):
        ObjectiveFeasibilityReport(
            objective=_objective(BusinessObjectiveType.CONVERSION_ROI),
            requirement=evaluate_objective_feasibility(
                _objective(BusinessObjectiveType.CONVERSION_ROI),
                _profile({"date", "spend", "conversions"}),
            ).requirement,
            availability=_profile({"date", "spend", "conversions"}),
            status=FeasibilityStatus.BLOCKED,
            supported_workflows=[WorkflowType.DIAGNOSTIC_ONLY],
            recommended_workflows=[WorkflowType.DIAGNOSTIC_ONLY],
            blocking_reasons=[],
        )


def test_feasible_report_cannot_have_missing_required_fields() -> None:
    with pytest.raises(ValidationError, match="missing required fields"):
        ObjectiveFeasibilityReport(
            objective=_objective(BusinessObjectiveType.CONVERSION_ROI),
            requirement=evaluate_objective_feasibility(
                _objective(BusinessObjectiveType.CONVERSION_ROI),
                _profile({"date", "spend", "conversions"}),
            ).requirement,
            availability=_profile({"date", "spend", "conversions"}),
            status=FeasibilityStatus.FEASIBLE,
            missing_required_fields=["spend"],
            supported_workflows=[WorkflowType.MMM_CHANNEL_ROI],
            recommended_workflows=[WorkflowType.MMM_CHANNEL_ROI],
        )


def test_diagnostic_fallback_recommends_diagnostic_only() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.CONVERSION_ROI),
        _profile({"date", "conversions"}),
    )
    assert report.status == FeasibilityStatus.DIAGNOSTIC_ONLY
    assert report.recommended_workflows == [WorkflowType.DIAGNOSTIC_ONLY]


def test_recommended_next_questions_asks_awareness_question() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.AWARENESS),
        _profile({"date", "spend"}),
    )
    questions = recommended_next_questions(report)
    assert any("upper-funnel" in question for question in questions)


def test_recommended_next_questions_asks_revenue_question() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.REVENUE_ROI),
        _profile({"date", "spend", "conversions"}),
    )
    questions = recommended_next_questions(report)
    assert any("revenue or order value" in question for question in questions)


def test_recommended_next_questions_asks_new_customer_question() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.NEW_CUSTOMER_ACQUISITION),
        _profile({"date", "spend", "conversions"}),
    )
    questions = recommended_next_questions(report)
    assert any("new customers from returning" in question for question in questions)


def test_recommended_next_questions_asks_geo_question() -> None:
    report = evaluate_objective_feasibility(
        _objective(BusinessObjectiveType.CONVERSION_ROI),
        _profile({"date", "spend", "conversions"}),
    )
    questions = recommended_next_questions(report)
    assert any("region, DMA, state" in question for question in questions)
