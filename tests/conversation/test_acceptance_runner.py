from pathlib import Path

import pytest

from mip.conversation.acceptance_runner import (
    AcceptanceCheckpointStore,
    AcceptanceRunner,
    CaseCheckpoint,
    CaseState,
    RunCheckpoint,
)


def runner(tmp_path: Path) -> tuple[AcceptanceRunner, AcceptanceCheckpointStore]:
    run = RunCheckpoint(
        "a",
        "r",
        "v",
        "groq",
        "model",
        "conversational_provider_wire_v3",
        2,
        [CaseCheckpoint("s", "test", "readiness_probe"), CaseCheckpoint("s", "mmm", "provider")],
    )
    store = AcceptanceCheckpointStore(tmp_path / "state.json")
    return AcceptanceRunner(run, store), store


def test_reservation_is_durable_and_conservative(tmp_path: Path) -> None:
    r, s = runner(tmp_path)
    c = r.run.cases[1]
    r.start(c)
    r.reserve(c)
    loaded = s.load()
    assert (
        loaded.provider_calls_reserved == 1
        and loaded.cases[1].state is CaseState.PROVIDER_CALL_RESERVED
    )
    r.reconcile_interruption()
    assert s.load().cases[1].state is CaseState.RESULT_MISSING


def test_deterministic_case_consumes_zero_calls(tmp_path: Path) -> None:
    r, s = runner(tmp_path)
    c = r.run.cases[0]
    r.start(c)
    r.complete(c, passed=True)
    assert s.load().provider_calls_reserved == 0


def test_corrupt_state_fails_closed_and_no_sensitive_content(tmp_path: Path) -> None:
    r, s = runner(tmp_path)
    s.path.write_text("{")
    with pytest.raises(ValueError):
        s.load()
    r, s = runner(tmp_path)
    r.start(r.run.cases[0])
    r.complete(r.run.cases[0], passed=True)
    text = s.path.read_text()
    assert "Authorization" not in text and "sk-" not in text and "prompt" not in text


def test_interruption_matrix_and_resume_safety(tmp_path: Path) -> None:
    r, s = runner(tmp_path)
    readiness, provider = r.run.cases
    assert r.resumable_cases() == [readiness, provider]  # before start
    r.start(readiness)  # after durable start
    assert r.resumable_cases() == [provider]
    r.complete(readiness, passed=True)  # after terminal persistence
    r.start(provider)
    r.reserve(provider)  # after reservation/before invocation or during invocation
    r.reconcile_interruption()  # response missing or terminal write interrupted
    loaded = s.load()
    assert loaded.cases[1].state is CaseState.RESULT_MISSING
    assert loaded.provider_calls_reserved == 1
    resumed = AcceptanceRunner(loaded, s)
    assert resumed.resumable_cases() == []
    assert resumed.resumable_cases(override=True) == loaded.cases


def test_budget_and_private_markers_are_never_persisted(tmp_path: Path) -> None:
    r, s = runner(tmp_path)
    r.run.maximum_provider_calls = 0
    r.start(r.run.cases[1])
    with pytest.raises(RuntimeError, match="provider_call_budget_exhausted"):
        r.reserve(r.run.cases[1])
    r.complete(r.run.cases[0], passed=True)
    persisted = s.path.read_text()
    for marker in ("synthetic-prompt", "synthetic-response", "transcript", "Bearer", "sk-"):
        assert marker not in persisted
