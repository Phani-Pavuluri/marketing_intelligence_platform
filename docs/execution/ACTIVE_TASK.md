# Active Task

**Status:** ready_for_review
**Owner:** MIP program governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `MIP_CROSS_REPOSITORY_COORDINATION_CONTROL_PLANE_001`
- **Feature branch:** `docs/mip-cross-repository-coordination-control-plane-001`
- **Execution mode:** `branch_and_fast_forward`
- **Pre-authoring base:** `4ddbe8323de6af44086da34001ec60072b58c1e8`
- **Authorization head:** `8fd0d30355510b7d239811163680c3dff87bfc7d`
- **Synchronized MIP main at review:** `631763cfb75fc42f8b1bf7025c5bce34c39097b5`
- **Rejected implementation commit:** `47ea2dc6f9a0096cfc76c975c6516c777ad20968`
- **Rejected remote review head:** `55b5dc7b6d58d268688955daa84ec9378ebdc8c7`
- **MMM main verified at review:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **GeoX main verified at review:** `ee9673c13e69082367c1727568946ac4c1a01015`
- **Capability authorizations changed:** `false`

## Review decision

The first implementation is not approved. It establishes the intended MIP-owned
coordination protocol, state, history, bootstrap rules, and focused test, but the
published ledger contains stale and internally contradictory sibling evidence,
duplicates already-authorized GeoX work, imposes an invalid cross-repository
dependency, lacks executable live dependency-resolution semantics, retains a
completion placeholder, and tests the incorrect cached state.

Resume this existing feature branch. Do not create a replacement branch, PR, or
merge. Re-fetch all three remote mains and stable execution files before making
corrections. Live Git at correction time overrides the review-time pins above.

## Review blockers

1. `MIP-COORD-REVIEW-STALE-GEOX-PIN`
2. `MIP-COORD-REVIEW-DUPLICATE-GEOX-WORK`
3. `MIP-COORD-REVIEW-INVALID-OWNER-DEPENDENCY`
4. `MIP-COORD-REVIEW-LIVE-RESOLUTION-GAP`
5. `MIP-COORD-REVIEW-COMPLETION-PLACEHOLDER`
6. `MIP-COORD-REVIEW-TEST-COVERAGE-GAP`

## Mandatory correction bootstrap

Before modifying anything:

1. Synchronize the MIP branch and verify its exact remote head.
2. Fetch current remote `main` for MIP, MMM, and GeoX.
3. Read root `AGENTS.md` and the stable execution files in all three repos.
4. Read MIP coordination protocol, state, history, program state, checkpoints,
   next sequence, decision register, and P2 consumer design.
5. Read the live GeoX active task and execution state rather than inferring its
   status from the cached MIP ledger.
6. Stop on a changed branch lineage, overlapping non-task-owned changes,
   unresolved authority conflict, or unverifiable sibling state.

At review time, GeoX `main` was
`ee9673c13e69082367c1727568946ac4c1a01015`, with active authorized task
`GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001`. Do not hardcode that as
current if live GeoX `main` has advanced.

## Required corrections

### 1. Correct all stale sibling evidence

Update every current-checkpoint reference using live Git, including:

- `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json`
- `docs/program/CROSS_REPOSITORY_COORDINATION_HISTORY.md`
- `docs/program/PROGRAM_CURRENT_STATE.md`
- `docs/program/REPOSITORY_CHECKPOINTS.md`
- `docs/program/NEXT_EXECUTION_SEQUENCE.md`
- `docs/roadmap/MIP_P2_CROSS_REPOSITORY_READINESS_RECONCILIATION_001.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`
- `tests/test_cross_repository_coordination_control_plane.py`

Keep GeoX `e0cef94c063b03b29e1e1760fb1c2320ce497b56` only as the prior V2 closure
and builder-task base when supported by live GeoX Git. Never combine that old
SHA with the newer builder task/status.

For active sibling tasks, record sufficient source identity to verify the state:
observed remote-main SHA, task ID/status, authorization head, base/closure where
relevant, feature branch, evidence paths, and verification date.

### 2. Represent the existing GeoX work once

The live GeoX task
`GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001` already owns:

- temporal boundaries;
- deterministic freshness and expiry;
- record kind and schema;
- producer package-version semantics;
- governed-readout builder;
- package entrypoint.

Represent this as one owner-repository workstream advancing both:

- `P2-GEOX-TEMPORAL-VERSION-SEMANTICS`
- `P2-GEOX-READOUT-BUILDER-ENTRYPOINT`

Remove the separate proposed temporal and builder tasks from the program
sequence, or explicitly mark those old identities absorbed/superseded by the
existing combined authorized GeoX task. Do not create parallel aliases for the
same capability.

### 3. Preserve repository authority

Remove any dependency from the already-authorized GeoX builder task to
`GEOX_CROSS_REPOSITORY_COORDINATION_PROTOCOL_ADOPTION_001`.

Remove any statement that GeoX implementation depends on MIP authorization.
GeoX authorizes GeoX work. Protocol adoption is separate governance work and may
run later or in parallel unless GeoX itself records it as a dependency.

MIP coordination metadata may observe and sequence owner-repository work, but it
cannot add, split, block, or authorize that work retroactively.

### 4. Make dependency resolution executable

For every workstream dependency, add an explicit live resolution condition and
source evidence. At minimum:

- `WS-MIP-COORDINATION-001` is satisfied only when live MIP execution state
  records this task as merged at the externally approved implementation lineage;
- sibling protocol-adoption work becomes eligible from that live merged
  condition even when the cached MIP repository entry is stale;
- a stale snapshot invokes a deterministic live overlay/reconciliation step;
- cached `in_progress` status cannot permanently block work after live Git shows
  the dependency merged;
- repository-main observed state, feature-branch review state, producer
  completion, consumer verification, and coordination-ledger state remain
  distinct.

Define how a live overlay changes eligibility without silently mutating cached
history or claiming the ledger itself is current.

### 5. Correct coordination history

Record GeoX V2 closure at `e0cef94...` as one historical event. Record the later
GeoX builder authorization at its own exact live authorization/main evidence as
a separate event. Do not attribute the later task to the earlier closure SHA.

The history remains append-only in meaning: preserve prior events and add a
correction/reconciliation event rather than rewriting historical facts into a
single combined event.

### 6. Replace completion placeholders

Remove the entire instructional placeholder beginning with
`Before ready_for_review, replace this section` from the completion report.
The corrected report must contain one actual execution-evidence section and one
current implementation SHA, with no stale implementation/review claims.

### 7. Strengthen focused governance tests

Update `tests/test_cross_repository_coordination_control_plane.py` to verify:

- exact current sibling pins and source task/status evidence;
- an active sibling task agrees with its observed main and authorization head;
- one owner workstream may advance multiple blocker IDs;
- the single live GeoX builder workstream advances both GeoX blocker IDs;
- no duplicate temporal/builder tasks remain proposed;
- the GeoX builder does not depend on protocol adoption;
- no GeoX task is described as requiring MIP authorization;
- every dependency has an explicit live resolution condition;
- stale coordinator-self state is reconcilable from live merged execution state;
- coordination history separates closure from later authorization;
- the completion report contains no placeholder instructions;
- all authority freezes remain unchanged.

Do not merely hardcode a new set of SHAs. Test the consistency relationships
that prevented the first implementation from failing closed.

## Owned files

Corrections may modify only the original task-owned paths:

- `AGENTS.md`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `docs/program/CROSS_REPOSITORY_COORDINATION_PROTOCOL.md`
- `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json`
- `docs/program/CROSS_REPOSITORY_COORDINATION_HISTORY.md`
- `docs/program/PROGRAM_CURRENT_STATE.md`
- `docs/program/REPOSITORY_CHECKPOINTS.md`
- `docs/program/NEXT_EXECUTION_SEQUENCE.md`
- `docs/program/DECISION_REGISTER.md`
- `docs/roadmap/MIP_P2_CROSS_REPOSITORY_READINESS_RECONCILIATION_001.md`
- `tests/test_cross_repository_coordination_control_plane.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

No sibling repository or other MIP path is authorized.

## Validation gate

Run on the corrected exact branch tree:

- focused coordination-control-plane test;
- relevant execution, documentation, and governance tests;
- JSON parsing and Markdown/path consistency checks;
- Ruff and mypy for the changed Python surface;
- `git diff --check`;
- exact changed-path verification;
- Docker-backed `make validate`.

Record exact pass, skip, and warning counts. If required validation cannot finish
successfully, publish an accurate `blocked` state with exact evidence.

## Required republish state

On successful correction:

- commit the corrected implementation;
- replace the rejected implementation SHA with the new full implementation SHA;
- publish a final metadata commit setting status to `ready_for_review`;
- keep `task_execution_authorized: true`;
- keep `merge_authorized: false`;
- keep approval SHA null;
- clear review blockers only after the corrections and validation pass;
- keep `capability_authorizations_changed: false`;
- push and prove the exact remote feature-branch head;
- stop without a PR, merge, or branch deletion.

## Correction execution result

The correction implementation is
`067aeca571f2702b88aee92f8647ededee1df0f1`. It refreshes the live GeoX pin
and source identity, represents the GeoX builder once for both blocker IDs,
removes the invalid protocol-adoption dependency, adds deterministic live-overlay
resolution rules, separates the GeoX closure and later authorization in history,
replaces the completion placeholder, and strengthens the focused governance
test. The task is ready for an exact-head review; `merge_authorized` remains
`false`, and no capability authority changed.

## Prohibited actions

Do not modify MMM or GeoX. Do not create a PR. Do not merge, squash, rebase,
force-push, or delete branches. Do not implement P2 consumers, engine contracts,
adapters, package entrypoints, simulations, recommendations, optimization,
orchestration, live integration, real data, pilot, production, or agents.
