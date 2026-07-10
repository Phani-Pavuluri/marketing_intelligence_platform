"""Tests for MMM planning-answer eligibility contracts."""

from __future__ import annotations

from mip.contracts import (
    FORBIDDEN_MMM_PLANNING_ANSWER_ELIGIBILITY_RESULT_FIELD_NAMES,
    RECOMMENDED_NEXT_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_CHECKPOINT_AUDIT_ARTIFACT,
    MMMPlanningAnswerEligibilityIssueCode,
    MMMPlanningAnswerEligibilityRequest,
    MMMPlanningAnswerEligibilityResult,
    MMMPlanningAnswerEligibilityStatus,
    MMMPlanningAnswerGateReference,
    MMMPlanningAnswerMode,
    MMMPlanningQuestionClass,
)

_FORBIDDEN_TOP_LEVEL = (
    "spend_delta",
    "delta_mu",
    "roi",
    "roas",
    "incrementality",
    "optimal_budget",
    "marginal_roi",
    "recommendation",
    "recommended_budget",
)


def test_required_enums_exist() -> None:
    assert MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE in MMMPlanningQuestionClass
    assert MMMPlanningQuestionClass.DIAGNOSTIC_DRIVER in MMMPlanningQuestionClass
    assert MMMPlanningQuestionClass.SCENARIO_COMPARISON in MMMPlanningQuestionClass
    assert MMMPlanningQuestionClass.SIMULATION_REQUEST in MMMPlanningQuestionClass
    assert MMMPlanningQuestionClass.OPTIMIZATION_REQUEST in MMMPlanningQuestionClass
    assert MMMPlanningQuestionClass.RECOMMENDATION_REQUEST in MMMPlanningQuestionClass
    assert MMMPlanningQuestionClass.UNKNOWN in MMMPlanningQuestionClass
    assert MMMPlanningAnswerMode.DESCRIPTIVE in MMMPlanningAnswerMode
    assert MMMPlanningAnswerMode.DIAGNOSTIC in MMMPlanningAnswerMode
    assert MMMPlanningAnswerMode.SCENARIO_COMPARISON in MMMPlanningAnswerMode
    assert MMMPlanningAnswerMode.SIMULATION_ONLY in MMMPlanningAnswerMode
    assert MMMPlanningAnswerMode.RECOMMENDATION_ELIGIBLE in MMMPlanningAnswerMode
    assert MMMPlanningAnswerMode.BLOCKED in MMMPlanningAnswerMode
    assert MMMPlanningAnswerMode.DEFERRED in MMMPlanningAnswerMode
    assert MMMPlanningAnswerEligibilityStatus.ANSWER_ELIGIBLE in (
        MMMPlanningAnswerEligibilityStatus
    )
    assert MMMPlanningAnswerEligibilityStatus.RECOMMENDATION_REQUIRES_GATES in (
        MMMPlanningAnswerEligibilityStatus
    )
    assert MMMPlanningAnswerEligibilityIssueCode.NO_OPTIMIZER_EXECUTION in (
        MMMPlanningAnswerEligibilityIssueCode
    )
    assert MMMPlanningAnswerEligibilityIssueCode.NO_RECOMMENDATION_CONTRACT_GENERATION in (
        MMMPlanningAnswerEligibilityIssueCode
    )


def test_request_and_result_models_serialize() -> None:
    request = MMMPlanningAnswerEligibilityRequest(request_id="pae-req-1")
    assert request.require_trust_review_for_planning is True
    assert request.require_decision_surface_for_scenario is True
    assert request.require_recommendation_gate_for_recommendation is True
    assert request.allow_descriptive_without_decision_surface is True
    assert request.allow_diagnostic_without_decision_surface is True
    result = MMMPlanningAnswerEligibilityResult(
        request_id="pae-req-1",
        question_class=MMMPlanningQuestionClass.UNKNOWN,
        answer_mode=MMMPlanningAnswerMode.BLOCKED,
        status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
    )
    payload = result.model_dump()
    assert payload["answer_allowed"] is False
    assert "recommendation" not in payload
    assert "recommended_budget" not in payload


def test_gate_reference_serializes() -> None:
    gate = MMMPlanningAnswerGateReference(
        gate_name="decision_surface",
        gate_status="pass",
        passed=True,
        required=True,
    )
    assert gate.model_dump()["gate_name"] == "decision_surface"


def test_forbidden_fields_absent() -> None:
    for name in _FORBIDDEN_TOP_LEVEL:
        assert name in FORBIDDEN_MMM_PLANNING_ANSWER_ELIGIBILITY_RESULT_FIELD_NAMES
        assert name not in MMMPlanningAnswerEligibilityResult.model_fields


def test_exports_from_mip_contracts() -> None:
    assert (
        RECOMMENDED_NEXT_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_CHECKPOINT_AUDIT_ARTIFACT
        == "MIP_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_CHECKPOINT_AUDIT_001"
    )
