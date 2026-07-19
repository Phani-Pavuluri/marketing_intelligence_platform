# MIP Execution Rebase Plan 001

## Status and authority

`PROPOSED` governance plan only. It is derived from canonical amendment commit
`4839d1b` and ratification commit `b4d04ce`; it is not implementation authority.
No inventory item is `AUTHORIZED_FOR_EXECUTION`. Existing task files are
discovery evidence only and retain no authority unless a later approved rebase
explicitly retains and reauthorizes them.

## Evidence and sibling status

Canonical evidence: `ROADMAP.md`, `ROADMAP_EXECUTION_SEQUENCE.md`, canonical
amendment 001, ratification brief 001, audit 001, and their committed summaries.
MMM was on `feat/mmm-public-simulation-handoff-001` at `da8bdbe` (0/0 to
`origin/main`) with tracked/untracked dirty work. panel_exp was on
`feature/non-production-geox-mip-artifact-envelope-dry-run-runtime-001` at
`827a5b8` (0/0) with tracked/untracked dirty work. Neither sibling worktree is
canonical evidence or was modified.

## Inventory and dispositions

All rows have current authorization state `APPROVED`, require later explicit
authorization, and preserve freeze status. `Source` is the governing committed
roadmap/amendment unless a legacy task is named as non-authoritative discovery.

| ID | Capability / prior position | R / lane | State / disposition | Rationale and prerequisites | Owner / evidence / stop-rollback |
|---|---|---|---|---|---|
| L1 | Core LLM benchmark | R1 / evaluation | PROPOSED / retain | Required before promotion; benchmark design, scenarios, thresholds/LKG missing | MIP benchmark owner; versioned benchmark; stop on missing governance; rollback LKG |
| L2 | Provider/model/prompt comparison and promotion | R1 / governance | APPROVED / reorder | Must follow L1 plus D2 target acceptance and explicit approval | MIP governance; benchmark + operational packet; provider rollback |
| L3 | Acceptance-004 | R1 / governance | APPROVED / remain_blocked | Operational-only; execution is frozen | MIP platform owner; target packet; provider-disable rollback |
| L4 | Artifact-grounded conversational/workflow benchmark | R3 / evaluation | APPROVED / reorder | Needs R2 lifecycle and certified truth | MIP + MMM/GeoX truth owners; grounded report; disable feature |
| A1 | Resolver contract/lifecycle design | R2 / resolver | APPROVED / reorder | Only after roadmap amendment and R1 benchmark-design approval | MIP artifact owner; contract/evidence; stop on unresolved ownership |
| A2 | Resolver/artifact implementation, registration/discovery | R2 / resolver | APPROVED / remain_blocked | Requires R1 gate, lifecycle/security, later authorization | MIP; lifecycle/grounded evidence; disable resolver |
| A3 | Persistence, supersession, isolated test storage | R2,R5 / artifact/security | APPROVED / modify | Separate sanitized non-customer test storage from product/customer artifacts | MIP security/artifact owners; retention/deletion/audit packet; purge/fixture-only rollback |
| N1 | MMM numerical-truth suites | R1,R3 / evaluation | APPROVED / retain | Engine-owned certified truth required for grounded evaluation | MMM owner; version/provenance/tolerances; retire/replacement policy |
| N2 | GeoX numerical-truth suites | R1,R3 / evaluation | APPROVED / retain | Engine-owned certified truth required for integration claims | GeoX owner; version/provenance/tolerances; retire/replacement policy |
| N3 | MIP wrappers/registry and certified fixture journeys | R1,R3 / evaluation | APPROVED / modify | MIP owns scenarios/scoring, not statistical truth | MIP + truth owners; deterministic fixtures; fixture-only rollback |
| I1 | MIP adapters, MMM/GeoX handoffs | R4 / integration | APPROVED / reorder | Must use D6 Gate 1 contracts before later certification | MIP/MMM/GeoX owners; compatibility matrix; stop on mismatch |
| I2 | D6 Gate 1 design and release packet | R4 / integration | APPROVED / remain_blocked | Planning item only; no live engine authority | Release owners; versions/fixtures/failures/order; no release rollback needed |
| I3 | D6 Gate 2 runtime certification/rollback | R4 / integration | APPROVED / remain_blocked | Needs actual entrypoint, security/environment, tested rollback | Release owners; runtime packet/LKG; rollback verified |
| S1 | Authn/z, tenant/workspace, classification, retention/deletion, audit, secrets | R0,R5 / security | APPROVED / retain | Required before real data/persistence/pilot | MIP security/platform; control evidence; deny/purge rollback |
| S2 | Jobs, recovery, observability, SLOs, incidents, support | R5 / operations | APPROVED / reorder | Pilot/production prerequisite | MIP platform; operational drill; disable service rollback |
| D1 | Live MMM/GeoX and DecisionSurface | R4–R6 / integration | APPROVED / remain_blocked | Needs certified release, real-data/security, pilot decision | Engine/release owners; runtime/pilot packet; disable engines |
| D2 | Simulation and optimization | R3–R6 / decision authority | APPROVED / remain_blocked | Needs truth, governed evidence, separate authority | MMM/optimizer/governance; controlled evidence; revoke/disable |
| D3 | RecommendationContract/lifecycle design | R5 / governance | APPROVED / reorder | Design only after later explicit planning authorization | MIP governance; contract/audit design; no runtime |
| D4 | Recommendation proposal/approval/execution/monitoring/revocation | R5,R6 / authorization | APPROVED / remain_blocked | Separate proposal/approval/execution and human accountability | Named owners; decision packet; revoke/rollback |
| D5 | Treatment assignment and external API/connector actions | R6 / authorization | APPROVED / remain_blocked | GeoX computation and human approval remain separate | GeoX/governance/execution owner; audit packet; kill switch |
| E1 | Public Fixture Demo | R0 / environment | APPROVED / retain | Fixture-only disclosure; live LLM separately D1/D2-gated | MIP demo owner; demo evidence; fixture-only rollback |
| E2 | Internal Fixture-Backed Integration | R0,R4 / environment | APPROVED / modify | Certified fixtures, no real data/external users; D5/D6 containment | MIP/MMM/GeoX owners; typed test evidence; fixture-only rollback |
| E3 | Limited pilot | R5,R6 / environment | APPROVED / remain_blocked | Needs real-data/security/ops/release/pilot approval | Program owners; pilot packet; return to private fixture mode |
| E4 | Production | R6 / environment | APPROVED / remain_blocked | Needs successful pilot and explicit production authorization | Production owners; release/support/DR packet; kill switch |

## Freeze reconciliation

The mandatory freeze list remains unchanged: acceptance-004, promotion, resolver
and artifact implementation, artifact-grounded implementation, fixture package
integration, isolated-storage implementation, D6 Gate 1/2 implementation, private
real-data integration, uploads, persistent artifacts, live MMM/GeoX, simulation,
optimization, recommendation lifecycle runtime, external actions, automated
decisions, treatment assignment, pilot, and production. Planning eligibility is
not implementation eligibility.

## Proposed post-amendment planning sequence

1. **R0 governance/environment matrix refinement**: next because all later work
   needs owners, capability boundaries, and authority evidence. Safe parallel
   design: D1 benchmark governance and D7 registry strategy. Serial boundary:
   no persistence/real-data/integration runtime.
2. **R1 core benchmark and Numerical Truth Dataset Program planning**: requires
   R0 roles; establishes scenarios, truth ownership, thresholds, and rollback.
3. **R2 resolver/lifecycle planning** after R1 benchmark-design approval; no
   implementation until benchmark-v1 gate.
4. **R3 grounded benchmark planning** after R2 contracts and certified truth.
5. **R4 Gate 1 then Gate 2 planning**: Gate 2 remains serial after Gate 1,
   lifecycle/security evidence, and engine-owner dependencies.
6. **R5/R6 security/operations, decision-lifecycle, pilot/production planning**:
   serial after R4 evidence; all runtime remains separately authorized.

The smallest future planning concepts are R0 ownership/environment matrix, R1
benchmark governance, and Numerical Truth Dataset Program governance. They are
not created here and require later explicit authorization.

## Old-task controls and future rebase requirements

A future approved rebase must classify every pending/paused/frozen task as
retain, modify, reorder, replace, retire, or remain blocked; cite canonical
roadmap section, approved inventory row, and prerequisite commits/artifacts on
`main`; preserve cross-repository sequencing; and create no implementation task
until explicitly approved. This plan itself neither performs that authorization
nor creates any task body.
