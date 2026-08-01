#!/usr/bin/env python3
"""Resolve the canonical MIP active task from origin/main, fail closed by default."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn, cast

ALLOWED_STATUSES = {
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
MAIN_ONLY_STATUSES = {"idle", "proposed", "merged", "superseded"}
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
LOCAL_ONLY_PREFIXES = (".codex/", "docs/tasks/")
DEFAULT_REPOSITORY = "Phani-Pavuluri/marketing_intelligence_platform"
STATE_PATH = "docs/execution/EXECUTION_STATE.json"
ACTIVE_PATH = "docs/execution/ACTIVE_TASK.md"
REPORT_PATH = "docs/execution/LATEST_COMPLETION_REPORT.md"

# A branch is permitted to move only through one of these explicit transitions.
TRANSITIONS: dict[tuple[str, str], str] = {
    ("authorized", "authorized"): "task",
    ("authorized", "in_progress"): "task",
    ("authorized", "blocked"): "resumption",
    ("authorized", "changes_requested"): "correction",
    ("authorized", "ready_for_review"): "review",
    ("ready_for_review", "ready_for_review"): "review",
    ("blocked", "blocked"): "resumption",
    ("blocked", "in_progress"): "resumption",
    ("changes_requested", "changes_requested"): "correction",
    ("changes_requested", "in_progress"): "correction",
    ("changes_requested", "blocked"): "resumption",
    # Publishing a completed correction for review is the terminal correction
    # transition; it does not grant merge or product authority.
    ("changes_requested", "ready_for_review"): "review",
}

REQUIRED_STRING_FIELDS = (
    "schema_version",
    "repository",
    "task_id",
    "execution_mode",
    "base_branch",
    "base_sha",
    "authorization_head_sha",
    "feature_branch",
    "task_path",
    "completion_report_path",
)
REQUIRED_BOOLEAN_FIELDS = (
    "task_execution_authorized",
    "correction_execution_authorized",
    "merge_authorized",
    "pr_creation_authorized",
    "capability_authorizations_changed",
)
SHA_FIELDS = ("base_sha", "authorization_head_sha")
NULLABLE_SHA_FIELDS = ("reviewed_head_sha", "implementation_commit_sha", "approval_commit_sha")
FIXED_INVARIANT_FIELDS = (
    "schema_version",
    "repository",
    "task_id",
    "execution_mode",
    "base_branch",
    "base_sha",
    "authorization_head_sha",
    "feature_branch",
    "task_path",
    "completion_report_path",
    "capability_authorizations_changed",
)
OPTIONAL_INVARIANT_FIELDS = (
    "affected_repositories",
    "mmm_resolver_adoption_authorized",
    "geox_resolver_adoption_authorized",
    "geox_active_builder_must_remain_unmodified",
)


@dataclass(frozen=True)
class Resolution:
    outcome: str
    reason_code: str
    repository: str
    task_id: str
    status: str
    feature_branch: str | None
    main_sha: str
    branch_sha: str | None
    local_branch_action: str

    def as_dict(self) -> dict[str, str | None]:
        return {
            "branch_sha": self.branch_sha,
            "feature_branch": self.feature_branch,
            "local_branch_action": self.local_branch_action,
            "main_sha": self.main_sha,
            "outcome": self.outcome,
            "reason_code": self.reason_code,
            "repository": self.repository,
            "status": self.status,
            "task_id": self.task_id,
        }


class ResolverError(RuntimeError):
    """A deterministic reason why the resolver refuses to continue."""

    def __init__(self, reason_code: str, detail: str) -> None:
        super().__init__(f"{reason_code}: {detail}")
        self.reason_code = reason_code
        self.detail = detail


def _fail(reason_code: str, detail: str) -> NoReturn:
    raise ResolverError(reason_code, detail)


def _run(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args], check=False, text=True, capture_output=True
    )
    if check and result.returncode != 0:
        _fail("git_command_failed", f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def _git_succeeds(repo: Path, *args: str) -> bool:
    return (
        subprocess.run(
            ["git", "-C", str(repo), *args],
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def _repository_root(repo: Path) -> Path:
    return Path(_run(repo, "rev-parse", "--show-toplevel"))


def _is_local_only(path: str) -> bool:
    normalized = path.rstrip("/")
    return normalized in {".codex", "docs/tasks"} or path.startswith(LOCAL_ONLY_PREFIXES)


def _validate_worktree(repo: Path) -> None:
    for line in _run(repo, "status", "--porcelain=v1", "--untracked-files=all").splitlines():
        code, path = line[:2], line[3:]
        if code == "??" and _is_local_only(path):
            continue
        if code == "??":
            _fail("unexpected_untracked_path", path)
        _fail("dirty_tracked_worktree", line)


def _origin_matches(repo: Path, expected_repository: str) -> None:
    origin_url = _run(repo, "remote", "get-url", "origin")
    normalized = origin_url.removesuffix(".git").rstrip("/")
    if not (
        normalized.endswith(f"/{expected_repository}")
        or normalized.endswith(f":{expected_repository}")
    ):
        _fail("wrong_origin", f"expected {expected_repository}, got {origin_url}")


def _fetch_and_hydrate(repo: Path) -> None:
    _run(repo, "fetch", "--prune", "origin")
    if _run(repo, "rev-parse", "--is-shallow-repository") == "true":
        _run(repo, "fetch", "--unshallow", "origin")


def _synchronize_main(repo: Path) -> str:
    _run(repo, "switch", "main")
    try:
        _run(repo, "pull", "--ff-only", "origin", "main")
    except ResolverError as error:
        _fail("stale_or_diverged_main", error.detail)
    main_sha, remote_sha = _run(repo, "rev-parse", "main"), _run(repo, "rev-parse", "origin/main")
    if main_sha != remote_sha:
        _fail("stale_or_diverged_main", "local main does not equal origin/main")
    return main_sha


def _read_json_from_ref(repo: Path, ref: str, path: str) -> dict[str, object]:
    try:
        payload = _run(repo, "show", f"{ref}:{path}")
    except ResolverError as error:
        _fail("missing_execution_state", f"{ref}:{path}: {error.detail}")
    try:
        parsed = json.loads(payload)
    except json.JSONDecodeError as error:
        _fail("invalid_execution_state_json", str(error))
    if not isinstance(parsed, dict):
        _fail("invalid_execution_state_json", "state must be an object")
    return cast(dict[str, object], parsed)


def _required_string(state: dict[str, object], key: str) -> str:
    value = state.get(key)
    if not isinstance(value, str) or not value:
        _fail("missing_required_field", key)
    return value


def _validate_path(value: str, key: str) -> None:
    if value.startswith("/") or ".." in Path(value).parts:
        _fail("invalid_execution_path", key)


def _validate_state(state: dict[str, object], expected_repository: str) -> None:
    for key in REQUIRED_STRING_FIELDS:
        _required_string(state, key)
    if state["schema_version"] != "mip_repo_execution_state_v2":
        _fail("invalid_schema_version", str(state["schema_version"]))
    if state["repository"] != expected_repository:
        _fail("repository_identity_mismatch", str(state["repository"]))
    if state.get("status") not in ALLOWED_STATUSES:
        _fail("invalid_status", str(state.get("status")))
    for key in REQUIRED_BOOLEAN_FIELDS:
        if not isinstance(state.get(key), bool):
            _fail("invalid_authorization_boolean", key)
    for key in SHA_FIELDS:
        if not SHA_PATTERN.fullmatch(_required_string(state, key)):
            _fail("invalid_sha_field", key)
    for key in NULLABLE_SHA_FIELDS:
        value = state.get(key)
        if value is not None and (not isinstance(value, str) or not SHA_PATTERN.fullmatch(value)):
            _fail("invalid_nullable_sha_field", key)
    for key in ("task_path", "completion_report_path"):
        _validate_path(_required_string(state, key), key)
    if not isinstance(state.get("blockers"), list) or not all(
        isinstance(item, str) for item in state["blockers"]
    ):
        _fail("invalid_blockers", "blockers")
    affected = state.get("affected_repositories")
    if affected is not None and (
        not isinstance(affected, list) or not all(isinstance(item, str) for item in affected)
    ):
        _fail("invalid_affected_repositories", "affected_repositories")
    for key in OPTIONAL_INVARIANT_FIELDS[1:]:
        if key in state and not isinstance(state[key], bool):
            _fail("invalid_authorization_boolean", key)
    status = str(state["status"])
    if status != "merged":
        if state["merge_authorized"] or state["pr_creation_authorized"]:
            _fail("unauthorized_merge_or_pr", status)
        if state["reviewed_head_sha"] is not None or state["approval_commit_sha"] is not None:
            _fail("premature_approval_metadata", status)
    if status == "ready_for_review":
        if state.get("implementation_commit_sha") is None:
            _fail(
                "invalid_implementation_sha", "ready_for_review requires implementation_commit_sha"
            )
    if status in MAIN_ONLY_STATUSES and (
        state["task_execution_authorized"] or state["correction_execution_authorized"]
    ):
        _fail("non_executable_authorization", status)


def _validate_human_views(
    repo: Path, ref: str, state: dict[str, object], branch_ref: str | None = None
) -> None:
    try:
        active = _run(repo, "show", f"{ref}:{ACTIVE_PATH}")
        report = _run(repo, "show", f"{ref}:{REPORT_PATH}")
    except ResolverError as error:
        _fail("missing_human_view", error.detail)
    status = str(state["status"])
    active_statuses = re.findall(r"^\*\*Status:\*\*\s+([a-z_]+)\s*$", active, flags=re.MULTILINE)
    report_statuses = re.findall(
        r"^- \*\*Current decision:\*\* `([a-z_]+)`\s*$", report, flags=re.MULTILINE
    )
    if status == "merged" and "ready_for_review" in active_statuses:
        _fail("contradictory_merged_closure_prose", "unlabeled ready_for_review status")
    if active_statuses != [status]:
        _fail("contradictory_active_task_status", f"expected one {status}")
    if report_statuses != [status]:
        _fail("contradictory_completion_report_decision", f"expected one {status}")
    task_id = str(state["task_id"])
    if task_id not in active or task_id not in report:
        _fail("human_task_id_mismatch", task_id)
    if status != "ready_for_review":
        return
    implementation = state.get("implementation_commit_sha")
    if not isinstance(implementation, str) or not SHA_PATTERN.fullmatch(implementation):
        _fail("invalid_implementation_sha", "ready_for_review implementation")
    if branch_ref is None:
        _fail("missing_remote_branch", "review state has no branch for implementation verification")
    if not _git_succeeds(repo, "cat-file", "-e", f"{implementation}^{{commit}}"):
        _fail("nonexistent_implementation_sha", implementation)
    if not _git_succeeds(repo, "merge-base", "--is-ancestor", implementation, branch_ref):
        _fail("implementation_sha_not_ancestral", implementation)
    if implementation not in active or implementation not in report:
        _fail("implementation_sha_human_mismatch", implementation)


def _branch_state_agrees(main_state: dict[str, object], branch_state: dict[str, object]) -> None:
    _validate_state(branch_state, str(main_state["repository"]))
    for key in FIXED_INVARIANT_FIELDS:
        if main_state.get(key) != branch_state.get(key):
            _fail("branch_state_mismatch", key)
    for key in OPTIONAL_INVARIANT_FIELDS:
        if (key in main_state or key in branch_state) and main_state.get(key) != branch_state.get(
            key
        ):
            _fail("branch_state_mismatch", key)
    for key in ("merge_authorized", "pr_creation_authorized", "capability_authorizations_changed"):
        if branch_state.get(key) is not False:
            _fail("branch_authority_escalation", key)
    if (
        branch_state.get("reviewed_head_sha") is not None
        or branch_state.get("approval_commit_sha") is not None
    ):
        _fail("branch_authority_escalation", "review metadata")


def _transition_mode(main_state: dict[str, object], branch_state: dict[str, object]) -> str:
    transition = (str(main_state["status"]), str(branch_state["status"]))
    mode = TRANSITIONS.get(transition)
    if mode is None:
        _fail("unsupported_lifecycle_transition", f"{transition[0]}->{transition[1]}")
    if mode == "task" and not bool(branch_state["task_execution_authorized"]):
        _fail("execution_not_authorized", "task_execution_authorized=false")
    if mode == "resumption" and not bool(
        branch_state["task_execution_authorized"] or branch_state["correction_execution_authorized"]
    ):
        _fail("execution_not_authorized", "blocked resumption lacks authorization")
    if mode == "correction" and not bool(branch_state["correction_execution_authorized"]):
        _fail("correction_not_authorized", "correction_execution_authorized=false")
    return mode


def _remote_feature(repo: Path, feature_branch: str) -> str:
    try:
        _run(repo, "fetch", "origin", feature_branch)
        return _run(repo, "rev-parse", f"origin/{feature_branch}")
    except ResolverError:
        _fail("missing_remote_branch", feature_branch)


def _validate_authorization_head(repo: Path, state: dict[str, object], branch_sha: str) -> None:
    authorization_head = _required_string(state, "authorization_head_sha")
    if not SHA_PATTERN.fullmatch(authorization_head):
        _fail("invalid_authorization_head", authorization_head)
    if not _git_succeeds(repo, "cat-file", "-e", f"{authorization_head}^{{commit}}"):
        _fail("nonexistent_authorization_head", authorization_head)
    if not _git_succeeds(repo, "merge-base", "--is-ancestor", authorization_head, branch_sha):
        _fail("authorization_head_not_ancestral", authorization_head)


def _checkout_exact_branch(repo: Path, feature_branch: str, branch_sha: str) -> str:
    local_exists = _git_succeeds(
        repo, "show-ref", "--verify", "--quiet", f"refs/heads/{feature_branch}"
    )
    if local_exists:
        local_sha = _run(repo, "rev-parse", feature_branch)
        if local_sha != branch_sha:
            _fail(
                "local_feature_branch_not_exact", f"{feature_branch}: {local_sha} != {branch_sha}"
            )
        _run(repo, "switch", feature_branch)
        return "used_existing_exact_tracking_branch"
    _run(repo, "switch", "--track", f"origin/{feature_branch}")
    if _run(repo, "rev-parse", "HEAD") != branch_sha:
        _fail("local_feature_branch_not_exact", feature_branch)
    return "created_exact_tracking_branch"


def resolve_active_task(repo: Path, expected_repository: str = DEFAULT_REPOSITORY) -> Resolution:
    root = _repository_root(repo)
    _validate_worktree(root)
    _origin_matches(root, expected_repository)
    _fetch_and_hydrate(root)
    main_sha = _synchronize_main(root)
    main_state = _read_json_from_ref(root, "origin/main", STATE_PATH)
    _validate_state(main_state, expected_repository)
    status, task_id = str(main_state["status"]), str(main_state["task_id"])
    if status != "ready_for_review":
        _validate_human_views(root, "origin/main", main_state)
    if status in MAIN_ONLY_STATUSES:
        return Resolution(
            "non_executable",
            "non_executable_state",
            expected_repository,
            task_id,
            status,
            None,
            main_sha,
            None,
            "stayed_on_main",
        )
    feature_branch = _required_string(main_state, "feature_branch")
    branch_sha = _remote_feature(root, feature_branch)
    _validate_authorization_head(root, main_state, branch_sha)
    branch_ref = f"origin/{feature_branch}"
    if status == "ready_for_review":
        _validate_human_views(root, "origin/main", main_state, branch_sha)
    branch_state = _read_json_from_ref(root, branch_ref, STATE_PATH)
    _branch_state_agrees(main_state, branch_state)
    _validate_human_views(root, branch_ref, branch_state, branch_sha)
    mode = _transition_mode(main_state, branch_state)
    if mode == "review":
        return Resolution(
            "review_only",
            "review_only_state",
            expected_repository,
            task_id,
            str(branch_state["status"]),
            feature_branch,
            main_sha,
            branch_sha,
            "stayed_on_main",
        )
    action = _checkout_exact_branch(root, feature_branch, branch_sha)
    return Resolution(
        "executable",
        "resolved",
        expected_repository,
        task_id,
        str(branch_state["status"]),
        feature_branch,
        main_sha,
        branch_sha,
        action,
    )


def _emit(resolution: Resolution, as_json: bool) -> None:
    if as_json:
        print(json.dumps(resolution.as_dict(), sort_keys=True))
    else:
        for key, value in resolution.as_dict().items():
            print(f"{key}: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--expected-repository", default=DEFAULT_REPOSITORY)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        _emit(resolve_active_task(args.repo, args.expected_repository), args.json)
    except ResolverError as error:
        payload = {"outcome": "blocked", "reason_code": error.reason_code, "detail": error.detail}
        print(
            json.dumps(payload, sort_keys=True)
            if args.json
            else f"outcome: blocked\nreason_code: {error.reason_code}\ndetail: {error.detail}"
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
