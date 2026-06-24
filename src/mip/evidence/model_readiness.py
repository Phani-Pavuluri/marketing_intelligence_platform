"""Model-scoped calibration readiness evaluation."""

from collections.abc import Iterable
from datetime import UTC, datetime

from pydantic import Field, field_validator, model_validator

from mip.contracts import ConfidenceTier, ContractBaseModel
from mip.evaluation import reasons as R
from mip.evaluation.gates import min_confidence_tier
from mip.evidence.calibration_audit import (
    CalibrationAuditReport,
    CalibrationTrace,
    build_calibration_audit_report,
    trace_calibration_signal,
)
from mip.evidence.registry import EvidenceRegistry


class ModelCalibrationReadiness(ContractBaseModel):
    """Calibration readiness summary for a target MMM model."""

    target_model_id: str
    audit_id: str
    created_at: datetime
    readiness_tier: ConfidenceTier
    is_calibration_ready: bool
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
    reason_codes: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    audit_report: CalibrationAuditReport

    @field_validator("target_model_id")
    @classmethod
    def target_model_id_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "target_model_id cannot be empty"
            raise ValueError(msg)
        return value

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
    def readiness_invariants(self) -> "ModelCalibrationReadiness":
        report = self.audit_report
        if self.total_signals != report.total_signals:
            msg = "total_signals must match audit_report"
            raise ValueError(msg)
        if self.traceable_signals != report.traceable_signals:
            msg = "traceable_signals must match audit_report"
            raise ValueError(msg)
        if self.missing_source_evidence != report.missing_source_evidence:
            msg = "missing_source_evidence must match audit_report"
            raise ValueError(msg)
        if self.passed_signals != report.passed_signals:
            msg = "passed_signals must match audit_report"
            raise ValueError(msg)
        if self.warned_signals != report.warned_signals:
            msg = "warned_signals must match audit_report"
            raise ValueError(msg)
        if self.blocked_signals != report.blocked_signals:
            msg = "blocked_signals must match audit_report"
            raise ValueError(msg)
        if self.compatible_signals != report.compatible_signals:
            msg = "compatible_signals must match audit_report"
            raise ValueError(msg)
        if self.partially_compatible_signals != report.partially_compatible_signals:
            msg = "partially_compatible_signals must match audit_report"
            raise ValueError(msg)
        if self.unknown_compatibility_signals != report.unknown_compatibility_signals:
            msg = "unknown_compatibility_signals must match audit_report"
            raise ValueError(msg)
        if self.incompatible_signals != report.incompatible_signals:
            msg = "incompatible_signals must match audit_report"
            raise ValueError(msg)

        if self.is_calibration_ready and self.readiness_tier != ConfidenceTier.DECISION_READY:
            msg = "is_calibration_ready requires decision_ready readiness_tier"
            raise ValueError(msg)

        if self.readiness_tier == ConfidenceTier.BLOCKED:
            if not self.reason_codes and not self.warnings:
                msg = "blocked readiness requires reason_codes or warnings"
                raise ValueError(msg)

        return self


def audit_calibration_for_model(
    registry: EvidenceRegistry,
    target_model_id: str,
    *,
    audit_id: str | None = None,
    created_at: datetime | None = None,
) -> CalibrationAuditReport:
    """Audit calibration signals scoped to one target model."""
    model_signals = [
        signal
        for signal in registry.list_calibration_signals()
        if signal.target_model_id == target_model_id
    ]
    traces = [
        trace_calibration_signal(registry, signal.calibration_id) for signal in model_signals
    ]
    timestamp = created_at or datetime.now(tz=UTC)
    resolved_audit_id = audit_id or f"calibration_audit:{target_model_id}"
    return build_calibration_audit_report(
        traces,
        audit_id=resolved_audit_id,
        created_at=timestamp,
    )


def evaluate_model_calibration_readiness(
    registry: EvidenceRegistry,
    target_model_id: str,
    *,
    audit_id: str | None = None,
    created_at: datetime | None = None,
) -> ModelCalibrationReadiness:
    """Evaluate whether a model has calibration-ready evidence."""
    if not target_model_id.strip():
        msg = "target_model_id cannot be empty"
        raise ValueError(msg)

    report = audit_calibration_for_model(
        registry,
        target_model_id,
        audit_id=audit_id,
        created_at=created_at,
    )
    trace_reasons = collect_calibration_trace_reasons(report.traces)
    trace_warnings = collect_calibration_trace_warnings(report.traces)

    readiness_tier: ConfidenceTier
    is_ready: bool
    readiness_reasons: list[str] = []

    if report.total_signals == 0:
        readiness_tier = ConfidenceTier.BLOCKED
        is_ready = False
        readiness_reasons.append(R.NO_CALIBRATION_SIGNALS)
    elif report.compatible_signals == 0:
        readiness_tier = ConfidenceTier.BLOCKED
        is_ready = False
        readiness_reasons.append(R.NO_COMPATIBLE_CALIBRATION_SIGNALS)
    elif report.blocked_signals > 0:
        readiness_tier = ConfidenceTier.BLOCKED
        is_ready = False
        readiness_reasons.append(R.BLOCKED_CALIBRATION_SIGNAL)
    elif (
        report.passed_signals == report.total_signals
        and report.compatible_signals > 0
        and report.missing_source_evidence == 0
        and report.overall_confidence_tier == ConfidenceTier.DECISION_READY
    ):
        readiness_tier = ConfidenceTier.DECISION_READY
        is_ready = True
    elif report.warned_signals > 0 and report.compatible_signals > 0:
        readiness_tier = min_confidence_tier(
            report.overall_confidence_tier,
            ConfidenceTier.DIRECTIONAL,
        )
        is_ready = False
        readiness_reasons.append(R.CALIBRATION_WARNINGS_PRESENT)
    else:
        readiness_tier = report.overall_confidence_tier
        is_ready = False

    reason_codes = _dedupe_stable([*trace_reasons, *readiness_reasons])
    warnings = _dedupe_stable(trace_warnings)

    return ModelCalibrationReadiness(
        target_model_id=target_model_id,
        audit_id=report.audit_id,
        created_at=report.created_at,
        readiness_tier=readiness_tier,
        is_calibration_ready=is_ready,
        total_signals=report.total_signals,
        traceable_signals=report.traceable_signals,
        missing_source_evidence=report.missing_source_evidence,
        passed_signals=report.passed_signals,
        warned_signals=report.warned_signals,
        blocked_signals=report.blocked_signals,
        compatible_signals=report.compatible_signals,
        partially_compatible_signals=report.partially_compatible_signals,
        unknown_compatibility_signals=report.unknown_compatibility_signals,
        incompatible_signals=report.incompatible_signals,
        reason_codes=reason_codes,
        warnings=warnings,
        audit_report=report,
    )


def collect_calibration_trace_reasons(traces: list[CalibrationTrace]) -> list[str]:
    """Collect de-duplicated reason codes from calibration traces."""
    return _dedupe_stable(code for trace in traces for code in trace.reason_codes)


def collect_calibration_trace_warnings(traces: list[CalibrationTrace]) -> list[str]:
    """Collect de-duplicated warnings from calibration traces."""
    return _dedupe_stable(warning for trace in traces for warning in trace.warnings)


def _dedupe_stable(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
