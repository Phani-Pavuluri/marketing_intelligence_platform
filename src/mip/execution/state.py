"""Canonical MIP repository execution-state validation and transitions."""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping, Sequence
from typing import Any, NoReturn

from mip.execution.errors import TaskControlError

ALLOWED_STATUSES = frozenset(
    {
        "idle",
        "proposed",
        "authorized",
        "in_progress",
        "blocked",
        "ready_for_review",
        "changes_requested",
        "merged",
        "superseded",
    }
)

TRANSITIONS: Mapping[str, frozenset[str]] = {
    "idle": frozenset(),
    "proposed": frozenset({"authorized", "superseded"}),
    "authorized": frozenset({"in_progress", "blocked", "ready_for_review", "superseded"}),
    "in_progress": frozenset({"blocked", "ready_for_review", "superseded"}),
    "blocked": frozenset({"in_progress", "ready_for_review", "superseded"}),
    "ready_for_review": frozenset({"changes_requested", "merged"}),
    "changes_requested": frozenset(
        {"in_progress", "blocked", "ready_for_review", "superseded"}
    ),
    "merged": frozenset(),
    "superseded": frozenset(),
}

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*$")

CORE_BOOLEAN_FIELDS = (
    "task_execution_authorized",
    "correction_execution_authorized",
    "merge_authorized",
    "pr_creation_authorized",
    "capability_authorizations_changed",
)
SHA_FIELDS = (
    "base_sha",
    "task_authoring_head_sha",
    "authorization_head_sha",
    "reviewed_head_sha",
    "rejected_review_head_sha",
    "implementation_commit_sha",
    "rejected_implementation_commit_sha",
    "approval_commit_sha",
)
PROTECTED_AUTHORITY_FIELDS = frozenset(
    {
        "capability_authorizations_changed",
        "coordination_refresh_authorized",
        "product_or_analytical_changes_authorized",
        "geox_certification_authorized",
        "mmm_implementation_authorized",
        "mip_bridge_resume_authorized",
        "calibration_signal_construction_authorized",
        "simulation_authorized",
        "optimization_authorized",
        "planning_authorized",
        "recommendation_authorized",
        "runtime_integration_authorized",
        "real_data_authorized",
        "pilot_authorized",
        "production_authorized",
        "next_task_authorized",
    }
)


def _fail(code: str, message: str) -> NoReturn:
    raise TaskControlError(code, message)


def _require_bool(state: Mapping[str, Any], field: str) -> bool:
    value = state.get(field)
    if not isinstance(value, bool):
        _fail("E_STATE_BOOLEAN", f"{field} must be boolean")
    return value


def _require_sha_or_null(state: Mapping[str, Any], field: str) -> str | None:
    value = state.get(field)
    if value is not None and (not isinstance(value, str) or SHA_RE.fullmatch(value) is None):
        _fail("E_STATE_SHA", f"{field} must be a 40-character lowercase SHA or null")
    return value


def _require_sha(state: Mapping[str, Any], field: str) -> str:
    value = _require_sha_or_null(state, field)
    if value is None:
        _fail("E_STATE_SHA_REQUIRED", f"{field} is required")
    return value


def _require_null(state: Mapping[str, Any], field: str, status: str) -> None:
    if state.get(field) is not None:
        _fail("E_STATE_STATUS_EVIDENCE", f"{field} must be null for {status}")


def _require_nonnegative_int(state: Mapping[str, Any], field: str) -> int:
    value = state.get(field)
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        _fail("E_STATE_CORRECTION_COUNTER", f"{field} must be a non-negative integer")
    return value


def validate_state(state: Mapping[str, Any]) -> None:
    """Validate the canonical V2 lifecycle state or raise a stable typed failure."""

    if state.get("schema_version") != "mip_repo_execution_state_v2":
        _fail("E_STATE_SCHEMA", "schema_version must be mip_repo_execution_state_v2")

    status = state.get("status")
    if not isinstance(status, str) or status not in ALLOWED_STATUSES:
        _fail("E_STATE_STATUS", f"unsupported lifecycle status: {status!r}")

    for field in ("repository", "task_id", "execution_mode", "feature_branch"):
        if not isinstance(state.get(field), str) or not state[field].strip():
            _fail("E_STATE_REQUIRED_FIELD", f"{field} must be a non-empty string")
    if state["repository"] != "Phani-Pavuluri/marketing_intelligence_platform":
        _fail("E_STATE_REPOSITORY", "canonical state belongs to a different repository")
    if state["execution_mode"] != "branch_and_fast_forward":
        _fail("E_STATE_EXECUTION_MODE", "unsupported execution_mode")
    if state.get("review_decision") != status:
        _fail("E_STATE_REVIEW_DECISION", "review_decision must match status")

    for field in CORE_BOOLEAN_FIELDS:
        _require_bool(state, field)
    _require_bool(state, "feature_branch_created")
    for field in SHA_FIELDS:
        _require_sha_or_null(state, field)
    _require_sha(state, "base_sha")

    authorization_head = state.get("authorization_head_sha")
    if status not in {"idle", "proposed", "superseded"} or authorization_head is not None:
        _require_sha(state, "authorization_head_sha")
        _require_sha(state, "task_authoring_head_sha")

    branch = state.get("feature_branch")
    if (
        not isinstance(branch, str)
        or branch == "main"
        or BRANCH_RE.fullmatch(branch) is None
        or ".." in branch
        or branch.endswith("/")
    ):
        _fail("E_STATE_BRANCH", "feature_branch is not a valid non-main branch identity")

    blockers = state.get("blockers")
    if (
        not isinstance(blockers, list)
        or any(not isinstance(item, str) or not item.strip() for item in blockers)
        or len(set(blockers)) != len(blockers)
    ):
        _fail("E_STATE_BLOCKERS", "blockers must be a unique list of non-empty strings")

    maximum, completed, remaining = (
        _require_nonnegative_int(state, "maximum_correction_cycles"),
        _require_nonnegative_int(state, "correction_cycles_completed"),
        _require_nonnegative_int(state, "correction_cycles_remaining"),
    )
    if completed + remaining != maximum:
        _fail(
            "E_STATE_CORRECTION_COUNTER",
            "correction_cycles_completed + correction_cycles_remaining must equal maximum",
        )

    if state["merge_authorized"]:
        _fail("E_STATE_MERGE_AUTHORITY", "persisted merge_authorized must remain false")
    if state["pr_creation_authorized"]:
        _fail("E_STATE_PR_AUTHORITY", "PR creation is not authorized by lifecycle state")
    if state["approval_commit_sha"] is not None:
        _fail("E_STATE_APPROVAL_PERSISTENCE", "approval_commit_sha must remain null in V2")
    if state["capability_authorizations_changed"]:
        _fail("E_STATE_CAPABILITY_AUTHORITY", "lifecycle state cannot grant capability authority")

    rejected_pair = (
        state["rejected_review_head_sha"],
        state["rejected_implementation_commit_sha"],
    )
    if (rejected_pair[0] is None) != (rejected_pair[1] is None):
        _fail("E_STATE_REJECTED_PROVENANCE", "rejected review provenance must be a complete pair")

    if status == "proposed":
        if state["task_execution_authorized"]:
            _fail("E_STATE_PROPOSED_AUTHORITY", "proposed is non-executable")
        for field in ("implementation_commit_sha", "reviewed_head_sha", "rejected_review_head_sha"):
            _require_null(state, field, status)
    elif status == "authorized":
        if not state["task_execution_authorized"] or blockers:
            _fail("E_STATE_EXECUTABLE", f"{status} requires execution authority and no blockers")
        for field in ("implementation_commit_sha", "reviewed_head_sha", "rejected_review_head_sha"):
            _require_null(state, field, status)
    elif status == "in_progress":
        if not state["task_execution_authorized"] or blockers:
            _fail("E_STATE_EXECUTABLE", "in_progress requires execution authority and no blockers")
        _require_null(state, "reviewed_head_sha", status)
    elif status == "blocked":
        if not state["task_execution_authorized"] or not blockers:
            _fail("E_STATE_BLOCKED", "blocked requires execution authority and blockers")
        _require_null(state, "reviewed_head_sha", status)
    elif status == "ready_for_review":
        if not state["task_execution_authorized"] or blockers:
            _fail("E_STATE_READY", "ready_for_review requires execution authority and no blockers")
        _require_sha(state, "implementation_commit_sha")
        _require_null(state, "reviewed_head_sha", status)
        if state["correction_execution_authorized"]:
            _fail("E_STATE_READY", "ready_for_review cannot retain correction authority")
    elif status == "changes_requested":
        if not state["task_execution_authorized"] or not state["correction_execution_authorized"]:
            _fail("E_STATE_CORRECTION_AUTHORITY", "changes_requested requires correction authority")
        _require_sha(state, "implementation_commit_sha")
        _require_sha(state, "rejected_review_head_sha")
        _require_sha(state, "rejected_implementation_commit_sha")
        if remaining == 0:
            _fail(
                "E_STATE_CORRECTION_BUDGET",
                "changes_requested requires remaining correction budget",
            )
        _require_null(state, "reviewed_head_sha", status)
    elif status == "merged":
        if (
            state["task_execution_authorized"]
            or state["correction_execution_authorized"]
            or blockers
        ):
            _fail("E_STATE_MERGED_AUTHORITY", "merged requires closed authority and no blockers")
        _require_sha(state, "implementation_commit_sha")
        _require_sha(state, "reviewed_head_sha")
        if state.get("feature_branch_created") is not False:
            _fail("E_STATE_CLEANUP", "merged requires feature_branch_created=false")
        for field in ("local_feature_branch_cleanup", "remote_feature_branch_cleanup"):
            if state.get(field) != "observed_deleted":
                _fail("E_STATE_CLEANUP", f"merged requires {field}=observed_deleted")
    elif status in {"idle", "superseded"}:
        if state["task_execution_authorized"] or state["correction_execution_authorized"]:
            _fail("E_STATE_CLOSED_AUTHORITY", f"{status} cannot retain execution authority")


def transition_state(
    state: Mapping[str, Any],
    target: str,
    *,
    implementation_sha: str | None = None,
    rejected_review_sha: str | None = None,
    rejected_implementation_sha: str | None = None,
    reviewed_head_sha: str | None = None,
    blockers: Sequence[str] = (),
    clear_blockers: bool = False,
    authorize_execution: bool = False,
    authorize_correction: bool = False,
    complete_correction: bool = False,
    authorization_head_sha: str | None = None,
    task_authoring_head_sha: str | None = None,
    local_branch_cleanup: str | None = None,
    remote_branch_cleanup: str | None = None,
) -> dict[str, Any]:
    """Return a validated candidate lifecycle state for an explicit transition."""

    validate_state(state)
    current = state["status"]
    if target not in ALLOWED_STATUSES:
        _fail("E_TRANSITION_TARGET", f"unsupported target status: {target}")
    if target not in TRANSITIONS[current]:
        _fail("E_TRANSITION_EDGE", f"transition {current} -> {target} is not allowed")

    candidate = copy.deepcopy(dict(state))
    candidate["status"] = target
    candidate["review_decision"] = target
    if clear_blockers:
        candidate["blockers"] = []
    if blockers:
        candidate["blockers"] = list(blockers)
    if implementation_sha is not None:
        candidate["implementation_commit_sha"] = implementation_sha

    if target == "authorized":
        if not authorize_execution:
            _fail("E_TRANSITION_AUTHORITY", "authorized requires --authorize-execution")
        if authorization_head_sha is None or task_authoring_head_sha is None:
            _fail(
                "E_TRANSITION_EVIDENCE",
                "authorized requires explicit authorization and task-authoring SHAs",
            )
        candidate["task_execution_authorized"] = True
        candidate["authorization_head_sha"] = authorization_head_sha
        candidate["task_authoring_head_sha"] = task_authoring_head_sha
    elif target == "in_progress":
        pass
    elif target == "blocked":
        if not blockers:
            _fail("E_TRANSITION_BLOCKER", "blocked requires at least one explicit --blocker")
    elif target == "ready_for_review":
        if implementation_sha is None:
            _fail("E_TRANSITION_EVIDENCE", "ready_for_review requires --implementation-sha")
        if state.get("blockers") and not clear_blockers:
            _fail("E_TRANSITION_BLOCKER", "use --clear-blockers explicitly before review")
        candidate["blockers"] = []
        candidate["correction_execution_authorized"] = False
        if current == "changes_requested":
            if not complete_correction:
                _fail(
                    "E_TRANSITION_CORRECTION_COUNTER",
                    "corrected review publication requires --complete-correction",
                )
            candidate["correction_cycles_completed"] += 1
            candidate["correction_cycles_remaining"] -= 1
    elif target == "changes_requested":
        if not authorize_correction:
            _fail("E_TRANSITION_AUTHORITY", "changes_requested requires --authorize-correction")
        if rejected_review_sha is None or rejected_implementation_sha is None:
            _fail(
                "E_TRANSITION_EVIDENCE",
                "changes_requested requires rejected review and implementation SHAs",
            )
        candidate["rejected_review_head_sha"] = rejected_review_sha
        candidate["rejected_implementation_commit_sha"] = rejected_implementation_sha
        candidate["correction_execution_authorized"] = True
    elif target == "merged":
        if reviewed_head_sha is None:
            _fail("E_TRANSITION_EVIDENCE", "merged requires --reviewed-head-sha")
        if local_branch_cleanup is None or remote_branch_cleanup is None:
            _fail("E_TRANSITION_EVIDENCE", "merged requires explicit branch cleanup evidence")
        candidate["reviewed_head_sha"] = reviewed_head_sha
        candidate["task_execution_authorized"] = False
        candidate["correction_execution_authorized"] = False
        candidate["feature_branch_created"] = False
        candidate["local_feature_branch_cleanup"] = local_branch_cleanup
        candidate["remote_feature_branch_cleanup"] = remote_branch_cleanup
    elif target == "superseded":
        candidate["task_execution_authorized"] = False
        candidate["correction_execution_authorized"] = False

    for field in PROTECTED_AUTHORITY_FIELDS:
        if candidate.get(field) != state.get(field):
            _fail("E_TRANSITION_CAPABILITY_AUTHORITY", f"transition cannot change {field}")

    validate_state(candidate)
    return candidate
