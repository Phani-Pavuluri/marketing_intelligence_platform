# Repository Context Index

**Status:** active navigation index
**Owner:** MIP program owner
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** execution state on synchronized `origin/main`
**Update trigger:** canonical source-path or bootstrap change.

## Fresh Chat Bootstrap

Use this prompt in a fresh ChatGPT/Codex session:

> Use connected GitHub and synchronized Git as the source of truth. Treat
> `Phani-Pavuluri/marketing_intelligence_platform` as the primary repository.
> First classify the worktree: allow untracked content only below `.codex/` and
> `docs/tasks/`, and stop on unrelated tracked or other unexpected untracked
> paths. Run `git fetch --prune origin`; hydrate shallow or missing required
> history; run `git switch main` and `git pull --ff-only origin main`; and prove
> `git rev-parse main` equals `git rev-parse origin/main`. Run
> `make resume-active-task` before reading branch-specific task instructions.
> It resolves the canonical pointer on `origin/main`, selects only an exact
> verified executable branch, and reports review-only or non-executable states
> without guessing. Then read `AGENTS.md`, the stable `docs/execution/` files,
> and the seven canonical `docs/program/` files. Summarize synchronized current
> state, active task, latest completion, blockers, dependencies, authority
> boundaries, and next eligible work. Do not modify files or authorize work
> unless explicitly requested.

## Canonical program memory

- `docs/program/PROGRAM_CHARTER.md`
- `docs/program/PROGRAM_CURRENT_STATE.md`
- `docs/program/REPOSITORY_CHECKPOINTS.md`
- `docs/program/AUTHORITY_AND_FREEZE_MATRIX.md`
- `docs/program/NEXT_EXECUTION_SEQUENCE.md`
- `docs/program/DECISION_REGISTER.md`
- `docs/program/DEFERRED_AND_PARKED_WORK.md`
- `docs/program/CROSS_REPOSITORY_COORDINATION_PROTOCOL.md`
- `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json`
- `docs/program/CROSS_REPOSITORY_COORDINATION_HISTORY.md`

## Roadmap and P2 design

- `docs/roadmap/ROADMAP.md`
- `docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md`
- `docs/roadmap/MIP_DECISION_LIFECYCLE_ROADMAP_CONSOLIDATION_001.md`
- `docs/roadmap/MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md`

## Execution handoff

- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`
- `docs/execution/EXECUTION_STATE.json`

## Connected repositories

- `Phani-Pavuluri/MMM`
- `Phani-Pavuluri/panel_exp`

Verify exact engine checkpoints from GitHub and
`docs/program/REPOSITORY_CHECKPOINTS.md` before dependent work. This index
points to sources and does not duplicate their authority.

For cross-repository work, verify the coordination-state SHAs against live
sibling Git and inspect the sibling execution state, completion report,
workstream, blocker, and owner records. A stale coordination snapshot is a
fail-closed orientation trigger, not cached authority.
