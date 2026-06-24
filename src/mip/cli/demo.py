"""Local deterministic CLI demo runner over the workflow orchestrator."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from pydantic import Field, ValidationError, field_validator

from mip.contracts.base import ContractBaseModel
from mip.workflows.intake.objectives import BusinessObjective
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


class DemoInput(ContractBaseModel):
    """JSON input payload for a local workflow demo run."""

    objective: BusinessObjective
    records: list[dict[str, Any]] = Field(default_factory=list)

    @field_validator("records")
    @classmethod
    def records_not_empty(cls, value: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not value:
            msg = "records cannot be empty"
            raise ValueError(msg)
        return value


def load_demo_input(path: str | Path) -> DemoInput:
    """Load and validate demo input JSON from a file path."""
    input_path = Path(path)
    if not input_path.is_file():
        msg = f"demo input file not found: {input_path}"
        raise FileNotFoundError(msg)

    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        msg = f"invalid JSON in demo input file: {input_path}"
        raise ValueError(msg) from exc

    if not isinstance(payload, dict):
        msg = "demo input must be a JSON object"
        raise ValueError(msg)

    try:
        return DemoInput.model_validate(payload)
    except ValidationError as exc:
        msg = f"invalid demo input: {exc}"
        raise ValueError(msg) from exc


def run_demo_from_file(path: str | Path) -> WorkflowRunSummary:
    """Run the local workflow demo from a JSON input file."""
    demo_input = load_demo_input(path)
    return run_local_workflow(demo_input.objective, demo_input.records)


def format_workflow_summary(summary: WorkflowRunSummary) -> str:
    """Format a workflow summary for CLI or file output."""
    config_status = _enum_value(summary.config_draft.metadata.status)
    sections = [
        "MIP Local Workflow Demo Summary",
        "================================",
        f"Workflow status: {_enum_value(summary.status)}",
        f"Objective type: {_enum_value(summary.objective.objective_type)}",
        f"Readiness status: {_enum_value(summary.readiness.status)}",
        f"Config draft status: {config_status}",
        f"Workflow type: {_enum_value(summary.config_draft.metadata.workflow_type)}",
        f"Production eligible: {summary.config_draft.metadata.production_eligible}",
        "",
        _format_list_section("Warnings", summary.warnings),
        _format_list_section("Blocking reasons", summary.blocking_reasons),
        _format_list_section("Recommended next questions", summary.recommended_next_questions),
        _format_list_section("Recommended fixes", summary.recommended_fixes),
        "Narrative summary",
        "-----------------",
        summary.narrative_summary,
    ]
    formatted = "\n".join(sections)
    _assert_safe_output(formatted)
    return formatted


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for the local workflow demo runner."""
    parser = argparse.ArgumentParser(
        description="Run a deterministic local MIP workflow demo from JSON input.",
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with objective and records",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Optional path to write formatted summary text",
    )
    args = parser.parse_args(argv)

    try:
        summary = run_demo_from_file(args.input_file)
        formatted = format_workflow_summary(summary)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(formatted)
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(formatted, encoding="utf-8")
    return 0


def _format_list_section(title: str, items: list[str]) -> str:
    if not items:
        return f"{title}: none"
    lines = [f"{title}:"]
    lines.extend(f"- {item}" for item in items)
    return "\n".join(lines)


def _enum_value(value: object) -> str:
    if isinstance(value, str):
        return value
    return str(getattr(value, "value", value))


def _assert_safe_output(text: str) -> None:
    lowered = text.lower()
    for phrase in _FORBIDDEN_OUTPUT_PHRASES:
        if phrase in lowered:
            msg = f"formatted output must not include forbidden phrase: {phrase}"
            raise ValueError(msg)
