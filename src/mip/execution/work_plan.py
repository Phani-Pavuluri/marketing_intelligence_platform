"""Read-only validator for MIP bounded work plans (plan schema v1).

A bounded work plan is a proposal only. A structurally valid plan never
authorizes execution: every result carries ``execution_authorized=false``.

Command line::

    python -m mip.execution.work_plan validate --plan PATH

The validator reads one UTF-8 JSON object of at most 1 MiB, writes one JSON
result object to stdout, and returns an exit code:

* ``0`` -- the plan is a valid proposal;
* ``2`` -- the file parses as JSON but violates plan constraints (including a
  well-formed JSON value that is not an object);
* ``3`` -- the input is missing, unreadable, oversized, or malformed
  (including duplicate JSON keys, which are rejected rather than silently
  overwritten, unprocessable nesting, or text unrepresentable as UTF-8).

Every failure prints one JSON result (``valid=false``,
``execution_authorized=false``) on stdout. Diagnostics go to stderr.

Diagnostics go to stderr. The validator performs no model call, no network
access, no Git mutation, no worker start, and no taskctl transition.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

PLAN_SCHEMA_VERSION = 1
MAX_PLAN_BYTES = 1024 * 1024
MAX_TASKS = 100
REPOSITORY = "Phani-Pavuluri/marketing_intelligence_platform"

STABLE_EXECUTION_FILES = frozenset(
    {
        "docs/execution/ACTIVE_TASK.md",
        "docs/execution/EXECUTION_STATE.json",
        "docs/execution/LATEST_COMPLETION_REPORT.md",
    }
)

_PLAN_FIELDS = frozenset(
    {
        "schema_version",
        "repository",
        "plan_id",
        "goal",
        "exclusions",
        "tasks",
    }
)

_TASK_FIELDS = frozenset(
    {
        "task_id",
        "feature_branch",
        "outcome",
        "observable_behavior",
        "owned_paths",
        "acceptance_evidence",
        "risk_tier",
        "depends_on",
        "unresolved_design_questions",
    }
)

_STABLE_ID_RE = re.compile(r"[A-Z][A-Z0-9_]{0,127}")
_BRANCH_FORBIDDEN_CHARS = frozenset(" ~^:?*[\\")


class _DuplicateKeyError(ValueError):
    """Raised when a JSON object contains a repeated key."""


def _no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(key)
        result[key] = value
    return result


def _is_int(value: object) -> bool:
    return type(value) is int


def _is_nonempty_text(value: object) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_stable_id(value: object) -> bool:
    return (
        isinstance(value, str)
        and _STABLE_ID_RE.fullmatch(value) is not None
    )


def _problem(code: str, message: str) -> dict[str, str]:
    return {"code": code, "message": message}


def is_valid_branch(name: object) -> bool:
    """Conservative ``git check-ref-format --branch`` equivalent.

    Accepts only names Git itself accepts (verified against
    ``git check-ref-format refs/heads/<name>``), with two documented
    stricter deviations: the reserved name ``main`` is refused, and names
    starting with ``-`` are refused because the ``--branch`` form (and most
    Git subcommands) would parse the leading dash as flags. No Git call.
    """
    if not isinstance(name, str) or name in ("", "@", "main"):
        return False
    if name.startswith("-"):
        return False
    if (
        name.startswith(("/", "."))
        or name.endswith(("/", "."))
        or "//" in name
        or ".." in name
        or "@{" in name
    ):
        return False
    for char in name:
        if ord(char) < 32 or ord(char) == 127 or char in _BRANCH_FORBIDDEN_CHARS:
            return False
    for component in name.split("/"):
        if component in ("", ".") or component.startswith("."):
            return False
        if component.endswith(".lock"):
            return False
    return True


def path_violation(path: object) -> str | None:
    """Return a violation description, or None when the owned path is allowed."""
    if not isinstance(path, str) or path == "":
        return "owned path must be a nonempty string"
    if "\x00" in path:
        return "owned path must not contain NUL"
    if "\\" in path:
        return "owned path must not contain backslashes"
    if path.startswith("/"):
        return "owned path must be repository-relative, not absolute"
    parts = path.split("/")
    if any(part in ("", ".") for part in parts):
        return "owned path must not contain empty or '.' components"
    if ".." in parts:
        return "owned path must not contain '..' traversal"
    if any(char in "*?[]" for char in path):
        return "owned path must be an exact filename, not a glob"
    if ".git" in parts:
        return "owned path must not reference .git/"
    if parts[0] == ".codex":
        return "owned path must not reference local-only .codex/"
    if len(parts) >= 2 and parts[0] == "docs" and parts[1] == "tasks":
        return "owned path must not reference local-only docs/tasks/"
    if path in STABLE_EXECUTION_FILES:
        return "stable execution metadata files are never plan-owned paths"
    return None


def canonical_digest(plan: dict[str, Any]) -> str:
    """SHA256 of canonical plan JSON: sorted keys, compact separators, UTF-8."""
    canonical = json.dumps(
        plan, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _result(
    plan_id: str | None,
    valid: bool,
    digest: str | None,
    ordered: list[str],
    problems: list[dict[str, str]],
) -> dict[str, Any]:
    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "plan_id": plan_id,
        "valid": valid,
        "execution_authorized": False,
        "plan_sha256": digest,
        "ordered_task_ids": ordered,
        "problems": problems,
    }


def validate_plan_object(plan: Any) -> tuple[bool, str | None, list[str], list[dict[str, str]]]:
    """Validate an already-parsed plan object.

    Returns ``(valid, plan_id_or_none, ordered_task_ids, problems)``.
    """
    problems: list[dict[str, str]] = []
    if not isinstance(plan, dict):
        return False, None, [], [_problem("PLAN_TOP_LEVEL", "plan must be a JSON object")]

    plan_id: str | None = plan.get("plan_id") if isinstance(plan.get("plan_id"), str) else None
    for field in sorted(set(plan.keys()) - _PLAN_FIELDS):
        problems.append(_problem("PLAN_UNKNOWN_FIELD", f"unknown plan field: {field}"))

    if not _is_int(plan.get("schema_version")) or plan.get("schema_version") != 1:
        problems.append(
            _problem("PLAN_SCHEMA_VERSION", "schema_version must be the integer 1")
        )
    if plan.get("repository") != REPOSITORY:
        problems.append(_problem("PLAN_REPOSITORY", f"repository must be {REPOSITORY!r}"))
    if not _is_stable_id(plan.get("plan_id")):
        problems.append(
            _problem(
                "PLAN_ID",
                "plan_id must start with a letter and contain only A-Z, 0-9, _ (max 128)",
            )
        )
    if not _is_nonempty_text(plan.get("goal")):
        problems.append(_problem("PLAN_GOAL", "goal must be nonempty text"))
    exclusions = plan.get("exclusions")
    if (
        not isinstance(exclusions, list)
        or not exclusions
        or not all(_is_nonempty_text(item) for item in exclusions)
    ):
        problems.append(
            _problem(
                "PLAN_EXCLUSIONS",
                "exclusions must be a nonempty array of nonempty text",
            )
        )

    tasks = plan.get("tasks")
    if not isinstance(tasks, list) or not tasks or len(tasks) > MAX_TASKS:
        problems.append(
            _problem(
                "PLAN_TASKS",
                f"tasks must be a nonempty array of at most {MAX_TASKS} tasks",
            )
        )
        tasks = None

    by_id: dict[str, dict[str, Any]] = {}
    branches: dict[str, str] = {}
    if isinstance(tasks, list):
        for index, task in enumerate(tasks):
            label = f"tasks[{index}]"
            if not isinstance(task, dict):
                problems.append(_problem("TASK_SHAPE", f"{label} must be an object"))
                continue
            for field in sorted(set(task.keys()) - _TASK_FIELDS):
                problems.append(
                    _problem("TASK_UNKNOWN_FIELD", f"{label} has unknown field: {field}")
                )
            task_id = task.get("task_id")
            if not _is_stable_id(task_id):
                problems.append(
                    _problem("TASK_ID", f"{label} has an invalid task_id")
                )
                continue
            assert isinstance(task_id, str)
            if task_id in by_id:
                problems.append(
                    _problem("TASK_DUPLICATE_ID", f"duplicate task_id: {task_id}")
                )
                continue
            by_id[task_id] = task
            branch = task.get("feature_branch")
            if not is_valid_branch(branch):
                problems.append(
                    _problem(
                        "TASK_BRANCH",
                        f"{task_id} has an invalid feature_branch (or reserved 'main')",
                    )
                )
            elif branch in branches:
                problems.append(
                    _problem(
                        "TASK_DUPLICATE_BRANCH",
                        f"duplicate feature_branch: {branch}",
                    )
                )
            else:
                assert isinstance(branch, str)
                branches[branch] = task_id
            if not _is_nonempty_text(task.get("outcome")):
                problems.append(
                    _problem("TASK_OUTCOME", f"{task_id} outcome must be nonempty text")
                )
            if not _is_nonempty_text(task.get("observable_behavior")):
                problems.append(
                    _problem(
                        "TASK_BEHAVIOR",
                        f"{task_id} observable_behavior must be nonempty text",
                    )
                )
            owned = task.get("owned_paths")
            if (
                not isinstance(owned, list)
                or not owned
                or not all(isinstance(item, str) for item in owned)
            ):
                problems.append(
                    _problem(
                        "TASK_PATHS",
                        f"{task_id} owned_paths must be a nonempty array of paths",
                    )
                )
            else:
                for item in owned:
                    violation = path_violation(item)
                    if violation is not None:
                        problems.append(
                            _problem("TASK_PATH", f"{task_id}: {violation}: {item!r}")
                        )
            evidence = task.get("acceptance_evidence")
            if (
                not isinstance(evidence, list)
                or not evidence
                or not all(_is_nonempty_text(item) for item in evidence)
            ):
                problems.append(
                    _problem(
                        "TASK_EVIDENCE",
                        f"{task_id} acceptance_evidence must be a nonempty array",
                    )
                )
            if not _is_int(task.get("risk_tier")) or task.get("risk_tier") not in (1, 2, 3):
                problems.append(
                    _problem(
                        "TASK_RISK_TIER",
                        f"{task_id} risk_tier must be the integer 1, 2, or 3",
                    )
                )
            depends = task.get("depends_on")
            if not isinstance(depends, list) or not all(
                isinstance(item, str) for item in depends
            ):
                problems.append(
                    _problem(
                        "TASK_DEPENDS_SHAPE",
                        f"{task_id} depends_on must be an array of task IDs",
                    )
                )
            elif len(set(depends)) != len(depends):
                problems.append(
                    _problem("TASK_DEPENDS_DUPLICATE", f"{task_id} has duplicate dependencies")
                )
            unresolved = task.get("unresolved_design_questions")
            if not isinstance(unresolved, list) or unresolved:
                problems.append(
                    _problem(
                        "TASK_UNRESOLVED_DESIGN",
                        f"{task_id} unresolved_design_questions must be an empty array",
                    )
                )

    if isinstance(tasks, list) and by_id:
        for task_id, task in by_id.items():
            depends = task.get("depends_on")
            if not isinstance(depends, list):
                continue
            for dep in depends:
                if not isinstance(dep, str):
                    continue
                if dep == task_id:
                    problems.append(
                        _problem("TASK_DEPENDS_SELF", f"{task_id} depends on itself")
                    )
                elif dep not in by_id:
                    problems.append(
                        _problem(
                            "TASK_DEPENDS_MISSING",
                            f"{task_id} depends on unknown task {dep}",
                        )
                    )

    ordered: list[str] = []
    dep_problems = [p for p in problems if p["code"].startswith("TASK_DEPENDS")]
    if isinstance(tasks, list) and by_id and not dep_problems:
        pending = {task_id: set(t.get("depends_on", [])) for task_id, t in by_id.items()}
        ready = sorted(task_id for task_id, deps in pending.items() if not deps)
        while ready:
            current = ready.pop(0)
            ordered.append(current)
            for task_id, deps in pending.items():
                if current in deps:
                    deps.remove(current)
                    if not deps and task_id not in ordered and task_id not in ready:
                        ready.append(task_id)
            ready.sort()
        if len(ordered) != len(by_id):
            problems.append(
                _problem("TASK_DEPENDS_CYCLE", "depends_on contains a dependency cycle")
            )
            ordered = []

    if isinstance(tasks, list) and by_id and ordered:
        ancestors: dict[str, set[str]] = {}
        for task_id in ordered:
            direct = set(by_id[task_id].get("depends_on", []))
            closure = set(direct)
            for dep in direct:
                closure |= ancestors.get(dep, set())
            ancestors[task_id] = closure
        owners: dict[str, set[str]] = {}
        for task_id, task in by_id.items():
            owned = task.get("owned_paths")
            if isinstance(owned, list):
                for item in owned:
                    if isinstance(item, str) and path_violation(item) is None:
                        owners.setdefault(item, set()).add(task_id)
        for item in sorted(owners):
            holders = sorted(owners[item])
            for pos, first in enumerate(holders):
                for second in holders[pos + 1 :]:
                    related = second in ancestors.get(first, set()) or first in ancestors.get(
                        second, set()
                    )
                    if not related:
                        problems.append(
                            _problem(
                                "TASK_OVERLAPPING_PATHS",
                                f"shared owned path {item!r} requires sequencing "
                                f"between {first} and {second}",
                            )
                        )
                        break
                else:
                    continue
                break

    if problems:
        return False, plan_id, [], problems
    assert isinstance(plan, dict)
    return True, plan_id, ordered, []


def validate_file(path: Path) -> tuple[dict[str, Any], int]:
    """Validate the plan file at *path*; return ``(result, exit_code)``.

    Every return path yields a structured JSON result: no input, however
    malformed, deeply nested, or unrepresentable, escapes as an empty stdout
    or a traceback. The read itself is bounded to ``MAX_PLAN_BYTES + 1``
    bytes, and the bound is enforced on the bytes actually read, so growth
    between any size check and the read cannot exceed it.
    """

    def _unreadable() -> tuple[dict[str, Any], int]:
        return (
            _result(
                None,
                False,
                None,
                [],
                [_problem("INPUT_UNREADABLE", f"cannot read plan file: {path}")],
            ),
            3,
        )

    try:
        with path.open("rb") as handle:
            raw = handle.read(MAX_PLAN_BYTES + 1)
    except OSError:
        return _unreadable()
    if len(raw) > MAX_PLAN_BYTES:
        return (
            _result(
                None,
                False,
                None,
                [],
                [_problem("INPUT_OVERSIZED", "plan file exceeds 1 MiB")],
            ),
            3,
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return (
            _result(
                None, False, None, [], [_problem("INPUT_ENCODING", "plan file is not UTF-8")]
            ),
            3,
        )
    try:
        try:
            parsed = json.loads(text, object_pairs_hook=_no_duplicate_object)
        except _DuplicateKeyError as exc:
            return (
                _result(
                    None,
                    False,
                    None,
                    [],
                    [_problem("INPUT_DUPLICATE_KEYS", f"duplicate JSON key: {exc}")],
                ),
                3,
            )
        except json.JSONDecodeError as exc:
            return (
                _result(
                    None,
                    False,
                    None,
                    [],
                    [_problem("INPUT_MALFORMED", f"plan file is not valid JSON: {exc.msg}")],
                ),
                3,
            )
        if not isinstance(parsed, dict):
            return (
                _result(
                    None,
                    False,
                    None,
                    [],
                    [_problem("PLAN_TOP_LEVEL", "plan must be a JSON object")],
                ),
                2,
            )
        valid, plan_id, ordered, problems = validate_plan_object(parsed)
        if not valid:
            return _result(plan_id, False, None, [], problems), 2
        try:
            digest = canonical_digest(parsed)
        except Exception:  # noqa: BLE001 - unrepresentable text stays structured
            return (
                _result(
                    plan_id,
                    False,
                    None,
                    [],
                    [
                        _problem(
                            "INPUT_UNENCODABLE",
                            "plan contains text that cannot be represented as UTF-8",
                        )
                    ],
                ),
                3,
            )
        return _result(plan_id, True, digest, ordered, []), 0
    except Exception as exc:  # noqa: BLE001 - bounded structured failure, no traceback
        print(f"work_plan: {type(exc).__name__} while validating plan", file=sys.stderr)
        return (
            _result(
                None,
                False,
                None,
                [],
                [_problem("INPUT_UNBOUNDED", "plan input could not be processed")],
            ),
            3,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mip.execution.work_plan",
        description="Validate a read-only MIP bounded work plan (proposal only).",
    )
    sub = parser.add_subparsers(dest="command", required=True)
    cmd = sub.add_parser("validate", help="validate a plan file and print the JSON result")
    cmd.add_argument("--plan", required=True, help="path to the plan JSON file")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command != "validate":
        print("work_plan: unknown command", file=sys.stderr)
        return 2
    try:
        result, code = validate_file(Path(args.plan))
    except Exception as exc:  # noqa: BLE001 - never leak tracebacks or secrets
        print(f"work_plan: internal error ({type(exc).__name__})", file=sys.stderr)
        return 3
    print(json.dumps(result))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
