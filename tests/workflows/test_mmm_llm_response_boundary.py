"""Workflow tests for MMM LLM response boundary."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.mmm_llm_response_boundary import (
    FORBIDDEN_MMM_LLM_RESPONSE_BOUNDARY_FIELD_NAMES,
    MMMLLMForbiddenAdditionType,
    MMMLLMResponseBoundary,
    MMMLLMResponseBoundaryIssueCode,
    MMMLLMResponseBoundaryRequest,
    MMMLLMResponseBoundaryStatus,
    MMMLLMSectionPolicy,
    MMMLLMSectionUsePolicy,
)
from mip.contracts.mmm_planning_answer_eligibility import (
    MMMPlanningAnswerEligibilityResult,
    MMMPlanningAnswerEligibilityStatus,
    MMMPlanningAnswerMode,
    MMMPlanningQuestionClass,
)
from mip.contracts.mmm_planning_answer_envelope import (
    MMMPlanningAnswerEnvelopeRequest,
    MMMPlanningAnswerEnvelopeStatus,
)
from mip.reports.mmm_planning_response_renderer import (
    MMMPlanningRenderedResponse,
    MMMPlanningResponseSection,
    render_mmm_planning_response,
)
from mip.workflows.mmm_llm_response_boundary import (
    build_mmm_llm_response_boundary,
    summarize_mmm_llm_response_boundary,
)
from mip.workflows.mmm_planning_answer_envelope import build_mmm_planning_answer_envelope

_CONTRACT_SOURCE = Path("src/mip/contracts/mmm_llm_response_boundary.py")
_WORKFLOW_SOURCE = Path("src/mip/workflows/mmm_llm_response_boundary.py")


def _policy_for(boundary: MMMLLMResponseBoundary, section_id: str) -> MMMLLMSectionPolicy:
    for policy in boundary.section_policies:
        if policy.section_id == section_id:
            return policy
    raise AssertionError(f"missing section policy {section_id}")


def _eligibility(
    *,
    answer_mode: MMMPlanningAnswerMode = MMMPlanningAnswerMode.DESCRIPTIVE,
    status: MMMPlanningAnswerEligibilityStatus = (
        MMMPlanningAnswerEligibilityStatus.ANSWER_ELIGIBLE
    ),
    answer_allowed: bool = True,
    human_review_required: bool = False,
    caveats: list[str] | None = None,
    blocked_reasons: list[str] | None = None,
    deferred_reasons: list[str] | None = None,
) -> MMMPlanningAnswerEligibilityResult:
    return MMMPlanningAnswerEligibilityResult(
        request_id="elig-1",
        question_class=MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE,
        answer_mode=answer_mode,
        status=status,
        answer_allowed=answer_allowed,
        human_review_required=human_review_required,
        caveats=caveats or [],
        blocked_reasons=blocked_reasons or [],
        deferred_reasons=deferred_reasons or [],
        lineage={"upstream": "eligibility"},
    )


def _rendered(
    eligibility: MMMPlanningAnswerEligibilityResult | None = None,
) -> MMMPlanningRenderedResponse:
    envelope = build_mmm_planning_answer_envelope(
        MMMPlanningAnswerEnvelopeRequest(
            request_id="env-1",
            eligibility_result=eligibility if eligibility is not None else _eligibility(),
            lineage={"caller": "test"},
        )
    )
    return render_mmm_planning_response(envelope)


def _manual_rendered(**overrides: object) -> MMMPlanningRenderedResponse:
    base: dict[str, object] = {
        "request_id": "rendered-1",
        "status": MMMPlanningAnswerEnvelopeStatus.READY_TO_EXPLAIN,
        "answer_mode": MMMPlanningAnswerMode.DESCRIPTIVE,
        "answer_allowed": True,
        "human_review_required": False,
        "sections": [
            MMMPlanningResponseSection(
                section_id="status", title="Status", items=["READY_TO_EXPLAIN"]
            ),
            MMMPlanningResponseSection(
                section_id="answer_mode", title="Answer mode", items=["DESCRIPTIVE"]
            ),
            MMMPlanningResponseSection(
                section_id="can_say",
                title="What I can say",
                items=["Can explain descriptive status from eligibility metadata."],
            ),
            MMMPlanningResponseSection(
                section_id="cannot_say",
                title="What I cannot say",
                items=[
                    "Cannot report ROI, ROAS, lift, or incrementality unless supplied "
                    "by an approved artifact."
                ],
            ),
            MMMPlanningResponseSection(
                section_id="caveats", title="Caveats", items=["No caveats supplied."]
            ),
            MMMPlanningResponseSection(
                section_id="required_gates",
                title="Required gates",
                items=["No required gates supplied."],
            ),
            MMMPlanningResponseSection(
                section_id="blocked_deferred_reasons",
                title="Blocked/deferred reasons",
                items=["No blocked reasons supplied.", "No deferred reasons supplied."],
            ),
            MMMPlanningResponseSection(
                section_id="human_review_required",
                title="Human review required",
                items=["No"],
            ),
            MMMPlanningResponseSection(
                section_id="evidence_references",
                title="Evidence references",
                items=["No evidence references supplied."],
            ),
        ],
        "issues": [],
        "lineage": {"source": "manual"},
        "metadata": {},
    }
    base.update(overrides)
    return MMMPlanningRenderedResponse(**base)  # type: ignore[arg-type]


def _build(
    rendered: MMMPlanningRenderedResponse | None,
    *,
    include_default_policies: bool = True,
    user_intent: str | None = None,
) -> MMMLLMResponseBoundary:
    return build_mmm_llm_response_boundary(
        MMMLLMResponseBoundaryRequest(
            request_id="bound-1",
            rendered_response=rendered,
            user_intent=user_intent,
            include_default_policies=include_default_policies,
            lineage={"caller": "test"},
        )
    )


def test_missing_rendered_response_returns_unknown() -> None:
    boundary = _build(None)
    assert boundary.status == MMMLLMResponseBoundaryStatus.UNKNOWN
    assert boundary.answer_allowed is False
    assert MMMLLMResponseBoundaryIssueCode.RENDERED_RESPONSE_MISSING in boundary.issues
    assert any(
        "deterministic rendered" in p.required_response.lower() for p in boundary.refusal_policies
    )


def test_rendered_status_preserved() -> None:
    boundary = _build(_rendered())
    assert boundary.status == MMMLLMResponseBoundaryStatus.READY_FOR_LLM_EXPLANATION_WITH_CAVEATS
    assert MMMLLMResponseBoundaryIssueCode.RENDERED_RESPONSE_PRESENT in boundary.issues


def test_answer_mode_preserved() -> None:
    boundary = _build(_manual_rendered())
    assert boundary.answer_mode == MMMPlanningAnswerMode.DESCRIPTIVE


def test_answer_allowed_preserved() -> None:
    boundary = _build(_manual_rendered(answer_allowed=True))
    assert boundary.answer_allowed is True


def test_human_review_preserved() -> None:
    boundary = _build(_manual_rendered(human_review_required=True))
    assert boundary.human_review_required is True
    assert boundary.status == MMMLLMResponseBoundaryStatus.HUMAN_REVIEW_REQUIRED


def test_status_section_must_preserve_verbatim() -> None:
    policy = _policy_for(_build(_manual_rendered()), "status")
    assert policy.use_policy == MMMLLMSectionUsePolicy.MUST_PRESERVE_VERBATIM
    assert policy.must_preserve_verbatim is True
    assert policy.must_include is True


def test_answer_mode_must_preserve_verbatim() -> None:
    policy = _policy_for(_build(_manual_rendered()), "answer_mode")
    assert policy.must_preserve_verbatim is True
    assert policy.must_include is True


def test_cannot_say_must_preserve_verbatim_and_not_omit() -> None:
    boundary = _build(_manual_rendered())
    policy = _policy_for(boundary, "cannot_say")
    assert policy.must_preserve_verbatim is True
    assert policy.use_policy == MMMLLMSectionUsePolicy.MUST_NOT_OMIT
    assert "cannot_say" in boundary.cannot_omit_sections
    assert MMMLLMResponseBoundaryIssueCode.CANNOT_SAY_MUST_BE_PRESERVED in boundary.issues


def test_caveats_must_preserve_meaning_and_not_omit() -> None:
    boundary = _build(_manual_rendered())
    policy = _policy_for(boundary, "caveats")
    assert policy.use_policy == MMMLLMSectionUsePolicy.MUST_PRESERVE_MEANING
    assert "caveats" in boundary.cannot_omit_sections
    assert MMMLLMResponseBoundaryIssueCode.CAVEATS_MUST_BE_PRESERVED in boundary.issues


def test_required_gates_must_preserve_meaning_and_not_omit() -> None:
    policy = _policy_for(_build(_manual_rendered()), "required_gates")
    assert policy.use_policy == MMMLLMSectionUsePolicy.MUST_PRESERVE_MEANING


def test_blocked_deferred_must_preserve_meaning_and_not_omit() -> None:
    boundary = _build(_manual_rendered())
    policy = _policy_for(boundary, "blocked_deferred_reasons")
    assert policy.use_policy == MMMLLMSectionUsePolicy.MUST_PRESERVE_MEANING
    assert (
        MMMLLMResponseBoundaryIssueCode.BLOCKED_DEFERRED_STATUS_MUST_BE_PRESERVED in boundary.issues
    )


def test_human_review_must_preserve_verbatim() -> None:
    policy = _policy_for(_build(_manual_rendered()), "human_review_required")
    assert policy.must_preserve_verbatim is True
    assert policy.must_include is True


def test_evidence_references_must_preserve_meaning_and_not_omit() -> None:
    boundary = _build(_manual_rendered())
    policy = _policy_for(boundary, "evidence_references")
    assert policy.use_policy == MMMLLMSectionUsePolicy.MUST_PRESERVE_MEANING
    assert "evidence_references" in boundary.cannot_omit_sections
    assert MMMLLMResponseBoundaryIssueCode.EVIDENCE_REFERENCES_MUST_BE_PRESERVED in boundary.issues


def test_can_say_may_rewrite_lightly_but_cannot_expand() -> None:
    policy = _policy_for(_build(_manual_rendered()), "can_say")
    assert policy.may_rewrite_lightly is True
    assert policy.forbidden_to_expand is True
    assert policy.use_policy == MMMLLMSectionUsePolicy.MAY_REWRITE_LIGHTLY


def test_forbidden_additions_include_numeric_claims() -> None:
    boundary = _build(_manual_rendered())
    assert MMMLLMForbiddenAdditionType.NEW_NUMERIC_CLAIM in boundary.forbidden_additions
    assert (
        MMMLLMForbiddenAdditionType.ROI_ROAS_LIFT_INCREMENTALITY_CLAIM
        in boundary.forbidden_additions
    )


def test_forbidden_additions_include_budget_recommendation() -> None:
    boundary = _build(_manual_rendered())
    assert MMMLLMForbiddenAdditionType.BUDGET_RECOMMENDATION in boundary.forbidden_additions
    assert MMMLLMForbiddenAdditionType.SPEND_REALLOCATION_ADVICE in boundary.forbidden_additions


def test_forbidden_additions_include_optimizer_simulator_decision_surface() -> None:
    boundary = _build(_manual_rendered())
    assert MMMLLMForbiddenAdditionType.OPTIMIZER_OUTPUT in boundary.forbidden_additions  # must not
    assert MMMLLMForbiddenAdditionType.SIMULATOR_OUTPUT in boundary.forbidden_additions  # must not
    assert MMMLLMForbiddenAdditionType.DECISION_SURFACE_OUTPUT in boundary.forbidden_additions


def test_forbidden_additions_include_blocker_softening_and_caveat_removal() -> None:
    boundary = _build(_manual_rendered())
    assert MMMLLMForbiddenAdditionType.BLOCKER_SOFTENING in boundary.forbidden_additions
    assert MMMLLMForbiddenAdditionType.CAVEAT_REMOVAL in boundary.forbidden_additions
    assert MMMLLMResponseBoundaryIssueCode.BLOCKER_SOFTENING_BLOCKED in boundary.issues
    assert MMMLLMResponseBoundaryIssueCode.CLAIM_INVENTION_BLOCKED in boundary.issues


def test_refusal_policy_for_recommendation_request() -> None:
    boundary = _build(_manual_rendered())
    refusal = next(
        p for p in boundary.refusal_policies if p.refusal_id == "refuse-budget-recommendation"
    )
    assert "RecommendationContract" in refusal.required_response
    assert MMMLLMResponseBoundaryIssueCode.RECOMMENDATION_REQUEST_REFUSAL_ADDED in boundary.issues


def test_refusal_policy_for_optimizer_simulator_request() -> None:
    boundary = _build(_manual_rendered())
    refusal = next(
        p for p in boundary.refusal_policies if p.refusal_id == "refuse-optimizer-simulator"
    )
    assert "optimizer" in refusal.required_response.lower()  # must not
    assert (
        MMMLLMResponseBoundaryIssueCode.OPTIMIZER_SIMULATOR_REQUEST_REFUSAL_ADDED in boundary.issues
    )


def test_refusal_policy_for_unsupported_numeric_claims() -> None:
    boundary = _build(_manual_rendered())
    refusal = next(
        p for p in boundary.refusal_policies if p.refusal_id == "refuse-unsupported-numeric-claims"
    )
    assert "not allowed" in refusal.required_response.lower()


def test_refusal_policy_for_ignoring_caveats_blockers() -> None:
    boundary = _build(_manual_rendered())
    refusal = next(
        p for p in boundary.refusal_policies if p.refusal_id == "refuse-ignore-caveats-blockers"
    )
    assert "cannot ignore" in refusal.required_response.lower()


def test_human_review_maps_to_human_review_required() -> None:
    boundary = _build(_manual_rendered(human_review_required=True))
    assert boundary.status == MMMLLMResponseBoundaryStatus.HUMAN_REVIEW_REQUIRED
    assert any(p.refusal_id == "refuse-skip-human-review" for p in boundary.refusal_policies)


def test_blocked_rendered_response_maps_blocked() -> None:
    rendered = _rendered(
        _eligibility(
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["blocked by gate"],
        )
    )
    boundary = _build(rendered)
    assert boundary.status == MMMLLMResponseBoundaryStatus.BLOCKED
    assert boundary.answer_allowed is False


def test_deferred_rendered_response_maps_deferred() -> None:
    rendered = _rendered(
        _eligibility(
            answer_mode=MMMPlanningAnswerMode.DEFERRED,
            status=MMMPlanningAnswerEligibilityStatus.DEFERRED,
            answer_allowed=False,
            deferred_reasons=["awaiting runtime"],
        )
    )
    boundary = _build(rendered)
    assert boundary.status == MMMLLMResponseBoundaryStatus.DEFERRED


def test_no_llm_call_provider_or_prompt() -> None:
    boundary = _build(_manual_rendered())
    assert MMMLLMResponseBoundaryIssueCode.NO_LLM_CALL in boundary.issues  # No LLM
    assert MMMLLMResponseBoundaryIssueCode.NO_PROVIDER_INTEGRATION in boundary.issues  # No LLM
    assert MMMLLMResponseBoundaryIssueCode.NO_PROMPT_TEMPLATE_EXECUTION in boundary.issues
    assert boundary.metadata.get("no_llm_call") is True
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")  # assert source scan only
    for token in ("ChatOpenAI", "anthropic", "chat.completions"):  # No LLM
        assert token not in source  # forbidden
    payload = boundary.model_dump()
    assert "prompt" not in payload
    assert "system_prompt" not in payload
    assert "provider" not in payload
    assert "completion" not in payload


def test_no_orchestration_routing() -> None:
    boundary = _build(_manual_rendered())
    assert MMMLLMResponseBoundaryIssueCode.NO_ORCHESTRATION_ROUTING in boundary.issues
    assert boundary.metadata.get("no_orchestration_routing") is True


def test_no_renderer_behavior_change() -> None:
    boundary = _build(_manual_rendered())
    assert MMMLLMResponseBoundaryIssueCode.NO_RENDERER_BEHAVIOR_CHANGE in boundary.issues


def test_no_decision_surface_trust_recommendation_construction() -> None:
    boundary = _build(_manual_rendered())
    assert MMMLLMResponseBoundaryIssueCode.NO_DECISION_SURFACE_CONSTRUCTION in boundary.issues
    assert MMMLLMResponseBoundaryIssueCode.NO_TRUST_REPORT_CONSTRUCTION in boundary.issues
    assert MMMLLMResponseBoundaryIssueCode.NO_RECOMMENDATION_CONTRACT_GENERATION in boundary.issues
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")  # assert source scan only
    assert "DecisionSurface(" not in source  # no DecisionSurface
    assert "TrustReport(" not in source  # TrustReport
    assert "RecommendationContract(" not in source  # RecommendationContract


def test_no_optimizer_simulator_budget_math() -> None:
    boundary = _build(_manual_rendered())
    assert MMMLLMResponseBoundaryIssueCode.NO_OPTIMIZER_EXECUTION in boundary.issues  # must not
    assert MMMLLMResponseBoundaryIssueCode.NO_SIMULATOR_EXECUTION in boundary.issues  # must not
    assert MMMLLMResponseBoundaryIssueCode.NO_BUDGET_ALLOCATION_CALCULATION in boundary.issues
    payload = boundary.model_dump()
    for forbidden in FORBIDDEN_MMM_LLM_RESPONSE_BOUNDARY_FIELD_NAMES:
        assert forbidden not in payload


def test_no_artifact_model_loading_execution_fitting() -> None:
    boundary = _build(_manual_rendered())
    assert MMMLLMResponseBoundaryIssueCode.NO_ARTIFACT_LOADING in boundary.issues
    assert MMMLLMResponseBoundaryIssueCode.NO_MODEL_LOADING in boundary.issues
    assert MMMLLMResponseBoundaryIssueCode.NO_MODEL_EXECUTION in boundary.issues
    assert MMMLLMResponseBoundaryIssueCode.NO_MMM_FITTING in boundary.issues


def test_no_recommendation_generation() -> None:
    boundary = _build(_manual_rendered())
    assert MMMLLMResponseBoundaryIssueCode.NO_RECOMMENDATION_GENERATION in boundary.issues
    assert "recommendation" not in boundary.model_dump()


def test_lineage_preserved() -> None:
    boundary = _build(_manual_rendered(lineage={"source": "manual", "trace": "t1"}))
    assert boundary.lineage["source"] == "manual"
    assert boundary.lineage["trace"] == "t1"
    assert boundary.lineage["source_rendered_request_id"] == "rendered-1"
    assert MMMLLMResponseBoundaryIssueCode.LINEAGE_PRESERVED in boundary.issues


def test_summary_helper_counts_only() -> None:
    boundary = _build(_manual_rendered())
    summary = summarize_mmm_llm_response_boundary(boundary)
    assert summary["answer_mode"] == MMMPlanningAnswerMode.DESCRIPTIVE.value
    assert summary["answer_allowed"] is True
    assert isinstance(summary["section_policy_count"], int)
    assert isinstance(summary["forbidden_addition_count"], int)
    assert isinstance(summary["refusal_policy_count"], int)
    assert isinstance(summary["must_include_section_count"], int)
    assert isinstance(summary["must_preserve_section_count"], int)
    assert isinstance(summary["may_rewrite_section_count"], int)
    assert isinstance(summary["issue_count"], int)
    assert "prompt" not in summary
    assert "recommend" not in str(summary).lower()
