"""Trust, explanation, diagnostics, and confidence tiering."""

from mip.trust.assembly import (
    build_trust_report_from_gates,
    collect_reason_codes,
    collect_warnings,
    confidence_from_gate_outcomes,
    decision_from_gate_outcomes,
    summarize_gate_outcomes,
)
from mip.trust.router import (
    artifact_id_for_trust,
    artifact_type_for_trust,
    build_trust_report_for_artifact,
    gate_outcomes_for_artifact,
)

__all__ = [
    "artifact_id_for_trust",
    "artifact_type_for_trust",
    "build_trust_report_for_artifact",
    "build_trust_report_from_gates",
    "collect_reason_codes",
    "collect_warnings",
    "confidence_from_gate_outcomes",
    "decision_from_gate_outcomes",
    "gate_outcomes_for_artifact",
    "summarize_gate_outcomes",
]
