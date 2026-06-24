"""Deterministic conversational explanations for workflow summaries."""

from __future__ import annotations

from mip.workflows.orchestrator import WorkflowRunStatus, WorkflowRunSummary

EXECUTION_DISCLAIMER = "No MMM, GeoX, adapter, or causal model execution was performed."

_FORBIDDEN_OUTPUT_PHRASES = (
    "estimated lift",
    "causal impact",
    "incremental roi",
    "budget recommendation",
    "model results",
    "ran mmm",
    "executed geox",
    "model execution was completed",
    "predicted conversions",
    "recommended spend",
)


def explain_workflow_summary(summary: WorkflowRunSummary) -> str:
    """Build a deterministic conversational explanation from a workflow summary."""
    status = _enum_value(summary.status)
    objective = _enum_value(summary.objective.objective_type)
    feasibility = _enum_value(summary.feasibility.status)
    readiness = _enum_value(summary.readiness.status)
    config_status = _enum_value(summary.config_draft.metadata.status)
    workflow_type = _enum_value(summary.config_draft.metadata.workflow_type)
    production_eligible = summary.config_draft.metadata.production_eligible

    paragraphs = [
        _opening_paragraph(status, objective, summary.profile.row_count),
        (
            f"Feasibility is {feasibility}, readiness is {readiness}, and the "
            f"{workflow_type} config draft is {config_status}. Production eligibility "
            f"is {production_eligible}."
        ),
    ]

    if summary.warnings:
        paragraphs.append(_list_paragraph("Warnings to review", summary.warnings))
    if summary.blocking_reasons:
        paragraphs.append(explain_blockers(summary))
    paragraphs.append(explain_next_steps(summary))
    paragraphs.append(summary.narrative_summary)
    paragraphs.append(EXECUTION_DISCLAIMER)

    text = "\n\n".join(paragraphs)
    assert_safe_explanation(text)
    return text


def explain_blockers(summary: WorkflowRunSummary) -> str:
    """Explain blocking reasons from an already-computed workflow summary."""
    if not summary.blocking_reasons:
        text = "There are no blocking reasons for this workflow run."
        assert_safe_explanation(text)
        return text

    text = _list_paragraph("This workflow is blocked because", summary.blocking_reasons)
    assert_safe_explanation(text)
    return text


def explain_next_steps(summary: WorkflowRunSummary) -> str:
    """Explain recommended questions and fixes from a workflow summary."""
    sections: list[str] = []
    if summary.recommended_next_questions:
        sections.append(
            _list_paragraph(
                "Recommended next questions",
                summary.recommended_next_questions,
            )
        )
    if summary.recommended_fixes:
        sections.append(_list_paragraph("Recommended fixes", summary.recommended_fixes))

    if not sections:
        text = "No specific next questions or fixes were identified."
        assert_safe_explanation(text)
        return text

    text = "\n\n".join(sections)
    assert_safe_explanation(text)
    return text


def assert_safe_explanation(text: str) -> None:
    """Raise if explanation text includes forbidden causal or model-output claims."""
    lowered = text.lower()
    for phrase in _FORBIDDEN_OUTPUT_PHRASES:
        if phrase in lowered:
            msg = f"explanation must not include forbidden phrase: {phrase}"
            raise ValueError(msg)


def _opening_paragraph(status: str, objective: str, row_count: int) -> str:
    if status == WorkflowRunStatus.BLOCKED:
        outcome = "is blocked"
    elif status == WorkflowRunStatus.COMPLETED_WITH_WARNINGS:
        outcome = "completed with warnings"
    else:
        outcome = "completed"
    return (
        f"Your local workflow review for the {objective} objective {outcome} "
        f"after reviewing {row_count} records."
    )


def _list_paragraph(title: str, items: list[str]) -> str:
    lines = [f"{title}:"]
    lines.extend(f"- {item}" for item in items)
    return "\n".join(lines)


def _enum_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))
