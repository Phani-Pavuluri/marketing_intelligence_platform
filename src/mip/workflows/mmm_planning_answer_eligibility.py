"""MMM planning-answer eligibility gate (metadata only)."""

from __future__ import annotations

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

_BOUNDARY_ISSUES = (
    MMMPlanningAnswerEligibilityIssueCode.LINEAGE_PRESERVED,
    MMMPlanningAnswerEligibilityIssueCode.NO_DECISION_SURFACE_CONSTRUCTION,
    MMMPlanningAnswerEligibilityIssueCode.NO_DECISION_SURFACE_EXECUTION,
    MMMPlanningAnswerEligibilityIssueCode.NO_TRUST_REPORT_CONSTRUCTION,
    MMMPlanningAnswerEligibilityIssueCode.NO_RECOMMENDATION_CONTRACT_GENERATION,
    MMMPlanningAnswerEligibilityIssueCode.NO_OPTIMIZER_EXECUTION,
    MMMPlanningAnswerEligibilityIssueCode.NO_SIMULATOR_EXECUTION,
    MMMPlanningAnswerEligibilityIssueCode.NO_BUDGET_ALLOCATION_CALCULATION,
    MMMPlanningAnswerEligibilityIssueCode.NO_ROI_ROAS_LIFT_INCREMENTALITY_CALCULATION,
    MMMPlanningAnswerEligibilityIssueCode.NO_ARTIFACT_LOADING,
    MMMPlanningAnswerEligibilityIssueCode.NO_MODEL_LOADING,
    MMMPlanningAnswerEligibilityIssueCode.NO_MODEL_EXECUTION,
    MMMPlanningAnswerEligibilityIssueCode.NO_MMM_FITTING,
    MMMPlanningAnswerEligibilityIssueCode.NO_CLAIM_AUTHORIZATION,
    MMMPlanningAnswerEligibilityIssueCode.NO_LLM_PROVIDER_BEHAVIOR_CHANGE,
)

_ARTIFACT_BLOCKED_STATUSES = frozenset(
    {
        MMMArtifactGovernanceUseReadinessStatus.BLOCKED,
        MMMArtifactGovernanceUseReadinessStatus.RUNTIME_FAILED,
        MMMArtifactGovernanceUseReadinessStatus.MISSING_RUNTIME_INGESTION_RESULT,
        MMMArtifactGovernanceUseReadinessStatus.MISSING_REQUIRED_ARTIFACT_METADATA,
    }
)

_ARTIFACT_BLOCKED_USE = frozenset(
    {
        MMMArtifactUseReadiness.BLOCKED,
    }
)

_ARTIFACT_DEFERRED_STATUSES = frozenset(
    {
        MMMArtifactGovernanceUseReadinessStatus.DEFERRED,
    }
)

_ARTIFACT_DEFERRED_USE = frozenset(
    {
        MMMArtifactUseReadiness.DEFERRED,
    }
)


def evaluate_mmm_planning_answer_eligibility(
    request: MMMPlanningAnswerEligibilityRequest,
) -> MMMPlanningAnswerEligibilityResult:
    """Evaluate whether an MMM-backed planning question may be answered (metadata only)."""
    lineage = {
        **request.lineage,
        "planning_answer_eligibility_stage": "mmm_planning_answer_eligibility",
    }
    issues: list[MMMPlanningAnswerEligibilityIssueCode] = list(_BOUNDARY_ISSUES)
    caveats: list[str] = []
    blocked_reasons: list[str] = []
    deferred_reasons: list[str] = []
    gate_references = _collect_gate_references(request)

    if request.artifact_use_readiness is None:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.ARTIFACT_USE_READINESS_MISSING)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["artifact use-readiness result is missing"],
            deferred_reasons=[],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            human_review_required=True,
        )

    readiness = request.artifact_use_readiness
    issues.append(MMMPlanningAnswerEligibilityIssueCode.ARTIFACT_USE_READINESS_PRESENT)
    planning_ready = readiness.planning_ready
    diagnostic_only = readiness.diagnostic_only
    ready_for_ds = readiness.ready_for_decision_surface_review
    ready_for_trust = readiness.ready_for_trust_report_review

    if planning_ready:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.ARTIFACT_PLANNING_READY)
    elif diagnostic_only:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.ARTIFACT_DIAGNOSTIC_ONLY)
    else:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.ARTIFACT_NOT_PLANNING_READY)

    if ready_for_trust:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.TRUST_REVIEW_ROUTE_AVAILABLE)
    else:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.TRUST_REVIEW_ROUTE_MISSING)

    if ready_for_ds:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.DECISION_SURFACE_REVIEW_ROUTE_AVAILABLE)
    else:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.DECISION_SURFACE_REVIEW_ROUTE_MISSING)

    if _artifact_blocked(readiness):
        issues.append(MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_ARTIFACT_READINESS)
        blocked_reasons.extend(readiness.blocked_reasons or ["artifact use-readiness is blocked"])
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=blocked_reasons,
            deferred_reasons=[],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            human_review_required=True,
        )

    if _artifact_deferred(readiness):
        issues.append(MMMPlanningAnswerEligibilityIssueCode.DEFERRED_PENDING_GOVERNANCE_REVIEW)
        deferred_reasons.append("artifact use-readiness is deferred")
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.DEFERRED,
            status=MMMPlanningAnswerEligibilityStatus.DEFERRED,
            answer_allowed=False,
            blocked_reasons=[],
            deferred_reasons=deferred_reasons,
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            human_review_required=True,
        )

    question = request.question_class
    if question == MMMPlanningQuestionClass.UNKNOWN:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.QUESTION_CLASS_UNKNOWN)
        deferred_reasons.append("planning question class is unknown")
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.DEFERRED,
            status=MMMPlanningAnswerEligibilityStatus.UNKNOWN,
            answer_allowed=False,
            blocked_reasons=[],
            deferred_reasons=deferred_reasons,
            caveats=["question class must be classified before answering"],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            human_review_required=True,
        )

    issues.append(MMMPlanningAnswerEligibilityIssueCode.QUESTION_CLASS_PRESENT)

    if question == MMMPlanningQuestionClass.DESCRIPTIVE_PERFORMANCE:
        return _evaluate_descriptive(
            request=request,
            readiness=readiness,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            caveats=caveats,
        )

    if question == MMMPlanningQuestionClass.DIAGNOSTIC_DRIVER:
        return _evaluate_diagnostic(
            request=request,
            readiness=readiness,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            caveats=caveats,
        )

    if question == MMMPlanningQuestionClass.SCENARIO_COMPARISON:
        return _evaluate_scenario(
            request=request,
            readiness=readiness,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            caveats=caveats,
        )

    if question == MMMPlanningQuestionClass.SIMULATION_REQUEST:
        return _evaluate_simulation(
            request=request,
            readiness=readiness,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            caveats=caveats,
        )

    if question == MMMPlanningQuestionClass.OPTIMIZATION_REQUEST:
        return _evaluate_optimization(
            request=request,
            readiness=readiness,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
        )

    if question == MMMPlanningQuestionClass.RECOMMENDATION_REQUEST:
        return _evaluate_recommendation(
            request=request,
            readiness=readiness,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            caveats=caveats,
        )

    issues.append(MMMPlanningAnswerEligibilityIssueCode.QUESTION_CLASS_UNKNOWN)
    return _result(
        request=request,
        answer_mode=MMMPlanningAnswerMode.BLOCKED,
        status=MMMPlanningAnswerEligibilityStatus.UNKNOWN,
        answer_allowed=False,
        blocked_reasons=["unsupported planning question class"],
        deferred_reasons=[],
        caveats=[],
        issues=issues,
        gate_references=gate_references,
        lineage=lineage,
        readiness=readiness,
        human_review_required=True,
    )


def summarize_mmm_planning_answer_eligibility(
    result: MMMPlanningAnswerEligibilityResult,
) -> dict[str, object]:
    """Return a metadata-only summary of planning-answer eligibility."""
    return {
        "question_class": _enum_value(result.question_class),
        "answer_mode": _enum_value(result.answer_mode),
        "status": _enum_value(result.status),
        "answer_allowed": result.answer_allowed,
        "decision_surface_required": result.decision_surface_required,
        "trust_review_required": result.trust_review_required,
        "recommendation_contract_required": result.recommendation_contract_required,
        "human_review_required": result.human_review_required,
        "blocked_reasons": list(result.blocked_reasons),
        "deferred_reasons": list(result.deferred_reasons),
        "caveats": list(result.caveats),
        "external_run_id": result.external_run_id,
        "model_artifact_id": result.model_artifact_id,
    }


def _enum_value(value: object) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _evaluate_descriptive(
    *,
    request: MMMPlanningAnswerEligibilityRequest,
    readiness: MMMArtifactGovernanceUseReadinessResult,
    issues: list[MMMPlanningAnswerEligibilityIssueCode],
    gate_references: list[MMMPlanningAnswerGateReference],
    lineage: dict[str, str],
    caveats: list[str],
) -> MMMPlanningAnswerEligibilityResult:
    if not readiness.planning_ready and not readiness.diagnostic_only:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_ARTIFACT_READINESS)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["artifact is not planning-ready or diagnostic-only"],
            deferred_reasons=[],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            human_review_required=True,
        )

    if (
        request.require_trust_review_for_planning
        and readiness.planning_ready
        and not readiness.ready_for_trust_report_review
        and not _gate_passed(request.trust_report_gate)
    ):
        issues.append(MMMPlanningAnswerEligibilityIssueCode.DEFERRED_PENDING_GOVERNANCE_REVIEW)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.DEFERRED,
            status=MMMPlanningAnswerEligibilityStatus.DEFERRED,
            answer_allowed=False,
            blocked_reasons=[],
            deferred_reasons=[
                "trust review route or gate required for planning descriptive answer"
            ],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            trust_review_required=True,
            human_review_required=True,
        )

    issues.append(MMMPlanningAnswerEligibilityIssueCode.DESCRIPTIVE_ANSWER_ALLOWED)
    if readiness.diagnostic_only and not readiness.planning_ready:
        caveats.append("descriptive answer limited to diagnostic-only artifact metadata")
        issues.append(MMMPlanningAnswerEligibilityIssueCode.CAVEATS_REQUIRED)
        issues.append(MMMPlanningAnswerEligibilityIssueCode.HUMAN_REVIEW_REQUIRED)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.DESCRIPTIVE,
            status=MMMPlanningAnswerEligibilityStatus.ANSWER_ELIGIBLE_WITH_CAVEATS,
            answer_allowed=True,
            blocked_reasons=[],
            deferred_reasons=[],
            caveats=caveats,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            human_review_required=True,
        )

    status = MMMPlanningAnswerEligibilityStatus.ANSWER_ELIGIBLE
    if readiness.warnings:
        caveats.append("artifact use-readiness reported warnings")
        issues.append(MMMPlanningAnswerEligibilityIssueCode.CAVEATS_REQUIRED)
        status = MMMPlanningAnswerEligibilityStatus.ANSWER_ELIGIBLE_WITH_CAVEATS

    return _result(
        request=request,
        answer_mode=MMMPlanningAnswerMode.DESCRIPTIVE,
        status=status,
        answer_allowed=True,
        blocked_reasons=[],
        deferred_reasons=[],
        caveats=caveats,
        issues=issues,
        gate_references=gate_references,
        lineage=lineage,
        readiness=readiness,
        trust_review_required=request.require_trust_review_for_planning,
        human_review_required=readiness.human_review_required,
    )


def _evaluate_diagnostic(
    *,
    request: MMMPlanningAnswerEligibilityRequest,
    readiness: MMMArtifactGovernanceUseReadinessResult,
    issues: list[MMMPlanningAnswerEligibilityIssueCode],
    gate_references: list[MMMPlanningAnswerGateReference],
    lineage: dict[str, str],
    caveats: list[str],
) -> MMMPlanningAnswerEligibilityResult:
    diagnostic_ok = (
        readiness.diagnostic_only
        or readiness.ready_for_diagnostic_review
        or readiness.planning_ready
    )
    if not diagnostic_ok:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_ARTIFACT_READINESS)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["artifact does not support diagnostic review"],
            deferred_reasons=[],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            human_review_required=True,
        )

    if (
        not request.allow_diagnostic_without_decision_surface
        and not readiness.ready_for_decision_surface_review
        and not _gate_passed(request.decision_surface_gate)
    ):
        issues.append(
            MMMPlanningAnswerEligibilityIssueCode.DEFERRED_PENDING_DECISION_SURFACE_REVIEW
        )
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.DEFERRED,
            status=MMMPlanningAnswerEligibilityStatus.DEFERRED,
            answer_allowed=False,
            blocked_reasons=[],
            deferred_reasons=["DecisionSurface review required for diagnostic answer"],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            human_review_required=True,
        )

    issues.append(MMMPlanningAnswerEligibilityIssueCode.DIAGNOSTIC_ANSWER_ALLOWED)
    if readiness.diagnostic_only or not readiness.planning_ready:
        caveats.append("diagnostic-only answer; not planning-ready")
        issues.append(MMMPlanningAnswerEligibilityIssueCode.CAVEATS_REQUIRED)
        issues.append(MMMPlanningAnswerEligibilityIssueCode.HUMAN_REVIEW_REQUIRED)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.DIAGNOSTIC,
            status=MMMPlanningAnswerEligibilityStatus.DIAGNOSTIC_ONLY,
            answer_allowed=True,
            blocked_reasons=[],
            deferred_reasons=[],
            caveats=caveats,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            human_review_required=True,
        )

    return _result(
        request=request,
        answer_mode=MMMPlanningAnswerMode.DIAGNOSTIC,
        status=MMMPlanningAnswerEligibilityStatus.ANSWER_ELIGIBLE,
        answer_allowed=True,
        blocked_reasons=[],
        deferred_reasons=[],
        caveats=caveats,
        issues=issues,
        gate_references=gate_references,
        lineage=lineage,
        readiness=readiness,
        human_review_required=readiness.human_review_required,
    )


def _evaluate_scenario(
    *,
    request: MMMPlanningAnswerEligibilityRequest,
    readiness: MMMArtifactGovernanceUseReadinessResult,
    issues: list[MMMPlanningAnswerEligibilityIssueCode],
    gate_references: list[MMMPlanningAnswerGateReference],
    lineage: dict[str, str],
    caveats: list[str],
) -> MMMPlanningAnswerEligibilityResult:
    if not readiness.planning_ready:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_ARTIFACT_READINESS)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["scenario comparison requires planning-ready artifact"],
            deferred_reasons=[],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            human_review_required=True,
        )

    ds_passed = _gate_passed(request.decision_surface_gate)
    ds_failed = _gate_failed(request.decision_surface_gate)
    if ds_failed:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_DECISION_SURFACE_GATE)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["DecisionSurface gate failed"],
            deferred_reasons=[],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            human_review_required=True,
        )

    if request.require_decision_surface_for_scenario and not ds_passed:
        if readiness.ready_for_decision_surface_review:
            issues.append(
                MMMPlanningAnswerEligibilityIssueCode.DEFERRED_PENDING_DECISION_SURFACE_REVIEW
            )
            caveats.append("DecisionSurface review route available; surface not yet gated")
            issues.append(MMMPlanningAnswerEligibilityIssueCode.CAVEATS_REQUIRED)
            issues.append(MMMPlanningAnswerEligibilityIssueCode.HUMAN_REVIEW_REQUIRED)
            return _result(
                request=request,
                answer_mode=MMMPlanningAnswerMode.SCENARIO_COMPARISON,
                status=MMMPlanningAnswerEligibilityStatus.DEFERRED,
                answer_allowed=False,
                blocked_reasons=[],
                deferred_reasons=["pending DecisionSurface review before scenario comparison"],
                caveats=caveats,
                issues=issues,
                gate_references=gate_references,
                lineage=lineage,
                readiness=readiness,
                decision_surface_required=True,
                trust_review_required=request.require_trust_review_for_planning,
                human_review_required=True,
            )
        issues.append(MMMPlanningAnswerEligibilityIssueCode.DECISION_SURFACE_REVIEW_ROUTE_MISSING)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["DecisionSurface route or gate required for scenario comparison"],
            deferred_reasons=[],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            human_review_required=True,
        )

    if request.require_trust_review_for_planning and not (
        readiness.ready_for_trust_report_review or _gate_passed(request.trust_report_gate)
    ):
        issues.append(MMMPlanningAnswerEligibilityIssueCode.DEFERRED_PENDING_GOVERNANCE_REVIEW)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.DEFERRED,
            status=MMMPlanningAnswerEligibilityStatus.DEFERRED,
            answer_allowed=False,
            blocked_reasons=[],
            deferred_reasons=["trust review route or gate required for scenario comparison"],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            trust_review_required=True,
            human_review_required=True,
        )

    issues.append(MMMPlanningAnswerEligibilityIssueCode.SCENARIO_COMPARISON_ALLOWED)
    issues.append(MMMPlanningAnswerEligibilityIssueCode.HUMAN_REVIEW_REQUIRED)
    return _result(
        request=request,
        answer_mode=MMMPlanningAnswerMode.SCENARIO_COMPARISON,
        status=MMMPlanningAnswerEligibilityStatus.SCENARIO_ONLY,
        answer_allowed=True,
        blocked_reasons=[],
        deferred_reasons=[],
        caveats=caveats,
        issues=issues,
        gate_references=gate_references,
        lineage=lineage,
        readiness=readiness,
        decision_surface_required=True,
        trust_review_required=request.require_trust_review_for_planning,
        human_review_required=True,
    )


def _evaluate_simulation(
    *,
    request: MMMPlanningAnswerEligibilityRequest,
    readiness: MMMArtifactGovernanceUseReadinessResult,
    issues: list[MMMPlanningAnswerEligibilityIssueCode],
    gate_references: list[MMMPlanningAnswerGateReference],
    lineage: dict[str, str],
    caveats: list[str],
) -> MMMPlanningAnswerEligibilityResult:
    if not readiness.planning_ready:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_ARTIFACT_READINESS)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["simulation request requires planning-ready artifact"],
            deferred_reasons=[],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            human_review_required=True,
        )

    ds_passed = _gate_passed(request.decision_surface_gate)
    simulation_supported = ds_passed or readiness.ready_for_decision_surface_review
    if not simulation_supported:
        issues.append(
            MMMPlanningAnswerEligibilityIssueCode.DEFERRED_PENDING_DECISION_SURFACE_REVIEW
        )
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.DEFERRED,
            status=MMMPlanningAnswerEligibilityStatus.DEFERRED,
            answer_allowed=False,
            blocked_reasons=[],
            deferred_reasons=[
                "DecisionSurface/simulation support missing; simulation not implemented in MIP"
            ],
            caveats=["no simulator execution in MIP"],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            human_review_required=True,
        )

    if not ds_passed and readiness.ready_for_decision_surface_review:
        issues.append(
            MMMPlanningAnswerEligibilityIssueCode.DEFERRED_PENDING_DECISION_SURFACE_REVIEW
        )
        caveats.append("simulation deferred pending DecisionSurface review; no simulator in MIP")
        issues.append(MMMPlanningAnswerEligibilityIssueCode.CAVEATS_REQUIRED)
        issues.append(MMMPlanningAnswerEligibilityIssueCode.HUMAN_REVIEW_REQUIRED)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.SIMULATION_ONLY,
            status=MMMPlanningAnswerEligibilityStatus.DEFERRED,
            answer_allowed=False,
            blocked_reasons=[],
            deferred_reasons=["pending DecisionSurface review before simulation-only answer"],
            caveats=caveats,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            human_review_required=True,
        )

    issues.append(MMMPlanningAnswerEligibilityIssueCode.SIMULATION_ONLY_ALLOWED)
    issues.append(MMMPlanningAnswerEligibilityIssueCode.HUMAN_REVIEW_REQUIRED)
    caveats.append("simulation-only eligibility; no recommendation generated")
    issues.append(MMMPlanningAnswerEligibilityIssueCode.CAVEATS_REQUIRED)
    return _result(
        request=request,
        answer_mode=MMMPlanningAnswerMode.SIMULATION_ONLY,
        status=MMMPlanningAnswerEligibilityStatus.SIMULATION_ONLY,
        answer_allowed=True,
        blocked_reasons=[],
        deferred_reasons=[],
        caveats=caveats,
        issues=issues,
        gate_references=gate_references,
        lineage=lineage,
        readiness=readiness,
        decision_surface_required=True,
        recommendation_contract_required=False,
        human_review_required=True,
    )


def _evaluate_optimization(
    *,
    request: MMMPlanningAnswerEligibilityRequest,
    readiness: MMMArtifactGovernanceUseReadinessResult,
    issues: list[MMMPlanningAnswerEligibilityIssueCode],
    gate_references: list[MMMPlanningAnswerGateReference],
    lineage: dict[str, str],
) -> MMMPlanningAnswerEligibilityResult:
    issues.append(
        MMMPlanningAnswerEligibilityIssueCode.OPTIMIZATION_REQUIRES_EXTERNAL_RUNTIME_OR_DECISION_SURFACE
    )
    issues.append(MMMPlanningAnswerEligibilityIssueCode.HUMAN_REVIEW_REQUIRED)
    deferred_reasons = [
        (
            "optimization requires external runtime or DecisionSurface; "
            "optimizer not executed in MIP"  # must not
        )
    ]
    if not readiness.planning_ready:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_ARTIFACT_READINESS)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["optimization request requires planning-ready artifact"],
            deferred_reasons=[],
            caveats=["no optimizer execution in MIP"],  # must not
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            recommendation_contract_required=True,
            human_review_required=True,
        )

    return _result(
        request=request,
        answer_mode=MMMPlanningAnswerMode.DEFERRED,
        status=MMMPlanningAnswerEligibilityStatus.RECOMMENDATION_REQUIRES_GATES,
        answer_allowed=False,
        blocked_reasons=[],
        deferred_reasons=deferred_reasons,
        caveats=["no optimizer execution in MIP"],  # must not
        issues=issues,
        gate_references=gate_references,
        lineage=lineage,
        readiness=readiness,
        decision_surface_required=True,
        trust_review_required=True,
        recommendation_contract_required=True,
        human_review_required=True,
    )


def _evaluate_recommendation(
    *,
    request: MMMPlanningAnswerEligibilityRequest,
    readiness: MMMArtifactGovernanceUseReadinessResult,
    issues: list[MMMPlanningAnswerEligibilityIssueCode],
    gate_references: list[MMMPlanningAnswerGateReference],
    lineage: dict[str, str],
    caveats: list[str],
) -> MMMPlanningAnswerEligibilityResult:
    issues.append(
        MMMPlanningAnswerEligibilityIssueCode.RECOMMENDATION_REQUIRES_RECOMMENDATION_CONTRACT
    )
    if not readiness.planning_ready:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_ARTIFACT_READINESS)
        issues.append(MMMPlanningAnswerEligibilityIssueCode.RECOMMENDATION_BLOCKED_PENDING_GATES)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.BLOCKED,
            answer_allowed=False,
            blocked_reasons=["recommendation request requires planning-ready artifact"],
            deferred_reasons=[],
            caveats=[],
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            trust_review_required=True,
            recommendation_contract_required=True,
            human_review_required=True,
        )

    ds_ok = _gate_passed(request.decision_surface_gate)
    trust_ok = _gate_passed(request.trust_report_gate)
    rec_ok = _gate_passed(request.recommendation_gate)

    if request.decision_surface_gate is None or not ds_ok:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_DECISION_SURFACE_GATE)
        issues.append(MMMPlanningAnswerEligibilityIssueCode.RECOMMENDATION_BLOCKED_PENDING_GATES)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.RECOMMENDATION_REQUIRES_GATES,
            answer_allowed=False,
            blocked_reasons=["DecisionSurface gate must pass for recommendation eligibility"],
            deferred_reasons=[],
            caveats=caveats,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            trust_review_required=True,
            recommendation_contract_required=True,
            human_review_required=True,
        )

    if request.trust_report_gate is None or not trust_ok:
        issues.append(MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_TRUST_GATE)
        issues.append(MMMPlanningAnswerEligibilityIssueCode.RECOMMENDATION_BLOCKED_PENDING_GATES)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.RECOMMENDATION_REQUIRES_GATES,
            answer_allowed=False,
            blocked_reasons=["TrustReport gate must pass for recommendation eligibility"],
            deferred_reasons=[],
            caveats=caveats,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            trust_review_required=True,
            recommendation_contract_required=True,
            human_review_required=True,
        )

    if request.require_recommendation_gate_for_recommendation and (
        request.recommendation_gate is None or not rec_ok
    ):
        if request.recommendation_gate is None:
            issues.append(MMMPlanningAnswerEligibilityIssueCode.RECOMMENDATION_GATE_MISSING)
        else:
            issues.append(MMMPlanningAnswerEligibilityIssueCode.BLOCKED_BY_RECOMMENDATION_GATE)
        issues.append(MMMPlanningAnswerEligibilityIssueCode.RECOMMENDATION_BLOCKED_PENDING_GATES)
        issues.append(MMMPlanningAnswerEligibilityIssueCode.DEFERRED_PENDING_RECOMMENDATION_REVIEW)
        return _result(
            request=request,
            answer_mode=MMMPlanningAnswerMode.BLOCKED,
            status=MMMPlanningAnswerEligibilityStatus.RECOMMENDATION_REQUIRES_GATES,
            answer_allowed=False,
            blocked_reasons=["Recommendation gate must pass for recommendation eligibility"],
            deferred_reasons=[],
            caveats=caveats,
            issues=issues,
            gate_references=gate_references,
            lineage=lineage,
            readiness=readiness,
            decision_surface_required=True,
            trust_review_required=True,
            recommendation_contract_required=True,
            human_review_required=True,
        )

    issues.append(MMMPlanningAnswerEligibilityIssueCode.RECOMMENDATION_GATE_PRESENT)
    issues.append(MMMPlanningAnswerEligibilityIssueCode.RECOMMENDATION_ALLOWED_BY_GATES)
    issues.append(MMMPlanningAnswerEligibilityIssueCode.HUMAN_REVIEW_REQUIRED)
    caveats.append("recommendation eligible by gates only; no RecommendationContract generated")
    issues.append(MMMPlanningAnswerEligibilityIssueCode.CAVEATS_REQUIRED)
    return _result(
        request=request,
        answer_mode=MMMPlanningAnswerMode.RECOMMENDATION_ELIGIBLE,
        status=MMMPlanningAnswerEligibilityStatus.ANSWER_ELIGIBLE,
        answer_allowed=True,
        blocked_reasons=[],
        deferred_reasons=[],
        caveats=caveats,
        issues=issues,
        gate_references=gate_references,
        lineage=lineage,
        readiness=readiness,
        decision_surface_required=True,
        trust_review_required=True,
        recommendation_contract_required=True,
        human_review_required=True,
    )


def _collect_gate_references(
    request: MMMPlanningAnswerEligibilityRequest,
) -> list[MMMPlanningAnswerGateReference]:
    refs: list[MMMPlanningAnswerGateReference] = []
    for gate in (
        request.decision_surface_gate,
        request.trust_report_gate,
        request.recommendation_gate,
    ):
        if gate is not None:
            refs.append(gate)
    return refs


def _gate_passed(gate: MMMPlanningAnswerGateReference | None) -> bool:
    return gate is not None and gate.passed


def _gate_failed(gate: MMMPlanningAnswerGateReference | None) -> bool:
    return gate is not None and not gate.passed and bool(gate.blocked_reasons)


def _artifact_blocked(readiness: MMMArtifactGovernanceUseReadinessResult) -> bool:
    return (
        readiness.status in _ARTIFACT_BLOCKED_STATUSES
        or readiness.use_readiness in _ARTIFACT_BLOCKED_USE
    )


def _artifact_deferred(readiness: MMMArtifactGovernanceUseReadinessResult) -> bool:
    return (
        readiness.status in _ARTIFACT_DEFERRED_STATUSES
        or readiness.use_readiness in _ARTIFACT_DEFERRED_USE
    )


def _result(
    *,
    request: MMMPlanningAnswerEligibilityRequest,
    answer_mode: MMMPlanningAnswerMode,
    status: MMMPlanningAnswerEligibilityStatus,
    answer_allowed: bool,
    blocked_reasons: list[str],
    deferred_reasons: list[str],
    caveats: list[str],
    issues: list[MMMPlanningAnswerEligibilityIssueCode],
    gate_references: list[MMMPlanningAnswerGateReference],
    lineage: dict[str, str],
    readiness: MMMArtifactGovernanceUseReadinessResult | None = None,
    decision_surface_required: bool = False,
    trust_review_required: bool = False,
    recommendation_contract_required: bool = False,
    human_review_required: bool = False,
) -> MMMPlanningAnswerEligibilityResult:
    return MMMPlanningAnswerEligibilityResult(
        request_id=request.request_id,
        question_class=request.question_class,
        answer_mode=answer_mode,
        status=status,
        answer_allowed=answer_allowed,
        decision_surface_required=decision_surface_required,
        trust_review_required=trust_review_required,
        recommendation_contract_required=recommendation_contract_required,
        human_review_required=human_review_required,
        artifact_planning_ready=bool(readiness.planning_ready) if readiness else False,
        artifact_diagnostic_only=bool(readiness.diagnostic_only) if readiness else False,
        ready_for_decision_surface_review=(
            bool(readiness.ready_for_decision_surface_review) if readiness else False
        ),
        ready_for_trust_report_review=(
            bool(readiness.ready_for_trust_report_review) if readiness else False
        ),
        blocked_reasons=list(dict.fromkeys(blocked_reasons)),
        deferred_reasons=list(dict.fromkeys(deferred_reasons)),
        caveats=list(dict.fromkeys(caveats)),
        issues=list(dict.fromkeys(issues)),
        gate_references=gate_references,
        external_run_id=readiness.external_run_id if readiness else None,
        model_artifact_id=readiness.model_artifact_id if readiness else None,
        lineage=lineage,
        metadata={
            **request.metadata,
            "metadata_only_eligibility": True,
            "no_recommendation_generated": True,
        },
    )
