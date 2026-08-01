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
        "execution_mode": "branch_and_fast_forward",
        "base_branch": "main",
        "base_sha": authorization_head,
        "authorization_head_sha": authorization_head,
        "feature_branch": FEATURE_BRANCH,
        "task_path": "docs/execution/ACTIVE_TASK.md",
        "completion_report_path": "docs/execution/LATEST_COMPLETION_REPORT.md",
        "task_execution_authorized": status in {"authorized", "in_progress", "blocked"},
        "correction_execution_authorized": status == "changes_requested",
        "merge_authorized": False,
        "pr_creation_authorized": False,
        "reviewed_head_sha": None,
        "implementation_commit_sha": implementation,
        "approval_commit_sha": None,
        "capability_authorizations_changed": False,
        "blockers": [],
    }


def commit_all(repo: Path, message: str) -> str:
    git(repo, "add", ".")
    git(repo, "commit", "-m", message)
    return git(repo, "rev-parse", "HEAD")


def make_repository(tmp_path: Path, status_name: str = "authorized") -> tuple[Path, Path, Path]:
    remote = tmp_path / "example" / "repo.git"
    remote.parent.mkdir(parents=True)
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


def push_main_state(seed: Path, new_state: dict[str, object], message: str = "main state") -> str:
    current_branch = git(seed, "branch", "--show-current")
    git(seed, "checkout", "main")
    write_views(seed, new_state)
    sha = commit_all(seed, message)
    git(seed, "push", "origin", "main")
    git(seed, "checkout", current_branch)
    return sha


def resolve(clone: Path) -> ResolutionLike:
    return cast(ResolutionLike, RESOLVER.resolve_active_task(clone, EXPECTED_REPOSITORY))


def read_state(repo: Path, ref: str = "HEAD") -> dict[str, object]:
    return cast(
        dict[str, object],
        json.loads(git(repo, "show", f"{ref}:docs/execution/EXECUTION_STATE.json")),
    )


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
    correction_state = read_state(seed, "main")
    correction_state["blockers"] = ["BRANCH_ONLY_CORRECTION"]
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
    git(seed, "checkout", "-b", "side")
    (seed / "side.txt").write_text("side\n")
    side_sha = commit_all(seed, "side implementation")
    git(seed, "push", "origin", "side")
    git(seed, "checkout", FEATURE_BRANCH)
    invalid = read_state(seed, "main")
    invalid["status"] = "ready_for_review"
    invalid["task_execution_authorized"] = False
    invalid["correction_execution_authorized"] = False
    invalid["implementation_commit_sha"] = "0" * 40
    git(seed, "checkout", "main")
    write_views(seed, invalid)
    commit_all(seed, "ready pointer")
    git(seed, "push", "origin", "main")
    git(seed, "checkout", FEATURE_BRANCH)
    push_feature_state(seed, invalid, "invalid implementation")
    with pytest.raises(RESOLVER.ResolverError, match="nonexistent_implementation_sha"):
        resolve(clone)
    valid_but_wrong = dict(invalid)
    valid_but_wrong["implementation_commit_sha"] = side_sha
    push_main_state(seed, valid_but_wrong, "non ancestral ready pointer")
    push_feature_state(seed, valid_but_wrong, "non ancestral implementation")
    with pytest.raises(RESOLVER.ResolverError, match="implementation_sha_not_ancestral"):
        resolve(clone)


def test_duplicate_human_current_decision_fails_closed(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    active = seed / "docs" / "execution" / "ACTIVE_TASK.md"
    active.write_text(active.read_text() + "\n**Status:** authorized\n")
    commit_all(seed, "duplicate status")
    git(seed, "push", "origin", FEATURE_BRANCH)
    with pytest.raises(RESOLVER.ResolverError, match="contradictory_active_task_status"):
        resolve(clone)


def test_stale_context_text_does_not_select_branch(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    context = seed / "docs" / "execution" / "REPOSITORY_CONTEXT_INDEX.md"
    context.write_text("# Context\n\nOld task: OTHER_TASK\n")
    commit_all(seed, "stale context")
    git(seed, "push", "origin", FEATURE_BRANCH)
    assert resolve(clone).task_id == TASK_ID


# Each requirement maps to an exact focused test.  The matrix is intentionally
# machine-checked so a later refactor cannot silently drop correction coverage.
REQUIREMENT_TESTS = {
    "R01": "test_r01_authorized_checkout",
    "R02": "test_r02_authorized_to_in_progress",
    "R03": "test_r03_branch_only_correction",
    "R04": "test_r04_blocked_resumption",
    "R05": "test_r05_ready_review_only",
    "R06": "test_r06_main_only_states_validate_views",
    "R07": "test_r07_wrong_origin",
    "R08": "test_r08_repository_identity",
    "R09": "test_r09_dirty_tracked",
    "R10": "test_r10_untracked_policy",
    "R11": "test_r11_main_synchronization",
    "R12": "test_r12_missing_remote_branch",
    "R13": "test_r13_authorization_head_failures",
    "R14": "test_r14_invariant_mismatch",
    "R15": "test_r15_authority_escalation",
    "R16": "test_r16_transition_matrix",
    "R17": "test_r17_nonexistent_implementation",
    "R18": "test_r18_nonancestral_implementation",
    "R19": "test_r19_active_status_conflict",
    "R20": "test_r20_report_decision_conflict",
    "R21": "test_r21_merged_closure_conflict",
    "R22": "test_r22_stale_context_ignored",
    "R23": "test_r23_stale_local_feature",
    "R24": "test_r24_malformed_field_reason_code",
    "R25": "test_r25_coordination_test_is_task_agnostic",
}


def test_requirement_matrix_is_complete() -> None:
    assert set(REQUIREMENT_TESTS) == {f"R{number:02d}" for number in range(1, 26)}
    for test_name in REQUIREMENT_TESTS.values():
        assert callable(globals()[test_name])


def test_r01_authorized_checkout(tmp_path: Path) -> None:
    _, clone, _ = make_repository(tmp_path)
    assert resolve(clone).outcome == "executable"


def test_r02_authorized_to_in_progress(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    branch_state = read_state(seed, "main")
    branch_state["status"] = "in_progress"
    branch_state["blockers"] = ["WORK_STARTED"]
    push_feature_state(seed, branch_state)
    assert resolve(clone).status == "in_progress"


def test_r03_branch_only_correction(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    branch_state = read_state(seed, "main")
    branch_state.update(
        {
            "status": "changes_requested",
            "task_execution_authorized": False,
            "correction_execution_authorized": True,
            "blockers": ["CORRECTION"],
        }
    )
    push_feature_state(seed, branch_state)
    assert resolve(clone).status == "changes_requested"


def test_r04_blocked_resumption(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    branch_state = read_state(seed, "main")
    branch_state.update(
        {
            "status": "blocked",
            "task_execution_authorized": False,
            "correction_execution_authorized": True,
            "blockers": ["PAUSED"],
        }
    )
    push_feature_state(seed, branch_state)
    assert resolve(clone).status == "blocked"
    branch_state["correction_execution_authorized"] = False
    push_feature_state(seed, branch_state, "blocked without authority")
    with pytest.raises(RESOLVER.ResolverError, match="execution_not_authorized"):
        resolve(clone)


def test_correction_can_publish_blocked_resumption_state(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path, "changes_requested")
    branch_state = read_state(seed, "main")
    branch_state["status"] = "blocked"
    branch_state["blockers"] = ["UNOWNED_VALIDATION_CONFLICT"]
    push_feature_state(seed, branch_state)
    assert resolve(clone).status == "blocked"


def test_r05_ready_review_only(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    implementation = git(seed, "rev-parse", "HEAD")
    review_state = read_state(seed, "main")
    review_state.update(
        {
            "status": "ready_for_review",
            "task_execution_authorized": False,
            "correction_execution_authorized": False,
            "implementation_commit_sha": implementation,
        }
    )
    push_main_state(seed, review_state)
    push_feature_state(seed, review_state)
    assert resolve(clone).outcome == "review_only"
    assert git(clone, "branch", "--show-current") == "main"


@pytest.mark.parametrize("status_name", ["idle", "proposed", "merged", "superseded"])
def test_r06_main_only_states_validate_views(tmp_path: Path, status_name: str) -> None:
    _, clone, _ = make_repository(tmp_path, status_name)
    assert resolve(clone).outcome == "non_executable"
    assert git(clone, "branch", "--show-current") == "main"


def test_r07_wrong_origin(tmp_path: Path) -> None:
    test_wrong_origin_fails_closed(tmp_path)


def test_r08_repository_identity(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    broken = read_state(seed, "main")
    broken["repository"] = "other/repository"
    push_main_state(seed, broken)
    with pytest.raises(RESOLVER.ResolverError, match="repository_identity_mismatch"):
        resolve(clone)


def test_r09_dirty_tracked(tmp_path: Path) -> None:
    _, clone, _ = make_repository(tmp_path)
    (clone / "README.md").write_text("changed\n")
    with pytest.raises(RESOLVER.ResolverError, match="dirty_tracked_worktree"):
        resolve(clone)


def test_r10_untracked_policy(tmp_path: Path) -> None:
    test_worktree_hygiene(tmp_path / "unexpected", "unexpected.txt")
    test_worktree_hygiene(tmp_path / "codex", ".codex/allowed.toml")
    test_worktree_hygiene(tmp_path / "tasks", "docs/tasks/allowed.md")


def test_r11_main_synchronization(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    git(seed, "checkout", "main")
    (seed / "after.txt").write_text("remote\n")
    commit_all(seed, "remote main advance")
    git(seed, "push", "origin", "main")
    assert resolve(clone).main_sha == git(clone, "rev-parse", "origin/main")
    git(clone, "checkout", "main")
    git(clone, "config", "user.email", "resolver@example.test")
    git(clone, "config", "user.name", "Resolver Test")
    (clone / "local-main.txt").write_text("local\n")
    commit_all(clone, "local main divergence")
    with pytest.raises(RESOLVER.ResolverError, match="stale_or_diverged_main"):
        resolve(clone)


def test_r12_missing_remote_branch(tmp_path: Path) -> None:
    test_missing_remote_branch_fails_closed(tmp_path)


def test_r13_authorization_head_failures(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    broken = read_state(seed, "main")
    broken["authorization_head_sha"] = "not-a-sha"
    push_main_state(seed, broken)
    with pytest.raises(RESOLVER.ResolverError, match="invalid_sha_field"):
        resolve(clone)
    missing = read_state(seed, "main")
    missing.pop("authorization_head_sha")
    with pytest.raises(RESOLVER.ResolverError, match="missing_required_field"):
        RESOLVER._validate_state(missing, EXPECTED_REPOSITORY)
    nonexistent = read_state(seed, "main")
    nonexistent["authorization_head_sha"] = "f" * 40
    with pytest.raises(RESOLVER.ResolverError, match="nonexistent_authorization_head"):
        RESOLVER._validate_authorization_head(seed, nonexistent, git(seed, "rev-parse", "HEAD"))


def test_r14_invariant_mismatch(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    branch_state = read_state(seed, "main")
    branch_state["base_branch"] = "other"
    push_feature_state(seed, branch_state)
    with pytest.raises(RESOLVER.ResolverError, match="branch_state_mismatch"):
        resolve(clone)


def test_r15_authority_escalation(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    branch_state = read_state(seed, "main")
    branch_state["merge_authorized"] = True
    push_feature_state(seed, branch_state)
    with pytest.raises(RESOLVER.ResolverError, match="unauthorized_merge_or_pr"):
        resolve(clone)


def test_r16_transition_matrix(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    branch_state = read_state(seed, "main")
    branch_state["status"] = "proposed"
    branch_state["task_execution_authorized"] = False
    branch_state["correction_execution_authorized"] = False
    push_feature_state(seed, branch_state)
    with pytest.raises(RESOLVER.ResolverError, match="unsupported_lifecycle_transition"):
        resolve(clone)


def test_r17_nonexistent_implementation(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    review_state = read_state(seed, "main")
    review_state.update(
        {
            "status": "ready_for_review",
            "task_execution_authorized": False,
            "implementation_commit_sha": "0" * 40,
        }
    )
    push_main_state(seed, review_state)
    push_feature_state(seed, review_state)
    with pytest.raises(RESOLVER.ResolverError, match="nonexistent_implementation_sha"):
        resolve(clone)


def test_r18_nonancestral_implementation(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    git(seed, "checkout", "-b", "side")
    (seed / "side.txt").write_text("side\n")
    side_sha = commit_all(seed, "side")
    git(seed, "push", "origin", "side")
    git(seed, "checkout", FEATURE_BRANCH)
    review_state = read_state(seed, "main")
    review_state.update(
        {
            "status": "ready_for_review",
            "task_execution_authorized": False,
            "implementation_commit_sha": side_sha,
        }
    )
    push_main_state(seed, review_state)
    push_feature_state(seed, review_state)
    with pytest.raises(RESOLVER.ResolverError, match="implementation_sha_not_ancestral"):
        resolve(clone)


def test_r19_active_status_conflict(tmp_path: Path) -> None:
    test_duplicate_human_current_decision_fails_closed(tmp_path)


def test_r20_report_decision_conflict(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    report = seed / "docs" / "execution" / "LATEST_COMPLETION_REPORT.md"
    report.write_text(report.read_text() + "\n- **Current decision:** `authorized`\n")
    commit_all(seed, "duplicate report decision")
    git(seed, "push", "origin", FEATURE_BRANCH)
    with pytest.raises(RESOLVER.ResolverError, match="contradictory_completion_report_decision"):
        resolve(clone)


def test_r21_merged_closure_conflict(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path, "merged")
    git(seed, "checkout", "main")
    active = seed / "docs" / "execution" / "ACTIVE_TASK.md"
    active.write_text(active.read_text() + "\n**Status:** ready_for_review\n")
    commit_all(seed, "bad merged closure")
    git(seed, "push", "origin", "main")
    with pytest.raises(RESOLVER.ResolverError, match="contradictory_merged_closure_prose"):
        resolve(clone)


def test_r22_stale_context_ignored(tmp_path: Path) -> None:
    test_stale_context_text_does_not_select_branch(tmp_path)


def test_r23_stale_local_feature(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    git(clone, "branch", FEATURE_BRANCH, f"origin/{FEATURE_BRANCH}")
    branch_state = read_state(seed, "main")
    branch_state["blockers"] = ["REMOTE_ADVANCE"]
    push_feature_state(seed, branch_state)
    with pytest.raises(RESOLVER.ResolverError, match="local_feature_branch_not_exact"):
        resolve(clone)


def test_r24_malformed_field_reason_code(tmp_path: Path) -> None:
    seed, clone, _ = make_repository(tmp_path)
    broken = read_state(seed, "main")
    broken.pop("task_path")
    push_main_state(seed, broken)
    with pytest.raises(RESOLVER.ResolverError, match="missing_required_field"):
        resolve(clone)


def test_r25_coordination_test_is_task_agnostic() -> None:
    source = (ROOT / "tests" / "test_cross_repository_coordination_control_plane.py").read_text()
    assert 'task_id = execution_state["task_id"]' in source
    assert "MIP_ACTIVE_TASK_CONTEXT_RESOLVER_001" not in source
