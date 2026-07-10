"""Planning/MMM calibration-signal mapping and readiness workflow.

Maps tabular intake metadata into calibration readiness assessments without
calibration math, model fitting, or governance artifact execution.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, date, datetime

from mip.contracts.planning_mmm_calibration_signal_mapping_readiness import (
    _CAUSAL_EVIDENCE_SOURCES,
    DEFAULT_MAX_SIGNAL_AGE_DAYS,
    PlanningMMMCalibrationSignalMappedRecord,
    PlanningMMMCalibrationSignalMappingIssueCode,
    PlanningMMMCalibrationSignalMappingReadinessRequest,
    PlanningMMMCalibrationSignalMappingReadinessResult,
    PlanningMMMCalibrationSignalMappingStatus,
    PlanningMMMCalibrationSignalMappingTarget,
    PlanningMMMCalibrationSignalReadinessAssessment,
    PlanningMMMCalibrationSignalReadinessStatus,
    PlanningMMMCalibrationSignalRecordMetadata,
    PlanningMMMCalibrationSignalUsability,
)
from mip.contracts.planning_mmm_calibration_signal_tabular_intake import (
    PlanningMMMCalibrationSignalColumnRole,
    PlanningMMMCalibrationSignalTabularIntakeStatus,
    PlanningMMMCalibrationSignalTabularSource,
)

_READY_INTAKE_STATUSES = {
    PlanningMMMCalibrationSignalTabularIntakeStatus.INTAKE_READY,
    PlanningMMMCalibrationSignalTabularIntakeStatus.INTAKE_READY_WITH_WARNINGS,
    PlanningMMMCalibrationSignalTabularIntakeStatus.DIAGNOSTIC_ONLY,
}

_BOUNDARY_ISSUES = (
    PlanningMMMCalibrationSignalMappingIssueCode.LINEAGE_PRESERVED,
    PlanningMMMCalibrationSignalMappingIssueCode.NO_MODEL_EXECUTION,
    PlanningMMMCalibrationSignalMappingIssueCode.NO_PRIOR_APPLICATION,
    PlanningMMMCalibrationSignalMappingIssueCode.NO_LIKELIHOOD_CONSTRUCTION,
    PlanningMMMCalibrationSignalMappingIssueCode.NO_POSTERIOR_CALCULATION,
    PlanningMMMCalibrationSignalMappingIssueCode.NO_OPTIMIZER_EXECUTION,
    PlanningMMMCalibrationSignalMappingIssueCode.NO_SIMULATOR_EXECUTION,
    PlanningMMMCalibrationSignalMappingIssueCode.NO_RECOMMENDATION_GENERATED,
    PlanningMMMCalibrationSignalMappingIssueCode.NO_DECISION_SURFACE_EXECUTION,
    PlanningMMMCalibrationSignalMappingIssueCode.NO_CLAIM_AUTHORIZATION,
)


def evaluate_planning_mmm_calibration_signal_mapping_readiness(
    request: PlanningMMMCalibrationSignalMappingReadinessRequest,
) -> PlanningMMMCalibrationSignalMappingReadinessResult:
    """Evaluate calibration-signal mapping and readiness for Planning/MMM."""
    lineage = {
        **request.lineage,
        "mapping_stage": "planning_mmm_calibration_signal_mapping_readiness",
        "target_model_id": request.target.target_model_id,
    }
    warnings: list[str] = []
    issues: list[PlanningMMMCalibrationSignalMappingIssueCode] = list(_BOUNDARY_ISSUES)

    if request.existing_model_availability_result is not None:
        lineage["existing_model_availability_request_id"] = (
            request.existing_model_availability_result.request_id
        )
        lineage["existing_model_availability_status"] = str(
            request.existing_model_availability_result.status
        )
        if request.existing_model_availability_result.selected_model is not None:
            lineage["existing_model_availability_selected_model_id"] = (
                request.existing_model_availability_result.selected_model.model_id
            )

    if request.intake_result is None:
        return _blocked_result(
            request_id=request.request_id,
            mapping_status=PlanningMMMCalibrationSignalMappingStatus.BLOCKED_MISSING_INTAKE,
            readiness_status=PlanningMMMCalibrationSignalReadinessStatus.BLOCKED,
            blocked_reasons=["calibration signal tabular intake result is missing"],
            issues=issues + [PlanningMMMCalibrationSignalMappingIssueCode.INTAKE_MISSING],
            warnings=warnings,
            lineage=lineage,
        )

    intake = request.intake_result
    warnings.extend(intake.warnings)
    lineage.update(intake.lineage)

    if intake.status not in _READY_INTAKE_STATUSES:
        return _blocked_result(
            request_id=request.request_id,
            mapping_status=PlanningMMMCalibrationSignalMappingStatus.BLOCKED_INTAKE_NOT_READY,
            readiness_status=PlanningMMMCalibrationSignalReadinessStatus.BLOCKED,
            blocked_reasons=[f"intake status not ready: {intake.status}"],
            issues=issues + [PlanningMMMCalibrationSignalMappingIssueCode.INTAKE_NOT_READY],
            warnings=warnings,
            lineage=lineage,
            intake_issues=intake.issues,
        )

    envelope = intake.envelope
    if envelope is None:
        return _blocked_result(
            request_id=request.request_id,
            mapping_status=PlanningMMMCalibrationSignalMappingStatus.BLOCKED_MISSING_INTAKE,
            readiness_status=PlanningMMMCalibrationSignalReadinessStatus.BLOCKED,
            blocked_reasons=["intake envelope missing"],
            issues=issues + [PlanningMMMCalibrationSignalMappingIssueCode.INTAKE_MISSING],
            warnings=warnings,
            lineage=lineage,
        )

    lineage.update(envelope.lineage)
    warnings.extend(envelope.warnings)
    issues.append(PlanningMMMCalibrationSignalMappingIssueCode.CALIBRATION_SIGNAL_METADATA_COMPATIBLE)

    record_metadata = _resolve_signal_records(request)
    if not record_metadata:
        return _blocked_result(
            request_id=request.request_id,
            mapping_status=PlanningMMMCalibrationSignalMappingStatus.BLOCKED_MISSING_REQUIRED_FIELDS,
            readiness_status=PlanningMMMCalibrationSignalReadinessStatus.BLOCKED,
            blocked_reasons=["no calibration signal record metadata available for mapping"],
            issues=issues + [PlanningMMMCalibrationSignalMappingIssueCode.REQUIRED_FIELD_MISSING],
            warnings=warnings,
            lineage=lineage,
        )

    sources_by_id = {source.source_id: source for source in envelope.calibration_signal_sources}
    mapped_records: list[PlanningMMMCalibrationSignalMappedRecord] = []
    for record_meta in record_metadata:
        source = sources_by_id.get(record_meta.source_id)
        mapped = _map_record(
            record_meta,
            source=source,
            target=request.target,
            reference_date=_reference_date(request.target),
        )
        mapped_records.append(mapped)
        issues.extend(mapped.issues)

    if any(
        issue == PlanningMMMCalibrationSignalMappingIssueCode.REQUIRED_FIELD_MISSING
        for record in mapped_records
        for issue in record.issues
    ):
        return _blocked_result(
            request_id=request.request_id,
            mapping_status=PlanningMMMCalibrationSignalMappingStatus.BLOCKED_MISSING_REQUIRED_FIELDS,
            readiness_status=PlanningMMMCalibrationSignalReadinessStatus.BLOCKED,
            blocked_reasons=["required mapping fields unavailable for one or more signals"],
            mapped_records=mapped_records,
            issues=issues,
            warnings=warnings,
            lineage=lineage,
        )

    assessment = _build_assessment(mapped_records, target=request.target, issues=issues)
    mapping_status, readiness_status, blocked_reasons = _resolve_statuses(
        mapped_records,
        assessment=assessment,
        intake_status=intake.status,
        target=request.target,
    )
    warnings.extend(assessment.warnings)

    mcr_reference_id, mcr_deferred, mcr_reason = _model_calibration_readiness_reference(
        request.target,
        assessment=assessment,
    )
    assessment.model_calibration_readiness_reference_id = mcr_reference_id
    assessment.model_calibration_readiness_deferred = mcr_deferred
    assessment.model_calibration_readiness_deferred_reason = mcr_reason
    if mcr_reference_id:
        issues.append(
            PlanningMMMCalibrationSignalMappingIssueCode.MODEL_CALIBRATION_READINESS_REFERENCE_CREATED
        )
    elif mcr_deferred:
        issues.append(PlanningMMMCalibrationSignalMappingIssueCode.MAPPING_DEFERRED)

    if envelope.data_source_refs:
        issues.append(PlanningMMMCalibrationSignalMappingIssueCode.DATA_SOURCE_REF_PRESERVED)
    if envelope.tabular_source_references:
        issues.append(PlanningMMMCalibrationSignalMappingIssueCode.TABULAR_SOURCE_REF_PRESERVED)

    return PlanningMMMCalibrationSignalMappingReadinessResult(
        request_id=request.request_id,
        mapping_status=mapping_status,
        readiness_status=readiness_status,
        assessment=assessment,
        mapped_records=mapped_records,
        blocked_reasons=blocked_reasons,
        warnings=list(dict.fromkeys(warnings)),
        issues=_dedupe_issues(issues),
        lineage=lineage,
        execution_allowed=_default_execution_allowed(),
    )


def summarize_planning_mmm_calibration_signal_mapping_readiness(
    result: PlanningMMMCalibrationSignalMappingReadinessResult,
) -> dict[str, str | int | list[str]]:
    """Return metadata-only summary of mapping/readiness evaluation."""
    assessment = result.assessment
    return {
        "request_id": result.request_id,
        "mapping_status": _enum_value(result.mapping_status),
        "readiness_status": _enum_value(result.readiness_status),
        "usable_count": len(assessment.usable_signal_ids),
        "diagnostic_only_count": len(assessment.diagnostic_only_signal_ids),
        "stale_count": len(assessment.stale_signal_ids),
        "blocked_count": len(assessment.blocked_signal_ids),
        "deferred_count": len(assessment.deferred_signal_ids),
        "warnings": list(result.warnings),
        "blocked_reasons": list(result.blocked_reasons),
    }


def _resolve_signal_records(
    request: PlanningMMMCalibrationSignalMappingReadinessRequest,
) -> list[PlanningMMMCalibrationSignalRecordMetadata]:
    if request.signal_records:
        return list(request.signal_records)

    intake = request.intake_result
    if intake is None or intake.envelope is None:
        return []

    records: list[PlanningMMMCalibrationSignalRecordMetadata] = []
    for source in intake.envelope.calibration_signal_sources:
        effect_field = _column_name_for_role(
            source, PlanningMMMCalibrationSignalColumnRole.LIFT
        )
        uncertainty_field = _column_name_for_role(
            source, PlanningMMMCalibrationSignalColumnRole.STANDARD_ERROR
        )
        records.append(
            PlanningMMMCalibrationSignalRecordMetadata(
                record_id=f"record:{source.source_id}",
                source_id=source.source_id,
                effect_field_name=effect_field,
                uncertainty_field_name=uncertainty_field,
            )
        )
    return records


def _map_record(
    record_meta: PlanningMMMCalibrationSignalRecordMetadata,
    *,
    source: PlanningMMMCalibrationSignalTabularSource | None,
    target: PlanningMMMCalibrationSignalMappingTarget,
    reference_date: date,
) -> PlanningMMMCalibrationSignalMappedRecord:
    warnings: list[str] = []
    issues: list[PlanningMMMCalibrationSignalMappingIssueCode] = []
    lineage: dict[str, str] = {}

    effect_field = record_meta.effect_field_name
    uncertainty_field = record_meta.uncertainty_field_name
    if source is not None:
        lineage.update(source.lineage)
        if effect_field is None:
            effect_field = _column_name_for_role(
                source, PlanningMMMCalibrationSignalColumnRole.LIFT
            )
        if uncertainty_field is None and target.require_uncertainty:
            uncertainty_field = _column_name_for_role(
                source, PlanningMMMCalibrationSignalColumnRole.STANDARD_ERROR
            )
        issues.append(PlanningMMMCalibrationSignalMappingIssueCode.TABULAR_SOURCE_REF_PRESERVED)
        if source.data_source_ref is not None:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.DATA_SOURCE_REF_PRESERVED)

    usability = PlanningMMMCalibrationSignalUsability.DEFERRED
    calibration_signal_id: str | None = None
    construction_deferred = True

    if target.require_uncertainty and not uncertainty_field:
        issues.append(PlanningMMMCalibrationSignalMappingIssueCode.UNCERTAINTY_MISSING)
        usability = PlanningMMMCalibrationSignalUsability.BLOCKED
    elif uncertainty_field:
        issues.append(PlanningMMMCalibrationSignalMappingIssueCode.UNCERTAINTY_PRESENT)
    else:
        warnings.append("uncertainty field missing; require_uncertainty is false")
        issues.append(PlanningMMMCalibrationSignalMappingIssueCode.UNCERTAINTY_MISSING)

    if not record_meta.metric or not record_meta.channel or not record_meta.estimand:
        issues.append(PlanningMMMCalibrationSignalMappingIssueCode.REQUIRED_FIELD_MISSING)
        if usability != PlanningMMMCalibrationSignalUsability.BLOCKED:
            usability = PlanningMMMCalibrationSignalUsability.DEFERRED
    else:
        metric_ok = _metric_aligned(record_meta.metric, target.metric)
        channel_ok = _channel_aligned(record_meta.channel, target.channels)
        estimand_ok = _estimand_aligned(record_meta.estimand, target.estimand)
        time_ok, time_warning = _time_window_aligned(
            record_meta.start_date,
            record_meta.end_date,
            target.planning_start_date,
            target.planning_end_date,
        )
        if time_warning:
            warnings.append(time_warning)

        fresh_ok, fresh_warning = _freshness_valid(
            record_meta.freshness_date,
            record_meta.end_date,
            reference_date=reference_date,
            max_age_days=target.max_signal_age_days,
        )
        if fresh_warning:
            warnings.append(fresh_warning)

        causal = _is_causal_evidence(record_meta.evidence_source)

        if metric_ok:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.METRIC_ALIGNED)
        else:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.METRIC_MISMATCH)
            usability = PlanningMMMCalibrationSignalUsability.BLOCKED

        if channel_ok:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.CHANNEL_ALIGNED)
        else:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.CHANNEL_MISMATCH)
            usability = PlanningMMMCalibrationSignalUsability.BLOCKED

        if estimand_ok:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.ESTIMAND_ALIGNED)
        elif target.allow_diagnostic_only:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.ESTIMAND_MISMATCH)
            if usability not in {
                PlanningMMMCalibrationSignalUsability.BLOCKED,
            }:
                usability = PlanningMMMCalibrationSignalUsability.DIAGNOSTIC_ONLY
                issues.append(PlanningMMMCalibrationSignalMappingIssueCode.DIAGNOSTIC_ONLY_SIGNAL)
        else:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.ESTIMAND_MISMATCH)
            usability = PlanningMMMCalibrationSignalUsability.BLOCKED

        if time_ok:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.TIME_WINDOW_ALIGNED)
        elif target.allow_diagnostic_only:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.TIME_WINDOW_MISMATCH)
            if usability not in {
                PlanningMMMCalibrationSignalUsability.BLOCKED,
            }:
                usability = PlanningMMMCalibrationSignalUsability.DIAGNOSTIC_ONLY
                issues.append(PlanningMMMCalibrationSignalMappingIssueCode.DIAGNOSTIC_ONLY_SIGNAL)
        else:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.TIME_WINDOW_MISMATCH)
            usability = PlanningMMMCalibrationSignalUsability.BLOCKED

        if fresh_ok:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.FRESHNESS_VALID)
        else:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.FRESHNESS_STALE)
            if usability in {
                PlanningMMMCalibrationSignalUsability.DEFERRED,
                PlanningMMMCalibrationSignalUsability.USABLE_FOR_CALIBRATION,
                PlanningMMMCalibrationSignalUsability.USABLE_WITH_WARNINGS,
            }:
                usability = PlanningMMMCalibrationSignalUsability.STALE

        if causal:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.CAUSAL_SIGNAL)
        else:
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.DIAGNOSTIC_ONLY_SIGNAL)
            if usability not in {
                PlanningMMMCalibrationSignalUsability.BLOCKED,
                PlanningMMMCalibrationSignalUsability.STALE,
            }:
                usability = PlanningMMMCalibrationSignalUsability.DIAGNOSTIC_ONLY

        if usability not in {
            PlanningMMMCalibrationSignalUsability.BLOCKED,
            PlanningMMMCalibrationSignalUsability.DIAGNOSTIC_ONLY,
            PlanningMMMCalibrationSignalUsability.STALE,
        }:
            if metric_ok and channel_ok and estimand_ok and time_ok and fresh_ok and causal:
                usability = (
                    PlanningMMMCalibrationSignalUsability.USABLE_WITH_WARNINGS
                    if warnings
                    else PlanningMMMCalibrationSignalUsability.USABLE_FOR_CALIBRATION
                )
            elif metric_ok and channel_ok and estimand_ok and time_ok and causal:
                usability = PlanningMMMCalibrationSignalUsability.USABLE_WITH_WARNINGS
            elif metric_ok and channel_ok and estimand_ok and time_ok and fresh_ok:
                usability = PlanningMMMCalibrationSignalUsability.USABLE_WITH_WARNINGS

        if (
            usability
            in {
                PlanningMMMCalibrationSignalUsability.USABLE_FOR_CALIBRATION,
                PlanningMMMCalibrationSignalUsability.USABLE_WITH_WARNINGS,
            }
            and construction_deferred
        ):
            issues.append(PlanningMMMCalibrationSignalMappingIssueCode.MAPPING_DEFERRED)

    return PlanningMMMCalibrationSignalMappedRecord(
        record_id=record_meta.record_id,
        source_id=record_meta.source_id,
        intake_record_id=record_meta.record_id,
        metric=record_meta.metric,
        channel=record_meta.channel,
        estimand=record_meta.estimand,
        effect_field_name=effect_field,
        uncertainty_field_name=uncertainty_field,
        start_date=record_meta.start_date,
        end_date=record_meta.end_date,
        freshness_date=record_meta.freshness_date,
        evidence_source=record_meta.evidence_source,
        geo_scope=record_meta.geo_scope,
        usability=usability,
        calibration_signal_id=calibration_signal_id,
        calibration_signal_construction_deferred=construction_deferred,
        data_source_ref=source.data_source_ref if source is not None else None,
        tabular_source_reference=source.tabular_source_reference if source is not None else None,
        lineage=lineage,
        warnings=warnings,
        issues=_dedupe_issues(issues),
    )


def _build_assessment(
    mapped_records: list[PlanningMMMCalibrationSignalMappedRecord],
    *,
    target: PlanningMMMCalibrationSignalMappingTarget,
    issues: list[PlanningMMMCalibrationSignalMappingIssueCode],
) -> PlanningMMMCalibrationSignalReadinessAssessment:
    usable: list[str] = []
    diagnostic: list[str] = []
    blocked: list[str] = []
    stale: list[str] = []
    deferred: list[str] = []
    warnings: list[str] = []

    for record in mapped_records:
        record_id = record.record_id
        if record.usability == PlanningMMMCalibrationSignalUsability.USABLE_FOR_CALIBRATION:
            usable.append(record_id)
        elif record.usability == PlanningMMMCalibrationSignalUsability.USABLE_WITH_WARNINGS:
            usable.append(record_id)
            warnings.extend(record.warnings)
        elif record.usability == PlanningMMMCalibrationSignalUsability.DIAGNOSTIC_ONLY:
            diagnostic.append(record_id)
        elif record.usability == PlanningMMMCalibrationSignalUsability.STALE:
            stale.append(record_id)
        elif record.usability == PlanningMMMCalibrationSignalUsability.BLOCKED:
            blocked.append(record_id)
        else:
            deferred.append(record_id)

    readiness = PlanningMMMCalibrationSignalReadinessStatus.DEFERRED
    if usable and not blocked:
        if stale:
            readiness = PlanningMMMCalibrationSignalReadinessStatus.STALE_REQUIRES_REVIEW
        elif warnings:
            readiness = PlanningMMMCalibrationSignalReadinessStatus.READY_WITH_WARNINGS
        else:
            readiness = PlanningMMMCalibrationSignalReadinessStatus.READY_FOR_MODEL_CALIBRATION
    elif usable and (stale or warnings):
        readiness = PlanningMMMCalibrationSignalReadinessStatus.READY_WITH_WARNINGS
    elif stale and not usable and not blocked:
        readiness = PlanningMMMCalibrationSignalReadinessStatus.STALE_REQUIRES_REVIEW
    elif diagnostic and not usable and not blocked:
        readiness = PlanningMMMCalibrationSignalReadinessStatus.DIAGNOSTIC_ONLY
    elif blocked and not usable and not diagnostic:
        readiness = PlanningMMMCalibrationSignalReadinessStatus.BLOCKED
    elif deferred and not usable and not diagnostic and not blocked:
        readiness = PlanningMMMCalibrationSignalReadinessStatus.DEFERRED

    return PlanningMMMCalibrationSignalReadinessAssessment(
        mapped_records=mapped_records,
        usable_signal_ids=usable,
        diagnostic_only_signal_ids=diagnostic,
        blocked_signal_ids=blocked,
        stale_signal_ids=stale,
        deferred_signal_ids=deferred,
        readiness_status=readiness,
        warnings=list(dict.fromkeys(warnings)),
        issues=_dedupe_issues(issues),
    )


def _resolve_statuses(
    mapped_records: list[PlanningMMMCalibrationSignalMappedRecord],
    *,
    assessment: PlanningMMMCalibrationSignalReadinessAssessment,
    intake_status: PlanningMMMCalibrationSignalTabularIntakeStatus,
    target: PlanningMMMCalibrationSignalMappingTarget,
) -> tuple[
    PlanningMMMCalibrationSignalMappingStatus,
    PlanningMMMCalibrationSignalReadinessStatus,
    list[str],
]:
    blocked_reasons: list[str] = []
    readiness = assessment.readiness_status

    if readiness == PlanningMMMCalibrationSignalReadinessStatus.READY_FOR_MODEL_CALIBRATION:
        mapping = PlanningMMMCalibrationSignalMappingStatus.MAPPING_READY
    elif readiness == PlanningMMMCalibrationSignalReadinessStatus.READY_WITH_WARNINGS:
        mapping = PlanningMMMCalibrationSignalMappingStatus.MAPPING_READY_WITH_WARNINGS
    elif readiness == PlanningMMMCalibrationSignalReadinessStatus.STALE_REQUIRES_REVIEW:
        mapping = PlanningMMMCalibrationSignalMappingStatus.MAPPING_READY_WITH_WARNINGS
        blocked_reasons.append("one or more calibration signals are stale and require review")
    elif readiness == PlanningMMMCalibrationSignalReadinessStatus.DIAGNOSTIC_ONLY:
        mapping = PlanningMMMCalibrationSignalMappingStatus.DIAGNOSTIC_ONLY
        blocked_reasons.append("only diagnostic calibration signals available")
    elif readiness == PlanningMMMCalibrationSignalReadinessStatus.DEFERRED:
        mapping = PlanningMMMCalibrationSignalMappingStatus.MAPPING_DEFERRED
        blocked_reasons.append("calibration signal mapping deferred pending additional context")
    else:
        mapping = _blocked_mapping_status(mapped_records, target=target)
        blocked_reasons.append("no usable calibration signals for model calibration")

    if intake_status == PlanningMMMCalibrationSignalTabularIntakeStatus.DIAGNOSTIC_ONLY:
        mapping = PlanningMMMCalibrationSignalMappingStatus.DIAGNOSTIC_ONLY
        readiness = PlanningMMMCalibrationSignalReadinessStatus.DIAGNOSTIC_ONLY

    return mapping, readiness, blocked_reasons


def _blocked_mapping_status(
    mapped_records: list[PlanningMMMCalibrationSignalMappedRecord],
    *,
    target: PlanningMMMCalibrationSignalMappingTarget,
) -> PlanningMMMCalibrationSignalMappingStatus:
    for record in mapped_records:
        if PlanningMMMCalibrationSignalMappingIssueCode.METRIC_MISMATCH in record.issues:
            return PlanningMMMCalibrationSignalMappingStatus.BLOCKED_INCOMPATIBLE_METRIC
        if PlanningMMMCalibrationSignalMappingIssueCode.CHANNEL_MISMATCH in record.issues:
            return PlanningMMMCalibrationSignalMappingStatus.BLOCKED_INCOMPATIBLE_CHANNEL
        if PlanningMMMCalibrationSignalMappingIssueCode.ESTIMAND_MISMATCH in record.issues:
            return PlanningMMMCalibrationSignalMappingStatus.BLOCKED_INCOMPATIBLE_ESTIMAND
        if PlanningMMMCalibrationSignalMappingIssueCode.TIME_WINDOW_MISMATCH in record.issues:
            return PlanningMMMCalibrationSignalMappingStatus.BLOCKED_INCOMPATIBLE_TIME_WINDOW
    if target.require_uncertainty and any(
        PlanningMMMCalibrationSignalMappingIssueCode.UNCERTAINTY_MISSING in record.issues
        for record in mapped_records
    ):
        return PlanningMMMCalibrationSignalMappingStatus.BLOCKED_MISSING_REQUIRED_FIELDS
    return PlanningMMMCalibrationSignalMappingStatus.BLOCKED_MISSING_REQUIRED_FIELDS


def _model_calibration_readiness_reference(
    target: PlanningMMMCalibrationSignalMappingTarget,
    *,
    assessment: PlanningMMMCalibrationSignalReadinessAssessment,
) -> tuple[str | None, bool, str]:
    if not assessment.usable_signal_ids and not assessment.diagnostic_only_signal_ids:
        return (
            None,
            True,
            "ModelCalibrationReadiness deferred: no usable or diagnostic signals to audit",
        )
    if assessment.readiness_status == PlanningMMMCalibrationSignalReadinessStatus.DEFERRED:
        return (
            None,
            True,
            "ModelCalibrationReadiness deferred: full CalibrationSignal construction unavailable",
        )
    reference_id = (
        f"mcr-metadata:{target.target_model_id}:{datetime.now(tz=UTC).date().isoformat()}"
    )
    return (
        reference_id,
        True,
        "ModelCalibrationReadiness metadata reference only; registry audit deferred",
    )


def _metric_aligned(signal_metric: str, target_metric: str) -> bool:
    return signal_metric.strip().lower() == target_metric.strip().lower()


def _channel_aligned(signal_channel: str, target_channels: list[str]) -> bool:
    if not target_channels:
        return True
    normalized = {channel.strip().lower() for channel in target_channels if channel.strip()}
    return signal_channel.strip().lower() in normalized


def _estimand_aligned(signal_estimand: str, target_estimand: str) -> bool:
    return signal_estimand.strip().lower() == target_estimand.strip().lower()


def _time_window_aligned(
    signal_start: date | None,
    signal_end: date | None,
    planning_start: date | None,
    planning_end: date | None,
) -> tuple[bool, str | None]:
    if signal_start is None or signal_end is None:
        return False, "signal time window dates unavailable"
    if planning_start is None or planning_end is None:
        return True, "planning window unspecified; signal dates accepted"
    overlaps = signal_start <= planning_end and signal_end >= planning_start
    if not overlaps:
        return False, "signal time window does not overlap planning window"
    return True, None


def _freshness_valid(
    freshness_date: date | None,
    end_date: date | None,
    *,
    reference_date: date,
    max_age_days: int,
) -> tuple[bool, str | None]:
    fresh_date = freshness_date or end_date
    if fresh_date is None:
        return False, "signal freshness date unavailable"
    age_days = (reference_date - fresh_date).days
    max_age = max_age_days or DEFAULT_MAX_SIGNAL_AGE_DAYS
    if age_days > max_age:
        return False, f"signal is {age_days} days old; max allowed is {max_age}"
    if age_days > max_age * 0.75:
        return True, f"signal is {age_days} days old; approaching max age {max_age}"
    return True, None


def _is_causal_evidence(evidence_source: str | None) -> bool:
    if not evidence_source:
        return False
    return evidence_source.strip().lower() in _CAUSAL_EVIDENCE_SOURCES


def _column_name_for_role(
    source: PlanningMMMCalibrationSignalTabularSource,
    role: PlanningMMMCalibrationSignalColumnRole,
) -> str | None:
    for mapping in source.column_mappings:
        if mapping.column_role == role and mapping.present:
            return mapping.normalized_column_name or mapping.column_name
    return None


def _reference_date(target: PlanningMMMCalibrationSignalMappingTarget) -> date:
    if target.planning_end_date is not None:
        return target.planning_end_date
    return datetime.now(tz=UTC).date()


def _enum_value(value: object) -> str:
    if hasattr(value, "value"):
        return str(getattr(value, "value"))
    return str(value)


def _default_execution_allowed() -> dict[str, bool]:
    return {
        "model_execution": False,
        "calibration_math": False,
        "prior_application": False,
        "likelihood_construction": False,
        "posterior_calculation": False,
        "optimizer_execution": False,
        "simulator_execution": False,
        "recommendation_generation": False,
        "decision_surface_execution": False,
        "claim_authorization": False,
    }


def _blocked_result(
    *,
    request_id: str,
    mapping_status: PlanningMMMCalibrationSignalMappingStatus,
    readiness_status: PlanningMMMCalibrationSignalReadinessStatus,
    blocked_reasons: list[str],
    issues: list[PlanningMMMCalibrationSignalMappingIssueCode],
    warnings: list[str],
    lineage: dict[str, str],
    mapped_records: list[PlanningMMMCalibrationSignalMappedRecord] | None = None,
    intake_issues: Sequence[object] | None = None,
) -> PlanningMMMCalibrationSignalMappingReadinessResult:
    if intake_issues:
        lineage["upstream_intake_issue_count"] = str(len(intake_issues))
    assessment = PlanningMMMCalibrationSignalReadinessAssessment(
        mapped_records=mapped_records or [],
        readiness_status=readiness_status,
        issues=_dedupe_issues(issues),
        warnings=list(dict.fromkeys(warnings)),
    )
    return PlanningMMMCalibrationSignalMappingReadinessResult(
        request_id=request_id,
        mapping_status=mapping_status,
        readiness_status=readiness_status,
        assessment=assessment,
        mapped_records=mapped_records or [],
        blocked_reasons=blocked_reasons,
        warnings=list(dict.fromkeys(warnings)),
        issues=_dedupe_issues(issues),
        lineage=lineage,
        execution_allowed=_default_execution_allowed(),
    )


def _dedupe_issues(
    issues: list[PlanningMMMCalibrationSignalMappingIssueCode],
) -> list[PlanningMMMCalibrationSignalMappingIssueCode]:
    seen: set[PlanningMMMCalibrationSignalMappingIssueCode] = set()
    ordered: list[PlanningMMMCalibrationSignalMappingIssueCode] = []
    for issue in issues:
        if issue not in seen:
            seen.add(issue)
            ordered.append(issue)
    return ordered
