"""Acceptance checks for the delegated routine merge preflight verifier.

Isolated Git remotes, synthetic observer bundles, and fixture notes only.
Never contacts production sessions, never performs Codex inference, and never
mutates branches or worktrees outside the dedicated notes ref under test.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from mip.execution import delegated_merge as dm
from mip.execution import review_observer as observer_module
from mip.execution.delegated_merge import DelegatedError
from mip.execution.opencode_advisory import Binding
from mip.execution.review_observer import Observer
from mip.execution.state import validate_state
from mip.execution.views import render_execution_view

LIVE_STATE_PATH = (Path(__file__).parents[1] / "docs/execution/EXECUTION_STATE.json").resolve()

Env = tuple[Path, Path, Path, dict[str, Any], dict[str, str]]

REVIEWER_UUID = "11111111-2222-4333-8444-555555555555"
OTHER_UUID = "22222222-3333-4444-8555-666666666666"
IMPL_SESSION = "ses_fixtureimpl001"
POLICY_VERSION = "fixture-policy-v1"
RECEIPT_UUID = "bbbbbbbb-cccc-4ddd-8eee-ffffffffffff"
ACT_UUID = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
POLICY_TEXT = "Fixture delegation policy v1.\n"


@pytest.fixture(autouse=True)
def _forbid_live_state_template(monkeypatch: pytest.MonkeyPatch) -> None:
    real_read_text = Path.read_text

    def guarded(self: Path, *args: Any, **kwargs: Any) -> str:
        if self.resolve() == LIVE_STATE_PATH:
            raise AssertionError("fixture must not read the live execution-state template")
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded)


def canonical_fixture_state(risk_tier: str = "tier_2_fixture_routine") -> dict[str, Any]:
    state: dict[str, Any] = {
        "schema_version": "mip_repo_execution_state_v2",
        "repository": "Phani-Pavuluri/marketing_intelligence_platform",
        "task_id": "FIXTURE_DELEGATED_001",
        "status": "proposed",
        "review_decision": "proposed",
        "execution_mode": "branch_and_fast_forward",
        "base_branch": "main",
        "authorization_head_convention": "fixture-owned provenance",
        "finalized_branch_baseline_resolution": "fixture-owned baseline",
        "task_path": "docs/execution/ACTIVE_TASK.md",
        "completion_report_path": "docs/execution/LATEST_COMPLETION_REPORT.md",
        "feature_branch": "feat/fixture-delegated",
        "feature_branch_created": True,
        "base_sha": "0" * 40,
        "task_authoring_start_sha": "0" * 40,
        "task_authoring_head_sha": None,
        "authorization_head_sha": None,
        "implementation_commit_sha": None,
        "reviewed_head_sha": None,
        "rejected_review_head_sha": None,
        "rejected_implementation_commit_sha": None,
        "approval_commit_sha": None,
        "local_feature_branch_cleanup": None,
        "remote_feature_branch_cleanup": None,
        "owned_implementation_paths": ["product.py"],
        "task_authoring_boundary": [
            "docs/execution/ACTIVE_TASK.md",
            "docs/execution/EXECUTION_STATE.json",
            "docs/execution/LATEST_COMPLETION_REPORT.md",
        ],
        "risk_tier": risk_tier,
        "validation_scope": "fixture",
        "compatibility_migration_policy": "not_applicable_fixture_only",
        "merge_approval_mode": "delegated_routine",
        "delegated_merge_required_validation": ["focused_tests", "taskctl_check", "git_diff_check"],
        "full_suite_validation_required": False,
        "blockers": [],
        "maximum_correction_cycles": 1,
        "correction_cycles_completed": 0,
        "correction_cycles_remaining": 1,
        "task_execution_authorized": False,
        "correction_execution_authorized": False,
        "merge_authorized": False,
        "pr_creation_authorized": False,
        "coordination_refresh_authorized": False,
        "audit_artifact_authorized": False,
        "execution_governance_changes_authorized": False,
        "product_or_analytical_changes_authorized": False,
        "geox_certification_authorized": False,
        "mmm_implementation_authorized": False,
        "mip_bridge_resume_authorized": False,
        "calibration_signal_construction_authorized": False,
        "simulation_authorized": False,
        "optimization_authorized": False,
        "planning_authorized": False,
        "llm_evaluation_implementation_authorized": False,
        "llm_infrastructure_authorized": False,
        "package_integration_authorized": False,
        "artifact_lifecycle_implementation_authorized": False,
        "recommendation_authorized": False,
        "runtime_integration_authorized": False,
        "real_data_authorized": False,
        "pilot_authorized": False,
        "production_authorized": False,
        "capability_authorizations_changed": False,
        "next_task_authorized": False,
    }
    validate_state(state)
    return state


def git(root: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(root), *args], text=True).strip()


def commit(root: Path, message: str) -> str:
    git(root, "add", ".")
    git(root, "commit", "-qm", message)
    return git(root, "rev-parse", "HEAD")


def write_state(root: Path, state: dict[str, Any]) -> None:
    directory = root / "docs/execution"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "EXECUTION_STATE.json").write_text(json.dumps(state))
    for name, document in (
        ("ACTIVE_TASK.md", "active_task"),
        ("LATEST_COMPLETION_REPORT.md", "completion_report"),
    ):
        (directory / name).write_text(
            render_execution_view(state, document=document)
            + (
                "\nTask: fixture total contract.\n"
                if document == "active_task"
                else "\nCompletion claim: fixture checks passed.\n"
            )
        )


@pytest.fixture
def environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Env:
    return _make_environment(tmp_path, monkeypatch, "tier_2_fixture_routine")


@pytest.fixture
def environment_tier3(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Env:
    return _make_environment(tmp_path, monkeypatch, "tier_3_fixture_authority")


def _make_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, risk_tier: str) -> Env:
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    root = tmp_path / "review"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Fixture author")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "remote", "add", "origin", str(remote))
    monkeypatch.setattr(observer_module, "EXPECTED_ORIGIN", str(remote))
    monkeypatch.setattr(dm, "EXPECTED_ORIGIN", str(remote))
    policy = root / "docs/execution/DELEGATED_ROUTINE_MERGE_POLICY.md"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(POLICY_TEXT)
    (root / "product.py").write_text("def total(values):\n    return sum(values)\n")
    (root / ".gitignore").write_text(".codex/\n")
    base = commit(root, "base")
    state = canonical_fixture_state(risk_tier)
    state.update(base_sha=base, task_authoring_start_sha=base)
    write_state(root, state)
    authorization = commit(root, "authorize contract")
    state.update(
        authorization_head_sha=authorization,
        task_authoring_head_sha=authorization,
        status="authorized",
        review_decision="authorized",
        task_execution_authorized=True,
    )
    write_state(root, state)
    main_head = commit(root, "finalize authority")
    git(root, "push", "-q", "origin", "main")
    git(root, "switch", "-qc", "feat/fixture-delegated")
    implementation = tmp_path / "implementation"
    subprocess.run(["git", "clone", "-q", str(remote), str(implementation)], check=True)
    ids = {"base": base, "auth": authorization, "main": main_head}
    return root, implementation, remote, state, ids


@pytest.fixture
def env(environment: Env) -> Env:
    return environment


def publish(env: Env) -> str:
    root, _, _, state, ids = env
    (root / "product.py").write_text("def total(values):\n    return sum(values) + 1\n")
    implementation = commit(root, "implement")
    ids["impl"] = implementation
    state.update(
        status="ready_for_review",
        review_decision="ready_for_review",
        implementation_commit_sha=implementation,
    )
    write_state(root, state)
    head = commit(root, "publish validation receipt")
    ids["reviewed"] = head
    git(root, "push", "-q", "origin", "feat/fixture-delegated")
    return head


def fake_result(checkpoint: Any) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "repository": observer_module.REPOSITORY,
        "task_id": checkpoint.state["task_id"],
        "checkpoint_kind": checkpoint.kind,
        "reviewed_sha": checkpoint.sha,
        "verdict": "pass",
        "summary": "Fixture advisory pass.",
        "findings": [],
        "limitations": ["Synthetic fixture; no readiness claim."],
        "owner_update": {
            "goal_impact": "Checks the fixture change.",
            "completed": [],
            "ongoing": [],
            "planned": [],
            "issues": [],
            "decisions_needed": [],
            "recommendation": "Inspect the evidence before deciding.",
        },
    }


def review_completed(env: Env, monkeypatch: pytest.MonkeyPatch) -> tuple[str, Path, dict[str, Any]]:
    root, _, _, state, _ = env
    observer = Observer(root)
    assert observer.execute("init") == 0
    publish(env)

    def run(bundle: Path, report: Path) -> dict[str, Any]:
        manifest = json.loads((bundle / "manifest.json").read_text())
        checkpoint = observer.checkpoint(manifest["ref"], manifest["reviewed_sha"])
        assert checkpoint is not None
        (report / "events.jsonl").write_text(
            json.dumps({"type": "thread.started", "thread_id": REVIEWER_UUID})
            + "\n"
            + json.dumps({"type": "turn.completed", "thread_id": REVIEWER_UUID}) + "\n"
        )
        (report / "model-output.json").write_text(json.dumps({"ok": True}))
        return fake_result(checkpoint)

    monkeypatch.setattr(observer, "run_codex", run)
    assert observer.execute("scan") == 0
    ledger = observer.load()
    assert len(ledger.events) == 1
    key = next(iter(ledger.events))
    event = ledger.events[key]
    assert event.report is not None
    result = json.loads((Path(event.report) / "result.json").read_text())
    return key, Path(event.report), result


def write_binding(env: Env, session: str = IMPL_SESSION, project: str = "proj-fixture") -> None:
    root, implementation, remote, _, _ = env
    binding = Binding(
        schema_version=1,
        repository=observer_module.REPOSITORY,
        review_repository=str(root.resolve()),
        review_origin=str(remote),
        implementation_directory=str(implementation.resolve()),
        implementation_origin=str(remote),
        session_id=session,
        project_id=project,
        provider="opencode",
        model="muse-spark-1.3-contributor-free",
        variant="high",
        agent="build",
        bound_at="2026-10-15T00:00:00+00:00",
    )
    path = root / dm.ADVISORY_BINDING
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(binding.model_dump_json(indent=2) + "\n")


def reviewed_blob(env: Env, field: str) -> Any:
    root, _, _, _, ids = env
    text = git(root, "show", f"{ids['reviewed']}:docs/execution/EXECUTION_STATE.json")
    return json.loads(text)[field]


def policy_hash(env: Env) -> str:
    root, _, _, _, ids = env
    raw = subprocess.check_output(
        [
            "git",
            "-C",
            str(root),
            "show",
            f"{ids['main']}:docs/execution/DELEGATED_ROUTINE_MERGE_POLICY.md",
        ]
    )
    return hashlib.sha256(raw).hexdigest()


def result_digest(result: dict[str, Any]) -> str:
    return dm.digest_bytes(dm.canonical_json_bytes(result))


def make_receipt(
    env: Env,
    report: Path,
    result: dict[str, Any],
    session: str = REVIEWER_UUID,
    impl_session: str = IMPL_SESSION,
) -> dict[str, Any]:
    root, _, _, _, ids = env
    _ = report
    categories: dict[str, Any] = {}
    for name in ("focused_tests", "taskctl_check", "git_diff_check"):
        categories[name] = {
            "status": "pass",
            "detail": f"{name}: 20 passed on fixture tree",
            "tree_sha": ids["reviewed"],
            "evidence": ["result.json", "events.jsonl"],
        }
    for name in ("docker_make_validate", "ruff", "mypy"):
        categories[name] = {
            "status": "not_required",
            "detail": f"{name}: outside fixture required set",
            "tree_sha": None,
            "evidence": [],
        }
    return {
        "schema_version": 1,
        "receipt_kind": "delegated_routine_merge_approval",
        "receipt_id": RECEIPT_UUID,
        "repository": observer_module.REPOSITORY,
        "task_id": "FIXTURE_DELEGATED_001",
        "feature_branch": "feat/fixture-delegated",
        "merge_approval_mode": "delegated_routine",
        "authorization_sha": ids["auth"],
        "implementation_sha": ids["impl"],
        "reviewed_remote_head_sha": ids["reviewed"],
        "main_baseline_sha": ids["main"],
        "reviewer": {
            "role": "independent_codex_reviewer",
            "session_id": session,
            "implementation_agent_session_id": impl_session,
            "reviewer_authored_implementation": False,
            "observer_report_digest": result_digest(result),
        },
        "decision": "approve_exact_reviewed_head",
        "issued_at": datetime.now(UTC).isoformat(),
        "delegation_provenance": {
            "policy_version": POLICY_VERSION,
            "activation_receipt_id": ACT_UUID,
            "activation_notes_ref": dm.DEDICATED_NOTES_REF,
            "owner_decision_ref": "fixture-owner-direction-2026-10-15",
            "user_reserved_unchanged": True,
            "activation_head_sha": ids["main"],
            "policy_sha256": policy_hash(env),
        },
        "validation": {"tier_class": 2, "categories": categories},
        "eligibility": {
            "tier_class": 2,
            "routine_assertions": {
                "within_authorized_scope": True,
                "no_contract_meaning_change": True,
                "no_architecture_change": True,
                "no_authority_change": True,
                "no_sibling_impact": True,
            },
            "quoted_state": {
                "risk_tier": reviewed_blob(env, "risk_tier"),
                "validation_scope": reviewed_blob(env, "validation_scope"),
                "owned_implementation_paths": reviewed_blob(env, "owned_implementation_paths"),
                "task_authoring_boundary": reviewed_blob(env, "task_authoring_boundary"),
                "merge_approval_mode": "delegated_routine",
                "capability_authorizations_changed": False,
                "all_protected_authority_false": True,
                "delegated_merge_required_validation": reviewed_blob(
                    env, "delegated_merge_required_validation"
                ),
                "full_suite_validation_required": reviewed_blob(
                    env, "full_suite_validation_required"
                ),
            },
            "findings": [
                {"condition": name, "result": "pass", "evidence": f"fixture evidence {name}"}
                for name in dm.REQUIRED_CONDITIONS
            ],
        },
        "authority_impact": {
            "capability_authority_added": False,
            "task_authorization_changed": False,
            "statement": "No authority added.",
        },
        "limitations": ["Fixture receipt; no merge authority."],
    }


def make_activation(env: Env) -> dict[str, Any]:
    _, _, _, _, ids = env
    return {
        "schema_version": 1,
        "receipt_kind": "delegation_activation",
        "receipt_id": ACT_UUID,
        "policy_version": POLICY_VERSION,
        "policy_sha256": policy_hash(env),
        "prerequisite_head_sha": ids["main"],
        "decision": "activate",
        "scope_tier_classes": [1, 2],
        "owner_decision_ref": "fixture-owner-direction-2026-10-15",
        "issued_at": datetime.now(UTC).isoformat(),
        "limitations": ["Fixture activation scope."],
    }


def notes_add(root: Path, target: str, payload: dict[str, Any]) -> None:
    text = dm.canonical_json_bytes(payload).decode("utf-8")
    subprocess.run(
        ["git", "-C", str(root), "notes", "--ref", dm.NOTES_SHORT_REF, "add", "-m", text, target],
        check=True,
        capture_output=True,
        text=True,
    )


def notes_push(env: Env) -> None:
    root, _, _, _, _ = env
    subprocess.run(
        ["git", "-C", str(root), "push", "-q", "origin", dm.DEDICATED_NOTES_REF],
        check=True,
    )


def eligible_setup(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> tuple[Path, dict[str, Any]]:
    _, _, _, _, ids = env
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    receipt = make_receipt(env, tmp_path, result)
    attach_approval_and_activation(env, tmp_path, receipt)
    path = write_json(tmp_path, receipt, "receipt.json")
    return path, receipt


def attach_approval_and_activation(env: Env, tmp_path: Path, receipt: dict[str, Any]) -> None:
    _, _, _, _, ids = env
    outcome, _ = dm.do_attach(
        env[0], write_json(tmp_path, receipt, "receipt.json"), ids["reviewed"], None
    )
    assert outcome == "attached"
    notes_add(env[0], ids["main"], make_activation(env))
    notes_push(env)


def write_json(directory: Path, payload: dict[str, Any], name: str) -> Path:
    path = directory / name
    path.write_text(json.dumps(payload, indent=2))
    return path


def assert_code(excinfo: Any, code: str, exit_code: int) -> None:
    assert excinfo.value.code == code
    assert excinfo.value.exit_code == exit_code


def test_happy_path_preflight_eligible(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path, receipt = eligible_setup(env, monkeypatch, tmp_path)
    before_head = git(env[0], "rev-parse", "HEAD")
    before_status = git(env[0], "status", "--porcelain", "--untracked-files=no")
    before_notes = git(env[0], "rev-parse", "--verify", dm.DEDICATED_NOTES_REF)
    summary = dm.do_preflight(env[0], path, None)
    assert summary["status"] == "eligible"
    assert summary["reviewed_head"] == receipt["reviewed_remote_head_sha"]
    assert git(env[0], "rev-parse", "HEAD") == before_head
    assert git(env[0], "status", "--porcelain", "--untracked-files=no") == before_status
    assert git(env[0], "rev-parse", "--verify", dm.DEDICATED_NOTES_REF) == before_notes


def test_validate_receipt_command(tmp_path: Path) -> None:
    payload = {"schema_version": 1}
    path = write_json(tmp_path, payload, "bad.json")
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_validate_receipt(path)
    assert_code(excinfo, "E_DELEGATED_RECEIPT", 2)
    assert dm.main(["validate-receipt", "--receipt", str(path)]) == 2


def test_missing_receipt_file(tmp_path: Path, env: Env) -> None:
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], tmp_path / "absent.json", None)
    assert_code(excinfo, "E_DELEGATED_RECEIPT", 2)


def test_malformed_and_extra_keys(tmp_path: Path) -> None:
    path = tmp_path / "broken.json"
    path.write_text("{not json")
    before = path.read_bytes()
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_validate_receipt(path)
    assert_code(excinfo, "E_DELEGATED_RECEIPT", 2)
    assert path.read_bytes() == before


def test_tier_class_and_findings_shape(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    receipt = make_receipt(env, tmp_path, result)
    receipt["eligibility"]["tier_class"] = 1
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_validate_receipt(write_json(tmp_path, receipt, "t.json"))
    assert_code(excinfo, "E_DELEGATED_RECEIPT", 2)
    receipt = make_receipt(env, tmp_path, result)
    receipt["eligibility"]["findings"] = receipt["eligibility"]["findings"][:-1]
    with pytest.raises(DelegatedError):
        dm.do_validate_receipt(write_json(tmp_path, receipt, "t.json"))
    receipt = make_receipt(env, tmp_path, result)
    receipt["eligibility"]["findings"].append(receipt["eligibility"]["findings"][0])
    with pytest.raises(DelegatedError):
        dm.do_validate_receipt(write_json(tmp_path, receipt, "t.json"))
    receipt = make_receipt(env, tmp_path, result)
    receipt["eligibility"]["quoted_state"]["risk_tier"] = "tier_9_unknown"
    with pytest.raises(DelegatedError):
        dm.do_validate_receipt(write_json(tmp_path, receipt, "t.json"))


def test_required_validation_declarations(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    receipt = make_receipt(env, tmp_path, result)
    quoted = receipt["eligibility"]["quoted_state"]
    quoted["delegated_merge_required_validation"] = ["taskctl_check"]
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_validate_receipt(write_json(tmp_path, receipt, "t.json"))
    assert_code(excinfo, "E_DELEGATED_RECEIPT", 2)
    receipt = make_receipt(env, tmp_path, result)
    receipt["eligibility"]["quoted_state"]["delegated_merge_required_validation"] = [
        "taskctl_check",
        "git_diff_check",
        "focused_tests",
        "unknown_gate",
    ]
    with pytest.raises(DelegatedError):
        dm.do_validate_receipt(write_json(tmp_path, receipt, "t.json"))
    receipt = make_receipt(env, tmp_path, result)
    receipt["validation"]["categories"]["taskctl_check"]["status"] = "not_required"
    with pytest.raises(DelegatedError):
        dm.do_validate_receipt(write_json(tmp_path, receipt, "t.json"))
    receipt = make_receipt(env, tmp_path, result)
    receipt["validation"]["categories"]["docker_make_validate"]["tree_sha"] = "f" * 40
    with pytest.raises(DelegatedError):
        dm.do_validate_receipt(write_json(tmp_path, receipt, "t.json"))
    receipt = make_receipt(env, tmp_path, result)
    validated = dm.do_validate_receipt(write_json(tmp_path, receipt, "t.json"))
    assert validated.receipt_id == RECEIPT_UUID


def test_non_routine_tier_rejected(
    environment_tier3: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env = environment_tier3
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    receipt = make_receipt(env, tmp_path, result)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_validate_receipt(write_json(tmp_path, receipt, "t.json"))
    assert_code(excinfo, "E_DELEGATED_RECEIPT", 2)


def test_self_approval_and_forged_attribution(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path, _ = eligible_setup(env, monkeypatch, tmp_path)
    forged_hex = REVIEWER_UUID.replace("-", "")
    write_binding(env, project="proj-" + forged_hex)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], path, None)
    assert_code(excinfo, "E_DELEGATED_IDENTITY", 2)
    write_binding(env, session="ses_" + forged_hex)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], path, None)
    assert_code(excinfo, "E_DELEGATED_IDENTITY", 2)


def test_stale_event_rejected(env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    path, _ = eligible_setup(env, monkeypatch, tmp_path)
    observer = Observer(env[0])
    ledger = observer.load()
    key = next(iter(ledger.events))
    ledger.events[key].stale = True
    observer.save(ledger)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], path, None)
    assert_code(excinfo, "E_DELEGATED_EVIDENCE", 2)


def test_replaced_head_rejected(env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    path, _ = eligible_setup(env, monkeypatch, tmp_path)
    (env[0] / "product.py").write_text("def total(values):\n    return 0\n")
    commit(env[0], "unrelated followup")
    git(env[0], "push", "-q", "origin", "feat/fixture-delegated")
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], path, None)
    assert_code(excinfo, "E_DELEGATED_EVIDENCE", 2)


def test_moved_main_rejected(env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    path, _ = eligible_setup(env, monkeypatch, tmp_path)
    git(env[0], "switch", "-q", "main")
    (env[0] / "product.py").write_text("def total(values):\n    return sum(values) + 0  # moved\n")
    commit(env[0], "main moved")
    git(env[0], "push", "-q", "origin", "main")
    git(env[0], "switch", "-q", "feat/fixture-delegated")
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], path, None)
    assert_code(excinfo, "E_DELEGATED_BASELINE", 2)


def test_digest_and_thread_mismatch(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, report, result = review_completed(env, monkeypatch)
    write_binding(env)
    result["summary"] = "Tampered after digest."
    (report / "result.json").write_text(json.dumps(result))
    receipt = make_receipt(env, tmp_path, result)
    receipt["reviewer"]["observer_report_digest"] = "0" * 64
    with pytest.raises(DelegatedError):
        dm.do_preflight(env[0], write_json(tmp_path, receipt, "t.json"), None)


def test_thread_uuid_absent(env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _, report, result = review_completed(env, monkeypatch)
    (report / "events.jsonl").write_text(
        json.dumps({"type": "thread.started", "thread_id": OTHER_UUID}) + "\n"
    )
    write_binding(env)
    receipt = make_receipt(env, tmp_path, result)
    notes_add(env[0], env[4]["reviewed"], receipt)
    notes_add(env[0], env[4]["main"], make_activation(env))
    notes_push(env)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], write_json(tmp_path, receipt, "t.json"), None)
    assert_code(excinfo, "E_DELEGATED_EVIDENCE", 2)


def test_model_output_absent(env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    path, _ = eligible_setup(env, monkeypatch, tmp_path)
    observer = Observer(env[0])
    event = next(iter(observer.load().events.values()))
    assert event.report is not None
    (Path(event.report) / "model-output.json").unlink()
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], path, None)
    assert_code(excinfo, "E_DELEGATED_EVIDENCE", 2)


def test_quoted_state_and_ancestry(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path, receipt = eligible_setup(env, monkeypatch, tmp_path)
    receipt["eligibility"]["quoted_state"]["validation_scope"] = "forged-scope"
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], write_json(tmp_path, receipt, "t.json"), None)
    assert_code(excinfo, "E_DELEGATED_EVIDENCE", 2)


def test_evidence_escape_and_symlink(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    receipt = make_receipt(env, tmp_path, result)
    receipt["validation"]["categories"]["focused_tests"]["evidence"] = ["../escape.txt"]
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_validate_receipt(write_json(tmp_path, receipt, "t.json"))
    assert_code(excinfo, "E_DELEGATED_EVIDENCE", 2)
    receipt = make_receipt(env, tmp_path, result)
    attach_approval_and_activation(env, tmp_path, receipt)
    observer = Observer(env[0])
    event = next(iter(observer.load().events.values()))
    assert event.report is not None
    link = Path(event.report) / "link.json"
    link.symlink_to(tmp_path / "outside.json")
    (tmp_path / "outside.json").write_text("{}")
    raw = json.loads((tmp_path / "receipt.json").read_text())
    raw["validation"]["categories"]["focused_tests"]["evidence"] = ["link.json"]
    synced = write_json(tmp_path, raw, "t.json")
    subprocess.run(
        ["git", "-C", str(env[0]), "notes", "--ref", dm.NOTES_SHORT_REF, "add", "-f",
         "-m", synced.read_text(), env[4]["reviewed"]],
        check=True,
        capture_output=True,
        text=True,
    )
    notes_push(env)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], synced, None)
    assert_code(excinfo, "E_DELEGATED_EVIDENCE", 2)


def test_activation_cases(env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    receipt = make_receipt(env, tmp_path, result)
    outcome, _ = dm.do_attach(
        env[0], write_json(tmp_path, receipt, "r.json"), env[4]["reviewed"], None
    )
    assert outcome == "attached"
    notes_push(env)
    path = write_json(tmp_path, receipt, "r.json")
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], path, None)
    assert_code(excinfo, "E_DELEGATED_NOT_ACTIVATED", 2)
    activation = make_activation(env)
    activation["policy_version"] = "other-version"
    notes_add(env[0], env[4]["main"], activation)
    notes_push(env)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], path, None)
    assert_code(excinfo, "E_DELEGATED_POLICY", 2)


def test_activation_nonancestor_target(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    git(env[0], "switch", "-q", "-c", "side/spurious")
    (env[0] / "side.txt").write_text("side")
    side = commit(env[0], "side work")
    git(env[0], "switch", "-q", "feat/fixture-delegated")
    receipt = make_receipt(env, tmp_path, result)
    receipt["delegation_provenance"]["activation_head_sha"] = side
    outcome, _ = dm.do_attach(
        env[0], write_json(tmp_path, receipt, "r.json"), env[4]["reviewed"], None
    )
    assert outcome == "attached"
    activation = make_activation(env)
    activation["prerequisite_head_sha"] = side
    notes_add(env[0], side, activation)
    notes_push(env)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], write_json(tmp_path, receipt, "r2.json"), None)
    assert_code(excinfo, "E_DELEGATED_NOT_ACTIVATED", 2)


def test_policy_drift_without_version_bump(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    git(env[0], "switch", "-q", "main")
    policy = env[0] / "docs/execution/DELEGATED_ROUTINE_MERGE_POLICY.md"
    policy.write_text(POLICY_TEXT + "Silent drift.\n")
    commit(env[0], "drift policy")
    git(env[0], "push", "-q", "origin", "main")
    git(env[0], "switch", "-q", "feat/fixture-delegated")
    new_main = git(env[0], "rev-parse", "main")
    receipt = make_receipt(env, tmp_path, result)
    receipt["main_baseline_sha"] = new_main
    receipt["delegation_provenance"]["activation_head_sha"] = new_main
    activation = make_activation(env)
    activation["prerequisite_head_sha"] = new_main
    outcome, _ = dm.do_attach(
        env[0], write_json(tmp_path, receipt, "r.json"), env[4]["reviewed"], None
    )
    assert outcome == "attached"
    notes_add(env[0], new_main, activation)
    notes_push(env)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], write_json(tmp_path, receipt, "r.json"), None)
    assert_code(excinfo, "E_DELEGATED_POLICY", 2)


def test_notes_missing_stale_and_mismatch(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    receipt = make_receipt(env, tmp_path, result)
    path = write_json(tmp_path, receipt, "r.json")
    outcome, _ = dm.do_attach(env[0], path, env[4]["reviewed"], None)
    assert outcome == "attached"
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], path, None)
    assert_code(excinfo, "E_DELEGATED_NOTE_MISSING", 2)
    notes_push(env)
    notes_add(env[0], env[4]["main"], make_activation(env))
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], path, None)
    assert_code(excinfo, "E_DELEGATED_NOTE_STALE", 2)
    notes_push(env)
    other = dict(receipt)
    other["limitations"] = ["Different bytes."]
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], write_json(tmp_path, other, "o.json"), None)
    assert_code(excinfo, "E_DELEGATED_EVIDENCE", 2)


def test_corrupt_note_preserved(env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    receipt = make_receipt(env, tmp_path, result)
    subprocess.run(
        ["git", "-C", str(env[0]), "notes", "--ref", dm.NOTES_SHORT_REF, "add", "-f",
         "-m", "not json", env[4]["reviewed"]],
        check=True,
        capture_output=True,
        text=True,
    )
    notes_push(env)
    before = git(env[0], "rev-parse", "--verify", dm.DEDICATED_NOTES_REF)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_preflight(env[0], write_json(tmp_path, receipt, "r.json"), None)
    assert_code(excinfo, "E_DELEGATED_NOTE_CORRUPT", 2)
    assert git(env[0], "rev-parse", "--verify", dm.DEDICATED_NOTES_REF) == before


def test_attach_idempotent_conflict_and_kind(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    receipt = make_receipt(env, tmp_path, result)
    path = write_json(tmp_path, receipt, "r.json")
    before_branches = git(env[0], "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads")
    outcome, _ = dm.do_attach(env[0], path, env[4]["reviewed"], None)
    assert outcome == "attached"
    outcome, _ = dm.do_attach(env[0], path, env[4]["reviewed"], None)
    assert outcome == "already-attached"
    after_branches = git(env[0], "for-each-ref", "--format=%(refname) %(objectname)", "refs/heads")
    assert after_branches == before_branches
    other = dict(receipt)
    other["limitations"] = ["Conflicting bytes."]
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_attach(env[0], write_json(tmp_path, other, "o.json"), env[4]["reviewed"], None)
    assert_code(excinfo, "E_DELEGATED_NOTE_CONFLICT", 2)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_attach(env[0], path, env[4]["reviewed"], "refs/notes/other")
    assert_code(excinfo, "E_DELEGATED_REF", 2)
    activation = make_activation(env)
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_attach(env[0], write_json(tmp_path, activation, "a.json"), env[4]["main"], None)
    assert_code(excinfo, "E_DELEGATED_RECEIPT", 2)


def test_attach_lock_contention(env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    _, _, result = review_completed(env, monkeypatch)
    write_binding(env)
    receipt = make_receipt(env, tmp_path, result)
    path = write_json(tmp_path, receipt, "r.json")
    with dm.attach_lock(env[0]):
        with pytest.raises(DelegatedError) as excinfo:
            dm.do_attach(env[0], path, env[4]["reviewed"], None)
    assert_code(excinfo, "E_DELEGATED_STATE", 3)


def test_oversized_receipt_rejected(tmp_path: Path) -> None:
    path = tmp_path / "huge.json"
    path.write_text(json.dumps({"schema_version": 1, "pad": "x" * (dm.MAX_RECEIPT_BYTES + 1)}))
    before = path.read_bytes()
    with pytest.raises(DelegatedError) as excinfo:
        dm.do_validate_receipt(path)
    assert_code(excinfo, "E_DELEGATED_RECEIPT", 2)
    assert path.read_bytes() == before


def test_transport_and_git_boundaries(tmp_path: Path) -> None:
    with pytest.raises(DelegatedError) as excinfo:
        dm.ls_remote("/nonexistent-remote-path-xyz", "refs/heads/main")
    assert_code(excinfo, "E_DELEGATED_TRANSPORT", 3)
    with pytest.raises(DelegatedError) as excinfo:
        dm.require_notes_ref("refs/notes/other")
    assert_code(excinfo, "E_DELEGATED_REF", 2)
    assert dm.main(["validate-receipt", "--receipt", str(tmp_path / "absent.json")]) == 2


def test_no_inference_during_preflight(
    env: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path, _ = eligible_setup(env, monkeypatch, tmp_path)

    def forbidden(bundle: Path, report: Path) -> dict[str, Any]:
        raise AssertionError("Codex inference must not run")

    monkeypatch.setattr(Observer, "run_codex", forbidden)
    summary = dm.do_preflight(env[0], path, None)
    assert summary["status"] == "eligible"
