"""Route platform contract artifacts through release gates into trust reports."""

from datetime import datetime

from mip.contracts import (
    CalibrationSignal,
    ConfidenceTier,
    DecisionSurface,
    ExperimentEvidence,
    RecommendationContract,
    TrustReport,
)
from mip.evaluation import reasons as R
from mip.evaluation.gates import (
    GateDecision,
    GateOutcome,
    GatePurpose,
    check_calibration_signal_gate,
    check_decision_surface_gate,
    check_experiment_evidence_gate,
    check_recommendation_gate,
    check_trust_report_gate,
)
from mip.trust.assembly import build_trust_report_from_gates


def artifact_id_for_trust(artifact: object) -> str:
    """Return the canonical identifier for a supported artifact."""
    if isinstance(artifact, ExperimentEvidence):
        return artifact.evidence_id
    if isinstance(artifact, CalibrationSignal):
        return artifact.calibration_id
    if isinstance(artifact, DecisionSurface):
        return artifact.surface_id
    if isinstance(artifact, RecommendationContract):
        return artifact.recommendation_id
    if isinstance(artifact, TrustReport):
        return artifact.trust_report_id
    return "unsupported_artifact"


def artifact_type_for_trust(artifact: object) -> str:
    """Return a stable artifact type string for trust reporting."""
    if isinstance(artifact, ExperimentEvidence):
        return "experiment_evidence"
    if isinstance(artifact, CalibrationSignal):
        return "calibration_signal"
    if isinstance(artifact, DecisionSurface):
        return "decision_surface"
    if isinstance(artifact, RecommendationContract):
        return "recommendation"
    if isinstance(artifact, TrustReport):
        return "trust_report"
    return "unsupported"


def gate_outcomes_for_artifact(artifact: object) -> list[GateOutcome]:
    """Run the appropriate release gate for a contract artifact."""
    if isinstance(artifact, ExperimentEvidence):
        return [check_experiment_evidence_gate(artifact)]
    if isinstance(artifact, CalibrationSignal):
        return [check_calibration_signal_gate(artifact)]
    if isinstance(artifact, DecisionSurface):
        return [check_decision_surface_gate(artifact)]
    if isinstance(artifact, RecommendationContract):
        return [check_recommendation_gate(artifact)]
    if isinstance(artifact, TrustReport):
        return [check_trust_report_gate(artifact)]

    return [
        GateOutcome(
            artifact_id="unsupported_artifact",
            artifact_type="unsupported",
            purpose=GatePurpose.TRUST_REPORTING,
            decision=GateDecision.BLOCK,
            max_confidence_tier=ConfidenceTier.BLOCKED,
            reason_codes=[R.UNSUPPORTED_ARTIFACT_TYPE],
            warnings=[R.UNSUPPORTED_ARTIFACT_TYPE],
        )
    ]


def build_trust_report_for_artifact(
    artifact: object,
    *,
    trust_report_id: str | None = None,
    assumptions: list[str] | None = None,
    unsupported_claims: list[str] | None = None,
    trace_uri: str | None = None,
    created_at: datetime | None = None,
) -> TrustReport:
    """Evaluate gates for an artifact and assemble a TrustReport."""
    artifact_id = artifact_id_for_trust(artifact)
    artifact_type = artifact_type_for_trust(artifact)
    gate_outcomes = gate_outcomes_for_artifact(artifact)

    report_id = trust_report_id or f"trust_report:{artifact_type}:{artifact_id}"
    output_id = artifact.trust_report_id if isinstance(artifact, TrustReport) else artifact_id

    return build_trust_report_from_gates(
        trust_report_id=report_id,
        output_id=output_id,
        output_type=artifact_type,
        gate_outcomes=gate_outcomes,
        assumptions=assumptions,
        unsupported_claims=unsupported_claims,
        trace_uri=trace_uri,
        created_at=created_at,
    )
