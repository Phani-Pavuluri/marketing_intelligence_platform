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
