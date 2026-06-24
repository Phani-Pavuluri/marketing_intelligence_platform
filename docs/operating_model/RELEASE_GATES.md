# Release Gates

Release gates are deterministic checks that cap confidence tiers and permit promotion. They are code-defined in `mip.evaluation` (future) and documented here as normative requirements.

## Gate: Experiment Result Usage

An experiment result may be cited in orchestration or used for calibration only if:

| Check | Requirement |
|-------|-------------|
| Registry | Evidence ID exists with complete metadata |
| Quality | Quality score ≥ policy threshold or explicit waiver |
| Compatibility | Compatibility verdict `pass` for target model/panel |
| Uncertainty | Interval or posterior summary present |
| Freshness | Age ≤ policy for calibration; stricter for decision-ready citation |
| Tier ceiling | Failed any check → `research only` or `blocked` for calibration |

**Promotion to “calibration-approved”** is a separate flag on the evidence record, not automatic on ingest.

## Gate: MMM Model Promotion

A model artifact may be marked **production** only if:

| Check | Requirement |
|-------|-------------|
| Decision surface | Certified full-panel Δμ contract emitted |
| Stability | Δμ perturbation tests within thresholds |
| Replay | Replay benchmark pass on reference slices |
| Diagnostics | Required diagnostics present (coverage, residual checks per policy) |
| Versioning | Immutable artifact hash stored |
| Decomposition | Curves/decomposition explicitly tagged diagnostic-only |

Non-promoted artifacts: max tier `diagnostic only` for MMM-derived planning.

## Gate: Calibration Signal Acceptance

A calibration event may apply to a promoted model only if:

| Check | Requirement |
|-------|-------------|
| Evidence | Source experiment `calibration-approved` |
| Mapping | Channel/geo/time mapping certified |
| Conflict | No unresolved conflict with other calibration-approved signals |
| Audit | Event logged with before/after parameter touch list |

Otherwise: block calibration; retain evidence in registry.

## Gate: Recommendation Readiness

A recommendation may reach `decision-ready` only if:

| Check | Requirement |
|-------|-------------|
| Contract | Full recommendation contract validation |
| Engines | All referenced engines promoted for claimed estimands |
| Tier inputs | No upstream `blocked` or incompatible tier mixing |
| Uncertainty | Present for all decision estimands cited |
| Unsupported claims | List populated; no silent gaps |
| Approval | Human approval recorded if realloc exceeds policy threshold |

Material reallocation thresholds are organization-specific constants in config (future).

## Gate: LLM Workflow Promotion

A workflow graph may be enabled in production orchestration only if:

| Check | Requirement |
|-------|-------------|
| Tools | All steps call registered, versioned tools |
| Boundaries | Reviewed against ORCHESTRATION_BOUNDARIES.md |
| Eval | Orchestration eval pass rate ≥ policy on held-out intents |
| Traces | Decision trace schema enforced on every run |
| Autonomy | No step commits spend or model promotion without human gate |

Failed gate: workflow remains disabled or sandbox-only.

## Gate Summary Table

| Asset | Promoted state | Failure default |
|-------|----------------|-----------------|
| Experiment | `calibration-approved` | Cite as research/blocked |
| MMM artifact | `production` | Diagnostic-only Δμ |
| Calibration event | `applied` | No model change |
| Recommendation | `decision-ready` | Downgrade or block |
| Workflow | `production-enabled` | Disabled |

## Waiver Process

Waivers for gate failures require recorded approver, reason, expiry, and max tier ceiling (never above `directional` for waived causal inputs unless executive policy exists outside this doc).

Initial implementation: gate functions return `blocked` with reason codes until engines exist.
