"""Calibration traceability audit over in-memory evidence registries."""

from collections.abc import Iterable
from datetime import UTC, datetime

from pydantic import Field, field_validator, model_validator

from mip.contracts import (
    CalibrationSignal,
    CompatibilityStatus,
    ConfidenceTier,
    ContractBaseModel,
    TrustReport,
)
from mip.evaluation import reasons as R
from mip.evaluation.gates import (
    GateDecision,
    GateOutcome,
    GatePurpose,
    check_calibration_signal_gate,
    min_confidence_tier,
)
from mip.evidence.registry import EvidenceRegistry, MissingEvidenceError
from mip.trust.assembly import build_trust_report_from_gates
from mip.trust.router import build_trust_report_for_artifact


class CalibrationTrace(ContractBaseModel):
    """Traceability record for one calibration signal in the registry."""

    calibration_id: str
    source_evidence_id: str
    target_model_id: str
    source_evidence_found: bool
    compatibility_status: CompatibilityStatus
    gate_decision: GateDecision
    max_confidence_tier: ConfidenceTier
    reason_codes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    trust_report: TrustReport

    @field_validator("calibration_id", "source_evidence_id", "target_model_id")
    @classmethod
    def ids_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "ID fields cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def missing_source_requires_reason(self) -> "CalibrationTrace":
        if not self.source_evidence_found and R.MISSING_EVIDENCE not in self.reason_codes:
            msg = "missing source evidence requires MISSING_EVIDENCE reason code"
            raise ValueError(msg)
        return self


class CalibrationAuditReport(ContractBaseModel):
    """Aggregate audit of calibration signal traceability in a registry."""

    audit_id: str
    created_at: datetime
    total_signals: int
    traceable_signals: int
    missing_source_evidence: int
    passed_signals: int
    warned_signals: int
    blocked_signals: int
    compatible_signals: int
    partially_compatible_signals: int
    unknown_compatibility_signals: int
    incompatible_signals: int
    overall_confidence_tier: ConfidenceTier
    traces: list[CalibrationTrace]

    @field_validator(
        "total_signals",
        "traceable_signals",
        "missing_source_evidence",
        "passed_signals",
        "warned_signals",
        "blocked_signals",
        "compatible_signals",
        "partially_compatible_signals",
        "unknown_compatibility_signals",
        "incompatible_signals",
    )
    @classmethod
    def counts_non_negative(cls, value: int) -> int:
        if value < 0:
            msg = "counts cannot be negative"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def counts_consistent(self) -> "CalibrationAuditReport":
        if self.total_signals != len(self.traces):
            msg = "total_signals must equal len(traces)"
            raise ValueError(msg)

        decision_total = self.passed_signals + self.warned_signals + self.blocked_signals
        if decision_total != self.total_signals:
            msg = "pass, warn, and block counts must sum to total_signals"
            raise ValueError(msg)

        compatibility_total = (
            self.compatible_signals
            + self.partially_compatible_signals
            + self.unknown_compatibility_signals
            + self.incompatible_signals
        )
        if compatibility_total != self.total_signals:
            msg = "compatibility counts must sum to total_signals"
            raise ValueError(msg)

        traceability_total = self.traceable_signals + self.missing_source_evidence
        if traceability_total != self.total_signals:
            msg = "traceable and missing source evidence counts must sum to total_signals"
            raise ValueError(msg)

        return self


def trace_calibration_signal(
    registry: EvidenceRegistry,
    calibration_id: str,
) -> CalibrationTrace:
    """Build a traceability record for one calibration signal."""
    signal = registry.get_calibration_signal(calibration_id)
    source_found = _source_evidence_exists(registry, signal)
    gate_outcome = check_calibration_signal_gate(signal)

    if source_found:
        trust_report = build_trust_report_for_artifact(signal)
        return CalibrationTrace(
            calibration_id=signal.calibration_id,
            source_evidence_id=signal.source_evidence_id,
            target_model_id=signal.target_model_id,
            source_evidence_found=True,
            compatibility_status=signal.compatibility_status,
            gate_decision=gate_outcome.decision,
            max_confidence_tier=gate_outcome.max_confidence_tier,
            reason_codes=list(gate_outcome.reason_codes),
            warnings=list(gate_outcome.warnings),
            trust_report=trust_report,
        )

    forced_outcome = _forced_missing_source_outcome(signal, gate_outcome)
    trust_report = build_trust_report_from_gates(
        trust_report_id=f"trust_report:calibration_signal:{signal.calibration_id}",
        output_id=signal.calibration_id,
        output_type="calibration_signal",
        gate_outcomes=[forced_outcome],
    )
    return CalibrationTrace(
        calibration_id=signal.calibration_id,
        source_evidence_id=signal.source_evidence_id,
        target_model_id=signal.target_model_id,
        source_evidence_found=False,
        compatibility_status=signal.compatibility_status,
        gate_decision=GateDecision.BLOCK,
        max_confidence_tier=ConfidenceTier.BLOCKED,
        reason_codes=list(forced_outcome.reason_codes),
        warnings=list(forced_outcome.warnings),
        trust_report=trust_report,
    )


def audit_calibration_registry(
    registry: EvidenceRegistry,
    *,
    audit_id: str = "calibration_audit",
    created_at: datetime | None = None,
) -> CalibrationAuditReport:
    """Audit all calibration signals in a registry for traceability and readiness."""
    signals = registry.list_calibration_signals()
    traces = [trace_calibration_signal(registry, signal.calibration_id) for signal in signals]
    timestamp = created_at or datetime.now(tz=UTC)
    return build_calibration_audit_report(traces, audit_id=audit_id, created_at=timestamp)


def build_calibration_audit_report(
    traces: list[CalibrationTrace],
    *,
    audit_id: str,
    created_at: datetime,
) -> CalibrationAuditReport:
    """Aggregate calibration traces into an audit report."""
    if not traces:
        return CalibrationAuditReport(
            audit_id=audit_id,
            created_at=created_at,
            total_signals=0,
            traceable_signals=0,
            missing_source_evidence=0,
            passed_signals=0,
            warned_signals=0,
            blocked_signals=0,
            compatible_signals=0,
            partially_compatible_signals=0,
            unknown_compatibility_signals=0,
            incompatible_signals=0,
            overall_confidence_tier=ConfidenceTier.BLOCKED,
            traces=[],
        )

    return CalibrationAuditReport(
        audit_id=audit_id,
        created_at=created_at,
        total_signals=len(traces),
        traceable_signals=sum(1 for trace in traces if trace.source_evidence_found),
        missing_source_evidence=sum(1 for trace in traces if not trace.source_evidence_found),
        passed_signals=sum(1 for trace in traces if trace.gate_decision == GateDecision.PASS),
        warned_signals=sum(1 for trace in traces if trace.gate_decision == GateDecision.WARN),
        blocked_signals=sum(1 for trace in traces if trace.gate_decision == GateDecision.BLOCK),
        compatible_signals=sum(
            1 for trace in traces if trace.compatibility_status == CompatibilityStatus.COMPATIBLE
        ),
        partially_compatible_signals=sum(
            1
            for trace in traces
            if trace.compatibility_status == CompatibilityStatus.PARTIALLY_COMPATIBLE
        ),
        unknown_compatibility_signals=sum(
            1 for trace in traces if trace.compatibility_status == CompatibilityStatus.UNKNOWN
        ),
        incompatible_signals=sum(
            1 for trace in traces if trace.compatibility_status == CompatibilityStatus.INCOMPATIBLE
        ),
        overall_confidence_tier=min_confidence_tier(
            *(trace.max_confidence_tier for trace in traces)
        ),
        traces=traces,
    )


def _source_evidence_exists(registry: EvidenceRegistry, signal: CalibrationSignal) -> bool:
    try:
        registry.get_evidence(signal.source_evidence_id)
    except MissingEvidenceError:
        return False
    return True


def _forced_missing_source_outcome(
    signal: CalibrationSignal,
    gate_outcome: GateOutcome,
) -> GateOutcome:
    return GateOutcome(
        artifact_id=signal.calibration_id,
        artifact_type="calibration_signal",
        purpose=GatePurpose.MODEL_CALIBRATION,
        decision=GateDecision.BLOCK,
        max_confidence_tier=ConfidenceTier.BLOCKED,
        reason_codes=_dedupe_stable([*gate_outcome.reason_codes, R.MISSING_EVIDENCE]),
        warnings=_dedupe_stable([*gate_outcome.warnings, R.MISSING_EVIDENCE]),
    )


def _dedupe_stable(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
