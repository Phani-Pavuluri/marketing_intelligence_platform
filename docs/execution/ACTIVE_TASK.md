# Active Task

**Status:** ready_for_review
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_LEAN_REPOSITORY_DELIVERY_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `70bd688b2506ca0bb3cb572dd00552bf10f1e9b8`
- **Task-authoring head:** `845d4bea477df7514128548193cbb942e04c20dc`
- **State authorization commit:** `aa74f576d0515e0289df25cef461fe118649c4b0`
- **Implementation commit:** `25d254a20a0eca75094c0b4a4d7e5cd23944e55c`
- **Feature branch:** `docs/mip-lean-repository-delivery-standard-001`
- **Execution mode:** `branch_and_fast_forward`
- **Capability authorizations changed:** `false`

Execution is authorized by the state-only commit above. A subsequent metadata-only
consistency correction aligns this human task view and the completion report with
`EXECUTION_STATE.json`. Before implementation, the untouched feature branch must
be fast-forwarded to the corrected synchronized `main`. This correction does not
change task scope, ownership, validation tier, or authority.

## Delivery shape

- **Primary mergeable outcome:** establish one concise MIP-owned program standard
  for small, risk-tiered, repository-native delivery and make it mandatory for
  future MIP task authoring.
- **Risk tier:** Tier 1 — documentation and governance guidance only.
- **Why it cannot be split further:** the program rule, MIP bootstrap pointer,
  repository execution guidance, and navigation pointer form one documentation
  contract; none creates an independent runtime or analytical capability.
- **Expected substantive commits:** one documentation implementation commit and
  one review-publication commit.
- **Deferred successor work:** any automated preflight, resolver reimplementation,
  MMM adoption, and GeoX adoption.

## Purpose

Create a lightweight project-wide delivery standard that preserves Git
authority, ownership, exact-head review, validation, and cross-repository trust
while preventing oversized tasks, long-lived branches, and repeated governance
correction loops.

The standard is MIP-owned program guidance. It does not modify or override live
MMM or GeoX execution state. Sibling adoption requires separately authorized
owner-repository tasks after MIP proves the standard on real work.

## Owned paths

Execution may modify only:

1. `AGENTS.md`
2. `docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md` (new)
3. `docs/execution/TASK_EXECUTION_STANDARD.md`
4. `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
5. `docs/execution/ACTIVE_TASK.md`
6. `docs/execution/EXECUTION_STATE.json`
7. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify resolver code, tests, Makefiles, product/runtime/analytical code,
contracts, adapters, fixtures, orchestration, UI, coordination snapshot/history,
MMM, or GeoX.

## Required result

### 1. Concise program standard

Create `docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md` defining:

- one authorized task equals one independently reviewable and mergeable outcome;
- internal checkpoints that produce valid standalone evidence become separate
  merge boundaries;
- Tier 1 routine, Tier 2 public-contract/package, and Tier 3 cross-repository or
  decision-authority validation;
- the non-negotiable controls retained at every tier;
- a one-correction-cycle default followed by re-scope when review reveals a new
  contract, migration, integration surface, or independently mergeable outcome;
- warning triggers such as multiple public surfaces, contract plus migration,
  product plus governance repair, several meaningful checkpoints, or a branch
  growing beyond a small review unit;
- Git history rather than duplicated current prose as the record of prior states;
  and
- MIP proof before separately authorized MMM or GeoX adoption.

Keep the standard operational and brief. Do not design a new workflow product or
machine task schema.

### 2. Minimal task-authoring shape

Update `TASK_EXECUTION_STANDARD.md` so each future MIP task declares only:

- primary mergeable outcome;
- risk tier;
- why it cannot be split further;
- owned paths;
- focused validation; and
- deferred successor tasks.

Require task authors to stop and split work when a meaningful portion can be
validated and merged independently.

### 3. Bootstrap and navigation

Add a short mandatory pointer in `AGENTS.md` and add the program standard to
`REPOSITORY_CONTEXT_INDEX.md`. Do not duplicate the full standard in either
file.

### 4. Explicit exclusions

This task does not implement automated task preflight, task-decomposition
inference, new execution-state fields, sibling adoption, resolver corrections,
coordination-ledger changes, or product capability.

## Acceptance criteria

- One canonical lean-delivery standard exists under `docs/program/`.
- Future MIP tasks are required to declare one mergeable outcome and a risk tier.
- The standard distinguishes Tier 1, Tier 2, and Tier 3 validation without
  weakening analytical or authority controls.
- Independently useful checkpoints are required to become merge boundaries.
- One correction cycle is the default before structural re-scope.
- `AGENTS.md` and the context index point to, rather than duplicate, the standard.
- No automation, resolver, sibling, product, analytical, or capability change is
  included.

## Validation gate

This is an explicitly authorized narrow docs-only gate. Run:

- JSON parsing for `EXECUTION_STATE.json`;
- Markdown structure and referenced-path existence checks;
- exact changed-path verification against the seven owned paths;
- `git diff --check`; and
- any existing focused documentation/governance consistency test directly
  affected by these files.

Ruff, mypy, Docker, and the full repository test suite are not required because
no executable Python, package, contract, fixture, or runtime file is owned. If a
changed path or repository rule unexpectedly requires executable validation,
publish `blocked` rather than expanding scope silently.

## Publication

On success, publish `ready_for_review` with one real implementation commit SHA,
empty blockers, merge and PR authorization false, and unchanged capability
authority. Push the exact branch head and stop.

On failure, publish `blocked` with exact debt. Do not create a PR, merge, rebase,
squash, force-push, delete branches, modify siblings, or authorize adoption.

## Publication state

The implementation is ready for exact-head review. The review-publication
commit contains only stable execution metadata and the completion report. Merge
and PR creation remain unauthorized; no capability authority changed.
