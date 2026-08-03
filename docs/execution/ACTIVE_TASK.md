# Active Task

**Status:** ready_for_review
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_LEAN_REPOSITORY_DELIVERY_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Feature branch:** `docs/mip-lean-repository-delivery-standard-001`
- **Implementation commit:** `9dda47f3f90877161175c02a736694d5ee253f48`
- **Risk tier:** Tier 1 — documentation and governance guidance only
- **Capability authorizations changed:** `false`

## Current outcome

The branch establishes one concise MIP-owned lean repository delivery standard
and makes risk-tier validation operative for execution, exact-head review, and
post-fast-forward validation.

Future MIP tasks must define one independently reviewable and mergeable outcome,
owned paths, focused validation, and deferred successor work. Independently
valid checkpoints must become separate merge boundaries. Tier 1 may use an
explicit narrow gate; Tier 2 uses focused and surface-required validation; Tier
3 and public, analytical, package, production, or otherwise explicitly gated
work retain the full applicable validation gate.

## Review boundary

The exact remote feature-branch head is the review candidate and is not embedded
in this commit. The task changes only these authorized paths:

- `AGENTS.md`
- `docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The completion report records the Tier 1 validation results. The same declared
gate must be rerun on the exact approved head before merge and after
fast-forward.

## Authority

- Task publication remains `ready_for_review`.
- Correction execution is no longer authorized.
- Merge and PR creation remain unauthorized.
- MMM and GeoX adoption remain separately unauthorized and owner-controlled.
- No automation, resolver, coordination-ledger, product, runtime, analytical,
  sibling-repository, or capability authority is included.
