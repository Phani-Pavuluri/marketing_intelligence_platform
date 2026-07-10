"""Tests for MMM planning-answer envelope contracts."""

from __future__ import annotations

from mip.contracts import (
    FORBIDDEN_MMM_PLANNING_ANSWER_ENVELOPE_FIELD_NAMES,
    RECOMMENDED_NEXT_MMM_PLANNING_ANSWER_ENVELOPE_CHECKPOINT_AUDIT_ARTIFACT,
    MMMPlanningAnswerClaimBoundary,
    MMMPlanningAnswerClaimStatement,
    MMMPlanningAnswerEnvelope,
    MMMPlanningAnswerEnvelopeIssueCode,
    MMMPlanningAnswerEnvelopeRequest,
    MMMPlanningAnswerEnvelopeStatus,
    MMMPlanningAnswerEvidenceReference,
    MMMPlanningAnswerEvidenceType,
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
    assert MMMPlanningAnswerEnvelopeStatus.READY_TO_EXPLAIN in (MMMPlanningAnswerEnvelopeStatus)
    assert MMMPlanningAnswerEnvelopeStatus.READY_TO_EXPLAIN_WITH_CAVEATS in (
        MMMPlanningAnswerEnvelopeStatus
    )
    assert MMMPlanningAnswerEnvelopeStatus.BLOCKED in MMMPlanningAnswerEnvelopeStatus
    assert MMMPlanningAnswerEnvelopeStatus.DEFERRED in MMMPlanningAnswerEnvelopeStatus
    assert MMMPlanningAnswerEnvelopeStatus.HUMAN_REVIEW_REQUIRED in (
        MMMPlanningAnswerEnvelopeStatus
    )
    assert MMMPlanningAnswerEnvelopeStatus.UNKNOWN in MMMPlanningAnswerEnvelopeStatus
    assert MMMPlanningAnswerClaimBoundary.CAN_SAY in MMMPlanningAnswerClaimBoundary
    assert MMMPlanningAnswerClaimBoundary.CANNOT_SAY in MMMPlanningAnswerClaimBoundary
    assert MMMPlanningAnswerClaimBoundary.CAN_SAY_WITH_CAVEAT in (MMMPlanningAnswerClaimBoundary)
    assert MMMPlanningAnswerClaimBoundary.REQUIRES_HUMAN_REVIEW in (MMMPlanningAnswerClaimBoundary)
    assert MMMPlanningAnswerClaimBoundary.REQUIRES_APPROVED_ARTIFACT in (
        MMMPlanningAnswerClaimBoundary
    )
    assert MMMPlanningAnswerEvidenceType.PLANNING_ANSWER_ELIGIBILITY in (
        MMMPlanningAnswerEvidenceType
    )
    assert MMMPlanningAnswerEvidenceType.DECISION_SURFACE_GATE in (MMMPlanningAnswerEvidenceType)
    assert MMMPlanningAnswerEnvelopeIssueCode.NO_RECOMMENDATION_GENERATION in (
        MMMPlanningAnswerEnvelopeIssueCode
    )
    assert MMMPlanningAnswerEnvelopeIssueCode.NO_OPTIMIZER_EXECUTION in (
        MMMPlanningAnswerEnvelopeIssueCode
    )


def test_evidence_reference_and_claim_statement_serialize() -> None:
    evidence = MMMPlanningAnswerEvidenceReference(
        evidence_id="ev-1",
        evidence_type=MMMPlanningAnswerEvidenceType.RUNTIME_RESULT,
        source_id="ext-1",
    )
    claim = MMMPlanningAnswerClaimStatement(
        claim_id="c-1",
        boundary=MMMPlanningAnswerClaimBoundary.CANNOT_SAY,
        statement="Cannot report ROI without approved artifact.",
        reason="unsupported numeric claims blocked",
        evidence_ids=["ev-1"],
    )
    assert evidence.model_dump()["evidence_id"] == "ev-1"
    assert claim.model_dump()["boundary"] == "cannot_say"


def test_request_and_envelope_serialize() -> None:
    request = MMMPlanningAnswerEnvelopeRequest(request_id="env-req-1")
    assert request.include_default_boundaries is True
    envelope = MMMPlanningAnswerEnvelope(
        request_id="env-req-1",
        status=MMMPlanningAnswerEnvelopeStatus.BLOCKED,
        question_class=MMMPlanningQuestionClass.UNKNOWN,
        answer_mode=MMMPlanningAnswerMode.BLOCKED,
    )
    payload = envelope.model_dump()
    assert payload["answer_allowed"] is False
    assert "recommendation" not in payload
    assert "recommended_budget" not in payload


def test_forbidden_fields_absent() -> None:
    for name in _FORBIDDEN_TOP_LEVEL:
        assert name in FORBIDDEN_MMM_PLANNING_ANSWER_ENVELOPE_FIELD_NAMES
        assert name not in MMMPlanningAnswerEnvelope.model_fields


def test_exports_from_mip_contracts() -> None:
    assert (
        RECOMMENDED_NEXT_MMM_PLANNING_ANSWER_ENVELOPE_CHECKPOINT_AUDIT_ARTIFACT
        == "MIP_MMM_PLANNING_ANSWER_ENVELOPE_CHECKPOINT_AUDIT_001"
    )
