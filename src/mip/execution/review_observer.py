"""Advisory exact-commit checkpoint reviews; never controls an implementation agent."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from mip.execution.errors import TaskControlError
from mip.execution.state import validate_state
from mip.execution.views import assert_execution_view, render_execution_view

REPOSITORY = "Phani-Pavuluri/marketing_intelligence_platform"
EXPECTED_ORIGIN = f"github.com/{REPOSITORY}"
STATE_PATH = "docs/execution/EXECUTION_STATE.json"
ACTIVE_PATH = "docs/execution/ACTIVE_TASK.md"
REPORT_PATH = "docs/execution/LATEST_COMPLETION_REPORT.md"
INSTRUCTIONS = Path(__file__).resolve().parents[3] / "docs/execution/REVIEW_OBSERVER.md"
SCHEMA = Path(__file__).with_name("review_observer.schema.json")
MAX_EXPORT = 64 * 1024 * 1024


class ObserverError(Exception):
    """A visible failure which cannot grant approval."""


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Finding(StrictModel):
    id: str = Field(min_length=1)
    severity: Literal["critical", "major", "minor", "suggestion"]
    source_path: str = Field(min_length=1)
    line: int | None = Field(ge=1)
    requirement: str = Field(min_length=1)
    observation: str = Field(min_length=1)
    impact: str = Field(min_length=1)
    proposed_correction: str = Field(min_length=1)
    acceptance_evidence: str = Field(min_length=1)
    user_decision_required: bool


class OwnerUpdate(StrictModel):
    goal_impact: str = Field(min_length=1)
    completed: list[str]
    ongoing: list[str]
    planned: list[str]
    issues: list[str]
    decisions_needed: list[str]
    recommendation: str = Field(min_length=1)


class ReviewResult(StrictModel):
    schema_version: Literal[1]
    repository: str
    task_id: str
    checkpoint_kind: Literal["completion", "closure"]
    reviewed_sha: str
    verdict: Literal["pass", "changes_requested", "needs_user", "blocked"]
    summary: str = Field(min_length=1)
    findings: list[Finding]
    limitations: list[str]
    owner_update: OwnerUpdate


class Event(StrictModel):
    ref: str
    task_id: str
    kind: Literal["completion", "closure"]
    sha: str
    status: Literal["pending", "running", "completed", "blocked"]
    updated_at: str
    report: str | None
    error: str | None
    verdict: Literal["pass", "changes_requested", "needs_user", "blocked"] | None
    stale: bool


class Ledger(StrictModel):
    schema_version: Literal[1]
    initialized_at: str
    baseline: list[str]
    observed_refs: dict[str, str]
    events: dict[str, Event]
    scan_errors: list[str]


class Checkpoint(StrictModel):
    ref: str
    sha: str
    kind: Literal["completion", "closure"]
    state: dict[str, Any]
    paths: list[str]

    @property
    def key(self) -> str:
        return f"{self.state['task_id']}:{self.kind}:{self.sha}"


def now() -> str:
    return datetime.now(UTC).isoformat()


def origin_identity(url: str) -> str:
    for prefix in ("git@github.com:", "https://github.com/", "ssh://git@github.com/"):
        if url.startswith(prefix):
            return "github.com/" + url[len(prefix) :].removesuffix(".git").rstrip("/")
    return url


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=".observer-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


class Observer:
    def __init__(self, repository: Path, *, codex: str = "codex", timeout: float = 900) -> None:
        self.repository = repository.resolve()
        self.directory = self.repository / ".codex/review-observer"
        self.mirror = self.directory / "mirror.git"
        self.ledger_path = self.directory / "ledger.json"
        self.codex = codex
        self.timeout = timeout
        if timeout <= 0:
            raise ObserverError("Review timeout must be positive.")

    def git(self, *args: str, mirror: bool = True) -> bytes:
        location = ["--git-dir", str(self.mirror)] if mirror else ["-C", str(self.repository)]
        try:
            result = subprocess.run(
                ["git", *location, *args], capture_output=True, timeout=30, check=False
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ObserverError(f"Git command failed: {exc}") from exc
        if result.returncode:
            raise ObserverError(result.stderr.decode(errors="replace").strip())
        return result.stdout

    @contextmanager
    def lock(self) -> Iterator[None]:
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / "observer.lock").open("a") as handle:
            try:
                fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ObserverError("Another observer owns this repository; retry later.") from exc
            try:
                yield
            finally:
                fcntl.flock(handle, fcntl.LOCK_UN)

    def fetch(self) -> dict[str, str]:
        origin = self.git("remote", "get-url", "origin", mirror=False).decode().strip()
        if origin_identity(origin) != EXPECTED_ORIGIN:
            raise ObserverError("Repository origin is not the expected MIP repository.")
        if not self.mirror.exists():
            self.git("init", "--bare", str(self.mirror), mirror=False)
            self.git("remote", "add", "origin", origin)
        mirror_origin = self.git("remote", "get-url", "origin").decode().strip()
        if mirror_origin != origin:
            raise ObserverError("Observer mirror origin differs from the repository origin.")
        self.git("fetch", "--prune", "origin", "+refs/heads/*:refs/heads/*")
        lines = self.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/heads").decode()
        return dict(line.split(" ", 1) for line in lines.splitlines())

    def load(self) -> Ledger:
        if not self.ledger_path.exists():
            raise ObserverError(
                "Initialize the observer with init before scanning or viewing status."
            )
        try:
            raw = json.loads(self.ledger_path.read_text())
            if type(raw.get("schema_version")) is not int:
                raise ValueError("Invalid ledger version type")
            ledger = Ledger.model_validate(raw)
        except (OSError, ValueError, AttributeError, ValidationError) as exc:
            raise ObserverError(f"Invalid ledger; preserved without reset: {exc}") from exc
        for event in ledger.events.values():
            if event.status == "running":
                event.status = "blocked"
                event.error = "Review was interrupted. Explicit review --ref is required to retry."
                event.verdict = "blocked"
                event.updated_at = now()
        return ledger

    def save(self, ledger: Ledger) -> None:
        atomic_write(self.ledger_path, ledger.model_dump_json(indent=2) + "\n")
        reports = [(key, event) for key, event in ledger.events.items() if event.report]
        if reports:
            key, _ = max(reports, key=lambda item: item[1].updated_at)
            relative = Path("reports") / hashlib.sha256(key.encode()).hexdigest()
            owner = self.directory / relative / "owner-update.md"
            if owner.exists():
                content = owner.read_text()
                for name in ("review.md", "result.json", "error.txt"):
                    content = content.replace(f"]({name})", f"]({relative.as_posix()}/{name})")
                if ledger.scan_errors:
                    content = (
                        "# Evidence refresh needs attention\n\nThe latest scan has errors. "
                        "The previous review below is historical evidence, not a current "
                        "readiness conclusion. Details are in ledger.json.\n\n" + content
                    )
                atomic_write(self.directory / "owner-update.md", content)
        elif ledger.scan_errors:
            atomic_write(
                self.directory / "owner-update.md",
                (
                    "# Your MIP update\n\nReview is blocked because remote evidence could "
                    "not be verified. No conclusion about completed work is available.\n\n"
                    "Next: resolve the scan errors listed in ledger.json, then retry.\n"
                ),
            )

    def blob(self, sha: str, path: str) -> str:
        return self.git("show", f"{sha}:{path}").decode("utf-8")

    def ancestor(self, ancestor: str, head: str) -> None:
        self.git("merge-base", "--is-ancestor", ancestor, head)

    def changed(self, base: str, head: str) -> list[str]:
        return self.git("diff", "--name-only", "-z", base, head).decode().rstrip("\0").split("\0")

    def checkpoint(self, ref: str, sha: str) -> Checkpoint | None:
        if not self.git("ls-tree", sha, "--", STATE_PATH).strip():
            return None
        try:
            state = json.loads(self.blob(sha, STATE_PATH))
            validate_state(state)
            if state["status"] not in {"ready_for_review", "merged"}:
                return None
            kind: Literal["completion", "closure"] = (
                "closure" if state["status"] == "merged" else "completion"
            )
            expected_ref = (
                "refs/heads/main"
                if kind == "closure"
                else ("refs/heads/" + state["feature_branch"])
            )
            if ref != expected_ref:
                if ref == "refs/heads/main" and kind == "completion":
                    # A reviewed implementation may be published on main before closure.
                    return None
                raise ObserverError("Checkpoint is on an unexpected branch for its lifecycle.")
            for path, document in (
                (ACTIVE_PATH, "active_task"),
                (REPORT_PATH, "completion_report"),
            ):
                assert_execution_view(
                    self.blob(sha, path),
                    render_execution_view(state, document=document),
                    document=path,
                )
            auth = state["authorization_head_sha"]
            self.ancestor(state["base_sha"], auth)
            self.ancestor(auth, state["implementation_commit_sha"])
            self.ancestor(state["implementation_commit_sha"], sha)
            boundary = {STATE_PATH, ACTIVE_PATH, REPORT_PATH}
            authored = set(self.changed(state["base_sha"], auth))
            if authored != boundary:
                raise ObserverError("Authorization boundary is not exactly the three stable files.")
            # Authoring finalization is the first descendant with unchanged contract authority.
            history = self.git("rev-list", "--reverse", "--ancestry-path", f"{auth}..{sha}")
            baseline: str | None = None
            for commit in history.decode().splitlines():
                candidate = json.loads(self.blob(commit, STATE_PATH))
                if (
                    candidate.get("authorization_head_sha") == auth
                    and (candidate.get("task_id") == state["task_id"])
                    and candidate.get("status") == "authorized"
                ):
                    baseline = commit
                    break
            if baseline is None:
                raise ObserverError("Finalized task authorization baseline was not found.")
            if set(self.changed(auth, baseline)) - boundary:
                raise ObserverError("Authorization finalization changed non-metadata paths.")
            authorized = json.loads(self.blob(baseline, STATE_PATH))
            for field in (
                "repository",
                "task_id",
                "feature_branch",
                "authorization_head_sha",
                "base_sha",
                "owned_implementation_paths",
                "task_authoring_boundary",
                "risk_tier",
                "validation_scope",
                "merge_approval_mode",
            ):
                if state.get(field) != authorized.get(field):
                    raise ObserverError(f"Task authority changed after authorization: {field}")
            for field, value in authorized.items():
                if (
                    field.endswith("_authorized")
                    and field
                    not in {"task_execution_authorized", "correction_execution_authorized"}
                    and state.get(field) != value
                ):
                    raise ObserverError(f"Authority changed after authorization: {field}")
            paths = [path for path in self.changed(baseline, sha) if path]
            owned = state.get("owned_implementation_paths")
            if not isinstance(owned, list) or not all(isinstance(p, str) for p in owned):
                raise ObserverError("Task owned paths are missing or invalid.")
            if set(paths) - (set(owned) | boundary):
                raise ObserverError("Checkpoint includes changes outside task-owned paths.")
            if (
                self.blob(sha, ACTIVE_PATH).split("<!-- END MIP TASKCTL EXECUTION VIEW -->", 1)[1]
                != (
                    self.blob(baseline, ACTIVE_PATH).split(
                        "<!-- END MIP TASKCTL EXECUTION VIEW -->", 1
                    )[1]
                )
            ):
                raise ObserverError("Task contract changed after authorization.")
            if kind == "closure":
                reviewed = state["reviewed_head_sha"]
                parents = self.git("show", "-s", "--format=%P", sha).decode().split()
                if parents != [reviewed]:
                    raise ObserverError(
                        "Closure is not one commit directly after the reviewed head."
                    )
                reviewed_state = json.loads(self.blob(reviewed, STATE_PATH))
                validate_state(reviewed_state)
                if reviewed_state["status"] != "ready_for_review" or any(
                    reviewed_state.get(k) != state.get(k)
                    for k in ("task_id", "authorization_head_sha", "implementation_commit_sha")
                ):
                    raise ObserverError(
                        "Closure reviewed head does not match published task evidence."
                    )
                if set(self.changed(reviewed, sha)) - boundary:
                    raise ObserverError(
                        "Closure changed files outside the three execution documents."
                    )
            return Checkpoint(ref=ref, sha=sha, kind=kind, state=state, paths=paths)
        except (
            ValueError,
            KeyError,
            UnicodeError,
            TypeError,
            AttributeError,
            TaskControlError,
        ) as exc:
            raise ObserverError(f"Invalid checkpoint evidence: {exc}") from exc

    def candidates(self, refs: dict[str, str], ledger: Ledger) -> list[Checkpoint]:
        ledger.scan_errors = []
        checkpoints: list[Checkpoint] = []
        try:
            main_head = refs["refs/heads/main"]
            scope = json.loads(self.blob(main_head, STATE_PATH))
            validate_state(scope)
        except (KeyError, ValueError, TypeError, AttributeError, TaskControlError, ObserverError):
            ledger.scan_errors = ["Current main task authority could not be verified."]
            return []
        for ref, sha in sorted(refs.items()):
            if ref != "refs/heads/main":
                if ref != "refs/heads/" + scope["feature_branch"]:
                    continue
                try:
                    branch_scope = json.loads(self.blob(sha, STATE_PATH))
                    if any(
                        branch_scope.get(key) != scope.get(key)
                        for key in (
                            "repository",
                            "task_id",
                            "feature_branch",
                            "authorization_head_sha",
                        )
                    ):
                        raise ObserverError("Active branch disagrees with main task authority.")
                except (ObserverError, ValueError, TypeError, AttributeError) as exc:
                    ledger.scan_errors.append(f"{ref}: {exc}")
                    continue
            commits = [sha]
            previous = ledger.observed_refs.get(ref) or ledger.observed_refs.get("refs/heads/main")
            if previous and previous != sha:
                try:
                    self.ancestor(previous, sha)
                    commits = (
                        self.git("rev-list", "--reverse", f"{previous}..{sha}")
                        .decode()
                        .splitlines()
                    )
                except ObserverError as exc:
                    ledger.scan_errors.append(f"{ref}: remote ancestry changed: {exc}")
                    continue
            for commit in commits:
                try:
                    checkpoint = self.checkpoint(ref, commit)
                    if checkpoint:
                        checkpoints.append(checkpoint)
                except ObserverError as exc:
                    ledger.scan_errors.append(f"{ref}@{commit}: {exc}")
        ledger.observed_refs = refs
        for key, event in ledger.events.items():
            was_stale = event.stale
            event.stale = event.stale or refs.get(event.ref) != event.sha
            if event.stale and not was_stale:
                report = self.directory / "reports" / hashlib.sha256(key.encode()).hexdigest()
                for name in ("owner-update.md", "review.md"):
                    path = report / name
                    if path.exists():
                        atomic_write(
                            path,
                            (
                                "# Stale review\n\nThe remote version changed. "
                                "A new review is needed; the previous result applies "
                                "only to the older commit.\n\n" + path.read_text()
                            ),
                        )
        return checkpoints

    def bundle(self, checkpoint: Checkpoint, directory: Path) -> set[str]:
        sources: dict[str, str] = {}
        omitted: list[str] = []
        size = 0
        entries = self.git("ls-tree", "-rz", "--full-tree", checkpoint.sha)
        for entry in entries.rstrip(b"\0").split(b"\0"):
            metadata, raw_path = entry.split(b"\t", 1)
            mode, kind, object_id = metadata.decode().split()
            source_path = raw_path.decode("utf-8")
            path = PurePosixPath(source_path)
            if path.is_absolute() or ".." in path.parts:
                raise ObserverError("Unsafe source path in Git evidence.")
            if kind != "blob" or mode not in {"100644", "100755"}:
                omitted.append(source_path)
                continue
            content = self.git("cat-file", "blob", object_id)
            size += len(content)
            if size > MAX_EXPORT:
                raise ObserverError("Evidence export exceeds the 64 MiB bound.")
            if b"\0" in content:
                omitted.append(source_path)
                continue
            try:
                content.decode("utf-8")
            except UnicodeError:
                omitted.append(source_path)
                continue
            target = "evidence/" + source_path + ".txt"
            output = directory / target
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(content)
            sources[source_path] = target
        manifest = {
            "repository": REPOSITORY,
            "task_id": checkpoint.state["task_id"],
            "checkpoint_kind": checkpoint.kind,
            "reviewed_sha": checkpoint.sha,
            "ref": checkpoint.ref,
            "changed_paths": checkpoint.paths,
            "source_mapping": sources,
            "omitted_nontext_or_nonregular": omitted,
        }
        atomic_write(directory / "manifest.json", json.dumps(manifest, indent=2) + "\n")
        (directory / "implementation.diff.txt").write_bytes(
            self.git("diff", checkpoint.state["base_sha"], checkpoint.sha)
        )
        (directory / "publication-receipts.txt").write_bytes(
            self.git("log", "--format=%H%n%B", checkpoint.state["base_sha"] + ".." + checkpoint.sha)
        )
        atomic_write(directory / "REVIEW_CONTRACT.md", INSTRUCTIONS.read_text())
        return set(sources)

    def run_codex(self, bundle: Path, report: Path) -> dict[str, Any]:
        output = report / "model-output.json"
        output.unlink(missing_ok=True)
        command = [
            self.codex,
            "exec",
            "--sandbox",
            "read-only",
            "--skip-git-repo-check",
            "--ephemeral",
            "--json",
            "--cd",
            str(bundle),
            "--output-schema",
            str(SCHEMA),
            "--output-last-message",
            str(output),
            "Review the checkpoint under REVIEW_CONTRACT.md using manifest.json.",
        ]
        try:
            with (
                (report / "events.jsonl").open("w") as stdout,
                (report / "stderr.log").open("w") as stderr,
            ):
                process = subprocess.Popen(
                    command, stdout=stdout, stderr=stderr, start_new_session=True
                )
                try:
                    code = process.wait(timeout=self.timeout)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    raise ObserverError(
                        "Codex review timed out; explicit retry is required."
                    ) from None
                except BaseException:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.wait()
                    raise
            if code:
                raise ObserverError(f"Codex failed with exit {code}; see the local stderr log.")
            value: Any = json.loads(output.read_text())
            if not isinstance(value, dict):
                raise ValueError("Model result is not a JSON object")
            return value
        except (OSError, ValueError) as exc:
            raise ObserverError(f"Codex result unavailable or malformed: {exc}") from exc

    def validate_result(
        self, value: dict[str, Any], checkpoint: Checkpoint, source_paths: set[str]
    ) -> ReviewResult:
        try:
            if type(value.get("schema_version")) is not int:
                raise ValueError("Invalid result version type")
            result = ReviewResult.model_validate(value)
            for field, expected in (
                ("repository", REPOSITORY),
                ("task_id", checkpoint.state["task_id"]),
                ("checkpoint_kind", checkpoint.kind),
                ("reviewed_sha", checkpoint.sha),
            ):
                if getattr(result, field) != expected:
                    raise ValueError(f"Model identity mismatch: {field}")
            ids = [finding.id for finding in result.findings]
            if len(ids) != len(set(ids)):
                raise ValueError("Duplicate finding identifiers")
            if any(f.source_path not in source_paths for f in result.findings):
                raise ValueError("Finding references a path outside the evidence manifest")
            material = any(f.severity != "suggestion" for f in result.findings)
            decision = any(f.user_decision_required for f in result.findings)
            if result.verdict == "pass" and (material or decision):
                raise ValueError(
                    "A passing review cannot contain material or user-decision findings"
                )
            if decision and result.verdict not in {"needs_user", "blocked"}:
                raise ValueError("User-reserved findings must be escalated")
            return result
        except (ValueError, ValidationError) as exc:
            raise ObserverError(f"Rejected model review: {exc}") from exc

    def write_report(self, result: ReviewResult, report: Path, *, stale: bool) -> None:
        atomic_write(report / "result.json", result.model_dump_json(indent=2) + "\n")
        heading = (
            "STALE — the remote head changed" if stale else "Advisory review — not merge approval"
        )
        details = [f"# {heading}", "", result.summary, "", f"Verdict: {result.verdict}", ""]
        for finding in result.findings:
            details.extend(
                [
                    f"## {finding.id}: {finding.severity}",
                    "",
                    f"Evidence: {finding.source_path}:{finding.line or 'unspecified'}",
                    "",
                    f"Requirement: {finding.requirement}",
                    "",
                    finding.observation,
                    "",
                    f"Impact: {finding.impact}",
                    "",
                    f"Recommendation: {finding.proposed_correction}",
                    "",
                    f"Acceptance evidence: {finding.acceptance_evidence}",
                    "",
                ]
            )
        details.extend(["## Limitations", "", *[f"- {item}" for item in result.limitations], ""])
        atomic_write(report / "review.md", "\n".join(details))
        owner = result.owner_update
        lines = ["# Your MIP update", "", heading, "", result.summary, "", owner.goal_impact, ""]
        for title, values in (
            ("Completed", owner.completed),
            ("Underway", owner.ongoing),
            ("Planned", owner.planned),
            ("Issues being discussed", owner.issues),
            ("Your decisions", owner.decisions_needed),
        ):
            lines.extend(
                [f"## {title}", "", *([f"- {v}" for v in values] or ["None reported."]), ""]
            )
        lines.extend(
            [
                "## My recommendation",
                "",
                owner.recommendation,
                "",
                "[Detailed review](review.md) · [Evidence and limitations](result.json)",
                "",
            ]
        )
        atomic_write(report / "owner-update.md", "\n".join(lines))

    def review(self, checkpoint: Checkpoint, ledger: Ledger) -> int:
        key = checkpoint.key
        report = self.directory / "reports" / hashlib.sha256(key.encode()).hexdigest()
        report.mkdir(parents=True, exist_ok=True)
        event = Event(
            ref=checkpoint.ref,
            task_id=checkpoint.state["task_id"],
            kind=checkpoint.kind,
            sha=checkpoint.sha,
            status="running",
            updated_at=now(),
            report=str(report),
            error=None,
            verdict=None,
            stale=False,
        )
        ledger.events[key] = event
        self.save(ledger)
        try:
            with tempfile.TemporaryDirectory(prefix="mip-review-") as temporary:
                directory = Path(temporary)
                sources = self.bundle(checkpoint, directory)
                result = self.validate_result(
                    self.run_codex(directory, report), checkpoint, sources
                )
            refs = self.fetch()
            event.stale = refs.get(checkpoint.ref) != checkpoint.sha
            self.write_report(result, report, stale=event.stale)
            event.status = "completed"
            event.verdict = result.verdict
            code = (
                3
                if event.stale or result.verdict == "blocked"
                else (0 if result.verdict == "pass" else 2)
            )
        except (ObserverError, OSError, ValueError) as exc:
            event.status = "blocked"
            event.error = str(exc)
            event.verdict = "blocked"
            atomic_write(
                report / "owner-update.md",
                (
                    "# Your MIP update\n\nReview could not be completed.\n\n"
                    "No conclusion about implementation quality or merge readiness "
                    "is available.\n\n"
                    "Next: resolve the review failure and explicitly retry this checkpoint.\n\n"
                    "[Technical reason](error.txt)\n"
                ),
            )
            atomic_write(report / "error.txt", str(exc) + "\n")
            code = 3
        event.updated_at = now()
        self.save(ledger)
        print(
            f"{event.verdict}: {event.task_id} at {event.sha}\n"
            f"Owner update: {report / 'owner-update.md'}"
        )
        return 3 if ledger.scan_errors and code == 0 else code

    def execute(self, command: str, ref: str | None = None) -> int:
        with self.lock():
            if command == "status":
                ledger = self.load()
                self.save(ledger)
                print(ledger.model_dump_json(indent=2))
                return (
                    3
                    if ledger.scan_errors
                    or any(e.status == "blocked" or e.stale for e in ledger.events.values())
                    else 0
                )
            if command == "scan":
                ledger = self.load()
                try:
                    refs = self.fetch()
                except ObserverError as exc:
                    ledger.scan_errors = [f"Remote scan unavailable: {exc}"]
                    self.save(ledger)
                    print("Review blocked: remote evidence could not be refreshed.")
                    return 3
            else:
                refs = self.fetch()
            if command == "init":
                if self.ledger_path.exists():
                    raise ObserverError(
                        "Ledger already exists; init will not erase review history."
                    )
                ledger = Ledger(
                    schema_version=1,
                    initialized_at=now(),
                    baseline=[],
                    observed_refs=refs,
                    events={},
                    scan_errors=[],
                )
                ledger.baseline = [c.key for c in self.candidates(refs, ledger)]
                self.save(ledger)
                print(f"Initialized; {len(ledger.baseline)} existing checkpoints skipped.")
                return 3 if ledger.scan_errors else 0
            if command == "review" and not self.ledger_path.exists():
                ledger = Ledger(
                    schema_version=1,
                    initialized_at=now(),
                    baseline=[],
                    observed_refs=refs,
                    events={},
                    scan_errors=[],
                )
            else:
                ledger = self.load()
            if command == "review":
                if not ref or ref.startswith("-"):
                    raise ObserverError("Provide an explicit safe Git ref or full SHA.")
                sha = self.git("rev-parse", "--verify", ref + "^{commit}").decode().strip()
                state = json.loads(self.blob(sha, STATE_PATH))
                if not isinstance(state, dict):
                    raise ObserverError("Explicit checkpoint state is not an object.")
                inferred = (
                    "refs/heads/main"
                    if state.get("status") == "merged"
                    else ("refs/heads/" + str(state.get("feature_branch", "")))
                )
                checkpoint = self.checkpoint(inferred, sha)
                if checkpoint is None:
                    raise ObserverError("Explicit ref is not an eligible checkpoint.")
                return self.review(checkpoint, ledger)
            checkpoints = self.candidates(refs, ledger)
            for checkpoint in checkpoints:
                if checkpoint.key not in ledger.baseline and checkpoint.key not in ledger.events:
                    ledger.events[checkpoint.key] = Event(
                        ref=checkpoint.ref,
                        task_id=checkpoint.state["task_id"],
                        kind=checkpoint.kind,
                        sha=checkpoint.sha,
                        status="pending",
                        updated_at=now(),
                        report=None,
                        error=None,
                        verdict=None,
                        stale=False,
                    )
            self.save(ledger)
            for event in list(ledger.events.values()):
                if event.status == "pending":
                    checkpoint = self.checkpoint(event.ref, event.sha)
                    if checkpoint is None:
                        raise ObserverError("Queued checkpoint lost its eligibility.")
                    return self.review(checkpoint, ledger)
            print(
                "No new checkpoint to review."
                if not ledger.scan_errors
                else ("Review blocked: " + "; ".join(ledger.scan_errors))
            )
            return (
                3
                if ledger.scan_errors
                or any(e.status == "blocked" or e.stale for e in ledger.events.values())
                else 0
            )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--timeout", type=float, default=900)
    parser.add_argument("--interval", type=float, default=30)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "scan", "watch", "status"):
        commands.add_parser(command)
    commands.add_parser("review").add_argument("--ref", required=True)
    args = parser.parse_args(argv)
    try:
        if args.interval <= 0:
            raise ObserverError("Watch interval must be positive.")
        observer = Observer(args.repository, codex=args.codex, timeout=args.timeout)
        while True:
            code = observer.execute(
                "scan" if args.command == "watch" else args.command, getattr(args, "ref", None)
            )
            if args.command != "watch":
                return code
            time.sleep(args.interval)
    except KeyboardInterrupt:
        return 0
    except (ObserverError, OSError, ValueError, TaskControlError) as exc:
        print(f"Review observer blocked: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
