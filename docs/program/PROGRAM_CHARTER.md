# Program Charter

**Status:** approved program memory; no execution authority
**Owner:** MIP program and control-plane owners
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** MIP `89caf56e73e814b6f5e0d0584536f8705ac97803`; MMM `origin/main` `9a3aa5cb9a48c9a59d45e266685228835237f328`; GeoX `origin/main` `860182386c39f487747de5f43e67a31e9978e57c`
**Update trigger:** a merged ownership, authority, lifecycle, or repository-checkpoint change.

## Goal and lifecycle

The Causal Marketing Intelligence Platform helps marketing decision makers
understand governed evidence before they act. Its enduring lifecycle is:

```text
business question → evidence readiness → causal measurement
→ experiment-to-MMM compatibility → scenario comparison → planning evidence
→ candidate generation → recommendation proposal → human approval → execution
→ outcome tracking and learning
```

P0–P8 remains the primary product roadmap. R0–R6 remains the binding
cross-cutting gate system for authority, evaluation, artifacts, grounded
behavior, release, security/operations, and pilot/production.

## Ownership and boundaries

- **GeoX:** experiment validity, analytical truth, readout handoff eligibility,
  effect/uncertainty/method/scope/freshness/provenance. Its analytical artifact
  is `GeoXGovernedExperimentReadout`; `GeoXArtifactEnvelope` is transport only.
- **MMM:** model-specific compatibility, fitting/diagnostics/calibration,
  scenario computation, full-panel candidate-minus-baseline delta-mu,
  supported-range/uncertainty, and optimizer numerical truth. Its artifacts are
  `MMMCalibrationCompatibilityResult` and `MMMPublicSimulationExport`.
- **MIP:** consumer validation/normalization, artifact resolution, workflow
  orchestration, safe explanation, claims control, planning-evidence reports,
  and interaction.
- **LLM:** may interpret, route, ask for information, and explain governed
  outputs. It does not recreate engine truth, choose treatment markets, approve,
  or execute.

Engine-owned truth is never recreated by MIP or the LLM. Simulation is not a
recommendation; optimizer output is not approval; proposal is not approval;
approval is not execution; implemented is not validated; validated is not
production-authorized.

## Evidence precedence and stale-state rule

Precedence is: (1) verified repository state and committed runtime behavior;
(2) these canonical program-state files; (3) active contracts, ADRs, roadmaps,
and validation reports; (4) archived/superseded documents; (5) chat summaries.
A lower-ranked source cannot override a higher-ranked one.

When a SHA, artifact, branch, or capability cannot be verified: mark it
unverified; inspect the owning repository; do not infer completion or authorize
dependents; update this packet only after verification.

## Shared status vocabulary

`observed`, `proposed`, `approved`, `authorized_for_execution`, `in_progress`,
`implemented`, `validated`, `merged`, `blocked`, `deferred`,
`diagnostic_only`, `research_only`, `superseded`, and `retired` have distinct
meanings. In particular, `approved != authorized_for_execution`,
`implemented != validated`, and `validated != production_authorized`.

## Enduring non-goals

This charter does not authorize live engines, customer data, uploads, customer
artifact persistence, scheduling, optimization, recommendations, treatment
assignment, pilots, or production. These require their applicable R0–R6 gates
and separate explicit authorization.
