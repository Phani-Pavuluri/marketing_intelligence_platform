"""Contract tests for MMM LLM response boundary."""

from __future__ import annotations

import mip.contracts as contracts
from mip.contracts.mmm_llm_response_boundary import (
    FORBIDDEN_MMM_LLM_RESPONSE_BOUNDARY_FIELD_NAMES,
    MMMLLMForbiddenAdditionType,
    MMMLLMRefusalPolicy,
    MMMLLMResponseBoundary,
    MMMLLMResponseBoundaryIssueCode,
    MMMLLMResponseBoundaryRequest,
    MMMLLMResponseBoundaryStatus,
    MMMLLMSectionPolicy,
    MMMLLMSectionUsePolicy,
)
from mip.contracts.mmm_planning_answer_eligibility import MMMPlanningAnswerMode


def test_status_enum_contains_required_values() -> None:
    values = {item.value for item in MMMLLMResponseBoundaryStatus}
    for required in (
        "ready_for_llm_explanation",
        "ready_for_llm_explanation_with_caveats",
        "blocked",
        "deferred",
        "human_review_required",
        "unknown",
    ):
        assert required in values


def test_section_use_policy_enum_contains_required_values() -> None:
    values = {item.value for item in MMMLLMSectionUsePolicy}
    for required in (
        "must_preserve_verbatim",
        "may_rewrite_lightly",
        "must_preserve_meaning",
        "must_include",
        "must_not_omit",
        "forbidden_to_expand",
        "refusal_required",
    ):
        assert required in values


def test_forbidden_addition_enum_contains_required_values() -> None:
    values = {item.value for item in MMMLLMForbiddenAdditionType}
    for required in (
        "new_numeric_claim",
        "roi_roas_lift_incrementality_claim",
        "budget_recommendation",
        "spend_reallocation_advice",
        "optimizer_output",
        "simulator_output",
        "decision_surface_output",
        "blocker_softening",
        "caveat_removal",
        "human_review_removal",
        "evidence_reference_removal",
    ):
        assert required in values


def test_issue_codes_contain_required_values() -> None:
    values = {item.value for item in MMMLLMResponseBoundaryIssueCode}
    for required in (
        "rendered_response_present",
        "rendered_response_missing",
        "cannot_say_must_be_preserved",
        "claim_invention_blocked",
        "blocker_softening_blocked",
        "no_llm_call",
        "no_provider_integration",
        "no_prompt_template_execution",
        "no_orchestration_routing",
    ):
        assert required in values


def test_section_policy_serializes() -> None:
    policy = MMMLLMSectionPolicy(
        section_id="status",
        title="Status",
        use_policy=MMMLLMSectionUsePolicy.MUST_PRESERVE_VERBATIM,
        must_include=True,
        must_preserve_verbatim=True,
        reason="Status must remain verbatim.",
    )
    payload = policy.model_dump(mode="json")
    assert payload["section_id"] == "status"
    assert payload["must_preserve_verbatim"] is True


def test_refusal_policy_serializes() -> None:
    policy = MMMLLMRefusalPolicy(
        refusal_id="refuse-budget-recommendation",
        trigger="budget_recommendation",
        required_response=(
            "Cannot recommend budget allocation without RecommendationContract approval."
        ),
        reason="recommendation refusal",
        forbidden_additions=[MMMLLMForbiddenAdditionType.BUDGET_RECOMMENDATION],
    )
    payload = policy.model_dump(mode="json")
    assert payload["refusal_id"] == "refuse-budget-recommendation"
    assert "budget_recommendation" in payload["forbidden_additions"]


def test_request_and_boundary_serialize() -> None:
    request = MMMLLMResponseBoundaryRequest(
        request_id="req-1",
        rendered_response=None,
        include_default_policies=True,
        lineage={"caller": "test"},
    )
    boundary = MMMLLMResponseBoundary(
        request_id="req-1",
        status=MMMLLMResponseBoundaryStatus.UNKNOWN,
        answer_mode=MMMPlanningAnswerMode.BLOCKED,
        answer_allowed=False,
        forbidden_additions=[MMMLLMForbiddenAdditionType.NEW_NUMERIC_CLAIM],
        issues=[MMMLLMResponseBoundaryIssueCode.RENDERED_RESPONSE_MISSING],
        lineage={"caller": "test"},
    )
    assert request.model_dump(mode="json")["request_id"] == "req-1"
    assert boundary.model_dump(mode="json")["status"] == "unknown"


def test_forbidden_fields_absent() -> None:
    boundary = MMMLLMResponseBoundary(
        request_id="req-1",
        status=MMMLLMResponseBoundaryStatus.BLOCKED,
        answer_mode=MMMPlanningAnswerMode.BLOCKED,
    )
    payload = boundary.model_dump()
    for name in FORBIDDEN_MMM_LLM_RESPONSE_BOUNDARY_FIELD_NAMES:
        assert name not in payload


def test_exports_from_mip_contracts() -> None:
    assert contracts.MMMLLMResponseBoundary is MMMLLMResponseBoundary
    assert contracts.MMMLLMResponseBoundaryRequest is MMMLLMResponseBoundaryRequest
    assert contracts.MMMLLMSectionPolicy is MMMLLMSectionPolicy
    assert contracts.MMMLLMRefusalPolicy is MMMLLMRefusalPolicy
    assert contracts.MMMLLMSectionUsePolicy is MMMLLMSectionUsePolicy
    assert contracts.MMMLLMForbiddenAdditionType is MMMLLMForbiddenAdditionType
