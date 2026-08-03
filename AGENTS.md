# MIP Codex Execution Rules

## Mandatory session bootstrap

Before task discovery or implementation:

1. Inspect `git status --porcelain=v1 --untracked-files=all`. Fail closed on
   unrelated tracked changes or unexpected untracked paths. Untracked content
   is permitted only below `.codex/` and `docs/tasks/`; never commit it.
2. Run `git fetch --prune origin`. If the clone is shallow or a required commit
   is absent, hydrate the required history before continuing.
3. Run `git switch main` and `git pull --ff-only origin main`.
4. Verify `git rev-parse main` exactly equals `git rev-parse origin/main`.
5. Read, in order:
   - `docs/execution/EXECUTION_STATE.json`
   - `docs/execution/ACTIVE_TASK.md`
   - `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
   - the relevant `docs/program/` files.

Stop rather than guess if synchronization, history hydration, execution files,
authorization, prerequisites, or repository state cannot be verified. Chats and
pasted summaries are never authoritative repository state.

Before authoring or executing a task, read
`docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md`. Keep one task to one
independently reviewable mergeable outcome; split an independently valid
checkpoint into a successor task and use validation proportionate to its risk.

## Execute the active task

Verify the authorized task, its task-authoring boundary, prerequisites, owned
files, and exact feature branch. Resume only when tracked changes are
task-owned. Run the active task's declared risk-tier validation gate for
execution, exact-head review, and post-fast-forward validation. Docker-backed
`make validate` remains required whenever Tier 3, the active task, the changed
surface, or another repository-authored gate requires it. Write
`docs/execution/LATEST_COMPLETION_REPORT.md`; update
`docs/execution/EXECUTION_STATE.json` to `ready_for_review` with
`merge_authorized: false`; commit and publish the exact remote feature-branch
head; then stop without merging.

## Cross-repository task rule

Before proposing or executing work that affects MMM or GeoX, read
`docs/program/CROSS_REPOSITORY_COORDINATION_PROTOCOL.md` and
`CROSS_REPOSITORY_COORDINATION_STATE.json`; verify every affected sibling SHA
against live Git; read live sibling execution state and completion evidence when
the snapshot is stale or a dependency exists; and stop on overlapping
workstream IDs or ownership conflicts. Record dependency IDs in the active task
and include the protocol's cross-repository impact section in the completion
report. Refresh coordination state only when the task explicitly owns a
verified refresh.

## Merge the externally approved head

User approval must identify the exact remote feature-branch head SHA. Re-run the
mandatory bootstrap, re-fetch the feature branch, verify its head still equals
the approved SHA, verify `main` has not moved beyond the authorization boundary,
and rerun the active task's required risk-tier gate. Use `git merge --ff-only`;
never create a pre-merge approval-metadata commit.

After the fast-forwarded implementation is pushed and branch cleanup is
observed, record approval provenance, reviewed head, validation, authority
impact, resulting main lineage, and cleanup results in exactly one post-merge
closure commit. Push and verify local/remote synchronization. No capability
authority follows from task execution metadata.
