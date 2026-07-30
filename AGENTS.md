# MIP Codex Execution Rules

Every Codex session must first read, in order:

1. `docs/execution/EXECUTION_STATE.json`
2. `docs/execution/ACTIVE_TASK.md`
3. `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
4. the relevant `docs/program/` files.

Stop rather than guess if an execution file is missing, stale, contradictory, or
unauthorized. `.codex/` and `docs/tasks/` are local-only and must never be
committed.

Fresh chats must begin with the **Fresh Chat Bootstrap** in
`docs/execution/REPOSITORY_CONTEXT_INDEX.md`; do not rely on prior chat
summaries as authoritative context.

## Execute the active task

Verify the execution status and `task_execution_authorized`; verify `main`, the
base SHA, prerequisites, and the exact feature branch; remain within owned
files; run focused and full validation; write
`docs/execution/LATEST_COMPLETION_REPORT.md`; update
`docs/execution/EXECUTION_STATE.json` to `ready_for_review` with
`merge_authorized: false`; commit and push; then stop without merging.

## Merge the approved active task

Verify `approved_for_merge`, `merge_authorized`, and reviewed-head integrity;
fast-forward merge only; push `main`; verify local/remote synchronization;
delete local and remote feature branches; and record the merged closure state.
No capability authority follows from task execution metadata.
