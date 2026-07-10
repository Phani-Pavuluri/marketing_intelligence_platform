"""Tests for deterministic MMM planning response renderer."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.mmm_planning_answer_eligibility import (
    MMMPlanningAnswerEligibilityResult,
    MMMPlanningAnswerEligibilityStatus,
    MMMPlanningAnswerGateReference,
    MMMPlanningAnswerMode,
    MMMPlanningQuestionClass,
)
from mip.contracts.mmm_planning_answer_envelope import (
    MMMPlanningAnswerClaimBoundary,
    MMMPlanningAnswerClaimStatement,
    MMMPlanningAnswerEnvelope,
    MMMPlanningAnswerEnvelopeRequest,
    MMMPlanningAnswerEnvelopeStatus,
    MMMPlanningAnswerEvidenceReference,
    MMMPlanningAnswerEvidenceType,
)
from mip.reports.mmm_planning_response_renderer import (
    MMMPlanningResponseRenderIssueCode,
    render_mmm_planning_response,
    summarize_mmm_planning_rendered_response,
)
from mip.workflows.mmm_planning_answer_envelope import build_mmm_planning_answer_envelope

_RENDERER_SOURCE = Path("src/mip/reports/mmm_planning_response_renderer.py")


def _section_items(response: object, section_id: str) -> list[str]:
    sections = getattr(response, "sections")
    for section in sections:
        if section.section_id == section_id:
            return list(section.items)
    raise AssertionError(f"missing section {section_id}")


def _section_text(response: object, section_id: str) -> str:
    return " | ".join(_section_items(response, section_id)).lower()


def _eligibility(
    *,
    question_class: MMMPlanningQuestionClass = MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE,
    answer_mode: MMMPlanningAnswerMode = MMMPlanningAnswerMode.DESCRIPTIVE,
    status: MMMPlanningAnswerEligibilityStatus = (
        MMMPlanningAnswerEligibilityStatus.ANSWER_ELIGIBLE
    ),
    answer_allowed: bool = True,
    human_review_required: bool = False,
    decision_surface_required: bool = False,
    trust_review_required: bool = False,
    recommendation_contract_required: bool = False,
    caveats: list[str] | None = None,
    blocked_reasons: list[str] | None = None,
    deferred_reasons: list[str] | None = None,
    gate_references: list[MMMPlanningAnswerGateReference] | None = None,
) -> MMMPlanningAnswerEligibilityResult:
    return MMMPlanningAnswerEligibilityResult(
        request_id="elig-1",
        question_class=question_class,
        answer_mode=answer_mode,
        status=status,
        answer_allowed=answer_allowed,
        human_review_required=human_review_required,
        decision_surface_required=decision_surface_required,
        trust_review_required=trust_review_required,
        recommendation_contract_required=recommendation_contract_required,
        caveats=caveats or [],
        blocked_reasons=blocked_reasons or [],
        deferred_reasons=deferred_reasons or [],
        gate_references=gate_references or [],
        external_run_id="ext-run-1",
        model_artifact_id="model-1",
        lineage={"upstream": "eligibility"},
    )


def _envelope_from_eligibility(
    eligibility: MMMPlanningAnswerEligibilityResult | None = None,
    *,
    include_default_boundaries: bool = True,
) -> MMMPlanningAnswerEnvelope:
    return build_mmm_planning_answer_envelope(
        MMMPlanningAnswerEnvelopeRequest(
            request_id="env-1",
            eligibility_result=eligibility,
            include_default_boundaries=include_default_boundaries,
            lineage={"caller": "test"},
        )
    )


def _manual_envelope(**overrides: object) -> MMMPlanningAnswerEnvelope:
    base: dict[str, object] = {
        "request_id": "env-manual",
        "status": MMMPlanningAnswerEnvelopeStatus.READY_TO_EXPLAIN,
        "question_class": MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE,
        "answer_mode": MMMPlanningAnswerMode.DESCRIPTIVE,
        "answer_allowed": True,
        "human_review_required": False,
        "decision_surface_required": False,
        "trust_review_required": False,
        "recommendation_contract_required": False,
        "caveats": [],
        "blocked_reasons": [],
        "deferred_reasons": [],
        "gate_references": [],
        "evidence_references": [],
        "can_say": [
            MMMPlanningAnswerClaimStatement(
                claim_id="can-1",
                boundary=MMMPlanningAnswerClaimBoundary.CAN_SAY,
                statement=(
                    "Can explain descriptive performance status from eligibility metadata."
                ),
                reason="descriptive mode",
            )
        ],
        "cannot_say": [
            MMMPlanningAnswerClaimStatement(
                claim_id="cannot-numeric",
                boundary=MMMPlanningAnswerClaimBoundary.CANNOT_SAY,
                statement=(
                    "Cannot report ROI, ROAS, lift, or incrementality unless supplied by "
                    "an approved artifact."
                ),
                reason="unsupported numeric claims blocked",
            )
        ],
        "issues": [],
        "lineage": {"source": "manual"},
        "metadata": {},
    }
    base.update(overrides)
    return MMMPlanningAnswerEnvelope(**base)  # type: ignore[arg-type]


def test_missing_envelope_renders_blocked_unknown() -> None:
    response = render_mmm_planning_response(None)
    assert response.status == MMMPlanningAnswerEnvelopeStatus.UNKNOWN
    assert response.answer_allowed is False
    assert MMMPlanningResponseRenderIssueCode.ENVELOPE_MISSING in response.issues
    assert "missing envelope" in _section_text(response, "status")
    assert "cannot answer without a planning-answer envelope" in _section_text(
        response, "cannot_say"
    )
    assert "build or provide" in _section_text(response, "required_gates")


def test_ready_envelope_renders_status_section() -> None:
    envelope = _envelope_from_eligibility(_eligibility())
    response = render_mmm_planning_response(envelope)
    assert response.status == MMMPlanningAnswerEnvelopeStatus.READY_TO_EXPLAIN
    assert "READY_TO_EXPLAIN" in _section_items(response, "status")[0]
    assert MMMPlanningResponseRenderIssueCode.STATUS_RENDERED in response.issues


def test_answer_mode_rendered() -> None:
    envelope = _envelope_from_eligibility(_eligibility())
    response = render_mmm_planning_response(envelope)
    assert "DESCRIPTIVE" in _section_items(response, "answer_mode")[0]
    assert MMMPlanningResponseRenderIssueCode.ANSWER_MODE_RENDERED in response.issues


def test_can_say_rendered_from_envelope() -> None:
    envelope = _manual_envelope()
    response = render_mmm_planning_response(envelope)
    text = _section_text(response, "can_say")
    assert "descriptive performance status" in text
    assert MMMPlanningResponseRenderIssueCode.CAN_SAY_RENDERED in response.issues


def test_cannot_say_rendered_from_envelope() -> None:
    envelope = _manual_envelope()
    response = render_mmm_planning_response(envelope)
    text = _section_text(response, "cannot_say")
    assert "roi" in text
    assert MMMPlanningResponseRenderIssueCode.CANNOT_SAY_RENDERED in response.issues


def test_caveats_rendered() -> None:
    envelope = _manual_envelope(caveats=["Human review is required before downstream use."])
    response = render_mmm_planning_response(envelope)
    assert "Human review is required before downstream use." in _section_items(
        response, "caveats"
    )


def test_required_gates_rendered_from_booleans_and_refs() -> None:
    envelope = _manual_envelope(
        decision_surface_required=True,
        trust_review_required=True,
        recommendation_contract_required=True,
        gate_references=[
            MMMPlanningAnswerGateReference(
                gate_name="decision_surface",
                gate_status="required",
                required=True,
            )
        ],
    )
    response = render_mmm_planning_response(envelope)
    text = _section_text(response, "required_gates")
    assert "decisionsurface" in text.replace(" ", "")
    assert "trust review required" in text
    assert "recommendationcontract" in text.replace(" ", "")
    assert "gate reference: decision_surface" in text


def test_blocked_reasons_rendered() -> None:
    envelope = _manual_envelope(
        status=MMMPlanningAnswerEnvelopeStatus.BLOCKED,
        answer_mode=MMMPlanningAnswerMode.BLOCKED,
        answer_allowed=False,
        blocked_reasons=["artifact not ready"],
    )
    response = render_mmm_planning_response(envelope)
    assert "Blocked: artifact not ready" in _section_items(
        response, "blocked_deferred_reasons"
    )


def test_deferred_reasons_rendered() -> None:
    envelope = _manual_envelope(
        status=MMMPlanningAnswerEnvelopeStatus.DEFERRED,
        answer_mode=MMMPlanningAnswerMode.DEFERRED,
        answer_allowed=False,
        deferred_reasons=["awaiting external runtime"],
    )
    response = render_mmm_planning_response(envelope)
    assert "Deferred: awaiting external runtime" in _section_items(
        response, "blocked_deferred_reasons"
    )


def test_human_review_rendered_yes_no() -> None:
    yes_response = render_mmm_planning_response(
        _manual_envelope(human_review_required=True)
    )
    no_response = render_mmm_planning_response(
        _manual_envelope(human_review_required=False)
    )
    assert _section_items(yes_response, "human_review_required") == ["Yes"]
    assert _section_items(no_response, "human_review_required") == ["No"]


def test_evidence_references_rendered_metadata_only() -> None:
    envelope = _manual_envelope(
        evidence_references=[
            MMMPlanningAnswerEvidenceReference(
                evidence_id="ev-1",
                evidence_type=MMMPlanningAnswerEvidenceType.PLANNING_ANSWER_ELIGIBILITY,
                status="present",
                artifact_id="art-1",
            )
        ]
    )
    response = render_mmm_planning_response(envelope)
    text = _section_text(response, "evidence_references")
    assert "planning_answer_eligibility" in text
    assert "ev-1" in text
    assert "status=present" in text
    assert "artifact_id=art-1" in text


def test_lineage_preserved() -> None:
    envelope = _manual_envelope(lineage={"source": "manual", "trace": "abc"})
    response = render_mmm_planning_response(envelope)
    assert response.lineage["source"] == "manual"
    assert response.lineage["trace"] == "abc"
    assert response.lineage["source_envelope_request_id"] == "env-manual"
    assert MMMPlanningResponseRenderIssueCode.LINEAGE_PRESERVED in response.issues


def test_blocked_envelope_first_class() -> None:
    envelope = _envelope_from_eligibility(
        _eligibility(
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["blocked by gate"],
        )
    )
    response = render_mmm_planning_response(envelope)
    assert response.status == MMMPlanningAnswerEnvelopeStatus.BLOCKED
    assert "BLOCKED" in _section_items(response, "status")[0]
    assert "Blocked: blocked by gate" in _section_items(
        response, "blocked_deferred_reasons"
    )


def test_deferred_envelope_first_class() -> None:
    envelope = _envelope_from_eligibility(
        _eligibility(
            answer_mode=MMMPlanningAnswerMode.DEFERRED,
            status=MMMPlanningAnswerEligibilityStatus.DEFERRED,
            answer_allowed=False,
            deferred_reasons=["deferred for runtime"],
        )
    )
    response = render_mmm_planning_response(envelope)
    assert response.status == MMMPlanningAnswerEnvelopeStatus.DEFERRED
    assert "DEFERRED" in _section_items(response, "status")[0]


def test_diagnostic_caveated_envelope_no_causal_claims_in_can_say() -> None:
    envelope = _envelope_from_eligibility(
        _eligibility(
            question_class=MMMPlanningQuestionClass.DIAGNOSTIC_DRIVER,
            answer_mode=MMMPlanningAnswerMode.DIAGNOSTIC,
            status=MMMPlanningAnswerEligibilityStatus.DIAGNOSTIC_ONLY,
            caveats=["diagnostic only"],
        )
    )
    response = render_mmm_planning_response(envelope)
    can_say = _section_text(response, "can_say")
    assert "causal lift" not in can_say
    assert "proves causal" not in can_say
    assert "diagnostic only" in _section_text(response, "caveats")


def test_scenario_envelope_does_not_compute_scenario_output() -> None:
    envelope = _envelope_from_eligibility(
        _eligibility(
            question_class=MMMPlanningQuestionClass.SCENARIO_COMPARISON,
            answer_mode=MMMPlanningAnswerMode.SCENARIO_COMPARISON,
            status=MMMPlanningAnswerEligibilityStatus.SCENARIO_ONLY,
            decision_surface_required=True,
        )
    )
    response = render_mmm_planning_response(envelope)
    can_say = _section_text(response, "can_say")
    cannot_say = _section_text(response, "cannot_say")
    assert "scenario" in can_say or "scenario" in cannot_say
    assert "computed scenario" not in can_say
    assert "DecisionSurface gate/reference required." in _section_items(
        response, "required_gates"
    )
    assert (
        MMMPlanningResponseRenderIssueCode.SCENARIO_SIMULATION_CLAIMS_NOT_RENDERED_WITHOUT_DECISION_SURFACE
        in response.issues
    )


def test_simulation_envelope_does_not_execute_simulation() -> None:  # must not
    envelope = _envelope_from_eligibility(
        _eligibility(
            question_class=MMMPlanningQuestionClass.SIMULATION_REQUEST,
            answer_mode=MMMPlanningAnswerMode.SIMULATION_ONLY,
            status=MMMPlanningAnswerEligibilityStatus.SIMULATION_ONLY,
            decision_surface_required=True,
        )
    )
    response = render_mmm_planning_response(envelope)
    can_say = _section_text(response, "can_say")
    assert "executed simulation" not in can_say  # must not
    assert MMMPlanningResponseRenderIssueCode.NO_SIMULATOR_EXECUTION in response.issues  # must not


def test_recommendation_eligible_does_not_generate_recommendation() -> None:
    envelope = _envelope_from_eligibility(
        _eligibility(
            question_class=MMMPlanningQuestionClass.RECOMMENDATION_REQUEST,
            answer_mode=MMMPlanningAnswerMode.RECOMMENDATION_ELIGIBLE,
            recommendation_contract_required=True,
        )
    )
    response = render_mmm_planning_response(envelope)
    can_say = _section_text(response, "can_say")
    assert "recommended budget" not in can_say
    assert "RecommendationContract gate/reference required." in _section_items(
        response, "required_gates"
    )
    assert response.metadata.get("no_recommendation_generated") is True


def test_unsupported_numeric_claims_only_under_cannot_say() -> None:
    envelope = _manual_envelope()
    response = render_mmm_planning_response(envelope)
    can_say = _section_text(response, "can_say")
    cannot_say = _section_text(response, "cannot_say")
    for token in ("roi", "roas", "lift", "incrementality"):
        assert token not in can_say
        assert token in cannot_say
    assert (
        MMMPlanningResponseRenderIssueCode.UNSUPPORTED_NUMERIC_CLAIMS_NOT_RENDERED
        in response.issues
    )


def test_no_decision_surface_trust_recommendation_construction() -> None:
    source = _RENDERER_SOURCE.read_text(encoding="utf-8")  # assert source scan only
    assert "DecisionSurface(" not in source  # no DecisionSurface
    assert "TrustReport(" not in source  # TrustReport
    assert "RecommendationContract(" not in source  # RecommendationContract
    response = render_mmm_planning_response(_manual_envelope())
    assert MMMPlanningResponseRenderIssueCode.NO_DECISION_SURFACE_CONSTRUCTION in response.issues
    assert MMMPlanningResponseRenderIssueCode.NO_TRUST_REPORT_CONSTRUCTION in response.issues
    assert (
        MMMPlanningResponseRenderIssueCode.NO_RECOMMENDATION_CONTRACT_GENERATION
        in response.issues
    )


def test_no_optimizer_or_budget_math_issue_codes() -> None:  # must not
    response = render_mmm_planning_response(_manual_envelope())
    assert MMMPlanningResponseRenderIssueCode.NO_OPTIMIZER_EXECUTION in response.issues  # must not
    assert MMMPlanningResponseRenderIssueCode.NO_SIMULATOR_EXECUTION in response.issues  # must not
    assert (
        MMMPlanningResponseRenderIssueCode.NO_BUDGET_ALLOCATION_CALCULATION in response.issues
    )
    assert (
        MMMPlanningResponseRenderIssueCode.NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION
        in response.issues
    )
    payload = response.model_dump()
    for forbidden in (
        "spend_delta",
        "delta_mu",
        "roi",
        "roas",
        "lift",
        "incrementality",
        "optimal_budget",
        "marginal_roi",
        "recommended_budget",
    ):
        assert forbidden not in payload


def test_no_artifact_model_loading_execution_fitting() -> None:
    response = render_mmm_planning_response(_manual_envelope())
    assert MMMPlanningResponseRenderIssueCode.NO_ARTIFACT_LOADING in response.issues
    assert MMMPlanningResponseRenderIssueCode.NO_MODEL_LOADING in response.issues
    assert MMMPlanningResponseRenderIssueCode.NO_MODEL_EXECUTION in response.issues
    assert MMMPlanningResponseRenderIssueCode.NO_MMM_FITTING in response.issues
    source = _RENDERER_SOURCE.read_text(encoding="utf-8")  # assert source scan only
    # forbidden tokens must not appear in renderer source
    for token in ("open(", "read_text", "json.load", "pickle", "joblib", "load_model"):  # forbidden
        assert token not in source  # forbidden


def test_no_provider_behavior_change() -> None:  # No LLM
    response = render_mmm_planning_response(_manual_envelope())
    assert MMMPlanningResponseRenderIssueCode.NO_LLM_CALL in response.issues  # No LLM
    assert (
        MMMPlanningResponseRenderIssueCode.NO_LLM_PROVIDER_BEHAVIOR_CHANGE in response.issues
    )
    assert response.metadata.get("no_llm_call") is True
    source = _RENDERER_SOURCE.read_text(encoding="utf-8")  # assert source scan only
    for token in ("ChatOpenAI", "anthropic", "chat.completions", "completion("):  # No LLM
        assert token not in source  # forbidden
    assert "from mip.llm" not in source  # No LLM
    assert "import openai" not in source.lower()  # No LLM


def test_summary_helper_returns_counts_only() -> None:
    response = render_mmm_planning_response(_manual_envelope())
    summary = summarize_mmm_planning_rendered_response(response)
    assert summary["status"] == MMMPlanningAnswerEnvelopeStatus.READY_TO_EXPLAIN.value
    assert summary["answer_mode"] == MMMPlanningAnswerMode.DESCRIPTIVE.value
    assert summary["answer_allowed"] is True
    assert summary["human_review_required"] is False
    assert summary["section_count"] == 9
    assert isinstance(summary["can_say_item_count"], int)
    assert isinstance(summary["cannot_say_item_count"], int)
    assert isinstance(summary["evidence_reference_count"], int)
    assert isinstance(summary["issue_count"], int)
    assert "recommend" not in str(summary).lower()
