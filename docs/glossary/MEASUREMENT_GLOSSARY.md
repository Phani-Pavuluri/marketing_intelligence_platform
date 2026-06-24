# Measurement Glossary

Key terms for experimentation, MMM, trust, and operations in MIP.

## GeoX

Geographic experiment design: units are markets or regions; treatment and control are assigned geographically. Common for media incrementality when user-level randomization is infeasible. Requires interference and spillover diagnostics.

## panel experiment

Experiment run on a defined **panel** of units (geos, stores, cohorts) aligned with MMM or planning data. Panel definition must match registry metadata for compatibility checks.

## A/B test

Randomized experiment typically at user or session level. In MIP, supported as evidence when mapped to outcomes and channels relevant to mix planning; often **not** directly interchangeable with geo lift without aggregation and compatibility rules.

## lift study

Study measuring incremental effect of media or marketing action, often via holdout or synthetic control. Umbrella term; specific design must be recorded in evidence metadata.

## MMM (media mix model)

Statistical model relating media inputs (and controls) to outcomes over time, used for counterfactuals and planning. MIP MMM emphasizes **Δμ surfaces** for decisions and separates diagnostic outputs.

## calibration

Process of adjusting model parameters or priors using **gated** experiment evidence. Calibration is an auditable event, not a one-time spreadsheet merge.

## replay validation

Re-running historical decisions or model outputs on frozen inputs to detect drift, bugs, or gate regressions. Part of evaluation philosophy and release gates.

## synthetic world

Simulated data environment with known ground-truth effects for method benchmarking during research intake. Does not replace replay on real data for promotion.

## trust score

Composite indicator of output reliability derived from diagnostics, tier, and evidence coverage (future implementation). Not a substitute for reading diagnostics and tier.

## decision trace

Immutable log of workflow steps, tool calls, contract hashes, approvals, and tier assignments for a user or API session outcome.

## evidence registry

System of record for experiment results, calibration events, compatibility verdicts, and freshness. Source for what orchestration may cite.

## recommendation contract

Typed bundle for a recommendation: actions, estimands, evidence IDs, assumptions, uncertainty, diagnostics, confidence tier, unsupported claims, and required approvals. Explanations are generated from this contract, not vice versa.

## Related

- [ESTIMANDS.md](./ESTIMANDS.md)
- [../architecture/TRUST_ARCHITECTURE.md](../architecture/TRUST_ARCHITECTURE.md)
