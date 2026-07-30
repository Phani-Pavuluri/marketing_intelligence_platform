import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
EXECUTION = ROOT / "docs" / "execution"
STATE_PATH = EXECUTION / "EXECUTION_STATE.json"
ACTIVE_TASK = EXECUTION / "ACTIVE_TASK.md"
REPORT = EXECUTION / "LATEST_COMPLETION_REPORT.md"
AGENTS = ROOT / "AGENTS.md"
STATUSES = {
    "idle", "proposed", "authorized", "in_progress", "blocked",
    "ready_for_review", "changes_requested", "approved_for_merge", "merged",
    "superseded",
}
BOOTSTRAP_TASK_ID = "MIP_REPO_NATIVE_EXECUTION_HANDOFF_WORKFLOW_001"


def test_repo_native_execution_handoff_is_consistent() -> None:
    required_paths = (
        EXECUTION / "TASK_EXECUTION_STANDARD.md",
        EXECUTION / "REPOSITORY_CONTEXT_INDEX.md",
        ACTIVE_TASK,
        REPORT,
        STATE_PATH,
        AGENTS,
    )
    for path in required_paths:
        assert path.is_file()
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    assert state["schema_version"] == "mip_repo_execution_state_v1"
    assert state["status"] in STATUSES
    task_id = state["task_id"]
    assert isinstance(task_id, str) and task_id
    for key in (
        "task_execution_authorized",
        "merge_authorized",
        "capability_authorizations_changed",
    ):
        assert isinstance(state[key], bool)
    assert (ROOT / state["task_path"]).is_file()
    assert (ROOT / state["completion_report_path"]).is_file()
    assert task_id in ACTIVE_TASK.read_text(encoding="utf-8")
    assert task_id in REPORT.read_text(encoding="utf-8")
    agents = AGENTS.read_text(encoding="utf-8")
    stable_paths: tuple[str, ...] = (
        "docs/execution/EXECUTION_STATE.json",
        "docs/execution/ACTIVE_TASK.md",
        "docs/execution/LATEST_COMPLETION_REPORT.md",
        "docs/execution/REPOSITORY_CONTEXT_INDEX.md",
    )
    for stable_path in stable_paths:
        assert stable_path in agents
    context_index = (EXECUTION / "REPOSITORY_CONTEXT_INDEX.md").read_text(
        encoding="utf-8"
    )
    assert "Fresh Chat Bootstrap" in context_index
    assert "connected GitHub as the source of truth" in context_index
    if state["status"] == "ready_for_review":
        assert state["task_execution_authorized"] is True
        assert state["merge_authorized"] is False
        assert re.fullmatch(r"[0-9a-f]{7,64}", state["implementation_commit_sha"])
        assert state["reviewed_head_sha"] is None
        assert state["approval_commit_sha"] is None
    if state["status"] == "approved_for_merge":
        assert state["task_execution_authorized"] is True
        assert state["merge_authorized"] is True
        assert state["reviewed_head_sha"]
        assert state["approval_commit_sha"]
    if task_id == BOOTSTRAP_TASK_ID:
        assert state["capability_authorizations_changed"] is False
