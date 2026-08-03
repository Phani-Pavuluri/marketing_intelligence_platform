import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
EXECUTION = ROOT / "docs" / "execution"
STANDARD = EXECUTION / "TASK_EXECUTION_STANDARD.md"
LEAN_STANDARD = ROOT / "docs" / "program" / "LEAN_REPOSITORY_DELIVERY_STANDARD.md"
STATE_PATH = EXECUTION / "EXECUTION_STATE.json"
ACTIVE_TASK = EXECUTION / "ACTIVE_TASK.md"
REPORT = EXECUTION / "LATEST_COMPLETION_REPORT.md"
CONTEXT_INDEX = EXECUTION / "REPOSITORY_CONTEXT_INDEX.md"
AGENTS = ROOT / "AGENTS.md"
STATUSES = {
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
SHA_PATTERN = r"[0-9a-f]{40}"


def _assert_sha(value: object) -> None:
    assert isinstance(value, str)
    assert re.fullmatch(SHA_PATTERN, value)


def test_repo_native_execution_handoff_is_consistent() -> None:
    required_paths = (
        STANDARD,
        CONTEXT_INDEX,
        ACTIVE_TASK,
        REPORT,
        STATE_PATH,
        AGENTS,
    )
    for path in required_paths:
        assert path.is_file()

    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    assert state["schema_version"] == "mip_repo_execution_state_v2"
    assert state["status"] in STATUSES
    task_id = state["task_id"]
    assert isinstance(task_id, str) and task_id
    for key in (
        "task_execution_authorized",
        "merge_authorized",
        "capability_authorizations_changed",
    ):
        assert isinstance(state[key], bool)
    _assert_sha(state["base_sha"])
    _assert_sha(state["authorization_head_sha"])
    assert (ROOT / state["task_path"]).is_file()
    assert (ROOT / state["completion_report_path"]).is_file()
    assert task_id in ACTIVE_TASK.read_text(encoding="utf-8")
    assert task_id in REPORT.read_text(encoding="utf-8")
    assert state["capability_authorizations_changed"] is False

    agents = AGENTS.read_text(encoding="utf-8")
    for stable_path in (
        "docs/execution/EXECUTION_STATE.json",
        "docs/execution/ACTIVE_TASK.md",
        "docs/execution/LATEST_COMPLETION_REPORT.md",
        "docs/execution/REPOSITORY_CONTEXT_INDEX.md",
    ):
        assert stable_path in agents

    standard = STANDARD.read_text(encoding="utf-8")
    lean_standard = LEAN_STANDARD.read_text(encoding="utf-8")
    context_index = CONTEXT_INDEX.read_text(encoding="utf-8")
    combined_bootstrap = f"{agents}\n{standard}\n{context_index}"
    standard_flat = " ".join(standard.split())
    for command in (
        "git fetch --prune origin",
        "git switch main",
        "git pull --ff-only origin main",
        "git rev-parse main",
        "git rev-parse origin/main",
    ):
        assert command in combined_bootstrap
    for local_only_path in (".codex/", "docs/tasks/"):
        assert local_only_path in agents
        assert local_only_path in standard
        assert local_only_path in context_index
    assert "unexpected untracked" in combined_bootstrap
    assert "git fetch --unshallow origin" in standard
    assert "base_sha..authorization_head_sha" in standard

    assert "No pre-merge approval-metadata commit" in standard_flat
    assert "git merge --ff-only" in standard
    assert "Docker-backed `make validate`" in standard
    assert "exactly one post-merge closure commit" in standard_flat
    assert "exact remote feature-branch head SHA" in agents
    assert "Persisted `merge_authorized` remains false" in standard

    definition_ready_guidance = f"{agents}\n{standard}\n{lean_standard}"
    for requirement in (
        "primary mergeable outcome",
        "exact observable behavior",
        "resolved design",
        "inputs/outputs appropriate to the changed surface",
        "failure semantics",
        "Compatibility or migration policy",
        "named acceptance tests or deterministic evidence",
        "unresolved execution-blocking design questions: none",
        "materially different contract meanings",
        "separately authorized owner-repository decision",
    ):
        assert requirement in definition_ready_guidance
    assert "Surface proportionality" in standard
    assert "`not_applicable`" in standard
    assert "retain `proposed`,\nmark it design-blocked, or split" in standard

    invocation_guidance = f"{agents}\n{standard}"
    for requirement in (
        "Invocation-only prompt rule",
        "Codex prompts are invocation-only",
        "Synchronize from Git and execute the active task.",
        "exact externally approved remote head SHA",
        "must not restate durable scope, owned paths, behavior, validation",
        "cannot repair, expand, override, or reinterpret",
        "fail-closed blocker",
        "separately authorized owner-repository decision",
    ):
        assert requirement in invocation_guidance
    assert "publish `ready_for_review`" not in standard
    assert "push\nthe exact branch head" not in standard
    resumed_guidance = f"{agents}\n{standard}"
    for requirement in (
        "verified branch is authoritative for current lifecycle state",
        "Main remains authority\nfor authorization provenance",
        "Do not stop merely because main has\nan older lifecycle snapshot",
        "terminal or chat output is not a completion report",
        "task ID, branch name, and authorization ancestry",
        "Fail closed on mismatches or\ninconsistent evidence",
        "record\nany fail-closed result there as `blocked`",
    ):
        assert requirement in resumed_guidance

    if state["status"] in {"authorized", "in_progress", "ready_for_review"}:
        assert state["task_execution_authorized"] is True
        assert state["merge_authorized"] is False
        assert state["reviewed_head_sha"] is None
        assert state["approval_commit_sha"] is None
    if state["status"] == "ready_for_review":
        _assert_sha(state["implementation_commit_sha"])
    if state["status"] == "blocked":
        assert state["task_execution_authorized"] is True
        assert state["merge_authorized"] is False
        assert state["reviewed_head_sha"] is None
        assert state["approval_commit_sha"] is None
        _assert_sha(state["implementation_commit_sha"])
        assert state["blockers"]
    if state["status"] == "merged":
        assert state["task_execution_authorized"] is False
        assert state["merge_authorized"] is False
        _assert_sha(state["reviewed_head_sha"])
        assert state["approval_commit_sha"] is None
