# MIP P2 Consumer Contract and Fixture Journey Design 001

## Scope and authority boundary

This is the MIP-owned design for P2, the certified planning-evidence lifecycle.
It defines consumer views, deterministic fixture expectations, and the report
contract. It does not define producer schemas, call MMM or GeoX packages,
calculate analytical values, authorize runtime integration, or authorize a
recommendation, execution, real data, persistence, pilot, or production.

The lifecycle is a bounded evidence journey:

```text
user-supplied or fixture-supplied baseline and candidate plans
→ GeoX governed readout
→ MMM calibration compatibility
→ MMM scenario comparison
→ MIP planning-evidence report
→ required human review
```

MIP treats a GeoX handoff state as input eligibility only. MMM alone owns the
subsequent experiment-to-model compatibility decision.

## Normalized MIP consumer views

The views below are adapter protocols, not copies of complete producer schemas.
All producer analytical values remain opaque, typed producer fields. MIP
validates shape and provenance, preserves values, resolves evidence state, and
uses them only for governed explanation.

| Consumer view | Producer artifact / wrapper | Required preserved fields | MIP rule |
|---|---|---|---|
| `GeoXReadoutConsumerView` | `GeoXArtifactEnvelope` containing `GeoXGovernedExperimentReadout` | artifact and experiment/readout identity; envelope, artifact, schema, and package versions; KPI, estimand, units, geography/time scope; method/instrument; effect and uncertainty as supplied; feasibility/method/freshness/handoff state; warnings, blockers; provenance and lineage; authorization flags | Accept only a supported envelope/artifact version; preserve the producer handoff state and never translate it into MMM compatibility. |
| `MMMCompatibilityConsumerView` | `MMMCalibrationCompatibilityResult` | artifact identity; schema/package versions; compatibility state (`compatible`, `compatible_with_warning`, `stale`, `incompatible`, or `blocked`); linked GeoX identity; model/run/configuration/dataset lineage; freshness; warnings, blockers, limitations; terminal status; authorization flags | Display MMM's state exactly; never recompute compatibility or convert warning/stale/incompatible/blocked into success. |
| `MMMSimulationConsumerView` | `MMMPublicSimulationExport` (`mmm_public_simulation_export_v1` candidate) | artifact identity; schema/package versions; baseline/candidate identities and requested scope; producer-supplied full-panel means and delta-mu; uncertainty availability/semantics; supported-range, extrapolation/restriction result; diagnostics, limitations, warnings, blockers; terminal state; run/model/configuration/panel/dataset lineage; authorization flags | Explain only an eligible, terminal producer artifact; absence of uncertainty stays unavailable, and a restriction stays a restriction. |

`GeoXReadoutConsumerView.handoff_eligibility` has this GeoX-owned state
vocabulary:

- `eligible_for_compatibility_evaluation`;
- `ineligible_for_calibration_handoff`; and
- `blocked_for_handoff`.

GeoX determines readout validity and this handoff eligibility. MMM alone
determines `compatible`, `compatible_with_warning`, `stale`, `incompatible`, or
`blocked` model-specific compatibility. MIP validates, routes, explains, and
reports producer results; it does not infer either analytical decision.

Common validation behavior for every view:

- reject unknown schema/package versions as incompatible rather than guessing;
- retain producer IDs, versions, lineage, warnings, blockers, limitations,
  terminal status, and authorization flags verbatim in normalized evidence;
- distinguish missing, stale, blocked, failed, superseded, and contradictory
  evidence; and
- emit a typed non-analytical readiness/failure context when the view is not
  explainable.

## Deterministic fixture-journey matrix

Each fixture journey has fixed producer inputs, expected consumer resolution,
safe explanation boundary, and a planning-evidence report status. Fixtures are
synthetic or analytically certified; they never imply package execution or real
customer data.

| Journey | Required producer evidence and expected MIP resolution | MIP may say | MIP must not say | Report status |
|---|---|---|---|---|
| Success | Eligible GeoX handoff; MMM `compatible`; terminal successful comparison with available uncertainty and supported range | The supplied candidate has the producer-reported full-panel delta-mu and uncertainty under the stated scope. | It is causally certain, approved, or ready to execute. | `evidence_ready_human_review_required` |
| Success with warning | Successful inputs plus producer warning/limitation | The bounded comparison is available with the listed warning. | The warning is immaterial or has been cleared. | `evidence_ready_with_warning_human_review_required` |
| Stale evidence | GeoX or MMM stale state/freshness | The evidence is stale and cannot support a current planning conclusion. | The stale result remains current. | `stale_evidence` |
| Incompatible experiment and model | GeoX eligible handoff plus MMM `incompatible` | MMM found the supplied experiment evidence incompatible with the model context. | GeoX or MIP calculated a replacement compatibility result. | `incompatible_evidence` |
| Blocked experiment handoff | GeoX `blocked_for_handoff` or blocker | The experiment readout is blocked for handoff and no model comparison is available. | A simulation can proceed. | `blocked_evidence` |
| Blocked simulation | Eligible input plus MMM terminal blocked state | MMM blocked the comparison for the producer-stated reason. | A delta-mu, recommendation, or workaround. | `blocked_evidence` |
| Failed producer artifact | Producer terminal failure | The producer artifact failed; the report preserves the typed failure context. | Failure establishes an analytical result. | `producer_failure` |
| Diagnostic-only evidence | Producer marks diagnostic-only | The artifact is diagnostic context, not decision-ready evidence. | It supports a planning conclusion. | `diagnostic_only` |
| Research-only evidence | Producer marks research-only | The artifact is research-only and excluded from planning evidence. | It is decision-authoritative. | `research_only` |
| Unavailable uncertainty | Successful comparison with unavailable/restricted uncertainty semantics | MMM supplied the comparison but uncertainty is unavailable or restricted. | An uncertainty interval or confidence level. | `evidence_with_unavailable_uncertainty` |
| Supported-range restriction | Successful comparison with producer range restriction/extrapolation state | The result is restricted to the producer-stated supported range. | It is validated beyond that range. | `evidence_with_range_restriction` |
| Conflicting or superseded artifacts | Competing lineage, supersession, or contradictory terminal evidence | MIP found conflicting or superseded evidence and requires resolution. | It selected a preferred analytical result. | `conflicting_or_superseded_evidence` |

## Canonical P2 planning-evidence report

`PlanningEvidenceReport` is an MIP report contract, not a recommendation. Its
minimum fields are:

1. `business_question`;
2. `evidence_inventory`, including availability, freshness, conflict, and
   supersession state;
3. `geox_readout_summary` and `geox_handoff_eligibility`;
4. `mmm_compatibility_result`;
5. user- or fixture-supplied `baseline_plan` and `candidate_plan` identities;
6. producer-supplied `full_panel_delta_mu`;
7. `uncertainty_availability_and_semantics`;
8. `supported_range_and_extrapolation_status`;
9. `warnings`, `blockers`, `diagnostics`, and `limitations`;
10. `permitted_claims` and `prohibited_claims`;
11. artifact schema/package versions and complete lineage;
12. `human_review_required: true`; and
13. terminal `report_status` from the fixture matrix.

The report must identify a missing or non-explainable producer artifact rather
than fabricate a value. A success report remains planning evidence and does not
contain approval, execution, or recommendation authority.

## Safe-claim policy

For a bounded success, MIP may describe the producer-supplied comparison,
scope, delta-mu, uncertainty availability, range state, warnings, limitations,
and required human review. With unavailable uncertainty, it may state only
that the producer marked uncertainty unavailable or restricted. With stale,
incompatible, diagnostic-only, research-only, blocked, failed, conflicting, or
superseded evidence, it may explain the typed evidence state and next required
evidence, but not give an analytical conclusion.

MIP must never claim causal certainty beyond the GeoX artifact; invent
uncertainty; imply production readiness; give an approved budget
recommendation; automatically calibrate or refit MMM; choose treatment markets;
or claim execution authority. The LLM may explain these governed states but may
not alter producer outputs or override blocked evidence.

## Later D6 consumer requirements

Later runtime integration must pin expected producer schema and package
versions, define required/optional fields and compatibility behavior, preserve
warning/failure/stale/incompatible handling, define release and rollback order,
record last-known-good pins, document migration/deprecation, and name GeoX,
MMM, and MIP producer/consumer owners. This design is D6 consumer input only;
it does not claim Gate 1 completion.

## Producer readiness boundary

Runtime package integration remains blocked until GeoX `main` contains a
numerical-truth fixture validation checkpoint, final governed readout contract,
certified readout fixtures, a governed readout builder/package entrypoint,
stable state semantics, D6 compatibility evidence, and exact schema/package
pins. MMM `main` must contain `MMMPublicSimulationExport`,
`MMMCalibrationCompatibilityResult`, registered parsers/package exports,
certified fixtures, verified dataset/input lineage, final validation, and exact
commit/package pins.

No design element in this document authorizes a GeoX or MMM package call,
fixture integration, storage implementation, real data, live engine, simulation
runtime, optimization, recommendation, treatment assignment, pilot, or
production capability.
