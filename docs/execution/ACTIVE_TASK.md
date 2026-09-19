<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** ready_for_review

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_ESTIMAND_PROTOCOL_DESIGN_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `8fcb309b9d55a4e52b868d9324145cfb93f4cb47`
- **Authorization provenance:** `96d164aca8400f0ba59643d1e869ebc045180d38`
- **Feature branch:** `docs/mip-estimand-protocol-design-001`
- **Feature branch created:** `true`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `685b7b21359a80ef0a83d0428d0c7ea1888f383d`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `ready_for_review`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END MIP TASKCTL EXECUTION VIEW -->

## Primary outcome

Publish one Git-authoritative, Tier 1 documentation-only design: a
non-normative estimand-protocol proposal at
`docs/design/MIP_ESTIMAND_PROTOCOL_DESIGN_001.md` that defines the
measurable quantities before any DE-1/DE-3 criterion is set, and move the
register's DE-0 row from `unchecked` / `not_eligible` to
`evidence_submitted`, recording the design artifact SHA while leaving the
acceptance SHA empty.

This document is a design proposal. It is not a new MIP contract and not a
cross-repository schema. It creates no code, schema, contract, runtime,
analytical, or authority change.

## Why this is one independently reviewable outcome

The design and its submission marker must be reviewed together: the
`evidence_submitted` row points at the exact design artifact in the same
branch, so the reviewer judges content and pointer as one unit. Flipping
the row to `accepted` is a separate successor because the acceptance SHA
cannot safely refer to the final reviewed head before that head exists —
`accepted` must never be self-asserted by the producing task.

## Design contents

The document must define:

- measurable quantities per lifecycle stage;
- the estimand-versus-planning-quantity distinction;
- lifecycle/R0 ownership mapping;
- boundaries and explicit non-claims;
- scope, version, and fingerprint fields;
- re-verification triggers.

## Acceptance authority and review evidence

- **Acceptance authority:** MIP program/governance owner.
- **External review evidence:** the exact approved review-head SHA.

The SHA proves which tree was reviewed; it does not identify who owns
acceptance. Acceptance is owned by the named role above, exercised through
the repository's exact-head review, and recorded by the successor that
flips the row to `accepted`.

## Status sequence for the DE-0 row

1. This task creates the design document.
2. The DE-0 row changes from `unchecked` / `not_eligible` to
   `evidence_submitted`, recording the design artifact/implementation SHA
   and leaving acceptance SHA empty.
3. The named governance authority reviews and accepts it.
4. A small successor lifecycle/documentation update changes the row to
   `accepted` and records the reviewed acceptance SHA.

## Authoring evidence

Task authoring observed clean synchronized MIP `origin/main` at
`8fcb309b9d55a4e52b868d9324145cfb93f4cb47` with
`poetry run python -m mip.execution.taskctl check` passing. The register
proposal (`MIP_DECISION_EVIDENCE_GAP_REGISTER_PROPOSAL_001`) is merged
with the DE-0 row unchecked. No sibling evidence is required: this task
neither reads nor writes MMM or GeoX, and no coordination-state refresh
is authorized.

## Inputs, outputs, invariants, and failure semantics

- **Inputs:** the merged register's DE-0 row at the finalized
  authorization baseline, plus this Git-authored contract.
- **Output:** only the new design document, the DE-0 row's move to
  `evidence_submitted`, and the required MIP lifecycle publication
  updates.
- **Invariants:** non-normative proposal; no new contract or schema; no
  row reaches `accepted` in this task; acceptance SHA stays empty; Git
  authority and repository ownership preserved; no product, analytical,
  capability, ledger, coordination-state, or runtime behavior changes.
- **Compatibility/migration:** `not_applicable`; no API, schema, state
  machine, persisted artifact, version, or migration changes.
- **Failure semantics:** any `accepted` flip, any non-empty acceptance
  SHA, any edit beyond the DE-0 row, any normative contract/schema
  language, any sibling write, any capability-authority change, or
  inability to run the Tier 1 gate must fail closed. If a safe authorized
  branch exists at execution time, publish a durable `blocked` state with
  exact evidence and a live resolution condition.

Unresolved execution-blocking design questions: none.

## Owned paths

Implementation may change only:

- `docs/design/MIP_ESTIMAND_PROTOCOL_DESIGN_001.md` (new design document)
- `docs/roadmap/ROADMAP.md` (DE-0 row status only)
- `docs/execution/EXECUTION_STATE.json`
- the generated lifecycle block in `docs/execution/ACTIVE_TASK.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The stable execution files are lifecycle publication paths, not additional
deliverables.

## Prohibited scope

Do not flip any row to `accepted`; fill any acceptance SHA; edit any
register row other than DE-0; finalize DE-1/DE-3 criteria; create or amend
any MIP contract, schema, or cross-repository interface; modify GeoX or
MMM in any way; authorize or execute sibling tasks; alter product or
analytical truth; construct `CalibrationSignal`; run calibration,
fitting, simulation, or optimization; resume the parked MIP bridge; change
P2 capability semantics; modify LLM prompts, providers, or runtime
behavior; change packages, fixtures, code, tests, CI, hooks, or Docker;
alter roadmaps beyond the DE-0 row; touch ledgers, coordination state, or
repository standards; use real or customer data; create persistent product
artifacts; make recommendations; authorize pilot, production, promotion,
or runtime integration; modify any capability-authority flag; or create a
PR, merge, squash, rebase, force-push, cherry-pick, or merge commit
outside the repository's allowed `branch_and_fast_forward` flow.

## Acceptance evidence

The completed design and report must prove:

1. measurable quantities are defined per lifecycle stage;
2. the estimand-versus-planning-quantity distinction is stated;
3. the R0 ownership mapping is present;
4. explicit non-claims are stated;
5. scope/version/fingerprint fields are present;
6. re-verification triggers are listed;
7. producer versus accepting authority is distinguished (MIP
   program/governance owner accepts; the SHA is review evidence only);
8. no independent execution or capability authority is granted or implied;
9. links and Markdown/document validation pass;
10. `taskctl`, JSON, diff, and changed-path checks pass;
11. the document declares itself a non-normative proposal, not a contract
    or schema;
12. the DE-0 row reads `evidence_submitted` with the design artifact SHA
    recorded and acceptance SHA empty; and
13. changed paths are limited to the owned paths.

## Validation

On the frozen exact implementation tree run and record:

```bash
poetry run python -m mip.execution.taskctl check
python3 -m json.tool docs/execution/EXECUTION_STATE.json >/dev/null
git diff --check
git diff --name-only <authorization-head>...HEAD
```

Also perform a manual review of every checklist item above, the row
status, SHA fields, and paths; verify local/remote branch-head equality;
and classify each validation category as `passed`, `failed`, `blocked`,
or `not_required`. Tier 1 uses this focused documentation gate;
Docker-backed `make validate` is `not_required` (no code, contract,
package, analytical, or runtime surface changes).

## Deferred successors

Deliberately not in this task: the small successor that flips the DE-0
row to `accepted` with the reviewed acceptance SHA; DE-1/DE-3 criteria
finalization; the stale-doc rename; archive moves; schema adoption;
`panel_exp`/MIP sequencing; the Tier-1 runner; `AGENTS.md` changes; and
any execution, authorization, or capability claim flowing from any
register row. This design may sequence future evidence work but must not
pre-authorize or silently define those tasks.

## Git workflow and stop condition

This task is authorized for execution on
`docs/mip-estimand-protocol-design-001` from the exact finalized
synchronized authorization baseline: create the design document, move the
DE-0 row to `evidence_submitted` with the artifact SHA and empty
acceptance SHA, run the Tier 1 gate on the exact tree, transition with
explicit evidence to `ready_for_review`, push, verify the exact remote
head, and stop for external exact-head review by the named acceptance
authority.

No implementation occurs during task authoring. No PR or merge is
authorized. `direct_to_main` is not authorized; the mode remains
`branch_and_fast_forward`.
