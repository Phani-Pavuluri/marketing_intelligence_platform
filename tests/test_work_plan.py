"""Behavior-based tests for the MIP bounded work plan validator."""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from mip.execution import work_plan
from mip.execution.work_plan import (
    canonical_digest,
    is_valid_branch,
    path_violation,
    validate_file,
    validate_plan_object,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

BASE_TASK = {
    "task_id": "TASK_ONE_001",
    "feature_branch": "feat/task-one-001",
    "outcome": "Deliver the first outcome.",
    "observable_behavior": "Files exist with expected content.",
    "owned_paths": ["docs/plan/ONE.md"],
    "acceptance_evidence": ["pytest passes"],
    "risk_tier": 1,
    "depends_on": [],
    "unresolved_design_questions": [],
}


def make_plan(**overrides: object) -> dict[str, Any]:
    plan = {
        "schema_version": 1,
        "repository": "Phani-Pavuluri/marketing_intelligence_platform",
        "plan_id": "PLAN_DEMO_001",
        "goal": "Demonstrate bounded planning.",
        "exclusions": ["no production writes"],
        "tasks": [dict(BASE_TASK)],
    }
    plan.update(overrides)
    return plan


def write_plan(path: Path, content: object) -> Path:
    path.write_text(
        json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return path


def run_cli(plan_path: Path, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "mip.execution.work_plan", "validate", "--plan", str(plan_path)],
        capture_output=True,
        text=True,
        cwd=str(cwd or REPO_ROOT),
        timeout=120,
    )


def test_valid_minimal_plan_is_accepted() -> None:
    valid, plan_id, ordered, problems = validate_plan_object(make_plan())
    assert valid is True
    assert plan_id == "PLAN_DEMO_001"
    assert ordered == ["TASK_ONE_001"]
    assert problems == []


def test_sequenced_shared_path_plan_orders_deterministically() -> None:
    first = dict(BASE_TASK, task_id="TASK_A_001", feature_branch="feat/a-001")
    second = dict(
        BASE_TASK,
        task_id="TASK_B_001",
        feature_branch="feat/b-001",
        owned_paths=["docs/plan/ONE.md"],
        depends_on=["TASK_A_001"],
    )
    valid, _, ordered, problems = validate_plan_object(make_plan(tasks=[second, first]))
    assert valid is True
    assert ordered == ["TASK_A_001", "TASK_B_001"]
    assert problems == []


def test_independent_tasks_use_lexicographic_order() -> None:
    first = dict(BASE_TASK, task_id="TASK_Z_001", feature_branch="feat/z-001")
    second = dict(
        BASE_TASK,
        task_id="TASK_A_001",
        feature_branch="feat/a-001",
        owned_paths=["docs/plan/TWO.md"],
    )
    valid, _, ordered, _ = validate_plan_object(make_plan(tasks=[first, second]))
    assert valid is True
    assert ordered == ["TASK_A_001", "TASK_Z_001"]


def test_shared_path_without_sequencing_is_rejected() -> None:
    other = dict(BASE_TASK, task_id="TASK_TWO_001", feature_branch="feat/two-001")
    valid, _, ordered, problems = validate_plan_object(make_plan(tasks=[BASE_TASK, other]))
    assert valid is False
    assert ordered == []
    assert any(p["code"] == "TASK_OVERLAPPING_PATHS" for p in problems)


def test_digest_is_stable_across_key_order_and_formatting(tmp_path: Path) -> None:
    plan = make_plan()
    first = tmp_path / "a.json"
    second = tmp_path / "b.json"
    first.write_text(json.dumps(plan, indent=4, sort_keys=False), encoding="utf-8")
    second.write_text(json.dumps(plan, separators=(",", ":"), sort_keys=True), encoding="utf-8")
    result_a, code_a = validate_file(first)
    result_b, code_b = validate_file(second)
    assert (code_a, code_b) == (0, 0)
    assert result_a["plan_sha256"] == result_b["plan_sha256"]
    assert result_a["execution_authorized"] is False
    assert len(result_a["plan_sha256"]) == 64


def test_canonical_digest_matches_documented_algorithm() -> None:
    plan = make_plan()
    expected = __import__("hashlib").sha256(
        json.dumps(plan, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode(
            "utf-8"
        )
    ).hexdigest()
    assert canonical_digest(plan) == expected


@pytest.mark.parametrize(
    ("mutate", "code"),
    [
        (lambda p: p.pop("goal"), "PLAN_GOAL"),
        (lambda p: p.update(schema_version=True), "PLAN_SCHEMA_VERSION"),
        (lambda p: p.update(schema_version=2), "PLAN_SCHEMA_VERSION"),
        (lambda p: p.update(repository="other/repo"), "PLAN_REPOSITORY"),
        (lambda p: p.update(plan_id="lowercase"), "PLAN_ID"),
        (lambda p: p.update(exclusions=[]), "PLAN_EXCLUSIONS"),
        (lambda p: p.update(tasks=[]), "PLAN_TASKS"),
        (lambda p: p.update(extra_field=1), "PLAN_UNKNOWN_FIELD"),
    ],
)
def test_plan_level_rejections(
    mutate: Callable[[dict[str, Any]], None], code: str
) -> None:
    plan = make_plan()
    mutate(plan)
    valid, _, _, problems = validate_plan_object(plan)
    assert valid is False
    assert any(p["code"] == code for p in problems)


def task_with(**fields: object) -> dict[str, Any]:
    task = dict(BASE_TASK)
    task.update(fields)
    return task


@pytest.mark.parametrize(
    ("fields", "code"),
    [
        ({"risk_tier": True}, "TASK_RISK_TIER"),
        ({"risk_tier": 4}, "TASK_RISK_TIER"),
        ({"feature_branch": "main"}, "TASK_BRANCH"),
        ({"feature_branch": "bad branch"}, "TASK_BRANCH"),
        ({"feature_branch": "../escape"}, "TASK_BRANCH"),
        ({"owned_paths": ["/absolute/path.md"]}, "TASK_PATH"),
        ({"owned_paths": ["a/../b.md"]}, "TASK_PATH"),
        ({"owned_paths": ["docs/tasks/local.md"]}, "TASK_PATH"),
        ({"owned_paths": [".codex/state.json"]}, "TASK_PATH"),
        ({"owned_paths": ["docs/execution/ACTIVE_TASK.md"]}, "TASK_PATH"),
        ({"owned_paths": ["src/*.py"]}, "TASK_PATH"),
        ({"owned_paths": []}, "TASK_PATHS"),
        ({"unresolved_design_questions": ["open?"]}, "TASK_UNRESOLVED_DESIGN"),
        ({"acceptance_evidence": []}, "TASK_EVIDENCE"),
        ({"depends_on": ["TASK_ONE_001"]}, "TASK_DEPENDS_SELF"),
        ({"depends_on": ["MISSING_001"]}, "TASK_DEPENDS_MISSING"),
        ({"outcome": "   "}, "TASK_OUTCOME"),
        ({"surprise": 1}, "TASK_UNKNOWN_FIELD"),
    ],
)
def test_task_level_rejections(fields: dict[str, Any], code: str) -> None:
    valid, _, _, problems = validate_plan_object(make_plan(tasks=[task_with(**fields)]))
    assert valid is False
    assert any(p["code"] == code for p in problems)


def test_duplicate_ids_branches_and_dependencies_rejected() -> None:
    twin = dict(BASE_TASK, feature_branch="feat/other-001")
    valid, _, _, problems = validate_plan_object(make_plan(tasks=[BASE_TASK, twin]))
    assert valid is False
    assert any(p["code"] == "TASK_DUPLICATE_ID" for p in problems)

    same_branch = dict(BASE_TASK, task_id="TASK_TWO_001")
    valid, _, _, problems = validate_plan_object(make_plan(tasks=[BASE_TASK, same_branch]))
    assert valid is False
    assert any(p["code"] == "TASK_DUPLICATE_BRANCH" for p in problems)

    dup_dep = task_with(task_id="TASK_TWO_001", feature_branch="feat/two-001",
                        owned_paths=["docs/plan/TWO.md"],
                        depends_on=["TASK_ONE_001", "TASK_ONE_001"])
    valid, _, _, problems = validate_plan_object(make_plan(tasks=[BASE_TASK, dup_dep]))
    assert valid is False
    assert any(p["code"] == "TASK_DEPENDS_DUPLICATE" for p in problems)


def test_dependency_cycle_rejected() -> None:
    first = task_with(depends_on=["TASK_B_001"], owned_paths=["docs/plan/A.md"])
    second = task_with(
        task_id="TASK_B_001",
        feature_branch="feat/b-001",
        owned_paths=["docs/plan/B.md"],
        depends_on=["TASK_ONE_001"],
    )
    valid, _, ordered, problems = validate_plan_object(make_plan(tasks=[first, second]))
    assert valid is False
    assert ordered == []
    assert any(p["code"] == "TASK_DEPENDS_CYCLE" for p in problems)


@pytest.mark.parametrize(
    ("branch", "expected"),
    [
        ("feat/ok-001", True),
        ("@", True),
        ("a-b_c/d.e-f", True),
        ("v1.0-rc1", True),
        ("UPPER/lower-1_2.3", True),
        ("a/b/c", True),
        ("a/-b", True),
        ("main", False),
        ("", False),
        ("-feature", False),
        ("-a/b", False),
        ("feature.lock", False),
        ("feature.lock/child", False),
        ("feature/part.lock/child", False),
        ("a.lock/b", False),
        ("has space", False),
        ("double//slash", False),
        (".leading-dot", False),
        ("a/.b", False),
        ("trailing.", False),
        ("ends.lock", False),
        ("at@{sign", False),
        ("star*.txt", False),
    ],
)
def test_branch_names(branch: str, expected: bool) -> None:
    assert is_valid_branch(branch) is expected


def test_branch_acceptance_implies_git_acceptance() -> None:
    """Acceptance here must imply acceptance by real Git in both ref forms."""
    names = [
        "feat/ok-001",
        "@",
        "a-b_c/d.e-f",
        "v1.0-rc1",
        "UPPER/lower-1_2.3",
        "a/b/c",
        "a/-b",
        "docs/plan/x",
    ]
    for name in names:
        assert is_valid_branch(name) is True
        for command in (
            ["git", "check-ref-format", f"refs/heads/{name}"],
            ["git", "check-ref-format", "--branch", name],
        ):
            proc = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert proc.returncode == 0, (name, command)


def test_git_rejected_branches_are_rejected() -> None:
    """Names real Git rejects must also be rejected here."""
    names = [
        "feature.lock/child",
        "feature/part.lock/child",
        "feature.lock",
        "double//slash",
        ".leading-dot",
        "a/.b",
        "trailing.",
        "at@{sign",
    ]
    for name in names:
        proc = subprocess.run(
            ["git", "check-ref-format", f"refs/heads/{name}"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert proc.returncode != 0, name
        assert is_valid_branch(name) is False


@pytest.mark.parametrize(
    ("candidate", "rejected"),
    [
        ("docs/ok.md", False),
        ("/absolute.md", True),
        ("a/../b.md", True),
        ("a/./b.md", True),
        ("docs/tasks/x.md", True),
        (".codex/x.json", True),
        ("x/.git/config", True),
        ("docs/execution/EXECUTION_STATE.json", True),
        ("glob/*.py", True),
        ("back\\slash.md", True),
        ("trailing/", True),
    ],
)
def test_owned_paths(candidate: str, rejected: bool) -> None:
    assert (path_violation(candidate) is not None) is rejected


def test_cli_accepts_valid_plan(tmp_path: Path) -> None:
    plan_path = write_plan(tmp_path / "plan.json", make_plan())
    proc = run_cli(plan_path)
    assert proc.returncode == 0, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["valid"] is True
    assert payload["execution_authorized"] is False
    assert payload["ordered_task_ids"] == ["TASK_ONE_001"]
    assert payload["problems"] == []
    assert "Traceback" not in proc.stderr


def test_cli_reports_constraint_violations_with_exit_2(tmp_path: Path) -> None:
    plan = make_plan()
    plan["tasks"][0]["risk_tier"] = 9
    proc = run_cli(write_plan(tmp_path / "plan.json", plan))
    assert proc.returncode == 2, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["valid"] is False
    assert payload["execution_authorized"] is False
    assert payload["plan_sha256"] is None
    assert payload["ordered_task_ids"] == []
    assert "Traceback" not in proc.stderr


@pytest.mark.parametrize("raw", ["{not json"])
def test_cli_reports_malformed_input_with_exit_3(tmp_path: Path, raw: str) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_bytes(raw.encode("utf-8", errors="surrogateescape"))
    proc = run_cli(plan_path)
    assert proc.returncode == 3, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["valid"] is False
    assert payload["plan_id"] is None
    assert payload["execution_authorized"] is False
    assert "Traceback" not in proc.stderr


def test_cli_reports_non_utf8_input_with_exit_3(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_bytes(b'{"goal": "\xff\xfe"}')
    proc = run_cli(plan_path)
    assert proc.returncode == 3, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["valid"] is False
    assert payload["execution_authorized"] is False
    assert "Traceback" not in proc.stderr


@pytest.mark.parametrize("raw", ["[1, 2, 3]", '"just a string"', "42", "null"])
def test_cli_reports_non_object_json_with_exit_2(tmp_path: Path, raw: str) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(raw, encoding="utf-8")
    proc = run_cli(plan_path)
    assert proc.returncode == 2, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["valid"] is False
    assert payload["execution_authorized"] is False
    assert any(p["code"] == "PLAN_TOP_LEVEL" for p in payload["problems"])
    assert "Traceback" not in proc.stderr


def test_cli_reports_lone_surrogate_text_as_structured_failure(tmp_path: Path) -> None:
    plan = make_plan()
    plan["goal"] = "surrogate \ud800 here"
    plan_path = tmp_path / "plan.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=True), encoding="utf-8")
    proc = run_cli(plan_path)
    assert proc.returncode == 3, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["valid"] is False
    assert payload["execution_authorized"] is False
    assert payload["plan_sha256"] is None
    assert "Traceback" not in proc.stderr


def test_cli_reports_deep_nesting_as_structured_failure(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text("[" * 1100 + "]" * 1100, encoding="utf-8")
    proc = run_cli(plan_path)
    assert proc.returncode == 3, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["valid"] is False
    assert payload["execution_authorized"] is False
    assert "Traceback" not in proc.stderr


def test_cli_rejects_duplicate_keys_with_exit_3(tmp_path: Path) -> None:
    plan_path = tmp_path / "plan.json"
    plan_path.write_text('{"schema_version": 1, "schema_version": 1}', encoding="utf-8")
    proc = run_cli(plan_path)
    assert proc.returncode == 3, proc.stderr
    assert json.loads(proc.stdout)["valid"] is False


def test_cli_handles_missing_and_oversized_input(tmp_path: Path) -> None:
    missing = run_cli(tmp_path / "absent.json")
    assert missing.returncode == 3
    assert json.loads(missing.stdout)["valid"] is False
    assert "Traceback" not in missing.stderr

    big = tmp_path / "big.json"
    big.write_bytes(b'{"pad": "' + b"x" * (1024 * 1024) + b'"}')
    proc = run_cli(big)
    assert proc.returncode == 3, proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["valid"] is False
    assert payload["execution_authorized"] is False
    assert any(p["code"] == "INPUT_OVERSIZED" for p in payload["problems"])
    assert "Traceback" not in proc.stderr


def test_cli_performs_no_repository_mutation(tmp_path: Path) -> None:
    before = {item.name for item in tmp_path.iterdir()}
    plan_path = write_plan(tmp_path / "plan.json", make_plan())
    proc = run_cli(plan_path, cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    after = {item.name for item in tmp_path.iterdir()}
    assert after == before | {"plan.json"}


def test_validator_has_no_side_effect_channels() -> None:
    source = Path(work_plan.__file__).read_text(encoding="utf-8")
    for channel in ("subprocess", "socket", "urllib", "http.client", "taskctl"):
        assert f"import {channel}" not in source
        assert f"from {channel}" not in source


def test_schema_file_is_well_formed() -> None:
    schema = json.loads(
        (REPO_ROOT / "src" / "mip" / "execution" / "work_plan.schema.json").read_text(
            encoding="utf-8"
        )
    )
    assert schema["title"].startswith("MIP bounded work plan")
    assert schema["properties"]["tasks"]["maxItems"] == 100
    assert set(schema["required"]) >= {"plan_id", "goal", "tasks"}
