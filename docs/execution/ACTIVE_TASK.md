<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** merged

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_DECISION_EVIDENCE_GAP_REGISTER_PROPOSAL_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `fa930ad6e6524a462c45dea122987ffc88b7dc4c`
- **Authorization provenance:** `d8dad41de11869b1611285c32dbc673d09658e71`
- **Feature branch:** `docs/mip-decision-evidence-gap-register-proposal-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `f98d8cbad654090047375b638961796c86766eb8`
- **Reviewed head:** `42c53328336915e7c93b18fa463256206cb4187f`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `merged`
- **Local feature-branch cleanup:** `observed_deleted`
- **Remote feature-branch cleanup:** `observed_deleted`
- **Capability authorizations changed:** `false`
<!-- END MIP TASKCTL EXECUTION VIEW -->

## Primary outcome

Publish one Git-authoritative, Tier 1 documentation-only proposal that:

1. Classifies the stale `docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md` as
   historical with a header-only change (no restructure, no rename),
   resolving the known P2 phase-name collision with precise retire-vs-retain
   scope; then
2. Inserts the Decision-Evidence Gap Register (rows DE-0 through DE-11) as a
   reviewed, explicitly non-authorizing proposal section in the canonical
   `docs/roadmap/ROADMAP.md`, with every row `unchecked` / `not_eligible`
   and authority impact `none` throughout at insertion.

Classification is the first-commit boundary: it lands first on the feature
branch and is verified before any register insertion. The rename stays a
separate successor and is not bundled into the classification commit.

## Why this is one independently reviewable outcome

The collision context and the register content must be reviewed together: the
classification commit states precisely which P2 meaning is retired versus
retained, and the register insertion is only legible against that resolved
namespace. Classification alone would leave the roadmap mid-sentence with no
register to justify the retained meanings; insertion alone would land rows
into a collided namespace. The rename, DE-0 design, archive moves, schema
adoption, sequencing work, the Tier-1 runner, and AGENTS changes are each
separately reviewable and are split off as successors below.

## Register objective and core rule

Objective: a governed register (DE-0 estimand protocol through DE-11 provider
evaluation) identifying where MIP needs measurement and experimentation
evidence before future planning decisions. Goal is bounded proof — more
calibrated, reproducible, transparent, safer evidence under declared
conditions — never a claim of universally best MMM.

Core rule: evidence completion never grants authority. No spend,
optimization, recommendation, real-data use, pilot, production, promotion, or
runtime integration follows from any row without a separate authority task
and gate.

## Entry discipline

- Register proposal first, all rows unchecked.
- DE-0 gets its own design task with named acceptance before DE-1/DE-3
  criteria finalize.
- Scanner (DE-6) and handoff contract (DE-7) after.
- Comparators and controlled outcomes only when gates permit.
- Ops and LLM lanes stay supporting.

## Row requirements

Every row carries: ID, bounded claim, phase plus governing gate, owning team,
entry condition, named evidence artifact, acceptance authority, acceptance
SHA (empty at insertion), version scope with re-verification triggers,
status from the controlled vocabulary (`unchecked` / `not_eligible` at
insertion), and authority impact defaulting to `none`. No producer
self-acceptance: the accepting authority is never the row's producing team.

## DE-3 upstream citation (known gap, not built)

DE-3's full-pipeline certification path records the known MMM-side gap as
cited context: producer inputs exist (replay calibration compatibility,
supported-range evidence, synthetic recovery worlds, calibration lineage),
but MMM has no deterministic Tier-1 batch runner — its authoring attempt
ended in an honest blocked receipt. Citing it is this task's work; building
the runner is not, and must not leak in.

## Tracked constraints carried into this task

- The `369805d` SHA may be cited in task or register text only after
  verification against live Git on both sides. It is currently a one-sided
  citation: the MIP tree contains no reference to it, so no bilateral
  coordination claim may rest on it until explicit Git evidence exists on
  both sides.
- The classification commit must state precisely which P2 meaning is retired
  versus retained: (a) canonical P2 certified planning evidence lifecycle in
  `ROADMAP.md` — retained; (b) legacy Phase 2 Reliability-First MMM
  Foundation in `ROADMAP.md` — retired to historical; (c) execution-sequence
  P2 (I3 required data assets) in `ROADMAP_EXECUTION_SEQUENCE.md` — retired
  to historical; (d) program-file working usage (fixture-only cross-repository
  tranche) — retained as working usage, not roadmap authority.

## Authoring evidence

Task authoring observed clean synchronized MIP `origin/main` at
`fa930ad6e6524a462c45dea122987ffc88b7dc4c` with
`poetry run python -m mip.execution.taskctl check` passing. No sibling
evidence is required: this task neither reads nor writes MMM or GeoX, and no
coordination-state refresh is authorized. The prior merged audit
(`MIP_GEOX_MMM_PENDING_WORK_AND_LLM_DEPENDENCY_AUDIT_001`) and the program
P2 ledger remain background context, not dependencies.

## Inputs, outputs, invariants, and failure semantics

- **Inputs:** the two roadmap documents at the finalized authorization
  baseline, plus this Git-authored contract.
- **Output:** only the header-only classification of
  `docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md` and the register proposal
  section in `docs/roadmap/ROADMAP.md`, plus the required MIP lifecycle
  publication updates.
- **Invariants:** proposal-only and non-authorizing; every row unchecked at
  insertion; authority impact none; Git authority and repository ownership
  preserved; no product, analytical, capability, ledger, coordination-state,
  or runtime behavior changes.
- **Compatibility/migration:** `not_applicable`; no API, schema, state
  machine, persisted artifact, version, or migration changes.
- **Failure semantics:** any checked row at insertion, any bundled rename or
  restructure, any widened classification diff, any sibling write, any
  capability-authority change, or inability to run the Tier 1 gate must fail
  closed. If a safe authorized branch exists at execution time, publish a
  durable `blocked` state with exact evidence and a live resolution
  condition.

Unresolved execution-blocking design questions: none.

## Owned paths

Implementation may change only:

- `docs/roadmap/ROADMAP.md` (register proposal section only)
- `docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md` (header-only historical classification only)
- `docs/execution/EXECUTION_STATE.json`
- the generated lifecycle block in `docs/execution/ACTIVE_TASK.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The stable execution files are lifecycle publication paths, not additional
deliverables.

## Prohibited scope

Do not bundle the rename; move archives; adopt schemas; resequence
`panel_exp`/MIP work; build the Tier-1 runner; change `AGENTS.md`;
modify GeoX or MMM in any way; authorize or execute sibling tasks; alter
product or analytical truth; construct `CalibrationSignal`; run calibration,
fitting, simulation, or optimization; resume the parked MIP bridge; change P2
capability semantics; modify LLM prompts, providers, or runtime behavior;
change packages, contracts, schemas, fixtures, code, tests, CI, hooks, or
Docker; alter roadmaps beyond the two owned surfaces; touch ledgers,
coordination state, or repository standards; use real or customer data;
create persistent product artifacts; make recommendations; authorize pilot,
production, promotion, or runtime integration; modify any
capability-authority flag; or create a PR, merge, squash, rebase,
force-push, cherry-pick, or merge commit outside the repository's allowed
`branch_and_fast_forward` flow.

## Acceptance evidence

The completed proposal and report must prove:

1. the classification diff is header-only with no restructure or rename;
2. the retire-vs-retain statement names all four P2 meanings precisely;
3. every register row DE-0 through DE-11 is present and `unchecked` /
   `not_eligible` with authority impact `none` and empty acceptance SHA;
4. no row is producer self-accepted;
5. entry discipline (DE-0 first, DE-6/DE-7 after, gated comparators,
   supporting ops/LLM lanes) is stated in text;
6. DE-3 cites the MMM upstream gap without building it;
7. `369805d` is cited only if verified against live Git, otherwise absent;
8. no sibling path changed and no coordination state was refreshed; and
9. changed paths are limited to the owned paths.

## Validation

On the frozen exact implementation tree run and record:

```bash
poetry run python -m mip.execution.taskctl check
python3 -m json.tool docs/execution/EXECUTION_STATE.json >/dev/null
git diff --check
git diff --name-only <authorization-head>...HEAD
```

Also perform a manual review of every row status, SHA field, path, and the
retire-vs-retain statement; verify local/remote branch-head equality; and
classify each validation category as `passed`, `failed`, `blocked`, or
`not_required`. Tier 1 uses this focused documentation gate; Docker-backed
`make validate` is `not_required` (no code, contract, package, analytical,
or runtime surface changes).

## Deferred successors

Deliberately not in this task: DE-0's own estimand-protocol design task with
named acceptance; the rename of the stale sequence doc; any archive moves;
schema adoption; `panel_exp`/MIP sequencing work; the Tier-1 runner;
`AGENTS.md` changes; and any execution, authorization, or capability claim
flowing from any register row. The register may sequence future evidence work
but must not pre-authorize or silently define those tasks.

## Git workflow and stop condition

This task is authorized for execution on
`docs/mip-decision-evidence-gap-register-proposal-001` from the exact
finalized synchronized authorization baseline: classification commit first
with verification that nothing else shifted, then the all-unchecked register
insertion, then the Tier 1 gate on the exact tree, transition with explicit
evidence to `ready_for_review`, push, verify the exact remote head, and stop
for external exact-head review.

No implementation occurs during task authoring. No PR or merge is
authorized. `direct_to_main` is not authorized; the mode remains
`branch_and_fast_forward`.
