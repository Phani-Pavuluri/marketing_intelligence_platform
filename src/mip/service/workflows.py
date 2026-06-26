"""Thin deterministic workflow wrappers for P10b API routes."""

from __future__ import annotations

from typing import Any

from mip.contracts.advisory import ColdStartAdvisoryPlan
from mip.contracts.calibration_intake import CalibrationEvidenceInput, CalibrationMappingReport
from mip.contracts.workflow_readiness import BaseWorkflowReadinessReport
from mip.service.contracts import (
    ADVISORY_GOVERNANCE,
    CALIBRATION_GOVERNANCE,
    INTAKE_GOVERNANCE,
    READINESS_GOVERNANCE,
    CalibrationMapResponse,
    ChannelHypothesisSummary,
    ColdStartAdvisoryResponse,
    IntakeOverviewResponse,
    LearningAgendaSummary,
    ReadinessAssessResponse,
    ReadinessReportSummary,
    TrackingChecklistSummary,
)
from mip.workflows.intake.advisory import build_cold_start_advisory_plan
from mip.workflows.intake.calibration_mapping import map_evidence_to_calibration_signal
from mip.workflows.intake.readiness import (
    build_geox_design_readiness_report,
    build_mmm_data_readiness_report,
    build_workflow_readiness_reports,
)
from mip.workflows.intake.recommendation import recommend_intake_path


def _enum_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))


def _advisory_governance() -> Any:
    return ADVISORY_GOVERNANCE


def _readiness_governance() -> Any:
    return READINESS_GOVERNANCE


def _calibration_governance() -> Any:
    return CALIBRATION_GOVERNANCE


def _intake_governance() -> Any:
    return INTAKE_GOVERNANCE


def run_cold_start_advisory(sample_key: str) -> ColdStartAdvisoryResponse:
    """Build advisory API response from demo inputs and workflow helper."""
    from app.demo_fixtures import resolve_advisory_demo_inputs

    inputs = resolve_advisory_demo_inputs(sample_key)
    plan = build_cold_start_advisory_plan(inputs.business_profile, inputs.traffic_profile)
    return _advisory_response_from_plan(plan)


def _advisory_response_from_plan(plan: ColdStartAdvisoryPlan) -> ColdStartAdvisoryResponse:
    hypotheses = [
        ChannelHypothesisSummary(
            channel=_enum_value(hypothesis.channel_candidate),
            claim_type=_enum_value(hypothesis.claim_type),
            evidence_level=_enum_value(hypothesis.evidence_level),
            summary=hypothesis.hypothesis_text,
            why_to_test=hypothesis.why_to_test,
        )
        for hypothesis in plan.channel_hypotheses
    ]
    tracking = None
    if plan.tracking_checklist is not None:
        tracking = TrackingChecklistSummary(
            required_items=list(plan.tracking_checklist.required_items),
            missing_items=list(plan.tracking_checklist.missing_items),
            recommended_items=list(plan.tracking_checklist.recommended_items),
        )
    learning = None
    if plan.learning_agenda is not None:
        learning = LearningAgendaSummary(
            agenda_id=plan.learning_agenda.agenda_id,
            learning_questions=list(plan.learning_agenda.learning_questions),
            success_criteria=list(plan.learning_agenda.success_criteria),
        )
    return ColdStartAdvisoryResponse(
        status=_enum_value(plan.status),
        evidence_mode=_enum_value(plan.evidence_mode),
        claim_types=[_enum_value(claim) for claim in plan.claim_types],
        channel_hypotheses=hypotheses,
        tracking_checklist=tracking,
        learning_agenda=learning,
        warnings=list(plan.warnings),
        blocking_reasons=list(plan.blocking_reasons),
        allowed_next_steps=list(plan.allowed_next_steps),
        blocked_next_steps=list(plan.blocked_next_steps),
        governance=_advisory_governance(),
    )


def run_readiness_assess(sample_key: str) -> ReadinessAssessResponse:
    """Build readiness API response from demo context and workflow helpers."""
    from app.demo_fixtures import resolve_readiness_demo_context

    context = resolve_readiness_demo_context(sample_key)
    reports = _build_readiness_reports_from_context(context)
    summaries = [_readiness_summary(report) for report in reports]
    warnings: list[str] = []
    blocking: list[str] = []
    for summary in summaries:
        warnings.extend(summary.warnings)
        blocking.extend(summary.blocking_reasons)
    return ReadinessAssessResponse(
        sample_key=sample_key,
        reports=summaries,
        warnings=warnings,
        blocking_reasons=blocking,
        governance=_readiness_governance(),
    )


def _build_readiness_reports_from_context(context: Any) -> list[BaseWorkflowReadinessReport]:
    reports = list(build_workflow_readiness_reports(context.primary_workbench))
    if context.geo_level_mmm_workbench is None or context.geox_workbench is None:
        return reports
    geo_level_mmm = build_mmm_data_readiness_report(context.geo_level_mmm_workbench)
    geox = build_geox_design_readiness_report(context.geox_workbench)
    existing_types = {report.report_type for report in reports}
    if geo_level_mmm.report_type not in existing_types:
        reports.append(geo_level_mmm)
    if geox.report_type not in existing_types:
        reports.append(geox)
    return reports


def _readiness_summary(report: BaseWorkflowReadinessReport) -> ReadinessReportSummary:
    supported_route = report.supported_route
    return ReadinessReportSummary(
        report_type=_enum_value(report.report_type),
        status=_enum_value(report.status),
        supported_route=_enum_value(supported_route) if supported_route is not None else None,
        warnings=list(report.warnings),
        blocking_reasons=list(report.blocking_reasons),
        required_next_inputs=list(report.required_next_inputs),
        allowed_next_steps=list(report.allowed_next_steps),
        blocked_next_steps=list(report.blocked_next_steps),
    )


def run_calibration_map(sample_key: str) -> CalibrationMapResponse:
    """Build calibration mapping API response from demo inputs and workflow helper."""
    from app.demo_fixtures import resolve_calibration_demo_inputs

    inputs = resolve_calibration_demo_inputs(sample_key)
    signal, report = map_evidence_to_calibration_signal(inputs.evidence, inputs.requirement)
    return _calibration_response(inputs.evidence, report, signal)


def _calibration_response(
    evidence: CalibrationEvidenceInput,
    report: CalibrationMappingReport,
    signal: Any,
) -> CalibrationMapResponse:
    mapped_signal_id = signal.calibration_id if signal is not None else report.mapped_signal_id
    lineage = {
        "input_id": report.input_id,
        "requirement_id": report.requirement_id or "",
        "source_artifact_id": evidence.source_artifact_id or "",
        "source_experiment_id": evidence.source_experiment_id or "",
        "source_readout_id": evidence.source_readout_id or "",
    }
    return CalibrationMapResponse(
        status=_enum_value(report.status),
        mapped_signal_id=mapped_signal_id,
        blocking_reasons=list(report.blocking_reasons),
        missing_fields=list(report.missing_fields),
        incompatible_fields=list(report.incompatible_fields),
        warnings=list(report.warnings),
        lineage=lineage,
        allowed_next_steps=list(report.allowed_next_steps),
        blocked_next_steps=list(report.blocked_next_steps),
        governance=_calibration_governance(),
    )


def run_intake_overview(example_key: str) -> IntakeOverviewResponse:
    """Build intake overview API response from demo session and workflow helper."""
    from app.demo_fixtures import resolve_intake_demo_inputs

    demo_inputs = resolve_intake_demo_inputs(example_key)
    recommendation = recommend_intake_path(demo_inputs.session)
    return _intake_response_from_example(
        demo_inputs.label,
        recommendation,
        demo_inputs.session,
    )


def _intake_response_from_example(
    label: str,
    recommendation: Any,
    session: Any,
) -> IntakeOverviewResponse:
    return IntakeOverviewResponse(
        label=label,
        business_question=session.business_question,
        workflow_kind=_enum_value(session.workflow_kind),
        recommended_path=_enum_value(recommendation.recommended_path),
        status=_enum_value(recommendation.status),
        why_this_path=recommendation.why_this_path,
        why_other_paths_blocked=list(recommendation.why_other_paths_blocked),
        required_next_inputs=list(recommendation.required_next_questions),
        warnings=list(recommendation.warnings),
        blocking_reasons=list(recommendation.blocking_reasons),
        allowed_next_steps=list(recommendation.allowed_next_steps),
        blocked_next_steps=list(recommendation.blocked_next_steps),
        governance=_intake_governance(),
    )
