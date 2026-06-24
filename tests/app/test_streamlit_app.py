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


def test_public_imports() -> None:
    from mip.app.streamlit_app import main

    assert callable(main)
    assert callable(parse_json_input)
    assert callable(run_streamlit_workflow_from_json)
