# Active Task

**Status:** authorized
**Task ID:** `MIP_EXECUTION_LIFECYCLE_SINGLE_SOURCE_CONSISTENCY_001`
**Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
**Local path:** `/Users/phani/Desktop/marketing_intelligence_platform`
**Pre-authoring base:** `4a392c7ecf7b421dae9fbd11e50eed01c168efa9`
**Authorization provenance:** `e1839bcfad482b2f79343202ac68d25a666acc42`
**Feature branch:** `feat/mip-execution-lifecycle-single-source-consistency-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 2 — repository execution-governance state machine
**Compatibility / migration policy:** `in_place_mip_execution_metadata_migration_v1`
**Task execution authorized:** `true`
**Merge / PR authorized:** `false`
**Unresolved execution-blocking design questions:** none

## Primary outcome

Establish one MIP-owned source of truth for mutable repository execution lifecycle
state and a deterministic control tool that renders and validates all duplicated
human-readable execution views from that state.

Today the same mutable facts can be independently edited in
`EXECUTION_STATE.json`, `ACTIVE_TASK.md`, `LATEST_COMPLETION_REPORT.md`, and
executor/action handling. That permits status, blocker, correction-cycle,
authorization, implementation/review SHA, and closure evidence to drift. This
milestone removes that class of ambiguity inside MIP without changing product,
analytical, P2, GeoX, or MMM numerical behavior.

This is one independently reviewable outcome because the canonical state model,
view renderer/checker, and lifecycle transition command are one control surface:
shipping only one of them would still permit divergent execution evidence.

## Scheduling prerequisite

The scheduling prerequisite is satisfied. Live GeoX `origin/main` at
`5ab881296c7c8248076bad61292b255aaade11d8` records
`GEOX_D5_POWER_CONTROL_GEOMETRY_REPAIR_002` as merged and closed. Its closure
evidence records externally approved review head
`9d17ad44f3a8cb860dfed36af860487c0877d12b` and implementation commit
`5a7b9ff9faecb50a28bab63688c9a53594fa733f`.

This is a temporary execution-governance detour. It does not alter the P2
capability sequence or authorize GeoX certification, MMM fixtures, the parked MIP
bridge, D6, planning, or any analytical/runtime capability.

## Canonical ownership model

Implement the following model exactly:

1. `docs/execution/EXECUTION_STATE.json` is the sole mutable source for lifecycle
   facts: status, blockers, execution/correction/merge/PR authority, correction
   counters, feature-branch identity, implementation/review/rejected/approval
   SHAs, cleanup state, and lifecycle decision.
2. `ACTIVE_TASK.md` remains the human-authored task contract. Mutable lifecycle
   facts shown there must live only inside an explicitly generated execution-view
   block rendered from `EXECUTION_STATE.json`; the contract body must remain
   untouched by synchronization.
3. `LATEST_COMPLETION_REPORT.md` remains evidence/reporting, not authority.
   Any lifecycle snapshot it displays must be inside an explicitly generated
   block rendered from the canonical state. Validation narrative remains
   human-authored evidence.
4. Repository execution must fail closed when the canonical state is invalid or
   either generated view differs from the deterministic rendering.
5. The external exact-head approval rule remains unchanged: approval is not
   persisted into the reviewed tree and no `approved_for_merge` state is added.

Do not create a second machine-authoritative lifecycle file.

## Deterministic lifecycle control

Add an MIP-owned execution-governance module under `src/mip/execution/` with a
module entry point callable as:

```bash
python -m mip.execution.taskctl check
python -m mip.execution.taskctl sync
python -m mip.execution.taskctl transition --to <status> [transition evidence]
```

Exact CLI details may be split into internal helpers, but observable behavior
must satisfy:

### `check`

- parses and validates the canonical JSON state;
- enforces the allowed V2 status vocabulary and status-specific invariants;
- validates SHA/null requirements, blockers, correction counters, authority
  booleans, feature-branch identity, and closure fields;
- renders the expected generated blocks in memory and requires byte-equivalent
  generated blocks in `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md`;
- exits nonzero with typed/stable reason codes for every mismatch category;
- never repairs files.

### `sync`

- validates canonical state first;
- deterministically replaces only the generated execution-view blocks in
  `ACTIVE_TASK.md` and `LATEST_COMPLETION_REPORT.md`;
- preserves every byte outside those blocks;
- is idempotent: a second run produces no diff;
- refuses files with missing, duplicated, nested, or malformed generated markers;
- never changes canonical state.

### `transition`

- validates the current state and current generated views before mutation;
- permits only declared lifecycle transitions;
- applies status-specific required evidence and invariants;
- updates canonical state first in memory, renders both views from that candidate,
  validates the complete candidate set, then writes the three candidate files;
- rejects impossible or incomplete transitions instead of partially updating
  lifecycle evidence;
- must not silently infer implementation/review SHAs, blockers, authorization,
  correction counts, or external approval.

The first implementation must support the repository's existing V2 states:
`idle`, `proposed`, `authorized`, `in_progress`, `blocked`,
`ready_for_review`, `changes_requested`, `merged`, and `superseded`.
`approved_for_merge` remains forbidden.

## Required transition/invariant coverage

At minimum, encode and test these rules:

- `proposed` is non-executable.
- `authorized` requires task execution authority, no blockers, and no
  implementation/review/approval SHA.
- `blocked` requires a non-empty blocker set and must not claim review/merge.
- `ready_for_review` requires an implementation SHA, no blockers, no reviewed or
  approval SHA, and merge authority remains false.
- `changes_requested` requires exact rejected-review provenance and correction
  budget semantics; correction authority must be explicit.
- `merged` requires execution authority false, merge authority false, a reviewed
  head, implementation lineage, no blockers, and closure/cleanup semantics
  consistent with repository policy.
- correction-cycle values have one representation and must satisfy
  `completed + remaining == maximum` whenever a bounded budget applies.
- no lifecycle transition may grant product, analytical, sibling, P2, pilot, or
  production capability authority.

Use a declared transition table/state machine rather than scattered conditionals
whose meanings can drift.

## Action / agent integration

Update `AGENTS.md` and `TASK_EXECUTION_STANDARD.md` so future executor/action
flows:

- read canonical lifecycle state from `EXECUTION_STATE.json`;
- use `taskctl check` during bootstrap/resumption and before publication;
- use `taskctl transition` for lifecycle changes rather than manually editing
  the same mutable fields in multiple files;
- use `taskctl sync` only to regenerate derived views after an authorized
  canonical-state change;
- fail closed if task contract, canonical state, remote branch, or generated
  views disagree.

The invocation-only prompt model remains unchanged.

## Current-state migration

Migrate the MIP execution files to generated-view markers without changing the
meaning of the active task being executed on the feature branch.

The migration must prove:

- canonical JSON carries every mutable lifecycle fact needed by the generated
  views;
- no mutable lifecycle fact has two independent machine-authoritative values;
- `taskctl sync` on a clean migrated tree is a no-op;
- `taskctl check` passes the clean migrated tree;
- a deliberately corrupted generated status, blocker, correction counter, or
  SHA is detected deterministically.

Do not migrate GeoX or MMM in this milestone.

## Owned implementation paths

- `AGENTS.md`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `src/mip/execution/`
- `tests/execution/`
- lifecycle updates to the three stable execution files required by the active
  task workflow

Do not modify P2/program ledgers, product code, analytical contracts, adapters,
LLM behavior, GeoX, MMM, CI, git hooks, Docker configuration, or capability
authority. Do not create a cross-repository shared runtime dependency.

## Acceptance tests

Add focused tests proving at least:

1. all allowed states and transition edges are table-driven and deterministic;
2. invalid status/evidence combinations fail with stable reason codes;
3. divergent `ACTIVE_TASK` status from canonical state fails `check`;
4. divergent completion-report blocker/correction/SHA snapshot fails `check`;
5. `sync` repairs only generated blocks and preserves contract/report bodies;
6. repeated `sync` is byte-idempotent;
7. `transition` cannot publish `ready_for_review` without implementation
   evidence or while blockers remain;
8. `changes_requested` correction-budget invariants reject the historical class
   of counter mismatch;
9. `merged` closure invariants reject reviewed-head/authority/cleanup
   contradictions;
10. a migrated clean MIP execution tree passes `check`;
11. no command changes product/analytical/capability authority.

## Validation

On the frozen candidate tree run:

```bash
python -m json.tool docs/execution/EXECUTION_STATE.json
pytest -q tests/execution
ruff check src/mip/execution tests/execution
mypy src/mip/execution
git diff --check
make validate
```

Also inspect the full diff and prove implementation changes remain inside owned
paths plus required lifecycle publication files. Record exact results and
not-run categories in the completion report.

## Deferred successors

After this MIP control is merged:

1. `GEOX_EXECUTION_LIFECYCLE_SINGLE_SOURCE_ADOPTION_001` — GeoX-owned adoption,
   required before authorizing the next GeoX baseline-repair milestone.
2. Resume GeoX baseline repair beginning with the then-live eligible successor
   (historically `GEOX_TBR_RECOVERY_CONTRACT_ALIGNMENT_001`) only after GeoX
   adoption passes.
3. `MMM_EXECUTION_LIFECYCLE_SINGLE_SOURCE_ADOPTION_001` — MMM-owned adoption
   before MMM's next P2 implementation task.
4. Any CI/git-hook enforcement or richer prompt-generation automation remains a
   separate milestone.

No successor is authorized by this task.

## Git workflow

When this task is later authorized, create `feat/mip-execution-lifecycle-single-source-consistency-001` only from the
synchronized authorization baseline. Commit and push the exact feature branch,
publish only `ready_for_review` or a genuine Git-durable `blocked` state, and
stop for external exact-head review.

No PR, merge, squash, rebase, force-push, merge commit, or sibling modification
is authorized during implementation.
