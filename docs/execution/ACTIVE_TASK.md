# Active Task

**Status:** ready_for_review
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_DEFINITION_READY_TASK_AUTHORIZATION_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `main` / `dab329bc6ff9d62971bbe12a7398e08131a4cf22`
- **Feature branch:** `docs/mip-definition-ready-task-authorization-standard-001`
- **Execution mode:** `branch_and_fast_forward`
- **Risk tier:** Tier 1 — documentation/governance rule plus focused governance test
- **Prior task:** `MIP_LEAN_REPOSITORY_DELIVERY_STANDARD_001`
- **Prior closure:** `dab329bc6ff9d62971bbe12a7398e08131a4cf22`
- **Capability authorizations changed:** `false`
- **Implementation commit:** `67abc7cfc2f02c45abb442d1f61834bcdc6287e7`

## Published review state

The definition-ready authorization rule is implemented and validated on the
frozen review-publication tree. This task is ready for exact-head review only.
Task execution remains authorized for the reviewed branch; correction execution,
merge, PR creation, sibling adoption, and capability authority remain false.

The final review-publication commit carries the durable exact-tree validation
receipt and is the only review candidate. No task-owned file may change after
that receipt commit without a new validation receipt.

## Primary mergeable outcome

Make definition-readiness an operative pre-authorization requirement for future
MIP executable tasks. A task must be sufficiently decided that the execution
agent implements an already-defined contract rather than deciding what the
contract should mean.

This is one independently reviewable outcome: the task-authoring rule and its
focused governance assertion establish one authorization gate. It cannot be
split further without leaving either an unenforced rule or a test with no
canonical requirement.

## Problem being closed

The merged lean delivery standard controls task size, merge boundaries,
risk-tier validation, and durable completion evidence. It does not yet require
an executable task to prove that behavioral, schema, compatibility, migration,
failure, and authority decisions relevant to its changed surface are resolved
before authorization.

A grammatically small task can therefore remain semantically vague and delegate
contract design to Codex. This task closes only that gap. It does not create a
new task schema, resolver, automation framework, approval state, checklist
service, or coordination mechanism.

## Definition-ready behavioral contract

Before a future MIP task may be `authorized` for execution, its stable active
task must identify, at the level appropriate to the changed surface:

1. **Primary mergeable outcome** — one independently reviewable result.
2. **Exact observable behavior or contract** — what changes and what must remain
   unchanged.
3. **Resolved design decisions** — architectural, schema, authority, and policy
   choices required for implementation.
4. **Inputs and outputs** — including exact public signatures, fields, types, or
   serialized shapes when the task changes those surfaces.
5. **Failure semantics** — fail-closed behavior, reason/error outcomes, and
   prohibited fallback or inference.
6. **Compatibility or migration policy** — required only when versions,
   persisted artifacts, public contracts, or migration surfaces change;
   otherwise explicitly `not_applicable`.
7. **Owned paths and prohibited scope**.
8. **Named acceptance tests or deterministic evidence** — concrete cases and
   expected outcomes, not only broad quality statements.
9. **Focused validation and applicable risk-tier gate**.
10. **Deferred successors** — independently mergeable work not owned here.
11. **Unresolved execution-blocking design questions:** `none`.

The requirement is surface-proportional. A documentation-only task does not
invent API fields or migration policy. A public API task must define its public
signature and behavior. A schema task must define fields, types, invariants,
version behavior, and compatibility. A state-machine task must define allowed
transitions and failures. A migration task must define source/target versions,
rollback, and incompatible cases.

If any execution-blocking design decision remains unresolved, the task must
remain `proposed`, be marked `blocked` for design, or be split. Codex must not
select among materially different contract meanings during execution.

## Resolved design decisions for this task

- The rule applies to future MIP executable tasks at authorization time.
- The rule is descriptive Markdown enforced by the existing focused governance
  test; no new schema or automation is introduced.
- Requirements are conditional on the changed surface, preventing artificial
  API or migration detail for routine documentation tasks.
- `unresolved execution-blocking design questions: none` is mandatory for
  execution authorization.
- Research or design-discovery tasks may still be authorized when their primary
  outcome is a bounded decision/evidence artifact rather than implementation;
  they must not claim implementation authority.
- MMM and GeoX adoption is not part of this task and requires separate
  owner-repository authorization after this MIP rule is merged.

## Owned paths

Execution may modify only:

1. `AGENTS.md`
2. `docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md`
3. `docs/execution/TASK_EXECUTION_STANDARD.md`
4. `tests/governance/test_repo_native_execution_handoff.py`
5. `docs/execution/ACTIVE_TASK.md`
6. `docs/execution/EXECUTION_STATE.json`
7. `docs/execution/LATEST_COMPLETION_REPORT.md`

Do not modify coordination files, roadmaps, product/runtime/analytical code,
contracts, adapters, fixtures, application code, MMM, or GeoX.

## Required implementation

1. Add a concise definition-ready rule to `LEAN_REPOSITORY_DELIVERY_STANDARD.md`.
2. Make the rule operative in `TASK_EXECUTION_STANDARD.md` before executable
   task authorization.
3. Add a compact reminder to `AGENTS.md` that execution authorization requires
   resolved implementation meaning and no unresolved execution-blocking design
   questions.
4. Strengthen the existing focused governance test to assert the canonical rule,
   surface-proportional behavior, and fail-closed handling of unresolved design.
5. Publish one current completion narrative and a durable exact-tree validation
   receipt under the merged publication rule.

Do not add a new task template file, JSON schema, resolver, linter service,
workflow engine, status, or checkpoint framework.

## Named acceptance tests

The focused governance test must prove that canonical repository guidance:

- requires a primary mergeable outcome and exact observable behavior;
- requires resolved design decisions and inputs/outputs appropriate to the
  changed surface;
- requires failure semantics and conditional compatibility/migration policy;
- requires named acceptance tests or deterministic evidence;
- requires unresolved execution-blocking design questions to be `none` before
  executable authorization;
- states that unresolved meaning remains proposed, design-blocked, or split;
- prevents Codex from deciding materially different contract meanings during
  implementation;
- preserves surface proportionality; and
- preserves separate owner-repository authority for MMM and GeoX adoption.

## Validation gate

Run the Tier 1 gate on the frozen publication tree:

- JSON parsing for `docs/execution/EXECUTION_STATE.json`;
- Markdown/current-state consistency;
- exact task-authoring boundary verification;
- exact changed-path verification against the seven owned paths;
- `git diff --check`;
- `pytest -q tests/governance/test_repo_native_execution_handoff.py`;
- receipt-trailer inspection; and
- local/remote publication-head equality after push.

Docker, Ruff, mypy, and the full suite are `not_required` unless the changed
focused test or another repository-authored gate requires them. If a required
check cannot run or fails, publish accurate `blocked` state rather than widening
scope or claiming completion.

## Deferred successors

- `MMM_DEFINITION_READY_TASK_AUTHORIZATION_STANDARD_ADOPTION_001` — proposed
  owner-repository adoption only; not authorized here.
- `GEOX_DEFINITION_READY_TASK_AUTHORIZATION_STANDARD_ADOPTION_001` — proposed
  owner-repository adoption only; must not alter or override the current GeoX
  builder task.
- Any GeoX builder supersession or rescoping remains a GeoX-owned decision.

## Authority and stop conditions

The implementation is complete and ready for review only. Merge and PR creation
are unauthorized. No product, analytical, live-integration, real-data,
persistence, recommendation, pilot, production, MMM, GeoX, or capability
authority changes.

The exact feature branch was created from synchronized post-authoring `main`.
Review the durable `ready_for_review` receipt and stop without PR or merge until
an exact-head external approval is recorded.
