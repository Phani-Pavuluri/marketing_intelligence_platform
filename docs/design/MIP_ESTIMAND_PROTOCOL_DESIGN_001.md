# MIP Estimand Protocol Design 001

**Status:** design proposal (non-normative)
**Owner:** MIP program owner
**Acceptance authority:** MIP program/governance owner
**Date:** 2026-09-19
**Register row:** DE-0 (`unchecked` / `not_eligible` → `evidence_submitted` by the producing task; `accepted` only by a separate successor)

This document is a design proposal. It is not a new MIP contract and not a
cross-repository schema. It creates no code, schema, contract, runtime,
analytical, or authority change, and it grants no independent execution or
capability authority. It exists so that DE-1/DE-3 criteria have a fixed
measurable-quantity vocabulary to finalize against.

## Measurable quantities per lifecycle stage

| Lifecycle stage | Measurable quantity | Unit / form |
|---|---|---|
| Business question (P0) | Stated decision and its observable success metric | Named metric with grain and window |
| Evidence readiness (P1) | Input coverage: time grain, history length, media variation, controls present | Readiness checklist with thresholds |
| Measurement (P1–P2) | Calibrated effect estimate with uncertainty at a declared grain | Estimate ± uncertainty, grain, scope |
| Experiment calibration (P2) | Compatibility state between experiment readout and model panel | Typed terminal state (success, warning, incompatible, stale, blocked, failed) |
| Scenario comparison (P2/P6) | Baseline-versus-candidate delta at full panel with lineage | Delta-mu with provenance pin |
| Candidate generation (P6) | Candidate set with constraints and provenance | Versioned candidate list |
| Recommendation proposal (P6) | Proposal packet referencing evidence rows | Packet with evidence links |
| Human approval (P6–P8) | Approval decision with identity and scope | Signed approval record |
| Reporting (P2/P5) | Planning-evidence report with lineage and claim limits | Report with lineage block |
| Outcome tracking (P7/P8) | Observed outcome against the declared success metric | Measured outcome with window |

## Estimand versus planning-quantity distinction

- An **estimand** is the quantity to be measured (e.g., incremental effect
  of a channel at a grain and window). It is defined before measurement and
  does not change when a plan changes.
- A **planning quantity** is a quantity used inside a human-supplied plan
  comparison (e.g., a budget shift under comparison). It is bounded by the
  plan and never promoted into measured truth.
- No planning quantity may be cited as an estimand without passing the
  measurement gates (R1/R3) and, where cross-repository, the R4 release
  evidence.

## Lifecycle/R0 ownership mapping

- MIP owns the protocol vocabulary, intake coordination, readiness
  evaluation, evidence assembly, and governed explanation.
- MMM owns fitting, diagnostics, calibration treatment, supported-range,
  and MMM numerical truth.
- GeoX/panel_exp owns experiment validation, power/MDE, matching and
  assignment computation, and experiment numerical truth.
- The LLM explains and proposes only when explicitly authorized; it never
  creates analytical truth and never approves.
- Humans approve consequential decisions (R0); no approval is execution
  authorization by itself.

## Boundaries

- This protocol standardizes names, grains, windows, and claim limits. It
  does not compute, certify, or consume any numerical result.
- Producer truth stays in the owning engine repository at exact pins with
  consumer verification; this document references that rule without
  restating engine semantics.
- Real or customer data, uploads, persistent product artifacts, live
  engines, simulation, optimization, recommendations, pilot, and production
  remain separately authorized and are out of scope here.

## Explicit non-claims

- This proposal claims no universally best MMM, no optimal mix, and no
  causal lift.
- Fixture evidence cited under this protocol does not establish production
  readiness.
- A certified fixture pair, where it later exists, is planning evidence
  for human approval — not a recommendation, spend execution, or treatment
  assignment.

## Scope, version, and fingerprint fields

- **Scope:** v1, MIP planning-evidence vocabulary only.
- **Version:** `estimand_protocol_v1`.
- **Fingerprint fields:** document SHA, register row DE-0 status, governing
  gate set (R0–R6), and the exact pins of any referenced producer evidence
  at acceptance time.

## Re-verification triggers

Re-verify this protocol when any of the following changes: the estimand
set, a lifecycle phase definition, a governing gate, the R0 ownership
mapping, a producer evidence contract, or a version/scope expansion. A
triggered re-verification is a separately authored task; it is not implied
by the trigger.

## Producer versus accepting authority

- **Producer:** the DE-0 design task (this proposal's authoring branch).
- **Accepting authority:** MIP program/governance owner, exercised through
  exact-head review. The exact approved review-head SHA is review evidence:
  it proves which tree was reviewed and does not by itself identify who
  owns acceptance.

## Authority impact

None. This proposal grants no spend, optimization, recommendation,
real-data, pilot, production, promotion, or runtime authority.

## References

- [Decision lifecycle roadmap](../roadmap/ROADMAP.md)
- [Decision-Evidence Gap Register](../roadmap/ROADMAP.md) (DE-0 row)
- [Cross-repository coordination protocol](../program/CROSS_REPOSITORY_COORDINATION_PROTOCOL.md)
- [Authority and freeze matrix](../program/AUTHORITY_AND_FREEZE_MATRIX.md)
