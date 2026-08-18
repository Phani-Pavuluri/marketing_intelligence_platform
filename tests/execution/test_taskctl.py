from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from mip.execution.errors import TaskControlError
from mip.execution.state import (
    ALLOWED_STATUSES,
    PROTECTED_AUTHORITY_FIELDS,
    TRANSITIONS,
    transition_state,
    validate_state,
)
from mip.execution.taskctl import check_repository, sync_repository
from mip.execution.views import BEGIN_MARKER, END_MARKER, render_execution_view

SHA_A = "a" * 40
SHA_B = "b" * 40
SHA_C = "c" * 40


def authorized_state() -> dict[str, object]:
    return {
        "schema_version": "mip_repo_execution_state_v2",
        "repository": "Phani-Pavuluri/marketing_intelligence_platform",
        "task_id": "EXAMPLE_001",
        "status": "authorized",
        "execution_mode": "branch_and_fast_forward",
        "base_sha": SHA_A,
        "task_authoring_head_sha": SHA_B,
        "authorization_head_sha": SHA_B,
        "feature_branch": "feat/example-001",
        "feature_branch_created": True,
        "local_feature_branch_cleanup": "not_applicable_before_merge",
        "remote_feature_branch_cleanup": "not_applicable_before_merge",
        "task_execution_authorized": True,
        "correction_execution_authorized": False,
        "merge_authorized": False,
        "pr_creation_authorized": False,
        "reviewed_head_sha": None,
        "rejected_review_head_sha": None,
        "implementation_commit_sha": None,
        "rejected_implementation_commit_sha": None,
        "approval_commit_sha": None,
        "capability_authorizations_changed": False,
        "blockers": [],
        "maximum_correction_cycles": 1,
        "correction_cycles_completed": 0,
        "correction_cycles_remaining": 1,
        "review_decision": "authorized",
        "coordination_refresh_authorized": False,
        "product_or_analytical_changes_authorized": False,
        "geox_certification_authorized": False,
        "mmm_implementation_authorized": False,
        "mip_bridge_resume_authorized": False,
        "calibration_signal_construction_authorized": False,
        "simulation_authorized": False,
        "optimization_authorized": False,
        "planning_authorized": False,
        "recommendation_authorized": False,
        "runtime_integration_authorized": False,
        "real_data_authorized": False,
        "pilot_authorized": False,
        "production_authorized": False,
        "next_task_authorized": False,
    }


def write_repository(root: Path, state: dict[str, object]) -> tuple[str, str]:
    execution = root / "docs" / "execution"
    execution.mkdir(parents=True)
    (root / "pyproject.toml").write_text("[tool.poetry]\nname='test'\n", encoding="utf-8")
    state_path = execution / "EXECUTION_STATE.json"
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    active_body = "\n## Contract body\n\nKeep this exact.\n"
    report_body = "\n## Evidence body\n\nKeep this exact too.\n"
    (execution / "ACTIVE_TASK.md").write_text(
        render_execution_view(state, document="active_task") + active_body,
        encoding="utf-8",
    )
    (execution / "LATEST_COMPLETION_REPORT.md").write_text(
        render_execution_view(state, document="completion_report") + report_body,
        encoding="utf-8",
    )
    return active_body, report_body


def test_allowed_states_and_transition_edges_are_declared_and_deterministic() -> None:
    assert frozenset(TRANSITIONS) == ALLOWED_STATUSES
    assert all(isinstance(targets, frozenset) for targets in TRANSITIONS.values())
    assert TRANSITIONS["ready_for_review"] == frozenset({"changes_requested", "merged"})
    assert "approved_for_merge" not in ALLOWED_STATUSES


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        ({"status": "unknown"}, "E_STATE_STATUS"),
        ({"merge_authorized": True}, "E_STATE_MERGE_AUTHORITY"),
        ({"blockers": ["duplicate", "duplicate"]}, "E_STATE_BLOCKERS"),
        ({"feature_branch": "main"}, "E_STATE_BRANCH"),
        ({"authorization_head_sha": "short"}, "E_STATE_SHA"),
    ],
)
def test_invalid_state_combinations_have_stable_reason_codes(
    mutation: dict[str, object], reason: str
) -> None:
    state = authorized_state()
    state.update(mutation)
    with pytest.raises(TaskControlError, match=f"^{reason}:"):
        validate_state(state)


def test_check_detects_divergent_active_task_status(tmp_path: Path) -> None:
    state = authorized_state()
    write_repository(tmp_path, state)
    active = tmp_path / "docs/execution/ACTIVE_TASK.md"
    active.write_text(active.read_text().replace("`authorized`", "`blocked`", 1))
    with pytest.raises(TaskControlError, match="^E_VIEW_DIVERGENCE:"):
        check_repository(tmp_path)


@pytest.mark.parametrize(
    "label", ["Blockers", "Correction cycles remaining", "Implementation commit"]
)
def test_check_detects_divergent_completion_snapshot(tmp_path: Path, label: str) -> None:
    state = authorized_state()
    write_repository(tmp_path, state)
    report = tmp_path / "docs/execution/LATEST_COMPLETION_REPORT.md"
    text = report.read_text()
    line = next(item for item in text.splitlines() if f"**{label}:**" in item)
    report.write_text(text.replace(line, f"- **{label}:** `corrupt`"))
    with pytest.raises(TaskControlError, match="^E_VIEW_DIVERGENCE:"):
        check_repository(tmp_path)


def test_sync_repairs_only_generated_blocks_and_preserves_bodies(tmp_path: Path) -> None:
    state = authorized_state()
    active_body, report_body = write_repository(tmp_path, state)
    for name in ("ACTIVE_TASK.md", "LATEST_COMPLETION_REPORT.md"):
        path = tmp_path / "docs/execution" / name
        path.write_text(path.read_text().replace("`authorized`", "`blocked`", 1))
    sync_repository(tmp_path)
    assert (tmp_path / "docs/execution/ACTIVE_TASK.md").read_text().endswith(active_body)
    assert (tmp_path / "docs/execution/LATEST_COMPLETION_REPORT.md").read_text().endswith(
        report_body
    )
    check_repository(tmp_path)


def test_sync_is_byte_idempotent(tmp_path: Path) -> None:
    write_repository(tmp_path, authorized_state())
    sync_repository(tmp_path)
    paths = [
        tmp_path / "docs/execution/ACTIVE_TASK.md",
        tmp_path / "docs/execution/LATEST_COMPLETION_REPORT.md",
    ]
    first = [path.read_bytes() for path in paths]
    sync_repository(tmp_path)
    assert [path.read_bytes() for path in paths] == first


@pytest.mark.parametrize(
    "contents",
    [
        "no markers",
        f"{BEGIN_MARKER}\n{BEGIN_MARKER}\n{END_MARKER}",
        f"{END_MARKER}\n{BEGIN_MARKER}",
    ],
)
def test_sync_refuses_malformed_markers(tmp_path: Path, contents: str) -> None:
    write_repository(tmp_path, authorized_state())
    (tmp_path / "docs/execution/ACTIVE_TASK.md").write_text(contents)
    with pytest.raises(TaskControlError, match="^E_VIEW_MARKERS:"):
        sync_repository(tmp_path)


def test_ready_for_review_requires_explicit_implementation_and_cleared_blockers() -> None:
    state = authorized_state()
    with pytest.raises(TaskControlError, match="^E_TRANSITION_EVIDENCE:"):
        transition_state(state, "ready_for_review")

    blocked = copy.deepcopy(state)
    blocked.update(
        status="blocked",
        review_decision="blocked",
        blockers=["WAIT"],
        implementation_commit_sha=SHA_A,
    )
    validate_state(blocked)
    with pytest.raises(TaskControlError, match="^E_TRANSITION_BLOCKER:"):
        transition_state(blocked, "ready_for_review", implementation_sha=SHA_C)


def test_authorized_can_enter_pre_implementation_blocked_state() -> None:
    state = authorized_state()
    blocked = transition_state(state, "blocked", blockers=["BOOTSTRAP_FAILED"])
    assert blocked["status"] == "blocked"
    assert blocked["implementation_commit_sha"] is None
    assert blocked["blockers"] == ["BOOTSTRAP_FAILED"]
    validate_state(blocked)


def test_direct_pre_implementation_blocked_state_is_valid() -> None:
    state = authorized_state()
    state.update(status="blocked", review_decision="blocked", blockers=["DEPENDENCY_MISSING"])
    validate_state(state)


def test_blocked_without_blockers_remains_invalid() -> None:
    state = authorized_state()
    state.update(status="blocked", review_decision="blocked")
    with pytest.raises(TaskControlError, match="^E_STATE_BLOCKED:"):
        validate_state(state)


def test_blocked_with_implementation_provenance_remains_valid() -> None:
    state = authorized_state()
    state.update(
        status="blocked",
        review_decision="blocked",
        blockers=["ENVIRONMENT_UNAVAILABLE"],
        implementation_commit_sha=SHA_C,
    )
    validate_state(state)


def test_blocked_returns_to_in_progress_after_explicit_clear() -> None:
    blocked = transition_state(
        authorized_state(), "blocked", blockers=["ANCESTRY_UNVERIFIED"]
    )
    resumed = transition_state(blocked, "in_progress", clear_blockers=True)
    assert resumed["status"] == "in_progress"
    assert resumed["blockers"] == []
    assert resumed["implementation_commit_sha"] is None
    validate_state(resumed)


def test_in_progress_to_blocked_preserves_existing_implementation_provenance() -> None:
    state = authorized_state()
    state.update(
        status="in_progress",
        review_decision="in_progress",
        implementation_commit_sha=SHA_C,
    )
    blocked = transition_state(state, "blocked", blockers=["ENVIRONMENT_UNAVAILABLE"])
    assert blocked["implementation_commit_sha"] == SHA_C
    validate_state(blocked)


def test_pre_implementation_block_transition_preserves_protected_authority() -> None:
    state = authorized_state()
    blocked = transition_state(state, "blocked", blockers=["REPOSITORY_STATE_UNSAFE"])
    for field in PROTECTED_AUTHORITY_FIELDS:
        assert blocked.get(field) == state.get(field)


def test_correction_counter_mismatch_and_implicit_completion_are_rejected() -> None:
    state = authorized_state()
    state["correction_cycles_remaining"] = 0
    with pytest.raises(TaskControlError, match="^E_STATE_CORRECTION_COUNTER:"):
        validate_state(state)

    correction = authorized_state()
    correction.update(
        status="changes_requested",
        review_decision="changes_requested",
        implementation_commit_sha=SHA_A,
        rejected_review_head_sha=SHA_B,
        rejected_implementation_commit_sha=SHA_A,
        correction_execution_authorized=True,
    )
    validate_state(correction)
    with pytest.raises(TaskControlError, match="^E_TRANSITION_CORRECTION_COUNTER:"):
        transition_state(correction, "ready_for_review", implementation_sha=SHA_C)
    result = transition_state(
        correction,
        "ready_for_review",
        implementation_sha=SHA_C,
        complete_correction=True,
    )
    assert result["correction_cycles_completed"] == 1
    assert result["correction_cycles_remaining"] == 0


@pytest.mark.parametrize(
    "mutation",
    [
        {"reviewed_head_sha": None},
        {"task_execution_authorized": True},
        {"remote_feature_branch_cleanup": "still_present"},
    ],
)
def test_merged_closure_contradictions_are_rejected(mutation: dict[str, object]) -> None:
    state = authorized_state()
    state.update(
        status="merged",
        review_decision="merged",
        task_execution_authorized=False,
        implementation_commit_sha=SHA_A,
        reviewed_head_sha=SHA_B,
        feature_branch_created=False,
        local_feature_branch_cleanup="observed_deleted",
        remote_feature_branch_cleanup="observed_deleted",
    )
    state.update(mutation)
    with pytest.raises(TaskControlError):
        validate_state(state)


def test_transition_preserves_product_and_capability_authority() -> None:
    state = authorized_state()
    result = transition_state(state, "ready_for_review", implementation_sha=SHA_C)
    for field in PROTECTED_AUTHORITY_FIELDS:
        assert result.get(field) == state.get(field)


def test_migrated_repository_tree_passes_check() -> None:
    check_repository(Path(__file__).parents[2])
