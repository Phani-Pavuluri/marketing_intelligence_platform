import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
EXECUTION = ROOT / "docs" / "execution"
STANDARD = EXECUTION / "TASK_EXECUTION_STANDARD.md"
STATE_PATH = EXECUTION / "EXECUTION_STATE.json"
ACTIVE_TASK = EXECUTION / "ACTIVE_TASK.md"
REPORT = EXECUTION / "LATEST_COMPLETION_REPORT.md"
CONTEXT_INDEX = EXECUTION / "REPOSITORY_CONTEXT_INDEX.md"
AGENTS = ROOT / "AGENTS.md"
SHA_PATTERN = r"[0-9a-f]{40}"
SYNC_LINE = (
    "Synchronize main from Git and read AGENTS.md and the repository execution files. "
    "Resolve authorization provenance and the exact feature branch from synchronized main, "
    "then fetch and resume that remote feature branch and read its current execution files."
)
PROGRESS_LINE = (
    "Progress updates are non-terminal. Do not stop or return control merely to report orientation "
    "or progress. Stop only when the remote feature branch durably records"
)
CANONICAL = {
    "Canonical execution launcher": "\n\n".join(
        (
            "Work in <local repository path>.",
            SYNC_LINE,
            "Execute the active task through implementation, required validation, "
            "exact-tree publication, "
            "push, and remote-head verification.",
            f"{PROGRESS_LINE} ready_for_review or a genuine blocked state.",
            "Do not create a pull request, merge, or change capability authority.",
        )
    ),
    "Canonical correction launcher": "\n\n".join(
        (
            "Work in <local repository path>.",
            SYNC_LINE,
            "Execute the Git-authored changes_requested correction through the complete "
            "required validation, "
            "a new exact-tree publication, push, and remote-head verification.",
            f"{PROGRESS_LINE} a new ready_for_review or a genuine blocked state.",
            "Do not create a pull request, merge, or change capability authority.",
        )
    ),
    "Canonical merge launcher": "\n\n".join(
        (
            "Work in <local repository path>.",
            "Synchronize main from Git and read AGENTS.md and the repository execution files. "
            "Execute the active task's merge and closure workflow.",
            "Approved exact remote head: <FULL_SHA>",
            "Revalidate the approved head, fast-forward merge only, validate after fast-forward, "
            "push main, perform task-branch cleanup, create exactly one closure commit, and "
            "verify local and remote main equality.",
            "Do not create a pull request, squash, rebase, force-push, or create a merge commit.",
        )
    ),
}


def _block(heading: str) -> str:
    text = STANDARD.read_text(encoding="utf-8")
    start = text.index(f"### {heading}")
    start = text.index("```text\n", start) + len("```text\n")
    end = text.index("\n```", start)
    return text[start:end]


def _sha(value: object) -> None:
    assert isinstance(value, str) and re.fullmatch(SHA_PATTERN, value)


def test_repo_native_execution_handoff_is_consistent() -> None:
    for required_path in (STANDARD, CONTEXT_INDEX, ACTIVE_TASK, REPORT, STATE_PATH, AGENTS):
        assert required_path.is_file()
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    assert state["schema_version"] == "mip_repo_execution_state_v2"
    assert state["task_id"] in ACTIVE_TASK.read_text(encoding="utf-8")
    assert state["task_id"] in REPORT.read_text(encoding="utf-8")
    _sha(state["base_sha"])
    _sha(state["authorization_head_sha"])
    assert state["capability_authorizations_changed"] is False
    for local_only_path in (".codex/", "docs/tasks/"):
        assert local_only_path in AGENTS.read_text(encoding="utf-8")
        assert local_only_path in STANDARD.read_text(encoding="utf-8")


def test_git_authoritative_thin_launcher_preserves_git_only_task_meaning() -> None:
    text = f"{AGENTS.read_text(encoding='utf-8')}\n{STANDARD.read_text(encoding='utf-8')}"
    assert "Git is the sole durable task authority" in text
    assert "cannot define, repair, expand, override, or reinterpret" in text
    assert "Codex prompts are invocation-only" not in text
    assert "The execution and correction invocation is exactly" not in text


def test_execution_and_correction_launchers_are_operational_and_non_terminal() -> None:
    assert _block("Canonical execution launcher") == CANONICAL["Canonical execution launcher"]
    assert _block("Canonical correction launcher") == CANONICAL["Canonical correction launcher"]


def test_merge_launcher_requires_only_path_and_approved_exact_sha() -> None:
    assert _block("Canonical merge launcher") == CANONICAL["Canonical merge launcher"]


def test_launchers_forbid_task_instance_duplication() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    forbidden = (state["task_id"], state["feature_branch"], "MMM", "GeoX", "pytest")
    for heading in CANONICAL:
        block = _block(heading)
        assert all(value not in block for value in forbidden)
        if heading == "Canonical merge launcher":
            assert "<FULL_SHA>" in block
        else:
            assert "<FULL_SHA>" not in block
            assert not re.search(SHA_PATTERN, block)


def test_current_lifecycle_state_is_coherent() -> None:
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if state["status"] != "ready_for_review":
        return
    active = ACTIVE_TASK.read_text(encoding="utf-8")
    report = REPORT.read_text(encoding="utf-8")
    implementation_sha = state["implementation_commit_sha"]
    _sha(implementation_sha)
    assert active.count("**Status:** ready_for_review") == 1
    assert report.count("**Current decision:** `ready_for_review`") == 1
    assert implementation_sha in active and implementation_sha in report
    assert state["correction_execution_authorized"] is False
    assert state["merge_authorized"] is False
    assert state["pr_creation_authorized"] is False
    assert state["blockers"] == []
    for text in (active, report):
        assert not re.search(
            r"^#{1,6} .*?(changes requested|required correction|correction authorization)",
            text,
            re.I | re.M,
        )
