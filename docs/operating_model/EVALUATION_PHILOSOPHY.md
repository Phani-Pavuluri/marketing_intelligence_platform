# Evaluation Philosophy

MIP evaluates components by **role**: orchestration is not judged like MMM; recommendations are not judged like retrieval. Each layer has metrics tied to contracts and gates, not generic “helpfulness.”

## Principles

1. **Evaluate the estimand, not the story** — success requires correct tier, uncertainty, and diagnostics, not fluent prose.
2. **Separate offline benchmarks from production gates** — synthetic and replay scores inform promotion; they do not auto-promote.
3. **Fail closed** — ambiguous eval outcomes map to blocked or research-only, not silent pass.
4. **Regression-first** — new releases must not break prior gate snapshots on reference datasets.

## Retrieval Evaluation

When orchestration or tools retrieve documents, registry entries, or prior traces:

- Precision/recall on **correct evidence IDs** for a fixed query set
- Penalty for retrieving stale or wrong-tier artifacts
- No metric that rewards volume of retrieved text

*Applicable in later phases when RAG supplements registry lookups; registry remains authoritative for decision paths.*

## Answer Evaluation

For natural language explanations of **contract-backed** answers:

- Faithfulness: every numerical claim maps to a contract field
- Completeness: tier, uncertainty, and unsupported claims present when required
- Hallucination rate on held-out sessions (must be near zero for numbers)

Does not apply to uncertified “open chat” — out of scope for MIP.

## Experimentation Evaluation

- Design quality classifier calibration
- Compatibility rule accuracy vs human adjudication set
- Coverage of uncertainty intervals (where defined)
- Freshness violation detection rate

## MMM Evaluation

- Δμ stability under input perturbations (decision surface)
- Replay error vs held-out outcomes where defined
- Diagnostic separation: curves/decomposition must not be used as pass/fail for promotion without Δμ criteria
- Runtime and artifact reproducibility

## Calibration Evaluation

- Post-calibration improvement on replay with **no** degradation on incompatible holdouts
- False calibration rate when gates are intentionally stressed
- Audit completeness of calibration events

## Optimization Evaluation

- Constraint satisfaction rate
- Objective value vs brute-force on small grids (synthetic)
- Sensitivity: allocation stability under Δμ noise
- Infeasibility handling (must return blocked, not best-effort junk)

## Recommendation Evaluation

- Contract schema compliance
- Tier correctness vs gate oracle
- Human review outcomes for material reallocations (approval appropriateness)
- Unsupported-claims recall (user questions left unanswered vs falsely answered)

## Orchestration Evaluation

- Correct tool selection on scripted intents
- Gate bypass attempts (must fail 100%)
- Trace completeness
- Latency and cost within budgets

Orchestration must never be the sole eval for causal accuracy—that belongs to engines.

## Harness Location

Implementation targets `mip.evaluation` with pytest suites per phase. Initial repository contains philosophy only.

See [RELEASE_GATES.md](./RELEASE_GATES.md) and [RESEARCH_INTAKE_PROCESS.md](./RESEARCH_INTAKE_PROCESS.md).
