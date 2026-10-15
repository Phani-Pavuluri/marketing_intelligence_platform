"""Independent delegated-routine merge preflight verification.

Read-only eligibility evidence for routine merges. This module never merges,
never activates delegation, never approves anything, and never mutates Git
branches, worktrees, or execution state. Preflight verifies a Git-notes
review receipt against live Git and independently produced observer evidence;
`attach` writes only the dedicated notes ref for reviewers.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import subprocess
import sys
import uuid
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from mip.execution.opencode_advisory import Binding
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

DEDICATED_NOTES_REF = "refs/notes/mip-delegated-routine-receipts"
NOTES_SHORT_REF = "mip-delegated-routine-receipts"
REVIEWER_ROLE = "independent_codex_reviewer"
APPROVAL_KIND = "delegated_routine_merge_approval"
ACTIVATION_KIND = "delegation_activation"
POLICY_DOC = "docs/execution/DELEGATED_ROUTINE_MERGE_POLICY.md"
OBSERVER_DIRNAME = ".codex/review-observer"
ADVISORY_BINDING = ".codex/opencode-advisory/binding.json"
STATE_PATH = "docs/execution/EXECUTION_STATE.json"
DELEGATED_DIRNAME = ".codex/delegated-merge"
LOCK_FILENAME = "attach.lock"

REQUIRED_CONDITIONS = (
    "definition_ready_opt_in",
    "tier_within_routine",
    "ownership_verified",
    "independent_review_exact_head",
    "no_open_findings",
    "validation_all_pass",
    "heads_and_baseline_stable",
    "activation_current",
)
REQUIRED_CATEGORIES = (
    "focused_tests",
    "docker_make_validate",
    "taskctl_check",
    "git_diff_check",
    "ruff",
    "mypy",
)
ALWAYS_REQUIRED = ("taskctl_check", "git_diff_check")

MAX_RECEIPT_BYTES = 256 * 1024
MAX_EVENTS_BYTES = 16 * 1024 * 1024
GIT_TIMEOUT = 30.0


class DelegatedError(Exception):
    """A stable coded preflight failure with a CLI exit status."""

    def __init__(self, code: str, message: str, exit_code: int) -> None:
        super().__init__(message)
        self.code = code
        self.exit_code = exit_code

    def __str__(self) -> str:
        return f"{self.code}: {super().__str__()}"


def _fail(code: str, message: str, exit_code: int) -> DelegatedError:
    return DelegatedError(code, message, exit_code)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


def _uuid(value: str) -> str:
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError("Not a valid UUID") from exc
    if str(parsed) != value.lower():
        raise ValueError("UUID must be canonical lowercase")
    return value


def _parse_moment(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"Invalid timestamp: {exc}") from exc


def _nonempty(value: str) -> str:
    if not value.strip():
        raise ValueError("Must be nonempty after strip")
    return value


class Reviewer(StrictModel):
    role: Literal["independent_codex_reviewer"]
    session_id: str
    implementation_agent_session_id: str = Field(pattern=r"^ses_[A-Za-z0-9]+$")
    reviewer_authored_implementation: Literal[False]
    observer_report_digest: str = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("session_id", mode="after")
    @classmethod
    def _check_session_uuid(cls, value: str) -> str:
        return _uuid(value)


class Provenance(StrictModel):
    policy_version: str
    activation_receipt_id: str
    activation_notes_ref: Literal["refs/notes/mip-delegated-routine-receipts"]
    owner_decision_ref: str
    user_reserved_unchanged: Literal[True]
    activation_head_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("activation_receipt_id", mode="after")
    @classmethod
    def _check_activation_uuid(cls, value: str) -> str:
        return _uuid(value)


class Category(StrictModel):
    status: Literal["pass", "not_required"]
    detail: str
    tree_sha: str | None = Field(pattern=r"^[0-9a-f]{40}$")
    evidence: list[str]


class Validation(StrictModel):
    tier_class: Literal[1, 2]
    categories: dict[str, Category]


class RoutineAssertions(StrictModel):
    within_authorized_scope: Literal[True]
    no_contract_meaning_change: Literal[True]
    no_architecture_change: Literal[True]
    no_authority_change: Literal[True]
    no_sibling_impact: Literal[True]


class QuotedState(StrictModel):
    risk_tier: str
    validation_scope: str
    owned_implementation_paths: list[str]
    task_authoring_boundary: list[str]
    merge_approval_mode: Literal["delegated_routine"]
    capability_authorizations_changed: Literal[False]
    all_protected_authority_false: Literal[True]
    delegated_merge_required_validation: list[str]
    full_suite_validation_required: bool


class Finding(StrictModel):
    condition: Literal[
        "definition_ready_opt_in",
        "tier_within_routine",
        "ownership_verified",
        "independent_review_exact_head",
        "no_open_findings",
        "validation_all_pass",
        "heads_and_baseline_stable",
        "activation_current",
    ]
    result: Literal["pass"]
    evidence: str


class Eligibility(StrictModel):
    tier_class: Literal[1, 2]
    routine_assertions: RoutineAssertions
    quoted_state: QuotedState
    findings: list[Finding]


class Authority(StrictModel):
    capability_authority_added: Literal[False]
    task_authorization_changed: Literal[False]
    statement: str


class Receipt(StrictModel):
    schema_version: Literal[1]
    receipt_kind: Literal["delegated_routine_merge_approval"]
    receipt_id: str
    repository: Literal["Phani-Pavuluri/marketing_intelligence_platform"]
    task_id: str
    feature_branch: str
    merge_approval_mode: Literal["delegated_routine"]
    authorization_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    implementation_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    reviewed_remote_head_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    main_baseline_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    reviewer: Reviewer
    decision: Literal["approve_exact_reviewed_head"]
    issued_at: str
    delegation_provenance: Provenance
    validation: Validation
    eligibility: Eligibility
    authority_impact: Authority
    limitations: list[str]

    @field_validator("receipt_id", mode="after")
    @classmethod
    def _check_receipt_uuid(cls, value: str) -> str:
        return _uuid(value)

    @field_validator("issued_at", mode="after")
    @classmethod
    def _check_receipt_moment(cls, value: str) -> str:
        moment = _parse_moment(value)
        if moment.tzinfo is None or moment.utcoffset() is None:
            raise ValueError("issued_at must carry timezone")
        return value


class ActivationRecord(StrictModel):
    schema_version: Literal[1]
    receipt_kind: Literal["delegation_activation"]
    receipt_id: str
    policy_version: str
    policy_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    prerequisite_head_sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    decision: Literal["activate"]
    scope_tier_classes: list[int]
    owner_decision_ref: str
    issued_at: str
    limitations: list[str]

    @field_validator("receipt_id", mode="after")
    @classmethod
    def _check_activation_record_uuid(cls, value: str) -> str:
        return _uuid(value)

    @field_validator("issued_at", mode="after")
    @classmethod
    def _check_activation_moment(cls, value: str) -> str:
        moment = _parse_moment(value)
        if moment.tzinfo is None or moment.utcoffset() is None:
            raise ValueError("issued_at must carry timezone")
        return value


def now() -> str:
    return datetime.now().astimezone().isoformat()


def canonical_json_bytes(value: Any) -> bytes:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return text.encode("utf-8")


def digest_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def delegated_directory(repository: Path) -> Path:
    return repository.resolve() / DELEGATED_DIRNAME


@contextmanager
def attach_lock(repository: Path) -> Iterator[None]:
    directory = delegated_directory(repository)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / LOCK_FILENAME).open("a", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise _fail(
                "E_DELEGATED_STATE",
                "Another delegation writer owns this repository; retry later.",
                3,
            ) from exc
        try:
            yield
        finally:
            fcntl.flock(handle, fcntl.LOCK_UN)


def git_text(repository: Path, *args: str, timeout: float = GIT_TIMEOUT) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), *args],
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail("E_DELEGATED_TRANSPORT", f"Git command did not settle: {exc}", 3) from exc
    if result.returncode:
        detail = result.stderr.decode(errors="replace").strip()[:300]
        raise _fail("E_DELEGATED_GIT", f"Git command failed: {detail}", 3)
    try:
        return result.stdout.decode("utf-8")
    except UnicodeError as exc:
        raise _fail("E_DELEGATED_GIT", f"Git output is not valid text: {exc}", 3) from exc


def git_origin(directory: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(directory), "remote", "get-url", "origin"],
            capture_output=True,
            timeout=GIT_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail("E_DELEGATED_TRANSPORT", f"Git origin could not be read: {exc}", 3) from exc
    if result.returncode:
        detail = result.stderr.decode(errors="replace").strip()[:300]
        raise _fail("E_DELEGATED_IDENTITY", f"Git origin is unavailable: {detail}", 2)
    return result.stdout.decode(errors="replace").strip()


def require_canonical_origin(raw_origin: str) -> str:
    identity = origin_identity(raw_origin)
    if identity != EXPECTED_ORIGIN:
        raise _fail(
            "E_DELEGATED_IDENTITY",
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
        raise _fail("E_DELEGATED_IDENTITY", f"{label} is not an existing directory.", 2)
    return candidate


def ls_remote(url: str, ref: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "ls-remote", url, ref],
            capture_output=True,
            timeout=GIT_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail("E_DELEGATED_TRANSPORT", f"Remote ref read did not settle: {exc}", 3) from exc
    if result.returncode:
        detail = result.stderr.decode(errors="replace").strip()[:300]
        raise _fail("E_DELEGATED_TRANSPORT", f"Remote ref read failed: {detail}", 3)
    try:
        text = result.stdout.decode("utf-8")
    except UnicodeError as exc:
        raise _fail("E_DELEGATED_TRANSPORT", f"Remote ref output invalid: {exc}", 3) from exc
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) == 2 and parts[1].strip() == ref:
            return parts[0].strip()
    return None


def require_notes_ref(value: str | None) -> str:
    ref = value or DEDICATED_NOTES_REF
    if ref != DEDICATED_NOTES_REF:
        raise _fail("E_DELEGATED_REF", "Only the dedicated delegation notes ref is accepted.", 2)
    return ref


def load_receipt_dict(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise _fail("E_DELEGATED_RECEIPT", f"Receipt file is unavailable: {exc}", 2) from exc
    if len(raw) > MAX_RECEIPT_BYTES:
        raise _fail("E_DELEGATED_RECEIPT", "Receipt file exceeds the bounded size.", 2)
    try:
        value = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise _fail("E_DELEGATED_RECEIPT", f"Receipt file is not valid JSON: {exc}", 2) from exc
    if not isinstance(value, dict):
        raise _fail("E_DELEGATED_RECEIPT", "Receipt file must contain a JSON object.", 2)
    return value


def parse_receipt(raw: dict[str, Any]) -> Receipt:
    try:
        return Receipt.model_validate(raw)
    except ValidationError as exc:
        raise _fail(
            "E_DELEGATED_RECEIPT",
            f"Receipt schema invalid: {exc.errors()[0]['msg']}",
            2,
        ) from exc


def check_receipt_invariants(receipt: Receipt) -> None:
    for value in (receipt.task_id, receipt.feature_branch, receipt.authority_impact.statement):
        if not value.strip():
            raise _fail("E_DELEGATED_RECEIPT", "Receipt strings must be nonempty after strip.", 2)
    if receipt.validation.tier_class != receipt.eligibility.tier_class:
        raise _fail("E_DELEGATED_RECEIPT", "Receipt tier classes disagree.", 2)
    conditions = [finding.condition for finding in receipt.eligibility.findings]
    if sorted(conditions) != sorted(REQUIRED_CONDITIONS):
        raise _fail(
            "E_DELEGATED_RECEIPT",
            "Receipt findings must be exactly the eight conditions.",
            2,
        )
    for finding in receipt.eligibility.findings:
        if not finding.evidence.strip():
            raise _fail("E_DELEGATED_RECEIPT", "Receipt finding evidence must be nonempty.", 2)
    required = list(receipt.eligibility.quoted_state.delegated_merge_required_validation)
    if len(set(required)) != len(required) or not required:
        raise _fail(
            "E_DELEGATED_RECEIPT",
            "Required validation declarations must be unique nonempty.",
            2,
        )
    for name in required:
        if name not in REQUIRED_CATEGORIES:
            raise _fail("E_DELEGATED_RECEIPT", f"Unknown required validation category: {name}", 2)
    for name in ALWAYS_REQUIRED:
        if name not in required:
            raise _fail("E_DELEGATED_RECEIPT", f"Required validation must include {name}.", 2)
    if receipt.eligibility.tier_class == 2 and "focused_tests" not in required:
        raise _fail("E_DELEGATED_RECEIPT", "Tier 2 requires focused_tests.", 2)
    if receipt.eligibility.quoted_state.full_suite_validation_required:
        for name in ("docker_make_validate", "ruff", "mypy"):
            if name not in required:
                raise _fail("E_DELEGATED_RECEIPT", f"Full suite requires {name}.", 2)
    categories = receipt.validation.categories
    for name in required:
        category = categories.get(name)
        if category is None:
            raise _fail("E_DELEGATED_RECEIPT", f"Required category missing: {name}.", 2)
        if category.status != "pass":
            raise _fail("E_DELEGATED_RECEIPT", f"Required category not passing: {name}.", 2)
        if category.tree_sha != receipt.reviewed_remote_head_sha:
            raise _fail(
                "E_DELEGATED_RECEIPT",
                f"Required category tree mismatch: {name}.",
                2,
            )
        if not category.detail.strip() or not category.evidence:
            raise _fail("E_DELEGATED_RECEIPT", f"Required category lacks evidence: {name}.", 2)
    for name, category in categories.items():
        if name not in required:
            if category.status != "not_required":
                raise _fail(
                    "E_DELEGATED_RECEIPT",
                    f"Optional category must be not_required: {name}.",
                    2,
                )
            if category.tree_sha is not None or category.evidence:
                raise _fail("E_DELEGATED_RECEIPT", f"Optional category must be empty: {name}.", 2)
            if not category.detail.strip():
                raise _fail("E_DELEGATED_RECEIPT", f"Optional category needs a reason: {name}.", 2)
    for name in list(required) + [n for n in categories if n not in required]:
        for entry in categories[name].evidence:
            if not entry.strip() or entry.startswith("/") or ".." in Path(entry).parts:
                raise _fail("E_DELEGATED_EVIDENCE", f"Evidence path escapes the bundle: {entry}", 2)
    if not receipt.limitations or any(not item.strip() for item in receipt.limitations):
        raise _fail("E_DELEGATED_RECEIPT", "Receipt limitations must be nonempty.", 2)
    prefix = "tier_1" if receipt.eligibility.tier_class == 1 else "tier_2"
    if not receipt.eligibility.quoted_state.risk_tier.startswith(prefix):
        raise _fail("E_DELEGATED_RECEIPT", "Receipt tier class mismatches canonical risk tier.", 2)


def do_validate_receipt(receipt_path: Path) -> Receipt:
    raw = load_receipt_dict(receipt_path)
    receipt = parse_receipt(raw)
    check_receipt_invariants(receipt)
    return receipt


def show_note(repository: Path, short_ref: str, target: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), "notes", "--ref", short_ref, "show", target],
            capture_output=True,
            timeout=GIT_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail("E_DELEGATED_TRANSPORT", f"Note read did not settle: {exc}", 3) from exc
    if result.returncode:
        return None
    try:
        return result.stdout.decode("utf-8")
    except UnicodeError as exc:
        raise _fail(
            "E_DELEGATED_NOTE_CORRUPT",
            f"Existing note is not valid text: {exc}",
            2,
        ) from exc


def list_notes(repository: Path, short_ref: str) -> list[tuple[str, str]]:
    try:
        result = subprocess.run(
            ["git", "-C", str(repository), "notes", "--ref", short_ref, "list"],
            capture_output=True,
            timeout=GIT_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise _fail("E_DELEGATED_TRANSPORT", f"Note listing did not settle: {exc}", 3) from exc
    if result.returncode:
        return []
    try:
        text = result.stdout.decode("utf-8")
    except UnicodeError as exc:
        raise _fail(
            "E_DELEGATED_NOTE_CORRUPT",
            f"Note listing is not valid text: {exc}",
            2,
        ) from exc
    entries: list[tuple[str, str]] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) == 2:
            entries.append((parts[0].strip(), parts[1].strip()))
    return entries


def load_ledger(repository: Path) -> Ledger:
    try:
        return Observer(repository).load()
    except ObserverError as exc:
        raise _fail("E_DELEGATED_EVIDENCE", f"Review ledger is unavailable: {exc}", 2) from exc


def load_binding(repository: Path) -> Binding:
    path = repository.resolve() / ADVISORY_BINDING
    if not path.is_file():
        raise _fail("E_DELEGATED_IDENTITY", "Implementation binding record is missing.", 2)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return Binding.model_validate(raw)
    except (OSError, ValueError, ValidationError) as exc:
        raise _fail(
            "E_DELEGATED_IDENTITY",
            f"Implementation binding record is invalid: {exc}",
            2,
        ) from exc


def event_key(task_id: str, sha: str) -> str:
    return f"{task_id}:completion:{sha}"


def check_observer_evidence(
    repository: Path, receipt: Receipt
) -> tuple[Event, dict[str, Any], Path]:
    ledger = load_ledger(repository)
    key = event_key(receipt.task_id, receipt.reviewed_remote_head_sha)
    event = ledger.events.get(key)
    if event is None:
        raise _fail("E_DELEGATED_EVIDENCE", "Review event key is unknown.", 2)
    if event.kind != "completion":
        raise _fail("E_DELEGATED_EVIDENCE", "Closure events are ineligible.", 2)
    if event.status != "completed":
        raise _fail("E_DELEGATED_EVIDENCE", "Review event is not completed.", 2)
    if event.stale:
        raise _fail("E_DELEGATED_EVIDENCE", "Review event is stale.", 2)
    if event.report is None or event.verdict is None:
        raise _fail("E_DELEGATED_EVIDENCE", "Review event evidence is incomplete.", 2)
    report = Path(event.report)
    try:
        resolved = report.resolve()
    except OSError as exc:
        raise _fail(
            "E_DELEGATED_EVIDENCE",
            f"Review report directory is invalid: {exc}",
            2,
        ) from exc
    result_path = resolved / "result.json"
    if not result_path.is_file() or result_path.is_symlink():
        raise _fail("E_DELEGATED_EVIDENCE", "Review result evidence is incomplete.", 2)
    try:
        raw_text = result_path.read_text(encoding="utf-8")
        raw = json.loads(raw_text)
        if type(raw.get("schema_version")) is not int:
            raise ValueError("Invalid result version type")
        result = ReviewResult.model_validate(raw)
    except (OSError, ValueError, ValidationError) as exc:
        raise _fail(
            "E_DELEGATED_EVIDENCE",
            f"Review result evidence is malformed: {exc}",
            2,
        ) from exc
    for actual, wanted in (
        (result.repository, REPOSITORY),
        (result.task_id, event.task_id),
        (result.checkpoint_kind, event.kind),
        (result.reviewed_sha, event.sha),
    ):
        if actual != wanted:
            raise _fail("E_DELEGATED_EVIDENCE", "Review result mismatched ledger evidence.", 2)
    if result.verdict != "pass":
        raise _fail("E_DELEGATED_EVIDENCE", "Review verdict is not pass.", 2)
    if event.verdict is not None and result.verdict != event.verdict:
        raise _fail("E_DELEGATED_EVIDENCE", "Review result mismatched ledger evidence.", 2)
    digest = digest_bytes(canonical_json_bytes(raw))
    if digest != receipt.reviewer.observer_report_digest:
        raise _fail("E_DELEGATED_EVIDENCE", "Observer report digest mismatched.", 2)
    events_path = resolved / "events.jsonl"
    if not events_path.is_file() or events_path.is_symlink():
        raise _fail("E_DELEGATED_EVIDENCE", "Review execution events are missing.", 2)
    try:
        if events_path.stat().st_size > MAX_EVENTS_BYTES:
            raise _fail("E_DELEGATED_EVIDENCE", "Review execution events exceed the bound.", 2)
        lines = events_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise _fail(
            "E_DELEGATED_EVIDENCE",
            f"Review execution events unreadable: {exc}",
            2,
        ) from exc
    if not lines:
        raise _fail("E_DELEGATED_EVIDENCE", "Review execution events are empty.", 2)
    started = False
    try:
        for line in lines:
            if not line.strip():
                continue
            entry = json.loads(line)
            if isinstance(entry, dict) and entry.get("type") == "thread.started":
                thread_id = entry.get("thread_id")
                if thread_id == receipt.reviewer.session_id:
                    started = True
    except ValueError as exc:
        raise _fail("E_DELEGATED_EVIDENCE", f"Review execution events malformed: {exc}", 2) from exc
    if not started:
        raise _fail("E_DELEGATED_EVIDENCE", "Independent reviewer run UUID not corroborated.", 2)
    model_output = resolved / "model-output.json"
    if not model_output.is_file() or model_output.is_symlink():
        raise _fail("E_DELEGATED_EVIDENCE", "Completed model turn evidence is missing.", 2)
    try:
        output = json.loads(model_output.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise _fail(
            "E_DELEGATED_EVIDENCE",
            f"Completed model turn evidence malformed: {exc}",
            2,
        ) from exc
    if not isinstance(output, dict):
        raise _fail("E_DELEGATED_EVIDENCE", "Completed model turn evidence malformed.", 2)
    return event, raw, resolved


def check_binding_identity(repository: Path, receipt: Receipt) -> None:
    binding = load_binding(repository)
    if binding.session_id != receipt.reviewer.implementation_agent_session_id:
        raise _fail("E_DELEGATED_IDENTITY", "Implementation session mismatched binding record.", 2)
    if receipt.reviewer.session_id == binding.session_id:
        raise _fail("E_DELEGATED_IDENTITY", "Reviewer session equals implementation session.", 2)
    review_hex = receipt.reviewer.session_id.replace("-", "").lower()
    for value in (binding.session_id, binding.project_id):
        if review_hex and review_hex in value.lower():
            raise _fail(
                "E_DELEGATED_IDENTITY",
                "Reviewer identity attributed to implementation.",
                2,
            )


def check_checkpoint(repository: Path, event: Event) -> None:
    try:
        checkpoint = Observer(repository).checkpoint(event.ref, event.sha)
    except ObserverError as exc:
        raise _fail("E_DELEGATED_EVIDENCE", f"Checkpoint identity unverifiable: {exc}", 2) from exc
    if checkpoint is None:
        raise _fail("E_DELEGATED_EVIDENCE", "Checkpoint is not an eligible completion.", 2)
    if checkpoint.key != f"{event.task_id}:{event.kind}:{event.sha}":
        raise _fail("E_DELEGATED_EVIDENCE", "Checkpoint identity mismatched ledger evidence.", 2)


def check_quoted_state(repository: Path, receipt: Receipt) -> None:
    try:
        text = git_text(repository, "show", f"{receipt.reviewed_remote_head_sha}:{STATE_PATH}")
    except DelegatedError as exc:
        raise _fail(
            "E_DELEGATED_EVIDENCE",
            f"Reviewed canonical state unreadable: {exc}",
            2,
        ) from exc
    try:
        state = json.loads(text)
    except ValueError as exc:
        raise _fail(
            "E_DELEGATED_EVIDENCE",
            f"Reviewed canonical state malformed: {exc}",
            2,
        ) from exc
    if not isinstance(state, dict):
        raise _fail("E_DELEGATED_EVIDENCE", "Reviewed canonical state malformed.", 2)
    quoted = receipt.eligibility.quoted_state
    for field, expected in (
        ("risk_tier", quoted.risk_tier),
        ("validation_scope", quoted.validation_scope),
        ("owned_implementation_paths", quoted.owned_implementation_paths),
        ("task_authoring_boundary", quoted.task_authoring_boundary),
        ("merge_approval_mode", quoted.merge_approval_mode),
        ("capability_authorizations_changed", quoted.capability_authorizations_changed),
    ):
        if state.get(field) != expected:
            raise _fail("E_DELEGATED_EVIDENCE", f"Quoted canonical state mismatched: {field}.", 2)
    if state.get("merge_approval_mode") != "delegated_routine":
        raise _fail("E_DELEGATED_NON_ROUTINE", "Reviewed task did not opt into delegation.", 2)
    actual_protected = all(
        value is False
        for key, value in state.items()
        if key.endswith("_authorized")
        and key not in {"task_execution_authorized", "correction_execution_authorized"}
    )
    if not quoted.all_protected_authority_false or not actual_protected:
        raise _fail("E_DELEGATED_NON_ROUTINE", "Protected authority is not uniformly false.", 2)
    if not quoted.risk_tier.startswith("tier_1") and not quoted.risk_tier.startswith("tier_2"):
        raise _fail("E_DELEGATED_NON_ROUTINE", "Risk tier is not routine-eligible.", 2)


def check_ancestry(repository: Path, receipt: Receipt) -> None:
    for ancestor, head in (
        (receipt.authorization_sha, receipt.implementation_sha),
        (receipt.implementation_sha, receipt.reviewed_remote_head_sha),
    ):
        try:
            result = subprocess.run(
                ["git", "-C", str(repository), "merge-base", "--is-ancestor", ancestor, head],
                capture_output=True,
                timeout=GIT_TIMEOUT,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise _fail(
                "E_DELEGATED_TRANSPORT",
                f"Ancestry check did not settle: {exc}",
                3,
            ) from exc
        if result.returncode:
            raise _fail("E_DELEGATED_EVIDENCE", "Authorization ancestry does not hold.", 2)


def check_evidence_paths(report: Path, receipt: Receipt) -> None:
    seen: set[str] = set()
    for category in receipt.validation.categories.values():
        for entry in category.evidence:
            if entry in seen:
                continue
            seen.add(entry)
            target = (report / entry)
            try:
                resolved = target.resolve()
            except OSError as exc:
                raise _fail("E_DELEGATED_EVIDENCE", f"Evidence path invalid: {entry}", 2) from exc
            try:
                resolved.relative_to(report.resolve())
            except ValueError as exc:
                raise _fail(
                    "E_DELEGATED_EVIDENCE",
                    f"Evidence path escapes bundle: {entry}",
                    2,
                ) from exc
            if not resolved.is_file() or resolved.is_symlink():
                raise _fail("E_DELEGATED_EVIDENCE", f"Evidence artifact missing: {entry}", 2)


def check_activation(repository: Path, receipt: Receipt, live_main: str) -> None:
    short = NOTES_SHORT_REF
    entries = list_notes(repository, short)
    if not entries:
        raise _fail("E_DELEGATED_NOT_ACTIVATED", "No delegation activation is recorded.", 2)
    provenance = receipt.delegation_provenance
    found = False
    for _, target in entries:
        content = show_note(repository, short, target)
        if content is None:
            continue
        try:
            record_raw = json.loads(content)
            record = ActivationRecord.model_validate(record_raw)
        except (ValueError, ValidationError):
            continue
        if record.receipt_id != provenance.activation_receipt_id:
            continue
        found = True
        if record.decision != "activate":
            raise _fail("E_DELEGATED_NOT_ACTIVATED", "Delegation is not activated.", 2)
        if record.scope_tier_classes != [1, 2]:
            raise _fail("E_DELEGATED_NOT_ACTIVATED", "Activation scope mismatched.", 2)
        if record.policy_version != provenance.policy_version:
            raise _fail("E_DELEGATED_POLICY", "Activation policy version mismatched.", 2)
        if record.prerequisite_head_sha != provenance.activation_head_sha:
            raise _fail("E_DELEGATED_NOT_ACTIVATED", "Activation target mismatched.", 2)
        if target != provenance.activation_head_sha:
            raise _fail("E_DELEGATED_NOT_ACTIVATED", "Activation target mismatched.", 2)
        try:
            activation_moment = _parse_moment(record.issued_at)
        except ValueError as exc:
            raise _fail(
                "E_DELEGATED_NOT_ACTIVATED",
                f"Activation timestamp invalid: {exc}",
                2,
            ) from exc
        if activation_moment.tzinfo is None or activation_moment.utcoffset() is None:
            raise _fail("E_DELEGATED_NOT_ACTIVATED", "Activation record timestamp invalid.", 2)
        try:
            result = subprocess.run(
                ["git", "-C", str(repository), "merge-base", "--is-ancestor", target, live_main],
                capture_output=True,
                timeout=GIT_TIMEOUT,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise _fail(
                "E_DELEGATED_TRANSPORT",
                f"Activation ancestry unsettled: {exc}",
                3,
            ) from exc
        if result.returncode:
            raise _fail("E_DELEGATED_NOT_ACTIVATED", "Activation target is not a main ancestor.", 2)
        try:
            policy_bytes = git_text(repository, "show", f"{live_main}:{POLICY_DOC}").encode("utf-8")
        except DelegatedError as exc:
            raise _fail("E_DELEGATED_POLICY", f"Policy document unreadable: {exc}", 2) from exc
        live_hash = digest_bytes(policy_bytes)
        if record.policy_sha256 != live_hash or provenance.policy_sha256 != live_hash:
            raise _fail("E_DELEGATED_POLICY", "Policy content drifted without version bump.", 2)
        break
    if not found:
        raise _fail("E_DELEGATED_NOT_ACTIVATED", "No delegation activation is recorded.", 2)


def parse_moment(value: str, label: str) -> datetime:
    try:
        moment = datetime.fromisoformat(value)
    except ValueError as exc:
        raise _fail("E_DELEGATED_EVIDENCE", f"{label} timestamp invalid: {exc}", 2) from exc
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise _fail("E_DELEGATED_EVIDENCE", f"{label} timestamp must carry timezone.", 2)
    return moment


def do_preflight(repository: Path, receipt_path: Path, notes_ref: str | None) -> dict[str, Any]:
    review_root = resolve_existing_directory(repository, "Review repository")
    ref = require_notes_ref(notes_ref)
    short = NOTES_SHORT_REF
    raw = load_receipt_dict(receipt_path)
    receipt = parse_receipt(raw)
    check_receipt_invariants(receipt)
    require_canonical_origin(git_origin(review_root))
    try:
        local_value = git_text(review_root, "rev-parse", "--verify", ref).strip()
    except DelegatedError as exc:
        raise _fail(
            "E_DELEGATED_NOTE_MISSING",
            f"Local delegation notes ref missing: {exc}",
            2,
        ) from exc
    origin = git_text(review_root, "remote", "get-url", "origin").strip()
    live_notes = ls_remote(origin, ref)
    if live_notes is None:
        raise _fail("E_DELEGATED_NOTE_MISSING", "Delegation notes ref is not pushed.", 2)
    if local_value != live_notes:
        raise _fail("E_DELEGATED_NOTE_STALE", "Local notes ref mismatches the live remote ref.", 2)
    live_branch = ls_remote(origin, f"refs/heads/{receipt.feature_branch}")
    if live_branch is None:
        raise _fail("E_DELEGATED_EVIDENCE", "Feature branch has no live remote head.", 2)
    if live_branch != receipt.reviewed_remote_head_sha:
        raise _fail("E_DELEGATED_EVIDENCE", "Live branch head replaced the reviewed head.", 2)
    live_main = ls_remote(origin, "refs/heads/main")
    if live_main is None:
        raise _fail("E_DELEGATED_TRANSPORT", "Live main head is unavailable.", 3)
    if live_main != receipt.main_baseline_sha:
        raise _fail("E_DELEGATED_BASELINE", "Main moved beyond the reviewed baseline.", 2)
    content = show_note(review_root, short, receipt.reviewed_remote_head_sha)
    if content is None:
        raise _fail(
            "E_DELEGATED_NOTE_MISSING",
            "No receipt note is attached to the reviewed head.",
            2,
        )
    try:
        note_raw = json.loads(content)
    except ValueError as exc:
        raise _fail(
            "E_DELEGATED_NOTE_CORRUPT",
            f"Attached note is corrupt; preserved: {exc}",
            2,
        ) from exc
    if canonical_json_bytes(note_raw) != canonical_json_bytes(raw):
        raise _fail("E_DELEGATED_EVIDENCE", "Receipt file mismatches the attached note.", 2)
    event, _, report = check_observer_evidence(review_root, receipt)
    receipt_moment = parse_moment(receipt.issued_at, "Receipt")
    event_moment = parse_moment(event.updated_at, "Review event")
    if receipt_moment < event_moment:
        raise _fail("E_DELEGATED_EVIDENCE", "Receipt predates review completion.", 2)
    check_binding_identity(review_root, receipt)
    check_checkpoint(review_root, event)
    check_quoted_state(review_root, receipt)
    check_ancestry(review_root, receipt)
    check_evidence_paths(report, receipt)
    check_activation(review_root, receipt, live_main)
    return {
        "status": "eligible",
        "task_id": receipt.task_id,
        "reviewed_head": receipt.reviewed_remote_head_sha,
        "notes_ref": ref,
        "notes_value": live_notes,
    }


def do_attach(
    repository: Path, receipt_path: Path, head: str, notes_ref: str | None
) -> tuple[str, dict[str, Any]]:
    if not head.strip() or len(head.strip()) != 40:
        raise _fail("E_DELEGATED_REF", "Head must be a 40-character commit SHA.", 2)
    head = head.strip().lower()
    review_root = resolve_existing_directory(repository, "Review repository")
    ref = require_notes_ref(notes_ref)
    short = NOTES_SHORT_REF
    raw = load_receipt_dict(receipt_path)
    receipt = parse_receipt(raw)
    check_receipt_invariants(receipt)
    if receipt.receipt_kind != APPROVAL_KIND:
        raise _fail("E_DELEGATED_KIND", "Only approval receipts may be attached here.", 2)
    if head != receipt.reviewed_remote_head_sha:
        raise _fail("E_DELEGATED_REF", "Head mismatches the receipt reviewed head.", 2)
    require_canonical_origin(git_origin(review_root))
    with attach_lock(review_root):
        existing = show_note(review_root, short, head)
        canonical = canonical_json_bytes(raw)
        if existing is not None:
            try:
                existing_raw = json.loads(existing)
            except ValueError as exc:
                raise _fail(
                    "E_DELEGATED_NOTE_CORRUPT",
                    f"Existing note corrupt; preserved: {exc}",
                    2,
                ) from exc
            if canonical_json_bytes(existing_raw) == canonical:
                return ("already-attached", {"head": head, "notes_ref": ref})
            raise _fail(
                "E_DELEGATED_NOTE_CONFLICT",
                "A different note already annotates this head.",
                2,
            )
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(review_root),
                    "notes",
                    "--ref",
                    short,
                    "add",
                    "-m",
                    canonical.decode("utf-8"),
                    head,
                ],
                capture_output=True,
                timeout=GIT_TIMEOUT,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise _fail("E_DELEGATED_TRANSPORT", f"Note attach did not settle: {exc}", 3) from exc
        if result.returncode:
            detail = result.stderr.decode(errors="replace").strip()[:300]
            raise _fail("E_DELEGATED_TRANSPORT", f"Note attach failed: {detail}", 3)
        return ("attached", {"head": head, "notes_ref": ref})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=GIT_TIMEOUT)
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate-receipt")
    validate.add_argument("--receipt", required=True, type=Path)
    preflight = commands.add_parser("preflight")
    preflight.add_argument("--repository", required=True, type=Path)
    preflight.add_argument("--receipt", required=True, type=Path)
    preflight.add_argument("--notes-ref", default=DEDICATED_NOTES_REF)
    attach = commands.add_parser("attach")
    attach.add_argument("--repository", required=True, type=Path)
    attach.add_argument("--receipt", required=True, type=Path)
    attach.add_argument("--head", required=True)
    attach.add_argument("--notes-ref", default=DEDICATED_NOTES_REF)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    global GIT_TIMEOUT
    try:
        if args.timeout <= 0:
            raise _fail("E_DELEGATED_STATE", "Timeout must be positive.", 3)
        GIT_TIMEOUT = args.timeout
        if args.command == "validate-receipt":
            receipt = do_validate_receipt(args.receipt)
            print(json.dumps({"status": "valid", "receipt_id": receipt.receipt_id}, indent=2))
            return 0
        if args.command == "preflight":
            summary = do_preflight(args.repository, args.receipt, args.notes_ref)
            print(json.dumps(summary, indent=2))
            return 0
        outcome, info = do_attach(args.repository, args.receipt, args.head, args.notes_ref)
        print(json.dumps({"status": outcome, **info}, indent=2))
        return 0
    except DelegatedError as exc:
        print(str(exc), file=sys.stderr)
        return exc.exit_code
    except (OSError, ValueError) as exc:
        print(f"E_DELEGATED_STATE: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
