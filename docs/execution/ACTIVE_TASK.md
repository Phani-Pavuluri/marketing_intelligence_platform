# Active Task

**Status:** ready_for_review
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_LEAN_REPOSITORY_DELIVERY_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-lean-repository-delivery-standard-001`
- **Rejected implementation commit:** `25d254a20a0eca75094c0b4a4d7e5cd23944e55c`
- **Rejected review head:** `0f48c697df28ff57241e894115f9bc2c47ee01e2`
- **Correction implementation commit:** `9dda47f3f90877161175c02a736694d5ee253f48`
- **Capability authorizations changed:** `false`

## Review decision

The lean-delivery standard, task sizing rule, and sibling authority boundaries are accepted in principle. One material contradiction remains: the new risk-tier guidance permits a narrow Tier 1 gate, while `AGENTS.md` and `TASK_EXECUTION_STANDARD.md` still command Docker-backed full validation for every execution and merge.

The user authorized a one-time clean branch reset from review-decision head `b995823896a7caa2245e43f468b2d08fe511bc42` back to rejected review head `0f48c697df28ff57241e894115f9bc2c47ee01e2`. That reset removed the accidental temporary `docs/tasks/.review-placeholder` history from the active branch. No history blocker remains.

## Correction authorization

Correction execution is authorized. Keep the correction to one mergeable outcome: make risk-tiered validation operative without weakening analytical, public-contract, cross-repository, or production gates.

## Owned paths

Correction work may modify only:

1. `AGENTS.md`
2. `docs/execution/TASK_EXECUTION_STANDARD.md`
3. `docs/execution/ACTIVE_TASK.md`
4. `docs/execution/EXECUTION_STATE.json`
5. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify the lean standard itself, the context index, automation, resolver code, tests, Makefiles, coordination files, product/runtime/analytical code, MMM, or GeoX.

## Required correction

- Make execution run the exact validation gate authorized by the active task and its risk tier.
- Require Docker/full-suite validation for Tier 3 and whenever the active task, changed repository surface, or repository-authored gate explicitly requires it.
- Permit Tier 1 documentation work to use its declared narrow gate.
- Apply the same task-authorized gate before merge and after fast-forward.
- Require completion and closure reports to mark each validation category as passed, failed, blocked, or not required.
- Preserve Git authority, exact-head review, owned-path enforcement, fail-closed behavior, and sibling authority.

## Validation and publication

Run JSON and Markdown consistency checks, exact changed-path verification, `git diff --check`, and the focused execution-governance test affected by these rules.

On success, publish `ready_for_review` with one new implementation commit SHA, empty blockers, merge and PR creation false, and unchanged capability authority. Push the exact branch head and stop.

Do not create a PR, merge, rebase, squash, force-push again, delete branches, modify siblings, or authorize any capability.

## Publication state

The bounded correction is ready for exact-head review. Its review-publication
commit contains only stable execution metadata and the completion report. Merge
and PR creation remain false; no capability authority changed.
