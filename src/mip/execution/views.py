"""Deterministic generated lifecycle views for stable execution documents."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from mip.execution.errors import TaskControlError

BEGIN_MARKER = "<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->"
END_MARKER = "<!-- END MIP TASKCTL EXECUTION VIEW -->"


def _display(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)


def render_execution_view(state: Mapping[str, Any], *, document: str) -> str:
    """Render the canonical lifecycle snapshot for one stable document."""

    if document not in {"active_task", "completion_report"}:
        raise TaskControlError("E_VIEW_DOCUMENT", f"unsupported document kind: {document}")
    title = "# Active Task" if document == "active_task" else "# Execution Completion Report"
    blockers = state["blockers"]
    blocker_text = "none" if not blockers else ", ".join(blockers)
    fields = (
        ("Task ID", state["task_id"]),
        ("Repository", state["repository"]),
        ("Execution mode", state["execution_mode"]),
        ("Base SHA", state["base_sha"]),
        ("Authorization provenance", state["authorization_head_sha"]),
        ("Feature branch", state["feature_branch"]),
        ("Feature branch created", state["feature_branch_created"]),
        ("Task execution authorized", state["task_execution_authorized"]),
        ("Correction execution authorized", state["correction_execution_authorized"]),
        ("Merge authorized", state["merge_authorized"]),
        ("PR creation authorized", state["pr_creation_authorized"]),
        ("Implementation commit", state["implementation_commit_sha"]),
        ("Reviewed head", state["reviewed_head_sha"]),
        ("Rejected review head", state["rejected_review_head_sha"]),
        ("Rejected implementation commit", state["rejected_implementation_commit_sha"]),
        ("Approval commit", state["approval_commit_sha"]),
        ("Blockers", blocker_text),
        ("Maximum correction cycles", state["maximum_correction_cycles"]),
        ("Correction cycles completed", state["correction_cycles_completed"]),
        ("Correction cycles remaining", state["correction_cycles_remaining"]),
        ("Review decision", state["review_decision"]),
        ("Local feature-branch cleanup", state.get("local_feature_branch_cleanup")),
        ("Remote feature-branch cleanup", state.get("remote_feature_branch_cleanup")),
        ("Capability authorizations changed", state["capability_authorizations_changed"]),
    )
    status_line = (
        f"**Status:** {state['status']}"
        if document == "active_task"
        else f"**Current decision:** `{state['status']}`"
    )
    lines = [
        BEGIN_MARKER,
        title,
        "",
        status_line,
        "",
        "_Generated from `EXECUTION_STATE.json`; do not edit._",
        "",
    ]
    lines.extend(f"- **{label}:** `{_display(value)}`" for label, value in fields)
    lines.extend((END_MARKER, ""))
    return "\n".join(lines)


def replace_execution_view(text: str, block: str) -> str:
    """Replace exactly one well-formed, non-nested generated block."""

    if text.count(BEGIN_MARKER) != 1 or text.count(END_MARKER) != 1:
        raise TaskControlError(
            "E_VIEW_MARKERS",
            "document must contain exactly one begin marker and one end marker",
        )
    begin = text.index(BEGIN_MARKER)
    end = text.index(END_MARKER)
    if end < begin:
        raise TaskControlError("E_VIEW_MARKERS", "generated markers are reversed")
    inner = text[begin + len(BEGIN_MARKER) : end]
    if BEGIN_MARKER in inner or END_MARKER in inner:
        raise TaskControlError("E_VIEW_MARKERS", "generated markers cannot be nested")
    suffix = end + len(END_MARKER)
    if suffix < len(text) and text[suffix] == "\n":
        suffix += 1
    return text[:begin] + block + text[suffix:]


def assert_execution_view(text: str, expected: str, *, document: str) -> None:
    """Require byte-equivalent generated content."""

    actual = replace_execution_view(text, expected)
    if actual != text:
        raise TaskControlError(
            "E_VIEW_DIVERGENCE",
            f"{document} generated execution view differs from canonical state",
        )
