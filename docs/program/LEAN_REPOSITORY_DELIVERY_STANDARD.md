# Lean Repository Delivery Standard

## Purpose

MIP work is delivered as small, independently reviewable Git outcomes. One
authorized task has one primary mergeable outcome. Git history preserves prior
states; current documents state only the current decision and boundary.

## Delivery shape

An internal checkpoint becomes a separate merge boundary when it produces valid
standalone evidence, can be reviewed independently, or changes a public
contract, migration, integration surface, or authority boundary. Task authors
must stop and split work when a meaningful portion can be validated and merged
independently.

Warning triggers include multiple public surfaces; a contract plus migration;
product work plus governance repair; several meaningful checkpoints; or a
branch growing beyond a small review unit.

One correction cycle is the default. If review exposes a new contract,
migration, integration surface, or independently mergeable outcome, re-scope it
as a successor task rather than expanding the existing branch.

## Definition-ready authorization

Before an executable MIP task is authorized, its active task must define one
primary mergeable outcome, exact observable behavior and preserved boundaries,
resolved design and authority decisions, and inputs/outputs appropriate to the
changed surface. It must also identify failure semantics, named acceptance tests
or deterministic evidence, owned and prohibited paths, focused validation, and
deferred successors.

Compatibility or migration policy is required when public contracts, versions,
persisted artifacts, or migrations change; otherwise it is explicitly
`not_applicable`. API, schema, state-machine, and migration surfaces require
their corresponding signatures, fields/types/invariants, transitions/failures,
or source/target/rollback behavior. Routine documentation work must not invent
those details.

The task must state `unresolved execution-blocking design questions: none`.
Unresolved implementation meaning leaves the work `proposed`, design-blocked,
or split into a bounded decision/evidence task. Codex must not decide among
materially different contract meanings during execution. MMM and GeoX adoption
of this rule remains a separately authorized owner-repository decision.

## Risk tiers

| Tier | Scope | Minimum validation |
|---|---|---|
| 1 | Routine documentation or governance guidance | Focused path, structure, and changed-path checks |
| 2 | Public contract, package, or externally visible behavior | Focused tests plus the repository validation required by that surface |
| 3 | Cross-repository, decision-authority, analytical, or production boundary | Owner-repository evidence, cross-repository review, and the full applicable validation gate |

## Controls at every tier

- Git and committed repository state remain authoritative.
- The task declares its single primary outcome, owned paths, validation, and
  deferred successors before implementation.
- Ownership, exact-head review, risk-proportional validation, and explicit
  authority boundaries are never weakened.
- A task does not authorize product, analytical, sibling-repository, or
  capability work beyond its explicit scope.

## Sibling adoption

MIP must prove this standard on its own work before MMM or GeoX adoption can be
considered. Any sibling adoption is a separately authorized owner-repository
task; this standard neither modifies nor overrides sibling execution state.
