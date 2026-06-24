"""Tests for governed planner/router."""

from datetime import UTC, datetime, timedelta

import pytest

from mip.orchestration.approvals import ApprovalCheckpoint
from mip.orchestration.manifest import HumanApprovalRequirement, WorkflowActionType
from mip.orchestration.router import (
    PlannerDecision,
    PlannerDecisionStatus,
    PlannerRoute,
    assert_safe_planner_route,
    format_planner_route_for_display,
    planner_route_from_summary,
    planner_route_with_mmm_fixture,
)
from mip.reports.mmm_fixture import build_mmm_fixture_report
from mip.workflows.intake import BusinessObjective, BusinessObjectiveType
from mip.workflows.orchestrator import WorkflowRunStatus, WorkflowRunSummary, run_local_workflow


def _weekly_rows(count: int = 12) -> list[dict[str, object]]:
    base = datetime(2025, 1, 1, tzinfo=UTC)
    return [
        {
            "date": (base + timedelta(days=7 * index)).date().isoformat(),
            "channel": "search",
            "spend": 100 + index,
            "conversions": 10 + index,
        }
        for index in range(count)
    ]


def _long_history_rows() -> list[dict[str, object]]:
    base = datetime(2024, 1, 1, tzinfo=UTC)
    return [
        {
            "date": (base + timedelta(days=7 * index)).date().isoformat(),
            "spend": 100,
            "conversions": 10,
            "channel": "search" if index % 2 == 0 else "social",
            "geo": "us" if index % 2 == 0 else "uk",
        }
        for index in range(60)
    ]


def _summary(objective_type: str, records: list[dict[str, object]]) -> WorkflowRunSummary:
    return run_local_workflow(
        BusinessObjective(objective_type=BusinessObjectiveType(objective_type)),
        records,
    )


def _allowed_actions(route: PlannerRoute) -> set[WorkflowActionType]:
    return {decision.action_type for decision in route.allowed_decisions}


def _blocked_actions(route: PlannerRoute) -> set[WorkflowActionType]:
    return {decision.action_type for decision in route.blocked_decisions}


def test_clean_conversion_roi_route_allows_next_actions() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    route = planner_route_from_summary(summary)
    assert route.agentic_planning_enabled is False
    allowed = _allowed_actions(route)
    assert WorkflowActionType.RENDER_REPORT in allowed
    assert WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE in allowed
    assert route.recommended_next_action == WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE


def test_blocked_awareness_route_allows_blocker_explanation_and_missing_data() -> None:
    summary = _summary("awareness", _weekly_rows(12))
    assert summary.status == WorkflowRunStatus.BLOCKED
    route = planner_route_from_summary(summary)
    allowed = _allowed_actions(route)
    assert WorkflowActionType.PARSE_INPUT in allowed
    assert WorkflowActionType.RENDER_REPORT in allowed
    assert WorkflowActionType.EVALUATE_FEASIBILITY in allowed
    parse_decision = next(
        decision
        for decision in route.allowed_decisions
        if decision.action_type == WorkflowActionType.PARSE_INPUT
    )
    assert "awareness_kpi" in parse_decision.required_inputs
    assert route.recommended_next_action == WorkflowActionType.PARSE_INPUT


def test_blocked_awareness_route_blocks_adapter_and_model_paths() -> None:
    summary = _summary("awareness", _weekly_rows(12))
    route = planner_route_from_summary(summary)
    blocked = _blocked_actions(route)
    assert WorkflowActionType.BUILD_ADAPTER_INPUT in blocked
    assert WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE in blocked
    assert WorkflowActionType.BUILD_TRUST_REPORT in blocked


def test_mmm_fixture_route_allows_placeholder_report_only() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    fixture_report = build_mmm_fixture_report(summary)
    assert fixture_report is not None
    route = planner_route_with_mmm_fixture(summary, fixture_report)
    allowed = _allowed_actions(route)
    assert allowed == {WorkflowActionType.RENDER_REPORT}
    assert route.recommended_next_action == WorkflowActionType.RENDER_REPORT
    blocked = _blocked_actions(route)
    assert WorkflowActionType.BUILD_ADAPTER_OUTPUT_FIXTURE in blocked
    assert WorkflowActionType.REQUEST_HUMAN_APPROVAL in blocked


def test_recommended_next_action_must_be_allowed() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    route = planner_route_from_summary(summary)
    assert route.recommended_next_action in _allowed_actions(route)


def test_blocked_decisions_require_reasons() -> None:
    with pytest.raises(ValueError, match="planner decision reason cannot be empty"):
        PlannerDecision(
            action_type=WorkflowActionType.BUILD_ADAPTER_INPUT,
            status=PlannerDecisionStatus.BLOCKED,
            reason="",
        )


def test_approval_required_decisions_require_approval_metadata() -> None:
    with pytest.raises(ValueError, match="approval-required decisions must declare"):
        PlannerDecision(
            action_type=WorkflowActionType.REQUEST_HUMAN_APPROVAL,
            status=PlannerDecisionStatus.REQUIRES_APPROVAL,
            reason="needs approval metadata",
            human_approval_requirement=HumanApprovalRequirement.NOT_REQUIRED,
        )


def test_assert_safe_rejects_forbidden_claims() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    route = planner_route_from_summary(summary)
    unsafe = route.model_copy(
        update={
            "routing_notes": [
                *route.routing_notes,
                "This route shows actual ROI from model results",
            ]
        }
    )
    with pytest.raises(ValueError, match="forbidden phrase"):
        assert_safe_planner_route(unsafe)


def test_format_planner_route_for_display_is_safe() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    route = planner_route_from_summary(summary)
    display = format_planner_route_for_display(route)
    assert display["recommended_next_action"] == "build_adapter_output_fixture"
    assert display["allowed_actions"]
    assert display["blocked_actions"]


def test_approval_required_decisions_include_checkpoint_after_finalize() -> None:
    summary = _summary("conversion_roi", _long_history_rows())
    route = planner_route_from_summary(summary)
    gated = [
        decision
        for decision in route.allowed_decisions
        if decision.status == PlannerDecisionStatus.REQUIRES_APPROVAL
    ]
    if not gated:
        pytest.skip("workflow summary did not require human approval")
    checkpoint = gated[0].approval_checkpoint
    assert isinstance(checkpoint, ApprovalCheckpoint)
    assert checkpoint.blocked_until_approved is True


def test_public_imports() -> None:
    from mip.orchestration import (
        PlannerRoute,
        planner_route_from_summary,
        route_next_actions,
    )

    assert PlannerRoute is not None
    assert callable(route_next_actions)
    assert callable(planner_route_from_summary)
