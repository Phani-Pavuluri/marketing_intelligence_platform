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
NON_EXECUTABLE_STATUSES = {"idle", "proposed", "merged", "superseded"}
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
LOCAL_ONLY_PREFIXES = (".codex/", "docs/tasks/")
DEFAULT_REPOSITORY = "Phani-Pavuluri/marketing_intelligence_platform"


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


def _run(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        text=True,
        capture_output=True,
    )
    if check and result.returncode != 0:
        raise ResolverError("git_command_failed", f"git {' '.join(args)}: {result.stderr.strip()}")
    return result.stdout.strip()


def _fail(reason_code: str, detail: str) -> NoReturn:
    raise ResolverError(reason_code, detail)


def _repository_root(repo: Path) -> Path:
    root = _run(repo, "rev-parse", "--show-toplevel")
    return Path(root)


def _is_local_only(path: str) -> bool:
    normalized = path.rstrip("/")
    return (
        normalized == ".codex" or normalized == "docs/tasks" or path.startswith(LOCAL_ONLY_PREFIXES)
    )


def _validate_worktree(repo: Path) -> None:
    status = _run(repo, "status", "--porcelain=v1", "--untracked-files=all")
    for line in status.splitlines():
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
    main_sha = _run(repo, "rev-parse", "main")
    if main_sha != _run(repo, "rev-parse", "origin/main"):
        _fail("stale_or_diverged_main", "local main does not equal origin/main")
    return main_sha


def _read_json_from_ref(repo: Path, ref: str, path: str) -> dict[str, object]:
    try:
        parsed = json.loads(_run(repo, "show", f"{ref}:{path}"))
    except json.JSONDecodeError as error:
        _fail("invalid_execution_state_json", str(error))
    if not isinstance(parsed, dict):
        _fail("invalid_execution_state_json", "state must be an object")
    return cast(dict[str, object], parsed)


def _validate_state(state: dict[str, object], expected_repository: str) -> None:
    required_strings = (
        "schema_version",
        "repository",
        "task_id",
        "status",
        "base_branch",
        "base_sha",
    )
    for key in required_strings:
        if not isinstance(state.get(key), str) or not state[key]:
            _fail("invalid_execution_state", f"missing or invalid {key}")
    if state["repository"] != expected_repository:
        _fail("repository_identity_mismatch", str(state["repository"]))
    if state["status"] not in ALLOWED_STATUSES:
        _fail("invalid_status", str(state["status"]))
    for key in ("task_execution_authorized", "correction_execution_authorized", "merge_authorized"):
        if not isinstance(state.get(key), bool):
            _fail("invalid_authorization_boolean", key)
    if state["status"] not in NON_EXECUTABLE_STATUSES | {"ready_for_review"}:
        feature_branch = state.get("feature_branch")
        authorization_head = state.get("authorization_head_sha")
        if not isinstance(feature_branch, str) or not feature_branch:
            _fail("missing_feature_branch", "resumable state has no feature branch")
        if not isinstance(authorization_head, str) or not SHA_PATTERN.fullmatch(authorization_head):
            _fail("invalid_authorization_head", "resumable state has no SHA")


def _is_executable(state: dict[str, object]) -> bool:
    status = state["status"]
    if status in {"authorized", "in_progress"}:
        return bool(state["task_execution_authorized"])
    if status in {"blocked", "changes_requested"}:
        return bool(state["task_execution_authorized"] or state["correction_execution_authorized"])
    return False


def _validate_human_views(
    repo: Path, ref: str, state: dict[str, object], branch_ref: str | None
) -> None:
    active = _run(repo, "show", f"{ref}:docs/execution/ACTIVE_TASK.md")
    report = _run(repo, "show", f"{ref}:docs/execution/LATEST_COMPLETION_REPORT.md")
    state_status = str(state["status"])
    active_statuses = re.findall(r"^\*\*Status:\*\*\s+([a-z_]+)\s*$", active, flags=re.MULTILINE)
    report_statuses = re.findall(
        r"^- \*\*Current decision:\*\* `([a-z_]+)`\s*$", report, flags=re.MULTILINE
    )
    if active_statuses != [state_status] or report_statuses != [state_status]:
        _fail(
            "contradictory_human_current_state",
            "stable Markdown must contain one matching current decision",
        )
    if str(state["task_id"]) not in active or str(state["task_id"]) not in report:
        _fail("human_task_id_mismatch", "task ID missing from stable Markdown")
    implementation_sha = state.get("implementation_commit_sha")
    if state_status == "ready_for_review":
        if not isinstance(implementation_sha, str) or not SHA_PATTERN.fullmatch(implementation_sha):
            _fail(
                "invalid_implementation_sha",
                "ready_for_review requires a full implementation SHA",
            )
        if branch_ref is None:
            _fail(
                "missing_remote_branch",
                "review state has no branch for implementation verification",
            )
        if (
            subprocess.run(
                ["git", "-C", str(repo), "cat-file", "-e", f"{implementation_sha}^{{commit}}"],
                check=False,
            ).returncode
            != 0
        ):
            _fail("invalid_implementation_sha", implementation_sha)
        if (
            subprocess.run(
                [
                    "git",
                    "-C",
                    str(repo),
                    "merge-base",
                    "--is-ancestor",
                    implementation_sha,
                    branch_ref,
                ],
                check=False,
            ).returncode
            != 0
        ):
            _fail("implementation_sha_not_ancestral", implementation_sha)
        if implementation_sha not in active or implementation_sha not in report:
            _fail("implementation_sha_human_mismatch", implementation_sha)


def _branch_state_agrees(main_state: dict[str, object], branch_state: dict[str, object]) -> None:
    for key in (
        "repository",
        "task_id",
        "feature_branch",
        "task_execution_authorized",
        "correction_execution_authorized",
    ):
        if main_state.get(key) != branch_state.get(key):
            _fail("branch_state_mismatch", key)
    _validate_state(branch_state, str(main_state["repository"]))


def resolve_active_task(repo: Path, expected_repository: str = DEFAULT_REPOSITORY) -> Resolution:
    root = _repository_root(repo)
    _validate_worktree(root)
    _origin_matches(root, expected_repository)
    _fetch_and_hydrate(root)
    main_sha = _synchronize_main(root)
    state = _read_json_from_ref(root, "origin/main", "docs/execution/EXECUTION_STATE.json")
    _validate_state(state, expected_repository)
    status = str(state["status"])
    task_id = str(state["task_id"])
    feature_value = state.get("feature_branch")
    feature_branch = feature_value if isinstance(feature_value, str) else None

    if status in NON_EXECUTABLE_STATUSES:
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
    if feature_branch is None:
        _fail("missing_feature_branch", "active state has no feature branch")

    try:
        _run(root, "fetch", "origin", feature_branch)
        branch_sha = _run(root, "rev-parse", f"origin/{feature_branch}")
    except ResolverError:
        _fail("missing_remote_branch", feature_branch)
    authorization_head = str(state["authorization_head_sha"])
    if (
        subprocess.run(
            ["git", "-C", str(root), "merge-base", "--is-ancestor", authorization_head, branch_sha],
            check=False,
        ).returncode
        != 0
    ):
        _fail("authorization_head_not_ancestral", authorization_head)
    branch_state = _read_json_from_ref(
        root,
        f"origin/{feature_branch}",
        "docs/execution/EXECUTION_STATE.json",
    )
    _branch_state_agrees(state, branch_state)
    branch_status = str(branch_state["status"])
    _validate_human_views(root, f"origin/{feature_branch}", branch_state, branch_sha)

    if status == "ready_for_review" or branch_status == "ready_for_review":
        return Resolution(
            "review_only",
            "review_only_state",
            expected_repository,
            task_id,
            branch_status,
            feature_branch,
            main_sha,
            branch_sha,
            "stayed_on_main",
        )
    if not _is_executable(state) or not _is_executable(branch_state):
        _fail("execution_not_authorized", f"main={status}, branch={branch_status}")

    local_branch_exists = (
        subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "show-ref",
                "--verify",
                "--quiet",
                f"refs/heads/{feature_branch}",
            ],
            check=False,
        ).returncode
        == 0
    )
    if local_branch_exists:
        _run(root, "switch", feature_branch)
        action = "used_existing_tracking_branch"
    else:
        _run(root, "switch", "--track", f"origin/{feature_branch}")
        action = "created_exact_tracking_branch"
    if _run(root, "rev-parse", "HEAD") != branch_sha:
        _fail("local_remote_head_mismatch", feature_branch)
    return Resolution(
        "executable",
        "resolved",
        expected_repository,
        task_id,
        branch_status,
        feature_branch,
        main_sha,
        branch_sha,
        action,
    )


def _emit(resolution: Resolution, as_json: bool) -> None:
    if as_json:
        print(json.dumps(resolution.as_dict(), sort_keys=True))
        return
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
        if args.json:
            print(json.dumps(payload, sort_keys=True))
        else:
            print(f"outcome: blocked\nreason_code: {error.reason_code}\ndetail: {error.detail}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
