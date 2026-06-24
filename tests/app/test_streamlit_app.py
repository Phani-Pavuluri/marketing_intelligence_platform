"""Tests for Streamlit demo shell helpers."""

import json
from datetime import date, timedelta

import pytest

from mip.app.streamlit_app import (
    SAMPLE_JSON,
    format_status_badge,
    parse_json_input,
    run_streamlit_workflow_from_json,
    summary_sections,
    summary_sections_with_mmm_fixture,
)
from mip.workflows.orchestrator import WorkflowRunStatus


def _weekly_json(objective_type: str, count: int = 12) -> str:
    records = [
        {
            "date": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "channel": "search",
            "spend": 100 + index,
            "conversions": 10 + index,
        }
        for index in range(count)
    ]
    return json.dumps({"objective": {"objective_type": objective_type}, "records": records})


def test_valid_json_parsing() -> None:
    demo_input = parse_json_input(SAMPLE_JSON)
    assert demo_input.objective.objective_type == "conversion_roi"
    assert len(demo_input.records) == 12


def test_invalid_json_raises_value_error() -> None:
    with pytest.raises(ValueError, match="invalid JSON input"):
        parse_json_input("{not valid json")


def test_conversion_roi_workflow_returns_renderable_sections() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_weekly_json("conversion_roi"))
    sections = summary_sections(summary, explanation)
    assert sections["objective_type"] == "conversion_roi"
    assert sections["workflow_status"] in (
        WorkflowRunStatus.COMPLETED,
        WorkflowRunStatus.COMPLETED_WITH_WARNINGS,
    )
    assert sections["config_draft_status"]
    assert sections["mock_explanation"]


def test_awareness_conversions_only_returns_blocked_sections() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_weekly_json("awareness"))
    sections = summary_sections(summary, explanation)
    assert sections["workflow_status"] == WorkflowRunStatus.BLOCKED
    assert sections["blocking_reasons"]


def test_mock_explanation_is_included() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_weekly_json("conversion_roi"))
    sections = summary_sections(summary, explanation)
    assert explanation.provider == "mock"
    assert sections["mock_explanation"]
    assert sections["disclaimers"]


def test_sections_do_not_claim_model_output() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_weekly_json("conversion_roi"))
    sections = summary_sections(summary, explanation)
    combined = "\n".join(
        value if isinstance(value, str) else "\n".join(value) for value in sections.values()
    ).lower()
    assert "no mmm, geox, adapter, or causal model execution was performed" in combined
    assert "estimated lift" not in combined
    assert "causal impact" not in combined
    assert "budget recommendation" not in combined


def test_format_status_badge() -> None:
    assert format_status_badge("blocked") == "[BLOCKED]"
    assert format_status_badge("completed_with_warnings") == "[COMPLETED WITH WARNINGS]"


def _long_history_json() -> str:
    records = [
        {
            "date": (date(2024, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "spend": 100,
            "conversions": 10,
            "channel": "search" if index % 2 == 0 else "social",
            "geo": "us" if index % 2 == 0 else "uk",
        }
        for index in range(60)
    ]
    return json.dumps({"objective": {"objective_type": "conversion_roi"}, "records": records})


def test_streamlit_sections_include_mmm_fixture_safely() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_long_history_json())
    sections = summary_sections_with_mmm_fixture(summary, explanation)
    assert "mmm_fixture_report" in sections
    mmm_fixture = sections["mmm_fixture_report"]
    assert isinstance(mmm_fixture, dict)
    assert mmm_fixture["decision_surface_type"] == "diagnostic_curve"
    labels = mmm_fixture["placeholder_labels"]
    assert isinstance(labels, list)
    assert "not_model_execution" in labels


def test_streamlit_sections_include_planner_route_safely() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_long_history_json())
    sections = summary_sections_with_mmm_fixture(summary, explanation)
    planner_route = sections["planner_route"]
    assert isinstance(planner_route, dict)
    assert planner_route["recommended_next_action"] == "render_report"
    assert planner_route["allowed_actions"]
    assert planner_route["blocked_actions"]
    combined = str(planner_route).lower()
    assert "actual roi" not in combined
    assert "budget recommendation" not in combined


def test_awareness_workflow_planner_route_requests_missing_data() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_weekly_json("awareness"))
    sections = summary_sections_with_mmm_fixture(summary, explanation)
    planner_route = sections["planner_route"]
    assert isinstance(planner_route, dict)
    assert planner_route["recommended_next_action"] == "parse_input"
    allowed = planner_route["allowed_actions"]
    assert isinstance(allowed, list)
    assert any(
        isinstance(item, dict) and item.get("action_type") == "parse_input" for item in allowed
    )


def test_awareness_workflow_has_no_mmm_fixture_section() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_weekly_json("awareness"))
    sections = summary_sections_with_mmm_fixture(summary, explanation)
    assert "mmm_fixture_report" not in sections


def test_streamlit_sections_include_fixture_engine_result_safely() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_long_history_json())
    sections = summary_sections_with_mmm_fixture(summary, explanation)
    results = sections["fixture_engine_results"]
    assert isinstance(results, list)
    assert results
    first = results[0]
    assert isinstance(first, dict)
    assert first["engine_kind"] == "mmm"
    assert first["status"] in ("completed_placeholder", "approval_required")
    labels = first["labels"]
    assert isinstance(labels, list)
    assert "fixture_engine_orchestration_only" in labels
    assert "not_real_engine_execution" in labels


def test_streamlit_sections_include_approval_checkpoints_safely() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_long_history_json())
    sections = summary_sections_with_mmm_fixture(summary, explanation)
    approval_checkpoints = sections["approval_checkpoints"]
    assert isinstance(approval_checkpoints, dict)
    assert "safety_note" in approval_checkpoints
    assert "local demo state only" in str(approval_checkpoints["safety_note"]).lower()


def test_streamlit_sections_include_sibling_fixture_imports_safely() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_long_history_json())
    sections = summary_sections_with_mmm_fixture(summary, explanation)
    sibling_imports = sections["sibling_fixture_imports"]
    assert isinstance(sibling_imports, list)
    assert len(sibling_imports) == 2
    mmm_item = sibling_imports[0]
    assert isinstance(mmm_item, dict)
    assert mmm_item["source_repo"] == "mmm"
    assert mmm_item["engine_kind"] == "mmm"
    labels = mmm_item["labels"]
    assert isinstance(labels, list)
    assert "pinned_sibling_repo_fixture_only" in labels
    assert "not_live_engine_execution" in labels
    combined = str(sibling_imports).lower()
    assert "actual roi" not in combined
    assert "budget recommendation" not in combined


def test_streamlit_sections_include_sibling_export_hook_safely() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_long_history_json())
    sections = summary_sections_with_mmm_fixture(summary, explanation)
    hook_sections = sections["sibling_export_hook"]
    assert isinstance(hook_sections, dict)
    assert hook_sections["status"] == "validated"
    labels = hook_sections["labels"]
    assert isinstance(labels, list)
    assert "readonly_sibling_export_hook_only" in labels
    assert "static_export_file_only" in labels
    combined = str(hook_sections).lower()
    assert "actual roi" not in combined
    assert "budget recommendation" not in combined


def test_streamlit_sections_include_sibling_compatibility_safely() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_long_history_json())
    sections = summary_sections_with_mmm_fixture(summary, explanation)
    compatibility = sections["sibling_compatibility"]
    assert isinstance(compatibility, dict)
    assert compatibility["aggregate_status"]
    reports = compatibility["reports"]
    assert isinstance(reports, list)
    assert reports
    combined = str(compatibility).lower()
    assert "sibling_repo_compatibility_check_only" in combined
    assert "actual roi" not in combined


def test_streamlit_sections_include_local_sibling_paths_safely() -> None:
    summary, explanation = run_streamlit_workflow_from_json(_long_history_json())
    sections = summary_sections_with_mmm_fixture(summary, explanation)
    local_paths = sections["local_sibling_paths"]
    assert isinstance(local_paths, dict)
    assert local_paths["mmm_repo_path"]
    assert local_paths["aggregate_status"]
    combined = str(local_paths).lower()
    assert "local_sibling_export_path_wiring_only" in combined
    assert "actual roi" not in combined


def test_public_imports() -> None:
    from mip.app.streamlit_app import main

    assert callable(main)
    assert callable(parse_json_input)
    assert callable(run_streamlit_workflow_from_json)
    assert callable(summary_sections_with_mmm_fixture)
