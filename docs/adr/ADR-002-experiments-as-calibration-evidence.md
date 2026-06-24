# ADR-002: Experiments as Calibration Evidence

**Status:** Accepted  
**Date:** 2026-05-28  
**Deciders:** Platform architecture (initial constitution)

## Context

Incrementality experiments (geo, panel, lift) are often treated as ground truth for MMM calibration. In practice, experiments differ in design quality, scale, duration, and alignment with the model panel. Blindly forcing experiment point estimates into model priors causes miscalibration, overconfidence, and silent failures when experiments are stale or incompatible.

MIP needs a principled role for experiments in the measurement stack.

## Decision

1. Experiments are **calibration evidence and causal anchors**, not automatic truth.
2. Before an experiment result may influence a **promoted** MMM artifact or production calibration, it must pass:
   - **Compatibility** with model geography, time grain, channel mapping, and outcome definition
   - **Quality** checks (design, power proxies, interference, stability)
   - **Uncertainty** representation (intervals or posterior summaries required for calibration use)
   - **Freshness** policy (age limits defined in release gates)
3. Failed checks result in **registry retention** (for audit) but **blocked or research-only** tier for calibration application—not deletion of the record.
4. Calibration events are **auditable**: which evidence ID, which model version, which parameter touch, and which gate snapshot.

## Consequences

### Positive

- Reduces harmful fusion of incompatible geo tests with national MMM panels
- Makes disagreement between experiment and model an explicit, reviewable state
- Supports evidence registry as system of record

### Negative

- More upfront metadata burden on experiment ingestion
- Some stakeholders expect “experiment always wins”; requires change management
- Slower path to auto-calibration until quality pipelines mature

### Operational

- `mip.evidence` owns registry and gate orchestration stubs
- `mip.experimentation` produces quality and compatibility contracts
- Calibration loop (roadmap phase 4) depends on this ADR

## Alternatives Considered

| Alternative | Why not chosen |
|-------------|----------------|
| **Experiments as sole truth; MMM secondary** | Ignores panel-wide counterfactual structure; poor for planning grids |
| **MMM only; ignore experiments** | Leaves systematic bias uncorrected; wastes costly tests |
| **Automatic calibration on ingest** | No gate for compatibility or freshness |
| **Discard failed experiments** | Loses audit trail and learning from bad fits |

## References

- [../glossary/MEASUREMENT_GLOSSARY.md](../glossary/MEASUREMENT_GLOSSARY.md)
- [../operating_model/RELEASE_GATES.md](../operating_model/RELEASE_GATES.md)
