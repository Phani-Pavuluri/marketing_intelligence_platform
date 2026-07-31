# Active Task

**Status:** authorized governance amendment
**Owner:** MIP repository governance
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** `main` / `5eebba6750a3754e4026397d6762c601b1d6a708`
**Update trigger:** execution-state transition or task closure.

## Identity

- **Task ID:** `MIP_REPO_NATIVE_EXECUTION_HANDOFF_WORKFLOW_V2_001`
- **Base branch/SHA:** `main` / `5eebba6750a3754e4026397d6762c601b1d6a708`
- **Feature branch:** `feat/mip-repo-native-execution-handoff-workflow-v2-001`
- **Execution mode:** `branch_and_fast_forward`
- **Capability authorizations changed:** `false`

## Objective and owned files

Amend the repository-native execution workflow so every session synchronizes
Git state before task discovery, worktree checks permit only the two declared
local-only paths, approval binds the exact remote feature-branch head without a
pre-merge metadata commit, merge remains fast-forward-only and Docker-validated,
and closure is recorded in exactly one post-merge metadata commit.

Owned files are:

- `AGENTS.md`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `tests/governance/test_repo_native_execution_handoff.py`

No `docs/program/` file, product code, package integration, MMM repository file,
or GeoX repository file is owned by this task.

## Prerequisites

- Connected GitHub and local Git both resolve MIP `main` to
  `5eebba6750a3754e4026397d6762c601b1d6a708` before task authoring.
- `MIP_REPO_NATIVE_EXECUTION_HANDOFF_WORKFLOW_001` is merged and closed.
- MMM and GeoX adoption tasks remain untouched, authorized but unstarted, and
  pinned to obsolete canonical MIP commit `5eebba6`.
- The task-authoring commits on `main` may be ahead of the task base only by
  replacement of the three stable task/state/report files.
- The worktree contains no unrelated tracked or unexpected untracked paths.

## Deliverables and acceptance

1. Define mandatory session bootstrap: fetch/prune remote refs, hydrate required
   history, switch to `main`, pull `origin/main` with `--ff-only`, prove
   `main == origin/main`, then inspect task and prerequisites.
2. Define the task-authoring boundary without treating approved stable metadata
   commits as unrelated product changes.
3. Permit only `.codex/` and `docs/tasks/` as local-only untracked paths; fail
   closed on unrelated tracked changes and every other unexpected untracked
   path.
4. Keep completion at `ready_for_review` with `merge_authorized: false`; user
   approval must bind the exact remote feature-branch head SHA.
5. Remove the required pre-merge approval-metadata commit. A merge session must
   re-fetch and verify that the approved SHA still equals the remote feature
   branch head, verify unchanged `main`, run required validation, and merge with
   `--ff-only`.
6. Record reviewed head, implementation head, resulting main lineage,
   validation, approval provenance, authority impact, and branch cleanup in
   exactly one post-merge closure commit.
7. Preserve `capability_authorizations_changed: false` and keep all product and
   package capabilities unauthorized.
8. Update focused tests so the V2 workflow is enforced and reusable for later
   MMM and GeoX adoption.

## Validation and stop condition

Run JSON parsing, the focused execution-handoff test, focused governance tests,
changed-path Ruff and mypy where applicable, Markdown/path consistency,
`git diff --check`, and Docker-backed `make validate`.

Commit and publish the exact feature-branch head with state
`ready_for_review`, `merge_authorized: false`, no reviewed head, and no approval
commit; then stop for user review. Do not merge or modify MMM/GeoX until the user
approves that exact head.

No product capability, live engine integration, real data, persistence,
simulation runtime, optimization, recommendation, treatment assignment, pilot,
or production capability is authorized.
