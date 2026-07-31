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
- **Synchronized MIP main:** `631763cfb75fc42f8b1bf7025c5bce34c39097b5`
- **MMM main:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **GeoX main:** `ee9673c13e69082367c1727568946ac4c1a01015`
- **First rejected implementation/review head:** `47ea2dc6f9a0096cfc76c975c6516c777ad20968` / `55b5dc7b6d58d268688955daa84ec9378ebdc8c7`
- **Second rejected implementation/review head:** `067aeca571f2702b88aee92f8647ededee1df0f1` / `96815daf3cfa3d8d5c658016219784e8e94947b8`
- **Capability authorizations changed:** `false`

## Review decision

The second implementation fixes the original six review blockers: current GeoX evidence is source-consistent, the existing GeoX task is represented once for both blockers, invalid owner dependencies are removed, live-overlay dependency resolution is defined, the completion placeholder is gone, and focused governance coverage is materially stronger.

It is not yet approved because the shared machine-readable snapshot still caches the rejected feature-branch review state as though it were the feature branch state, and the append-only history attributes implemented corrections to the earlier review-decision head rather than to the correction implementation.

Resume the existing branch. Do not create a replacement branch, PR, or merge. Re-fetch live MIP, MMM, and GeoX `main` before modifying files.

## Current review blockers

1. `MIP-COORD-REVIEW-MUTABLE-FEATURE-STATE-CACHE`
2. `MIP-COORD-REVIEW-HISTORY-EVIDENCE-ATTRIBUTION`

## Required corrections

### 1. Do not cache mutable feature-branch status in the shared snapshot

`docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json` currently records under `WS-MIP-COORDINATION-001`:

- feature head `b0a9a9c1812b1ae1740d85fbb29827d60d338ebe`;
- status `changes_requested`.

That pair accurately describes the prior rejected review state, but the feature branch is now at rejected review head `96815daf3cfa3d8d5c658016219784e8e94947b8` with execution state `ready_for_review`. A field named `feature_branch_review_state` in the current coordination snapshot therefore becomes stale immediately and conflicts with the branch execution files.

Remove mutable feature-branch status/head from the shared coordination snapshot. Replace it with a policy/source reference stating:

- repository `main` observations belong in the coordination snapshot;
- mutable feature-branch review state must be read from that branch's `EXECUTION_STATE.json`, `ACTIVE_TASK.md`, and `LATEST_COMPLETION_REPORT.md` at the exact remote head;
- rejected review heads remain recorded in repository execution metadata and coordination history;
- a feature branch never satisfies a merged workstream dependency.

Do not embed the final branch-head SHA in the commit that creates it. The final exact review head remains externally observed.

Update `CROSS_REPOSITORY_COORDINATION_PROTOCOL.md` if needed to make this source boundary explicit.

### 2. Correct history evidence attribution

`CROSS_REPOSITORY_COORDINATION_HISTORY.md` currently says the event evidenced by MIP branch head `b0a9a9c1812b1ae1740d85fbb29827d60d338ebe` corrected stale pins, duplicate GeoX identities, and live-overlay behavior.

That SHA recorded the first `changes_requested` decision; it did not implement those corrections. Preserve append-only meaning by representing separate events:

- `b0a9a9c...`: review changes requested; no implementation or authority impact;
- `067aeca...`: first correction implementation published, fixing the original six review blockers, pending exact-head review;
- `96815daf...`: corrected review state published and then rejected by this second review because of mutable feature-state caching and history attribution.

Do not claim that a review-decision SHA implemented later changes.

### 3. Strengthen focused tests

Update `tests/test_cross_repository_coordination_control_plane.py` to verify:

- the shared snapshot does not cache mutable feature-branch review status/head;
- the snapshot points reviewers to exact branch execution files for mutable feature state;
- feature branches cannot satisfy merged dependency conditions;
- history distinguishes review-decision, correction-implementation, and later review-head events;
- `b0a9a9c...` is not described as implementing the coordination corrections;
- `067aeca...` is recorded as the first correction implementation;
- all prior source consistency, ownership, blocker, live-overlay, placeholder, and authority assertions remain.

### 4. Completion evidence

Publish one new implementation SHA for this correction. The completion report must retain the earlier rejected heads as history, contain no placeholders, distinguish GitHub-observed from execution-reported validation, and report exact validation counts.

## Owned files

This correction may modify only:

- `docs/program/CROSS_REPOSITORY_COORDINATION_PROTOCOL.md`
- `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json`
- `docs/program/CROSS_REPOSITORY_COORDINATION_HISTORY.md`
- `tests/test_cross_repository_coordination_control_plane.py`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

No sibling repository or other MIP path is authorized.

## Validation gate

Run on the exact corrected tree:

- focused coordination-control-plane test;
- relevant execution, documentation, and governance tests;
- JSON parsing and Markdown/path checks;
- Ruff and mypy for the changed Python surface;
- `git diff --check`;
- exact changed-path verification;
- Docker-backed `make validate`.

Publish `blocked` if required validation cannot complete successfully.

## Required republish state

On success:

- commit the correction implementation;
- publish a final metadata commit setting `ready_for_review`;
- record one new implementation SHA;
- retain both prior rejected review heads and implementations as history;
- clear these two blockers only after corrections and validation pass;
- keep task execution authorized;
- keep merge and PR authorization false;
- keep approval SHA null;
- keep capability authority unchanged;
- push and verify the exact remote feature head;
- stop without PR, merge, or branch deletion.

## Second correction execution result

Corrected implementation `4c93a7c300b3471ffee2a11ff449094e82a1f11d`
removes mutable feature-branch status and head from the shared coordination
snapshot, adds a stable exact-branch evidence policy, correctly separates the
two review decisions from the first correction implementation in history, and
extends the focused test to enforce both boundaries. The task is ready for a
new exact-head review only: `merge_authorized` and PR authorization remain
`false`; capability authority is unchanged.

## Prohibited actions

Do not modify MMM or GeoX. Do not create a PR. Do not merge, squash, rebase, force-push, or delete branches. Do not implement product, analytical, runtime, recommendation, optimization, pilot, production, or package-side-agent capability.
