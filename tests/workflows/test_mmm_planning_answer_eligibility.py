"""Tests for MMM planning-answer eligibility workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.mmm_artifact_governance_use_readiness import (
    MMMArtifactGovernanceUseReadinessResult,
    MMMArtifactGovernanceUseReadinessStatus,
    MMMArtifactUseReadiness,
)
from mip.contracts.mmm_planning_answer_eligibility import (
    MMMPlanningAnswerEligibilityIssueCode,
    MMMPlanningAnswerEligibilityRequest,
    MMMPlanningAnswerEligibilityResult,
    MMMPlanningAnswerEligibilityStatus,
    MMMPlanningAnswerGateReference,
    MMMPlanningAnswerMode,
    MMMPlanningQuestionClass,
)
from mip.workflows.mmm_planning_answer_eligibility import (
    evaluate_mmm_planning_answer_eligibility,
    summarize_mmm_planning_answer_eligibility,
)

_WORKFLOW_SOURCE = Path("src/mip/workflows/mmm_planning_answer_eligibility.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/mmm_planning_answer_eligibility.py")


def _readiness(
    *,
    status: MMMArtifactGovernanceUseReadinessStatus = (
        MMMArtifactGovernanceUseReadinessStatus.READY_FOR_GOVERNANCE_REVIEW
    ),
    use_readiness: MMMArtifactUseReadiness = MMMArtifactUseReadiness.PLANNING_READY,
    planning_ready: bool = True,
    diagnostic_only: bool = False,
    ready_for_trust_report_review: bool = True,
    ready_for_decision_surface_review: bool = True,
    ready_for_diagnostic_review: bool = True,
    human_review_required: bool = False,
    blocked_reasons: list[str] | None = None,
    warnings: list[str] | None = None,
) -> MMMArtifactGovernanceUseReadinessResult:
    return MMMArtifactGovernanceUseReadinessResult(
        request_id="gov-1",
        status=status,
        use_readiness=use_readiness,
        planning_ready=planning_ready,
        diagnostic_only=diagnostic_only,
        ready_for_trust_report_review=ready_for_trust_report_review,
        ready_for_decision_surface_review=ready_for_decision_surface_review,
        ready_for_diagnostic_review=ready_for_diagnostic_review,
        human_review_required=human_review_required,
        blocked_reasons=blocked_reasons or [],
        warnings=warnings or [],
        external_run_id="ext-run-1",
        model_artifact_id="model-1",
        lineage={"upstream": "governance_use_readiness"},
    )


def _gate(
    name: str,
    *,
    passed: bool = True,
    required: bool = True,
    blocked_reasons: list[str] | None = None,
) -> MMMPlanningAnswerGateReference:
    return MMMPlanningAnswerGateReference(
        gate_name=name,
        gate_status="pass" if passed else "block",
        passed=passed,
        required=required,
        blocked_reasons=blocked_reasons or ([] if passed else ["gate blocked"]),
        metadata={"metadata_only": True},
    )


def _evaluate(
    *,
    question_class: MMMPlanningQuestionClass,
    readiness: MMMArtifactGovernanceUseReadinessResult | None = None,
    decision_surface_gate: MMMPlanningAnswerGateReference | None = None,
    trust_report_gate: MMMPlanningAnswerGateReference | None = None,
    recommendation_gate: MMMPlanningAnswerGateReference | None = None,
    require_trust_review_for_planning: bool = True,
    require_decision_surface_for_scenario: bool = True,
    require_recommendation_gate_for_recommendation: bool = True,
    allow_descriptive_without_decision_surface: bool = True,
    allow_diagnostic_without_decision_surface: bool = True,
) -> MMMPlanningAnswerEligibilityResult:
    return evaluate_mmm_planning_answer_eligibility(
        MMMPlanningAnswerEligibilityRequest(
            request_id="pae-1",
            question_class=question_class,
            question_text="test question",
            artifact_use_readiness=readiness,
            decision_surface_gate=decision_surface_gate,
            trust_report_gate=trust_report_gate,
            recommendation_gate=recommendation_gate,
            require_trust_review_for_planning=require_trust_review_for_planning,
            require_decision_surface_for_scenario=require_decision_surface_for_scenario,
            require_recommendation_gate_for_recommendation=(
                require_recommendation_gate_for_recommendation
            ),
            allow_descriptive_without_decision_surface=allow_descriptive_without_decision_surface,
            allow_diagnostic_without_decision_surface=allow_diagnostic_without_decision_surface,
            lineage={"caller": "test"},
        )
    )


def test_missing_artifact_readiness_blocks() -> None:
    result = _evaluate(question_class=MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE)
    assert result.answer_allowed is False
    assert result.answer_mode == MMMPlanningAnswerMode.BLOCKED
    assert result.status == MMMPlanningAnswerEligibilityStatus.BLOCKED
    assert MMMPlanningAnswerEligibilityIssueCode.ARTIFACT_USE_READINESS_MISSING in result.issues


def test_unknown_question_class_defers() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.UNKNOWN,
        readiness=_readiness(),
    )
    assert result.answer_allowed is False
    assert result.status == MMMPlanningAnswerEligibilityStatus.UNKNOWN
    assert result.answer_mode == MMMPlanningAnswerMode.DEFERRED


def test_descriptive_allowed_with_planning_ready() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE,
        readiness=_readiness(),
    )
    assert result.answer_allowed is True
    assert result.answer_mode == MMMPlanningAnswerMode.DESCRIPTIVE
    assert result.status == MMMPlanningAnswerEligibilityStatus.ANSWER_ELIGIBLE
    assert MMMPlanningAnswerEligibilityIssueCode.DESCRIPTIVE_ANSWER_ALLOWED in result.issues


def test_descriptive_allowed_with_diagnostic_only_plus_caveats() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE,
        readiness=_readiness(
            status=MMMArtifactGovernanceUseReadinessStatus.DIAGNOSTIC_ONLY,
            use_readiness=MMMArtifactUseReadiness.DIAGNOSTIC_ONLY,
            planning_ready=False,
            diagnostic_only=True,
            ready_for_decision_surface_review=False,
        ),
    )
    assert result.answer_allowed is True
    assert result.answer_mode == MMMPlanningAnswerMode.DESCRIPTIVE
    assert result.status == MMMPlanningAnswerEligibilityStatus.ANSWER_ELIGIBLE_WITH_CAVEATS
    assert result.caveats
    assert result.human_review_required is True


def test_diagnostic_allowed_with_diagnostic_only() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.DIAGNOSTIC_DRIVER,
        readiness=_readiness(
            status=MMMArtifactGovernanceUseReadinessStatus.DIAGNOSTIC_ONLY,
            use_readiness=MMMArtifactUseReadiness.DIAGNOSTIC_ONLY,
            planning_ready=False,
            diagnostic_only=True,
            ready_for_decision_surface_review=False,
        ),
    )
    assert result.answer_allowed is True
    assert result.answer_mode == MMMPlanningAnswerMode.DIAGNOSTIC
    assert result.status == MMMPlanningAnswerEligibilityStatus.DIAGNOSTIC_ONLY
    assert result.caveats
    assert MMMPlanningAnswerEligibilityIssueCode.CAVEATS_REQUIRED in result.issues


def test_scenario_requires_planning_ready() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.SCENARIO_COMPARISON,
        readiness=_readiness(
            planning_ready=False,
            diagnostic_only=True,
            use_readiness=MMMArtifactUseReadiness.DIAGNOSTIC_ONLY,
            status=MMMArtifactGovernanceUseReadinessStatus.DIAGNOSTIC_ONLY,
        ),
    )
    assert result.answer_allowed is False
    assert result.answer_mode == MMMPlanningAnswerMode.BLOCKED
    assert "planning-ready" in result.blocked_reasons[0]


def test_scenario_requires_decision_surface_route_or_gate() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.SCENARIO_COMPARISON,
        readiness=_readiness(ready_for_decision_surface_review=False),
    )
    assert result.answer_allowed is False
    assert result.decision_surface_required is True
    assert result.answer_mode == MMMPlanningAnswerMode.BLOCKED


def test_scenario_defers_when_route_exists_but_gate_not_passed() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.SCENARIO_COMPARISON,
        readiness=_readiness(ready_for_decision_surface_review=True),
    )
    assert result.answer_allowed is False
    assert result.status == MMMPlanningAnswerEligibilityStatus.DEFERRED
    assert result.answer_mode == MMMPlanningAnswerMode.SCENARIO_COMPARISON
    assert result.human_review_required is True


def test_scenario_allowed_when_decision_surface_gate_passes() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.SCENARIO_COMPARISON,
        readiness=_readiness(),
        decision_surface_gate=_gate("decision_surface", passed=True),
    )
    assert result.answer_allowed is True
    assert result.answer_mode == MMMPlanningAnswerMode.SCENARIO_COMPARISON
    assert result.status == MMMPlanningAnswerEligibilityStatus.SCENARIO_ONLY
    assert result.human_review_required is True


def test_simulation_is_simulation_only_no_recommendation() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.SIMULATION_REQUEST,
        readiness=_readiness(),
        decision_surface_gate=_gate("decision_surface", passed=True),
    )
    assert result.answer_mode == MMMPlanningAnswerMode.SIMULATION_ONLY
    assert result.recommendation_contract_required is False
    assert result.answer_allowed is True
    assert "no recommendation" in " ".join(result.caveats).lower()


def test_simulation_defers_if_decision_surface_support_missing() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.SIMULATION_REQUEST,
        readiness=_readiness(ready_for_decision_surface_review=False),
    )
    assert result.answer_allowed is False
    assert result.answer_mode == MMMPlanningAnswerMode.DEFERRED
    assert result.status == MMMPlanningAnswerEligibilityStatus.DEFERRED


def test_optimization_does_not_execute_optimizer() -> None:  # must not
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.OPTIMIZATION_REQUEST,
        readiness=_readiness(),
    )
    assert result.answer_allowed is False
    assert (
        MMMPlanningAnswerEligibilityIssueCode.OPTIMIZATION_REQUIRES_EXTERNAL_RUNTIME_OR_DECISION_SURFACE
        in result.issues
    )
    assert MMMPlanningAnswerEligibilityIssueCode.NO_OPTIMIZER_EXECUTION in result.issues
    assert result.status == MMMPlanningAnswerEligibilityStatus.RECOMMENDATION_REQUIRES_GATES


def test_recommendation_blocked_without_recommendation_gate() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.RECOMMENDATION_REQUEST,
        readiness=_readiness(),
        decision_surface_gate=_gate("decision_surface"),
        trust_report_gate=_gate("trust_report"),
    )
    assert result.answer_allowed is False
    assert result.status == MMMPlanningAnswerEligibilityStatus.RECOMMENDATION_REQUIRES_GATES
    assert result.recommendation_contract_required is True
    assert MMMPlanningAnswerEligibilityIssueCode.RECOMMENDATION_GATE_MISSING in result.issues


def test_recommendation_blocked_without_trust_gate() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.RECOMMENDATION_REQUEST,
        readiness=_readiness(),
        decision_surface_gate=_gate("decision_surface"),
        recommendation_gate=_gate("recommendation"),
    )
    assert result.answer_allowed is False
    assert MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_TRUST_GATE in result.issues


def test_recommendation_blocked_without_decision_surface_gate() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.RECOMMENDATION_REQUEST,
        readiness=_readiness(),
        trust_report_gate=_gate("trust_report"),
        recommendation_gate=_gate("recommendation"),
    )
    assert result.answer_allowed is False
    assert MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_DECISION_SURFACE_GATE in (
        result.issues
    )


def test_recommendation_eligible_only_when_all_gates_pass() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.RECOMMENDATION_REQUEST,
        readiness=_readiness(),
        decision_surface_gate=_gate("decision_surface"),
        trust_report_gate=_gate("trust_report"),
        recommendation_gate=_gate("recommendation"),
    )
    assert result.answer_allowed is True
    assert result.answer_mode == MMMPlanningAnswerMode.RECOMMENDATION_ELIGIBLE
    assert result.status == MMMPlanningAnswerEligibilityStatus.ANSWER_ELIGIBLE
    assert MMMPlanningAnswerEligibilityIssueCode.RECOMMENDATION_ALLOWED_BY_GATES in result.issues
    assert result.recommendation_contract_required is True
    assert result.human_review_required is True


def test_artifact_blocked_state_blocks_answer() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE,
        readiness=_readiness(
            status=MMMArtifactGovernanceUseReadinessStatus.BLOCKED,
            use_readiness=MMMArtifactUseReadiness.BLOCKED,
            planning_ready=False,
            blocked_reasons=["promotion blocked"],
        ),
    )
    assert result.answer_allowed is False
    assert result.answer_mode == MMMPlanningAnswerMode.BLOCKED
    assert MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_ARTIFACT_READINESS in result.issues


def test_artifact_deferred_state_defers_answer() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE,
        readiness=_readiness(
            status=MMMArtifactGovernanceUseReadinessStatus.DEFERRED,
            use_readiness=MMMArtifactUseReadiness.DEFERRED,
            planning_ready=False,
        ),
    )
    assert result.answer_allowed is False
    assert result.answer_mode == MMMPlanningAnswerMode.DEFERRED
    assert result.status == MMMPlanningAnswerEligibilityStatus.DEFERRED


def test_human_review_required_for_scenario_simulation_recommendation() -> None:
    scenario = _evaluate(
        question_class=MMMPlanningQuestionClass.SCENARIO_COMPARISON,
        readiness=_readiness(),
        decision_surface_gate=_gate("decision_surface"),
    )
    simulation = _evaluate(
        question_class=MMMPlanningQuestionClass.SIMULATION_REQUEST,
        readiness=_readiness(),
        decision_surface_gate=_gate("decision_surface"),
    )
    rec_result = _evaluate(  # recommendation_gate path covered elsewhere
        question_class=MMMPlanningQuestionClass.RECOMMENDATION_REQUEST,
        readiness=_readiness(),
        decision_surface_gate=_gate("decision_surface"),
        trust_report_gate=_gate("trust_report"),
        recommendation_gate=_gate("recommendation"),
    )
    assert scenario.human_review_required is True
    assert simulation.human_review_required is True
    assert rec_result.human_review_required is True


def test_caveats_required_for_diagnostic_only_answers() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.DIAGNOSTIC_DRIVER,
        readiness=_readiness(
            planning_ready=False,
            diagnostic_only=True,
            use_readiness=MMMArtifactUseReadiness.DIAGNOSTIC_ONLY,
            status=MMMArtifactGovernanceUseReadinessStatus.DIAGNOSTIC_ONLY,
        ),
    )
    assert result.caveats
    assert MMMPlanningAnswerEligibilityIssueCode.CAVEATS_REQUIRED in result.issues


def test_lineage_preserved() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE,
        readiness=_readiness(),
    )
    assert result.lineage.get("caller") == "test"
    assert result.lineage.get("planning_answer_eligibility_stage") == (
        "mmm_planning_answer_eligibility"
    )
    assert result.external_run_id == "ext-run-1"
    assert result.model_artifact_id == "model-1"


def test_gate_references_preserved_metadata_only() -> None:
    ds = _gate("decision_surface")
    trust = _gate("trust_report")
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.SCENARIO_COMPARISON,
        readiness=_readiness(),
        decision_surface_gate=ds,
        trust_report_gate=trust,
    )
    names = {g.gate_name for g in result.gate_references}
    assert names == {"decision_surface", "trust_report"}
    assert all(g.metadata.get("metadata_only") is True for g in result.gate_references)


def test_summarize_returns_metadata_only() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE,
        readiness=_readiness(),
    )
    summary = summarize_mmm_planning_answer_eligibility(result)
    assert summary["answer_allowed"] is True
    assert "recommendation" not in summary
    assert "recommended_budget" not in summary


def test_no_forbidden_construction_in_sources() -> None:
    # forbidden tokens must not appear in gate sources (string assert list)
    forbidden = (
        "DecisionSurface(",  # forbidden
        "TrustReport(",  # forbidden
        "RecommendationContract(",  # forbidden
        "open(",  # forbidden
        "read_text",  # forbidden
        "read_bytes",  # forbidden
        "json.load",  # forbidden
        "pandas",  # forbidden
        "pd.read",  # forbidden
        "import requests",  # forbidden
        "import httpx",  # forbidden
        "import pickle",  # forbidden
        "import joblib",  # forbidden
        "load_model(",  # forbidden
        ".fit(",  # forbidden
        ".predict(",  # forbidden
        ".sample(",  # forbidden
    )
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        for line in path.read_text(encoding="utf-8").splitlines():  # forbidden source scan
            if line.strip().startswith("#"):
                continue
            for token in forbidden:
                assert token not in line, f"{token} in {path}: {line}"


def test_boundary_issue_codes_present() -> None:
    result = _evaluate(
        question_class=MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE,
        readiness=_readiness(),
    )
    assert MMMPlanningAnswerEligibilityIssueCode.NO_DECISION_SURFACE_CONSTRUCTION in (
        result.issues
    )
    assert MMMPlanningAnswerEligibilityIssueCode.NO_RECOMMENDATION_CONTRACT_GENERATION in (
        result.issues
    )
    assert MMMPlanningAnswerEligibilityIssueCode.NO_OPTIMIZER_EXECUTION in result.issues
    assert MMMPlanningAnswerEligibilityIssueCode.NO_CLAIM_AUTHORIZATION in result.issues
