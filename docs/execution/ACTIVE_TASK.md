# Active Task

**Status:** authorized
**Owner:** MIP program governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `MIP_COORDINATION_POST_MERGE_CLOSURE_RECONCILIATION_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `main` / `3520176126d129e9288a9ce37591299ec856650a`
- **Feature branch:** `docs/mip-coordination-post-merge-closure-reconciliation-001`
- **Execution mode:** `branch_and_fast_forward`
- **Prior task:** `MIP_CROSS_REPOSITORY_COORDINATION_CONTROL_PLANE_001`
- **Approved prior review head / merged implementation head:** `cc1904db8e18b5ba461cca2da738026acadfb43c`
- **Prior correction implementation:** `4c93a7c300b3471ffee2a11ff449094e82a1f11d`
- **Prior closure commit:** `3520176126d129e9288a9ce37591299ec856650a`
- **MMM main observed:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **GeoX main observed:** `ee9673c13e69082367c1727568946ac4c1a01015`
- **Capability authorizations changed:** `false`

## Purpose

Reconcile the MIP repository's stable execution and coordination records after
the prior coordination-control-plane task was fast-forwarded and closed. The
prior implementation is accepted and remains merged. This task corrects only
post-merge governance evidence that still presents review-era or pre-merge state
as current.

This task does not reopen or replace the coordination protocol implementation.
It does not modify MMM or GeoX, and it does not repair GeoX
`tests/test_repo_native_execution_handoff.py`; that is an owner-repository issue
outside MIP authority.

## Starting evidence

Live Git at authorization shows:

- MIP `main` at closure `3520176126d129e9288a9ce37591299ec856650a`;
- the approved exact head `cc1904db8e18b5ba461cca2da738026acadfb43c`
  is the parent merged implementation lineage;
- the completed remote MIP feature branch is absent;
- MMM remains merged at `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`;
- GeoX remains independently authorized at
  `ee9673c13e69082367c1727568946ac4c1a01015` for
  `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001`;
- no sibling capability or consumer verification has changed.

The prior closure currently contains contradictory current-state evidence:
`LATEST_COMPLETION_REPORT.md` still says `ready_for_review` and names the old
pre-merge MIP main as current; `ACTIVE_TASK.md` retains obsolete correction
instructions; `EXECUTION_STATE.json` retains review-era decision/checkpoint
fields; the coordination snapshot and canonical program files still describe
the prior MIP task as authorized or in progress; and focused tests do not enforce
post-merge consistency.

## Authorized result

Produce a narrow post-merge reconciliation that:

1. makes the three stable execution files agree that the prior coordination task
   is merged and closed;
2. distinguishes the approved review head, merged implementation head, closure
   commit, current synchronized main, and this new task's authorization lineage;
3. records remote feature-branch deletion as GitHub-observed evidence and does
   not claim unverified local cleanup;
4. removes obsolete instructions to resume, correct, review, or merge the prior
   task from current stable state;
5. transitions the MIP repository entry and `WS-MIP-COORDINATION-001` in the
   coordination snapshot to merged historical state at the verified prior
   closure, while preserving deterministic live-overlay behavior;
6. appends the corrected implementation, approval, fast-forward merge, closure,
   and post-merge reconciliation events to coordination history without
   rewriting prior events;
7. updates program current state, repository checkpoints, and next execution
   sequence so the completed coordination task is not still listed as pending;
8. records that MMM and GeoX protocol adoption remain proposed and independently
   owner-authorized, and that the existing GeoX builder may continue without a
   retroactive MIP dependency;
9. adds focused tests that fail on mixed `merged`/`ready_for_review` state, stale
   current MIP evidence, missing closure history, obsolete resume instructions,
   unobserved-cleanup claims, or an `in_progress` MIP coordination workstream
   after live merged closure; and
10. preserves all runtime, integration, real-data, recommendation, optimization,
    pilot, production, and package-side-agent freezes.

## Owned files

Execution may modify only:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`
- `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json`
- `docs/program/CROSS_REPOSITORY_COORDINATION_HISTORY.md`
- `docs/program/PROGRAM_CURRENT_STATE.md`
- `docs/program/REPOSITORY_CHECKPOINTS.md`
- `docs/program/NEXT_EXECUTION_SEQUENCE.md`
- `tests/test_cross_repository_coordination_control_plane.py`

No MIP runtime, contract, adapter, fixture, orchestration, UI, analytical, or
other test path is owned. No MMM or GeoX path is owned.

## Non-overlap and sequencing

- The prior MIP coordination task is merged and cannot be resumed.
- The active-task context resolver is not part of this task. After this task is
  merged and closed, `MIP_ACTIVE_TASK_CONTEXT_RESOLVER_001` may be considered
  for separate authorization.
- MMM and GeoX protocol/resolver adoption remain separate owner-repository tasks.
- GeoX's authorized builder task remains canonical and is not blocked, renamed,
  split, or modified by this MIP task.
- The stale GeoX repository-context/test mismatch is not repaired here and must
  not be used to expand MIP scope.

## Validation gate

Run on the exact implementation tree:

- focused coordination-control-plane and execution/documentation tests;
- JSON parsing and Markdown/path consistency checks;
- exact changed-path verification;
- Ruff and configured mypy for changed Python files;
- `git diff --check`;
- Docker-backed full `make validate`.

Publish `blocked` with exact evidence if the complete authored gate cannot finish
successfully. Focused success does not hide full-suite debt.

## Acceptance criteria

- Stable execution files agree on current task status and prior merged closure.
- The prior completion report no longer describes the current decision as
  `ready_for_review`.
- Current GitHub-observed MIP evidence distinguishes prior closure
  `3520176126d129e9288a9ce37591299ec856650a` from this task's later
  authorization/implementation heads.
- Remote branch cleanup is recorded as observed; local cleanup is not claimed
  without evidence.
- Obsolete prior-task resume/correction instructions are absent from current
  stable task state.
- The coordination snapshot represents the prior MIP coordination workstream as
  merged, not authorized or in progress, while retaining stale-snapshot overlay
  rules.
- Canonical current-state, checkpoint, sequence, and history files reflect the
  prior merge and closure.
- Tests enforce these post-merge invariants.
- MMM and GeoX remain unmodified and authoritative for their own work.
- All capability authority flags remain false or blocked.

## State transitions

On success, publish `ready_for_review` with one implementation SHA, empty
blockers, `task_execution_authorized: true`, `merge_authorized: false`, null
reviewed/approval SHAs, unchanged capability authority, exact validation counts,
and the exact remote feature-branch head observed externally after push.

On failure, publish an accurate `blocked` state with specific blockers and exact
validation evidence, commit and push the branch, and stop.

Do not create a pull request, merge, squash, rebase, force-push, delete branches,
or modify sibling repositories during execution.

## Prohibited authority

This task does not authorize live MMM/GeoX integration, customer data, uploads,
persistence, jobs, simulation runtime, optimization, recommendations, treatment
assignment, LLM decisioning, pilot, production, or package-side agents.
