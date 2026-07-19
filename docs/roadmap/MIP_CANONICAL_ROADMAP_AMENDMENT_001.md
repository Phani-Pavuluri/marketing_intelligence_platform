# MIP Canonical Roadmap Amendment 001

## Purpose and canonical files

This governance-only amendment incorporates ratified D1–D10 into the canonical
[Roadmap](ROADMAP.md) and [Roadmap execution sequence](ROADMAP_EXECUTION_SEQUENCE.md).
It creates no execution-rebase plan, implementation task, runtime change, or
capability authorization.

| Canonical file | Amendment effect |
|---|---|
| `docs/roadmap/ROADMAP.md` | Adds authoritative R0–R6, lanes, decisions, and freezes; retains older phases as context where not conflicting |
| `docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md` | Adds a gate overlay; retains P/I/CF material as historical context and supersedes conflicting next-artifact wording |

## Migration and supersession

The prior roadmap language is retained for historical phase detail. It is modified
only where a legacy next-step or phase implication could bypass the ratified
R0–R6 sequence. No prior document is retired. The amendment report, ratification
brief, and audit remain traceability evidence; `ROADMAP.md` and
`ROADMAP_EXECUTION_SEQUENCE.md` are the canonical execution authority.

## D1–D10 mapping

| Decision | Canonical roadmap effect |
|---|---|
| D1 | R1 benchmark + operational acceptance + explicit promotion approval |
| D2 | Acceptance-004 is operational-only and frozen |
| D3 | R2 design/fixture/user-facing gates precede R3 |
| D4 | Security/lifecycle architecture and persistent-data gates, including isolated test evidence distinction |
| D5 | Contained fixture-backed integration only; no real-data/live claim |
| D6 | R4 Gate 1 design and Gate 2 certification/rollback; versioned release packet |
| D7 | Standalone engine-owned Numerical Truth Dataset Program |
| D8 | Four environments, storage categories, and capability-authority matrix |
| D9 | Lifecycle/RecommendationContract design only; separate decision states |
| D10 | Hybrid R0–R6 sequence plus governed lanes and state model |

## R0–R6 and lane binding

R0–R6, lane owners, evidence, prerequisites, stop/rollback rules, and release
boundaries are defined in the canonical Roadmap amendment section. The mandatory
state model is `OBSERVED → PROPOSED → APPROVED → AUTHORIZED_FOR_EXECUTION`.
Parallel lane work requires its milestone gate and all dependencies; no lane is
independent execution authority.

## Explicit non-authorizations and future rebase

All freezes listed in the canonical Roadmap remain unchanged. In particular, no
provider promotion, acceptance-004 execution, resolver/artifact implementation,
real-data/persistent artifact handling, live engines, simulation, optimization,
recommendation, automated decision, treatment assignment, pilot, or production
work is authorized.

Execution rebase remains a separate future decision. It must classify every
pending/paused/frozen task, cite the amended roadmap/evidence, verify prerequisites
on `main`, preserve cross-repository sequencing, and explicitly reauthorize any
retained task before implementation. It is not created by this amendment.

## Validation evidence

This amendment must pass JSON validation, Markdown/JSON consistency, focused
roadmap/governance and documentation-inventory checks, `git diff --check`, and
repository-standard Docker validation before commit.
