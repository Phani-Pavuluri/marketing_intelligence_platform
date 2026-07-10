"""MMM planning-answer envelope builder (metadata only)."""

from __future__ import annotations

from mip.contracts.mmm_planning_answer_eligibility import (
    MMMPlanningAnswerEligibilityResult,
    MMMPlanningAnswerGateReference,
    MMMPlanningAnswerMode,
    MMMPlanningQuestionClass,
)
from mip.contracts.mmm_planning_answer_envelope import (
    MMMPlanningAnswerClaimBoundary,
    MMMPlanningAnswerClaimStatement,
    MMMPlanningAnswerEnvelope,
    MMMPlanningAnswerEnvelopeIssueCode,
    MMMPlanningAnswerEnvelopeRequest,
    MMMPlanningAnswerEnvelopeStatus,
    MMMPlanningAnswerEvidenceReference,
    MMMPlanningAnswerEvidenceType,
)

_BOUNDARY_ISSUES = (
    MMMPlanningAnswerEnvelopeIssueCode.LINEAGE_PRESERVED,
    MMMPlanningAnswerEnvelopeIssueCode.NO_DECISION_SURFACE_CONSTRUCTION,
    MMMPlanningAnswerEnvelopeIssueCode.NO_DECISION_SURFACE_EXECUTION,
    MMMPlanningAnswerEnvelopeIssueCode.NO_TRUST_REPORT_CONSTRUCTION,
    MMMPlanningAnswerEnvelopeIssueCode.NO_TRUST_REPORT_BYPASS,
    MMMPlanningAnswerEnvelopeIssueCode.NO_RECOMMENDATION_CONTRACT_GENERATION,
    MMMPlanningAnswerEnvelopeIssueCode.NO_RECOMMENDATION_GENERATION,
    MMMPlanningAnswerEnvelopeIssueCode.NO_OPTIMIZER_EXECUTION,
    MMMPlanningAnswerEnvelopeIssueCode.NO_SIMULATOR_EXECUTION,
    MMMPlanningAnswerEnvelopeIssueCode.NO_BUDGET_ALLOCATION_CALCULATION,
    MMMPlanningAnswerEnvelopeIssueCode.NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION,
    MMMPlanningAnswerEnvelopeIssueCode.NO_ARTIFACT_LOADING,
    MMMPlanningAnswerEnvelopeIssueCode.NO_MODEL_LOADING,
    MMMPlanningAnswerEnvelopeIssueCode.NO_MODEL_EXECUTION,
    MMMPlanningAnswerEnvelopeIssueCode.NO_MMM_FITTING,
    MMMPlanningAnswerEnvelopeIssueCode.NO_CLAIM_AUTHORIZATION,
    MMMPlanningAnswerEnvelopeIssueCode.NO_LLM_PROVIDER_BEHAVIOR_CHANGE,
)


def build_mmm_planning_answer_envelope(
    request: MMMPlanningAnswerEnvelopeRequest,
) -> MMMPlanningAnswerEnvelope:
    """Package eligibility into a metadata-only planning-answer response boundary."""
    lineage = {
        **request.lineage,
        "planning_answer_envelope_stage": "mmm_planning_answer_envelope",
    }
    issues: list[MMMPlanningAnswerEnvelopeIssueCode] = list(_BOUNDARY_ISSUES)

    if request.eligibility_result is None:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.ELIGIBILITY_RESULT_MISSING)
        missing_cannot_say = [
            _claim(
                claim_id="missing-eligibility",
                boundary=MMMPlanningAnswerClaimBoundary.CANNOT_SAY,
                statement=(
                    "Cannot explain an MMM planning answer without an eligibility result."
                ),
                reason="eligibility_result is missing",
            )
        ]
        if request.include_default_boundaries:
            missing_cannot_say.extend(_universal_cannot_say(evidence_ids=[]))
            issues.append(MMMPlanningAnswerEnvelopeIssueCode.CANNOT_SAY_BOUNDARY_ADDED)
            issues.append(
                MMMPlanningAnswerEnvelopeIssueCode.UNSUPPORTED_NUMERIC_CLAIMS_BLOCKED
            )
            issues.append(
                MMMPlanningAnswerEnvelopeIssueCode.OPTIMIZER_SIMULATOR_CLAIMS_BLOCKED
            )
        return MMMPlanningAnswerEnvelope(
            request_id=request.request_id,
            status=MMMPlanningAnswerEnvelopeStatus.UNKNOWN,
            question_class=MMMPlanningQuestionClass.UNKNOWN,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            answer_allowed=False,
            cannot_say=missing_cannot_say,
            issues=list(dict.fromkeys(issues)),
            lineage=lineage,
            metadata={
                **request.metadata,
                "metadata_only_envelope": True,
                "no_recommendation_generated": True,
            },
        )

    eligibility = request.eligibility_result
    issues.append(MMMPlanningAnswerEnvelopeIssueCode.ELIGIBILITY_RESULT_PRESENT)
    issues.append(MMMPlanningAnswerEnvelopeIssueCode.ANSWER_MODE_PRESERVED)

    if eligibility.answer_allowed:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.ANSWER_ALLOWED)
    elif eligibility.answer_mode == MMMPlanningAnswerMode.DEFERRED or eligibility.deferred_reasons:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.ANSWER_DEFERRED)
    else:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.ANSWER_BLOCKED)

    if eligibility.caveats:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.CAVEATS_PRESERVED)
    if eligibility.blocked_reasons:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.BLOCKED_REASONS_PRESERVED)
    if eligibility.deferred_reasons:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.DEFERRED_REASONS_PRESERVED)
    if eligibility.gate_references:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.GATE_REFERENCES_PRESERVED)
    if eligibility.human_review_required:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.HUMAN_REVIEW_REQUIRED_PRESERVED)

    evidence_refs = _build_evidence_references(request, eligibility)
    if evidence_refs:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.EVIDENCE_REFERENCES_ADDED)

    status = _map_status(eligibility)
    can_say: list[MMMPlanningAnswerClaimStatement] = []
    cannot_say: list[MMMPlanningAnswerClaimStatement] = []

    if request.include_default_boundaries:
        evidence_ids = [ref.evidence_id for ref in evidence_refs]
        can_say, cannot_say, boundary_issues = _build_boundaries(
            eligibility=eligibility,
            evidence_ids=evidence_ids,
        )
        issues.extend(boundary_issues)

    return MMMPlanningAnswerEnvelope(
        request_id=request.request_id,
        status=status,
        question_class=eligibility.question_class,
        answer_mode=eligibility.answer_mode,
        answer_allowed=eligibility.answer_allowed,
        human_review_required=eligibility.human_review_required,
        decision_surface_required=eligibility.decision_surface_required,
        trust_review_required=eligibility.trust_review_required,
        recommendation_contract_required=eligibility.recommendation_contract_required,
        caveats=list(eligibility.caveats),
        blocked_reasons=list(eligibility.blocked_reasons),
        deferred_reasons=list(eligibility.deferred_reasons),
        gate_references=list(eligibility.gate_references),
        evidence_references=evidence_refs,
        can_say=can_say,
        cannot_say=cannot_say,
        issues=list(dict.fromkeys(issues)),
        external_run_id=eligibility.external_run_id,
        model_artifact_id=eligibility.model_artifact_id,
        lineage={**eligibility.lineage, **lineage},
        metadata={
            **eligibility.metadata,
            **request.metadata,
            "metadata_only_envelope": True,
            "no_recommendation_generated": True,
            "eligibility_request_id": eligibility.request_id,
            "eligibility_status": _enum_value(eligibility.status),
        },
    )


def summarize_mmm_planning_answer_envelope(
    envelope: MMMPlanningAnswerEnvelope,
) -> dict[str, object]:
    """Return a metadata-only summary of a planning-answer envelope."""
    return {
        "status": _enum_value(envelope.status),
        "question_class": _enum_value(envelope.question_class),
        "answer_mode": _enum_value(envelope.answer_mode),
        "answer_allowed": envelope.answer_allowed,
        "human_review_required": envelope.human_review_required,
        "caveats": list(envelope.caveats),
        "blocked_reasons": list(envelope.blocked_reasons),
        "deferred_reasons": list(envelope.deferred_reasons),
        "can_say_count": len(envelope.can_say),
        "cannot_say_count": len(envelope.cannot_say),
        "evidence_reference_count": len(envelope.evidence_references),
        "external_run_id": envelope.external_run_id,
        "model_artifact_id": envelope.model_artifact_id,
    }


def _map_status(
    eligibility: MMMPlanningAnswerEligibilityResult,
) -> MMMPlanningAnswerEnvelopeStatus:
    if not eligibility.answer_allowed:
        if _enum_value(eligibility.status) == "unknown" and not (
            eligibility.blocked_reasons or eligibility.deferred_reasons
        ):
            return MMMPlanningAnswerEnvelopeStatus.UNKNOWN
        if (
            eligibility.answer_mode == MMMPlanningAnswerMode.DEFERRED
            or eligibility.deferred_reasons
            or _enum_value(eligibility.status) == "deferred"
        ):
            return MMMPlanningAnswerEnvelopeStatus.DEFERRED
        if (
            eligibility.answer_mode == MMMPlanningAnswerMode.BLOCKED
            or eligibility.blocked_reasons
            or _enum_value(eligibility.status) in {"blocked", "recommendation_requires_gates"}
        ):
            return MMMPlanningAnswerEnvelopeStatus.BLOCKED
        return MMMPlanningAnswerEnvelopeStatus.UNKNOWN

    if eligibility.human_review_required:
        return MMMPlanningAnswerEnvelopeStatus.HUMAN_REVIEW_REQUIRED
    if eligibility.caveats:
        return MMMPlanningAnswerEnvelopeStatus.READY_TO_EXPLAIN_WITH_CAVEATS
    return MMMPlanningAnswerEnvelopeStatus.READY_TO_EXPLAIN


def _build_evidence_references(
    request: MMMPlanningAnswerEnvelopeRequest,
    eligibility: MMMPlanningAnswerEligibilityResult,
) -> list[MMMPlanningAnswerEvidenceReference]:
    refs = list(request.evidence_references)
    refs.append(
        MMMPlanningAnswerEvidenceReference(
            evidence_id=f"eligibility:{eligibility.request_id}",
            evidence_type=MMMPlanningAnswerEvidenceType.PLANNING_ANSWER_ELIGIBILITY,
            source_id=eligibility.request_id,
            status=_enum_value(eligibility.status),
            metadata={"metadata_only": True},
        )
    )
    for gate in eligibility.gate_references:
        refs.append(_gate_evidence_ref(gate))
    if eligibility.external_run_id:
        refs.append(
            MMMPlanningAnswerEvidenceReference(
                evidence_id=f"runtime:{eligibility.external_run_id}",
                evidence_type=MMMPlanningAnswerEvidenceType.RUNTIME_RESULT,
                source_id=eligibility.external_run_id,
                status="referenced",
                metadata={"metadata_only": True},
            )
        )
    if eligibility.model_artifact_id:
        refs.append(
            MMMPlanningAnswerEvidenceReference(
                evidence_id=f"model:{eligibility.model_artifact_id}",
                evidence_type=MMMPlanningAnswerEvidenceType.MODEL_ARTIFACT,
                artifact_id=eligibility.model_artifact_id,
                status="referenced",
                metadata={"metadata_only": True},
            )
        )
    return _dedupe_evidence(refs)


def _gate_evidence_ref(
    gate: MMMPlanningAnswerGateReference,
) -> MMMPlanningAnswerEvidenceReference:
    name = gate.gate_name.lower()
    if "decision" in name or "surface" in name:
        evidence_type = MMMPlanningAnswerEvidenceType.DECISION_SURFACE_GATE
    elif "trust" in name:
        evidence_type = MMMPlanningAnswerEvidenceType.TRUST_REPORT_GATE
    elif "recommend" in name:
        evidence_type = MMMPlanningAnswerEvidenceType.RECOMMENDATION_GATE
    else:
        evidence_type = MMMPlanningAnswerEvidenceType.OTHER
    return MMMPlanningAnswerEvidenceReference(
        evidence_id=f"gate:{gate.gate_name}",
        evidence_type=evidence_type,
        gate_name=gate.gate_name,
        status=gate.gate_status,
        metadata={"metadata_only": True, "passed": gate.passed},
    )


def _build_boundaries(
    *,
    eligibility: MMMPlanningAnswerEligibilityResult,
    evidence_ids: list[str],
) -> tuple[
    list[MMMPlanningAnswerClaimStatement],
    list[MMMPlanningAnswerClaimStatement],
    list[MMMPlanningAnswerEnvelopeIssueCode],
]:
    can_say: list[MMMPlanningAnswerClaimStatement] = []
    cannot_say = _universal_cannot_say(evidence_ids=evidence_ids)
    issues: list[MMMPlanningAnswerEnvelopeIssueCode] = [
        MMMPlanningAnswerEnvelopeIssueCode.CANNOT_SAY_BOUNDARY_ADDED,
        MMMPlanningAnswerEnvelopeIssueCode.UNSUPPORTED_NUMERIC_CLAIMS_BLOCKED,
        MMMPlanningAnswerEnvelopeIssueCode.OPTIMIZER_SIMULATOR_CLAIMS_BLOCKED,
        MMMPlanningAnswerEnvelopeIssueCode.RECOMMENDATION_CLAIMS_BLOCKED_WITHOUT_GATE,
    ]

    mode = eligibility.answer_mode
    if mode == MMMPlanningAnswerMode.DESCRIPTIVE and eligibility.answer_allowed:
        can_say.append(
            _claim(
                claim_id="can-say-descriptive",
                boundary=MMMPlanningAnswerClaimBoundary.CAN_SAY,
                statement=("Can explain descriptive performance status from eligibility metadata."),
                reason="descriptive answer mode is eligible",
                evidence_ids=evidence_ids,
            )
        )
        if eligibility.caveats:
            can_say.append(
                _claim(
                    claim_id="can-say-descriptive-caveats",
                    boundary=MMMPlanningAnswerClaimBoundary.CAN_SAY_WITH_CAVEAT,
                    statement="Can surface descriptive caveats from eligibility metadata.",
                    reason="caveats are present on eligibility result",
                    evidence_ids=evidence_ids,
                )
            )

    elif mode == MMMPlanningAnswerMode.DIAGNOSTIC and eligibility.answer_allowed:
        can_say.append(
            _claim(
                claim_id="can-say-diagnostic",
                boundary=MMMPlanningAnswerClaimBoundary.CAN_SAY_WITH_CAVEAT,
                statement=(
                    "Can explain diagnostic eligibility and caveats; cannot assert causal "
                    "effects unless an approved artifact is supplied."
                ),
                reason="diagnostic answer mode is eligible",
                evidence_ids=evidence_ids,
            )
        )
        cannot_say.append(
            _claim(
                claim_id="cannot-say-causal-without-artifact",
                boundary=MMMPlanningAnswerClaimBoundary.REQUIRES_APPROVED_ARTIFACT,
                statement=(
                    "Cannot assert causal driver claims without an approved diagnostic artifact."
                ),
                reason="diagnostic mode does not authorize causal claims by itself",
                evidence_ids=evidence_ids,
            )
        )

    elif mode == MMMPlanningAnswerMode.SCENARIO_COMPARISON:
        if eligibility.decision_surface_required:
            issues.append(MMMPlanningAnswerEnvelopeIssueCode.DECISION_SURFACE_REQUIRED_FOR_SCENARIO)
        can_say.append(
            _claim(
                claim_id="can-say-scenario-eligibility",
                boundary=MMMPlanningAnswerClaimBoundary.CAN_SAY,
                statement=(
                    "Can describe scenario-comparison eligibility and required DecisionSurface "
                    "route or gate."
                ),
                reason="scenario comparison mode packaging",
                required_gate="decision_surface",
                evidence_ids=evidence_ids,
            )
        )
        cannot_say.append(
            _claim(
                claim_id="cannot-say-scenario-output",
                boundary=MMMPlanningAnswerClaimBoundary.CANNOT_SAY,
                statement="Cannot compute or return scenario comparison outputs in this envelope.",
                reason="no DecisionSurface execution in planning-answer envelope",
                required_gate="decision_surface",
                evidence_ids=evidence_ids,
            )
        )

    elif mode == MMMPlanningAnswerMode.SIMULATION_ONLY:
        if eligibility.decision_surface_required:
            issues.append(MMMPlanningAnswerEnvelopeIssueCode.DECISION_SURFACE_REQUIRED_FOR_SCENARIO)
        can_say.append(
            _claim(
                claim_id="can-say-simulation-eligibility",
                boundary=MMMPlanningAnswerClaimBoundary.CAN_SAY,
                statement="Can describe simulation-only eligibility and required gates.",
                reason="simulation-only mode packaging",
                required_gate="decision_surface",
                evidence_ids=evidence_ids,
            )
        )
        cannot_say.append(
            _claim(
                claim_id="cannot-say-run-simulation",
                boundary=MMMPlanningAnswerClaimBoundary.CANNOT_SAY,
                statement=(
                    "Cannot run simulation or return simulated outcomes "  # must not
                    "in this envelope."
                ),
                reason="no simulator execution in planning-answer envelope",  # must not
                required_gate="decision_surface",
                evidence_ids=evidence_ids,
            )
        )

    elif mode == MMMPlanningAnswerMode.RECOMMENDATION_ELIGIBLE:
        if eligibility.recommendation_contract_required:
            issues.append(
                MMMPlanningAnswerEnvelopeIssueCode.RECOMMENDATION_CONTRACT_REQUIRED_FOR_RECOMMENDATION
            )
        can_say.append(
            _claim(
                claim_id="can-say-recommendation-eligibility",
                boundary=MMMPlanningAnswerClaimBoundary.CAN_SAY,
                statement=("Can describe recommendation eligibility status from gate references."),
                reason="recommendation-eligible mode packaging",
                required_gate="recommendation",
                evidence_ids=evidence_ids,
            )
        )
        cannot_say.append(
            _claim(
                claim_id="cannot-say-generate-recommendation",
                boundary=MMMPlanningAnswerClaimBoundary.CANNOT_SAY,
                statement=(
                    "Cannot generate RecommendationContract or budget recommendations here."
                ),
                reason="recommendation generation is out of envelope scope",
                required_gate="recommendation",
                evidence_ids=evidence_ids,
            )
        )

    elif mode in {MMMPlanningAnswerMode.BLOCKED, MMMPlanningAnswerMode.DEFERRED}:
        can_say.append(
            _claim(
                claim_id="can-say-blockers",
                boundary=MMMPlanningAnswerClaimBoundary.CAN_SAY,
                statement=(
                    "Can explain why the planning answer is blocked or deferred and which "
                    "gates are required next."
                ),
                reason="blocked/deferred answers are first-class envelope outputs",
                evidence_ids=evidence_ids,
            )
        )

    if eligibility.trust_review_required:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.TRUST_REVIEW_REQUIRED_FOR_PLANNING)
        cannot_say.append(
            _claim(
                claim_id="cannot-say-trust-tier-without-gate",
                boundary=MMMPlanningAnswerClaimBoundary.REQUIRES_HUMAN_REVIEW,
                statement=("Cannot assert TrustReport confidence tiers without trust review gate."),
                reason="trust_review_required is true on eligibility",
                required_gate="trust_report",
                evidence_ids=evidence_ids,
            )
        )

    if eligibility.human_review_required:
        can_say.append(
            _claim(
                claim_id="can-say-human-review-required",
                boundary=MMMPlanningAnswerClaimBoundary.REQUIRES_HUMAN_REVIEW,
                statement="Can state that human review is required before downstream use.",
                reason="human_review_required preserved from eligibility",
                evidence_ids=evidence_ids,
            )
        )

    if can_say:
        issues.append(MMMPlanningAnswerEnvelopeIssueCode.CAN_SAY_BOUNDARY_ADDED)

    return can_say, cannot_say, issues


def _universal_cannot_say(
    *,
    evidence_ids: list[str],
) -> list[MMMPlanningAnswerClaimStatement]:
    return [
        _claim(
            claim_id="cannot-say-numeric-claims",
            boundary=MMMPlanningAnswerClaimBoundary.CANNOT_SAY,
            statement=(
                "Cannot report ROI, ROAS, lift, or incrementality unless supplied by an "
                "approved artifact."
            ),
            reason="unsupported numeric claims are blocked in planning-answer envelopes",
            evidence_ids=evidence_ids,
        ),
        _claim(
            claim_id="cannot-say-budget-recommendation",
            boundary=MMMPlanningAnswerClaimBoundary.CANNOT_SAY,
            statement=("Cannot recommend budget allocation without RecommendationContract gate."),
            reason="recommendation claims require RecommendationContract gate",
            required_gate="recommendation",
            evidence_ids=evidence_ids,
        ),
        _claim(
            claim_id="cannot-say-optimizer-simulator",  # must not
            boundary=MMMPlanningAnswerClaimBoundary.CANNOT_SAY,
            statement=(
                "Cannot emit optimizer or simulator outputs unless external approved "  # must not
                "artifacts or gates exist."
            ),
            reason="optimizer/simulator claims are blocked in this envelope",  # must not
            evidence_ids=evidence_ids,
        ),
        _claim(
            claim_id="cannot-say-decision-surface-execution",
            boundary=MMMPlanningAnswerClaimBoundary.CANNOT_SAY,
            statement=("Cannot execute DecisionSurface or invent DecisionSurface payloads here."),
            reason="no DecisionSurface construction or execution",
            required_gate="decision_surface",
            evidence_ids=evidence_ids,
        ),
        _claim(
            claim_id="cannot-say-trust-report-construction",
            boundary=MMMPlanningAnswerClaimBoundary.CANNOT_SAY,
            statement="Cannot construct or bypass TrustReport in this envelope.",
            reason="no TrustReport construction or bypass",
            required_gate="trust_report",
            evidence_ids=evidence_ids,
        ),
    ]


def _claim(
    *,
    claim_id: str,
    boundary: MMMPlanningAnswerClaimBoundary,
    statement: str,
    reason: str,
    required_gate: str | None = None,
    evidence_ids: list[str] | None = None,
) -> MMMPlanningAnswerClaimStatement:
    return MMMPlanningAnswerClaimStatement(
        claim_id=claim_id,
        boundary=boundary,
        statement=statement,
        reason=reason,
        required_gate=required_gate,
        evidence_ids=list(evidence_ids or []),
        metadata={"metadata_only_boundary": True},
    )


def _dedupe_evidence(
    refs: list[MMMPlanningAnswerEvidenceReference],
) -> list[MMMPlanningAnswerEvidenceReference]:
    seen: set[str] = set()
    ordered: list[MMMPlanningAnswerEvidenceReference] = []
    for ref in refs:
        if ref.evidence_id in seen:
            continue
        seen.add(ref.evidence_id)
        ordered.append(ref)
    return ordered


def _enum_value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)
