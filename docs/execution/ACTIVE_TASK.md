# Active Task

**Status:** changes_requested
**Owner:** MIP program governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `MIP_ACTIVE_TASK_CONTEXT_RESOLVER_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `d35fbbb82711b073c3504d5cc0f1b807e9b36c81`
- **Authorization head:** `221b0dedc73432a9b04d331c2544fe807b8f1013`
- **Synchronized state-only head:** `11c062eb785b3518d531992aa554d0a3a4c0b84b`
- **Feature branch:** `feat/mip-active-task-context-resolver-001`
- **Rejected implementation:** `18f7ffdd5b3ef20af4cea177047c11f5ffadd8f0`
- **Rejected review head:** `abf57a6fb0c08d23fb51c56a5ea744445b3ab82c`
- **Review-state head before amendment:** `e5a0fd5f1d7fadd2d9268128bd69409962d32e45`
- **Observed MMM main:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Observed GeoX main:** `ee9673c13e69082367c1727568946ac4c1a01015`
- **Capability authorizations changed:** `false`

## Correction authorization

The user authorized the scope amendment and correction execution on 2026-07-31.
Correction execution is now authorized on the existing feature branch. Preserve
the materially correct resolver architecture and correct only the findings and
matrices below.

## Corrected owned-path boundary

Correction work may modify only these ten paths:

1. `AGENTS.md`
2. `Makefile`
3. `scripts/resolve_active_task.py`
4. `docs/execution/TASK_EXECUTION_STANDARD.md`
5. `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
6. `docs/execution/ACTIVE_TASK.md`
7. `docs/execution/EXECUTION_STATE.json`
8. `docs/execution/LATEST_COMPLETION_REPORT.md`
9. `tests/test_active_task_context_resolver.py`
10. `tests/test_cross_repository_coordination_control_plane.py`

The tenth path is explicitly authorized because the existing coordination test
contains the state-coupled assertions that this task must replace with semantic
execution invariants.

Do not modify program coordination artifacts, MIP product/runtime/analytical
code, contracts, adapters, fixtures, orchestration, UI, MMM, or GeoX.

## Preserve from the rejected implementation

Preserve unless correction requires adjustment:

- pointer-first reads from `origin/main:docs/execution/EXECUTION_STATE.json`;
- repository/origin, worktree, fetch, fast-forward-only main synchronization,
  remote-branch, ancestry, and exact local/remote head checks;
- `make resume-active-task` and deterministic text/JSON output;
- review-only treatment of `ready_for_review`;
- real Git-object and ancestry checks for `implementation_commit_sha`;
- temporary local Git repositories and bare remotes for tests;
- no sibling or capability authority changes.

## Required corrections

### A. Human-view validation for every state

Validate `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md` against the canonical
execution state before returning for any lifecycle state, including `idle`,
`proposed`, `merged`, `superseded`, and `ready_for_review`.

Each human-readable file must expose exactly one current status/decision matching
state. Explicitly historical sections may contain old statuses only when clearly
labeled historical and excluded from current-state parsing. A merged closure
must not retain an unlabeled current `ready_for_review` claim.

### B. Exact schema and reason-coded failures

Require schema version exactly `mip_repo_execution_state_v2`. Validate all
required strings, paths, SHA fields, booleans, and nullability before access.
Malformed or missing fields must produce deterministic resolver reason codes,
not `KeyError`, uncaught Git errors, or permissive continuation.

### C. Main-pointer to branch-state transition matrix

Implement this explicit matrix. Any unlisted transition fails closed.

| Main pointer | Branch state | Resolver outcome | Required branch authority |
|---|---|---|---|
| `authorized` | `authorized` | executable | `task_execution_authorized=true` |
| `authorized` | `in_progress` | executable | `task_execution_authorized=true` |
| `authorized` | `blocked` | executable only when resumption is authorized | task or correction authorization true |
| `authorized` | `changes_requested` | executable correction | `correction_execution_authorized=true` |
| `authorized` | `ready_for_review` | review-only; stay on main | valid implementation SHA; merge/PR false |
| `ready_for_review` | `ready_for_review` | review-only; stay on main | valid implementation SHA; merge/PR false |
| `blocked` | `blocked` or `in_progress` | executable only when authorized | task or correction authorization true |
| `changes_requested` | `changes_requested` or `in_progress` | executable correction | `correction_execution_authorized=true` |
| `changes_requested` | `ready_for_review` | review-only; stay on main | valid implementation SHA; merge/PR false |

For `idle`, `proposed`, `merged`, and `superseded` on main, validate main human
views, remain on main, and do not fetch or select a feature branch.

### D. Main/branch invariant matrix

The following must agree exactly between main pointer and branch state:

- `schema_version`;
- `repository`;
- `task_id`;
- `execution_mode`;
- `base_branch` and `base_sha`;
- `authorization_head_sha`;
- `feature_branch`;
- `task_path` and `completion_report_path`;
- `affected_repositories` when present;
- sibling-adoption and owner-boundary flags when present;
- `capability_authorizations_changed`.

The following may evolve only according to the transition matrix:

- `status`;
- `task_execution_authorized`;
- `correction_execution_authorized`;
- `blockers`;
- `implementation_commit_sha`.

The following may never be escalated by the feature branch during execution,
correction, or review publication:

- `merge_authorized` must remain `false`;
- `pr_creation_authorized` must remain `false`;
- `reviewed_head_sha` must remain `null` before merge closure;
- `approval_commit_sha` must remain `null`;
- capability and sibling adoption authority must remain unchanged/false.

### E. Implementation identity

For `ready_for_review`, require one forty-character lowercase hexadecimal
`implementation_commit_sha` that exists as a commit, is ancestral to the exact
remote branch head, and is named consistently in execution state, active task,
and completion report. Earlier commits are historical lineage only.

### F. Existing local branch behavior

When the local feature branch exists, do not silently accept or overwrite it.
After switching, require local `HEAD` to equal the exact fetched remote branch
head. A stale, ahead, or diverged local feature branch fails with an actionable
reason code.

## Required test matrix

The completion report must map every ID below to an exact test name. Passing test
counts without this one-to-one mapping are insufficient.

- **R01** authorized task resolves and checks out exact remote branch.
- **R02** authorized main → branch `in_progress` resolves.
- **R03** main authorized → branch-only `changes_requested` resumes with explicit correction authority.
- **R04** main authorized → branch-only `blocked` resumes only with applicable authority.
- **R05** `ready_for_review` stays on main and validates one real ancestral implementation SHA.
- **R06** `idle`, `proposed`, `merged`, and `superseded` stay on main after human-view validation.
- **R07** wrong origin fails.
- **R08** execution-state repository identity mismatch fails separately from wrong origin.
- **R09** dirty tracked worktree fails.
- **R10** unexpected untracked path fails; `.codex/` and `docs/tasks/` are permitted.
- **R11** clean behind-main state fast-forwards; diverged main fails.
- **R12** missing remote feature branch fails.
- **R13** authorization head missing, malformed, nonexistent, or non-ancestral fails reason-coded.
- **R14** main/branch task, base, branch, or authorization-head mismatch fails.
- **R15** branch merge, PR, capability, sibling-adoption, or other invariant authority escalation fails.
- **R16** unsupported main-to-branch lifecycle transition fails.
- **R17** nonexistent implementation SHA fails.
- **R18** non-ancestral implementation SHA fails.
- **R19** duplicate or contradictory current status in `ACTIVE_TASK.md` fails.
- **R20** duplicate or contradictory current decision in the completion report fails.
- **R21** contradictory merged closure prose on synchronized main fails.
- **R22** stale task text in the context index is ignored for task/branch selection.
- **R23** existing local feature branch with nonmatching remote head fails.
- **R24** malformed required field produces a resolver reason code rather than an uncaught exception.
- **R25** coordination test validates semantic current-state agreement without hard-coding a historical task identity.

## Owned-path and requirement closure gate

Before publication:

1. Compare the complete branch diff with the ten authorized paths and fail on any
   extra path.
2. Confirm every required test ID R01-R25 is mapped to and exercised by at least
   one exact test.
3. Confirm no acceptance criterion requires an unowned path.
4. Confirm all named owned paths exist at the final tree.

## Validation and publication

Run on the exact final implementation tree:

- resolver tests and R01-R25 mapping check;
- relevant execution-handoff, documentation, and coordination governance tests;
- JSON parsing and current-state Markdown checks;
- exact owned-path verification;
- Ruff for changed Python files;
- configured mypy for the resolver/test surface;
- `git diff --check`;
- Docker-backed full `make validate`.

On success, publish `ready_for_review` with one final implementation-tree SHA,
empty blockers, task execution authorization false, correction execution
authorization true only as required for the review branch, merge and PR false,
reviewed and approval SHAs null, and unchanged capability authority. Push the
exact remote head and stop.

On incomplete validation or unresolved requirements, publish an accurate
`blocked` state with exact debt, push, and stop.

Do not create a PR, merge, rebase, squash, force-push, delete branches, modify
siblings, or authorize any capability.

## Follow-on task boundary

After this resolver task is merged and closed, recommend but do not authorize:

`MIP_EXECUTION_TASK_AUTHORING_PREFLIGHT_001`

That separate task will own requirement-to-path closure, a machine-readable task
contract, automatic owned-path enforcement, lifecycle/invariant matrices,
numbered test-evidence coverage, path-existence checks, normalized human views,
and a bounded correction-loop policy. It must be proven on one narrow MIP task
before any MMM or GeoX adoption is proposed.
