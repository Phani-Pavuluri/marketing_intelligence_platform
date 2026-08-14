# Active Task

**Status:** authorized
**Task ID:** `MIP_ROOT_README_NARRATIVE_FLOW_POLISH_001`
**Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
**Local path:** `/Users/phani/Desktop/marketing_intelligence_platform`
**Pre-authoring base:** `ebe2aae41433bf315f0da999c498d65c92e0030d`
**Authorization provenance:** `null` until the metadata-finalization commit
**Feature branch:** `docs/mip-root-readme-narrative-flow-polish-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 1 — routine repository-local documentation
**Compatibility or migration policy:** `not_applicable`
**Capability authority changed:** `false`
**Unresolved execution-blocking design questions:** none

## Primary outcome

Polish the existing root `README.md` narrative flow without broadly rewriting
its content. Improve only the opening product definition and causal-learning
setup, the learning-loop visual in “Why MIP exists,” the centerpiece “How MIP
works” visual, and the ordering of journeys and core capabilities so a marketer,
technical leader, or senior data scientist can quickly understand how MMM,
experimentation, MIP, and AI connect before technical detail.

This is one independently reviewable outcome because it is a narrow editorial
polish of one existing repository front door. It does not redesign the README
information architecture or change product behavior, contracts, architecture,
governance, code, tests, fixtures, program state, or authority.

## Authorization provenance convention

`authorization_head_sha` identifies the first `main` commit establishing this
authorized task contract. That commit may contain a null self-reference. One
subsequent metadata-only commit must record the first commit SHA as immutable
authorization provenance. It must never be replaced by the metadata-finalization,
feature-branch, implementation, publication, review, or merge head.

Create the feature branch only from synchronized metadata-finalized `main`. The
finalized baseline must descend from the immutable authorization provenance;
the intervening diff may contain only the three stable execution files. No
README or implementation change may precede feature-branch creation.

## Owned and prohibited paths

The sole implementation-owned path is:

- `README.md`

Lifecycle updates to these stable execution files are allowed only as required
by the execution standard:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify product/source code, tests, fixtures, apps, contracts, architecture
documents, roadmaps, program files, governance or execution standards,
dependencies, CI, Docker, data, MMM, GeoX, or any sibling repository.

## Required editorial changes

### 1. Opening product definition

Replace the current list-heavy definition with two or three natural sentences:
MIP connects MMM and causal experimentation into a continuous marketing
measurement and planning system; MMM supplies the portfolio view; experiments
supply stronger causal evidence where observational measurement is uncertain;
MIP carries compatible learning into future measurement and planning; and AI
makes the workflow easier to navigate without becoming analytical authority.

Keep the public demo link and concise current-version note. Do not reintroduce a
large disclaimer or describe MIP as merely a portfolio workflow.

### 2. Why MIP exists: transition and learning-loop visual

Replace the current short transition with a plain-language sequence that starts
from MMM's broad portfolio view, explains observational uncertainty, shows how
that uncertainty identifies valuable narrower GeoX/incrementality experiments,
and explains how compatible evidence returns through the governed bridge for
MMM-owned calibration/fitting. The improved portfolio evidence supports
scenario/planning decisions, and remaining uncertainty becomes the next
measurement question. MIP and AI coordinate and expose this process.

Rebuild the visual so it remains glanceable while explicitly connecting:

```text
Business / portfolio question
  → MMM provides the current portfolio view
  → assess what is known confidently versus uncertain
  → identify a material measurement gap when evidence is weak
  → design / run a targeted experiment
  → GeoX produces governed causal lift evidence
  → check quality, scope, uncertainty, freshness, and compatibility
  → eligible evidence becomes CalibrationSignal
  → MMM applies calibration through MMM-owned numerical behavior
  → updated / eligible MMM evidence
  → scenario and planning decisions
  → remaining uncertainty / new business questions
  → next measurement gap ↺
```

Do not imply raw GeoX results edit MMM coefficients, every experiment
automatically calibrates MMM, or MIP performs MMM numerical calibration.

### 3. How MIP works: centerpiece system visual

Retain the current conceptual split across experiment/GeoX, MMM, and existing
evidence, but show each path's intermediate work before convergence.

The visual must begin with the user question, show AI/MIP understanding the
objective, and clarify KPI, channels, geography/population, time horizon,
constraints, and available data/evidence before building the measurement or
decision plan. It must then show:

- **Experiment / GeoX path:** experiment/data readiness; design/assignment when
  needed; GeoX inference; governed experiment readout.
- **MMM path:** data/model readiness; MMM-owned fitting and diagnostics; current
  portfolio measurement; eligible MMM decision surfaces.
- **Existing-evidence path:** retrieve prior experiments, eligible MMM/model
  artifacts, and prior trust/provenance; decide whether existing evidence
  already answers the question.

At convergence, show scope/estimand normalization; lineage, freshness,
uncertainty, quality, and compatibility checks; calibration eligibility;
`CalibrationSignal` into MMM-owned calibration behavior only when eligible;
retention of relevant non-calibration evidence as decision context; and trust
and decision-eligibility evaluation.

Then branch by user need:

- measurement answer → explain incrementality and evidence;
- planning answer → compare eligible full-panel Δμ scenario surfaces;
- insufficient evidence → identify missing evidence and recommend additional
  measurement or experimentation.

End with AI/MIP explaining the result, evidence used, uncertainty, trade-offs,
blockers, and recommended next action, then connect the result back to the
continuous learning loop. Use marketer-friendly labels first; technical
contract names may appear sparingly where they clarify a handoff.

### 4. Example decision journeys

Preserve the three existing short journeys:

1. Channel incrementality — “Is this channel actually incremental?”
2. Experiment → MMM learning — “We finished an experiment. What does this mean
   for our MMM?”
3. Budget planning — “How should I plan next quarter?”

Add one and only one additional journey unless synchronized evidence proves a
major distinct capability would otherwise be missing:

4. Measurement strategy / cold start — “We want to evaluate a new channel.
   What should we measure first?”

Keep it short: business objective → clarify KPI/geography/decision → inspect
historical data and existing evidence → determine whether MMM, experiment, or
additional data collection is feasible → identify missing information →
recommend the next measurement workflow.

### 5. Core capabilities

Keep the `Capability | What MIP does | Why it matters` table, but make its first
column tell the decision story in this order:

1. Frame the business decision.
2. Check data and evidence readiness.
3. Identify the measurement gap and choose the workflow.
4. Measure incrementality and orchestrate targeted experimentation.
5. Reconcile experiment evidence and determine calibration eligibility.
6. Build or refresh the portfolio view through MMM-owned measurement.
7. Compare scenarios and support budget planning.
8. Verify trust and decision eligibility.
9. Explain the answer and recommend the next measurement/action.

Use concise capability names. Each row must state what MIP coordinates or
checks and why it matters without assigning GeoX/MMM numerical computation to
MIP. Where checks recur throughout the workflow, say so. Keep the existing
“Technical foundations” subsection after the table.

## Preserved sections and factual invariants

Make only minimal consistency edits to “How AI fits into MIP,” “Architecture
and trust model,” “Current version and implementation maturity,” “Demo and
quick start,” “Deeper documentation,” and “License.” Do not reopen them for a
general rewrite.

Preserve exactly these authority boundaries:

- `TrustReport` is the sole trust verdict.
- `CalibrationSignal` is the sole GeoX → MMM bridge.
- Full-panel Δμ is the sole MMM production decision surface.
- GeoX owns experiment design/inference and experiment numerical truth.
- MMM owns fitting, diagnostics, calibration application, simulation,
  optimization, and MMM numerical truth.
- MIP owns orchestration, governance, consumer workflows, UX, and LLM behavior.
- MIP does not edit MMM coefficients or recompute GeoX lift.
- Experiment evidence must pass quality, compatibility, uncertainty, freshness,
  and governance checks before it can inform MMM.
- Do not imply automatic experiment-to-MMM recalibration.
- Label current live engine, planning, and LLM maturity conservatively.

## Acceptance evidence and failure semantics

The finished README must retain its existing major section order while making
the opening, learning loop, system visual, four journeys, and capability
progression observable exactly as described above. It must remain materially a
polish of the current content, not another information-architecture rewrite.

Fail closed without publication if links or commands do not resolve, a required
visual stage or journey is absent, the capability order is wrong, a planned
capability is stated as shipped, an invariant or authority boundary is weakened,
or any implementation-content path other than `README.md` changes.

## Tier-1 validation gate

On the frozen publication tree:

1. Run `git diff --check` and inspect `git diff -- README.md`.
2. Programmatically verify every relative README link resolves.
3. Verify the existing major headings remain in intended order and all four
   journey headings exist.
4. Verify the “Why MIP exists” loop contains the connected portfolio-view,
   uncertainty, experiment, governed-lift, compatibility, calibration,
   planning, and next-gap stages.
5. Verify “How MIP works” explicitly contains objective clarification, three
   analysis paths, path-specific steps, evidence convergence,
   compatibility/trust, answer-versus-missing-evidence branches, and
   explanation/next action.
6. Verify the Core capabilities first-column order follows the declared
   decision progression.
7. Verify all referenced quick-start commands and entrypoints still exist.
8. Discover and run relevant existing README/documentation tests.
9. Parse `docs/execution/EXECUTION_STATE.json` as JSON.
10. Verify implementation content changes only `README.md`, and verify P2,
    program, architecture, source, and test surfaces are unchanged.

Full pytest, Ruff, mypy, and Docker-backed `make validate` are `not_required`
for this Tier-1 Markdown-only surface unless synchronized repository-authored
rules require them.

## Publication and review workflow

Execute only after a fresh bootstrap verifies this authorization and the exact
feature branch. Freeze the task-owned tree and run the Tier-1 gate. Update the
three stable execution files to `ready_for_review`, preserving
`task_execution_authorized: true`, `merge_authorized: false`, and
`pr_creation_authorized: false`. Publish the exact feature head with a durable
validation-receipt commit and stop for external review.

Do not create a PR or merge, squash, rebase, force-push, cherry-pick, or create
a merge commit. One correction cycle is available. No product, analytical,
runtime, planning, recommendation, sibling, capability, pilot, production,
merge, or PR authority follows from this task.

## Preserved P2 sequence and deferred work

The P2 program sequence remains unchanged. The parked MIP GeoX/MMM bridge
remains blocked. `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001`
remains next eligible and unauthorized. GeoX certification, MMM implementation,
`CalibrationSignal` construction, simulation, optimization, planning,
recommendations, runtime integration, real data, pilot, and production remain
unauthorized and outside this task.
