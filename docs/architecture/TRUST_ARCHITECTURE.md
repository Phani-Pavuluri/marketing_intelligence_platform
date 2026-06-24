# Trust Architecture

Trust is how MIP makes analytical outputs auditable and safe to use. It is implemented as contracts, diagnostics, and tiering—not as marketing copy around charts.

## Core Trust Objects

### Evidence

Registered artifacts that support a claim: experiment results, replay outcomes, model versions, calibration events. Evidence entries link to source systems, ingestion time, and compatibility tags.

### Diagnostics

Engine-computed checks: fit quality, stability, constraint violations, data coverage, identifiability warnings, replay deltas. Diagnostics are structured fields, not LLM commentary.

### Uncertainty

Intervals, posterior summaries, sensitivity ranges, and scenario bands attached to estimands. Uncertainty must be present for decision-grade tiers or the output is downgraded.

### Calibration quality

Scores and flags for how well experiment evidence aligns with model structure: geo coverage match, time alignment, spend scale compatibility, sign consistency. Poor calibration quality blocks automatic prior updates.

### Experiment quality

Design strength, power proxies, interference risk, pre-trend checks, and post-period stability. Low-quality experiments may remain in the registry as research-only.

### Optimization confidence

Feasibility proof, binding constraints, objective landscape sensitivity (e.g., flat regions of Δμ), and scenario stability under perturbations.

### Recommendation rationale

Machine-readable links from each recommendation clause to: estimand, engine version, evidence IDs, diagnostics passed/failed, and assumptions list.

### Workflow traceability

Decision trace: ordered steps, tool invocations, parameter hashes, human approvals, and timestamps. Enables replay and incident review.

## Confidence Tiers

Every user-facing analytical output and recommendation receives exactly one tier.

| Tier | Meaning | Typical use |
|------|---------|-------------|
| **decision-ready** | Gates passed; uncertainty and evidence sufficient for approved decision workflows | Signed budget scenarios within policy |
| **directional** | Useful signal with material gaps; not for automatic commitment | Exploration, prioritization |
| **diagnostic only** | Explains model behavior; not an estimand for commitment | Curves, decomposition, attribution views |
| **research only** | Prototype, benchmark, or ungated evidence | Method development, intake prototypes |
| **blocked** | Failed gate or policy; must not drive automated or silent decisions | Stale model, incompatible experiment, solver infeasible |

Tier assignment is **deterministic** from gate rules and engine outputs. Orchestration may explain tiers but not upgrade them.

## Tier Downgrade Rules (Examples)

- MMM artifact not promoted → max tier `diagnostic only` for Δμ claims
- Experiment fails freshness → cannot support `decision-ready` calibration
- Missing uncertainty on incremental estimand → cap at `directional`
- Optimization on diagnostic-only surface → `blocked` for allocation recommendations

## Unsupported Claims

Outputs must include an explicit list of **unsupported claims**: questions the user asked that the system cannot certify with current evidence and gates. Silence is not allowed—if the orchestration layer would otherwise speculate, it must list the claim as unsupported.

## Trust Score (Future)

A composite index derived from diagnostics, tier, and evidence coverage—not a single LLM judgment. Definition and weighting live in `mip.trust` once engines exist. Initial repository documents semantics only.

## Integration Points

```
Engine raw output → contract validation → diagnostics enrichment
       → tier assignment → recommendation contract → orchestration explain
```

Release gates in [../operating_model/RELEASE_GATES.md](../operating_model/RELEASE_GATES.md) map directly to tier ceilings.
