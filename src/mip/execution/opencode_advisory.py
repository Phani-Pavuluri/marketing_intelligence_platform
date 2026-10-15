"""Deliver completed MIP checkpoint reviews to a verified OpenCode session.

Advisory transport only. This module never controls an implementation agent,
never runs Codex inference, and never mutates Git worktrees, branches, or
repository state. It binds one explicit recipient session, formats bounded
advisory evidence from an existing completed review-observer event, and admits
that evidence through ``opencode api session.prompt`` with ``resume:false``.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
import tempfile
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from mip.execution.review_observer import (
    EXPECTED_ORIGIN,
    REPOSITORY,
    Event,
    Ledger,
    Observer,
    ObserverError,
    ReviewResult,
    origin_identity,
)

EXPECTED_PROVIDER = "opencode"
EXPECTED_MODEL = "muse-spark-1.3-contributor-free"
EXPECTED_VARIANT = "high"
EXPECTED_AGENT = "build"

ADVISORY_DIRNAME = ".codex/opencode-advisory"
BINDING_FILENAME = "binding.json"
JOURNAL_FILENAME = "deliveries.json"
LOCK_FILENAME = "advisory.lock"

MAX_ADVISORY_CHARS = 12000
DEFAULT_TIMEOUT = 60.0
DEFAULT_OPENCODE_BIN = "opencode"


class AdvisoryError(Exception):
    """A stable coded advisory failure with a CLI exit status."""

    def __init__(self, code: str, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code

    def __str__(self) -> str:
        return f"{self.code}: {super().__str__()}"


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Binding(StrictModel):
    schema_version: Literal[1]
    repository: str = Field(min_length=1)
    review_repository: str = Field(min_length=1)
    review_origin: str = Field(min_length=1)
    implementation_directory: str = Field(min_length=1)
    implementation_origin: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    project_id: str = Field(min_length=1)
    provider: str = Field(min_length=1)
    model: str = Field(min_length=1)
    variant: str = Field(min_length=1)
    agent: str = Field(min_length=1)
    bound_at: str = Field(min_length=1)


class Delivery(StrictModel):
    event_key: str = Field(min_length=1)
    repository: str = Field(min_length=1)
    task_id: str = Field(min_length=1)
    kind: Literal["completion"]
    sha: str = Field(min_length=1)
    session_id: str = Field(min_length=1)
    status: Literal["admitted", "indeterminate"]
    message_id: str | None
    attempted_at: str = Field(min_length=1)
    updated_at: str = Field(min_length=1)
    error: str | None
    advisory_marker: str = Field(min_length=1)


class Journal(StrictModel):
    schema_version: Literal[1]
    deliveries: dict[str, Delivery]


def now() -> str:
    return datetime.now(UTC).isoformat()


def _fail(code: str, message: str, exit_code: int) -> AdvisoryError:
    return AdvisoryError(code, message, exit_code)


def advisory_directory(repository: Path) -> Path:
    return repository.resolve() / ADVISORY_DIRNAME


def binding_path(repository: Path) -> Path:
    return advisory_directory(repository) / BINDING_FILENAME


def journal_path(repository: Path) -> Path:
    return advisory_directory(repository) / JOURNAL_FILENAME


def lock_path(repository: Path) -> Path:
    return advisory_directory(repository) / LOCK_FILENAME


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".advisory-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


@contextmanager
def advisory_lock(repository: Path) -> Iterator[None]:
    directory = advisory_directory(repository)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / LOCK_FILENAME).open("a", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise _fail(
                "E_ADVISORY_STATE",
                "Another advisory writer owns this repository; retry later.",
                3,
            ) from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def git_origin(directory: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(directory), "remote", "get-url", "origin"],
            capture_output=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail("E_ADVISORY_IDENTITY", f"Git origin could not be read: {exc}", 2) from exc
    if result.returncode:
        detail = result.stderr.decode(errors="replace").strip()
        raise _fail("E_ADVISORY_IDENTITY", f"Git origin is unavailable: {detail}", 2)
    return result.stdout.decode(errors="replace").strip()


def require_canonical_origin(raw_origin: str) -> str:
    identity = origin_identity(raw_origin)
    if identity != EXPECTED_ORIGIN:
        raise _fail(
            "E_ADVISORY_IDENTITY",
            "Repository origin is not the expected MIP repository.",
            2,
        )
    return identity


def resolve_existing_directory(path: Path, label: str) -> Path:
    candidate = path.expanduser()
    if not candidate.is_absolute():
        candidate = (Path.cwd() / candidate).resolve()
    else:
        candidate = candidate.resolve()
    if not candidate.is_dir():
        raise _fail("E_ADVISORY_IDENTITY", f"{label} is not an existing directory.", 2)
    return candidate


def session_get(
    session_id: str, *, opencode_bin: str = DEFAULT_OPENCODE_BIN, timeout: float = DEFAULT_TIMEOUT
) -> dict[str, Any]:
    if not session_id.strip():
        raise _fail("E_ADVISORY_IDENTITY", "Session ID must be non-empty.", 2)
    if timeout <= 0:
        raise _fail("E_ADVISORY_STATE", "Transport timeout must be positive.", 3)
    try:
        result = subprocess.run(
            [opencode_bin, "api", "session.get", "--param", f"sessionID={session_id}"],
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail("E_ADVISORY_TRANSPORT", f"OpenCode session.get unavailable: {exc}", 3) from exc
    if result.returncode:
        detail = result.stderr.decode(errors="replace").strip()[:500]
        raise _fail("E_ADVISORY_TRANSPORT", f"OpenCode session.get failed: {detail}", 3)
    try:
        payload = json.loads(result.stdout.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise _fail(
            "E_ADVISORY_TRANSPORT",
            f"OpenCode session.get returned invalid JSON: {exc}",
            3,
        ) from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), dict):
        raise _fail("E_ADVISORY_TRANSPORT", "OpenCode session.get acknowledgment was invalid.", 3)
    data = payload["data"]
    if not isinstance(data, dict):
        raise _fail("E_ADVISORY_TRANSPORT", "OpenCode session.get acknowledgment was invalid.", 3)
    return data


def _string_field(data: dict[str, Any], *names: str) -> str | None:
    for name in names:
        value = data.get(name)
        if isinstance(value, str) and value:
            return value
    return None


def parse_session_identity(data: dict[str, Any]) -> dict[str, str]:
    session_id = _string_field(data, "id", "sessionID")
    project_id = _string_field(data, "projectID", "project_id")
    agent = _string_field(data, "agent")
    location = data.get("location")
    directory = None
    if isinstance(location, dict):
        value = location.get("directory")
        if isinstance(value, str) and value:
            directory = value
    if directory is None:
        direct = data.get("directory")
        if isinstance(direct, str) and direct:
            directory = direct
    model = data.get("model")
    provider: str | None = None
    model_id: str | None = None
    variant: str | None = None
    if isinstance(model, dict):
        maybe_provider = model.get("providerID", model.get("provider"))
        maybe_model = model.get("id", model.get("model"))
        maybe_variant = model.get("variant")
        if isinstance(maybe_provider, str) and maybe_provider:
            provider = maybe_provider
        if isinstance(maybe_model, str) and maybe_model:
            model_id = maybe_model
        if isinstance(maybe_variant, str) and maybe_variant:
            variant = maybe_variant
    if (
        session_id is None
        or project_id is None
        or agent is None
        or directory is None
        or provider is None
        or model_id is None
        or variant is None
    ):
        raise _fail("E_ADVISORY_IDENTITY", "OpenCode session identity is incomplete.", 2)
    return {
        "session_id": session_id,
        "project_id": project_id,
        "agent": agent,
        "directory": directory,
        "provider": provider,
        "model": model_id,
        "variant": variant,
    }


def require_expected_session(
    data: dict[str, Any], *, session_id: str, implementation_directory: Path
) -> dict[str, str]:
    identity = parse_session_identity(data)
    if identity["session_id"] != session_id:
        raise _fail(
            "E_ADVISORY_IDENTITY",
            "OpenCode session ID does not match the bound recipient.",
            2,
        )
    try:
        observed_directory = Path(identity["directory"]).expanduser().resolve()
    except OSError as exc:
        raise _fail(
            "E_ADVISORY_IDENTITY",
            f"OpenCode session directory is invalid: {exc}",
            2,
        ) from exc
    if observed_directory != implementation_directory.resolve():
        raise _fail("E_ADVISORY_IDENTITY", "OpenCode session directory does not match.", 2)
    if identity["provider"] != EXPECTED_PROVIDER:
        raise _fail(
            "E_ADVISORY_IDENTITY",
            "OpenCode session provider is not the expected recipient.",
            2,
        )
    if identity["model"] != EXPECTED_MODEL:
        raise _fail(
            "E_ADVISORY_IDENTITY",
            "OpenCode session model is not the expected recipient.",
            2,
        )
    if identity["variant"] != EXPECTED_VARIANT:
        raise _fail(
            "E_ADVISORY_IDENTITY",
            "OpenCode session variant is not the expected recipient.",
            2,
        )
    if identity["agent"] != EXPECTED_AGENT:
        raise _fail(
            "E_ADVISORY_IDENTITY",
            "OpenCode session agent is not the expected recipient.",
            2,
        )
    return identity


def session_prompt(
    session_id: str,
    text: str,
    *,
    opencode_bin: str = DEFAULT_OPENCODE_BIN,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    if not text.strip():
        raise _fail("E_ADVISORY_STATE", "Advisory text must be non-empty.", 3)
    if len(text) > MAX_ADVISORY_CHARS:
        raise _fail("E_ADVISORY_STATE", "Advisory text exceeds the bounded limit.", 3)
    if timeout <= 0:
        raise _fail("E_ADVISORY_STATE", "Transport timeout must be positive.", 3)
    body = json.dumps({"text": text, "resume": False}, ensure_ascii=False)
    try:
        result = subprocess.run(
            [
                opencode_bin,
                "api",
                "session.prompt",
                "--param",
                f"sessionID={session_id}",
                "-d",
                body,
            ],
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail(
            "E_ADVISORY_INDETERMINATE",
            f"OpenCode session.prompt did not settle: {exc}",
            3,
        ) from exc
    if result.returncode:
        detail = result.stderr.decode(errors="replace").strip()[:500]
        raise _fail("E_ADVISORY_TRANSPORT", f"OpenCode session.prompt failed: {detail}", 3)
    try:
        payload = json.loads(result.stdout.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise _fail(
            "E_ADVISORY_INDETERMINATE",
            f"OpenCode prompt acknowledgment was invalid: {exc}",
            3,
        ) from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), dict):
        raise _fail("E_ADVISORY_INDETERMINATE", "OpenCode prompt acknowledgment was invalid.", 3)
    data = payload["data"]
    if not isinstance(data, dict):
        raise _fail("E_ADVISORY_INDETERMINATE", "OpenCode prompt acknowledgment was invalid.", 3)
    message_id = data.get("id")
    returned_session = data.get("sessionID", data.get("session_id"))
    if not isinstance(message_id, str) or not message_id:
        raise _fail("E_ADVISORY_INDETERMINATE", "OpenCode prompt acknowledgment was invalid.", 3)
    if returned_session != session_id:
        raise _fail(
            "E_ADVISORY_INDETERMINATE",
            "OpenCode prompt acknowledgment mismatched session.",
            3,
        )
    return message_id


def load_binding(repository: Path) -> Binding:
    path = binding_path(repository)
    if not path.exists():
        raise _fail(
            "E_ADVISORY_IDENTITY",
            "No advisory recipient is bound; bind a session first.",
            2,
        )
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        binding = Binding.model_validate(raw)
    except (OSError, ValueError, ValidationError) as exc:
        raise _fail(
            "E_ADVISORY_STATE",
            f"Invalid advisory binding; preserved without reset: {exc}",
            3,
        ) from exc
    if binding.repository != REPOSITORY:
        raise _fail("E_ADVISORY_IDENTITY", "Advisory binding belongs to a different repository.", 2)
    return binding


def load_journal(repository: Path) -> Journal:
    path = journal_path(repository)
    if not path.exists():
        return Journal(schema_version=1, deliveries={})
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return Journal.model_validate(raw)
    except (OSError, ValueError, ValidationError) as exc:
        raise _fail(
            "E_ADVISORY_STATE",
            f"Invalid advisory journal; preserved without reset: {exc}",
            3,
        ) from exc


def save_binding(repository: Path, binding: Binding) -> None:
    atomic_write(binding_path(repository), binding.model_dump_json(indent=2) + "\n")


def save_journal(repository: Path, journal: Journal) -> None:
    atomic_write(journal_path(repository), journal.model_dump_json(indent=2) + "\n")


def delivery_key(task_id: str, kind: str, sha: str, session_id: str) -> str:
    return f"{task_id}:{kind}:{sha}:{session_id}"


def load_ledger(repository: Path) -> Ledger:
    observer = Observer(repository)
    try:
        return observer.load()
    except ObserverError as exc:
        raise _fail("E_ADVISORY_EVIDENCE", f"Review ledger is unavailable: {exc}", 2) from exc


def load_review_result(report_dir: str) -> ReviewResult:
    report = Path(report_dir)
    try:
        resolved = report.resolve()
    except OSError as exc:
        raise _fail("E_ADVISORY_EVIDENCE", f"Review report directory is invalid: {exc}", 2) from exc
    result_path = resolved / "result.json"
    if not result_path.is_file():
        raise _fail("E_ADVISORY_EVIDENCE", "Review result evidence is incomplete.", 2)
    try:
        raw = json.loads(result_path.read_text(encoding="utf-8"))
        if type(raw.get("schema_version")) is not int:
            raise ValueError("Invalid result version type")
        return ReviewResult.model_validate(raw)
    except (OSError, ValueError, ValidationError) as exc:
        raise _fail(
            "E_ADVISORY_EVIDENCE",
            f"Review result evidence is malformed: {exc}",
            2,
        ) from exc


def require_eligible_event(event: Event) -> None:
    if event.kind != "completion":
        raise _fail(
            "E_ADVISORY_EVIDENCE",
            "Closure events are ineligible for advisory delivery.",
            2,
        )
    if event.status != "completed":
        raise _fail("E_ADVISORY_EVIDENCE", "Review event is not a completed review.", 2)
    if event.stale:
        raise _fail("E_ADVISORY_STALE", "Review event is stale; a new review is required.", 2)
    if event.report is None or event.verdict is None:
        raise _fail("E_ADVISORY_EVIDENCE", "Review event evidence is incomplete.", 2)


def verify_checkpoint_identity(repository: Path, event: Event) -> None:
    observer = Observer(repository)
    try:
        checkpoint = observer.checkpoint(event.ref, event.sha)
    except ObserverError as exc:
        raise _fail(
            "E_ADVISORY_EVIDENCE",
            f"Checkpoint identity could not be verified: {exc}",
            2,
        ) from exc
    if checkpoint is None:
        raise _fail("E_ADVISORY_EVIDENCE", "Checkpoint is not an eligible completion.", 2)
    if checkpoint.key != f"{event.task_id}:{event.kind}:{event.sha}":
        raise _fail("E_ADVISORY_EVIDENCE", "Checkpoint identity mismatched ledger evidence.", 2)


def require_matching_result(event: Event, result: ReviewResult) -> None:
    expected = (
        (result.repository, REPOSITORY),
        (result.task_id, event.task_id),
        (result.checkpoint_kind, event.kind),
        (result.reviewed_sha, event.sha),
    )
    for actual, wanted in expected:
        if actual != wanted:
            raise _fail("E_ADVISORY_EVIDENCE", "Review result mismatched ledger evidence.", 2)
    if event.verdict is not None and result.verdict != event.verdict:
        raise _fail("E_ADVISORY_EVIDENCE", "Review result mismatched ledger evidence.", 2)


def advisory_marker(task_id: str, kind: str, sha: str, session_id: str) -> str:
    return f"[MIP advisory {task_id}:{kind}:{sha[:12]} -> {session_id}]"


def format_advisory(
    *,
    event: Event,
    result: ReviewResult,
    session_id: str,
    project_id: str,
) -> str:
    marker = advisory_marker(event.task_id, event.kind, event.sha, session_id)
    lines: list[str] = [
        marker,
        "",
        f"Reviewed task: {event.task_id}",
        f"Reviewed head: {event.sha} ({event.ref})",
        f"Review verdict: {result.verdict}",
        f"Session recipient: {session_id} (project {project_id})",
        "",
        "Summary:",
        result.summary,
        "",
        f"Findings ({len(result.findings)}):",
    ]
    reserved: list[str] = []
    if not result.findings:
        lines.append("None.")
    for finding in result.findings:
        flag = str(finding.user_decision_required).lower()
        where = finding.line if finding.line is not None else "unspecified"
        lines.extend(
            [
                "",
                f"- [{finding.id} {finding.severity} "
                f"user_decision_required={flag}] "
                f"{finding.source_path}:{where}",
                f"  Requirement: {finding.requirement}",
                f"  Observation: {finding.observation}",
                f"  Impact: {finding.impact}",
                f"  Recommendation: {finding.proposed_correction}",
                f"  Acceptance evidence: {finding.acceptance_evidence}",
            ]
        )
        if finding.user_decision_required:
            reserved.append(f"- {finding.id}: {finding.requirement} (see {finding.source_path})")
    lines.extend(["", "Limitations:"])
    if result.limitations:
        for item in result.limitations:
            lines.append(f"- {item}")
    else:
        lines.append("None reported.")
    owner_needed = [d for d in result.owner_update.decisions_needed if d.strip()]
    if owner_needed:
        for item in owner_needed:
            reserved.append(f"- owner decision needed: {item}")
    lines.extend(
        ["", "Owner-reserved decisions (require owner input;", "agent agreement cannot resolve):"]
    )
    if reserved:
        lines.extend(reserved)
    else:
        lines.append("None. Pass feedback below, if any, is advisory only.")
    lines.extend(
        [
            "",
            "Authority and handling:",
            "- Git owns authorized scope; Muse-Spark owns implementation choices.",
            "- This advisory is evidence only, not task, approval, execution, correction,",
            "  merge, or pause/release instructions.",
            "- No implementation command, correction authorization, merge approval,",
            "  or pause/release control is introduced.",
            "- Findings marked user_decision_required remain pending owner input.",
            "- Delivery admission is not proof the session read or implemented findings.",
        ]
    )
    text = "\n".join(lines) + "\n"
    if len(text) <= MAX_ADVISORY_CHARS:
        return text
    truncated: list[str] = [
        marker,
        "",
        f"Reviewed task: {event.task_id}",
        f"Reviewed head: {event.sha} ({event.ref})",
        f"Review verdict: {result.verdict}",
        f"Session recipient: {session_id} (project {project_id})",
        "",
        "Summary:",
        result.summary[:2000],
        "",
        "Findings: truncated to fit the bounded limit; read the full report.",
        "",
        "Limitations:",
        "- Bounded advisory output; full evidence remains in the review report.",
        "",
        "Owner-reserved decisions (require owner input;",
        "agent agreement cannot resolve):",
        "- Withheld by truncation; consult the full review report before deciding.",
        "",
        "Authority and handling:",
        "- Git owns authorized scope; Muse-Spark owns implementation choices.",
        "- This advisory is evidence only, not task, approval, execution, correction,",
        "  merge, or pause/release instructions.",
        "- Delivery admission is not proof the session read or implemented findings.",
    ]
    bounded = "\n".join(truncated) + "\n"
    return bounded[:MAX_ADVISORY_CHARS]


def do_bind(
    repository: Path,
    session_id: str,
    implementation_directory: Path,
    *,
    opencode_bin: str = DEFAULT_OPENCODE_BIN,
    timeout: float = DEFAULT_TIMEOUT,
) -> Binding:
    review_root = resolve_existing_directory(repository, "Review repository")
    implementation_root = resolve_existing_directory(
        implementation_directory, "Implementation directory"
    )
    review_origin = require_canonical_origin(git_origin(review_root))
    implementation_origin = require_canonical_origin(git_origin(implementation_root))
    data = session_get(session_id, opencode_bin=opencode_bin, timeout=timeout)
    identity = require_expected_session(
        data, session_id=session_id, implementation_directory=implementation_root
    )
    binding = Binding(
        schema_version=1,
        repository=REPOSITORY,
        review_repository=str(review_root),
        review_origin=review_origin,
        implementation_directory=str(implementation_root),
        implementation_origin=implementation_origin,
        session_id=identity["session_id"],
        project_id=identity["project_id"],
        provider=identity["provider"],
        model=identity["model"],
        variant=identity["variant"],
        agent=identity["agent"],
        bound_at=now(),
    )
    with advisory_lock(review_root):
        save_binding(review_root, binding)
    return binding


def do_send(
    repository: Path,
    event_key: str,
    *,
    opencode_bin: str = DEFAULT_OPENCODE_BIN,
    timeout: float = DEFAULT_TIMEOUT,
) -> tuple[str, Delivery]:
    if not event_key.strip():
        raise _fail("E_ADVISORY_EVIDENCE", "Event key must be non-empty.", 2)
    review_root = resolve_existing_directory(repository, "Review repository")
    with advisory_lock(review_root):
        binding = load_binding(review_root)
        current_origin = require_canonical_origin(git_origin(review_root))
        if current_origin != binding.review_origin:
            raise _fail(
                "E_ADVISORY_IDENTITY",
                "Review checkout origin mismatched the bound origin.",
                2,
            )
        ledger = load_ledger(review_root)
        event = ledger.events.get(event_key)
        if event is None:
            raise _fail("E_ADVISORY_EVIDENCE", "Review event key is unknown.", 2)
        require_eligible_event(event)
        if event.report is None:
            raise _fail("E_ADVISORY_EVIDENCE", "Review event evidence is incomplete.", 2)
        result = load_review_result(event.report)
        require_matching_result(event, result)
        verify_checkpoint_identity(review_root, event)
        data = session_get(binding.session_id, opencode_bin=opencode_bin, timeout=timeout)
        identity = require_expected_session(
            data,
            session_id=binding.session_id,
            implementation_directory=Path(binding.implementation_directory),
        )
        if identity["project_id"] != binding.project_id:
            raise _fail(
                "E_ADVISORY_IDENTITY",
                "OpenCode session project changed since binding.",
                2,
            )
        journal = load_journal(review_root)
        key = delivery_key(event.task_id, event.kind, event.sha, binding.session_id)
        existing = journal.deliveries.get(key)
        if existing is not None and existing.status == "admitted":
            return ("already-admitted", existing)
        if existing is not None and existing.status == "indeterminate":
            raise _fail(
                "E_ADVISORY_INDETERMINATE",
                "Prior delivery is indeterminate; reconcile before retrying.",
                3,
            )
        text = format_advisory(
            event=event,
            result=result,
            session_id=binding.session_id,
            project_id=binding.project_id,
        )
        marker = advisory_marker(event.task_id, event.kind, event.sha, binding.session_id)
        reservation = Delivery(
            event_key=event_key,
            repository=REPOSITORY,
            task_id=event.task_id,
            kind="completion",
            sha=event.sha,
            session_id=binding.session_id,
            status="indeterminate",
            message_id=None,
            attempted_at=now(),
            updated_at=now(),
            error="reserved before transport",
            advisory_marker=marker,
        )
        journal.deliveries[key] = reservation
        save_journal(review_root, journal)
        try:
            message_id = session_prompt(
                binding.session_id, text, opencode_bin=opencode_bin, timeout=timeout
            )
        except AdvisoryError as exc:
            failure = Delivery(
                event_key=event_key,
                repository=REPOSITORY,
                task_id=event.task_id,
                kind="completion",
                sha=event.sha,
                session_id=binding.session_id,
                status="indeterminate",
                message_id=None,
                attempted_at=reservation.attempted_at,
                updated_at=now(),
                error=f"{exc.code}: transport did not settle",
                advisory_marker=marker,
            )
            journal.deliveries[key] = failure
            save_journal(review_root, journal)
            raise
        admitted = Delivery(
            event_key=event_key,
            repository=REPOSITORY,
            task_id=event.task_id,
            kind="completion",
            sha=event.sha,
            session_id=binding.session_id,
            status="admitted",
            message_id=message_id,
            attempted_at=reservation.attempted_at,
            updated_at=now(),
            error=None,
            advisory_marker=marker,
        )
        journal.deliveries[key] = admitted
        save_journal(review_root, journal)
        return ("admitted", admitted)


def do_status(repository: Path) -> dict[str, Any]:
    review_root = resolve_existing_directory(repository, "Review repository")
    with advisory_lock(review_root):
        binding = load_binding(review_root)
        journal = load_journal(review_root)
        return {
            "repository": REPOSITORY,
            "review_repository": str(review_root),
            "binding": binding.model_dump(),
            "deliveries": {key: value.model_dump() for key, value in journal.deliveries.items()},
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--opencode-bin", default=DEFAULT_OPENCODE_BIN)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    commands = parser.add_subparsers(dest="command", required=True)
    bind = commands.add_parser("bind")
    bind.add_argument("--session", required=True)
    bind.add_argument("--implementation-directory", required=True, type=Path)
    send = commands.add_parser("send")
    send.add_argument("--event-key", required=True)
    commands.add_parser("status")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.timeout <= 0:
            raise _fail("E_ADVISORY_STATE", "Transport timeout must be positive.", 3)
        if args.command == "bind":
            binding = do_bind(
                args.repository,
                args.session,
                args.implementation_directory,
                opencode_bin=args.opencode_bin,
                timeout=args.timeout,
            )
            print(json.dumps({"status": "bound", "binding": binding.model_dump()}, indent=2))
            return 0
        if args.command == "send":
            outcome, delivery = do_send(
                args.repository,
                args.event_key,
                opencode_bin=args.opencode_bin,
                timeout=args.timeout,
            )
            print(json.dumps({"status": outcome, "delivery": delivery.model_dump()}, indent=2))
            return 0
        status = do_status(args.repository)
        print(json.dumps({"status": "ok", **status}, indent=2))
        return 0
    except AdvisoryError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code
    except (OSError, ValueError) as exc:
        print(f"E_ADVISORY_STATE: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
