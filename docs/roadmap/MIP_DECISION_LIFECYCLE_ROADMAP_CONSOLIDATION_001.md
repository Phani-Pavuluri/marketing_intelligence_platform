# MIP Decision Lifecycle Roadmap Consolidation 001

## Purpose and verified evidence

This docs-only consolidation makes the trustworthy marketing decision lifecycle
the primary MIP product roadmap. It preserves—not replaces—the completed audit,
ratification, amendment, execution-rebase, and classification-review evidence.

| Repository | Committed evidence used | Treatment |
|---|---|---|
| MIP | `6c73643370c43b4b22bbb7cab264ccf5a5254fc7` | Classification review is complete evidence; it grants no execution authority. |
| MMM | `da8bdbe1cc6254d2a09602568b63689aa9a1b404` on `origin/main` | Committed checkpoint only; dirty local work excluded. |
| GeoX/panel_exp | `d9c9ac038c16646779c26400117379b18f4725a8` on `origin/main` | Committed checkpoint only; local work excluded. |

The steering correction avoids treating components or governance mechanics as
the product outcome. The product story is:

```text
Business question → evidence readiness → measurement → experiment calibration
→ scenario comparison → candidate generation → recommendation proposal
→ human approval → reporting → outcome tracking and learning
```

## Canonical product phases

| Phase | Title | Outcome and boundary |
|---|---|---|
| P0 | Product, ownership, and authority contract | Defines MIP, MMM, GeoX, LLM, human, and environment authority boundaries. |
| P1 | Minimum trusted analytical evidence | Engine-owned certified fixture truth, typed lineage, limitations, and terminal states. |
| P2 | Certified planning evidence lifecycle | Fixture-backed GeoX → MMM → MIP journey for human-supplied plan comparison. |
| P3 | LLM and artifact-grounding evaluation | Versioned benchmark and target-environment operational evidence; no independent provider-promotion authority. |
| P4 | Certified package integration | Real package entrypoints on certified fixtures with deterministic replay and rollback. |
| P5 | Artifact lifecycle and historical memory | Governed identity, lineage, state, retention/deletion, access, and historical decision memory. |
| P6 | Simulation, candidate generation, and recommendation workflows | Separates simulation, optimizer candidate, proposal, approval, execution, monitoring, revocation, and rollback. |
| P7 | Limited real-data pilot | Controlled advisory pilot after security, lifecycle, operations, runtime certification, and explicit authorization. |
| P8 | Production and expansion | Production only after successful pilot evidence and separately authorized capabilities. |

## R0–R6 cross-cutting gates

R0–R6 remain the binding controls across every product phase: ownership and
environments (R0); benchmark/promotion governance (R1); resolver and artifact
lifecycle (R2); artifact-grounded evaluation (R3); cross-repository
compatibility/release/rollback (R4); security, data lifecycle, and operations
(R5); and pilot/production authorization (R6). The unified state model remains
`OBSERVED → PROPOSED → APPROVED → AUTHORIZED_FOR_EXECUTION`; completion or
approval never implies the last state.

## First cross-repository tranche and P2 exits

The first evidence-producing lifecycle is:

```text
certified GeoX experiment evidence
→ MMM calibration compatibility
→ MMM bounded baseline-versus-candidate public Ridge simulation
→ MIP planning-evidence journey
→ concrete D6 release evidence
```

P2 exits only when certified fixture cases cover success, warning,
incompatible, stale, blocked, and failed states; MMM provides a baseline and
candidate identity, scope, full-panel delta-mu, uncertainty availability,
supported-range result, limitations, terminal state, and lineage; MIP preserves
readiness, calibration compatibility, permitted/prohibited claims, warnings,
and blockers in a planning-evidence report. Human approval remains required.
P2 explicitly excludes automatic candidate generation, optimization, approved
recommendations, spend execution, and treatment assignment.

## Ownership and D6 treatment

MIP coordinates workflow, resolves artifacts/readiness, records evidence, and
explains governed outputs. MMM owns MMM computation, calibration treatment,
range, uncertainty, simulation/optimization, and MMM numerical truth.
GeoX/panel_exp owns experiment validation, assignment and inference computation,
readouts, effect/uncertainty semantics, and GeoX numerical truth. The LLM may
route, ask for information, explain certified evidence, and only when separately
authorized formulate bounded proposals; it never computes analytical truth,
selects treatment markets, approves, or executes.

R4/D6 Gate 1 is concrete lifecycle evidence, not a standalone abstract program:
it requires versions, a compatibility matrix, fixture ownership, field and
warning/failure semantics, release/rollback order, last-known-good versions,
limitations, migration/deprecation, named owners/approvers, and authorization
flags. Gate 2 adds integrated runtime certification and tested rollback. Neither
gate alone authorizes real data, live engines, recommendation/execution, pilot,
or production.

## Active controls, historical treatment, and governance simplification

| Document/control type | Treatment |
|---|---|
| `ROADMAP.md` and `ROADMAP_EXECUTION_SEQUENCE.md` | Active canonical control: P0–P8 lifecycle plus binding R0–R6 gates. |
| Capability/environment, evidence/release, and authorization/decision controls | Active supporting gates; must be referenced by later authorized work. |
| Audit, ratification, amendment, rebase, and classification-review artifacts | Preserved evidence and traceability; no independent execution authority. |
| Older P/I/CF sequences and old task files | Historical/supporting detail only; cannot regain authority or bypass current gates. |

Routine future implementation needs an approved phase objective, explicit task
authorization, verified prerequisites on `main`, bounded scope, acceptance and
validation evidence, non-goals, and stop/rollback conditions. ADRs or major
review are reserved for ownership/authority changes, real-data use,
recommendation/execution authority, environment progression, or material
architecture changes. This simplifies control without weakening analytical,
security, release, or production boundaries.

## Explicit deferrals and authority boundary

No capability is authorized by this consolidation. The following remain frozen:
provider promotion and Acceptance-004; resolver/artifact implementation;
fixture integration; isolated test-storage implementation; uploads and
persistent customer/product artifacts; live MMM/GeoX; simulation; optimization;
recommendation proposal/approval/execution; treatment assignment; pilot; and
production. No downstream task is generated.

## Validation

JSON parsing, Markdown/JSON consistency, focused roadmap/documentation/
governance tests, `git diff --check`, and repository-standard Docker-backed
`make validate` are required before commit. Results are recorded in the summary
artifact after validation.
