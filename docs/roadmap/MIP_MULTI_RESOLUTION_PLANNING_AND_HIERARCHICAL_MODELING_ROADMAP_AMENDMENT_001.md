# MIP Multi-Resolution Planning and Hierarchical Modeling Roadmap Amendment 001

**Status:** future architecture and research direction; non-authorizing
**Owner:** MIP program/governance
**Related source proposal:** [Cross-Repository Capability Roadmap Packet 001](CROSS_REPOSITORY_CAPABILITY_ROADMAP_PACKET_001.md)
**Related current consumer design:** [MIP P2 Consumer Contract and Fixture Journey Design 001](MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md)
**Date:** 2026-09-26

This amendment layers multi-resolution planning and hierarchical modeling onto
the existing MIP/MMM/GeoX roadmap. It reuses the packet's scope-aware routing,
high-level-to-low-level allocation, model applicability and decision readiness,
risk-aware optimization, granular and strategy response surfaces, full-panel
simulation reconciliation, calibration freshness and coverage, supported-range
rules, Meridian/Robyn decision benchmarking, and separation of simulation,
optimization, recommendation, approval, and execution.

It is a future architecture and research direction. It does not change current
analytical truth, current P2 sequencing, current production authority, the
current certified Ridge baseline, or active sibling work. A roadmap entry is
not an implementation, contract, schema, capability authorization, or evidence
of readiness.

## 1. Planning at multiple resolutions

Future planning may be organized as a general hierarchy:

```text
global / portfolio planning
→ regional planning
→ country / market × channel planning
→ local geo × channel planning
```

Examples such as AMER/EMEA/APAC, country × channel, or DMA/state/region ×
channel illustrate possible operating levels. They are examples only. The
architecture reasons about a general decision or planning scope and does not
hard-code a geography vocabulary.

### DecisionScope / PlanningScope

`DecisionScope` or `PlanningScope` is a roadmap-level concept, not a committed
schema. It should eventually capture:

- geography hierarchy and grain;
- temporal grain and planning horizon;
- channel hierarchy;
- KPI/outcome and estimand;
- decision variables;
- baseline plan;
- movable versus locked spend;
- constraints;
- value and currency basis;
- calibration/evidence scope; and
- supported-range requirements.

Conceptually:

```text
DecisionScope = (geography, time, channel, KPI, estimand,
                 decision variables, constraints, value basis)
```

The platform must distinguish these grains explicitly, including the data grain
from the model-estimation grain:

| Grain | Meaning | Required interpretation |
|---|---|---|
| Data grain | Resolution at which rows or events are observed | Row availability alone does not establish decision support |
| Model-estimation grain | Resolution at which parameters are estimated | Pooling and identifiability must be disclosed |
| Experiment/calibration grain | Population, treatment, and outcome scope of evidence | Handoff eligibility and compatibility remain owner decisions |
| Scenario/simulation grain | Resolution represented in candidate and baseline replay | Full-panel semantics and supported range must be preserved |
| Optimization grain | Resolution at which variables are moved under constraints | A finer variable grid requires evidence or explicit policy |
| Reporting/decision grain | Resolution at which a claim is shown to a decision maker | Claims must carry scope, lineage, warnings, and restrictions |

No finer-grained decision may be represented as directly supported merely
because rows exist at that grain. Future artifacts may declare the decision
scopes they support, and planning requests may declare the scope they require.
The future resolver should classify a request as directly supported, supported
through a governed hierarchical model, supported only through explicit policy
disaggregation, restricted, experiment-required, or unsupported.

## 2. MMM future direction

### Current production truth

Current truth remains unchanged. Ridge remains the certified/production baseline
where live MMM Git establishes it. Promotion remains reliability-first.
`CalibrationSignal` remains the sole governed experiment-to-MMM bridge.
TrustReport and release gates remain in force. Within an MMM model scope, the
canonical numerical decision surface remains full-panel delta-mu:

```text
delta_mu = mu(candidate full panel) - mu(baseline full panel)
```

Bayesian MMM has not replaced Ridge, and response curves have not generally
replaced full-panel delta-mu. Curves and mROI may support diagnostics, candidate
generation, search acceleration, or explainability while the governed decision
surface remains full-panel simulation.

### Hierarchical geo/channel Bayesian challenger

MMM may research a hierarchical geo/channel Bayesian challenger with partial
pooling, conceptually:

```text
beta[g,c] ~ Normal(mu[c], tau[c])
```

The research motivation includes heterogeneous geographic response, sparse local
markets, pooling local markets toward a population/channel distribution, richer
uncertainty propagation, and compatibility with experiment-informed calibration.
This is a challenger requiring reliability evidence, not a predetermined Ridge
successor. Promotion depends on measurable improvement in decision-grade
recovery and operational reliability rather than model sophistication.

### Centered, non-centered, and adaptive parameterization

Centered, non-centered, and auto/adaptive parameterization are future inference-
reliability modes. Selection must use effective local information rather than
rules based only on daily or weekly data. Relevant geometry includes observations
per geo, within-geo spend variation, signal-to-noise, number of geos, hierarchy
variance, cross-parameter correlation and identifiability, and calibration
coverage.

An adaptive workflow may be governed as:

```text
data geometry
→ initial parameterization candidate
→ short pilot fit
→ sampler diagnostics
→ retain or switch parameterization
→ production/research fit
```

Diagnostics may include divergent transitions, R-hat, effective sample size,
tree depth, energy/E-BFMI where supported, interval behavior, and posterior
pathologies. If both parameterizations fail required diagnostics, the workflow
must fail closed rather than assume reparameterization solved identification.

### Reliability program extension

Future synthetic-world evaluation should span number of geos, number of periods,
geo heterogeneity, hierarchy variance, signal/noise, within-geo spend variation,
cross-channel correlation, sparse versus dense markets, and calibration
availability/freshness. At minimum compare Ridge, centered hierarchical Bayes,
non-centered hierarchical Bayes, and adaptive parameterization selection.

Evaluation should prioritize full-panel delta-mu recovery, interval or credible-
interval coverage, decision loss or regret, diagnostic parameter recovery,
calibration recovery, divergence rate, effective sample size, false convergence,
and compute cost. This amendment defines no thresholds and promotes no method.

## 3. Cross-scope response surfaces

### Within one MMM model scope

For a candidate plan, full-panel delta-mu remains canonical:

```text
delta_mu = mu(candidate full panel) - mu(baseline full panel)
```

Channel response curves and mROI may accelerate search, generate candidates,
support diagnostics, or explain a result. They may not silently replace the
governed full-panel decision surface inside that scope.

### Across intentionally separate model scopes

Future independently certified regional or market models may emit a conceptual
`PortfolioResponseSurface`. A higher-level allocator may consume certified
regional portfolio abstractions instead of fitting one giant global MMM when
structural heterogeneity makes a unified model inappropriate. Relevant
heterogeneity may include baseline demand, consumer behavior, campaign
structure, product availability, pricing, media taxonomy, calendars, currencies,
and local constraints.

Response surfaces may replace cross-region full-panel replay at the higher
portfolio allocation layer only after the underlying regional models have
independently produced certified, comparable response evidence. This direction
does not prohibit every possible unified global raw-panel model.

### Comparability requirements

A higher-level allocator must not compare raw marginal-return functions unless
the contributing artifacts are economically and semantically comparable. Future
artifacts should preserve or expose KPI and value unit, currency/value
normalization, spend unit, baseline plan, planning horizon, geo/channel scope,
estimand, incremental versus total value semantics, uncertainty semantics,
supported spend range, calibration state, model/data fingerprints,
TrustReport/readiness state, lineage, restrictions, and warnings.

These are roadmap requirements, not a schema commitment in this amendment.

## 4. Global and nested portfolio allocation

For independently modeled regional portfolio functions `F_r(B_r)`, future
planning may consider:

```text
maximize sum_r F_r(B_r)
```

subject to total budget conservation, regional floors and caps, business
constraints, and permitted movement bounds. If certified regional functions are
concave over the permitted range and constraints are convex, the problem is
eligible for convex optimization. For unconstrained regions, the interior
condition may be explained through marginal-value equalization:

```text
F'_r(B_r) = lambda
```

SLSQP usage does not prove convexity. Hill or saturation surfaces are not
necessarily globally concave over every domain. Discrete commitments, activation
thresholds, interactions, inventory limits, or other constraints may make the
problem non-convex. When convexity assumptions do not hold, the roadmap
direction is governed constrained nonlinear optimization with diagnostics,
multistart and stability checks, and explicit limitations.

Risk-aware planning extends the existing risk-aware optimization direction. A
future planner may compare expected-value, conservative/downside-aware,
probability or quantile, and robust objectives. P20/P50/P80/P90 can be
conceptual planning views, but they are not current policy. Posterior or other
uncertainty evidence remains distinct from an optimization candidate, a
recommendation proposal, human approval, and execution.

The long-term nested structure is:

```text
global budget
→ regional budgets
→ market/channel allocations
→ local geo/channel allocations
```

Each level should conserve the parent budget where applicable, declare its
supported scope, preserve provenance, distinguish model-derived allocation from
explicit policy disaggregation, expose uncertainty and supported range, and
reconcile to its parent where mathematically meaningful. Organizations and
datasets do not need to contain every level.

## 5. Ownership direction

### GeoX

Future multi-resolution calibration evidence from GeoX should preserve the
experiment estimand, geography/population scope, treatment definition, KPI and
units, exposure window, outcome window, uncertainty, lineage, and handoff
eligibility. Research questions include when local evidence may inform a broader
population prior, when national evidence may inform local hierarchical
components, calibration under heterogeneous geo effects, transportability
limits, partial-pooling calibration semantics, scope mismatch, sparse-market
evidence, and calibration freshness.

GeoX owns experimental truth and handoff eligibility. GeoX does not fit
hierarchical MMM, calculate MMM response surfaces, optimize budgets, or decide
MMM compatibility or calibration treatment. MMM remains the owner of
experiment-to-model compatibility and calibration treatment.

### MMM

MMM owns future hierarchical MMM, pooling, parameterization selection, Bayesian
sampler diagnostics, response surfaces, full-panel delta-mu, simulation,
uncertainty, candidate generation, and numerical optimization. MMM owns the
analytical truth for those artifacts and their reliability evidence.

### MIP

MIP is the future product and control-plane owner. It may eventually interpret a
user's planning question, construct or resolve the requested `DecisionScope`,
determine required analytical artifacts, check model/evidence/readiness
compatibility, route to appropriate MMM and GeoX evidence, explain supported
scenarios and candidates, preserve TrustReport and warnings, and require human
approval for consequential decisions.

MIP does not implement hierarchical pooling, fit MMM, calculate response-curve
or mROI truth, calculate optimization numerical truth, calculate experiment lift,
or decide calibration treatment. LLM behavior remains orchestration and
explanation only.

The future system should distinguish questions such as “How should FY27 budget
move across AMER, EMEA and APAC?”, “Within the US, how should Search, Meta and
CTV be allocated?”, and “Which US geographies should receive additional Meta
spend?” These examples illustrate distinct scopes; they do not hard-code
geography names.

## 6. Current sequence and authority boundary

This amendment does not change the current six-step P2 dependency order:

1. GeoX test isolation and checkpoint context recovery;
2. GeoX calibration-source certification recovery;
3. MMM provenance-linked compatibility fixtures;
4. the MIP GeoX/MMM compatibility bridge;
5. D6 release-compatibility evidence; and
6. the MIP fixture-only planning-evidence journey.

The sequence remains dependency order, not authorization. This amendment does
not skip GeoX prerequisites, certify GeoX, authorize CalibrationSignal
construction, start hierarchical Bayes, start portfolio-response work, start
optimization, resume the parked MIP bridge, modify D6 sequencing, authorize LLM
runtime, authorize package integration, authorize real-data work, authorize
recommendation, or authorize pilot or production. Existing active MMM and GeoX
tasks remain untouched. No capability becomes executable because it appears in a
roadmap. Owner-repository adoption is a later separately authorized task.

`CalibrationSignal` remains the sole governed GeoX-to-MMM bridge. No exact
serialized producer is assigned here unless a future live certified contract
establishes it.

Claims about Meridian, Robyn, PyMC, or industry practice are external context
unless directly supported by repository evidence. This amendment does not claim
that Meridian implements an automatic centered/non-centered switch.

## 7. Compact future task seeds

These are compact proposals rather than work orders. Each owner must author and
authorize its own repository task later.

| Seed | Owner | Priority | Prerequisites | Evidence and acceptance | Prohibited authority | Re-verify when |
|---|---|---|---|---|---|---|
| Scope/grain compatibility | MIP | P1 | Existing CAP-001/002 and live P2 evidence | Scope matrix covering all grains and direct/policy/restricted/unsupported outcomes | No schema or router runtime | Scope, estimand, or evidence contract changes |
| Multi-resolution applicability | MIP + MMM | P1 | Scope registry and model readiness | Scope applicability and supported-range evidence | No model fitting or promotion | Model, data, or calibration fingerprint changes |
| Hierarchical geo Bayesian challenger | MMM | Research/P2 successor | Ridge baseline and certified synthetic worlds | Decision-grade recovery and reliability comparison | No automatic Ridge replacement | DGP, sampler, or production-gate change |
| Parameterization reliability | MMM | Research | Hierarchical challenger and local-information diagnostics | Centered/non-centered/adaptive diagnostics; fail closed if both fail | No daily/weekly heuristic or runtime switch | Geometry, sampler, or diagnostic policy changes |
| Multi-resolution CalibrationSignal compatibility | GeoX + MMM | P2 successor | Certified GeoX evidence and MMM compatibility owner decision | Scope/estimand/uncertainty/lineage compatibility evidence | No MIP-invented compatibility or serialized producer | Contract, scope, or freshness change |
| PortfolioResponseSurface | MMM | P2/P3 successor | Independently certified regional evidence | Comparable surfaces, supported range, uncertainty, and reconciliation | No cross-scope raw-return comparison | KPI, currency, taxonomy, or model change |
| Cross-scope comparability | MIP + MMM | P1/P2 | Existing CAP-009/015/019 | Comparable-artifact checklist and refusal fixtures | No numerical response math in MIP | Value basis, estimand, or lineage change |
| Convex/nonlinear allocation | MMM + MIP | P2/P3 successor | Certified surfaces and constraints | Conditional convex classification; nonlinear diagnostics otherwise | No optimizer implementation here | Surface shape or constraint change |
| Nested budget reconciliation | MIP + MMM | P1/P2 | Scope and allocation evidence | Parent conservation, provenance, policy disaggregation, reconciliation | No spend execution | Hierarchy or constraint change |
| Risk-aware multi-level allocation | MMM + MIP | P2/P3 successor | Uncertainty and certified surfaces | Scenario/regret/stability evidence and human-review boundary | No recommendation or approval | Risk policy or uncertainty semantics change |

Every successor task must name its owner, priority, prerequisites, prohibited
authority, reliability evidence, acceptance authority, and re-verification
triggers. It must use one repository and one independently reviewable outcome.

## 8. Non-authority and external adoption

This amendment changes no current P2 ledger state, coordination state, contract,
schema, fixture, analytical code, package behavior, runtime behavior, or
production authority. MMM and GeoX roadmap adoption must occur in separately
authorized owner-repository tasks. MIP may coordinate and explain the direction
but cannot implement sibling responsibilities or retroactively alter sibling
roadmaps.

The amendment is complete as a roadmap document only. Future implementation,
research, certification, consumer verification, recommendation, approval,
execution, pilot, production, and real-data work each require their own
repository-authored evidence and authorization.
