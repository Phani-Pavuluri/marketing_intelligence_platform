"""CLI for canonical MIP repository execution lifecycle control."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from mip.execution.errors import TaskControlError
from mip.execution.state import ALLOWED_STATUSES, transition_state, validate_state
from mip.execution.views import assert_execution_view, render_execution_view, replace_execution_view

STATE_RELATIVE = Path("docs/execution/EXECUTION_STATE.json")
ACTIVE_RELATIVE = Path("docs/execution/ACTIVE_TASK.md")
REPORT_RELATIVE = Path("docs/execution/LATEST_COMPLETION_REPORT.md")


def find_repository_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / STATE_RELATIVE).is_file() and (candidate / "pyproject.toml").is_file():
            return candidate
    raise TaskControlError("E_REPOSITORY_ROOT", "could not locate MIP repository root")


def _read_state(root: Path) -> dict[str, Any]:
    try:
        value = json.loads((root / STATE_RELATIVE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise TaskControlError("E_STATE_PARSE", str(exc)) from exc
    if not isinstance(value, dict):
        raise TaskControlError("E_STATE_SCHEMA", "execution state root must be an object")
    return value


def _read_views(root: Path) -> tuple[str, str]:
    try:
        return (
            (root / ACTIVE_RELATIVE).read_text(encoding="utf-8"),
            (root / REPORT_RELATIVE).read_text(encoding="utf-8"),
        )
    except OSError as exc:
        raise TaskControlError("E_VIEW_READ", str(exc)) from exc


def check_repository(root: Path) -> None:
    state = _read_state(root)
    validate_state(state)
    active, report = _read_views(root)
    assert_execution_view(
        active,
        render_execution_view(state, document="active_task"),
        document="ACTIVE_TASK.md",
    )
    assert_execution_view(
        report,
        render_execution_view(state, document="completion_report"),
        document="LATEST_COMPLETION_REPORT.md",
    )


def _write_atomic(path: Path, content: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _candidate_views(root: Path, state: dict[str, Any]) -> tuple[str, str]:
    active, report = _read_views(root)
    active_candidate = replace_execution_view(
        active, render_execution_view(state, document="active_task")
    )
    report_candidate = replace_execution_view(
        report, render_execution_view(state, document="completion_report")
    )
    return active_candidate, report_candidate


def sync_repository(root: Path) -> None:
    state = _read_state(root)
    validate_state(state)
    active, report = _candidate_views(root, state)
    _write_atomic(root / ACTIVE_RELATIVE, active)
    _write_atomic(root / REPORT_RELATIVE, report)
    check_repository(root)


def transition_repository(root: Path, arguments: argparse.Namespace) -> None:
    state = _read_state(root)
    validate_state(state)
    check_repository(root)
    candidate = transition_state(
        state,
        arguments.to,
        implementation_sha=arguments.implementation_sha,
        rejected_review_sha=arguments.rejected_review_sha,
        rejected_implementation_sha=arguments.rejected_implementation_sha,
        reviewed_head_sha=arguments.reviewed_head_sha,
        blockers=arguments.blocker,
        clear_blockers=arguments.clear_blockers,
        authorize_execution=arguments.authorize_execution,
        authorize_correction=arguments.authorize_correction,
        complete_correction=arguments.complete_correction,
        authorization_head_sha=arguments.authorization_head_sha,
        task_authoring_head_sha=arguments.task_authoring_head_sha,
        local_branch_cleanup=arguments.local_branch_cleanup,
        remote_branch_cleanup=arguments.remote_branch_cleanup,
    )
    active, report = _candidate_views(root, candidate)
    state_text = json.dumps(candidate, indent=2, ensure_ascii=False) + "\n"
    # Validate the complete candidate set before replacing any repository file.
    validate_state(candidate)
    assert_execution_view(
        active,
        render_execution_view(candidate, document="active_task"),
        document="ACTIVE_TASK.md",
    )
    assert_execution_view(
        report,
        render_execution_view(candidate, document="completion_report"),
        document="LATEST_COMPLETION_REPORT.md",
    )
    _write_atomic(root / STATE_RELATIVE, state_text)
    _write_atomic(root / ACTIVE_RELATIVE, active)
    _write_atomic(root / REPORT_RELATIVE, report)
    check_repository(root)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m mip.execution.taskctl")
    parser.add_argument("--root", type=Path, help="repository root (defaults to auto-discovery)")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("check", help="validate canonical state and generated views")
    subparsers.add_parser("sync", help="regenerate both lifecycle views")
    transition = subparsers.add_parser("transition", help="apply one allowed lifecycle transition")
    transition.add_argument("--to", required=True, choices=sorted(ALLOWED_STATUSES))
    transition.add_argument("--implementation-sha")
    transition.add_argument("--rejected-review-sha")
    transition.add_argument("--rejected-implementation-sha")
    transition.add_argument("--reviewed-head-sha")
    transition.add_argument("--blocker", action="append", default=[])
    transition.add_argument("--clear-blockers", action="store_true")
    transition.add_argument("--authorize-execution", action="store_true")
    transition.add_argument("--authorize-correction", action="store_true")
    transition.add_argument("--complete-correction", action="store_true")
    transition.add_argument("--authorization-head-sha")
    transition.add_argument("--task-authoring-head-sha")
    transition.add_argument("--local-branch-cleanup")
    transition.add_argument("--remote-branch-cleanup")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        root = find_repository_root(arguments.root)
        if arguments.command == "check":
            check_repository(root)
        elif arguments.command == "sync":
            sync_repository(root)
        else:
            transition_repository(root, arguments)
    except TaskControlError as exc:
        print(exc, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
