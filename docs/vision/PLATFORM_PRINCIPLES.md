# Platform Principles

These principles govern design, implementation, and review across MIP. They are non-negotiable defaults unless an ADR explicitly documents an exception.

## 1. Statistical systems compute; LLMs orchestrate

All causal estimation, optimization, calibration math, and numerical diagnostics run in **certified analytical engines** with versioned code, tests, and release gates. Language models plan workflows, select tools within policy, format explanations, and surface uncertainty—they do not replace estimators.

**Implication:** No “LLM does the MMM” paths. Orchestration calls engines; engines return typed contracts.

## 2. Experiments calibrate models

Randomized and quasi-experimental evidence **constrains and calibrates** MMM and planning surfaces. Experiments are not treated as infallible truth: each signal passes compatibility, quality, uncertainty, and freshness checks before influencing production decisions.

**Implication:** Experiment ingestion, registry, and gating precede automated calibration in production workflows.

## 3. Transparency over autonomy

Reliability, inspectability, and diagnosability outweigh agentic convenience. Users must see what ran, on what data, with what assumptions, and what could not be supported.

**Implication:** Workflow traceability, decision traces, and blocked states are first-class—not afterthought logging.

## 4. Explainability by default

Every user-facing analytical output and recommendation includes rationale structured for audit: evidence pointers, diagnostics, uncertainty summaries, and explicit **unsupported claims** (statements the system refuses to certify).

**Implication:** Trust layer is not optional packaging; it is part of the output contract.

## 5. Strategic planning, not platform bidding

In scope: mix-level budget planning, scenario analysis, constraint-aware allocation. Out of scope: user-level auction optimization, bid multipliers, and real-time platform bidding automation.

**Implication:** Optimization module targets portfolio planners; it does not integrate as a bid agent.

## 6. Decision contracts over informal interpretation

Estimands, evidence bundles, model outputs, and recommendations are **typed contracts** (schemas with validation), not free-form JSON or narrative-only answers. Informal interpretation may supplement contracts but never replace them for decision-grade outputs.

**Implication:** `contracts/` is foundational; orchestration and UI consume contracts, not raw engine internals.

## Application in Review

| Question | Expected answer |
|----------|-----------------|
| Where does this math run? | In a named engine with tests and gates |
| Can an LLM skip a gate? | No |
| Is this decision- or diagnostic-grade? | Explicit tier per ADR-001 and trust architecture |
| What if evidence is weak? | Downgrade tier or block; do not hedge in prose |

Related: [../architecture/ORCHESTRATION_BOUNDARIES.md](../architecture/ORCHESTRATION_BOUNDARIES.md), [../adr/](../adr/).
