# Active Task

**Status:** ready_for_review
**Owner:** MIP program governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `MIP_COORDINATION_POST_MERGE_CLOSURE_RECONCILIATION_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `main` / `3520176126d129e9288a9ce37591299ec856650a`
- **Authorization head:** `15657c31501f1376a015b773d913861f63322fb5`
- **Synchronized main after state authorization:** `18ab0d0c798dfcedd3f07034f4561320929477ea`
- **Feature branch:** `docs/mip-coordination-post-merge-closure-reconciliation-001`
- **Execution mode:** `branch_and_fast_forward`
- **Prior task:** `MIP_CROSS_REPOSITORY_COORDINATION_CONTROL_PLANE_001`
- **Approved prior review head / merged implementation head:** `cc1904db8e18b5ba461cca2da738026acadfb43c`
- **Prior correction implementation:** `4c93a7c300b3471ffee2a11ff449094e82a1f11d`
- **Prior closure commit:** `3520176126d129e9288a9ce37591299ec856650a`
- **Rejected reconciliation implementation:** `c6648ef8b4a68fb0f863a53c3bb0c2dc167e2e17`
- **Rejected review head:** `9a0c4b04ae3cc7f27c02249588388bd8b6436011`
- **Earlier intermediate reconciliation commit:** `113ba2c099608a7841e39202710caddabc50fa61`
- **Correction implementation:** `20d5aee7170df4ce335376170290c167048812d9`
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

The prior coordination implementation was externally approved at exact head
`cc1904db8e18b5ba461cca2da738026acadfb43c`, fast-forwarded, and closed at
`3520176126d129e9288a9ce37591299ec856650a`. The completed remote feature branch
was observed absent. MMM remains merged at
`1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`. GeoX remains independently
authorized at `ee9673c13e69082367c1727568946ac4c1a01015` for
`GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001`. No sibling capability or
consumer-verification state changed.

This reconciliation task was authored from prior closure `3520176126d129e9288a9ce37591299ec856650a`.
Its two-file authorization head is `15657c31501f1376a015b773d913861f63322fb5`,
and synchronized MIP `main` after the state-only authorization commit is
`18ab0d0c798dfcedd3f07034f4561320929477ea`.

## Authorized result

Produce a narrow post-merge reconciliation that:

1. makes the three stable execution files agree on the current reconciliation
   task state and the prior coordination task's merged closure;
2. distinguishes the prior approved review head, prior merged implementation
   head, prior closure commit, this task's authorization lineage, current
   synchronized MIP `main`, and the exact remote reconciliation review head;
3. records remote prior-feature-branch deletion as GitHub-observed evidence and
   does not claim unverified local cleanup;
4. removes obsolete instructions to resume, correct, review, or merge the prior
   task from current stable state;
5. transitions the prior MIP repository entry and `WS-MIP-COORDINATION-001` in
   the coordination snapshot to merged historical state at the verified prior
   closure, while preserving deterministic live-overlay behavior;
6. preserves append-only coordination history without treating review or task-
   authoring SHAs as implementation evidence;
7. updates program current state, repository checkpoints, and next execution
   sequence so the completed coordination task is not still listed as pending;
8. records that MMM and GeoX protocol adoption remain proposed and independently
   owner-authorized, and that the existing GeoX builder may continue without a
   retroactive MIP dependency;
9. adds focused tests that fail on mixed current-task state, stale current MIP
   evidence, missing closure history, obsolete resume instructions, unobserved-
   cleanup claims, an `in_progress` prior MIP coordination workstream after live
   merged closure, or internally inconsistent sequence numbering; and
10. preserves all runtime, integration, real-data, recommendation, optimization,
    pilot, production, and package-side-agent freezes.

## Rejected review history

The exact remote review head
`9a0c4b04ae3cc7f27c02249588388bd8b6436011` is **not approved**. The core
post-merge transition is materially correct, remains within scope, and preserves
ownership and authority. Three source-consistency defects must be corrected.

### 1. Publish one current implementation SHA

The task requires one implementation SHA. The rejected report instead lists two
"Implementation commits," while execution state names
`c6648ef8b4a68fb0f863a53c3bb0c2dc167e2e17` as current, stores a two-SHA
`implementation_lineage`, and then describes
`113ba2c099608a7841e39202710caddabc50fa61` as the implementation ready for
review.

Publish one new final correction implementation SHA. The completion report,
`implementation_commit_sha`, task execution result, and task-authoring note must
all name that same single SHA. Earlier commits may remain Git history, but must
be labeled intermediate or rejected history rather than additional current
implementation SHAs. Do not embed the final remote review-head SHA in the commit
that creates it.

### 2. Distinguish current MIP main from prior closure

At review, live MIP `main` is
`18ab0d0c798dfcedd3f07034f4561320929477ea`, not prior closure
`3520176126d129e9288a9ce37591299ec856650a`. The rejected completion report calls
the prior closure MIP `origin/main`; `PROGRAM_CURRENT_STATE.md` and
`REPOSITORY_CHECKPOINTS.md` also label the prior closure as their current
remote-main verification source.

Correct the current evidence model:

- `3520176126d129e9288a9ce37591299ec856650a` is the prior task closure and this
  task's pre-authoring base;
- `15657c31501f1376a015b773d913861f63322fb5` is the two-file authorization head;
- `18ab0d0c798dfcedd3f07034f4561320929477ea` is synchronized MIP `main` after the
  state-only authorization commit and remains the live main at this review;
- the correction implementation and exact remote review head remain feature-
  branch evidence, not MIP-main evidence.

The historical coordination snapshot may remain pinned to prior closure where
its repository-main observation is intentionally historical, but current-state,
checkpoint, execution, and report wording must not call that prior closure the
current MIP remote main.

### 3. Repair renumbered sequence semantics

`NEXT_EXECUTION_SEQUENCE.md` now has six steps but still says "steps 5–7." It
also says step 4 depends on live merged GeoX evidence, even though the direct
GeoX-producer dependency belongs to MMM normalization in step 3, while MIP step
4 depends on both merged GeoX producer evidence and merged MMM normalization /
certified fixtures with required consumer verification.

Correct the prose to the current six-step numbering and exact dependency chain.
Extend the focused test so nonexistent step references and this dependency
misassignment fail.

## Correction execution result

**Current decision:** `ready_for_review`

Correction implementation `20d5aee7170df4ce335376170290c167048812d9` is the
sole current implementation for this task. It corrects the current-MIP-main
evidence and the six-step dependency semantics, while preserving the historical
coordination snapshot at prior closure and all ownership and authority
boundaries. The earlier intermediate, rejected implementation, and rejected
review-head SHAs above remain review history only and are not current
implementation evidence.

## Owned files

Corrections may modify only:

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

Run on the exact corrected tree:

- focused coordination-control-plane and execution/documentation tests;
- JSON parsing and Markdown/path consistency checks;
- exact changed-path verification;
- Ruff and configured mypy for changed Python files;
- `git diff --check`;
- Docker-backed full `make validate`.

Publish `blocked` with exact evidence if the complete authored gate cannot finish
successfully. Focused success does not hide full-suite debt.

## Ready-for-review state

The three requested corrections are implemented at
`20d5aee7170df4ce335376170290c167048812d9`. `implementation_commit_sha` names
only that SHA; rejected review and implementation SHAs remain historical. The
three blockers are cleared after the complete authored validation gate passes.
Task and correction execution remain authorized for review, while merge and PR
authorization remain false; reviewed and approval SHAs remain null. Capability
authority remains unchanged. The branch must stop after pushing its exact remote
review head, without a PR, merge, or branch deletion.

## Prohibited authority

This task does not authorize live MMM/GeoX integration, customer data, uploads,
persistence, jobs, simulation runtime, optimization, recommendations, treatment
assignment, LLM decisioning, pilot, production, or package-side agents.
