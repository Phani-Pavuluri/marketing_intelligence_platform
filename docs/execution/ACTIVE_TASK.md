# Active Task

**Status:** ready_for_review
**Owner:** MIP program governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `MIP_ACTIVE_TASK_CONTEXT_RESOLVER_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `main` / `d35fbbb82711b073c3504d5cc0f1b807e9b36c81`
- **Feature branch:** `feat/mip-active-task-context-resolver-001`
- **Execution mode:** `branch_and_fast_forward`
- **Observed MMM main:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Observed GeoX main:** `ee9673c13e69082367c1727568946ac4c1a01015`
- **Capability authorizations changed:** `false`
- **Implementation commit:** `18f7ffdd5b3ef20af4cea177047c11f5ffadd8f0`

## Purpose

Implement the MIP-owned canonical active-task resolver and simplify the
repository-native execution handoff so a fresh or resumed agent selects the
correct remote task branch before reading branch-specific task instructions.
The resolver must replace manual task discovery, not analytical or product
logic.

This task addresses the verified workflow failures from the completed
coordination work: branch-dependent `ACTIVE_TASK.md` discovery, duplicated
current-state prose, nonexistent or ambiguous implementation SHAs, and tests
that couple unrelated work to literal task IDs rather than semantic execution
invariants.

## Current evidence and non-overlap

MIP prior task `MIP_COORDINATION_POST_MERGE_CLOSURE_RECONCILIATION_001` is merged
and closed at current MIP `main`
`d35fbbb82711b073c3504d5cc0f1b807e9b36c81`; execution authorization is false.
Its completion report retains contradictory pre-merge and merged current-state
claims, which this task must eliminate by replacing the stable files and adding
mechanical consistency rules.

MMM is merged with no active implementation task at
`1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`. GeoX has the separately authorized
producer-owned task `GEOX_GOVERNED_READOUT_BUILDER_PACKAGE_ENTRYPOINT_001` at
`ee9673c13e69082367c1727568946ac4c1a01015`. This MIP task neither modifies nor
blocks that work.

No existing MIP resolver implementation or authorized resolver task was found at
task authorization. The completed implementation is recorded below.

## Owned files

Execution may modify only:

- `AGENTS.md`
- `Makefile`
- `scripts/resolve_active_task.py`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`
- `tests/test_active_task_context_resolver.py`

Do not modify MIP runtime, contracts, adapters, fixtures, orchestration, UI,
analytical code, roadmap/program coordination files, MMM, or GeoX.

## Task-authoring boundary

The pre-authoring base is
`d35fbbb82711b073c3504d5cc0f1b807e9b36c81`. Task authoring may change only
`ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md`; one immediately following
state-only commit may change only `EXECUTION_STATE.json` to record the exact
authorization head. Create the feature branch from that synchronized state-only
commit. Stop on any other intervening path or commit.

## Required implementation

### 1. Repository-authored resolver

Add `scripts/resolve_active_task.py` and `make resume-active-task`. From a
synchronized MIP checkout, the command must deterministically:

1. verify repository root and exact `origin` identity;
2. classify the worktree and allow local-only untracked content only below
   `.codex/` and `docs/tasks/`;
3. fetch and prune `origin` and hydrate required history;
4. synchronize local `main` with `origin/main` using fast-forward-only behavior;
5. read the canonical pointer branch-independently from
   `origin/main:docs/execution/EXECUTION_STATE.json` before reading
   `ACTIVE_TASK.md`;
6. validate schema, task ID, status, authorization booleans, feature branch,
   authorization head, repository identity, and allowed lifecycle transition;
7. fetch the exact remote feature branch when the state is resumable;
8. verify the branch descends from the authorization head and that its branch
   execution state agrees with the main pointer on repository, task ID, branch,
   and authority;
9. switch to the exact remote-backed branch and prove local `HEAD` equals the
   remote branch head before permitting task instruction reads; and
10. emit a deterministic human-readable and machine-readable resolution summary.

Fail closed on wrong repository/origin, dirty or unexpected worktree, stale or
diverged main, missing history, missing branch, ancestry failure, task mismatch,
unauthorized execution, invalid status, inconsistent state, or local/remote head
mismatch. Never guess a branch or silently create one.

For non-executable states (`idle`, `proposed`, `merged`, or `superseded`), remain
on synchronized `main`, report the state, and stop without selecting a feature
branch. `ready_for_review` must be reported as review-only rather than executable.
`blocked` or `changes_requested` may resume only when the applicable execution or
correction authorization is explicitly true.

### 2. Canonical state and derived prose rules

Make `docs/execution/EXECUTION_STATE.json` the sole mutable machine-readable
current-task pointer. `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md` remain
human-readable task and evidence views, but must be mechanically checked against
state rather than treated as independent current-state authorities.

Define and enforce:

- exactly one current status/decision in each human-readable stable file;
- historical review or rejection evidence is explicitly labeled historical and
  cannot be parsed as current state;
- closure replaces or normalizes review-era current claims rather than merely
  appending contradictory merged prose;
- the repository context index points to canonical sources and never has to
  repeat the current task ID;
- stale context-index prose cannot block an unrelated authorized task;
- current task identity and branch selection come only from execution state.

### 3. Exact implementation identity

Define `implementation_commit_sha` as the single final implementation-tree
commit immediately before review-state metadata publication. Earlier commits may
be retained only as historical lineage. Before `ready_for_review`, validate that
the SHA:

- is exactly forty hexadecimal characters;
- exists as a commit object;
- is an ancestor of the exact remote review head; and
- is named consistently in execution state, active task, and completion report.

String length alone is insufficient.

### 4. Bootstrap integration

Update `AGENTS.md`, the execution standard, and the context index so agents:

1. synchronize `main` without reading branch-specific task prose;
2. run `make resume-active-task`;
3. read `ACTIVE_TASK.md` only after resolver success and branch proof; and
4. stop on non-executable, review-only, merged, or contradictory state.

Keep Codex prompts minimal because durable instructions remain in Git.

### 5. Semantic tests

Add isolated deterministic tests using temporary local Git repositories and bare
remotes. Cover at minimum:

- successful authorized-task resolution and exact branch checkout;
- merged/no-active-task behavior;
- `ready_for_review` review-only behavior;
- authorized correction resumption;
- wrong origin/repository;
- dirty tracked and unexpected untracked paths;
- permitted `.codex/` and `docs/tasks/` local-only paths;
- stale/diverged main;
- missing remote branch;
- authorization-head ancestry failure;
- main/branch task or authority mismatch;
- nonexistent implementation SHA;
- implementation SHA not ancestral to review head;
- duplicate or contradictory current decisions in Markdown;
- stale context-index task text not being used for branch selection.

Tests must validate semantics and Git objects, not require the current task ID to
appear in every document.

## Acceptance criteria

- `make resume-active-task` resolves the exact remote task branch from
  `origin/main` state before branch-specific instruction reads.
- Wrong-repository, stale-state, ancestry, ownership, and authority conflicts
  fail closed with actionable reason codes and nonzero exit status.
- Merged and review-only states never trigger execution.
- Execution state is the sole machine current-state pointer.
- Human-readable stable files cannot contain multiple current decisions.
- One real, ancestral implementation SHA is required for review.
- Context-index staleness cannot block unrelated task execution.
- No sibling repository, product code, capability, or analytical truth changes.

## Validation gate

Run on the exact implementation tree:

- focused resolver and execution-handoff tests;
- all relevant documentation/governance tests;
- resolver scenario tests against temporary Git repositories;
- JSON parsing and Markdown/current-state consistency checks;
- exact changed-path verification;
- Ruff on every changed Python file;
- configured mypy for the resolver surface;
- `git diff --check`;
- Docker-backed full `make validate`.

If the complete gate cannot finish successfully, publish an accurate `blocked`
state with exact validation debt. Focused success cannot hide full-suite debt.

## State transitions

On success, publish `ready_for_review` with one real
`implementation_commit_sha`, empty blockers, task execution authorization true,
merge and PR authorization false, reviewed and approval SHAs null, unchanged
capability authority, and the exact remote branch head reported separately.

On failure, publish `blocked` with specific blockers and evidence, commit and
push the exact branch head, and stop.

Do not create a PR, merge, squash, rebase, force-push, delete branches, or modify
MMM or GeoX during execution.

## Execution result

The sole implementation commit is `18f7ffdd5b3ef20af4cea177047c11f5ffadd8f0`.
It adds `make resume-active-task` and `scripts/resolve_active_task.py`, updates
the bootstrap/source-of-truth documentation, and adds isolated temporary-Git
semantic tests. The resolver selects only the exact remote-backed authorized
branch from `origin/main` state, reports review-only/non-executable states
without branch selection, and fails closed on repository, worktree, state,
authority, ancestry, implementation-identity, or human-view disagreement.

The branch is `ready_for_review`. Task execution authorization remains true for
review; merge and PR authorization remain false; reviewed and approval SHAs
remain null; capability authorizations remain unchanged. MMM and GeoX were not
modified, their adoption remains unauthorized, and the GeoX builder remains
unmodified and unblocked.

## Deferred owner-repository adoption

This task defines and stabilizes the MIP canonical resolver behavior only. It
does not authorize MMM or GeoX adoption. After this task is merged and closed:

- MMM may combine coordination-protocol and resolver adoption in one separately
  authorized MMM task;
- GeoX may do the same only after its active builder task is merged and closed;
- each repository must resolve its own `origin/main` and its own feature branch;
- MIP must not mutate sibling branches or override sibling execution state.

## Prohibited authority

This task does not authorize live engine integration, real data, uploads,
persistence, scheduling, simulation, optimization, recommendations, treatment
assignment, LLM decisioning, pilot, production, or package-side agents.
