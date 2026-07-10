"""Build metadata-only MMM LLM response boundaries from rendered planning sections."""

from __future__ import annotations

from mip.contracts.mmm_llm_response_boundary import (
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
from mip.contracts.mmm_planning_answer_envelope import MMMPlanningAnswerEnvelopeStatus
from mip.reports.mmm_planning_response_renderer import (
    MMMPlanningRenderedResponse,
    MMMPlanningResponseSection,
)

_BOUNDARY_ISSUES = (
    MMMLLMResponseBoundaryIssueCode.LINEAGE_PRESERVED,
    MMMLLMResponseBoundaryIssueCode.CLAIM_INVENTION_BLOCKED,
    MMMLLMResponseBoundaryIssueCode.BLOCKER_SOFTENING_BLOCKED,
    MMMLLMResponseBoundaryIssueCode.GATE_BYPASS_BLOCKED,
    MMMLLMResponseBoundaryIssueCode.UNSUPPORTED_NUMERIC_CLAIM_BLOCKED,
    MMMLLMResponseBoundaryIssueCode.NO_LLM_CALL,
    MMMLLMResponseBoundaryIssueCode.NO_PROVIDER_INTEGRATION,
    MMMLLMResponseBoundaryIssueCode.NO_PROMPT_TEMPLATE_EXECUTION,
    MMMLLMResponseBoundaryIssueCode.NO_ORCHESTRATION_ROUTING,
    MMMLLMResponseBoundaryIssueCode.NO_RENDERER_BEHAVIOR_CHANGE,
    MMMLLMResponseBoundaryIssueCode.NO_DECISION_SURFACE_CONSTRUCTION,
    MMMLLMResponseBoundaryIssueCode.NO_DECISION_SURFACE_EXECUTION,
    MMMLLMResponseBoundaryIssueCode.NO_TRUST_REPORT_CONSTRUCTION,
    MMMLLMResponseBoundaryIssueCode.NO_TRUST_REPORT_BYPASS,
    MMMLLMResponseBoundaryIssueCode.NO_RECOMMENDATION_CONTRACT_GENERATION,
    MMMLLMResponseBoundaryIssueCode.NO_RECOMMENDATION_GENERATION,
    MMMLLMResponseBoundaryIssueCode.NO_OPTIMIZER_EXECUTION,
    MMMLLMResponseBoundaryIssueCode.NO_SIMULATOR_EXECUTION,
    MMMLLMResponseBoundaryIssueCode.NO_BUDGET_ALLOCATION_CALCULATION,
    MMMLLMResponseBoundaryIssueCode.NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION,
    MMMLLMResponseBoundaryIssueCode.NO_ARTIFACT_LOADING,
    MMMLLMResponseBoundaryIssueCode.NO_MODEL_LOADING,
    MMMLLMResponseBoundaryIssueCode.NO_MODEL_EXECUTION,
    MMMLLMResponseBoundaryIssueCode.NO_MMM_FITTING,
    MMMLLMResponseBoundaryIssueCode.NO_CLAIM_AUTHORIZATION,
    MMMLLMResponseBoundaryIssueCode.NO_LLM_PROVIDER_BEHAVIOR_CHANGE,
)

_DEFAULT_FORBIDDEN_ADDITIONS = tuple(MMMLLMForbiddenAdditionType)


def build_mmm_llm_response_boundary(
    request: MMMLLMResponseBoundaryRequest,
) -> MMMLLMResponseBoundary:
    """Build a metadata-only LLM response boundary from rendered planning sections.

    Does not call an LLM/provider, execute prompts, or change renderer behavior.
    """
    issues: list[MMMLLMResponseBoundaryIssueCode] = list(_BOUNDARY_ISSUES)
    lineage = {
        **request.lineage,
        "mmm_llm_response_boundary_stage": "mmm_llm_response_boundary",
    }

    rendered = _coerce_rendered_response(request.rendered_response)
    if rendered is None:
        issues.append(MMMLLMResponseBoundaryIssueCode.RENDERED_RESPONSE_MISSING)
        refusal = MMMLLMRefusalPolicy(
            refusal_id="missing-rendered-response",
            trigger="rendered_response_missing",
            required_response=(
                "Cannot explain without deterministic rendered planning sections."
            ),
            reason="LLM boundary requires MMMPlanningRenderedResponse",
            forbidden_additions=list(_DEFAULT_FORBIDDEN_ADDITIONS),
        )
        return MMMLLMResponseBoundary(
            request_id=request.request_id,
            status=MMMLLMResponseBoundaryStatus.UNKNOWN,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            answer_allowed=False,
            human_review_required=False,
            forbidden_additions=list(_DEFAULT_FORBIDDEN_ADDITIONS),
            refusal_policies=[refusal],
            issues=list(dict.fromkeys(issues)),
            lineage=lineage,
            metadata={
                **request.metadata,
                "metadata_only_boundary": True,
                "no_llm_call": True,  # No LLM
                "no_provider_integration": True,  # No LLM provider integration
                "no_prompt_template_execution": True,
                "no_orchestration_routing": True,
            },
        )

    issues.append(MMMLLMResponseBoundaryIssueCode.RENDERED_RESPONSE_PRESENT)
    lineage = {
        **lineage,
        **rendered.lineage,
        "source_rendered_request_id": rendered.request_id,
    }

    section_policies: list[MMMLLMSectionPolicy] = []
    refusal_policies: list[MMMLLMRefusalPolicy] = []
    forbidden = list(_DEFAULT_FORBIDDEN_ADDITIONS)
    issues.append(MMMLLMResponseBoundaryIssueCode.FORBIDDEN_ADDITIONS_ADDED)

    if request.include_default_policies:
        section_policies = _default_section_policies(rendered.sections)
        refusal_policies = _default_refusal_policies(
            human_review_required=rendered.human_review_required,
        )
        issues.extend(_policy_issue_codes(section_policies, refusal_policies))

    status = _map_status(rendered)
    if status == MMMLLMResponseBoundaryStatus.READY_FOR_LLM_EXPLANATION:
        issues.append(MMMLLMResponseBoundaryIssueCode.READY_FOR_LLM_EXPLANATION)
    if status == MMMLLMResponseBoundaryStatus.HUMAN_REVIEW_REQUIRED:
        issues.append(MMMLLMResponseBoundaryIssueCode.HUMAN_REVIEW_REQUIRED)

    must_include = [p.section_id for p in section_policies if p.must_include]
    must_preserve = [
        p.section_id
        for p in section_policies
        if p.must_preserve_verbatim
        or p.use_policy
        in {
            MMMLLMSectionUsePolicy.MUST_PRESERVE_VERBATIM,
            MMMLLMSectionUsePolicy.MUST_PRESERVE_MEANING,
            MMMLLMSectionUsePolicy.MUST_NOT_OMIT,
        }
    ]
    may_rewrite = [p.section_id for p in section_policies if p.may_rewrite_lightly]
    cannot_omit = [
        p.section_id
        for p in section_policies
        if p.use_policy == MMMLLMSectionUsePolicy.MUST_NOT_OMIT
        or p.section_id
        in {
            "cannot_say",
            "caveats",
            "required_gates",
            "blocked_deferred_reasons",
            "evidence_references",
        }
    ]

    return MMMLLMResponseBoundary(
        request_id=request.request_id,
        status=status,
        answer_mode=rendered.answer_mode,
        answer_allowed=rendered.answer_allowed,
        human_review_required=rendered.human_review_required,
        section_policies=section_policies,
        forbidden_additions=forbidden,
        refusal_policies=refusal_policies,
        must_include_sections=list(dict.fromkeys(must_include)),
        must_preserve_sections=list(dict.fromkeys(must_preserve)),
        may_rewrite_sections=list(dict.fromkeys(may_rewrite)),
        cannot_omit_sections=list(dict.fromkeys(cannot_omit)),
        issues=list(dict.fromkeys(issues)),
        lineage=lineage,
        metadata={
            **request.metadata,
            **rendered.metadata,
            "metadata_only_boundary": True,
            "no_llm_call": True,  # No LLM
            "no_provider_integration": True,  # No LLM provider integration
            "no_prompt_template_execution": True,
            "no_orchestration_routing": True,
            "user_intent": request.user_intent or "",
        },
    )


def summarize_mmm_llm_response_boundary(
    boundary: MMMLLMResponseBoundary,
) -> dict[str, object]:
    """Return count/status summary only (no prompt or recommendation wording)."""
    return {
        "status": _enum_value(boundary.status),
        "answer_mode": _enum_value(boundary.answer_mode),
        "answer_allowed": boundary.answer_allowed,
        "human_review_required": boundary.human_review_required,
        "section_policy_count": len(boundary.section_policies),
        "forbidden_addition_count": len(boundary.forbidden_additions),
        "refusal_policy_count": len(boundary.refusal_policies),
        "must_include_section_count": len(boundary.must_include_sections),
        "must_preserve_section_count": len(boundary.must_preserve_sections),
        "may_rewrite_section_count": len(boundary.may_rewrite_sections),
        "issue_count": len(boundary.issues),
    }


def _coerce_rendered_response(
    value: object | None,
) -> MMMPlanningRenderedResponse | None:
    if value is None:
        return None
    if isinstance(value, MMMPlanningRenderedResponse):
        return value
    msg = "rendered_response must be MMMPlanningRenderedResponse or None"
    raise TypeError(msg)


def _map_status(rendered: MMMPlanningRenderedResponse) -> MMMLLMResponseBoundaryStatus:
    status = rendered.status
    if status == MMMPlanningAnswerEnvelopeStatus.UNKNOWN:
        return MMMLLMResponseBoundaryStatus.UNKNOWN
    if status == MMMPlanningAnswerEnvelopeStatus.BLOCKED or (
        not rendered.answer_allowed and rendered.answer_mode == MMMPlanningAnswerMode.BLOCKED
    ):
        return MMMLLMResponseBoundaryStatus.BLOCKED
    if status == MMMPlanningAnswerEnvelopeStatus.DEFERRED or (
        not rendered.answer_allowed and rendered.answer_mode == MMMPlanningAnswerMode.DEFERRED
    ):
        return MMMLLMResponseBoundaryStatus.DEFERRED
    if (
        rendered.human_review_required
        or status == MMMPlanningAnswerEnvelopeStatus.HUMAN_REVIEW_REQUIRED
    ):
        return MMMLLMResponseBoundaryStatus.HUMAN_REVIEW_REQUIRED
    if status == MMMPlanningAnswerEnvelopeStatus.READY_TO_EXPLAIN_WITH_CAVEATS or _has_caveats(
        rendered
    ):
        return MMMLLMResponseBoundaryStatus.READY_FOR_LLM_EXPLANATION_WITH_CAVEATS
    if rendered.answer_allowed:
        return MMMLLMResponseBoundaryStatus.READY_FOR_LLM_EXPLANATION
    return MMMLLMResponseBoundaryStatus.UNKNOWN


def _has_caveats(rendered: MMMPlanningRenderedResponse) -> bool:
    for section in rendered.sections:
        if section.section_id == "caveats":
            items = [item.lower() for item in section.items]
            if items and items != ["no caveats supplied."]:
                return True
        if section.section_id == "cannot_say" and section.items:
            return True
    return False


def _default_section_policies(
    sections: list[MMMPlanningResponseSection],
) -> list[MMMLLMSectionPolicy]:
    by_id = {section.section_id: section for section in sections}
    specs: list[tuple[str, str, MMMLLMSectionUsePolicy, dict[str, bool], str]] = [
        (
            "status",
            "Status",
            MMMLLMSectionUsePolicy.MUST_PRESERVE_VERBATIM,
            {"must_include": True, "must_preserve_verbatim": True},
            "Status must remain verbatim from the rendered response.",
        ),
        (
            "answer_mode",
            "Answer mode",
            MMMLLMSectionUsePolicy.MUST_PRESERVE_VERBATIM,
            {"must_include": True, "must_preserve_verbatim": True},
            "Answer mode must remain verbatim from the rendered response.",
        ),
        (
            "cannot_say",
            "What I cannot say",
            MMMLLMSectionUsePolicy.MUST_NOT_OMIT,
            {"must_preserve_verbatim": True},
            "Cannot-say boundaries must be preserved verbatim and not omitted.",
        ),
        (
            "caveats",
            "Caveats",
            MMMLLMSectionUsePolicy.MUST_PRESERVE_MEANING,
            {},
            "Caveats must preserve meaning and must not be omitted.",
        ),
        (
            "required_gates",
            "Required gates",
            MMMLLMSectionUsePolicy.MUST_PRESERVE_MEANING,
            {},
            "Required gates must preserve meaning and must not be omitted.",
        ),
        (
            "blocked_deferred_reasons",
            "Blocked/deferred reasons",
            MMMLLMSectionUsePolicy.MUST_PRESERVE_MEANING,
            {},
            "Blocked/deferred reasons must preserve meaning and must not be omitted.",
        ),
        (
            "human_review_required",
            "Human review required",
            MMMLLMSectionUsePolicy.MUST_PRESERVE_VERBATIM,
            {"must_include": True, "must_preserve_verbatim": True},
            "Human review required must remain verbatim.",
        ),
        (
            "evidence_references",
            "Evidence references",
            MMMLLMSectionUsePolicy.MUST_PRESERVE_MEANING,
            {},
            "Evidence references must preserve meaning and must not be omitted.",
        ),
        (
            "can_say",
            "What I can say",
            MMMLLMSectionUsePolicy.MAY_REWRITE_LIGHTLY,
            {"may_rewrite_lightly": True, "forbidden_to_expand": True},
            "Can-say may be lightly rewritten but must not be expanded beyond rendered content.",
        ),
    ]
    policies: list[MMMLLMSectionPolicy] = []
    for section_id, default_title, use_policy, flags, reason in specs:
        section = by_id.get(section_id)
        title = section.title if section is not None else default_title
        policies.append(
            MMMLLMSectionPolicy(
                section_id=section_id,
                title=title,
                use_policy=use_policy,
                must_include=flags.get("must_include", False),
                must_preserve_verbatim=flags.get("must_preserve_verbatim", False),
                may_rewrite_lightly=flags.get("may_rewrite_lightly", False),
                forbidden_to_expand=flags.get("forbidden_to_expand", False),
                reason=reason,
                metadata={"metadata_only_policy": True},
            )
        )
    return policies


def _default_refusal_policies(*, human_review_required: bool) -> list[MMMLLMRefusalPolicy]:
    policies = [
        MMMLLMRefusalPolicy(
            refusal_id="refuse-budget-recommendation",
            trigger="budget_recommendation_or_spend_reallocation_without_recommendation_contract",
            required_response=(
                "Cannot recommend budget allocation without RecommendationContract approval."
            ),
            reason="recommendation claims require RecommendationContract gate",
            forbidden_additions=[
                MMMLLMForbiddenAdditionType.BUDGET_RECOMMENDATION,
                MMMLLMForbiddenAdditionType.SPEND_REALLOCATION_ADVICE,
                MMMLLMForbiddenAdditionType.RECOMMENDATION_CONTRACT_CLAIM,
            ],
        ),
        MMMLLMRefusalPolicy(
            refusal_id="refuse-optimizer-simulator",  # must not
            trigger="optimizer_or_simulator_output_request",  # must not
            required_response=(
                "Cannot compute optimizer or simulator outputs from the LLM boundary."  # must not
            ),
            reason="optimizer/simulator outputs are forbidden additions",  # must not
            forbidden_additions=[
                MMMLLMForbiddenAdditionType.OPTIMIZER_OUTPUT,
                MMMLLMForbiddenAdditionType.SIMULATOR_OUTPUT,
                MMMLLMForbiddenAdditionType.DECISION_SURFACE_OUTPUT,
            ],
        ),
        MMMLLMRefusalPolicy(
            refusal_id="refuse-unsupported-numeric-claims",
            trigger="roi_roas_lift_incrementality_not_in_rendered_sections",
            required_response=(
                "Cannot provide that because the rendered response marks this claim "
                "as not allowed."
            ),
            reason="unsupported numeric claims are blocked",
            forbidden_additions=[
                MMMLLMForbiddenAdditionType.NEW_NUMERIC_CLAIM,
                MMMLLMForbiddenAdditionType.ROI_ROAS_LIFT_INCREMENTALITY_CLAIM,
            ],
        ),
        MMMLLMRefusalPolicy(
            refusal_id="refuse-ignore-caveats-blockers",
            trigger="ignore_caveats_blockers_or_cannot_say",
            required_response=(
                "Cannot ignore caveats, blockers, or cannot-say boundaries from the "
                "rendered response."
            ),
            reason="blocker softening and caveat removal are forbidden",
            forbidden_additions=[
                MMMLLMForbiddenAdditionType.BLOCKER_SOFTENING,
                MMMLLMForbiddenAdditionType.CAVEAT_REMOVAL,
                MMMLLMForbiddenAdditionType.GATE_BYPASS_LANGUAGE,
            ],
        ),
    ]
    if human_review_required:
        policies.append(
            MMMLLMRefusalPolicy(
                refusal_id="refuse-skip-human-review",
                trigger="proceed_without_human_review_when_required",
                required_response=(
                    "Cannot proceed without human review because the rendered response "
                    "requires it."
                ),
                reason="human review removal is forbidden when required",
                forbidden_additions=[MMMLLMForbiddenAdditionType.HUMAN_REVIEW_REMOVAL],
            )
        )
    return policies


def _policy_issue_codes(
    section_policies: list[MMMLLMSectionPolicy],
    refusal_policies: list[MMMLLMRefusalPolicy],
) -> list[MMMLLMResponseBoundaryIssueCode]:
    issues: list[MMMLLMResponseBoundaryIssueCode] = [
        MMMLLMResponseBoundaryIssueCode.PRESERVE_POLICY_ADDED,
    ]
    if any(p.must_preserve_verbatim for p in section_policies):
        issues.append(MMMLLMResponseBoundaryIssueCode.VERBATIM_POLICY_ADDED)
    if any(p.may_rewrite_lightly for p in section_policies):
        issues.append(MMMLLMResponseBoundaryIssueCode.REWRITE_POLICY_ADDED)
    if any(p.section_id == "cannot_say" for p in section_policies):
        issues.append(MMMLLMResponseBoundaryIssueCode.CANNOT_SAY_MUST_BE_PRESERVED)
    if any(p.section_id == "caveats" for p in section_policies):
        issues.append(MMMLLMResponseBoundaryIssueCode.CAVEATS_MUST_BE_PRESERVED)
    if any(p.section_id == "blocked_deferred_reasons" for p in section_policies):
        issues.append(MMMLLMResponseBoundaryIssueCode.BLOCKED_DEFERRED_STATUS_MUST_BE_PRESERVED)
    if any(p.section_id == "human_review_required" for p in section_policies):
        issues.append(MMMLLMResponseBoundaryIssueCode.HUMAN_REVIEW_MUST_BE_PRESERVED)
    if any(p.section_id == "evidence_references" for p in section_policies):
        issues.append(MMMLLMResponseBoundaryIssueCode.EVIDENCE_REFERENCES_MUST_BE_PRESERVED)
    if any(p.refusal_id == "refuse-budget-recommendation" for p in refusal_policies):
        issues.append(MMMLLMResponseBoundaryIssueCode.RECOMMENDATION_REQUEST_REFUSAL_ADDED)
    if any(p.refusal_id == "refuse-optimizer-simulator" for p in refusal_policies):
        issues.append(MMMLLMResponseBoundaryIssueCode.OPTIMIZER_SIMULATOR_REQUEST_REFUSAL_ADDED)
    return issues


def _enum_value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)
