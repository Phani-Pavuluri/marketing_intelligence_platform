import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Protocol, cast

import pytest

ROOT = Path(__file__).parents[1]
MODULE_PATH = ROOT / "scripts" / "resolve_active_task.py"
SPEC = importlib.util.spec_from_file_location("resolve_active_task", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
RESOLVER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = RESOLVER
SPEC.loader.exec_module(RESOLVER)

EXPECTED_REPOSITORY = "example/repo"
FEATURE_BRANCH = "feat/example-task"
TASK_ID = "EXAMPLE_TASK_001"


class ResolutionLike(Protocol):
    branch_sha: str | None
    outcome: str
    feature_branch: str | None
    reason_code: str
    status: str
    task_id: str


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def write_views(repo: Path, state: dict[str, object]) -> None:
    execution = repo / "docs" / "execution"
    execution.mkdir(parents=True, exist_ok=True)
    status = str(state["status"])
    implementation = state.get("implementation_commit_sha")
    implementation_line = ""
    if isinstance(implementation, str) and implementation:
        implementation_line = f"\n- **Implementation commit:** `{implementation}`\n"
    (execution / "EXECUTION_STATE.json").write_text(json.dumps(state, indent=2) + "\n")
    (execution / "ACTIVE_TASK.md").write_text(
        f"# Active Task\n\n**Status:** {status}\n\n- Task ID: `{TASK_ID}`{implementation_line}"
    )
    report = f"# Completion\n\n- Task ID: `{TASK_ID}`\n- **Current decision:** `{status}`"
    (execution / "LATEST_COMPLETION_REPORT.md").write_text(report + implementation_line)
    (execution / "REPOSITORY_CONTEXT_INDEX.md").write_text("# Context\n\nCanonical sources only.\n")


def state(
    status: str, authorization_head: str, implementation: str | None = None
) -> dict[str, object]:
    return {
        "schema_version": "mip_repo_execution_state_v2",
        "repository": EXPECTED_REPOSITORY,
        "task_id": TASK_ID,
        "status": status,
        "base_branch": "main",
        "base_sha": authorization_head,
        "authorization_head_sha": authorization_head,
        "feature_branch": FEATURE_BRANCH,
        "task_execution_authorized": status not in {"merged", "idle", "proposed", "superseded"},
        "correction_execution_authorized": status == "changes_requested",
        "merge_authorized": False,
        "implementation_commit_sha": implementation,
    }


def commit_all(repo: Path, message: str) -> str:
    git(repo, "add", ".")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def make_repository(tmp_path: Path, status_name: str = "authorized") -> tuple[Path, Path, Path]:
    remote = tmp_path / "example" / "repo.git"
    remote.parent.mkdir()
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, stdout=subprocess.PIPE)
    seed = tmp_path / "seed"
    git(tmp_path, "init", str(seed))
    git(seed, "config", "user.email", "resolver@example.test")
    git(seed, "config", "user.name", "Resolver Test")
    git(seed, "checkout", "-b", "main")
    git(seed, "remote", "add", "origin", str(remote))
    (seed / "README.md").write_text("baseline\n")
    baseline = commit_all(seed, "baseline")
    write_views(seed, state(status_name, baseline))
    metadata = commit_all(seed, "task metadata")
    git(seed, "push", "-u", "origin", "main")
    git(seed, "checkout", "-b", FEATURE_BRANCH)
    git(seed, "push", "-u", "origin", FEATURE_BRANCH)
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", str(remote), str(clone)], check=True, stdout=subprocess.PIPE)
    git(clone, "checkout", "main")
    assert metadata
    return seed, clone, remote


def push_feature_state(
    seed: Path, new_state: dict[str, object], message: str = "feature state"
) -> str:
    write_views(seed, new_state)
    sha = commit_all(seed, message)
    git(seed, "push", "origin", FEATURE_BRANCH)
    return sha


def resolve(clone: Path) -> ResolutionLike:
    return cast(ResolutionLike, RESOLVER.resolve_active_task(clone, EXPECTED_REPOSITORY))


def test_resolves_authorized_task_and_exact_remote_branch(tmp_path: Path) -> None:
    _, clone, _ = make_repository(tmp_path)
    resolution = resolve(clone)
    assert resolution.outcome == "executable"
    assert resolution.feature_branch == FEATURE_BRANCH
    assert git(clone, "branch", "--show-current") == FEATURE_BRANCH
    assert resolution.branch_sha == git(clone, "rev-parse", f"origin/{FEATURE_BRANCH}")


def test_merged_state_stays_on_main(tmp_path: Path) -> None:
    _, clone, _ = make_repository(tmp_path, "merged")
    resolution = resolve(clone)
    assert resolution.outcome == "non_executable"
    assert resolution.reason_code == "non_executable_state"
    assert git(clone, "branch", "--show-current") == "main"


def test_ready_for_review_is_review_only(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path, "ready_for_review")
    implementation = git(seed, "rev-parse", "HEAD")
    ready_state = state("ready_for_review", implementation, implementation)
    git(seed, "checkout", "main")
    write_views(seed, ready_state)
    commit_all(seed, "ready pointer")
    git(seed, "push", "origin", "main")
    git(seed, "checkout", FEATURE_BRANCH)
    push_feature_state(seed, ready_state, "ready branch")
    resolution = resolve(clone)
    assert resolution.outcome == "review_only"
    assert git(clone, "branch", "--show-current") == "main"


def test_authorized_correction_resumes(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path, "changes_requested")
    correction_state = state("changes_requested", git(seed, "rev-parse", "main"))
    push_feature_state(seed, correction_state)
    resolution = resolve(clone)
    assert resolution.outcome == "executable"
    assert resolution.status == "changes_requested"


def test_wrong_origin_fails_closed(tmp_path: Path) -> None:
    _, clone, _ = make_repository(tmp_path)
    git(clone, "remote", "set-url", "origin", str(tmp_path / "other.git"))
    with pytest.raises(RESOLVER.ResolverError, match="wrong_origin"):
        resolve(clone)


@pytest.mark.parametrize("path", ["unexpected.txt", "docs/tasks/allowed.md", ".codex/allowed.toml"])
def test_worktree_hygiene(tmp_path: Path, path: str) -> None:
    _, clone, _ = make_repository(tmp_path)
    target = clone / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text("local\n")
    if path == "unexpected.txt":
        with pytest.raises(RESOLVER.ResolverError, match="unexpected_untracked_path"):
            resolve(clone)
    else:
        assert resolve(clone).outcome == "executable"


def test_missing_remote_branch_fails_closed(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    git(seed, "push", "origin", "--delete", FEATURE_BRANCH)
    with pytest.raises(RESOLVER.ResolverError, match="missing_remote_branch"):
        resolve(clone)


def test_authorization_head_ancestry_failure(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    git(seed, "checkout", "main")
    (seed / "alternate.txt").write_text("alternate\n")
    alternate = commit_all(seed, "alternate authorization")
    broken = state("authorized", alternate)
    write_views(seed, broken)
    commit_all(seed, "broken pointer")
    git(seed, "push", "origin", "main")
    with pytest.raises(RESOLVER.ResolverError, match="authorization_head_not_ancestral"):
        resolve(clone)


def test_branch_state_mismatch_fails_closed(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    mismatched = state("authorized", git(seed, "rev-parse", "main"))
    mismatched["task_id"] = "OTHER_TASK"
    push_feature_state(seed, mismatched)
    with pytest.raises(RESOLVER.ResolverError, match="branch_state_mismatch"):
        resolve(clone)


def test_nonexistent_or_nonancestral_implementation_fails_closed(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    feature_head = git(seed, "rev-parse", "HEAD")
    git(seed, "checkout", "-b", "side")
    (seed / "side.txt").write_text("side\n")
    side_sha = commit_all(seed, "side implementation")
    git(seed, "push", "origin", "side")
    git(seed, "checkout", FEATURE_BRANCH)
    invalid = state("ready_for_review", feature_head, "0" * 40)
    push_feature_state(seed, invalid, "invalid implementation")
    with pytest.raises(RESOLVER.ResolverError, match="invalid_implementation_sha"):
        resolve(clone)
    valid_but_wrong = state("ready_for_review", feature_head, side_sha)
    push_feature_state(seed, valid_but_wrong, "non ancestral implementation")
    with pytest.raises(RESOLVER.ResolverError, match="implementation_sha_not_ancestral"):
        resolve(clone)


def test_duplicate_human_current_decision_fails_closed(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    active = seed / "docs" / "execution" / "ACTIVE_TASK.md"
    active.write_text(active.read_text() + "\n**Status:** authorized\n")
    commit_all(seed, "duplicate status")
    git(seed, "push", "origin", FEATURE_BRANCH)
    with pytest.raises(RESOLVER.ResolverError, match="contradictory_human_current_state"):
        resolve(clone)


def test_stale_context_text_does_not_select_branch(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    context = seed / "docs" / "execution" / "REPOSITORY_CONTEXT_INDEX.md"
    context.write_text("# Context\n\nOld task: OTHER_TASK\n")
    commit_all(seed, "stale context")
    git(seed, "push", "origin", FEATURE_BRANCH)
    assert resolve(clone).task_id == TASK_ID
