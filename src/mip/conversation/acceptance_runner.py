"""Durable, sanitized checkpointing for bounded live-acceptance runners."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path


class CaseState(StrEnum):
    NOT_STARTED = "not_started"
    STARTED = "started"
    PROVIDER_CALL_RESERVED = "provider_call_reserved"
    PROVIDER_CALL_COMPLETED = "provider_call_completed"
    PASSED = "passed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"
    RESULT_MISSING = "result_missing"
    EXECUTION_STATE_UNKNOWN = "execution_state_unknown"
    SKIPPED = "skipped"


class Resumability(StrEnum):
    NOT_SENT = "confirmed_not_sent"
    SENT_WITH_RESULT = "confirmed_sent_with_sanitized_result"
    SENT_RESULT_MISSING = "confirmed_sent_result_missing"
    UNKNOWN = "execution_state_unknown"


def _now() -> str:
    return datetime.now(UTC).isoformat()


@dataclass
class CaseCheckpoint:
    suite_id: str
    case_id: str
    route_type: str
    state: CaseState = CaseState.NOT_STARTED
    resumability_classification: Resumability = Resumability.NOT_SENT
    started_at: str | None = None
    terminal_at: str | None = None
    provider_invoked: bool = False
    provider_call_reserved: bool = False
    safe_request_id: str | None = None
    safe_provider_code: str | None = None
    failure_stage: str | None = None
    structured_parse_status: str | None = None
    mapping_status: str | None = None
    claim_guard_status: str | None = None
    fallback_used: bool | None = None
    latency_ms: int | None = None


@dataclass
class RunCheckpoint:
    acceptance_id: str
    run_id: str
    runner_version: str
    provider_id: str
    model_id: str
    wire_schema_version: str
    maximum_provider_calls: int
    cases: list[CaseCheckpoint]
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    provider_calls_reserved: int = 0
    provider_calls_completed: int = 0
    deterministic_cases_completed: int = 0
    next_case_id: str | None = None
    run_status: str = "running"


class AcceptanceCheckpointStore:
    def __init__(self, path: Path):
        self.path = path

    def save(self, run: RunCheckpoint) -> None:
        run.updated_at = _now()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_suffix(".tmp")
        temp.write_text(json.dumps(asdict(run), sort_keys=True), encoding="utf-8")
        os.replace(temp, self.path)

    def load(self) -> RunCheckpoint:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError("corrupt_acceptance_checkpoint") from exc
        try:
            raw["cases"] = [
                CaseCheckpoint(
                    state=CaseState(c["state"]),
                    resumability_classification=Resumability(c["resumability_classification"]),
                    **{
                        k: v
                        for k, v in c.items()
                        if k not in {"state", "resumability_classification"}
                    },
                )
                for c in raw["cases"]
            ]
            return RunCheckpoint(**raw)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("corrupt_acceptance_checkpoint") from exc


class AcceptanceRunner:
    def __init__(self, run: RunCheckpoint, store: AcceptanceCheckpointStore):
        self.run, self.store = run, store

    def start(self, case: CaseCheckpoint) -> None:
        case.state = CaseState.STARTED
        case.started_at = _now()
        self.run.next_case_id = case.case_id
        self.store.save(self.run)

    def reserve(self, case: CaseCheckpoint) -> None:
        if self.run.provider_calls_reserved >= self.run.maximum_provider_calls:
            raise RuntimeError("provider_call_budget_exhausted")
        self.run.provider_calls_reserved += 1
        case.provider_call_reserved = True
        case.provider_invoked = True
        case.state = CaseState.PROVIDER_CALL_RESERVED
        case.resumability_classification = Resumability.SENT_RESULT_MISSING
        self.store.save(self.run)

    def complete(self, case: CaseCheckpoint, *, passed: bool, **safe: object) -> None:
        for key, value in safe.items():
            setattr(case, key, value)
        if case.provider_call_reserved:
            self.run.provider_calls_completed += 1
        else:
            self.run.deterministic_cases_completed += 1
        case.state = CaseState.PASSED if passed else CaseState.FAILED
        case.resumability_classification = (
            Resumability.SENT_WITH_RESULT if case.provider_invoked else Resumability.NOT_SENT
        )
        case.terminal_at = _now()
        self.store.save(self.run)

    def reconcile_interruption(self) -> None:
        for case in self.run.cases:
            if case.state is CaseState.PROVIDER_CALL_RESERVED and case.terminal_at is None:
                case.state = CaseState.RESULT_MISSING
                case.resumability_classification = Resumability.SENT_RESULT_MISSING
        self.store.save(self.run)

    def resumable_cases(self, *, override: bool = False) -> list[CaseCheckpoint]:
        if override:
            return self.run.cases
        return [
            case
            for case in self.run.cases
            if case.state is CaseState.NOT_STARTED
            and case.resumability_classification is Resumability.NOT_SENT
        ]
