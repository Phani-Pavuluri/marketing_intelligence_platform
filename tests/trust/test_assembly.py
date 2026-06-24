"""Tests for trust report assembly from gate outcomes."""

from datetime import UTC, datetime

from mip.contracts import ConfidenceTier, TrustReport
from mip.evaluation import reasons as R
from mip.evaluation.gates import GateDecision, GateOutcome, GatePurpose
from mip.trust import (
    build_trust_report_from_gates,
    collect_reason_codes,
    collect_warnings,
    confidence_from_gate_outcomes,
    decision_from_gate_outcomes,
)


def _outcome(
    *,
    decision: GateDecision,
    max_tier: ConfidenceTier,
    reason_codes: list[str] | None = None,
    warnings: list[str] | None = None,
    artifact_id: str = "art-001",
) -> GateOutcome:
    codes = reason_codes or []
    warn = warnings or []
    if decision == GateDecision.BLOCK and not codes:
        codes = [R.DIAGNOSTICS_FAILED]
    if decision == GateDecision.WARN and not codes and not warn:
        codes = [R.LOW_FRESHNESS_SCORE]
    return GateOutcome(
        artifact_id=artifact_id,
        artifact_type="test_artifact",
        purpose=GatePurpose.RESEARCH_REVIEW,
        decision=decision,
        max_confidence_tier=max_tier,
        reason_codes=codes,
        warnings=warn,
    )


def test_empty_gate_outcomes_produce_blocked_trust_report() -> None:
    report = build_trust_report_from_gates(
        trust_report_id="trust-001",
        output_id="out-001",
        output_type="recommendation",
        gate_outcomes=[],
    )
    assert report.confidence_tier == ConfidenceTier.BLOCKED
    assert report.diagnostics.passed is False
    assert R.NO_GATE_OUTCOMES in report.diagnostics.failures
    assert R.NO_GATE_OUTCOMES in report.warnings


def test_pass_only_gates_produce_passing_diagnostics() -> None:
    outcomes = [
        _outcome(decision=GateDecision.PASS, max_tier=ConfidenceTier.DIRECTIONAL),
        _outcome(
            decision=GateDecision.PASS,
            max_tier=ConfidenceTier.DECISION_READY,
            artifact_id="art-002",
        ),
    ]
    report = build_trust_report_from_gates(
        trust_report_id="trust-002",
        output_id="out-002",
        output_type="recommendation",
        gate_outcomes=outcomes,
    )
    assert report.diagnostics.passed is True
    assert report.confidence_tier == ConfidenceTier.DIRECTIONAL
    assert decision_from_gate_outcomes(outcomes) == GateDecision.PASS


def test_warning_gate_outcomes_produce_passed_diagnostics_with_warnings() -> None:
    outcomes = [
        _outcome(
            decision=GateDecision.WARN,
            max_tier=ConfidenceTier.DIRECTIONAL,
            reason_codes=[R.LOW_FRESHNESS_SCORE],
            warnings=["freshness below policy"],
        ),
    ]
    report = build_trust_report_from_gates(
        trust_report_id="trust-003",
        output_id="out-003",
        output_type="experiment_evidence",
        gate_outcomes=outcomes,
    )
    assert report.diagnostics.passed is True
    assert R.LOW_FRESHNESS_SCORE in report.warnings
    assert "freshness below policy" in report.warnings
    assert decision_from_gate_outcomes(outcomes) == GateDecision.WARN


def test_block_gate_outcomes_produce_failed_diagnostics() -> None:
    outcomes = [
        _outcome(
            decision=GateDecision.BLOCK,
            max_tier=ConfidenceTier.BLOCKED,
            reason_codes=[R.DIAGNOSTICS_FAILED],
        ),
    ]
    report = build_trust_report_from_gates(
        trust_report_id="trust-004",
        output_id="out-004",
        output_type="calibration_signal",
        gate_outcomes=outcomes,
    )
    assert report.diagnostics.passed is False
    assert R.DIAGNOSTICS_FAILED in report.diagnostics.failures
    assert report.confidence_tier == ConfidenceTier.BLOCKED


def test_confidence_from_gate_outcomes_returns_most_restrictive_tier() -> None:
    outcomes = [
        _outcome(decision=GateDecision.PASS, max_tier=ConfidenceTier.DECISION_READY),
        _outcome(
            decision=GateDecision.PASS,
            max_tier=ConfidenceTier.DIAGNOSTIC_ONLY,
            artifact_id="art-002",
        ),
    ]
    assert confidence_from_gate_outcomes(outcomes) == ConfidenceTier.DIAGNOSTIC_ONLY
    assert confidence_from_gate_outcomes([]) == ConfidenceTier.BLOCKED


def test_decision_from_gate_outcomes_block_if_any_block() -> None:
    outcomes = [
        _outcome(decision=GateDecision.PASS, max_tier=ConfidenceTier.DIRECTIONAL),
        _outcome(
            decision=GateDecision.BLOCK,
            max_tier=ConfidenceTier.BLOCKED,
            reason_codes=[R.BLOCKED_CONFIDENCE_TIER],
            artifact_id="art-002",
        ),
    ]
    assert decision_from_gate_outcomes(outcomes) == GateDecision.BLOCK
    assert decision_from_gate_outcomes([]) == GateDecision.BLOCK


def test_decision_from_gate_outcomes_warn_if_warning_and_no_block() -> None:
    outcomes = [
        _outcome(decision=GateDecision.PASS, max_tier=ConfidenceTier.DIRECTIONAL),
        _outcome(
            decision=GateDecision.WARN,
            max_tier=ConfidenceTier.DIRECTIONAL,
            reason_codes=[R.NOT_VALIDATED_OR_CERTIFIED],
            artifact_id="art-002",
        ),
    ]
    assert decision_from_gate_outcomes(outcomes) == GateDecision.WARN


def test_collect_reason_codes_deduplicates_preserving_order() -> None:
    outcomes = [
        _outcome(
            decision=GateDecision.WARN,
            max_tier=ConfidenceTier.DIRECTIONAL,
            reason_codes=[R.LOW_FRESHNESS_SCORE, R.RESEARCH_ONLY],
        ),
        _outcome(
            decision=GateDecision.BLOCK,
            max_tier=ConfidenceTier.BLOCKED,
            reason_codes=[R.RESEARCH_ONLY, R.DIAGNOSTICS_FAILED],
            artifact_id="art-002",
        ),
    ]
    assert collect_reason_codes(outcomes) == [
        R.LOW_FRESHNESS_SCORE,
        R.RESEARCH_ONLY,
        R.DIAGNOSTICS_FAILED,
    ]


def test_collect_warnings_deduplicates_preserving_order() -> None:
    outcomes = [
        _outcome(
            decision=GateDecision.WARN,
            max_tier=ConfidenceTier.DIRECTIONAL,
            reason_codes=[R.LOW_FRESHNESS_SCORE],
            warnings=["stale inputs", "review recommended"],
        ),
        _outcome(
            decision=GateDecision.WARN,
            max_tier=ConfidenceTier.DIRECTIONAL,
            reason_codes=[R.NOT_VALIDATED_OR_CERTIFIED],
            warnings=["stale inputs"],
            artifact_id="art-002",
        ),
    ]
    assert collect_warnings(outcomes) == [
        "stale inputs",
        "review recommended",
    ]


def test_build_trust_report_includes_assumptions() -> None:
    report = build_trust_report_from_gates(
        trust_report_id="trust-005",
        output_id="out-005",
        output_type="recommendation",
        gate_outcomes=[
            _outcome(decision=GateDecision.PASS, max_tier=ConfidenceTier.DIRECTIONAL),
        ],
        assumptions=["panel stable", "no interference"],
    )
    assert report.assumptions == ["panel stable", "no interference"]


def test_build_trust_report_includes_unsupported_claims() -> None:
    report = build_trust_report_from_gates(
        trust_report_id="trust-006",
        output_id="out-006",
        output_type="recommendation",
        gate_outcomes=[
            _outcome(decision=GateDecision.PASS, max_tier=ConfidenceTier.DIRECTIONAL),
        ],
        unsupported_claims=["cannot certify cross-channel synergy"],
    )
    assert report.unsupported_claims == ["cannot certify cross-channel synergy"]


def test_uncertainty_summary_includes_gate_counts() -> None:
    outcomes = [
        _outcome(decision=GateDecision.PASS, max_tier=ConfidenceTier.DIRECTIONAL),
        _outcome(
            decision=GateDecision.WARN,
            max_tier=ConfidenceTier.DIRECTIONAL,
            reason_codes=[R.LOW_FRESHNESS_SCORE],
            artifact_id="art-002",
        ),
        _outcome(
            decision=GateDecision.BLOCK,
            max_tier=ConfidenceTier.BLOCKED,
            reason_codes=[R.DIAGNOSTICS_FAILED],
            artifact_id="art-003",
        ),
    ]
    report = build_trust_report_from_gates(
        trust_report_id="trust-007",
        output_id="out-007",
        output_type="decision_surface",
        gate_outcomes=outcomes,
    )
    assert report.uncertainty_summary["gate_count"] == 3
    assert report.uncertainty_summary["pass_count"] == 1
    assert report.uncertainty_summary["warn_count"] == 1
    assert report.uncertainty_summary["block_count"] == 1


def test_public_imports_from_mip_trust() -> None:
    from mip.trust import (
        build_trust_report_from_gates as build_fn,
    )
    from mip.trust import (
        confidence_from_gate_outcomes as confidence_fn,
    )
    from mip.trust import (
        decision_from_gate_outcomes as decision_fn,
    )

    assert callable(build_fn)
    assert callable(confidence_fn)
    assert callable(decision_fn)


def test_blocked_trust_report_satisfies_validation() -> None:
    report = build_trust_report_from_gates(
        trust_report_id="trust-008",
        output_id="out-008",
        output_type="recommendation",
        gate_outcomes=[
            _outcome(
                decision=GateDecision.BLOCK,
                max_tier=ConfidenceTier.BLOCKED,
                reason_codes=[R.MISSING_EVIDENCE],
            ),
        ],
    )
    assert isinstance(report, TrustReport)
    assert report.confidence_tier == ConfidenceTier.BLOCKED
    assert report.warnings or report.unsupported_claims


def test_decision_ready_requires_passing_diagnostics() -> None:
    outcomes = [
        _outcome(decision=GateDecision.PASS, max_tier=ConfidenceTier.DECISION_READY),
    ]
    report = build_trust_report_from_gates(
        trust_report_id="trust-009",
        output_id="out-009",
        output_type="decision_surface",
        gate_outcomes=outcomes,
        created_at=datetime(2025, 6, 1, tzinfo=UTC),
    )
    assert report.confidence_tier == ConfidenceTier.DECISION_READY
    assert report.diagnostics.passed is True
