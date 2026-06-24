"""Tests for contract-driven release gates."""

from datetime import UTC, datetime

import pytest

from mip.contracts import (
    ArtifactStatus,
    CompatibilityStatus,
    ConfidenceTier,
    DecisionSurfaceType,
    DiagnosticSummary,
    Estimand,
    RecommendationContract,
    RecommendationType,
)
from mip.evaluation import (
    GateDecision,
    GateOutcome,
    GatePurpose,
    check_calibration_signal_gate,
    check_decision_surface_gate,
    check_experiment_evidence_gate,
    check_recommendation_gate,
    check_trust_report_gate,
    min_confidence_tier,
)
from mip.evaluation import reasons as R
from tests.evaluation.conftest import (
    build_calibration_signal,
    build_decision_surface,
    build_experiment_evidence,
    build_recommendation,
    build_trust_report,
)


def test_passing_experiment_evidence_gate(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(delta_mu_estimand, passing_diagnostics)
    outcome = check_experiment_evidence_gate(evidence)
    assert outcome.decision == GateDecision.PASS
    assert outcome.max_confidence_tier == ConfidenceTier.DIRECTIONAL


def test_experiment_evidence_blocks_on_failed_diagnostics(
    delta_mu_estimand: Estimand,
    failed_diagnostics: DiagnosticSummary,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(
        delta_mu_estimand,
        passing_diagnostics,
        design_diagnostics=failed_diagnostics,
    )
    outcome = check_experiment_evidence_gate(evidence)
    assert outcome.decision == GateDecision.BLOCK
    assert R.DIAGNOSTICS_FAILED in outcome.reason_codes
    assert outcome.max_confidence_tier == ConfidenceTier.BLOCKED


def test_experiment_evidence_warns_on_low_freshness(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(
        delta_mu_estimand,
        passing_diagnostics,
        freshness_score=0.2,
    )
    outcome = check_experiment_evidence_gate(evidence)
    assert outcome.decision == GateDecision.WARN
    assert R.LOW_FRESHNESS_SCORE in outcome.reason_codes


def test_experiment_evidence_warns_if_draft(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(
        delta_mu_estimand,
        passing_diagnostics,
        status=ArtifactStatus.DRAFT,
    )
    outcome = check_experiment_evidence_gate(evidence)
    assert outcome.decision == GateDecision.WARN
    assert R.NOT_VALIDATED_OR_CERTIFIED in outcome.reason_codes


def test_experiment_evidence_blocks_if_quality_below_threshold(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(
        delta_mu_estimand,
        passing_diagnostics,
        quality_score=0.4,
    )
    outcome = check_experiment_evidence_gate(evidence)
    assert outcome.decision == GateDecision.BLOCK
    assert R.LOW_QUALITY_SCORE in outcome.reason_codes


def test_calibration_signal_passes_when_compatible(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    signal = build_calibration_signal(passing_diagnostics)
    outcome = check_calibration_signal_gate(signal)
    assert outcome.decision == GateDecision.PASS
    assert outcome.max_confidence_tier == ConfidenceTier.DIRECTIONAL


def test_calibration_signal_blocks_when_incompatible(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    signal = build_calibration_signal(
        passing_diagnostics,
        compatibility_status=CompatibilityStatus.INCOMPATIBLE,
        weight=0.0,
    )
    outcome = check_calibration_signal_gate(signal)
    assert outcome.decision == GateDecision.BLOCK
    assert R.INCOMPATIBLE_CALIBRATION in outcome.reason_codes


def test_calibration_signal_blocks_when_weight_is_zero(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    signal = build_calibration_signal(passing_diagnostics, weight=0.0)
    outcome = check_calibration_signal_gate(signal)
    assert outcome.decision == GateDecision.BLOCK
    assert R.ZERO_CALIBRATION_WEIGHT in outcome.reason_codes


def test_partially_compatible_calibration_caps_at_directional(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    signal = build_calibration_signal(
        passing_diagnostics,
        compatibility_status=CompatibilityStatus.PARTIALLY_COMPATIBLE,
        confidence_tier=ConfidenceTier.DIRECTIONAL,
    )
    outcome = check_calibration_signal_gate(signal)
    assert outcome.decision == GateDecision.WARN
    assert outcome.max_confidence_tier == ConfidenceTier.DIRECTIONAL


def test_unknown_calibration_caps_at_diagnostic_only(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    signal = build_calibration_signal(
        passing_diagnostics,
        compatibility_status=CompatibilityStatus.UNKNOWN,
        confidence_tier=ConfidenceTier.DIRECTIONAL,
    )
    outcome = check_calibration_signal_gate(signal)
    assert outcome.decision == GateDecision.WARN
    assert outcome.max_confidence_tier == ConfidenceTier.DIAGNOSTIC_ONLY


def test_certified_full_panel_surface_passes_budget_planning(
    delta_mu_estimand: Estimand,
) -> None:
    surface = build_decision_surface(delta_mu_estimand)
    outcome = check_decision_surface_gate(surface)
    assert outcome.decision == GateDecision.PASS
    assert outcome.max_confidence_tier == ConfidenceTier.DECISION_READY


def test_diagnostic_curve_blocks_budget_planning(
    delta_mu_estimand: Estimand,
) -> None:
    surface = build_decision_surface(
        delta_mu_estimand,
        surface_type=DecisionSurfaceType.DIAGNOSTIC_CURVE,
        certification_status=ArtifactStatus.DRAFT,
        reliability_scorecard_id=None,
    )
    outcome = check_decision_surface_gate(surface)
    assert outcome.decision == GateDecision.BLOCK
    assert R.NOT_FULL_PANEL_DELTA_MU in outcome.reason_codes


def test_uncertified_decision_surface_warns(
    delta_mu_estimand: Estimand,
) -> None:
    surface = build_decision_surface(
        delta_mu_estimand,
        certification_status=ArtifactStatus.VALIDATED,
    )
    outcome = check_decision_surface_gate(surface)
    assert outcome.decision == GateDecision.WARN
    assert R.NOT_VALIDATED_OR_CERTIFIED in outcome.reason_codes
    assert outcome.max_confidence_tier == ConfidenceTier.DIRECTIONAL


def test_missing_reliability_scorecard_blocks_budget_planning(
    delta_mu_estimand: Estimand,
) -> None:
    surface = build_decision_surface(
        delta_mu_estimand,
        reliability_scorecard_id=None,
        certification_status=ArtifactStatus.VALIDATED,
    )
    outcome = check_decision_surface_gate(surface)
    assert outcome.decision == GateDecision.BLOCK
    assert R.MISSING_RELIABILITY_SCORECARD in outcome.reason_codes


def test_budget_shift_recommendation_blocks_without_decision_surface(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    recommendation = RecommendationContract.model_construct(
        recommendation_id="rec-001",
        recommendation_type=RecommendationType.BUDGET_SHIFT,
        action={"shift_usd": 10000},
        diagnostics_summary=passing_diagnostics,
        confidence_tier=ConfidenceTier.DIRECTIONAL,
        created_at=datetime(2025, 5, 1, tzinfo=UTC),
        decision_surface_ids=[],
    )
    outcome = check_recommendation_gate(recommendation)
    assert outcome.decision == GateDecision.BLOCK
    assert R.MISSING_DECISION_SURFACE in outcome.reason_codes


def test_recommendation_warns_on_unsupported_claims(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    recommendation = build_recommendation(
        passing_diagnostics,
        unsupported_claims=["cannot certify channel synergy"],
    )
    outcome = check_recommendation_gate(recommendation)
    assert outcome.decision == GateDecision.WARN
    assert R.UNSUPPORTED_CLAIMS_PRESENT in outcome.reason_codes


def test_blocked_recommendation_blocks(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    recommendation = build_recommendation(
        passing_diagnostics,
        confidence_tier=ConfidenceTier.BLOCKED,
        risks=["stale model"],
    )
    outcome = check_recommendation_gate(recommendation)
    assert outcome.decision == GateDecision.BLOCK
    assert R.BLOCKED_CONFIDENCE_TIER in outcome.reason_codes


def test_trust_report_blocks_on_failed_diagnostics(
    failed_diagnostics: DiagnosticSummary,
) -> None:
    report = build_trust_report(failed_diagnostics)
    outcome = check_trust_report_gate(report)
    assert outcome.decision == GateDecision.BLOCK
    assert R.TRUST_DIAGNOSTICS_FAILED in outcome.reason_codes


def test_trust_report_warns_on_unsupported_claims(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    report = build_trust_report(
        passing_diagnostics,
        unsupported_claims=["outcome attribution not certified"],
    )
    outcome = check_trust_report_gate(report)
    assert outcome.decision == GateDecision.WARN
    assert R.UNSUPPORTED_CLAIMS_PRESENT in outcome.reason_codes


def test_public_imports_from_mip_evaluation() -> None:
    from mip.evaluation import (
        GateDecision as GD,
    )
    from mip.evaluation import (
        GateOutcome as GO,
    )
    from mip.evaluation import (
        GatePurpose as GP,
    )
    from mip.evaluation import (
        check_calibration_signal_gate as ccal,
    )
    from mip.evaluation import (
        check_decision_surface_gate as cds,
    )
    from mip.evaluation import (
        check_experiment_evidence_gate as cee,
    )
    from mip.evaluation import (
        check_recommendation_gate as cr,
    )
    from mip.evaluation import (
        check_trust_report_gate as ctr,
    )

    assert GD.PASS.value == "pass"
    assert GO is not None
    assert GP.BUDGET_PLANNING.value == "budget_planning"
    assert callable(cee)
    assert callable(ccal)
    assert callable(cds)
    assert callable(cr)
    assert callable(ctr)


def test_min_confidence_tier_returns_lower_tier() -> None:
    assert min_confidence_tier(
        ConfidenceTier.DECISION_READY,
        ConfidenceTier.DIRECTIONAL,
    ) == ConfidenceTier.DIRECTIONAL
    assert min_confidence_tier(
        ConfidenceTier.DIRECTIONAL,
        ConfidenceTier.BLOCKED,
    ) == ConfidenceTier.BLOCKED


def test_gate_outcome_block_requires_reason_codes() -> None:
    with pytest.raises(ValueError, match="reason_codes"):
        GateOutcome(
            artifact_id="a1",
            artifact_type="test",
            purpose=GatePurpose.RESEARCH_REVIEW,
            decision=GateDecision.BLOCK,
            max_confidence_tier=ConfidenceTier.BLOCKED,
            reason_codes=[],
        )
