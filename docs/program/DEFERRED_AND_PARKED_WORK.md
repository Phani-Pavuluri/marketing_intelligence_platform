# Deferred and Parked Work

**Status:** non-active work inventory
**Owner:** MIP program owner and named engine owners
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** MIP `89caf56`; MMM `origin/main` `9a3aa5c`; GeoX `origin/main` `8601823`
**Update trigger:** an explicit activation, retirement, or authority decision.

| ID | State | Owner | Description / reason | Prerequisites and revisit trigger | Intended phase / source |
|---|---|---|---|---|---|
| PK-01 | deferred | MMM/MIP | Automatic candidate generation and constrained optimization; P2 is comparison only. | P6 gates, optimizer truth, explicit authority. | P6; `ROADMAP.md` |
| PK-02 | deferred | MIP/humans | Recommendation proposal, approval, and execution. | RecommendationContract, human approval, environment gates. | P6; D9 treatment |
| PK-03 | deferred | MMM | DecisionSurface production export. | Concrete lifecycle need, D6/R5/R6 approval. | P5/P6 |
| PK-04 | blocked | MIP | Real uploads/customer data and persistent customer artifacts. | Security, tenancy, retention/deletion, access controls. | P5/P7; D4 |
| PK-05 | blocked | MIP | Scheduling and operational jobs. | Jobs/recovery/SLO ownership and R5 approval. | P5/P7 |
| PK-06 | blocked | program | Pilot and production. | R5/R6, runtime certification, real-data approval. | P7/P8 |
| PK-07 | blocked | MMM | Automatic refit or parameter override. | Model governance and explicit MMM authority. | later MMM phase |
| PK-08 | research_only | MMM | Bayesian MMM production use and uncertainty-aware optimization. | Certified production evidence and separate authorization. | P6/P8 |
| PK-09 | deferred | engine owners | Package-side agents. | Clear authority/safety design and runtime authorization. | later architecture |
| PK-10 | deferred | GeoX | Broad GeoX method-selection automation and policy-adapter runtime. | Validated policy boundary and explicit authority. | later GeoX phase |
| PK-11 | deferred | GeoX | Broad method-family expansion and multicell/shared-control production claims. | Certified supported methods and release evidence. | later GeoX phase |
| PK-12 | diagnostic_only | GeoX | Classic/Aggregate TBR overclaim path and TBRRidge paths. | New governed evidence explicitly promotes a supported use. | GeoX truth fixtures |
| PK-13 | research_only | GeoX | Bayesian TBR, TROP, Synthetic DID where unauthorized, and LOG_LOG MMM. | Research results plus explicit production authorization. | research only |

`deferred`, `blocked`, `diagnostic_only`, `research_only`, `superseded`, and
`retired` are not interchangeable. No parked item becomes active without an
explicit activation decision and the prerequisite evidence named above.
