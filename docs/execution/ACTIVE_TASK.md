# Active Task

**Status:** changes_requested
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_P2_ROADMAP_AND_COORDINATION_RECONCILIATION_AFTER_GEOX_SUPERSESSION_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `369805d923454a51ce98845cea29bdb1ee3c3895`
- **Feature branch:** `docs/mip-p2-roadmap-coordination-reconciliation-after-geox-supersession-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 3 — cross-repository coordination and dependency-state governance
- **Starting MMM checkpoint:** `Phani-Pavuluri/MMM@b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`
- **Starting GeoX checkpoint:** `Phani-Pavuluri/panel_exp@a4bf6bfaa4311dacd3642d289dca3917543e0309`
- **Coordination workstream:** `WS-MIP-P2-ROADMAP-RECONCILIATION-001`
- **Capability owner:** MIP program governance
- **Capability authorizations changed:** `false`

## Primary mergeable outcome

Reconcile MIP's current P2 roadmap, repository checkpoints, execution sequence,
and cross-repository coordination ledger with live Git after:

1. the oversized GeoX governed-readout builder task was superseded without merge;
2. GeoX authorized its lean repository-delivery adoption task;
3. MMM authorized its repository-execution-protocol adoption task; and
4. MIP completed the invocation-only and terminal-outcome execution standard.

The outcome is one current, internally consistent, stale-failing program snapshot
that names the actual critical path and dependency conditions without changing
the canonical P0–P8 lifecycle or authorizing product/runtime work.

## Why this task cannot be split further

The program-current-state narrative, repository checkpoint inventory, ordered
execution sequence, coordination JSON ledger, append-only coordination history,
roadmap execution-current-state section, stable context navigation, and semantic
coordination test describe one shared dependency graph. Updating only a subset
would knowingly preserve contradictory task identities, pins, blockers, or next
steps. No product contract, runtime, analytical implementation, or canonical
roadmap redesign is included.

## Live orientation and ownership findings

Connected GitHub established the following starting state:

- MIP `main` is `369805d923454a51ce98845cea29bdb1ee3c3895`; the prior terminal-outcome task is merged and closed, with all execution, merge, PR, and capability authority false.
- MMM `main` is `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`; `MMM_REPOSITORY_EXECUTION_PROTOCOL_ADOPTION_001` is authorized on `docs/mmm-repository-execution-protocol-adoption-001`. Its earlier proposed coordination-protocol task is absorbed, not duplicated.
- GeoX `main` is `a4bf6bfaa4311dacd3642d289dca3917543e0309`; `GEOX_LEAN_REPOSITORY_DELIVERY_STANDARD_ADOPTION_001` is authorized on `docs/geox-lean-repository-delivery-standard-adoption-001`.
- `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001` is superseded without merge. Its preserved branch and partial commits do not satisfy any producer or consumer dependency.

### Stale MIP resolver disposition

The remote branch `feat/mip-active-task-context-resolver-001` is preserved at
`b96dfc4365d5aadf9425d31aa576664f58270fa5`. It is 13 commits ahead and 72
commits behind current MIP `main`, with merge base
`11c062eb785b3518d531992aa554d0a3a4c0b84b`. Its durable branch state is
`blocked`, with correction execution previously authorized and implementation
commit `785d83f25891274a42a5a82efbd17103563c29a7`.

That branch cannot be fast-forward merged into current `main`; rebasing,
wholesale cherry-picking, force-updating, or concurrently resuming it would
violate the current workflow and overlap this task's execution and coordination
test surfaces. This authorization therefore **supersedes
`MIP_ACTIVE_TASK_CONTEXT_RESOLVER_001` without merge**. The branch remains
historical partial evidence only. Do not resume, merge, rebase, create a PR from,
or reuse it wholesale. A future resolver task may reuse a specifically reviewed
hunk only from current `main`, within a separately authorized definition-ready
successor and independent validation.

Resolver reauthoring is deferred and unauthorized. It does not unblock P2 and
must not compete with this reconciliation.

## Exact observable behavior

### 1. Reverify live state at execution and publication

Before modifying files and again before the exact-tree receipt, fetch live
`main` for MIP, MMM, and GeoX and read each repository's `AGENTS.md`,
`EXECUTION_STATE.json`, `ACTIVE_TASK.md`, `REPOSITORY_CONTEXT_INDEX.md`, and
`LATEST_COMPLETION_REPORT.md`.

The starting sibling SHAs above are orientation evidence, not immutable final
pins. If a sibling main moves, apply the coordination protocol's live overlay and
record the exact final main, task, status, branch/closure evidence, validation
debt, and authority. Never combine an older SHA with a newer task status.

Stop with Git-durable `blocked` if a live repository, task identity, ownership,
dependency, authorization boundary, or exact evidence cannot be verified.

### 2. Preserve the canonical lifecycle

`docs/roadmap/ROADMAP.md` remains unchanged. P0–P8 remains the primary product
lifecycle and R0–R6 remain mandatory cross-cutting gates.

Update only stale current-state and near-term sequence text. Remove or clearly
classify obsolete statements such as `Current main: 000273a`, the old
"immediate next phase," and the single active GeoX builder sequence. Historical
implementation inventories may remain when clearly labeled historical and may
not authorize execution.

### 3. Record sibling protocol-adoption work accurately

The program snapshot must record the live MMM and GeoX protocol-adoption tasks
using their exact owner-repository task IDs, states, branches or merged closure
SHAs, and final observed mains.

- MMM's absorbed `MMM_CROSS_REPOSITORY_COORDINATION_PROTOCOL_ADOPTION_001` must not remain a separately executable workstream.
- GeoX's prior proposed coordination-protocol adoption must be represented by the broader owner-authorized lean-delivery adoption task, without inventing MIP authority.
- Authorization, implementation, validation, approval, merge, and closure remain distinct.

### 4. Reconcile the superseded GeoX producer work

Record `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001` and
`WS-GEOX-READOUT-BUILDER-001` as superseded without merge. Preserve exact
historical branch/partial evidence where useful, but remove them from active and
ordered execution.

Do not mark either existing GeoX P2 blocker resolved. Replace the former single
builder step with the owner-repository successor sequence declared by current
GeoX Git:

1. governed-readout temporal lifecycle contract;
2. typed producer builder;
3. certified fixture generation, hashes, and replay semantics; and
4. optional envelope plus final handoff/integration validation.

Represent these as proposed GeoX-owned outcomes/workstreams unless live GeoX Git
has separately authorized or merged a specific successor by execution time. MIP
must not invent task IDs or authorize those successors.

### 5. Keep MMM normalization fail-closed

`MMM_GEOX_READOUT_NORMALIZATION_AND_CROSS_REPOSITORY_FIXTURES_001` remains
proposed and unauthorized unless live MMM Git says otherwise. Its dependency
must require the exact merged GeoX producer sequence needed by its contract,
full required producer validation, and declared MMM consumer verification.

An authorized, blocked, review-ready, or superseded GeoX branch does not satisfy
that dependency. Producer completion alone does not resolve MMM or MIP consumer
blockers.

### 6. Keep the MIP P2 journey fail-closed

`MIP_P2_FIXTURE_ONLY_PLANNING_EVIDENCE_JOURNEY_001` remains proposed and
unauthorized. It requires:

- exact merged GeoX producer evidence and required consumer verification;
- exact merged MMM normalization and certified cross-repository fixture evidence;
- declared MIP consumer verification; and
- the D6 release/compatibility evidence transition.

The reconciliation task itself does not implement fixtures, package calls,
planning evidence, LLM behavior, resolver runtime, or D6 runtime certification.

### 7. Reconcile blocker and workstream semantics

The coordination JSON must:

- use unique workstream IDs and capability owners;
- preserve old IDs as superseded where downstream references exist rather than silently deleting history;
- give every active dependency a live resolution condition;
- distinguish `authorized`, `blocked`, `ready_for_review`, `merged`, `superseded`, and `producer_completed_pending_consumer_verification`;
- prevent a feature branch from satisfying a merged dependency;
- preserve the original P2 GeoX blocker IDs as open unless their exact criteria are live-verified as resolved;
- record the stale resolver task as superseded MIP-only historical work, not a P2 dependency; and
- preserve all authority freezes.

### 8. Update stable navigation and semantic tests

`REPOSITORY_CONTEXT_INDEX.md` must remain navigation-only and remove stale
verification pins or mutable task mirroring. Current task selection comes from
stable execution files and exact feature-branch state when applicable.

Update `tests/test_cross_repository_coordination_control_plane.py` from a
historical identity snapshot to semantic current-state assertions. It must not
hard-code an obsolete MIP execution task or require the superseded GeoX builder
to be active.

## Owned paths

Execution may modify only:

1. `docs/program/PROGRAM_CURRENT_STATE.md`
2. `docs/program/REPOSITORY_CHECKPOINTS.md`
3. `docs/program/NEXT_EXECUTION_SEQUENCE.md`
4. `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json`
5. `docs/program/CROSS_REPOSITORY_COORDINATION_HISTORY.md`
6. `docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md`
7. `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
8. `tests/test_cross_repository_coordination_control_plane.py`
9. `docs/execution/ACTIVE_TASK.md`
10. `docs/execution/EXECUTION_STATE.json`
11. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify any other path.

## Prohibited scope and paths

Do not modify:

- `docs/roadmap/ROADMAP.md` or the P0–P8/R0–R6 lifecycle;
- `AGENTS.md`, `docs/execution/TASK_EXECUTION_STANDARD.md`, or the merged lean standard;
- `scripts/resolve_active_task.py`, `Makefile`, resolver tests, or the preserved stale resolver branch;
- MIP product/runtime/contract/adapter/fixture/orchestration/LLM/UI code;
- MMM or GeoX repositories, branches, contracts, fixtures, tests, or analytical truth;
- capability/environment matrices except to cite their unchanged freezes; or
- release, security, real-data, pilot, or production authority.

Do not create a PR, merge, squash, rebase, force-push, delete preserved historical
branches, or modify sibling task state.

## Named acceptance evidence

Update `tests/test_cross_repository_coordination_control_plane.py` with separate
semantic assertions covering:

1. `test_live_repository_pins_and_protocol_adoption_states_are_coherent` — committed repository observations, task IDs, statuses, and evidence paths agree across coordination JSON and program Markdown.
2. `test_geox_builder_supersession_and_successor_sequence_are_fail_closed` — the old builder is superseded, no producer blocker is resolved, the four successor outcomes are owner-repository work, and no feature branch satisfies completion.
3. `test_mmm_normalization_and_mip_p2_dependencies_require_consumer_verification` — MMM and MIP remain blocked on exact merged evidence plus declared consumer verification.
4. `test_roadmap_execution_sequence_preserves_p0_p8_and_removes_stale_current_state` — canonical roadmap is referenced and unchanged while obsolete current-main/next-phase text and the single-builder sequence are removed or historical.
5. `test_stale_mip_resolver_is_superseded_without_merge_authority` — exact preserved branch/implementation evidence is recorded, correction execution is no longer active, and no resolver code is owned by this task.
6. `test_coordination_authority_freezes_remain_false` — runtime integration, recommendations, optimization, real data, pilot, production, package-side agents, and capability changes remain blocked/false.
7. `test_coordination_test_is_current_state_semantic_not_task_identity_coupled` — the test no longer hard-codes an obsolete execution task or stale historical pin as the only valid current state.

Equivalent names are acceptable only if all seven semantic groups remain
separate and explicit.

## Validation gate

This is Tier 3 because it changes cross-repository dependency and blocker
representation. Run on the frozen exact task-owned tree during execution,
exact-head review, and after fast-forward:

- parse `docs/execution/EXECUTION_STATE.json` and `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json` as JSON;
- verify Markdown/current-state consistency and exact final repository pins;
- prove the task-authoring boundary and immediate state-only authorization boundary;
- verify exact changed paths against the eleven owned paths;
- run `git diff --check`;
- run `pytest -q tests/test_cross_repository_coordination_control_plane.py`;
- run `pytest -q tests/governance/test_repo_native_execution_handoff.py`;
- run Ruff and configured mypy for the changed Python test;
- run Docker-backed `make validate` and record exact passed/failed/skipped/warning counts;
- inspect the final exact-tree validation-receipt trailers; and
- prove local/remote feature-branch head equality after push.

Do not narrow the gate or reuse old validation. If Docker, live sibling
verification, required history, or any required validation cannot complete,
publish accurate Git-durable `blocked` state with exact diagnostics and a live
resolution condition.

## Task-authoring and authorization boundaries

- Pre-authoring base: `369805d923454a51ce98845cea29bdb1ee3c3895`.
- The task-authoring range may change only `docs/execution/ACTIVE_TASK.md` and `docs/execution/LATEST_COMPLETION_REPORT.md`.
- The task-authoring commit becomes the `authorization_head_sha` recorded by the immediate next commit.
- The immediate next commit is state-only and may change only `docs/execution/EXECUTION_STATE.json`.
- Create the exact feature branch from the synchronized state-only `main` head.
- No other commit or path may occur between these boundaries.

## Deferred successors

- GeoX protocol adoption and its four producer successors remain GeoX-owned.
- MMM protocol adoption and later GeoX-readout normalization/fixtures remain MMM-owned.
- `MIP_ACTIVE_TASK_CONTEXT_RESOLVER_REAUTHORING_001` is deferred and unauthorized; any future task must start from current main and use a small independent merge unit.
- `MIP_P2_FIXTURE_ONLY_PLANNING_EVIDENCE_JOURNEY_001` remains proposed and unauthorized until all declared dependencies and consumer verification are satisfied.
- D6 fixture-only dry-run and live package integration remain separately authorized future work.

## Failure and terminal semantics

After successful orientation and a safe branch are verified, continue without
another user prompt until publishing either:

- `ready_for_review` with one implementation SHA, empty blockers, exact-tree receipt, execution authorization true, merge/PR false, null reviewed/approval SHAs, and unchanged capability authority; or
- Git-durable `blocked` with exact blocker, attempted evidence, validation-category dispositions, and live resolution condition.

Incomplete implementation or stale evidence is not success. Do not leave the
current decision only in chat or terminal output.

**Unresolved execution-blocking design questions: none.**

## Publication result

- **Rejected exact review head:** `1f2783fbb490673b9aaf82f74fe5923df5d2e97f`
- **Implementation at rejected head:** `c4a849b00cc8f0c954b6c3ffcc56b914a4ee0614`
- **Review state:** `changes_requested`
- **Correction execution:** authorized on this exact branch
- **Merge and PR authority:** false
- **Capability authority:** unchanged

## Required correction

The rejected publication is directionally correct but not current enough for
approval.

1. The receipt at `2026-08-04T00:44:25Z` records GeoX main
   `f15b0ee1713eaa46b7dc55e597e713443f5a8d32` and
   `GEOX_EXECUTION_BRANCH_BINDING_001` as proposed. GeoX main had already moved at
   `2026-08-04T00:42:08Z` to
   `d17bb81c9dbc67f773fd71068c26b14c92989f42`, where that task is authorized at
   authorization head `dc68853e87a65a494c942b3fe2794e321a22b036` on
   `feat/geox-execution-branch-binding-001`.
2. The rejected coordination JSON records the GeoX repository entry as
   `GEOX_LEAN_REPOSITORY_DELIVERY_STANDARD_ADOPTION_001` / `superseded`, but its
   corresponding `WS-GEOX-LEAN-DELIVERY-ADOPTION-001` workstream as
   `authorized`. Historical and current status must agree.

Correction must re-read live MIP, MMM, and GeoX mains and exact execution files
immediately before editing and again immediately before publication. Update the
existing eleven owned paths as needed so every repository entry, workstream,
sequence, Markdown view, and semantic test agrees with the final live evidence.
At minimum, record GeoX branch binding with its actual live lifecycle state,
mark the superseded lean-delivery workstream as superseded, keep every P2 blocker
open, and preserve all owner and authority boundaries.

Run the complete Tier-3 validation gate on the frozen corrected tree and publish
a new exact-tree receipt. Retain rejected head
`1f2783fbb490673b9aaf82f74fe5923df5d2e97f` as historical review evidence. Do
not modify product/runtime code, siblings, canonical P0–P8, or capability
authority.