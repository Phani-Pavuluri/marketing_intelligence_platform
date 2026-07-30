# MIP Repository Execution Handoff V1

**Status:** active execution standard
**Owner:** MIP program governance
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** MIP `a2bda05fdb32ee621963a6c61261e4f92c67c89e`
**Update trigger:** an approved execution-governance change.

## Source precedence

1. Verified Git repository state and committed behavior.
2. `docs/program/` canonical state.
3. `docs/execution/` active task and execution state.
4. Active contracts, roadmaps, ADRs, and validation evidence.
5. Archived or superseded documents.
6. Chats and pasted summaries.

A lower-ranked source cannot override a higher-ranked one.

## Stable paths and default mode

Exactly one current copy exists at `docs/execution/ACTIVE_TASK.md`,
`docs/execution/LATEST_COMPLETION_REPORT.md`, and
`docs/execution/EXECUTION_STATE.json`. Future tasks replace these files in
place; Git history preserves prior versions.

The default mode is `branch_and_fast_forward`:

```text
task proposed → user approval → task/state committed to main → feature-branch execution
→ completion report → ready_for_review → GitHub/diff review → exact-head approval
→ fast-forward merge → push/cleanup → merged → next task replaces stable files
```

No pull request is required. `direct_to_main` is permitted only when the active
task explicitly authorizes it.

## Statuses and fail-closed rules

Allowed statuses are `idle`, `proposed`, `authorized`, `in_progress`,
`blocked`, `ready_for_review`, `changes_requested`, `approved_for_merge`,
`merged`, and `superseded`.

Codex must stop if task status is not authorized; task authorization is false;
`main` differs from base; a prerequisite is absent; task/state disagree; branch
does not match; unrelated tracked changes exist; scope or authority is exceeded;
validation cannot complete (including Docker or dependency failure); merge
approval is absent; or the branch changes after reviewed head is recorded.
Proposed, implemented, or validated never means authorized.

## Authoring, reporting, review, and merge

After user approval, ChatGPT may write the full task into ACTIVE_TASK and state
on `main`; that metadata authorizes only the named task, never a product
capability. Before completion, Codex writes the completion report with task and
repository identity, mode, base/branch/implementation commit, changed files,
prerequisites, deliverables, acceptance results, focused/full validation, Ruff,
mypy, diff check, Docker result, GitHub-observed versus local evidence,
limitations, deferred work, authority impact, merge readiness, and local-only
paths. It then records `ready_for_review` while merge authorization remains
false.

ChatGPT review uses current main, all stable execution files from the branch,
complete branch diff and commits, and available GitHub CI. Approval binds an
exact reviewed head. Merge requires `approved_for_merge`, `merge_authorized`, a
populated reviewed head that remains an ancestor, only execution-approval
metadata after it, and passed required validation. Merge is fast-forward only;
then push, synchronize, delete both branch copies, set state `merged`, and
preserve the report on main.
