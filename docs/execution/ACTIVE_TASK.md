# Active Task

**Status:** merged and closed
**Owner:** MIP repository governance
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** MIP `main` / `e3a6c8cb437296e1319449b471c19301b08d43cb`
**Update trigger:** execution-state transition, review decision, or task closure.

## Identity

- **Task ID:** `MIP_REPO_NATIVE_EXECUTION_HANDOFF_V2_RECOVERY_001`
- **Base branch/SHA:** `main` / `e3a6c8cb437296e1319449b471c19301b08d43cb`
- **Feature branch:** `feat/mip-repo-native-execution-handoff-v2-recovery-001`
- **Execution mode:** `branch_and_fast_forward`
- **Recovery target:** `MIP_REPO_NATIVE_EXECUTION_HANDOFF_WORKFLOW_V2_001`
- **External PR:** `#48`
- **External branch head:** `6313c3e807226d20c260b62a6e863d94a213c533`
- **External merge commit:** `e3a6c8cb437296e1319449b471c19301b08d43cb`
- **Capability authorizations changed:** `false`
- **Approved recovery head:** `25ea5204bc6210dde9343d6ef49254f6b3689d71`
- **Conforming merge mechanism:** local fast-forward after exact-head approval

## Why recovery is required

PR #48 placed the V2 workflow files on `main` while the committed task was
`blocked` because Docker-backed `make validate` had not run. The committed state
had `merge_authorized: false`, no reviewed head, and no approval commit. GitHub
contained no PR review or conversation approval record when this recovery task
was authorized. The merge used a GitHub merge commit rather than the required
fast-forward path.

This task must preserve those facts. Do not retroactively describe PR #48 as an
approved or conforming V2 merge. Do not rewrite or revert Git history merely to
make it look conforming.

## Objective

Validate the exact V2 workflow tree now present on `main`, reconcile its lineage
and scope, and produce an auditable recovery branch that can be reviewed and
fast-forward merged under the V2 exact-head process. After a later explicit
approval and merge session, close the recovery accurately, remove stale workflow
branches, and establish the final canonical MIP V2 pin.

This is governance recovery only. No product or analytical implementation is
owned or authorized.

## Owned files

Execution may modify only:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify `AGENTS.md`, `TASK_EXECUTION_STANDARD.md`, tests, `docs/program/`,
product code, contracts, adapters, orchestration, MMM, or GeoX. If an existing
focused test cannot represent the recovery using the current V2 schema and
status vocabulary, stop and report the conflict rather than expanding scope.

## Task-authoring boundary

The pre-authoring base is `e3a6c8cb437296e1319449b471c19301b08d43cb`.
Verify `base_sha..authorization_head_sha` changes only the three stable execution
files. Because a commit cannot contain its own SHA, one final state-only commit
may be present immediately after `authorization_head_sha` solely to record that
boundary. No other path or commit is permitted between the authorization head
and synchronized `main`.

Create the feature branch from the exact synchronized post-authoring `main`, not
from stale local state or the pre-authoring base.

## Prerequisites

1. Complete the mandatory bootstrap in `AGENTS.md` before reading or executing
   this task.
2. Prove local `main == origin/main` and that current `main` descends from
   `e3a6c8cb437296e1319449b471c19301b08d43cb` only through this task's stable
   metadata authoring commits.
3. Verify PR #48 metadata and lineage:
   - base `f83e91ef883af88808e03184b96bea26fba5eef8`;
   - branch head `6313c3e807226d20c260b62a6e863d94a213c533`;
   - merge commit `e3a6c8cb437296e1319449b471c19301b08d43cb`;
   - no recorded approval may be invented.
4. Verify the external branch head descends from the original V2 authorization
   head and that its changed paths are limited to the original V2 task-owned
   workflow/governance files.
5. Verify MMM and GeoX are not modified by this task. Their workflow adoption
   work remains paused pending a closed canonical MIP V2 pin.
6. Permit local-only untracked content only below `.codex/` and `docs/tasks/`.
   Stop for unrelated tracked changes or any other unexpected untracked path.

## Required execution

1. Create and switch to
   `feat/mip-repo-native-execution-handoff-v2-recovery-001` from exact
   synchronized `main`.
2. Record exact Git lineage and changed-path evidence for the original V2 task,
   PR #48, the external merge commit, and this task-authoring boundary.
3. Run the focused repository-native execution-handoff test and relevant
   governance/documentation checks.
4. Run JSON parsing, Markdown/path consistency checks, Ruff and mypy where
   applicable, and `git diff --check`.
5. Run Docker-backed `make validate` on the exact recovery branch tree. Host
   validation may supplement but never replace the Docker gate.
6. If Docker validation or any prerequisite fails, update the three stable files
   to an accurate `blocked` state, commit and push the branch, and stop. Do not
   claim recovery success.
7. If every gate passes, write a complete recovery report and publish a
   `ready_for_review` branch state with:
   - `task_execution_authorized: true`;
   - `merge_authorized: false`;
   - `reviewed_head_sha: null`;
   - `approval_commit_sha: null`;
   - populated `implementation_commit_sha`;
   - `capability_authorizations_changed: false`;
   - no blockers.
8. Commit and push the exact remote branch head, verify local/remote equality,
   and stop for ChatGPT review. Do not create or use a pull request. Do not merge
   or delete branches during execution.

## Completion report requirements

The report must preserve:

- original V2 base and authorization head;
- original implementation and blocked-state branch heads;
- PR #48 and external merge commit;
- explicit absence of a conforming pre-merge approval record;
- exact changed paths and lineage;
- Docker and host validation evidence;
- the recovery implementation commit and exact published review head;
- MMM/GeoX pause state;
- limitations and deferred work;
- `capability_authorizations_changed: false`.

## Later approved merge and closure

Only after the user approves the exact remote recovery-branch head may Codex run
`Merge the approved active task`. That merge session must re-fetch and verify the
approved head, rerun required validation, fast-forward merge without a PR, push
and verify `main`, delete both the recovery branch and the stale original V2
feature branch where present, then write exactly one post-merge closure metadata
commit.

The closure must record the external nonconforming merge and the conforming
recovery separately. It must not convert the former into an approved merge.
The resulting closure commit becomes the canonical MIP V2 pin for later MMM and
GeoX workflow adoption reconciliation.

## Prohibited scope and authority

The exact recovery head was explicitly approved, validated, fast-forwarded to
`main`, pushed, and followed by branch cleanup. This task is merged and closed.
The earlier PR #48 remains an external nonconforming merge and is not
retroactively described as conforming or approved.

Do not change or authorize product code, live package integration, real data,
persistence, simulation runtime, optimization, recommendations, treatment
assignment, pilot, production, MMM numerical truth, GeoX numerical truth, or any
package-side agent. Do not modify MMM or GeoX repositories.
