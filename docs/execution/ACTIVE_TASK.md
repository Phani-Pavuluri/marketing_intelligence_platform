# Active Task

**Status:** authorized bootstrap task
**Owner:** MIP repository governance
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** base `a2bda05fdb32ee621963a6c61261e4f92c67c89e`
**Update trigger:** task replacement or execution-state transition.

## Identity

- **Task ID:** `MIP_REPO_NATIVE_EXECUTION_HANDOFF_WORKFLOW_001`
- **Base branch/SHA:** `main` / `a2bda05fdb32ee621963a6c61261e4f92c67c89e`
- **Feature branch:** `feat/mip-repo-native-execution-handoff-workflow-001`
- **Execution mode:** `branch_and_fast_forward`

## Objective and owned files

Establish repository-native task, completion-report, and fresh-chat handoff
workflow. Owned files are `AGENTS.md`, all four stable execution files, the
execution standard/context index, and
`tests/governance/test_repo_native_execution_handoff.py`.

## Prerequisites, deliverables, and acceptance

Prerequisites: verified base SHA, clean tracked worktree, and existing
`docs/program/` state. Deliverables are the repository instructions, execution
standard, context index, active task/state/report, and focused consistency test.
Acceptance requires stable paths, fail-closed state validation, full completion
report, passing focused/full validation, and a `ready_for_review` state with
merge authorization false.

## Validation, limits, and closure

Run JSON parsing, execution-file consistency, Markdown link/path checks, diff
check, focused governance/documentation tests, and Docker `make validate`.
Do not implement product capability, live MMM/GeoX integration, real data,
persistence, simulation runtime, optimization, recommendation, pilot, or
production. Commit and push the feature branch, but do not merge before review.
