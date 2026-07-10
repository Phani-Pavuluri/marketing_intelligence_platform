"""Structured report assembly for governed demo artifacts."""

from mip.reports.advisory_reports import (
    build_cold_start_advisory_report_from_stage_a_fixture,
    export_cold_start_advisory_report_from_stage_a_fixture,
    list_supported_advisory_fixture_ids,
)
from mip.reports.calibration_reports import (
    build_calibration_report_from_stage_a_fixture,
    export_calibration_report_from_stage_a_fixture,
    list_supported_calibration_fixture_ids,
)
from mip.reports.deterministic_reports import (
    DeterministicReportExportError,
    report_to_dict,
    report_to_json,
    validate_report_has_no_unsupported_advanced_outputs,
    write_report_json,
)
from mip.reports.mmm_fixture import (
    MMMFixtureReport,
    assert_safe_mmm_fixture_report,
    build_mmm_fixture_report,
    format_mmm_fixture_disclaimer,
    mmm_fixture_report_sections,
)
from mip.reports.mmm_planning_response_renderer import (
    MMMPlanningRenderedResponse,
    MMMPlanningResponseRenderIssueCode,
    MMMPlanningResponseSection,
    render_mmm_planning_response,
    summarize_mmm_planning_rendered_response,
)

__all__ = [
    "DeterministicReportExportError",
    "MMMFixtureReport",
    "MMMPlanningRenderedResponse",
    "MMMPlanningResponseRenderIssueCode",
    "MMMPlanningResponseSection",
    "assert_safe_mmm_fixture_report",
    "build_cold_start_advisory_report_from_stage_a_fixture",
    "build_calibration_report_from_stage_a_fixture",
    "build_mmm_fixture_report",
    "export_cold_start_advisory_report_from_stage_a_fixture",
    "export_calibration_report_from_stage_a_fixture",
    "format_mmm_fixture_disclaimer",
    "list_supported_advisory_fixture_ids",
    "list_supported_calibration_fixture_ids",
    "mmm_fixture_report_sections",
    "render_mmm_planning_response",
    "report_to_dict",
    "report_to_json",
    "summarize_mmm_planning_rendered_response",
    "validate_report_has_no_unsupported_advanced_outputs",
    "write_report_json",
]
