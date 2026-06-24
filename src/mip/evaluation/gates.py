"""Contract-driven release and readiness gates."""

from enum import StrEnum

from pydantic import Field, field_validator, model_validator

from mip.contracts import (
    ArtifactStatus,
    CalibrationSignal,
    CompatibilityStatus,
    ConfidenceTier,
    ContractBaseModel,
    DecisionSurface,
    DecisionSurfaceType,
    ExperimentEvidence,
    RecommendationContract,
    RecommendationType,
    TrustReport,
)
from mip.evaluation import reasons as R

_TIER_RANK: dict[ConfidenceTier, int] = {
    ConfidenceTier.BLOCKED: 0,
    ConfidenceTier.RESEARCH_ONLY: 1,
    ConfidenceTier.DIAGNOSTIC_ONLY: 2,
    ConfidenceTier.DIRECTIONAL: 3,
    ConfidenceTier.DECISION_READY: 4,
}

_DIAGNOSTIC_SURFACE_TYPES = frozenset(
    {
        DecisionSurfaceType.DIAGNOSTIC_CURVE,
        DecisionSurfaceType.DECOMPOSITION,
    }
)


class GateDecision(StrEnum):
    """Gate verdict for a specific purpose."""

    PASS = "pass"
    WARN = "warn"
    BLOCK = "block"


class GatePurpose(StrEnum):
    """Platform usage context being gated."""

    EXPERIMENT_CALIBRATION = "experiment_calibration"
    MODEL_CALIBRATION = "model_calibration"
    BUDGET_PLANNING = "budget_planning"
    RECOMMENDATION_DECISIONING = "recommendation_decisioning"
    TRUST_REPORTING = "trust_reporting"
    RESEARCH_REVIEW = "research_review"


class GateOutcome(ContractBaseModel):
    """Structured result of a release gate evaluation."""

    artifact_id: str
    artifact_type: str
    purpose: GatePurpose
    decision: GateDecision
    max_confidence_tier: ConfidenceTier
    reason_codes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    details: dict[str, str | int | float | bool] = Field(default_factory=dict)

    @field_validator("artifact_id", "artifact_type")
    @classmethod
    def non_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "artifact_id and artifact_type cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def decision_requires_reasons(self) -> "GateOutcome":
        if self.decision == GateDecision.BLOCK and not self.reason_codes:
            msg = "blocked gate outcomes require reason_codes"
            raise ValueError(msg)
        if self.decision == GateDecision.WARN and not self.warnings and not self.reason_codes:
            msg = "warn gate outcomes require warnings or reason_codes"
            raise ValueError(msg)
        return self


def min_confidence_tier(*tiers: ConfidenceTier) -> ConfidenceTier:
    """Return the most restrictive (lowest) confidence tier."""
    return min(tiers, key=lambda tier: _TIER_RANK[_coerce_tier(tier)])


def _coerce_tier(tier: ConfidenceTier | str) -> ConfidenceTier:
    if isinstance(tier, ConfidenceTier):
        return tier
    return ConfidenceTier(tier)


def _outcome(
    *,
    artifact_id: str,
    artifact_type: str,
    purpose: GatePurpose,
    decision: GateDecision,
    max_confidence_tier: ConfidenceTier,
    reason_codes: list[str] | None = None,
    warnings: list[str] | None = None,
    details: dict[str, str | int | float | bool] | None = None,
) -> GateOutcome:
    return GateOutcome(
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        purpose=purpose,
        decision=decision,
        max_confidence_tier=max_confidence_tier,
        reason_codes=reason_codes or [],
        warnings=warnings or [],
        details=details or {},
    )


def check_experiment_evidence_gate(
    evidence: ExperimentEvidence,
    purpose: GatePurpose = GatePurpose.EXPERIMENT_CALIBRATION,
) -> GateOutcome:
    """Gate experiment evidence for calibration and related uses."""
    blocks: list[str] = []
    warns: list[str] = []
    input_tier = _coerce_tier(evidence.confidence_tier)
    max_tier = input_tier

    if not (
        evidence.design_diagnostics.passed
        and evidence.execution_diagnostics.passed
        and evidence.inference_diagnostics.passed
    ):
        blocks.append(R.DIAGNOSTICS_FAILED)

    if evidence.quality_score < 0.5:
        blocks.append(R.LOW_QUALITY_SCORE)

    if input_tier == ConfidenceTier.BLOCKED:
        blocks.append(R.BLOCKED_CONFIDENCE_TIER)

    if blocks:
        return _outcome(
            artifact_id=evidence.evidence_id,
            artifact_type="experiment_evidence",
            purpose=purpose,
            decision=GateDecision.BLOCK,
            max_confidence_tier=ConfidenceTier.BLOCKED,
            reason_codes=blocks,
        )

    if evidence.freshness_score < 0.3:
        warns.append(R.LOW_FRESHNESS_SCORE)

    if evidence.status not in (ArtifactStatus.VALIDATED, ArtifactStatus.CERTIFIED):
        warns.append(R.NOT_VALIDATED_OR_CERTIFIED)

    if input_tier == ConfidenceTier.RESEARCH_ONLY:
        warns.append(R.RESEARCH_ONLY)
        max_tier = min_confidence_tier(max_tier, ConfidenceTier.RESEARCH_ONLY)

    max_tier = min_confidence_tier(max_tier, input_tier)

    if warns:
        return _outcome(
            artifact_id=evidence.evidence_id,
            artifact_type="experiment_evidence",
            purpose=purpose,
            decision=GateDecision.WARN,
            max_confidence_tier=max_tier,
            reason_codes=warns,
        )

    return _outcome(
        artifact_id=evidence.evidence_id,
        artifact_type="experiment_evidence",
        purpose=purpose,
        decision=GateDecision.PASS,
        max_confidence_tier=max_tier,
    )


def check_calibration_signal_gate(
    signal: CalibrationSignal,
    purpose: GatePurpose = GatePurpose.MODEL_CALIBRATION,
) -> GateOutcome:
    """Gate calibration signals before model parameter updates."""
    blocks: list[str] = []
    warns: list[str] = []
    input_tier = _coerce_tier(signal.confidence_tier)
    max_tier = input_tier

    if not signal.diagnostics.passed:
        blocks.append(R.DIAGNOSTICS_FAILED)

    if signal.compatibility_status == CompatibilityStatus.INCOMPATIBLE:
        blocks.append(R.INCOMPATIBLE_CALIBRATION)

    if signal.weight == 0:
        blocks.append(R.ZERO_CALIBRATION_WEIGHT)

    if input_tier == ConfidenceTier.BLOCKED:
        blocks.append(R.BLOCKED_CONFIDENCE_TIER)

    if blocks:
        return _outcome(
            artifact_id=signal.calibration_id,
            artifact_type="calibration_signal",
            purpose=purpose,
            decision=GateDecision.BLOCK,
            max_confidence_tier=ConfidenceTier.BLOCKED,
            reason_codes=blocks,
        )

    warning_messages: list[str] = []

    if signal.compatibility_status == CompatibilityStatus.UNKNOWN:
        warning_messages.append("compatibility status is unknown")
        max_tier = min_confidence_tier(max_tier, ConfidenceTier.DIAGNOSTIC_ONLY)

    if signal.compatibility_status == CompatibilityStatus.PARTIALLY_COMPATIBLE:
        warning_messages.append("compatibility is partially_compatible")
        max_tier = min_confidence_tier(max_tier, ConfidenceTier.DIRECTIONAL)

    if signal.freshness_decay < 0.3:
        warns.append(R.LOW_FRESHNESS_SCORE)

    max_tier = min_confidence_tier(max_tier, input_tier)

    if warns or warning_messages:
        return _outcome(
            artifact_id=signal.calibration_id,
            artifact_type="calibration_signal",
            purpose=purpose,
            decision=GateDecision.WARN,
            max_confidence_tier=max_tier,
            reason_codes=warns,
            warnings=warning_messages,
        )

    return _outcome(
        artifact_id=signal.calibration_id,
        artifact_type="calibration_signal",
        purpose=purpose,
        decision=GateDecision.PASS,
        max_confidence_tier=max_tier,
    )


def check_decision_surface_gate(
    surface: DecisionSurface,
    purpose: GatePurpose = GatePurpose.BUDGET_PLANNING,
) -> GateOutcome:
    """Gate decision surfaces for budget planning and related uses."""
    blocks: list[str] = []
    warns: list[str] = []

    if purpose == GatePurpose.BUDGET_PLANNING:
        if surface.surface_type != DecisionSurfaceType.FULL_PANEL_DELTA_MU:
            blocks.append(R.NOT_FULL_PANEL_DELTA_MU)
        if surface.surface_type in _DIAGNOSTIC_SURFACE_TYPES:
            blocks.append(R.UNSUPPORTED_DECISION_SURFACE)

        if surface.certification_status == ArtifactStatus.BLOCKED:
            blocks.append(R.BLOCKED_CONFIDENCE_TIER)

        if not surface.reliability_scorecard_id:
            blocks.append(R.MISSING_RELIABILITY_SCORECARD)

        if blocks:
            return _outcome(
                artifact_id=surface.surface_id,
                artifact_type="decision_surface",
                purpose=purpose,
                decision=GateDecision.BLOCK,
                max_confidence_tier=ConfidenceTier.BLOCKED,
                reason_codes=_dedupe(blocks),
            )

        max_tier = ConfidenceTier.DECISION_READY

        if surface.certification_status != ArtifactStatus.CERTIFIED:
            warns.append(R.NOT_VALIDATED_OR_CERTIFIED)
            max_tier = min_confidence_tier(max_tier, ConfidenceTier.DIRECTIONAL)

        if surface.unsupported_claims:
            warns.append(R.UNSUPPORTED_CLAIMS_PRESENT)

        if warns:
            return _outcome(
                artifact_id=surface.surface_id,
                artifact_type="decision_surface",
                purpose=purpose,
                decision=GateDecision.WARN,
                max_confidence_tier=max_tier,
                reason_codes=warns,
            )

        return _outcome(
            artifact_id=surface.surface_id,
            artifact_type="decision_surface",
            purpose=purpose,
            decision=GateDecision.PASS,
            max_confidence_tier=max_tier,
        )

    return _outcome(
        artifact_id=surface.surface_id,
        artifact_type="decision_surface",
        purpose=purpose,
        decision=GateDecision.PASS,
        max_confidence_tier=ConfidenceTier.DIAGNOSTIC_ONLY,
    )


def check_recommendation_gate(
    recommendation: RecommendationContract,
    purpose: GatePurpose = GatePurpose.RECOMMENDATION_DECISIONING,
) -> GateOutcome:
    """Gate recommendations before decision-ready presentation."""
    blocks: list[str] = []
    warns: list[str] = []
    input_tier = _coerce_tier(recommendation.confidence_tier)
    max_tier = input_tier

    if input_tier == ConfidenceTier.BLOCKED:
        blocks.append(R.BLOCKED_CONFIDENCE_TIER)

    if not recommendation.diagnostics_summary.passed:
        blocks.append(R.DIAGNOSTICS_FAILED)

    if recommendation.recommendation_type == RecommendationType.BUDGET_SHIFT:
        if not recommendation.decision_surface_ids:
            blocks.append(R.MISSING_DECISION_SURFACE)

    if input_tier == ConfidenceTier.DECISION_READY:
        if not recommendation.evidence_ids and not recommendation.decision_surface_ids:
            blocks.append(R.MISSING_EVIDENCE)

    if blocks:
        return _outcome(
            artifact_id=recommendation.recommendation_id,
            artifact_type="recommendation",
            purpose=purpose,
            decision=GateDecision.BLOCK,
            max_confidence_tier=ConfidenceTier.BLOCKED,
            reason_codes=_dedupe(blocks),
        )

    if input_tier == ConfidenceTier.RESEARCH_ONLY:
        warns.append(R.RESEARCH_ONLY)
        max_tier = min_confidence_tier(max_tier, ConfidenceTier.RESEARCH_ONLY)

    if recommendation.unsupported_claims:
        warns.append(R.UNSUPPORTED_CLAIMS_PRESENT)

    max_tier = min_confidence_tier(max_tier, input_tier)

    if warns:
        return _outcome(
            artifact_id=recommendation.recommendation_id,
            artifact_type="recommendation",
            purpose=purpose,
            decision=GateDecision.WARN,
            max_confidence_tier=max_tier,
            reason_codes=warns,
        )

    return _outcome(
        artifact_id=recommendation.recommendation_id,
        artifact_type="recommendation",
        purpose=purpose,
        decision=GateDecision.PASS,
        max_confidence_tier=max_tier,
    )


def check_trust_report_gate(
    report: TrustReport,
    purpose: GatePurpose = GatePurpose.TRUST_REPORTING,
) -> GateOutcome:
    """Gate trust reports for downstream decision support."""
    blocks: list[str] = []
    warns: list[str] = []
    input_tier = _coerce_tier(report.confidence_tier)
    max_tier = input_tier

    if not report.diagnostics.passed:
        blocks.append(R.TRUST_DIAGNOSTICS_FAILED)

    if input_tier == ConfidenceTier.BLOCKED:
        blocks.append(R.BLOCKED_CONFIDENCE_TIER)

    if blocks:
        return _outcome(
            artifact_id=report.trust_report_id,
            artifact_type="trust_report",
            purpose=purpose,
            decision=GateDecision.BLOCK,
            max_confidence_tier=ConfidenceTier.BLOCKED,
            reason_codes=_dedupe(blocks),
        )

    if input_tier == ConfidenceTier.RESEARCH_ONLY:
        warns.append(R.RESEARCH_ONLY)
        max_tier = min_confidence_tier(max_tier, ConfidenceTier.RESEARCH_ONLY)

    if report.unsupported_claims:
        warns.append(R.UNSUPPORTED_CLAIMS_PRESENT)

    max_tier = min_confidence_tier(max_tier, input_tier)

    if warns:
        return _outcome(
            artifact_id=report.trust_report_id,
            artifact_type="trust_report",
            purpose=purpose,
            decision=GateDecision.WARN,
            max_confidence_tier=max_tier,
            reason_codes=warns,
        )

    return _outcome(
        artifact_id=report.trust_report_id,
        artifact_type="trust_report",
        purpose=purpose,
        decision=GateDecision.PASS,
        max_confidence_tier=max_tier,
    )


def _dedupe(codes: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for code in codes:
        if code not in seen:
            seen.add(code)
            ordered.append(code)
    return ordered
