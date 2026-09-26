# Active Task

<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** ready_for_review

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_MULTI_RESOLUTION_PLANNING_AND_HIERARCHICAL_MODELING_ROADMAP_AMENDMENT_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `ac578ad2f5dfece99a853d2cd11b3b6d92af16b3`
- **Authorization provenance:** `9e4de817473a8faf822c98b5e04e3f8cf60d8774`
- **Feature branch:** `docs/mip-multi-resolution-planning-hierarchical-modeling-roadmap-amendment-001`
- **Feature branch created:** `true`
- **Task execution authorized:** `true`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `edf6cd6d3ddbed51dc060bcd4c958698cccd329a`
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

## MIP_MULTI_RESOLUTION_PLANNING_AND_HIERARCHICAL_MODELING_ROADMAP_AMENDMENT_001 — task contract

**Status:** proposed; documentation implementation requires the separate lifecycle authorization recorded in Git.

## Primary outcome

Create one MIP-owned roadmap amendment at
`docs/roadmap/MIP_MULTI_RESOLUTION_PLANNING_AND_HIERARCHICAL_MODELING_ROADMAP_AMENDMENT_001.md`,
with one bounded reference from
`docs/roadmap/CROSS_REPOSITORY_CAPABILITY_ROADMAP_PACKET_001.md`. The amendment
will layer future multi-resolution planning, hierarchical MMM research,
cross-scope response abstractions, nested allocation, and experiment-evidence
handoff direction onto the existing capability packet.

This is a documentation-only, non-authorizing planning artifact. It preserves
current analytical truth, current P2 sequencing, current production authority,
the existing packet's concepts, and active MMM/GeoX work. It does not implement
the amendment during this task.

## Why this is one outcome

The amendment is one independently reviewable roadmap boundary and the bounded
packet pointer only makes its relationship discoverable. Capability rows,
schemas, code, fixtures, or owner-repository adoption would be separate tasks.
The implementation must extend existing CAP-001, CAP-002, CAP-003, CAP-006,
CAP-007, CAP-009, CAP-013, CAP-015, CAP-019 and related rows by reference where
they already cover the concept; it must not create a parallel hierarchy or
renumber existing rows. New capability IDs are unnecessary unless live Git
proves that an existing row cannot carry the concept, in which case the task
must select the next available ID and explain the boundary.

## Required amendment content

### 1. Generic planning scope

Describe a general planning hierarchy from global or portfolio planning through
regional, country/market × channel, and local geo × channel decisions. AMER,
EMEA, APAC, US, DMA, state, and similar examples may illustrate the concept but
must not become hard-coded geography names.

Introduce `DecisionScope` or `PlanningScope` as a roadmap concept only, with
geography hierarchy/grain, temporal grain, planning horizon, channel hierarchy,
KPI/outcome, estimand, decision variables, baseline plan, movable and locked
spend, constraints, value/currency basis, calibration/evidence scope, and
supported-range requirements. The conceptual tuple is
`(geography, time, channel, KPI, estimand, decision variables, constraints,
value basis)`.

Explicitly distinguish data, model-estimation, experiment/calibration,
scenario/simulation, optimization, and reporting/decision grains. Row presence
at a finer grain cannot establish direct decision support.

Future artifacts may declare supported scopes and future requests may declare
required scopes. The resolution vocabulary must distinguish directly supported,
supported through a governed hierarchical model, supported only through explicit
policy disaggregation, restricted, experiment-required, and unsupported.

### 2. MMM future research and response surfaces

Preserve Ridge as the current certified/production baseline where live MMM Git
supports that statement, reliability-first promotion, `CalibrationSignal` as
the sole governed experiment-to-MMM bridge, TrustReport/release gates, and
full-panel delta-mu as canonical numerical decision truth inside an MMM model
scope. Do not say that Bayesian MMM replaces Ridge or that curves replace
full-panel delta-mu generally.

Record a future hierarchical geo/channel Bayesian challenger with conceptual
partial pooling such as `beta[g,c] ~ Normal(mu[c], tau[c])`. Explain
heterogeneous geographic response, sparse local markets, pooling toward a
population/channel distribution, uncertainty propagation, and compatibility
with experiment-informed calibration. It is a reliability-evidence challenger,
not a predetermined successor; promotion depends on decision-grade recovery,
not sophistication.

Record centered, non-centered, and auto/adaptive parameterization as an
inference-reliability research question. Use effective local information—geo
observations, within-geo spend variation, signal/noise, number of geos, hierarchy
variance, correlation/identifiability, and calibration coverage—instead of
daily/weekly rules. The adaptive workflow is data geometry → initial candidate
→ short pilot fit → sampler diagnostics → retain or switch → research or
production fit. Diagnostics include divergences, R-hat, effective sample size,
tree depth, energy/E-BFMI where supported, interval behavior, and posterior
pathologies. If both parameterizations fail required diagnostics, fail closed.

Extend reliability research across geo count, periods, heterogeneity, hierarchy
variance, signal/noise, within-geo variation, cross-channel correlation, sparse
versus dense markets, and calibration availability/freshness. Compare Ridge,
centered Bayes, non-centered Bayes, and adaptive selection on full-panel
delta-mu recovery, interval coverage, regret/decision loss, diagnostic
parameter recovery, calibration recovery, divergence rate, effective sample
size, false convergence, and compute cost. This task defines no thresholds.

Within one MMM model scope, retain `delta_mu = mu(candidate full panel) -
mu(baseline full panel)` as canonical truth. Curves/mROI are diagnostic,
candidate-generation, search-acceleration, or explainability aids only. Across
intentionally separate certified model scopes, a future `PortfolioResponseSurface`
may support higher-level allocation when regional heterogeneity makes a unified
model inappropriate. It may replace cross-region full-panel replay at that
higher layer only after independently certified, comparable regional evidence.
The amendment must not prohibit every possible unified global model.

Cross-scope artifacts must preserve or expose KPI/value unit, currency/value and
spend normalization, baseline, horizon, geo/channel scope, estimand,
incremental/total semantics, uncertainty semantics, supported range, calibration
state, fingerprints, TrustReport/readiness, lineage, restrictions, and warnings.

### 3. Portfolio optimization and nesting

Describe future global allocation over certified regional functions `F_r(B_r)`:
maximize `sum_r F_r(B_r)` subject to total-budget conservation, regional
floors/caps, business constraints, and permitted movement bounds. Convex
optimization is eligible only when certified regional functions are concave over
the permitted range and constraints are convex; explain marginal-value
equalization `F'_r(B_r) = lambda` for unconstrained regions.

State that SLSQP does not prove convexity, Hill/saturation surfaces may not be
globally concave, and discrete commitments, thresholds, interactions, inventory,
or other constraints may make the problem non-convex. Those cases remain
governed constrained nonlinear optimization with diagnostics, multistart and
stability checks, and explicit limitations.

Connect to existing risk-aware optimization direction: future expected-value,
downside-aware, probability/quantile, or robust views may be considered, with
conceptual P20/P50/P80/P90 examples clearly framed as future examples rather
than current policy. Preserve the separation of uncertainty evidence,
optimization candidate, recommendation proposal, human approval, and
execution.

Capture nested global → regional → market/channel → local geo/channel planning.
Each level declares supported scope, conserves parent budget where applicable,
preserves provenance, separates model-derived allocation from policy
disaggregation, exposes uncertainty and supported range, and reconciles to the
parent where mathematically meaningful. No dataset must contain every level.

### 4. GeoX and MIP ownership direction

GeoX future evidence preserves experiment estimand, population/geography scope,
treatment, KPI/units, exposure and outcome windows, uncertainty, lineage, and
handoff eligibility. Research questions include local-to-broad prior use,
national-to-local hierarchical components, heterogeneous effects, transportability,
partial-pooling calibration, scope mismatch, sparse markets, and freshness.
GeoX owns experimental truth and handoff eligibility; it does not fit
hierarchical MMM, calculate response surfaces, optimize budgets, or determine
MMM compatibility/calibration treatment. MMM owns experiment-to-model
compatibility and calibration treatment.

MIP is the future product/control-plane owner: interpret the planning question,
resolve the requested scope, determine needed artifacts, check readiness and
compatibility, route MMM/GeoX evidence, explain scenarios, preserve TrustReport
and warnings, and require human approval where consequential. It does not fit
models, pool parameters, calculate response curves/mROI/lift/calibration, or
own numerical optimization truth. LLM behavior remains orchestration and
explanation only.

### 5. Sequence and authority preservation

The amendment must explicitly leave the live P2 dependency sequence unchanged.
It must not skip GeoX prerequisites, certify GeoX, authorize CalibrationSignal
construction, start hierarchical Bayes, response surfaces, optimization, the
parked bridge, D6 changes, LLM runtime, package integration, real-data work,
recommendation, pilot, or production. Existing active MMM and GeoX tasks remain
untouched. Roadmap appearance never makes a capability executable. Owner
repository adoption is a later separately authorized task.

Claims about Meridian, Robyn, PyMC, or industry practice are external context
unless directly supported by repository evidence. Do not claim Meridian has an
automatic centered/non-centered switch without authoritative evidence.

## Compact task-seed requirements

Include compact seeds for scope/grain compatibility, multi-resolution
applicability, hierarchical Bayesian challenger, parameterization reliability,
multi-resolution CalibrationSignal compatibility, portfolio response surfaces,
cross-scope comparability, convex/nonlinear allocation, nested budget
reconciliation, and risk-aware multi-level allocation. Each seed names owner
repository, priority, prerequisites, prohibited authority, validation/reliability
evidence, acceptance evidence, and re-verification triggers. Seeds are proposals,
not work orders or authorization.

## Ownership and prohibited scope

MIP owns the roadmap architecture, scope semantics, coordination, product
routing, and governance framing. MMM owns future modeling, pooling,
parameterization, diagnostics, response surfaces, simulation, uncertainty,
candidate generation, and numerical optimization. GeoX owns future experiment
truth and experiment-side multi-resolution calibration evidence.

Only MIP may change the two declared roadmap paths. Prohibit all MMM and GeoX
file changes; analytical code; contracts, schemas, fixtures, unrelated tests,
runtime/package behavior; `NEXT_EXECUTION_SEQUENCE.md` unless a reference-only
change is proven necessary; P2 ledger state; coordination-state refresh;
parked-bridge resumption; CalibrationSignal/Bayesian/response-surface/optimizer/
LLM implementation; real data, pilot, production, PR, merge, squash, rebase,
force-push, and cherry-pick.

## Risk and validation

Use the repository-defined Tier 3 cross-repository documentation/governance
posture. The future implementation gate must include taskctl check; JSON parsing;
changed-path boundary proof; available Markdown/link/reference validation;
fresh cross-repository live-ref verification; ownership-pattern checks;
`git diff --check`; exact-tree publication receipt; and local/remote feature-head
equality. Run Docker `make validate` only if the live MIP risk rules require it;
the task must record it as not required when the documentation-only gate allows
omission. Validation must cover the acceptance criteria below and must not
execute analytical or sibling work.

## Acceptance evidence

The future implementation must prove that existing packet concepts are reused;
planning is generic; all grains are distinguished; delta-mu remains canonical
within scope; cross-scope surfaces are future certified abstractions; convexity
is conditional; non-convex cases remain governed nonlinear problems; Bayesian
work is a challenger; parameterization is diagnostic and fails closed; GeoX,
MMM, and MIP boundaries and CalibrationSignal authority remain unchanged; no
unestablished serialized producer is assigned; P2 ordering and active sibling
work remain unchanged; roadmap rows grant no executable authority; owner adoption
is separate; and external Meridian/PyMC/industry claims are properly qualified.

## Deferred successors and stop condition

Deferred successors are the owner-repository roadmap insertions, MMM
hierarchical-model/reliability/response-surface/optimizer research, GeoX
multi-resolution experiment evidence, MIP scope routing and governance
implementation, any contract/schema, and all runtime, recommendation, pilot,
production, or real-data work. The task stops after authoring, validation, and
publication of the documentation-only outcome at `ready_for_review`; it does
not implement the amendment. Unresolved execution-blocking design questions:
none.
