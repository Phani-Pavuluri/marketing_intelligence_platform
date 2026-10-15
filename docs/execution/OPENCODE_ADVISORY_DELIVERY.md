# OpenCode Advisory Delivery

Advisory transport for delivering an already completed MIP checkpoint review
to one explicitly verified Muse-Spark session. Muse-Spark owns all
implementation choices. Codex provides independent review and high-level
guidance only.

## Commands

From an installed MIP environment:

```sh
python -m mip.execution.opencode_advisory --repository /path/to/MIP bind \
  --session SES_ID --implementation-directory /path/to/implementation
python -m mip.execution.opencode_advisory --repository /path/to/MIP send \
  --event-key TASK_ID:completion:SHA
python -m mip.execution.opencode_advisory --repository /path/to/MIP status
```

`bind` verifies both supplied repositories identify the canonical MIP origin
and reads OpenCode `session.get` for the exact session ID. It requires the
expected implementation directory, provider `opencode`, model
`muse-spark-1.3-contributor-free`, `high` variant, and `build` agent, then
persists a strict version-1 binding under `.codex/opencode-advisory/`. No
title lookup, session creation, or model switch is performed.

`send` admits one advisory for a completed, non-stale `completion` event in
the existing `.codex/review-observer/ledger.json`. Closure events are
ineligible. It reuses the existing Ledger, Event, and ReviewResult validation,
matches event and result repository, task, kind, SHA, and verdict, verifies
the checkpoint through the observer's read-only checks, re-reads session
metadata, reserves the delivery atomically, and calls OpenCode
`session.prompt` with structured text and `resume:false`. Identical repeats
make no API mutation. Everything under `.codex/` is local-only and never
committed.

`status` reports the persisted binding and delivery states.

## Boundaries

- Advisory evidence only. Git owns authorized scope; Muse-Spark owns
  implementation choices. No implementation command, correction
  authorization, merge approval, or pause/release control is introduced.
- Findings marked `user_decision_required` remain explicitly pending owner
  input; agent agreement cannot resolve them. Pass feedback is advisory only.
- A running session receives advisory input at its normal delivery boundary;
  an idle session stays idle. Admission is not proof the session read,
  agreed, or implemented any finding.
- The adapter never runs scan, review, or model inference, never mutates Git
  worktrees or branches, and never writes sibling repositories.
- The binding records the separately observed implementation directory; it is
  not required to equal the review checkout path. A later send from a
  separate checkout of the same canonical repository is permitted when its
  origin matches the bound canonical origin.

## Failure semantics

- Exit 0: bind, admission, already-admitted, or status success.
- Exit 2: identity, evidence, or stale ineligibility (wrong origin,
  directory, project, model, agent, or session; incomplete, mismatched,
  malformed, closure, or stale review evidence).
- Exit 3: transport, state, or indeterminate failure (OpenCode unavailable,
  corrupt binding or journal, competing writer, timeout, crash, or invalid
  acknowledgment).

Timeout, crash, or invalid acknowledgment after reservation is indeterminate
and never automatically resent. `status` exposes the uncertainty for
reconciliation. Corrupt local state fails closed without erasure. Concurrent
writers are serialized; a held lock fails closed. Advisory text is bounded
to 12000 characters. Errors use stable codes and carry no secrets.

## Validation

Focused gate:

```sh
poetry run pytest -q tests/test_opencode_advisory.py tests/test_review_observer.py
poetry run python -m mip.execution.taskctl check
```

Full gate adds native Docker `make validate`, JSON parsing,
`git diff --check`, and exact owned-path, ancestry, and authority checks.
Tests use isolated Git and observer fixtures with fake transports, never real
implementation sessions as synthetic targets. The full existing observer
suite is preserved.
