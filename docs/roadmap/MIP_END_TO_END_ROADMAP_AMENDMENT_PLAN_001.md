# MIP End-to-End Roadmap Amendment Plan 001

This is a proposed amendment, not a replacement for the canonical roadmap.

1. **R0 — Program ownership and environment matrix (MIP):** define owners,
   entry/exit criteria, public-demo/pilot/production boundaries, rollback and
   support ownership.
2. **R1 — Core LLM evaluation dataset and benchmark v1 (MIP):** versioned
   conversational, multi-turn, governance/refusal, terminology, cost/latency,
   human-evaluation and provider-comparison coverage. Gate provider/prompt/model
   promotion on regression thresholds and define rollback, cost/latency limits,
   and numerical-truth ownership (MMM/GeoX analytical truth; MIP scenarios).
3. **R2 — Resolver and artifact lifecycle (MIP):** only after R1; identity,
   lineage, storage, access, retention, migration, staleness and failure states.
4. **R3 — Artifact-grounded benchmark (MIP with MMM/panel_exp truth owners):**
   versioned expected truth and grounding checks after R2 exists.
5. **R4 — Cross-repo integration release gate (all owners):** compatibility,
   fixture/runtime adapter, failure behavior, release order and rollback for
   GeoX→MIP, MIP→MMM, MMM→MIP, and MIP workflows.
6. **R5 — Pilot security/operations gate (MIP):** tenancy, data lifecycle and
   deletion, observability, jobs/recovery, SLOs, incident/DR, cost controls,
   human approval/override, and product-success metrics.
7. **R6 — Limited pilot then production authorization (program owners):**
   explicit success metrics, support, rollback, release and deprecation gates.

Deferred until their prerequisites pass: live engine execution, simulation,
optimization, budget recommendations, and production promotion.

The amendment review must explicitly keep Groq acceptance-004/provider promotion,
the artifact and requirement resolver, deeper Phase F, uploaded-data expansion,
live engine execution, simulation, optimization, and recommendation work frozen
until the canonical roadmap rebase is ratified.
