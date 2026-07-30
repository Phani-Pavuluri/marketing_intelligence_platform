import json
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
TASK_ID = "MIP_REPO_NATIVE_EXECUTION_HANDOFF_WORKFLOW_001"


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
    assert state["task_id"] == TASK_ID
    assert state["task_execution_authorized"] is True
    assert state["capability_authorizations_changed"] is False
    assert (ROOT / state["task_path"]).is_file()
    assert (ROOT / state["completion_report_path"]).is_file()
    assert TASK_ID in ACTIVE_TASK.read_text(encoding="utf-8")
    assert TASK_ID in REPORT.read_text(encoding="utf-8")
    agents = AGENTS.read_text(encoding="utf-8")
    stable_paths: tuple[str, ...] = (
        "docs/execution/EXECUTION_STATE.json",
        "docs/execution/ACTIVE_TASK.md",
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
        assert state["merge_authorized"] is False
