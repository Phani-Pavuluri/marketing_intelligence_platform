"""Tests for MMM planning-answer envelope workflow."""

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
    MMMPlanningAnswerEnvelope,
    MMMPlanningAnswerEnvelopeIssueCode,
    MMMPlanningAnswerEnvelopeRequest,
    MMMPlanningAnswerEnvelopeStatus,
    MMMPlanningAnswerEvidenceReference,
    MMMPlanningAnswerEvidenceType,
)
from mip.workflows.mmm_planning_answer_envelope import (
    build_mmm_planning_answer_envelope,
    summarize_mmm_planning_answer_envelope,
)

_WORKFLOW_SOURCE = Path("src/mip/workflows/mmm_planning_answer_envelope.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/mmm_planning_answer_envelope.py")


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


def _build(
    eligibility: MMMPlanningAnswerEligibilityResult | None = None,
    *,
    evidence_references: list[MMMPlanningAnswerEvidenceReference] | None = None,
    include_default_boundaries: bool = True,
) -> MMMPlanningAnswerEnvelope:
    return build_mmm_planning_answer_envelope(
        MMMPlanningAnswerEnvelopeRequest(
            request_id="env-1",
            eligibility_result=eligibility,
            evidence_references=evidence_references or [],
            include_default_boundaries=include_default_boundaries,
            lineage={"caller": "test"},
        )
    )


def test_missing_eligibility_result_unknown() -> None:
    envelope = _build(None)
    assert envelope.answer_allowed is False
    assert envelope.status == MMMPlanningAnswerEnvelopeStatus.UNKNOWN
    assert MMMPlanningAnswerEnvelopeIssueCode.ELIGIBILITY_RESULT_MISSING in envelope.issues
    assert any(c.boundary == MMMPlanningAnswerClaimBoundary.CANNOT_SAY for c in envelope.cannot_say)


def test_eligibility_fields_preserved() -> None:
    eligibility = _eligibility(
        caveats=["warn"],
        gate_references=[
            MMMPlanningAnswerGateReference(
                gate_name="decision_surface",
                gate_status="pass",
                passed=True,
            )
        ],
        decision_surface_required=True,
        trust_review_required=True,
        human_review_required=True,
    )
    envelope = _build(eligibility)
    assert envelope.question_class == MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE
    assert envelope.answer_mode == MMMPlanningAnswerMode.DESCRIPTIVE
    assert envelope.answer_allowed is True
    assert envelope.caveats == ["warn"]
    assert envelope.decision_surface_required is True
    assert envelope.trust_review_required is True
    assert envelope.human_review_required is True
    assert envelope.external_run_id == "ext-run-1"
    assert envelope.model_artifact_id == "model-1"
    assert len(envelope.gate_references) == 1


def test_allowed_no_caveats_maps_ready_to_explain() -> None:
    envelope = _build(_eligibility(human_review_required=False, caveats=[]))
    assert envelope.status == MMMPlanningAnswerEnvelopeStatus.READY_TO_EXPLAIN


def test_allowed_with_caveats_maps_ready_with_caveats() -> None:
    envelope = _build(_eligibility(human_review_required=False, caveats=["diagnostic caveat"]))
    assert envelope.status == MMMPlanningAnswerEnvelopeStatus.READY_TO_EXPLAIN_WITH_CAVEATS


def test_human_review_maps_human_review_required() -> None:
    envelope = _build(_eligibility(human_review_required=True, caveats=["x"]))
    assert envelope.status == MMMPlanningAnswerEnvelopeStatus.HUMAN_REVIEW_REQUIRED


def test_blocked_eligibility_maps_blocked_envelope() -> None:
    envelope = _build(
        _eligibility(
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["artifact blocked"],
        )
    )
    assert envelope.status == MMMPlanningAnswerEnvelopeStatus.BLOCKED
    assert envelope.blocked_reasons == ["artifact blocked"]


def test_deferred_eligibility_maps_deferred_envelope() -> None:
    envelope = _build(
        _eligibility(
            answer_mode=MMMPlanningAnswerMode.DEFERRED,
            status=MMMPlanningAnswerEligibilityStatus.DEFERRED,
            answer_allowed=False,
            deferred_reasons=["pending DecisionSurface review"],
        )
    )
    assert envelope.status == MMMPlanningAnswerEnvelopeStatus.DEFERRED
    assert envelope.deferred_reasons


def test_evidence_references_preserved_and_defaults_added() -> None:
    supplied = MMMPlanningAnswerEvidenceReference(
        evidence_id="custom-ev",
        evidence_type=MMMPlanningAnswerEvidenceType.OTHER,
        source_id="custom",
    )
    envelope = _build(
        _eligibility(
            gate_references=[
                MMMPlanningAnswerGateReference(
                    gate_name="trust_report",
                    gate_status="pass",
                    passed=True,
                )
            ]
        ),
        evidence_references=[supplied],
    )
    ids = {ref.evidence_id for ref in envelope.evidence_references}
    assert "custom-ev" in ids
    assert "eligibility:elig-1" in ids
    assert "gate:trust_report" in ids
    assert "runtime:ext-run-1" in ids
    assert "model:model-1" in ids
    assert MMMPlanningAnswerEnvelopeIssueCode.EVIDENCE_REFERENCES_ADDED in envelope.issues


def test_descriptive_mode_boundaries() -> None:
    envelope = _build(_eligibility())
    assert any("descriptive" in c.statement.lower() for c in envelope.can_say)
    assert any("roi" in c.statement.lower() for c in envelope.cannot_say)


def test_diagnostic_mode_boundaries() -> None:
    envelope = _build(
        _eligibility(
            question_class=MMMPlanningQuestionClass.DIAGNOSTIC_DRIVER,
            answer_mode=MMMPlanningAnswerMode.DIAGNOSTIC,
            status=MMMPlanningAnswerEligibilityStatus.DIAGNOSTIC_ONLY,
            caveats=["diagnostic-only"],
            human_review_required=True,
        )
    )
    assert any("diagnostic" in c.statement.lower() for c in envelope.can_say)
    assert any("causal" in c.statement.lower() for c in envelope.cannot_say)


def test_scenario_comparison_boundaries_no_computation() -> None:
    envelope = _build(
        _eligibility(
            question_class=MMMPlanningQuestionClass.SCENARIO_COMPARISON,
            answer_mode=MMMPlanningAnswerMode.SCENARIO_COMPARISON,
            status=MMMPlanningAnswerEligibilityStatus.SCENARIO_ONLY,
            decision_surface_required=True,
            human_review_required=True,
        )
    )
    assert any("scenario" in c.statement.lower() for c in envelope.can_say)
    assert any("cannot compute" in c.statement.lower() for c in envelope.cannot_say)
    assert (
        MMMPlanningAnswerEnvelopeIssueCode.DECISION_SURFACE_REQUIRED_FOR_SCENARIO in envelope.issues
    )


def test_simulation_only_boundaries_no_execution() -> None:
    envelope = _build(
        _eligibility(
            question_class=MMMPlanningQuestionClass.SIMULATION_REQUEST,
            answer_mode=MMMPlanningAnswerMode.SIMULATION_ONLY,
            status=MMMPlanningAnswerEligibilityStatus.SIMULATION_ONLY,
            decision_surface_required=True,
            human_review_required=True,
        )
    )
    assert any("simulation" in c.statement.lower() for c in envelope.can_say)
    assert any("cannot run simulation" in c.statement.lower() for c in envelope.cannot_say)
    assert MMMPlanningAnswerEnvelopeIssueCode.NO_SIMULATOR_EXECUTION in envelope.issues


def test_recommendation_eligible_boundaries_no_generation() -> None:
    envelope = _build(
        _eligibility(
            question_class=MMMPlanningQuestionClass.RECOMMENDATION_REQUEST,
            answer_mode=MMMPlanningAnswerMode.RECOMMENDATION_ELIGIBLE,
            recommendation_contract_required=True,
            human_review_required=True,
        )
    )
    assert any("recommendation eligibility" in c.statement.lower() for c in envelope.can_say)
    assert any(
        "cannot generate recommendationcontract" in c.statement.lower() for c in envelope.cannot_say
    )
    assert (
        MMMPlanningAnswerEnvelopeIssueCode.RECOMMENDATION_CONTRACT_REQUIRED_FOR_RECOMMENDATION
        in envelope.issues
    )


def test_blocked_deferred_boundaries_explain_blockers() -> None:
    blocked = _build(
        _eligibility(
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["missing gate"],
        )
    )
    deferred = _build(
        _eligibility(
            answer_mode=MMMPlanningAnswerMode.DEFERRED,
            status=MMMPlanningAnswerEligibilityStatus.DEFERRED,
            answer_allowed=False,
            deferred_reasons=["pending review"],
        )
    )
    assert any("blocked or deferred" in c.statement.lower() for c in blocked.can_say)
    assert any("blocked or deferred" in c.statement.lower() for c in deferred.can_say)


def test_unsupported_numeric_claims_blocked() -> None:
    envelope = _build(_eligibility())
    assert MMMPlanningAnswerEnvelopeIssueCode.UNSUPPORTED_NUMERIC_CLAIMS_BLOCKED in envelope.issues
    assert any(
        "roi" in c.statement.lower() and "roas" in c.statement.lower() for c in envelope.cannot_say
    )


def test_recommendation_contract_required_for_recommendation_claims() -> None:
    envelope = _build(
        _eligibility(
            answer_mode=MMMPlanningAnswerMode.RECOMMENDATION_ELIGIBLE,
            recommendation_contract_required=True,
            human_review_required=True,
        )
    )
    assert any(c.required_gate == "recommendation" for c in envelope.cannot_say)


def test_decision_surface_required_for_scenario_simulation_claims() -> None:
    scenario = _build(
        _eligibility(
            answer_mode=MMMPlanningAnswerMode.SCENARIO_COMPARISON,
            decision_surface_required=True,
            human_review_required=True,
        )
    )
    assert any(c.required_gate == "decision_surface" for c in scenario.cannot_say)


def test_trust_review_required_for_trust_tier_claims() -> None:
    envelope = _build(_eligibility(trust_review_required=True, human_review_required=True))
    assert MMMPlanningAnswerEnvelopeIssueCode.TRUST_REVIEW_REQUIRED_FOR_PLANNING in (
        envelope.issues
    )
    assert any(c.required_gate == "trust_report" for c in envelope.cannot_say)


def test_lineage_preserved() -> None:
    envelope = _build(_eligibility())
    assert envelope.lineage.get("caller") == "test"
    assert envelope.lineage.get("upstream") == "eligibility"
    assert envelope.lineage.get("planning_answer_envelope_stage") == (
        "mmm_planning_answer_envelope"
    )


def test_summarize_returns_metadata_only() -> None:
    envelope = _build(_eligibility())
    summary = summarize_mmm_planning_answer_envelope(envelope)
    assert summary["answer_allowed"] is True
    assert "can_say_count" in summary
    assert "recommendation" not in summary
    assert "recommended_budget" not in summary


def test_no_forbidden_construction_in_sources() -> None:
    # forbidden tokens must not appear in envelope sources (string assert list)
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
    envelope = _build(_eligibility())
    assert MMMPlanningAnswerEnvelopeIssueCode.NO_DECISION_SURFACE_CONSTRUCTION in (envelope.issues)
    assert MMMPlanningAnswerEnvelopeIssueCode.NO_RECOMMENDATION_CONTRACT_GENERATION in (
        envelope.issues
    )
    assert MMMPlanningAnswerEnvelopeIssueCode.NO_CLAIM_AUTHORIZATION in envelope.issues
