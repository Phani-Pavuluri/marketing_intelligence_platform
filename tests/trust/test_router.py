"""Tests for artifact trust evaluation router."""

from mip.contracts import ConfidenceTier, DiagnosticSummary, Estimand, TrustReport
from mip.evaluation import reasons as R
from mip.evaluation.gates import GateDecision
from mip.trust import (
    artifact_id_for_trust,
    artifact_type_for_trust,
    build_trust_report_for_artifact,
    gate_outcomes_for_artifact,
)
from tests.trust.conftest import (
    build_calibration_signal,
    build_decision_surface,
    build_experiment_evidence,
    build_recommendation,
    build_trust_report_input,
)


def test_artifact_id_for_trust_experiment_evidence(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(delta_mu_estimand, passing_diagnostics)
    assert artifact_id_for_trust(evidence) == "exp-001"


def test_artifact_type_for_trust_experiment_evidence(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(delta_mu_estimand, passing_diagnostics)
    assert artifact_type_for_trust(evidence) == "experiment_evidence"


def test_gate_outcomes_for_experiment_evidence(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(delta_mu_estimand, passing_diagnostics)
    outcomes = gate_outcomes_for_artifact(evidence)
    assert len(outcomes) == 1
    assert outcomes[0].artifact_type == "experiment_evidence"
    assert outcomes[0].artifact_id == "exp-001"


def test_build_trust_report_for_experiment_evidence(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(delta_mu_estimand, passing_diagnostics)
    report = build_trust_report_for_artifact(evidence)
    assert isinstance(report, TrustReport)
    assert report.output_id == "exp-001"
    assert report.output_type == "experiment_evidence"
    assert report.trust_report_id == "trust_report:experiment_evidence:exp-001"


def test_build_trust_report_for_calibration_signal(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    signal = build_calibration_signal(passing_diagnostics)
    report = build_trust_report_for_artifact(signal)
    assert report.output_id == "cal-001"
    assert report.output_type == "calibration_signal"


def test_build_trust_report_for_decision_surface(
    delta_mu_estimand: Estimand,
) -> None:
    surface = build_decision_surface(delta_mu_estimand)
    report = build_trust_report_for_artifact(surface)
    assert report.output_id == "surf-001"
    assert report.output_type == "decision_surface"
    assert report.confidence_tier == ConfidenceTier.DECISION_READY


def test_build_trust_report_for_recommendation(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    recommendation = build_recommendation(passing_diagnostics)
    report = build_trust_report_for_artifact(recommendation)
    assert report.output_id == "rec-001"
    assert report.output_type == "recommendation"


def test_build_trust_report_for_trust_report(
    passing_diagnostics: DiagnosticSummary,
) -> None:
    trust_input = build_trust_report_input(passing_diagnostics)
    report = build_trust_report_for_artifact(trust_input)
    assert report.output_id == "tr_123"
    assert report.output_type == "trust_report"
    assert report.trust_report_id == "trust_report:trust_report:tr_123"


def test_unsupported_artifact_returns_blocked_trust_report() -> None:
    report = build_trust_report_for_artifact({"not": "a contract"})
    assert report.confidence_tier == ConfidenceTier.BLOCKED
    assert report.diagnostics.passed is False


def test_unsupported_artifact_includes_unsupported_reason_code() -> None:
    outcomes = gate_outcomes_for_artifact(42)
    assert len(outcomes) == 1
    assert outcomes[0].decision == GateDecision.BLOCK
    assert R.UNSUPPORTED_ARTIFACT_TYPE in outcomes[0].reason_codes

    report = build_trust_report_for_artifact(42)
    assert R.UNSUPPORTED_ARTIFACT_TYPE in report.diagnostics.failures


def test_default_trust_report_id_is_deterministic(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(delta_mu_estimand, passing_diagnostics)
    report = build_trust_report_for_artifact(evidence)
    assert report.trust_report_id == "trust_report:experiment_evidence:exp-001"


def test_explicit_trust_report_id_overrides_default(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(delta_mu_estimand, passing_diagnostics)
    report = build_trust_report_for_artifact(
        evidence,
        trust_report_id="custom-trust-999",
    )
    assert report.trust_report_id == "custom-trust-999"


def test_assumptions_passed_into_generated_trust_report(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(delta_mu_estimand, passing_diagnostics)
    report = build_trust_report_for_artifact(
        evidence,
        assumptions=["stable panel", "no spillover"],
    )
    assert report.assumptions == ["stable panel", "no spillover"]


def test_unsupported_claims_passed_into_generated_trust_report(
    delta_mu_estimand: Estimand,
    passing_diagnostics: DiagnosticSummary,
) -> None:
    evidence = build_experiment_evidence(delta_mu_estimand, passing_diagnostics)
    report = build_trust_report_for_artifact(
        evidence,
        unsupported_claims=["cannot certify incrementality at geo level"],
    )
    assert report.unsupported_claims == ["cannot certify incrementality at geo level"]


def test_public_imports_from_mip_trust() -> None:
    from mip.trust import (
        artifact_id_for_trust as aid,
    )
    from mip.trust import (
        artifact_type_for_trust as atype,
    )
    from mip.trust import (
        build_trust_report_for_artifact as build_fn,
    )
    from mip.trust import (
        gate_outcomes_for_artifact as gates_fn,
    )

    assert callable(aid)
    assert callable(atype)
    assert callable(build_fn)
    assert callable(gates_fn)
