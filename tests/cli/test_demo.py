"""Tests for local CLI demo runner."""

import json
from datetime import date, timedelta
from pathlib import Path

import pytest

from mip.cli.demo import (
    format_workflow_summary,
    load_demo_input,
    run_demo_from_file,
)
from mip.workflows.orchestrator import WorkflowRunStatus


def _write_demo(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _weekly_records(count: int = 12) -> list[dict[str, object]]:
    return [
        {
            "date": (date(2025, 1, 1) + timedelta(days=7 * index)).isoformat(),
            "channel": "search",
            "spend": 100 + index,
            "conversions": 10 + index,
        }
        for index in range(count)
    ]


def test_load_valid_json(tmp_path: Path) -> None:
    demo_path = tmp_path / "demo.json"
    _write_demo(
        demo_path,
        {
            "objective": {"objective_type": "conversion_roi", "primary_kpi": "conversions"},
            "records": _weekly_records(12),
        },
    )
    demo_input = load_demo_input(demo_path)
    assert demo_input.objective.objective_type == "conversion_roi"
    assert len(demo_input.records) == 12


def test_missing_objective_raises_clean_error(tmp_path: Path) -> None:
    demo_path = tmp_path / "invalid.json"
    _write_demo(demo_path, {"records": _weekly_records(2)})
    with pytest.raises(ValueError, match="invalid demo input"):
        load_demo_input(demo_path)


def test_conversion_roi_demo_returns_formatted_summary(tmp_path: Path) -> None:
    demo_path = tmp_path / "conversion_roi.json"
    _write_demo(
        demo_path,
        {
            "objective": {"objective_type": "conversion_roi"},
            "records": _weekly_records(12),
        },
    )
    summary = run_demo_from_file(demo_path)
    formatted = format_workflow_summary(summary)
    assert "Workflow status:" in formatted
    assert "conversion_roi" in formatted
    assert summary.status in (
        WorkflowRunStatus.COMPLETED,
        WorkflowRunStatus.COMPLETED_WITH_WARNINGS,
    )


def test_awareness_conversions_only_shows_blocked_summary(tmp_path: Path) -> None:
    demo_path = tmp_path / "awareness.json"
    _write_demo(
        demo_path,
        {
            "objective": {"objective_type": "awareness"},
            "records": _weekly_records(12),
        },
    )
    summary = run_demo_from_file(demo_path)
    formatted = format_workflow_summary(summary)
    assert summary.status == WorkflowRunStatus.BLOCKED
    assert "Blocking reasons:" in formatted


def test_output_does_not_claim_model_execution_or_causal_results(tmp_path: Path) -> None:
    demo_path = tmp_path / "demo.json"
    _write_demo(
        demo_path,
        {
            "objective": {"objective_type": "conversion_roi"},
            "records": _weekly_records(12),
        },
    )
    formatted = format_workflow_summary(run_demo_from_file(demo_path))
    lowered = formatted.lower()
    assert "no mmm, geox, adapter, or causal model execution was performed" in lowered
    assert "estimated lift" not in lowered
    assert "causal impact" not in lowered
    assert "budget recommendation" not in lowered


def test_public_imports() -> None:
    from mip.cli.demo import load_demo_input, main, run_demo_from_file

    assert callable(load_demo_input)
    assert callable(run_demo_from_file)
    assert callable(main)
