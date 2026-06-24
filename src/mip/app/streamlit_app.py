"""Thin Streamlit shell over the deterministic local workflow stack."""

from __future__ import annotations

import json
from datetime import date, timedelta
from typing import Any

from pydantic import ValidationError

from mip.cli.demo import DemoInput
from mip.llm.explanations import EXECUTION_DISCLAIMER, assert_safe_explanation
from mip.llm.providers import LLMProviderResponse, MockLLMProvider
from mip.workflows.orchestrator import WorkflowRunSummary, run_local_workflow

_FORBIDDEN_OUTPUT_PHRASES = (
    "estimated lift",
    "causal impact",
    "incremental roi",
    "budget recommendation",
    "model results",
    "ran mmm",
    "executed geox",
)

_STATUS_BADGES = {
    "completed": "[COMPLETED]",
    "completed_with_warnings": "[COMPLETED WITH WARNINGS]",
    "blocked": "[BLOCKED]",
}


def _build_sample_json() -> str:
    records = [
        {
            "date": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "channel": "Search",
            "spend": 100 + index * 10,
            "conversions": 10 + index,
        }
        for index in range(12)
    ]
    payload = {
        "objective": {
            "objective_type": "conversion_roi",
            "primary_kpi": "conversions",
        },
        "records": records,
    }
    return json.dumps(payload, indent=2)


SAMPLE_JSON = _build_sample_json()


def parse_json_input(text: str) -> DemoInput:
    """Parse and validate JSON workflow input from pasted or uploaded text."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        msg = "invalid JSON input"
        raise ValueError(msg) from exc

    if not isinstance(payload, dict):
        msg = "JSON input must be an object"
        raise ValueError(msg)

    try:
        return DemoInput.model_validate(payload)
    except ValidationError as exc:
        msg = f"invalid workflow input: {exc}"
        raise ValueError(msg) from exc


def run_streamlit_workflow_from_json(
    text: str,
) -> tuple[WorkflowRunSummary, LLMProviderResponse]:
    """Run the local workflow and mock explanation from JSON text."""
    demo_input = parse_json_input(text)
    summary = run_local_workflow(demo_input.objective, demo_input.records)
    explanation = MockLLMProvider().explain(summary)
    return summary, explanation


def format_status_badge(status: str) -> str:
    """Format a workflow status value for display."""
    normalized = status.strip().lower().replace(" ", "_")
    return _STATUS_BADGES.get(normalized, f"[{status.upper()}]")


def summary_sections(
    summary: WorkflowRunSummary,
    explanation_response: LLMProviderResponse,
) -> dict[str, str | list[str]]:
    """Build renderable summary sections from workflow and explanation artifacts."""
    sections: dict[str, str | list[str]] = {
        "workflow_status": _enum_value(summary.status),
        "workflow_status_badge": format_status_badge(_enum_value(summary.status)),
        "objective_type": _enum_value(summary.objective.objective_type),
        "feasibility_status": _enum_value(summary.feasibility.status),
        "readiness_status": _enum_value(summary.readiness.status),
        "config_draft_status": _enum_value(summary.config_draft.metadata.status),
        "workflow_type": _enum_value(summary.config_draft.metadata.workflow_type),
        "production_eligible": str(summary.config_draft.metadata.production_eligible),
        "warnings": list(summary.warnings),
        "blocking_reasons": list(summary.blocking_reasons),
        "recommended_fixes": list(summary.recommended_fixes),
        "recommended_next_questions": list(summary.recommended_next_questions),
        "narrative_summary": summary.narrative_summary,
        "mock_explanation": explanation_response.text,
        "disclaimers": list(explanation_response.disclaimers),
        "execution_disclaimer": EXECUTION_DISCLAIMER,
    }
    _assert_sections_safe(sections)
    return sections


def main() -> None:
    """Streamlit entrypoint for the local workflow demo shell."""
    import streamlit as st

    st.set_page_config(page_title="MIP Local Demo", layout="wide")
    st.title("MIP Local Workflow Demo")
    st.caption(
        "Deterministic intake, readiness, and config draft review. "
        "No engine execution or real LLM APIs."
    )

    with st.expander("Sample JSON"):
        st.code(SAMPLE_JSON, language="json")

    uploaded = st.file_uploader("Upload JSON file", type=["json"])
    json_text = st.text_area("JSON input", value=SAMPLE_JSON, height=240)

    if st.button("Run workflow", type="primary"):
        try:
            input_text = uploaded.getvalue().decode("utf-8") if uploaded is not None else json_text
            summary, explanation = run_streamlit_workflow_from_json(input_text)
            sections = summary_sections(summary, explanation)
        except ValueError as exc:
            st.error(str(exc))
            return

        st.subheader("Workflow status")
        st.write(sections["workflow_status_badge"])
        st.write(f"Objective: `{sections['objective_type']}`")
        st.write(f"Feasibility: `{sections['feasibility_status']}`")
        st.write(f"Readiness: `{sections['readiness_status']}`")
        st.write(f"Config draft: `{sections['config_draft_status']}`")
        st.write(f"Workflow type: `{sections['workflow_type']}`")
        st.write(f"Production eligible: `{sections['production_eligible']}`")

        _render_list_section(st, "Warnings", sections["warnings"])
        _render_list_section(st, "Blocking reasons", sections["blocking_reasons"])
        _render_list_section(st, "Recommended fixes", sections["recommended_fixes"])
        _render_list_section(
            st,
            "Recommended next questions",
            sections["recommended_next_questions"],
        )

        st.subheader("Narrative summary")
        st.write(sections["narrative_summary"])

        st.subheader("Mock conversational explanation")
        st.write(sections["mock_explanation"])

        st.info(sections["execution_disclaimer"])


def _render_list_section(
    st: Any,
    title: str,
    items: str | list[str],
) -> None:
    st.subheader(title)
    if isinstance(items, str):
        st.write(items)
        return
    if not items:
        st.write("None")
        return
    for item in items:
        st.write(f"- {item}")


def _enum_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))


def _assert_sections_safe(sections: dict[str, str | list[str]]) -> None:
    text_parts: list[str] = []
    for value in sections.values():
        if isinstance(value, str):
            text_parts.append(value)
        else:
            text_parts.extend(value)
    combined = "\n".join(text_parts)
    assert_safe_explanation(combined)
    lowered = combined.lower()
    for phrase in _FORBIDDEN_OUTPUT_PHRASES:
        if phrase in lowered:
            msg = f"rendered sections must not include forbidden phrase: {phrase}"
            raise ValueError(msg)
