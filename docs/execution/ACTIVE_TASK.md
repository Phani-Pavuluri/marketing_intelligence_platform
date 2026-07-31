# Active Task

**Status:** changes_requested
**Owner:** MIP program governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `MIP_ACTIVE_TASK_CONTEXT_RESOLVER_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `d35fbbb82711b073c3504d5cc0f1b807e9b36c81`
- **Authorization head:** `221b0dedc73432a9b04d331c2544fe807b8f1013`
- **Synchronized state-only head:** `11c062eb785b3518d531992aa554d0a3a4c0b84b`
- **Feature branch:** `feat/mip-active-task-context-resolver-001`
- **Rejected implementation:** `18f7ffdd5b3ef20af4cea177047c11f5ffadd8f0`
- **Rejected exact review head:** `abf57a6fb0c08d23fb51c56a5ea744445b3ab82c`
- **Observed MMM main:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Observed GeoX main:** `ee9673c13e69082367c1727568946ac4c1a01015`
- **Capability authorizations changed:** `false`

## Review decision

The exact remote head `abf57a6fb0c08d23fb51c56a5ea744445b3ab82c`
is not approved. The resolver direction and implementation identity are useful,
but the candidate violates the authorized path boundary and does not satisfy all
required fail-closed semantics or the minimum test matrix.

Correction execution is not authorized yet because one required correction
needs an explicit scope amendment. Do not modify the branch until the user
authorizes adding the named path below to this task.

## Authority blocker: owned-path amendment required

The authorized implementation boundary contains exactly these nine paths:

- `AGENTS.md`
- `Makefile`
- `scripts/resolve_active_task.py`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`
- `tests/test_active_task_context_resolver.py`

The rejected implementation also modifies:

- `tests/test_cross_repository_coordination_control_plane.py`

That tenth path is outside the authorized boundary. Its change is substantively
related because the existing test hard-couples repository governance to a prior
current task, but this relationship does not retroactively grant authority.
Explicit user authorization is required before this path may become correction-
owned. Reverting it without a scope amendment is expected to restore the old
state-coupled full-suite failure; if that occurs, publish `blocked` rather than
hiding the debt.

## Required technical corrections after scope authorization

### 1. Validate human views for every lifecycle state

The resolver currently returns immediately for `idle`, `proposed`, `merged`, and
`superseded`, before validating `ACTIVE_TASK.md` and
`LATEST_COMPLETION_REPORT.md`. This fails the task's primary closure-consistency
requirement. Validate the synchronized-main human views before every
non-executable return, including merged closure state. Detect duplicate or
contradictory current status/decision declarations in both files while ignoring
explicitly historical evidence.

### 2. Enforce complete schema, authority, and lifecycle agreement

Validate the exact supported execution-state schema and all required booleans,
including `pr_creation_authorized`. Require a valid authorization-head SHA for
every state that needs a feature branch. Replace unchecked key access with
reason-coded fail-closed errors.

Define and enforce allowed main-pointer to branch-state transitions. Branch
agreement must cover repository, task ID, feature branch, authorization head,
base identity, and all authority fields that must remain invariant. A branch may
never set merge or PR authority when the main pointer does not authorize it.

### 3. Support the real branch-only correction model

`origin/main` remains the stable task-and-branch pointer after authorization;
mutable `blocked`, `changes_requested`, and `ready_for_review` state lives on the
feature branch. The current test places `changes_requested` on main and therefore
does not represent actual review correction flow. Support a main pointer that
remains `authorized` while the exact feature branch records
`changes_requested` with explicit correction authorization. Preserve fail-closed
checks without requiring mutable branch correction authority to equal stale main
review metadata.

### 4. Complete the minimum semantic test matrix

Add deterministic temporary-Git tests for every required case, including:

- dirty tracked worktree;
- stale and diverged local main;
- repository identity mismatch separate from wrong origin;
- branch authority mismatch, including merge and PR flags;
- invalid or missing authorization head without uncaught exceptions;
- allowed and disallowed main-to-branch lifecycle transitions;
- realistic branch-only `changes_requested` resumption;
- duplicate current decision in the completion report;
- contradictory merged closure prose on synchronized main;
- `idle`, `proposed`, and `superseded` non-executable behavior;
- existing local feature branch whose head differs from the remote head.

The tests must prove that context-index task text is not authority and must not
require the current task ID to appear in the context index.

### 5. Scope and publication

After explicit scope authorization, correct only the ten resolver-governance
paths. Keep MMM, GeoX, program coordination files, product code, analytical code,
runtime, contracts, adapters, fixtures, orchestration, and UI unchanged.

Rerun the complete authored validation gate, including Docker-backed
`make validate`, exact changed-path verification, focused temporary-Git tests,
JSON and Markdown consistency, Ruff, mypy, and `git diff --check`. Publish one
new final implementation-tree SHA and one new exact remote review head as
`ready_for_review`, or publish an accurate `blocked` state.

Do not create a PR, merge, rebase, squash, force-push, delete branches, modify
siblings, authorize sibling adoption, or change capability authority.
