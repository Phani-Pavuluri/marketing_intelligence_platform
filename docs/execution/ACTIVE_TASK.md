# Active Task

<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** merged

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_CROSS_REPOSITORY_CAPABILITY_ROADMAP_PACKET_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `fb232c4d3943df2198602ed976ba01a4dbe9e199`
- **Authorization provenance:** `d749beff0d1e74133f1d994197ddffbded7b1a26`
- **Feature branch:** `docs/mip-cross-repository-capability-roadmap-packet-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `780f880fe62ac99ef247122c754e11c0d8155753`
- **Reviewed head:** `8b7007d213664ff0edea4e502d5bd13b5ab552e6`
- **Rejected review head:** `1ea6a21efa4409278d74775403254e74380fd4fc`
- **Rejected implementation commit:** `3dc94c15bc6596e7e9799a84c081ebee3242d123`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `1`
- **Correction cycles remaining:** `0`
- **Review decision:** `merged`
- **Local feature-branch cleanup:** `observed_deleted`
- **Remote feature-branch cleanup:** `observed_deleted`
- **Capability authorizations changed:** `false`
<!-- END MIP TASKCTL EXECUTION VIEW -->

## MIP_CROSS_REPOSITORY_CAPABILITY_ROADMAP_PACKET_001 — proposed task contract

**Status:** proposed; non-executable until separately authorized.

## Primary outcome

Publish one MIP-owned, non-authorizing roadmap packet at
`docs/roadmap/CROSS_REPOSITORY_CAPABILITY_ROADMAP_PACKET_001.md`.
The packet will consolidate the agreed MMM, GeoX, and MIP capability gaps into
priority-ordered, agent-executable roadmap entries with ownership, dependencies,
acceptance evidence, metrics, validation gates, and deferred successors.

The packet is a planning artifact. It does not modify MMM or GeoX, change any
canonical sibling roadmap, create a contract or schema, authorize implementation,
or grant analytical, recommendation, optimization, pilot, production, or runtime
authority.

## Why this is one outcome

The packet is the single cross-repository source proposal from which later
owner-repository roadmap and implementation tasks may be derived. Splitting it
into separate capability documents would duplicate authority and make ownership,
priority, and dependencies drift.

## Required packet contents

The implementation must include:

1. operating principles and explicit non-authority boundaries;
2. P0–P3 priority definitions and prioritization metrics;
3. P0 foundations: estimand protocol, model applicability/decision-readiness
   registry, package-diagnosable validity checks, and warning/refusal semantics;
4. P1 decision capabilities: scope-aware routing, high-level-to-low-level
   allocation, strategy/segment estimands, experiment prioritization and the
   MIP→GeoX handoff, calibration coverage/freshness, remaining-horizon
   reallocation, macro/promotion scenarios, risk-aware optimization, and actual
   outcome feedback;
5. P2 advanced capabilities: interaction/halo/cannibalization analysis,
   granular and strategy curves, and incremental/hurdle reporting;
6. P3 operational refinements;
7. ownership boundaries: MMM numerical truth, GeoX experiment truth, MIP
   orchestration/claims/decision routing, and LLM interpretation only;
8. package-relevant diagnostic metrics, including data quality, identifiability,
   extrapolation, lag/saturation sensitivity, temporal stability, calibration
   coverage, scenario validity, and optimizer stability;
9. implementation instructions requiring one bounded task per owner repository,
   exact scope, evidence, version/fingerprint, re-verification triggers, and
   no silent authority expansion;
10. insertion guidance mapping the packet into existing canonical roadmaps
    without duplicating or overwriting them; and
11. a future-task template for implementation, validation, publication, and
    exact-head review.
12. a compact-row composition rule and per-entry status, authority impact,
    validation gate, acceptance authority, and re-verification fields;
13. explicit adversarial/disagreement fixture requirements, the current MMM
    Tier-1 characterization/runner as a refreshable read-only input, and
    fixture gates for MIP orchestration behavior;
14. GeoX handoff minimums: feasibility, power/MDE, assignment,
    carryover/spillover, cost, duration, constraints, stop rules, and return to
    MMM calibration;
15. the bounded Meridian/Robyn decision benchmark, its equivalent-input rule,
    decision-output metrics, disagreement taxonomy, and non-authority boundary;
16. named P3 refinements, exploration floors, freshness-triggered refit policy,
    segment-support evidence, and regret-based candidate comparison.

## Required decision semantics

The packet must distinguish exploratory simulation, decision-supported
recommendation, execution-eligible output, and unsupported or experiment-required
output. Warnings may permit exploration but must state the affected scope,
limitation, required resolution, and whether execution is prohibited. User inputs
and LLM suggestions must become visible structured constraints, weights, or
scenarios; they may not silently change an optimizer objective.

## Inputs and evidence

Read-only inputs are the merged DE-0 estimand protocol, the current MIP roadmap
and coordination protocol, and live synchronized `origin/main` plus execution
files for MMM and GeoX. The packet must record observed sibling SHAs and date
them as orientation evidence, while stating that sibling repositories remain
authoritative for their own roadmaps and tasks.

Observed orientation pins for this proposal:

- MIP `main`: `fb232c4d3943df2198602ed976ba01a4dbe9e199`;
- MMM `origin/main`: `e33b925b3a0bbdd343ff3b7197c2051a2b7c7388`;
- GeoX/panel_exp `origin/main`: `496c317bc44c31a89aff805896863bd7eb637b7e9`.

These pins are evidence of orientation only, not sibling completion or
authorization. A later implementation task must refresh them before use.

## Owned paths

Implementation may change only:

- `docs/roadmap/CROSS_REPOSITORY_CAPABILITY_ROADMAP_PACKET_001.md`;
- `docs/execution/EXECUTION_STATE.json`;
- generated lifecycle blocks in `docs/execution/ACTIVE_TASK.md`; and
- `docs/execution/LATEST_COMPLETION_REPORT.md`.

## Prohibited scope

Do not modify MMM or GeoX; edit existing canonical roadmap bodies; create
implementation tasks in sibling repositories; change contracts, schemas,
runtime behavior, prompts, model code, calibration, simulation, optimization,
recommendation, authority flags, coordination state, or decision registers;
archive or delete documents; use real/customer data; create a PR; merge,
rebase, squash, force-push, or create a merge commit.

## Acceptance evidence

Acceptance requires:

1. all required packet sections are present;
2. every capability has an owner, priority, dependency, bounded outcome,
   acceptance evidence, metric, and re-verification trigger;
3. all package-diagnosable diagnostics identify observable inputs and actions;
4. warning/refusal, scope, calibration, disaggregation, and authority boundaries
   are explicit;
5. MMM/GeoX ownership and read-only sibling status are preserved;
6. insertion guidance does not duplicate or silently alter canonical roadmaps;
7. links and Markdown checks pass;
8. JSON, taskctl, diff, changed-path, and cross-repository pin checks pass;
9. no sibling file or authority state changes; and
10. the packet is explicitly non-authorizing and non-normative.
11. the external comparator is bounded to decision evidence and does not claim
    universal engine superiority; and
12. per-entry status and authority impact are explicit for every capability.

## Validation

On the frozen implementation tree run the repository taskctl check, JSON
structure check, Markdown/link check, `git diff --check`, and an exact
changed-path proof against the authorization head. Re-fetch and verify the
recorded live sibling pins, manually verify every required section, and classify
each category as passed, failed, blocked, or not_required. No Docker or
analytical gate is required for this documentation-only packet unless the owner
repository standard changes before execution.

## Cross-repository impact

Affected repositories are MIP, MMM, and GeoX/panel_exp; only MIP is modified.
The workstream is planning/governance documentation. No dependency is resolved
and no sibling task is authorized. The completion report must repeat the live
pins, ownership boundaries, consumer-verification requirement, and authority
impact.

## Deferred successors

Deferred work includes owner-repository roadmap insertion, MMM diagnostic or
optimizer implementation, GeoX experiment capability, MIP scope-router or
outcome-registry implementation, schema/contract adoption, and any capability
or execution authorization. Each requires a separate task in the owning
repository.

## Stop condition

This proposal stops at `proposed`. No branch or implementation may be created
until a separate exact contract authorization transitions it to `authorized`.

Unresolved execution-blocking design questions: none.
