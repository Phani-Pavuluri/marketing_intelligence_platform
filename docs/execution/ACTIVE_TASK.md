# Active Task

**Status:** changes_requested
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
- **Earlier intermediate reconciliation commit:** `113ba2c099608a7841e39202710caddabc50fa61`
- **Earlier rejected reconciliation implementation:** `c6648ef8b4a68fb0f863a53c3bb0c2dc167e2e17`
- **Earlier rejected review head:** `9a0c4b04ae3cc7f27c02249588388bd8b6436011`
- **GitHub-observed correction implementation:** `20d5aeea025ad6a4733367b085e583e73580caa2`
- **Rejected latest review head:** `29a18a3531bb202c13d9ae7b4fce9d0c3b115703`
- **Invalid reported SHA:** `20d5aee7170df4ce335376170290c167048812d9`
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

## Materially correct implementation

The branch implementation correctly:

1. distinguishes current MIP `main` at
   `18ab0d0c798dfcedd3f07034f4561320929477ea` from prior coordination closure
   `3520176126d129e9288a9ce37591299ec856650a`;
2. transitions the prior MIP coordination repository entry and workstream to
   merged historical state;
3. preserves live-overlay, ownership, dependency, and capability-authority
   boundaries;
4. repairs the six-step execution sequence and its GeoX/MMM/MIP dependency
   semantics;
5. keeps the active-task resolver, GeoX handoff-test repair, runtime, product,
   and sibling work outside scope.

The actual GitHub commit containing those corrections is
`20d5aeea025ad6a4733367b085e583e73580caa2`.

## Exact-head review decision

The exact remote review head
`29a18a3531bb202c13d9ae7b4fce9d0c3b115703` is **not approved**.

The three stable execution files report
`20d5aee7170df4ce335376170290c167048812d9` as the correction implementation.
GitHub does not contain that commit. The actual parent implementation commit of
the review-state commit is
`20d5aeea025ad6a4733367b085e583e73580caa2`.

This violates the task requirement that the completion report contain one exact,
GitHub-observed implementation SHA. A well-formed forty-character string is not
sufficient evidence that a Git commit exists.

## Required correction

Correct only the three stable execution files:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The republished state must:

1. use `20d5aeea025ad6a4733367b085e583e73580caa2` as the sole current
   `implementation_commit_sha`;
2. remove every current implementation claim for
   `20d5aee7170df4ce335376170290c167048812d9`, retaining it only as rejected
   erroneous metadata if useful;
3. retain rejected review head
   `29a18a3531bb202c13d9ae7b4fce9d0c3b115703` as history;
4. verify and report:
   - `git cat-file -e 20d5aeea025ad6a4733367b085e583e73580caa2^{commit}`;
   - `git merge-base --is-ancestor 20d5aeea025ad6a4733367b085e583e73580caa2 HEAD`;
   - the invalid SHA is absent from all current implementation fields;
5. rerun the complete authored validation gate and report exact results;
6. publish `ready_for_review` or an accurate `blocked` state;
7. keep task and correction execution authorized until review;
8. keep merge and PR authorization false;
9. keep reviewed and approval SHAs null;
10. keep capability authorization unchanged;
11. push and verify the new exact remote feature head; and
12. stop without PR, merge, branch deletion, sibling modification, resolver
    implementation, or GeoX handoff-test repair.

No program file or focused-test change is requested in this correction. The
substantive sequence, current-main, coordination, ownership, and authority fixes
at `20d5aeea025ad6a4733367b085e583e73580caa2` are accepted.

## Owned files

The task's full owned-file boundary remains:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`
- `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json`
- `docs/program/CROSS_REPOSITORY_COORDINATION_HISTORY.md`
- `docs/program/PROGRAM_CURRENT_STATE.md`
- `docs/program/REPOSITORY_CHECKPOINTS.md`
- `docs/program/NEXT_EXECUTION_SEQUENCE.md`
- `tests/test_cross_repository_coordination_control_plane.py`

This review correction authorizes edits only to the three stable execution files.
No MIP runtime, contract, adapter, fixture, orchestration, UI, analytical, or
other test path is owned. No MMM or GeoX path is owned.

## Validation gate

Run on the exact corrected tree:

- Git object-existence and ancestry checks for the implementation SHA;
- focused coordination-control-plane and execution/documentation tests;
- JSON parsing and Markdown/path consistency checks;
- exact changed-path verification;
- Ruff and configured mypy for changed Python files;
- `git diff --check`;
- Docker-backed full `make validate`.

Publish `blocked` with exact evidence if the complete authored gate cannot finish
successfully. Focused success does not hide full-suite debt.

## Prohibited authority

This task does not authorize live MMM/GeoX integration, customer data, uploads,
persistence, jobs, simulation runtime, optimization, recommendations, treatment
assignment, LLM decisioning, pilot, production, or package-side agents.
