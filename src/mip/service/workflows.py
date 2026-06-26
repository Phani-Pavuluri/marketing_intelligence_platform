"""Thin deterministic workflow wrappers for P10b API routes."""

from __future__ import annotations

from typing import Any

from mip.contracts.advisory import ColdStartAdvisoryPlan
from mip.contracts.calibration_intake import CalibrationMappingReport
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

_INTAKE_EXAMPLE_KEYS = {
    "national_mmm_diagnostic": "National MMM diagnostic intake",
    "geox_experiment_design": "GeoX experiment design intake",
}


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
    """Build advisory API response from demo fixture helper."""
    from app.demo_fixtures import build_advisory_plan

    plan = build_advisory_plan(sample_key)
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
    """Build readiness API response from demo fixture helper."""
    from app.demo_fixtures import build_readiness_reports

    reports = build_readiness_reports(sample_key)
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
    """Build calibration mapping API response from demo fixture helper."""
    from app.demo_fixtures import build_calibration_fixture

    fixture = build_calibration_fixture(sample_key)
    return _calibration_response_from_fixture(fixture)


def _calibration_response_from_fixture(fixture: Any) -> CalibrationMapResponse:
    report: CalibrationMappingReport = fixture.report
    evidence = fixture.evidence
    mapped_signal_id = (
        fixture.signal.calibration_id if fixture.signal is not None else report.mapped_signal_id
    )
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
    """Build intake overview API response from demo fixture helper."""
    from app.demo_fixtures import build_intake_overview_examples

    label = _INTAKE_EXAMPLE_KEYS.get(example_key)
    if label is None:
        msg = f"unknown intake example: {example_key}"
        raise ValueError(msg)
    for example in build_intake_overview_examples():
        if example.label == label:
            return _intake_response_from_example(
                example.label,
                example.recommendation,
                example.session,
            )
    msg = f"intake example not found: {example_key}"
    raise ValueError(msg)


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
