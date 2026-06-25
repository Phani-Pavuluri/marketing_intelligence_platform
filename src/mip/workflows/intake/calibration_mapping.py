"""Deterministic CalibrationSignal intake mapping helpers (P6 / I9)."""

from datetime import UTC, datetime

from mip.contracts.calibration import CalibrationSignal
from mip.contracts.calibration_intake import (
    CalibrationEvidenceInput,
    CalibrationIntakeBlockingReason,
    CalibrationIntakeStatus,
    CalibrationMappingReport,
    CalibrationMappingRequirement,
)
from mip.contracts.enums import CompatibilityStatus, ConfidenceTier
from mip.contracts.evidence import DiagnosticSummary

_BLOCKED_NEXT_DEFAULT = [
    "execute_mmm_calibration",
    "execute_model_refresh",
    "claim_causal_certification",
    "claim_decision_recommendation",
    "claim_budget_recommendation",
    "claim_roi_or_lift",
]

_ALLOWED_NEXT_MAPPED = [
    "register_calibration_signal",
    "run_calibration_audit",
    "reassess_with_trust_report",
]

_ALLOWED_NEXT_NEEDS_DATA = [
    "supply_missing_fields",
    "revalidate_evidence_input",
]


def _now() -> datetime:
    return datetime.now(tz=UTC)


def _slug(value: object) -> str:
    if hasattr(value, "value"):
        return str(value.value)
    return str(value)


def _source_evidence_id(evidence: CalibrationEvidenceInput) -> str:
    for candidate in (
        evidence.source_readout_id,
        evidence.source_artifact_id,
        evidence.source_experiment_id,
        evidence.input_id,
    ):
        if candidate and candidate.strip():
            return candidate
    return evidence.input_id


def _has_uncertainty(evidence: CalibrationEvidenceInput) -> bool:
    if evidence.standard_error is not None:
        return True
    return (
        evidence.confidence_interval_low is not None
        and evidence.confidence_interval_high is not None
    )


def _has_mappable_uncertainty(evidence: CalibrationEvidenceInput) -> bool:
    return evidence.standard_error is not None


def _is_stale(evidence: CalibrationEvidenceInput) -> bool:
    return _slug(evidence.freshness_status).lower() == "stale"


def _append_unique(target: list[str], value: str) -> None:
    if value not in target:
        target.append(value)


def _compare_field(
    *,
    evidence_value: str | None,
    required_value: str | None,
    field_name: str,
    missing_reason: CalibrationIntakeBlockingReason,
    incompatible_reason: CalibrationIntakeBlockingReason,
    missing_fields: list[str],
    incompatible_fields: list[str],
    blocking_reasons: list[str],
) -> bool:
    if required_value is None:
        return True
    if not evidence_value or not evidence_value.strip():
        _append_unique(missing_fields, field_name)
        _append_unique(blocking_reasons, incompatible_reason.value)
        return False
    if evidence_value.strip().lower() != required_value.strip().lower():
        _append_unique(incompatible_fields, field_name)
        _append_unique(blocking_reasons, incompatible_reason.value)
        return False
    return True


def _validate_alignment(
    evidence: CalibrationEvidenceInput,
    requirement: CalibrationMappingRequirement | None,
    *,
    missing_fields: list[str],
    incompatible_fields: list[str],
    blocking_reasons: list[str],
    warnings: list[str],
) -> CalibrationIntakeStatus:
    if requirement is None:
        return CalibrationIntakeStatus.READY_FOR_MAPPING

    aligned = True
    aligned &= _compare_field(
        evidence_value=evidence.metric_id,
        required_value=requirement.required_metric_id,
        field_name="metric_id",
        missing_reason=CalibrationIntakeBlockingReason.MISSING_METRIC_MAPPING,
        incompatible_reason=CalibrationIntakeBlockingReason.INCOMPATIBLE_METRIC,
        missing_fields=missing_fields,
        incompatible_fields=incompatible_fields,
        blocking_reasons=blocking_reasons,
    )
    aligned &= _compare_field(
        evidence_value=evidence.estimand_id,
        required_value=requirement.required_estimand_id,
        field_name="estimand_id",
        missing_reason=CalibrationIntakeBlockingReason.MISSING_ESTIMAND_MAPPING,
        incompatible_reason=CalibrationIntakeBlockingReason.INCOMPATIBLE_ESTIMAND,
        missing_fields=missing_fields,
        incompatible_fields=incompatible_fields,
        blocking_reasons=blocking_reasons,
    )
    aligned &= _compare_field(
        evidence_value=evidence.channel,
        required_value=requirement.required_channel,
        field_name="channel",
        missing_reason=CalibrationIntakeBlockingReason.MISSING_CHANNEL_MAPPING,
        incompatible_reason=CalibrationIntakeBlockingReason.INCOMPATIBLE_METRIC,
        missing_fields=missing_fields,
        incompatible_fields=incompatible_fields,
        blocking_reasons=blocking_reasons,
    )
    aligned &= _compare_field(
        evidence_value=evidence.platform,
        required_value=requirement.required_platform,
        field_name="platform",
        missing_reason=CalibrationIntakeBlockingReason.MISSING_CHANNEL_MAPPING,
        incompatible_reason=CalibrationIntakeBlockingReason.INCOMPATIBLE_METRIC,
        missing_fields=missing_fields,
        incompatible_fields=incompatible_fields,
        blocking_reasons=blocking_reasons,
    )
    aligned &= _compare_field(
        evidence_value=evidence.product_scope,
        required_value=requirement.required_product_scope,
        field_name="product_scope",
        missing_reason=CalibrationIntakeBlockingReason.MISSING_METRIC_MAPPING,
        incompatible_reason=CalibrationIntakeBlockingReason.INCOMPATIBLE_METRIC,
        missing_fields=missing_fields,
        incompatible_fields=incompatible_fields,
        blocking_reasons=blocking_reasons,
    )
    aligned &= _compare_field(
        evidence_value=evidence.geo_scope,
        required_value=requirement.required_geo_scope,
        field_name="geo_scope",
        missing_reason=CalibrationIntakeBlockingReason.MISSING_GEO_SCOPE,
        incompatible_reason=CalibrationIntakeBlockingReason.INCOMPATIBLE_METRIC,
        missing_fields=missing_fields,
        incompatible_fields=incompatible_fields,
        blocking_reasons=blocking_reasons,
    )
    aligned &= _compare_field(
        evidence_value=evidence.lift_scale,
        required_value=requirement.required_lift_scale,
        field_name="lift_scale",
        missing_reason=CalibrationIntakeBlockingReason.MISSING_UNCERTAINTY,
        incompatible_reason=CalibrationIntakeBlockingReason.INCOMPATIBLE_SCALE,
        missing_fields=missing_fields,
        incompatible_fields=incompatible_fields,
        blocking_reasons=blocking_reasons,
    )

    if requirement.required_time_window_start and evidence.time_window_start is None:
        _append_unique(missing_fields, "time_window_start")
        _append_unique(blocking_reasons, CalibrationIntakeBlockingReason.MISSING_TIME_WINDOW.value)
        aligned = False
    elif (
        requirement.required_time_window_start
        and evidence.time_window_start
        and evidence.time_window_start != requirement.required_time_window_start
    ):
        _append_unique(incompatible_fields, "time_window_start")
        _append_unique(blocking_reasons, CalibrationIntakeBlockingReason.INCOMPATIBLE_METRIC.value)
        aligned = False

    if requirement.required_time_window_end and evidence.time_window_end is None:
        _append_unique(missing_fields, "time_window_end")
        _append_unique(blocking_reasons, CalibrationIntakeBlockingReason.MISSING_TIME_WINDOW.value)
        aligned = False
    elif (
        requirement.required_time_window_end
        and evidence.time_window_end
        and evidence.time_window_end != requirement.required_time_window_end
    ):
        _append_unique(incompatible_fields, "time_window_end")
        _append_unique(blocking_reasons, CalibrationIntakeBlockingReason.INCOMPATIBLE_METRIC.value)
        aligned = False

    if requirement.require_causal_flag and not evidence.is_causal:
        _append_unique(blocking_reasons, CalibrationIntakeBlockingReason.NOT_CAUSAL_EVIDENCE.value)
        aligned = False

    if _is_stale(evidence) and not requirement.allow_stale_evidence:
        _append_unique(blocking_reasons, CalibrationIntakeBlockingReason.STALE_EVIDENCE.value)
        warnings.append("Evidence is stale; mapping blocked unless allow_stale_evidence is true.")
        aligned = False

    if requirement.require_trust_report and not evidence.source_trust_report_id:
        _append_unique(missing_fields, "source_trust_report_id")
        _append_unique(
            blocking_reasons,
            CalibrationIntakeBlockingReason.TRUST_REPORT_REQUIRED.value,
        )
        aligned = False

    if incompatible_fields:
        return CalibrationIntakeStatus.INCOMPATIBLE
    if not aligned:
        return CalibrationIntakeStatus.BLOCKED
    return CalibrationIntakeStatus.READY_FOR_MAPPING


def _validate_required_fields(
    evidence: CalibrationEvidenceInput,
    requirement: CalibrationMappingRequirement | None,
) -> tuple[
    CalibrationIntakeStatus,
    list[str],
    list[str],
    list[str],
    list[str],
]:
    missing_fields: list[str] = []
    incompatible_fields: list[str] = []
    blocking_reasons: list[str] = []
    warnings: list[str] = list(evidence.warnings)

    if evidence.effect_estimate is None:
        _append_unique(missing_fields, "effect_estimate")
        _append_unique(
            blocking_reasons,
            CalibrationIntakeBlockingReason.MISSING_EFFECT_ESTIMATE.value,
        )

    if not evidence.metric_id or not evidence.metric_id.strip():
        _append_unique(missing_fields, "metric_id")
        _append_unique(
            blocking_reasons,
            CalibrationIntakeBlockingReason.MISSING_METRIC_MAPPING.value,
        )

    if not evidence.estimand_id or not evidence.estimand_id.strip():
        _append_unique(missing_fields, "estimand_id")
        _append_unique(
            blocking_reasons,
            CalibrationIntakeBlockingReason.MISSING_ESTIMAND_MAPPING.value,
        )

    if evidence.time_window_start is None or evidence.time_window_end is None:
        if evidence.time_window_start is None:
            _append_unique(missing_fields, "time_window_start")
        if evidence.time_window_end is None:
            _append_unique(missing_fields, "time_window_end")
        _append_unique(
            blocking_reasons,
            CalibrationIntakeBlockingReason.MISSING_TIME_WINDOW.value,
        )

    if not _has_uncertainty(evidence):
        _append_unique(missing_fields, "standard_error")
        _append_unique(
            blocking_reasons,
            CalibrationIntakeBlockingReason.MISSING_UNCERTAINTY.value,
        )
    elif not _has_mappable_uncertainty(evidence):
        warnings.append(
            "Confidence interval present but standard_error missing; "
            "uncertainty is not auto-derived from CI."
        )
        _append_unique(missing_fields, "standard_error")
        _append_unique(
            blocking_reasons,
            CalibrationIntakeBlockingReason.MISSING_UNCERTAINTY.value,
        )

    if missing_fields and blocking_reasons:
        status = CalibrationIntakeStatus.NEEDS_MORE_DATA
    else:
        status = _validate_alignment(
            evidence,
            requirement,
            missing_fields=missing_fields,
            incompatible_fields=incompatible_fields,
            blocking_reasons=blocking_reasons,
            warnings=warnings,
        )

    return status, missing_fields, incompatible_fields, blocking_reasons, warnings


def build_calibration_mapping_report(
    evidence: CalibrationEvidenceInput,
    requirement: CalibrationMappingRequirement | None = None,
    *,
    report_id: str | None = None,
) -> CalibrationMappingReport:
    """Build a calibration mapping validation report."""
    status, missing_fields, incompatible_fields, blocking_reasons, warnings = (
        _validate_required_fields(evidence, requirement)
    )
    alignment_passed = status == CalibrationIntakeStatus.READY_FOR_MAPPING

    allowed_next = list(_ALLOWED_NEXT_NEEDS_DATA)
    if alignment_passed:
        allowed_next = ["map_to_calibration_signal", *_ALLOWED_NEXT_NEEDS_DATA]

    return CalibrationMappingReport(
        report_id=report_id or f"cal-map-{evidence.input_id}",
        input_id=evidence.input_id,
        requirement_id=requirement.requirement_id if requirement else None,
        status=status,
        alignment_passed=alignment_passed,
        missing_fields=missing_fields,
        incompatible_fields=incompatible_fields,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        allowed_next_steps=allowed_next,
        blocked_next_steps=list(_BLOCKED_NEXT_DEFAULT),
        created_at=_now(),
    )


def validate_calibration_evidence_input(
    evidence: CalibrationEvidenceInput,
    requirement: CalibrationMappingRequirement | None = None,
) -> CalibrationMappingReport:
    """Validate governed evidence for CalibrationSignal mapping readiness."""
    return build_calibration_mapping_report(evidence, requirement)


def _build_calibration_signal(
    evidence: CalibrationEvidenceInput,
    requirement: CalibrationMappingRequirement,
) -> CalibrationSignal:
    source_id = _source_evidence_id(evidence)
    channel_key = evidence.channel or "unknown_channel"
    geo_key = evidence.geo_scope or "unknown_geo"
    time_key = "analysis_window"
    if evidence.time_window_start and evidence.time_window_end:
        time_key = (
            f"{evidence.time_window_start.isoformat()}:{evidence.time_window_end.isoformat()}"
        )

    metrics: dict[str, float | int | str | bool] = {
        "effect_estimate": evidence.effect_estimate or 0.0,
        "metric_id": evidence.metric_id or "",
        "estimand_id": evidence.estimand_id or "",
        "evidence_type": evidence.evidence_type or "unknown",
        "is_causal": evidence.is_causal,
        "freshness_status": evidence.freshness_status,
    }
    if evidence.standard_error is not None:
        metrics["standard_error"] = evidence.standard_error
    if evidence.source_artifact_id:
        metrics["source_artifact_id"] = evidence.source_artifact_id
    if evidence.source_experiment_id:
        metrics["source_experiment_id"] = evidence.source_experiment_id
    if evidence.source_readout_id:
        metrics["source_readout_id"] = evidence.source_readout_id
    if evidence.source_trust_report_id:
        metrics["source_trust_report_id"] = evidence.source_trust_report_id

    diagnostics = DiagnosticSummary(
        passed=True,
        warnings=list(evidence.warnings),
        metrics=metrics,
    )

    freshness_decay = 0.7 if _is_stale(evidence) else 1.0

    return CalibrationSignal(
        calibration_id=f"cal-{evidence.input_id}",
        source_evidence_id=source_id,
        target_model_id=requirement.target_model_id,
        compatibility_status=CompatibilityStatus.COMPATIBLE,
        mapping_type="experiment_readout",
        lift_scale=evidence.lift_scale or requirement.required_lift_scale or "absolute",
        channel_mapping={channel_key: requirement.required_channel or channel_key},
        geography_mapping={geo_key: requirement.required_geo_scope or geo_key},
        time_mapping={time_key: time_key},
        weight=0.5,
        uncertainty=evidence.standard_error,
        freshness_decay=freshness_decay,
        allowed_usage=["mmm_calibration_candidate"],
        blocked_usage=[
            "decision_recommendation",
            "budget_optimization",
            "model_refresh_execution",
        ],
        diagnostics=diagnostics,
        confidence_tier=ConfidenceTier.DIAGNOSTIC_ONLY,
    )


def map_evidence_to_calibration_signal(
    evidence: CalibrationEvidenceInput,
    requirement: CalibrationMappingRequirement,
) -> tuple[CalibrationSignal | None, CalibrationMappingReport]:
    """Validate and map governed evidence into a CalibrationSignal contract."""
    report = validate_calibration_evidence_input(evidence, requirement)
    if report.status != CalibrationIntakeStatus.READY_FOR_MAPPING:
        return None, report

    signal = _build_calibration_signal(evidence, requirement)
    mapped_report = report.model_copy(
        update={
            "status": CalibrationIntakeStatus.MAPPED,
            "mapped_signal_id": signal.calibration_id,
            "mapped_signal": signal,
            "alignment_passed": True,
            "allowed_next_steps": list(_ALLOWED_NEXT_MAPPED),
            "warnings": [
                *report.warnings,
                "Mapped structurally only; MMM calibration execution remains deferred.",
            ],
        }
    )
    return signal, mapped_report
