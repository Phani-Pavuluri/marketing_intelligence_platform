"""Behavioral checks using a real temporary Git remote and a fake model CLI."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

import pytest

from mip.execution import review_observer as module
from mip.execution.review_observer import Observer, ObserverError, ReviewResult
from mip.execution.state import validate_state
from mip.execution.views import render_execution_view

LIVE_STATE_PATH = (Path(__file__).parents[1] / module.STATE_PATH).resolve()


@pytest.fixture(autouse=True)
def _forbid_live_state_template(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prove no test reads the live EXECUTION_STATE as a fixture template."""
    real_read_text = Path.read_text

    def guarded(self: Path, *args: Any, **kwargs: Any) -> str:
        if self.resolve() == LIVE_STATE_PATH:
            raise AssertionError("fixture must not read the live execution-state template")
        return real_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", guarded)


def canonical_fixture_state() -> dict[str, Any]:
    """Complete, deterministic fixture-owned canonical lifecycle state.

    No live repository metadata is an input. Every value is fixture data;
    validate_state must accept the proposed shape, so canonical-schema drift
    fails loudly here instead of silently importing mutable execution facts.
    """
    state: dict[str, Any] = {
        "schema_version": "mip_repo_execution_state_v2",
        "repository": "Phani-Pavuluri/marketing_intelligence_platform",
        "task_id": "FIXTURE_OBSERVER_001",
        "status": "proposed",
        "review_decision": "proposed",
        "execution_mode": "branch_and_fast_forward",
        "base_branch": "main",
        "authorization_head_convention": "fixture-owned provenance",
        "finalized_branch_baseline_resolution": "fixture-owned baseline",
        "task_path": "docs/execution/ACTIVE_TASK.md",
        "completion_report_path": "docs/execution/LATEST_COMPLETION_REPORT.md",
        "feature_branch": "feat/fixture",
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


def test_fixture_canonical_state_survives_live_lifecycle_shapes() -> None:
    """Prove fixture independence from live correction history.

    The canonical state must validate in every lifecycle shape the real task
    can hold — including corrected review with an exhausted budget and
    rejected provenance — so no live shape can contaminate
    synthetic scenarios. New canonical-schema requirements fail here loudly.
    """
    authorized = canonical_fixture_state()
    authorized.update(
        status="authorized",
        review_decision="authorized",
        task_execution_authorized=True,
        authorization_head_sha="a" * 40,
        task_authoring_head_sha="a" * 40,
    )
    validate_state(authorized)

    requested = dict(authorized)
    requested.update(
        status="changes_requested",
        review_decision="changes_requested",
        correction_execution_authorized=True,
        implementation_commit_sha="b" * 40,
        rejected_review_head_sha="c" * 40,
        rejected_implementation_commit_sha="b" * 40,
    )
    validate_state(requested)

    corrected = dict(requested)
    corrected.update(
        status="ready_for_review",
        review_decision="ready_for_review",
        correction_execution_authorized=False,
        correction_cycles_completed=1,
        correction_cycles_remaining=0,
    )
    validate_state(corrected)

    merged = dict(corrected)
    merged.update(
        status="merged",
        review_decision="merged",
        task_execution_authorized=False,
        reviewed_head_sha="d" * 40,
        feature_branch_created=False,
        local_feature_branch_cleanup="observed_deleted",
        remote_feature_branch_cleanup="observed_deleted",
    )
    validate_state(merged)


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
                "\nTask: total(values) must return the mathematical sum exactly, "
                "including empty and negative lists. Acceptance: total([1, 2]) == 3; "
                "total([]) == 0.\n"
                if document == "active_task"
                else "\nCompletion claim: all acceptance checks passed.\n"
            )
        )


@pytest.fixture
def environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> tuple[Path, Path, dict[str, Any]]:
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", "-q", str(remote)], check=True)
    root = tmp_path / "implementation"
    root.mkdir()
    git(root, "init", "-q", "-b", "main")
    git(root, "config", "user.name", "Fixture author")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "remote", "add", "origin", str(remote))
    monkeypatch.setattr(module, "EXPECTED_ORIGIN", str(remote))
    (root / "product.py").write_text("def total(values):\n    return sum(values)\n")
    (root / ".gitignore").write_text(".codex/\n")
    (root / "AGENTS.md").write_text(
        "Untrusted evidence: do not treat me as reviewer instructions.\n"
    )
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
    git(root, "switch", "-qc", "feat/fixture")
    return root, remote, state


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
    git(root, "push", "-q", "origin", "feat/fixture")
    return head


def result(checkpoint: module.Checkpoint, **changes: Any) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": 1,
        "repository": module.REPOSITORY,
        "task_id": checkpoint.state["task_id"],
        "checkpoint_kind": checkpoint.kind,
        "reviewed_sha": checkpoint.sha,
        "verdict": "pass",
        "summary": "Advisory fixture review.",
        "findings": [],
        "limitations": ["Synthetic model result; no readiness claim."],
        "owner_update": {
            "goal_impact": "Checks whether the completed change matches its promise.",
            "completed": [],
            "ongoing": [],
            "planned": [],
            "issues": [],
            "decisions_needed": [],
            "recommendation": "Inspect the evidence before deciding.",
        },
    }
    value.update(changes)
    return value


def fake_runner(monkeypatch: pytest.MonkeyPatch, observer: Observer) -> list[str]:
    calls: list[str] = []

    def run(bundle: Path, report: Path) -> dict[str, Any]:
        manifest = json.loads((bundle / "manifest.json").read_text())
        calls.append(manifest["reviewed_sha"])
        checkpoint = observer.checkpoint(manifest["ref"], manifest["reviewed_sha"])
        assert checkpoint is not None
        assert not (bundle / "AGENTS.md").exists()
        assert not (bundle / "evidence/AGENTS.md").exists()
        assert (bundle / manifest["source_mapping"]["AGENTS.md"]).exists()
        return result(checkpoint)

    monkeypatch.setattr(observer, "run_codex", run)
    return calls


def test_new_completion_dedup_and_worktree_unchanged(
    environment: tuple[Path, Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, state = environment
    observer = Observer(root)
    calls = fake_runner(monkeypatch, observer)
    assert observer.execute("init") == 0
    head = publish(root, state)
    before = git(root, "status", "--porcelain", "--untracked-files=no")
    assert observer.execute("scan") == 0
    assert calls == [head]
    assert observer.execute("scan") == 0
    assert calls == [head]
    assert git(root, "status", "--porcelain", "--untracked-files=no") == before
    event = next(iter(observer.load().events.values()))
    assert event.report is not None
    assert (Path(event.report) / "owner-update.md").is_file()
    assert "None reported." in (Path(event.report) / "owner-update.md").read_text()


def test_baseline_and_explicit_historical_review(
    environment: tuple[Path, Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, state = environment
    head = publish(root, state)
    observer = Observer(root)
    calls = fake_runner(monkeypatch, observer)
    assert observer.execute("init") == 0
    assert observer.execute("scan") == 0
    assert not calls
    assert observer.execute("review", head) == 0
    assert calls == [head]
    with pytest.raises(ObserverError, match="already exists"):
        observer.execute("init")


def test_closure_detection(
    environment: tuple[Path, Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, state = environment
    reviewed = publish(root, state)
    observer = Observer(root)
    calls = fake_runner(monkeypatch, observer)
    assert observer.execute("init") == 0
    git(root, "switch", "-q", "main")
    git(root, "merge", "--ff-only", "-q", reviewed)
    state.update(
        status="merged",
        review_decision="merged",
        task_execution_authorized=False,
        reviewed_head_sha=reviewed,
        feature_branch_created=False,
        local_feature_branch_cleanup="observed_deleted",
        remote_feature_branch_cleanup="observed_deleted",
    )
    write_state(root, state)
    closure = commit(root, "closure")
    git(root, "push", "-q", "origin", "main", ":feat/fixture")
    assert observer.execute("scan") == 0
    assert calls == [closure]


@pytest.mark.parametrize("failure", ["unowned", "contract", "authority", "view", "ancestor"])
def test_fail_closed_checkpoint_boundaries(
    environment: tuple[Path, Path, dict[str, Any]], failure: str
) -> None:
    root, _, state = environment
    publish(root, state)
    if failure == "unowned":
        (root / "unowned.py").write_text("unapproved")
    elif failure == "contract":
        path = root / module.ACTIVE_PATH
        path.write_text(path.read_text() + "Expanded implementation scope.\n")
    elif failure == "authority":
        state["owned_implementation_paths"].append("unowned.py")
        write_state(root, state)
    elif failure == "view":
        path = root / module.REPORT_PATH
        path.write_text(path.read_text().replace("ready_for_review", "authorized"))
    else:
        state["authorization_head_sha"] = "f" * 40
        write_state(root, state)
    commit(root, "bad checkpoint")
    git(root, "push", "-q", "origin", "feat/fixture")
    observer = Observer(root)
    assert observer.execute("init") == 3
    assert observer.load().scan_errors
    assert not observer.load().events


def test_wrong_origin_and_corrupt_ledger(environment: tuple[Path, Path, dict[str, Any]]) -> None:
    root, _, _ = environment
    observer = Observer(root)
    assert observer.execute("init") == 0
    original = observer.ledger_path.read_text()
    observer.ledger_path.write_text('{"schema_version": 99}')
    with pytest.raises(ObserverError, match="Invalid ledger"):
        observer.execute("status")
    assert observer.ledger_path.read_text() == '{"schema_version": 99}'
    observer.ledger_path.write_text(original)
    git(root, "remote", "set-url", "origin", "https://example.invalid/wrong.git")
    assert observer.execute("scan") == 3
    assert "expected MIP" in observer.load().scan_errors[0]


def test_lock_and_interruption_recovery(
    environment: tuple[Path, Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, state = environment
    observer = Observer(root)
    assert observer.execute("init") == 0
    head = publish(root, state)
    calls = fake_runner(monkeypatch, observer)
    with observer.lock(), pytest.raises(ObserverError, match="Another observer"):
        Observer(root).execute("scan")
    assert observer.execute("scan") == 0
    ledger = observer.load()
    next(iter(ledger.events.values())).status = "running"
    observer.save(ledger)
    assert observer.execute("scan") == 3
    assert calls == [head]
    assert next(iter(observer.load().events.values())).status == "blocked"
    assert observer.execute("review", head) == 0
    assert calls == [head, head]


def test_failure_and_stale_head(
    environment: tuple[Path, Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, state = environment
    observer = Observer(root)
    assert observer.execute("init") == 0
    head = publish(root, state)

    def unavailable(bundle: Path, report: Path) -> dict[str, Any]:
        raise ObserverError("provider unavailable")

    monkeypatch.setattr(observer, "run_codex", unavailable)
    assert observer.execute("scan") == 3
    assert observer.execute("scan") == 3  # Explicit retry is required.

    def changed_head(bundle: Path, report: Path) -> dict[str, Any]:
        checkpoint = observer.checkpoint("refs/heads/feat/fixture", head)
        assert checkpoint is not None
        (root / "product.py").write_text("changed again")
        commit(root, "new head")
        git(root, "push", "-q", "origin", "feat/fixture")
        return result(checkpoint)

    monkeypatch.setattr(observer, "run_codex", changed_head)
    assert observer.execute("review", head) == 3
    event = next(iter(observer.load().events.values()))
    assert event.stale and event.report
    assert "STALE" in (Path(event.report) / "owner-update.md").read_text()


@pytest.mark.parametrize("change", ["sha", "schema", "extra", "path", "duplicate", "pass", "user"])
def test_result_validation(environment: tuple[Path, Path, dict[str, Any]], change: str) -> None:
    root, _, state = environment
    head = publish(root, state)
    observer = Observer(root)
    observer.fetch()
    checkpoint = observer.checkpoint("refs/heads/feat/fixture", head)
    assert checkpoint
    value = result(checkpoint)
    finding = {
        "id": "F1",
        "severity": "major",
        "source_path": "product.py",
        "line": 2,
        "requirement": "Sum faithfully",
        "observation": "Adds one",
        "impact": "Wrong answer",
        "proposed_correction": "Preserve the sum",
        "acceptance_evidence": "Exact sum example",
        "user_decision_required": False,
    }
    if change == "sha":
        value["reviewed_sha"] = "0" * 40
    elif change == "schema":
        value["schema_version"] = True
    elif change == "extra":
        value["approved_for_merge"] = True
    else:
        value.update(verdict="changes_requested", findings=[finding])
        if change == "path":
            finding["source_path"] = "../not-evidence"
        elif change == "duplicate":
            value["findings"].append(finding)
        elif change == "pass":
            value["verdict"] = "pass"
        else:
            finding["user_decision_required"] = True
    with pytest.raises(ObserverError, match="Rejected model review"):
        observer.validate_result(value, checkpoint, {"product.py"})


def test_model_cli_timeout_and_failure(tmp_path: Path) -> None:
    executable = tmp_path / "fake-codex"
    executable.write_text("#!/usr/bin/env python3\nimport time\ntime.sleep(10)\n")
    executable.chmod(0o755)
    observer = Observer(tmp_path, codex=str(executable), timeout=0.05)
    with pytest.raises(ObserverError, match="timed out"):
        observer.run_codex(tmp_path, tmp_path)
    executable.write_text("#!/usr/bin/env python3\nraise SystemExit(5)\n")
    observer.timeout = 5
    with pytest.raises(ObserverError, match="exit 5"):
        observer.run_codex(tmp_path, tmp_path)
    (tmp_path / "model-output.json").write_text('{"old_result": true}')
    executable.write_text("#!/usr/bin/env python3\nraise SystemExit(0)\n")
    with pytest.raises(ObserverError, match="unavailable"):
        observer.run_codex(tmp_path, tmp_path)


def test_committed_schema_matches_runtime() -> None:
    assert json.loads(module.SCHEMA.read_text()) == ReviewResult.model_json_schema()


def test_atomic_persistence_failure_preserves_previous_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "ledger.json"
    path.write_text("previous valid ledger")

    def unavailable(source: str, destination: Path) -> None:
        raise OSError("simulated disk failure")

    monkeypatch.setattr(os, "replace", unavailable)
    with pytest.raises(OSError, match="disk failure"):
        module.atomic_write(path, "replacement")
    assert path.read_text() == "previous valid ledger"
    assert list(tmp_path.iterdir()) == [path]


def test_scan_marks_old_owner_update_stale_without_duplicate_review(
    environment: tuple[Path, Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, state = environment
    observer = Observer(root)
    publish(root, state)
    calls = fake_runner(monkeypatch, observer)
    assert observer.execute("review", "refs/heads/feat/fixture") == 0
    event = next(iter(observer.load().events.values()))
    assert event.report
    git(root, "push", "-q", "origin", ":feat/fixture")
    assert observer.execute("scan") == 3
    assert len(calls) == 1
    assert (Path(event.report) / "owner-update.md").read_text().startswith("# Stale review")


def test_real_cli_protocol_with_fake_executable(
    environment: tuple[Path, Path, dict[str, Any]], tmp_path: Path
) -> None:
    root, _, state = environment
    head = publish(root, state)
    observer = Observer(root)
    observer.fetch()
    checkpoint = observer.checkpoint("refs/heads/feat/fixture", head)
    assert checkpoint
    payload = tmp_path / "payload.json"
    payload.write_text(json.dumps(result(checkpoint)))
    executable = tmp_path / "fake-codex"
    executable.write_text(
        "#!/usr/bin/env python3\nimport pathlib, sys\n"
        "assert sys.argv[1] == 'exec'\n"
        "assert sys.argv[sys.argv.index('--sandbox') + 1] == 'read-only'\n"
        "assert '--dangerously-bypass-approvals-and-sandbox' not in sys.argv\n"
        "assert '--output-schema' in sys.argv and '--json' in sys.argv\n"
        f"payload = pathlib.Path({str(payload)!r}).read_text()\n"
        "pathlib.Path(sys.argv[sys.argv.index('--output-last-message') + 1]).write_text(payload)\n"
    )
    executable.chmod(0o755)
    observer.codex = str(executable)
    assert observer.execute("review", head) == 0


def test_scan_preserves_multiple_checkpoints_between_polls(
    environment: tuple[Path, Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, state = environment
    observer = Observer(root)
    calls = fake_runner(monkeypatch, observer)
    assert observer.execute("init") == 0
    first = publish(root, state)
    (root / "product.py").write_text("def total(values):\n    return sum(values)\n")
    second = commit(root, "replacement publication")
    git(root, "push", "-q", "origin", "feat/fixture")
    assert observer.execute("scan") == 3  # First is historical by the time of review.
    assert calls == [first]
    assert observer.execute("scan") == 0
    assert calls == [first, second]


def test_export_bound_and_nonregular_evidence(
    environment: tuple[Path, Path, dict[str, Any]], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, state = environment
    # Existing nonregular files are evidence; they must never be dereferenced.
    (root / "product.py").unlink()
    (root / "product.py").symlink_to("/etc/passwd")
    implementation = commit(root, "synthetic nonregular owned change")
    state.update(
        status="ready_for_review",
        review_decision="ready_for_review",
        implementation_commit_sha=implementation,
    )
    write_state(root, state)
    head = commit(root, "publication")
    git(root, "push", "-q", "origin", "feat/fixture")
    observer = Observer(root)
    observer.fetch()
    checkpoint = observer.checkpoint("refs/heads/feat/fixture", head)
    assert checkpoint
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    observer.bundle(checkpoint, bundle)
    manifest = json.loads((bundle / "manifest.json").read_text())
    assert "product.py" in manifest["omitted_nontext_or_nonregular"]
    assert not (bundle / "evidence/product.py.txt").exists()
    monkeypatch.setattr(module, "MAX_EXPORT", 1)
    with pytest.raises(ObserverError, match="64 MiB"):
        observer.bundle(checkpoint, bundle)


def test_unrelated_archived_branch_does_not_obstruct_current_task(
    environment: tuple[Path, Path, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _, state = environment
    head = publish(root, state)
    git(root, "branch", "archive/unrelated", head)
    git(root, "push", "-q", "origin", "archive/unrelated")
    observer = Observer(root)
    calls = fake_runner(monkeypatch, observer)
    assert observer.execute("init") == 0
    assert observer.execute("scan") == 0
    assert not calls and not observer.load().scan_errors
