# Cross-Repository Capability Roadmap Packet 001

**Status:** proposal for roadmap insertion; non-authorizing
**Owner:** MIP program/governance
**Version:** `capability-roadmap-packet-v1`
**Authored against:** MIP `82feba8`, MMM `e33b925b3a0bbdd343ff3b7197c2051a2b7c7388`, GeoX/panel_exp `496c317bc44c31a89aff805896863bd7eb637b7e`
**Date:** 2026-09-21

This packet is a cross-repository planning proposal. It does not modify MMM or
GeoX, replace their canonical roadmaps, create a contract or schema, or grant
spend, recommendation, optimization, runtime, pilot, production, or sibling
authority. Later work requires a separate task in the owning repository.

## 1. Operating model

The platform answers a business question at the highest scope that the model
and evidence actually support. It must distinguish:

```text
exploratory simulation
→ decision-supported recommendation
→ execution-eligible output
```

An unsupported or experiment-required question is returned as such, with the
missing evidence and a proposed next measurement. Warnings may permit
exploration, but a severe warning states the affected scope, the required
resolution, and whether execution is prohibited.

Ownership remains explicit:

| Responsibility | Owner |
|---|---|
| Fit, diagnostics, calibration compatibility, supported range, uncertainty, full-panel simulation, numerical optimization | MMM |
| Experiment design, assignment, power/MDE, readout, experimental truth | GeoX/panel_exp |
| Estimands, scope routing, evidence registry, claims, user workflow, planning evidence, approvals | MIP |
| Interpretation, question routing, and structured input collection only | LLM layer |

Simulation is not a recommendation; optimization is not approval; approval is
not execution. LLM suggestions become visible constraints, weights, or
scenarios and never silently alter an optimizer objective.

## 2. Prioritization and acceptance vocabulary

| Priority | Meaning | Entry bar |
|---|---|---|
| P0 | Safety or evidence prerequisite | Blocks downstream claims or prevents misleading decisions |
| P1 | High-value decision capability | Closes a material user decision gap with observable evidence |
| P2 | Advanced analytical capability | Requires validated P0/P1 scope and evidence |
| P3 | Operational convenience or scale | Does not change truth or authority |

Every row below must carry these metrics:

- decision value and risk reduction;
- observable input coverage;
- supported scope and calibration coverage;
- uncertainty and extrapolation rate;
- stability/reproducibility;
- implementation effort and dependencies;
- named accepting authority;
- version/fingerprint and re-verification trigger.

Acceptance never follows from prose alone. It requires a named artifact,
accepting role, exact reviewed SHA, and version-scoped re-verification.

## 3. Capability backlog

| ID | Priority | Capability and bounded outcome | Owner | Dependencies | Acceptance evidence / metric |
|---|---|---|---|---|---|
| CAP-001 | P0 | Estimand and evaluation protocol defines quantities, baseline, scope, horizon, non-claims, and R0 ownership | MIP | Merged DE-0 design | Accepted protocol with exact SHA; reverify on estimand, phase, or gate change |
| CAP-002 | P0 | Model applicability and decision-readiness registry records data, parameter, calibration, pooling, spend-support, uncertainty, and decision scope per model release | MIP + MMM | CAP-001 | Scope matrix resolves direct, policy-derived, restricted, or unsupported questions |
| CAP-003 | P0 | Package-diagnosable validity checks cover completeness, schema drift, sparsity, identifiability, extrapolation, lag, saturation, temporal drift, scenario validity, and optimizer stability | MMM | CAP-002 | Deterministic diagnostic artifact with affected scope, severity, action, and re-verification trigger |
| CAP-004 | P0 | Warning/refusal semantics make severe limitations actionable without blocking safe exploration | MIP + MMM | CAP-003 | Fixtures prove warning versus refusal behavior and explicit resolution text |
| CAP-005 | P1 | Scope-aware decision router maps each user question to supported model scope, calibration scope, decision permission, or experiment route | MIP | CAP-002, CAP-003 | Question-routing matrix and negative tests for unsupported scope |
| CAP-006 | P1 | High-level-to-low-level allocation contract conserves parent budgets and distinguishes joint optimization, policy disaggregation, and unsupported output | MIP + MMM | CAP-005 | Parent/child reconciliation report; provenance for user, model, policy, and LLM inputs |
| CAP-007 | P1 | Strategy and segment estimands define valid taxonomy, pooling status, supported dimensions, and direct versus inferred claims | MMM + MIP | CAP-001, CAP-006 | Strategy/segment estimand registry with calibration and uncertainty coverage |
| CAP-008 | P1 | Evidence-gap scanner ranks experiments by decision impact, uncertainty, sensitivity, information value, feasibility, cost, and risk | MIP + GeoX | CAP-002, CAP-005 | Ranked recommendation plus MIP→GeoX handoff; no automatic experiment authority |
| CAP-009 | P1 | Calibration coverage and freshness registry tracks experiment/model scope, estimand match, uncertainty, age, fingerprints, and re-verification triggers | MMM + MIP + GeoX | CAP-001, CAP-002 | Scope-specific calibration status and stale-evidence fixtures |
| CAP-010 | P1 | Remaining-horizon workflow refreshes data, derives spent/committed/remaining budget, locks sunk spend, and optimizes eligible remaining weeks | MMM + MIP | CAP-005, CAP-006 | Replayable mid-quarter fixture with missing-input prompts and exact budget conservation |
| CAP-011 | P1 | Explicit macro, promotion, pricing, and seasonality scenario overlays support full-panel forecasting without inventing futures | MMM + MIP | CAP-003, CAP-005 | Scenario manifest, lineage, uncertainty, supported-range and causal-limit disclosures |
| CAP-012 | P1 | Actual-outcome registry closes approved plan → realized outcome → evaluation → evidence refresh | MIP + MMM | CAP-001, CAP-009 | Immutable decision snapshot, outcome window, variance report, and recalibration trigger |
| CAP-013 | P1 | Risk-aware optimization supports expected-value, conservative, downside-constrained, and robust modes | MMM + MIP | CAP-003, CAP-009 | Expected value, uncertainty, downside, sensitivity, concentration, and stability report |
| CAP-014 | P2 | Interaction, halo, and cannibalization analysis compares additive and interaction/bundle models | MMM + GeoX | CAP-007, CAP-009 | Recovery, sensitivity, and experiment evidence before promotion |
| CAP-015 | P2 | Granular and strategy response surfaces are emitted only at supported estimand scope and reconcile to full-panel simulation | MMM | CAP-006, CAP-007, CAP-013 | Curve scope, allocation policy, uncertainty, support range, and aggregate reconciliation |
| CAP-016 | P2 | Incremental/hurdle reporting explains next-dollar decisions without replacing full-panel optimization | MMM + MIP | CAP-013 | Hurdle-rate report for incremental funding and finance explanation |
| CAP-017 | P3 | Guided diagnose → remediate → re-optimize workflow bundles existing freshness, fingerprint, calibration, and optimization checks | MIP | CAP-004, CAP-005, CAP-010 | End-to-end receipt with every check, correction, and final lineage |
| CAP-018 | P3 | Refresh and stale-model prompts identify when new data requires refit or revalidation rather than assuming freshness | MIP + MMM | CAP-003, CAP-009 | Data-as-of and structural-change diagnostics with explicit next action |

## 4. Package-diagnosable diagnostic contract

The following are immediate diagnostic surfaces because they can be measured
from MMM panels, configs, artifacts, or linked experiment evidence:

| Diagnostic | Observable inputs | Decision response |
|---|---|---|
| Coverage/schema | dates, keys, missingness, duplicates, fingerprints | block or restrict affected scope |
| Identifiability | variance, zero-share, correlation, effective sample size | pooled/weak/unsupported label |
| Extrapolation | recommended versus observed spend support | warn or refuse execution |
| Lag/saturation | residual autocorrelation, lag sensitivity, curve behavior | sensitivity report and revalidation |
| Temporal stability | rolling fits, holdouts, drift, forecast error | refit/reverify trigger |
| Granularity | cell counts, pooling, calibration coverage | direct, inferred, or unsupported claim |
| Scenario validity | overlay coverage, future dates, baseline consistency | supported scenario or hypothetical-only label |
| Optimizer stability | multistart, perturbation, posterior draws, boundary concentration | stable/fragile recommendation |
| Outcome feedback | plan, realized spend, outcome window, confounders | evidence refresh, not automatic causal success |

Observational diagnostics do not prove causality. They identify risk and missing
evidence; causal confirmation remains an experiment or other explicitly governed
design.

## 5. High-level-to-low-level decision process

For a user-supplied national or strategy budget:

1. MIP parses requested parent and child scopes.
2. The registry checks model and calibration support.
3. If supported, MMM jointly optimizes children under parent-budget and business constraints.
4. If not supported, MIP applies an explicit user/policy allocation rule and labels it inferred.
5. If neither is defensible, MIP returns an aggregate or experiment-required answer.
6. MMM runs full-panel simulation and reconciles child results to the parent.
7. MIP reports uncertainty, unsupported cells, winners/losers, and approval requirements.

## 6. Roadmap insertion and implementation rules

This packet is the source proposal, not a replacement roadmap. After review,
each owning repository should insert only its rows into its existing canonical
roadmap and link back to this packet. No row is considered implemented because
it appears here.

Every future agent task must:

1. use one repository, one owner, and one independently reviewable outcome;
2. declare owned/prohibited paths and exact observable behavior;
3. name dependencies, acceptance authority, evidence artifacts, and metrics;
4. preserve scope, calibration, warning/refusal, and authority boundaries;
5. record model/data fingerprints and re-verification triggers;
6. validate the exact frozen tree and publish a durable receipt;
7. stop at `ready_for_review` or a genuine Git-durable `blocked` state; and
8. defer cross-repository implementation to separately authorized owner tasks.

## 7. Current boundary and deferred work

This packet does not claim that any CAP row is complete. Current implementation
status must be read from the owning repository's live Git state and execution
files. MMM, GeoX, and MIP retain their own authority and roadmap truth.

Deferred successors include owner-roadmap insertion, MMM diagnostic/optimizer
implementation, GeoX experiment capability, MIP scope-router/outcome-registry
implementation, schema or contract adoption, and any recommendation, pilot, or
production authorization.

## References

- [MIP estimand protocol](../design/MIP_ESTIMAND_PROTOCOL_DESIGN_001.md)
- [MIP canonical roadmap](ROADMAP.md)
- [MIP cross-repository coordination protocol](../program/CROSS_REPOSITORY_COORDINATION_PROTOCOL.md)
- [MIP program charter](../program/PROGRAM_CHARTER.md)
