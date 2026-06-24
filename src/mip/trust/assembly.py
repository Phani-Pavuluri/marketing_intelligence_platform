"""Assemble TrustReport artifacts from release gate outcomes."""

from collections.abc import Iterable
from datetime import UTC, datetime

from mip.contracts import ConfidenceTier, DiagnosticSummary, TrustReport
from mip.evaluation import reasons as R
from mip.evaluation.gates import GateDecision, GateOutcome, min_confidence_tier


def confidence_from_gate_outcomes(outcomes: list[GateOutcome]) -> ConfidenceTier:
    """Return the most restrictive max confidence tier across gate outcomes."""
    if not outcomes:
        return ConfidenceTier.BLOCKED
    return min_confidence_tier(*(outcome.max_confidence_tier for outcome in outcomes))


def decision_from_gate_outcomes(outcomes: list[GateOutcome]) -> GateDecision:
    """Return the aggregate gate decision (block > warn > pass)."""
    if not outcomes:
        return GateDecision.BLOCK
    if any(outcome.decision == GateDecision.BLOCK for outcome in outcomes):
        return GateDecision.BLOCK
    if any(outcome.decision == GateDecision.WARN for outcome in outcomes):
        return GateDecision.WARN
    return GateDecision.PASS


def collect_reason_codes(outcomes: list[GateOutcome]) -> list[str]:
    """Collect de-duplicated reason codes in stable first-seen order."""
    return _dedupe_stable(
        code for outcome in outcomes for code in outcome.reason_codes
    )


def collect_warnings(outcomes: list[GateOutcome]) -> list[str]:
    """Collect de-duplicated warnings in stable first-seen order."""
    return _dedupe_stable(
        warning for outcome in outcomes for warning in outcome.warnings
    )


def summarize_gate_outcomes(
    outcomes: list[GateOutcome],
) -> dict[str, int | list[str]]:
    """Summarize gate outcomes by decision counts and collected messages."""
    return {
        "gate_count": len(outcomes),
        "pass_count": sum(1 for o in outcomes if o.decision == GateDecision.PASS),
        "warn_count": sum(1 for o in outcomes if o.decision == GateDecision.WARN),
        "block_count": sum(1 for o in outcomes if o.decision == GateDecision.BLOCK),
        "reason_codes": collect_reason_codes(outcomes),
        "warnings": collect_warnings(outcomes),
    }


def build_trust_report_from_gates(
    *,
    trust_report_id: str,
    output_id: str,
    output_type: str,
    gate_outcomes: list[GateOutcome],
    assumptions: list[str] | None = None,
    unsupported_claims: list[str] | None = None,
    trace_uri: str | None = None,
    created_at: datetime | None = None,
) -> TrustReport:
    """Build a TrustReport from one or more gate outcomes."""
    assumptions_list = list(assumptions or [])
    unsupported_list = list(unsupported_claims or [])
    timestamp = created_at or datetime.now(tz=UTC)

    if not gate_outcomes:
        return TrustReport(
            trust_report_id=trust_report_id,
            output_id=output_id,
            output_type=output_type,
            confidence_tier=ConfidenceTier.BLOCKED,
            diagnostics=DiagnosticSummary(
                passed=False,
                failures=[R.NO_GATE_OUTCOMES],
            ),
            assumptions=assumptions_list,
            warnings=[R.NO_GATE_OUTCOMES],
            unsupported_claims=unsupported_list,
            uncertainty_summary={
                "gate_count": 0,
                "pass_count": 0,
                "warn_count": 0,
                "block_count": 0,
            },
            trace_uri=trace_uri,
            created_at=timestamp,
        )

    aggregate_decision = decision_from_gate_outcomes(gate_outcomes)
    confidence_tier = confidence_from_gate_outcomes(gate_outcomes)
    if aggregate_decision == GateDecision.BLOCK:
        confidence_tier = ConfidenceTier.BLOCKED

    reason_codes = collect_reason_codes(gate_outcomes)
    outcome_warnings = collect_warnings(gate_outcomes)
    warn_outcome_reasons = [
        code
        for outcome in gate_outcomes
        if outcome.decision == GateDecision.WARN
        for code in outcome.reason_codes
    ]
    report_warnings = _dedupe_stable([*outcome_warnings, *warn_outcome_reasons])

    if aggregate_decision == GateDecision.PASS:
        diagnostics = DiagnosticSummary(passed=True)
    elif aggregate_decision == GateDecision.WARN:
        diagnostics = DiagnosticSummary(
            passed=True,
            warnings=report_warnings or reason_codes,
        )
    else:
        diagnostics = DiagnosticSummary(
            passed=False,
            failures=reason_codes,
            warnings=outcome_warnings,
        )

    if confidence_tier == ConfidenceTier.BLOCKED:
        if not report_warnings and not unsupported_list:
            report_warnings = _dedupe_stable([*reason_codes, R.NO_GATE_OUTCOMES])

    uncertainty_summary: dict[str, float | int | str | bool] = {
        "gate_count": len(gate_outcomes),
        "pass_count": sum(1 for o in gate_outcomes if o.decision == GateDecision.PASS),
        "warn_count": sum(1 for o in gate_outcomes if o.decision == GateDecision.WARN),
        "block_count": sum(1 for o in gate_outcomes if o.decision == GateDecision.BLOCK),
    }

    return TrustReport(
        trust_report_id=trust_report_id,
        output_id=output_id,
        output_type=output_type,
        confidence_tier=confidence_tier,
        diagnostics=diagnostics,
        assumptions=assumptions_list,
        warnings=report_warnings,
        unsupported_claims=unsupported_list,
        uncertainty_summary=uncertainty_summary,
        trace_uri=trace_uri,
        created_at=timestamp,
    )


def _dedupe_stable(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
