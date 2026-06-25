"""Tests for P7 UI display helper functions."""

import importlib

from app.demo_fixtures import (
    build_dtc_skincare_advisory_plan,
    build_national_blocked_readiness_reports,
    build_valid_calibration_fixture,
)
from app.ui_renderers import (
    advisory_plan_to_display_dict,
    calibration_mapping_to_display_dict,
    contract_to_display_dict,
    format_status_badge,
    mode_banner,
    readiness_report_to_display_dict,
    render_allowed_blocked_steps,
    summarize_blocking_reasons,
    summarize_warnings,
)
from mip.contracts.advisory import AdvisoryClaimType, AdvisoryEvidenceMode


def test_format_status_badge() -> None:
    assert format_status_badge("ready") == "[READY]"
    assert format_status_badge("needs_more_data") == "[NEEDS MORE DATA]"


def test_summarize_warnings_and_blocking_reasons() -> None:
    assert summarize_warnings([]) == ["None"]
    assert summarize_warnings(["warn-a"]) == ["warn-a"]
    assert summarize_blocking_reasons(["missing_trust_report"]) == ["missing_trust_report"]


def test_render_allowed_blocked_steps() -> None:
    sections = render_allowed_blocked_steps(["step_a"], ["step_b"])
    assert sections["allowed_next_steps"] == ["step_a"]
    assert sections["blocked_next_steps"] == ["step_b"]


def test_advisory_display_preserves_status_warnings_and_steps() -> None:
    plan = build_dtc_skincare_advisory_plan()
    display = advisory_plan_to_display_dict(plan)
    assert display["status"] == str(plan.status)
    assert display["evidence_mode"] == AdvisoryEvidenceMode.BUSINESS_PROFILE_ONLY.value
    assert AdvisoryClaimType.HYPOTHESIS_TO_TEST.value in display["claim_types"]
    assert display["warnings"] == summarize_warnings(plan.warnings)
    assert display["blocking_reasons"] == summarize_blocking_reasons(plan.blocking_reasons)
    assert display["allowed_next_steps"] == plan.allowed_next_steps
    assert display["blocked_next_steps"] == plan.blocked_next_steps
    assert "advisory_disclaimer" in display


def test_readiness_display_preserves_status_warnings_and_blocking_reasons() -> None:
    reports = build_national_blocked_readiness_reports()
    display = readiness_report_to_display_dict(reports[0])
    assert display["status"] == str(reports[0].status)
    assert display["warnings"] == summarize_warnings(reports[0].warnings)
    assert display["blocking_reasons"] == summarize_blocking_reasons(reports[0].blocking_reasons)


def test_calibration_display_preserves_mapping_fields() -> None:
    result = build_valid_calibration_fixture()
    assert result.signal is not None
    display = calibration_mapping_to_display_dict(
        result.report,
        signal_id=result.signal.calibration_id,
    )
    assert display["status"] == result.report.status.value
    assert display["mapped_signal_id"] == result.signal.calibration_id
    assert display["warnings"] == summarize_warnings(result.report.warnings)
    assert display["blocking_reasons"] == summarize_blocking_reasons(result.report.blocking_reasons)


def test_contract_to_display_dict_round_trip() -> None:
    plan = build_dtc_skincare_advisory_plan()
    payload = contract_to_display_dict(plan)
    assert payload["plan_id"] == plan.plan_id


def test_mode_banner_is_deterministic() -> None:
    banner = mode_banner()
    assert banner["mode"] == "Deterministic"
    assert "No LLM" in banner["description"]


def test_app_package_imports() -> None:
    streamlit_app = importlib.import_module("app.streamlit_app")
    demo_fixtures = importlib.import_module("app.demo_fixtures")
    ui_renderers = importlib.import_module("app.ui_renderers")
    assert callable(streamlit_app.main)
    assert hasattr(demo_fixtures, "build_advisory_plan")
    assert hasattr(ui_renderers, "advisory_plan_to_display_dict")
    assert hasattr(ui_renderers, "format_provider_mode")
    assert hasattr(ui_renderers, "format_explanation_plan")


def test_format_provider_mode_and_explanation_plan() -> None:
    from app.ui_renderers import format_explanation_plan, format_provider_mode
    from mip.contracts.llm_provider import LLMGovernedInputSourceType, LLMUseCase
    from mip.workflows.intake.llm_explanation import (
        build_default_llm_provider_config,
        build_governed_input_reference,
        build_llm_explanation_plan,
        build_llm_explanation_request,
    )

    config = build_default_llm_provider_config()
    provider_display = format_provider_mode(config)
    assert provider_display["mode"] == "disabled"
    ref = build_governed_input_reference(
        LLMGovernedInputSourceType.COLD_START_ADVISORY_PLAN.value,
        "adv-001",
        "summary",
    )
    request = build_llm_explanation_request(config, LLMUseCase.ADVISORY_PLAN_EXPLANATION, [ref])
    plan = build_llm_explanation_plan(request)
    plan_display = format_explanation_plan(plan)
    assert plan_display["status"] == "deterministic_only"
    assert "generated_answer" not in plan_display
