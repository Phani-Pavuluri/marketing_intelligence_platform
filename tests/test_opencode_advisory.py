"""Behavioral checks for the OpenCode advisory delivery adapter.

Uses isolated Git remotes and fake OpenCode transports. Never contacts a real
implementation session and never performs Codex inference.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import pytest

from mip.execution import opencode_advisory as advisory
from mip.execution import review_observer as observer_module
from mip.execution.opencode_advisory import AdvisoryError
from mip.execution.review_observer import Observer
from mip.execution.state import validate_state
from mip.execution.views import render_execution_view

LIVE_STATE_PATH = (Path(__file__).parents[1] / "docs/execution/EXECUTION_STATE.json").resolve()

Env = tuple[Path, Path, Path, dict[str, Any], str]


@pytest.fixture(autouse=True)
def _forbid_live_state_template(monkeypatch: pytest.MonkeyPatch) -> None:
    real_read_text = Path.read_text

    def guarded(self: Path, *args: Any, **kwargs: Any) -> str:
        if self.resolve() == LIVE_STATE_PATH:
            raise AssertionError("fixture must not read the live execution-state template")
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded)


def canonical_fixture_state() -> dict[str, Any]:
    state: dict[str, Any] = {
        "schema_version": "mip_repo_execution_state_v2",
        "repository": "Phani-Pavuluri/marketing_intelligence_platform",
        "task_id": "FIXTURE_ADVISORY_001",
        "status": "proposed",
        "review_decision": "proposed",
        "execution_mode": "branch_and_fast_forward",
        "base_branch": "main",
        "authorization_head_convention": "fixture-owned provenance",
        "finalized_branch_baseline_resolution": "fixture-owned baseline",
        "task_path": "docs/execution/ACTIVE_TASK.md",
        "completion_report_path": "docs/execution/LATEST_COMPLETION_REPORT.md",
        "feature_branch": "feat/fixture-advisory",
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
        "risk_tier": "tier_2_fixture_isolation",
        "validation_scope": "fixture",
        "compatibility_migration_policy": "not_applicable_fixture_only",
        "merge_approval_mode": "user_exact_head",
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
                "\nTask: total(values) must return the mathematical sum exactly.\n"
                if document == "active_task"
                else "\nCompletion claim: all acceptance checks passed.\n"
            )
        )


@pytest.fixture
def environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, Path, dict[str, Any], str]:
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    root = tmp_path / "review"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Fixture author")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "remote", "add", "origin", str(remote))
    monkeypatch.setattr(observer_module, "EXPECTED_ORIGIN", str(remote))
    monkeypatch.setattr(advisory, "EXPECTED_ORIGIN", str(remote))
    (root / "product.py").write_text("def total(values):\n    return sum(values)\n")
    (root / ".gitignore").write_text(".codex/\n")
    (root / "AGENTS.md").write_text("Untrusted evidence.\n")
    base = commit(root, "base")
    state = canonical_fixture_state()
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
    commit(root, "finalize authority")
    git(root, "push", "-q", "origin", "main")
    git(root, "switch", "-qc", "feat/fixture-advisory")
    # A separate implementation checkout shares the canonical origin.
    implementation = tmp_path / "implementation"
    subprocess.run(["git", "clone", "-q", str(remote), str(implementation)], check=True)
    git(implementation, "config", "user.name", "Fixture author")
    git(implementation, "config", "user.email", "fixture@example.invalid")
    return root, implementation, remote, state, base


def publish(root: Path, state: dict[str, Any]) -> str:
    (root / "product.py").write_text("def total(values):\n    return sum(values) + 1\n")
    implementation = commit(root, "implement")
    state.update(
        status="ready_for_review",
        review_decision="ready_for_review",
        implementation_commit_sha=implementation,
    )
    write_state(root, state)
    head = commit(root, "publish validation receipt")
    git(root, "push", "-q", "origin", "feat/fixture-advisory")
    return head


def fake_result(checkpoint: Any, **changes: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": 1,
        "repository": observer_module.REPOSITORY,
        "task_id": checkpoint.state["task_id"],
        "checkpoint_kind": checkpoint.kind,
        "reviewed_sha": checkpoint.sha,
        "verdict": "needs_user",
        "summary": "Fixture review summary.",
        "findings": [
            {
                "id": "F1",
                "severity": "major",
                "source_path": "product.py",
                "line": 2,
                "requirement": "Sum faithfully",
                "observation": "Adds one",
                "impact": "Wrong answer",
                "proposed_correction": "Preserve the sum",
                "acceptance_evidence": "Exact sum example",
                "user_decision_required": True,
            }
        ],
        "limitations": ["Synthetic fixture; no readiness claim."],
        "owner_update": {
            "goal_impact": "Checks whether the completed change matches its promise.",
            "completed": [],
            "ongoing": [],
            "planned": [],
            "issues": [],
            "decisions_needed": ["Choose the correct total semantics."],
            "recommendation": "Inspect the evidence before deciding.",
        },
    }
    value.update(changes)
    return value


def complete_event(
    environment: tuple[Path, Path, Path, dict[str, Any], str],
    monkeypatch: pytest.MonkeyPatch,
    **result_changes: Any,
) -> tuple[str, Path]:
    root, _, _, state, _ = environment
    observer = Observer(root)
    assert observer.execute("init") == 0
    publish(root, state)

    def run(bundle: Path, report: Path) -> dict[str, Any]:
        manifest = json.loads((bundle / "manifest.json").read_text())
        checkpoint = observer.checkpoint(manifest["ref"], manifest["reviewed_sha"])
        assert checkpoint is not None
        return fake_result(checkpoint, **result_changes)

    monkeypatch.setattr(observer, "run_codex", run)
    assert observer.execute("scan") in (0, 2, 3)
    ledger = observer.load()
    assert len(ledger.events) == 1
    key = next(iter(ledger.events))
    assert ledger.events[key].status == "completed"
    return key, root


def fake_session_data(
    session_id: str,
    directory: Path,
    *,
    project_id: str = "proj-fixture",
    provider: str = "opencode",
    model: str = "muse-spark-1.3-contributor-free",
    variant: str = "high",
    agent: str = "build",
) -> dict[str, Any]:
    return {
        "id": session_id,
        "projectID": project_id,
        "agent": agent,
        "model": {"id": model, "providerID": provider, "variant": variant},
        "location": {"directory": str(directory.resolve())},
    }


def bind_ok(
    environment: tuple[Path, Path, Path, dict[str, Any], str],
    monkeypatch: pytest.MonkeyPatch,
    session_id: str = "ses_fixture123",
) -> str:
    root, implementation, _, _, _ = environment
    monkeypatch.setattr(
        advisory, "session_get", lambda sid, **_: fake_session_data(sid, implementation)
    )
    binding = advisory.do_bind(root, session_id, implementation)
    assert binding.session_id == session_id
    return session_id


def test_correct_binding(environment: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    env: Env = environment
    root, implementation, _, _, _ = env
    seen: list[str] = []

    def fake_get(session_id: str, **kwargs: Any) -> dict[str, Any]:
        seen.append(session_id)
        return fake_session_data(session_id, implementation)

    monkeypatch.setattr(advisory, "session_get", fake_get)
    binding = advisory.do_bind(root, "ses_abc", implementation)
    assert binding.provider == "opencode"
    assert binding.model == "muse-spark-1.3-contributor-free"
    assert binding.variant == "high"
    assert binding.agent == "build"
    assert binding.project_id == "proj-fixture"
    assert seen == ["ses_abc"]
    stored = json.loads((advisory.binding_path(root)).read_text())
    assert stored["session_id"] == "ses_abc"


def test_wrong_origin_rejected(environment: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    env: Env = environment
    root, implementation, tmp_remote, _, _ = env
    _ = tmp_remote
    other = root.parent / "other.git"
    subprocess.run(["git", "init", "--bare", "-q", str(other)], check=True)
    git(root, "remote", "set-url", "origin", str(other))
    monkeypatch.setattr(
        advisory, "session_get", lambda sid, **_: fake_session_data(sid, implementation)
    )
    with pytest.raises(AdvisoryError, match="E_ADVISORY_IDENTITY"):
        advisory.do_bind(root, "ses_x", implementation)
    git(root, "remote", "set-url", "origin", str(env[2]))


@pytest.mark.parametrize(
    "field,value",
    [
        ("directory", "wrong"),
        ("provider", "other"),
        ("model", "other-model"),
        ("variant", "default"),
        ("agent", "plan"),
        ("session_id", "ses_other"),
    ],
)
def test_wrong_session_identity_rejected(
    environment: Env, monkeypatch: pytest.MonkeyPatch, field: str, value: str
) -> None:
    env: Env = environment
    root, implementation, _, _, _ = env
    session_id = "ses_expected"

    def fake_get(sid: str, **kwargs: Any) -> dict[str, Any]:
        data = fake_session_data(session_id, implementation)
        if field == "directory":
            data["location"]["directory"] = str((implementation.parent / "elsewhere").resolve())
        elif field == "project_id":
            data["projectID"] = value
        elif field == "provider":
            data["model"]["providerID"] = value
        elif field == "model":
            data["model"]["id"] = value
        elif field == "variant":
            data["model"]["variant"] = value
        elif field == "agent":
            data["agent"] = value
        elif field == "session_id":
            data["id"] = value
        return data

    monkeypatch.setattr(advisory, "session_get", fake_get)
    with pytest.raises(AdvisoryError) as excinfo:
        advisory.do_bind(root, session_id, implementation)
    assert excinfo.value.exit_code == 2
    assert excinfo.value.code == "E_ADVISORY_IDENTITY"


def test_completed_review_admission(
    environment: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env: Env = environment
    key, root = complete_event(env, monkeypatch)
    bind_ok(env, monkeypatch)
    prompts: list[tuple[str, str]] = []

    def fake_prompt(sid: str, text: str, **kwargs: Any) -> str:
        prompts.append((sid, text))
        assert '"resume": false' in json.dumps({"text": text, "resume": False})
        assert "[MIP advisory" in text
        assert "Git owns authorized scope" in text
        return "msg_1"

    monkeypatch.setattr(advisory, "session_get", lambda sid, **_: fake_session_data(sid, env[1]))
    monkeypatch.setattr(advisory, "session_prompt", fake_prompt)
    before_tree = git(root, "rev-parse", "HEAD")
    before_status = git(root, "status", "--porcelain", "--untracked-files=no")
    outcome, delivery = advisory.do_send(root, key)
    assert outcome == "admitted"
    assert delivery.message_id == "msg_1"
    assert len(prompts) == 1
    assert git(root, "rev-parse", "HEAD") == before_tree
    assert git(root, "status", "--porcelain", "--untracked-files=no") == before_status


def test_stale_event_rejected(environment: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    env: Env = environment
    key, root = complete_event(env, monkeypatch)
    bind_ok(env, monkeypatch)
    observer = Observer(root)
    ledger = observer.load()
    ledger.events[key].stale = True
    observer.save(ledger)
    monkeypatch.setattr(advisory, "session_get", lambda sid, **_: fake_session_data(sid, env[1]))
    with pytest.raises(AdvisoryError) as excinfo:
        advisory.do_send(root, key)
    assert excinfo.value.exit_code == 2


def test_project_change_on_send_rejected(
    environment: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env: Env = environment
    key, root = complete_event(env, monkeypatch)
    bind_ok(env, monkeypatch, session_id="ses_proj")
    changed = fake_session_data("ses_proj", env[1], project_id="proj-changed")
    monkeypatch.setattr(advisory, "session_get", lambda sid, **_: changed)
    monkeypatch.setattr(advisory, "session_prompt", lambda sid, text, **kw: "msg_never")
    with pytest.raises(AdvisoryError) as excinfo:
        advisory.do_send(root, key)
    assert excinfo.value.exit_code == 2


def test_closure_malformed_incomplete_rejected(
    environment: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env: Env = environment
    key, root = complete_event(env, monkeypatch)
    bind_ok(env, monkeypatch)
    monkeypatch.setattr(advisory, "session_get", lambda sid, **_: fake_session_data(sid, env[1]))
    observer = Observer(root)
    ledger = observer.load()
    original_report = ledger.events[key].report
    assert original_report is not None
    # Closure kind is ineligible.
    ledger.events[key].kind = "closure"
    observer.save(ledger)
    with pytest.raises(AdvisoryError) as excinfo:
        advisory.do_send(root, key)
    assert excinfo.value.exit_code == 2
    ledger = observer.load()
    ledger.events[key].kind = "completion"
    ledger.events[key].report = None
    observer.save(ledger)
    with pytest.raises(AdvisoryError):
        advisory.do_send(root, key)
    # Malformed result.
    ledger = observer.load()
    ledger.events[key].report = original_report
    observer.save(ledger)
    (Path(original_report) / "result.json").write_text('{"schema_version": 99}')
    with pytest.raises(AdvisoryError):
        advisory.do_send(root, key)


def test_reserved_owner_labeling(environment: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    env: Env = environment
    key, root = complete_event(env, monkeypatch)
    bind_ok(env, monkeypatch)
    captured: list[str] = []

    def fake_prompt(sid: str, text: str, **kwargs: Any) -> str:
        captured.append(text)
        return "msg_2"

    monkeypatch.setattr(advisory, "session_get", lambda sid, **_: fake_session_data(sid, env[1]))
    monkeypatch.setattr(advisory, "session_prompt", fake_prompt)
    advisory.do_send(root, key)
    text = captured[0]
    assert "user_decision_required=true" in text
    assert "Owner-reserved decisions" in text
    assert "agent agreement cannot resolve" in text
    assert "pending owner input" in text


def test_no_inference_and_resume_false_boundary(
    environment: Env, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    env: Env = environment
    key, root = complete_event(env, monkeypatch)
    bind_ok(env, monkeypatch)

    def forbidden_bundle(bundle: Path, report: Path) -> dict[str, Any]:
        raise AssertionError("Codex inference must not run")

    monkeypatch.setattr(Observer, "run_codex", forbidden_bundle)
    monkeypatch.setattr(advisory, "session_get", lambda sid, **_: fake_session_data(sid, env[1]))
    executable = tmp_path / "fake-opencode"
    executable.write_text(
        "#!/usr/bin/env python3\nimport json,sys\n"
        "args=sys.argv\n"
        "assert 'session.prompt' in args\n"
        "idx=args.index('-d')\n"
        "body=json.loads(args[idx+1])\n"
        "assert body.get('resume') is False\n"
        "assert isinstance(body.get('text'), str)\n"
        "sid=args[args.index('--param')+1].split('=',1)[1]\n"
        "print(json.dumps({'data': {'id': 'msg_boundary', 'sessionID': sid}}))\n"
    )
    executable.chmod(0o755)
    outcome, delivery = advisory.do_send(
        root, key, opencode_bin=str(executable), timeout=10.0
    )
    assert outcome == "admitted"
    assert delivery.message_id == "msg_boundary"


def test_repeated_delivery_deduplicated(
    environment: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env: Env = environment
    key, root = complete_event(env, monkeypatch)
    bind_ok(env, monkeypatch)
    calls: list[str] = []

    def fake_prompt(sid: str, text: str, **kwargs: Any) -> str:
        calls.append(text)
        return "msg_dup"

    monkeypatch.setattr(advisory, "session_get", lambda sid, **_: fake_session_data(sid, env[1]))
    monkeypatch.setattr(advisory, "session_prompt", fake_prompt)
    outcome, _ = advisory.do_send(root, key)
    assert outcome == "admitted"
    outcome2, delivery2 = advisory.do_send(root, key)
    assert outcome2 == "already-admitted"
    assert delivery2.message_id == "msg_dup"
    assert len(calls) == 1


def test_timeout_and_crash_reservation_suppress_resend(
    environment: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env: Env = environment
    key, root = complete_event(env, monkeypatch)
    bind_ok(env, monkeypatch)
    monkeypatch.setattr(advisory, "session_get", lambda sid, **_: fake_session_data(sid, env[1]))

    def timeout_prompt(sid: str, text: str, **kwargs: Any) -> str:
        raise AdvisoryError("E_ADVISORY_INDETERMINATE", "timeout", 3)

    monkeypatch.setattr(advisory, "session_prompt", timeout_prompt)
    with pytest.raises(AdvisoryError) as excinfo:
        advisory.do_send(root, key)
    assert excinfo.value.exit_code == 3
    calls: list[str] = []

    def _never_prompt(sid: str, text: str, **kw: Any) -> str:
        calls.append(text)
        return "msg_never"

    monkeypatch.setattr(advisory, "session_prompt", _never_prompt)
    with pytest.raises(AdvisoryError, match="E_ADVISORY_INDETERMINATE"):
        advisory.do_send(root, key)
    assert calls == []


def test_corrupt_state_fails_closed_without_erasure(
    environment: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env: Env = environment
    key, root = complete_event(env, monkeypatch)
    bind_ok(env, monkeypatch)
    journal_file = advisory.journal_path(root)
    journal_file.write_text('{"schema_version": 1, "deliveries": {}}')
    monkeypatch.setattr(advisory, "session_get", lambda sid, **_: fake_session_data(sid, env[1]))
    monkeypatch.setattr(advisory, "session_prompt", lambda sid, text, **kw: "msg_x")
    # Corrupt the journal after a reservation path exists.
    journal_file.write_text("not json")
    before = journal_file.read_text()
    with pytest.raises(AdvisoryError) as excinfo:
        advisory.do_send(root, key)
    assert excinfo.value.exit_code == 3
    assert journal_file.read_text() == before
    binding_file = advisory.binding_path(root)
    binding_before = binding_file.read_text()
    binding_file.write_text('{"schema_version": 2}')
    with pytest.raises(AdvisoryError):
        advisory.do_send(root, key)
    assert binding_file.read_text() == '{"schema_version": 2}'
    assert binding_before != '{"schema_version": 2}'


def test_competing_writers_fail_closed(
    environment: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env: Env = environment
    root, implementation, _, _, _ = env
    monkeypatch.setattr(
        advisory, "session_get", lambda sid, **_: fake_session_data(sid, implementation)
    )
    with advisory.advisory_lock(root):
        with pytest.raises(AdvisoryError, match="E_ADVISORY_STATE"):
            advisory.do_bind(root, "ses_locked", implementation)


def test_bounded_output(environment: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    env: Env = environment
    huge = "x" * 50000
    key, root = complete_event(env, monkeypatch, summary=huge)
    bind_ok(env, monkeypatch)
    captured: list[str] = []
    monkeypatch.setattr(advisory, "session_get", lambda sid, **_: fake_session_data(sid, env[1]))

    def _capture_prompt(sid: str, text: str, **kw: Any) -> str:
        captured.append(text)
        return "m"

    monkeypatch.setattr(advisory, "session_prompt", _capture_prompt)
    advisory.do_send(root, key)
    assert len(captured[0]) <= advisory.MAX_ADVISORY_CHARS


def test_status_reports_binding_and_deliveries(
    environment: Env, monkeypatch: pytest.MonkeyPatch
) -> None:
    env: Env = environment
    key, root = complete_event(env, monkeypatch)
    bind_ok(env, monkeypatch)
    status = advisory.do_status(root)
    assert status["binding"]["session_id"]
    assert status["deliveries"] == {}
    monkeypatch.setattr(advisory, "session_get", lambda sid, **_: fake_session_data(sid, env[1]))
    monkeypatch.setattr(advisory, "session_prompt", lambda sid, text, **kw: "msg_s")
    advisory.do_send(root, key)
    status2 = advisory.do_status(root)
    assert len(status2["deliveries"]) == 1
