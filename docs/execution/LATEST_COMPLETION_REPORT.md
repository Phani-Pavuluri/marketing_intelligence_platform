# TASK_AUTHORIZATION_REPORT

## Current decision

- **Task ID:** `MIP_GIT_AUTHORITATIVE_THIN_LAUNCHER_STANDARD_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Status:** `authorized`
- **Pre-authoring base:** `976d3a1daeae9c52c8772e5112574f698951a57c`
- **Feature branch:** `docs/mip-git-authoritative-thin-launcher-standard-001`
- **Risk tier:** Tier 1 repository execution governance
- **Implementation SHA:** not yet created
- **Capability authority:** unchanged

## Orientation and eligibility evidence

Connected GitHub verified MIP `main` at
`976d3a1daeae9c52c8772e5112574f698951a57c` before authoring.
The prior P2 reconciliation task is superseded without merge on its preserved
branch at `0629af616943c53e8d4a275dec147624bb9e040c`; it has no remaining task,
correction, merge, or PR authority.

Live sibling evidence is read-only:

- MMM `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`; its protocol-adoption branch is
  `ready_for_review` at `c370dc7cd59a61cc2e19025d1a2328c7867b63be`
  against the older invocation-only standard.
- GeoX `0a463ad96cda31dc2bdc962fd24f5481bb7aede9`; its branch-binding reauthoring
  branch records `changes_requested` at
  `377050f76ddc03d6feb6f4f75eb2c9c9f8c954d1`.

Neither sibling owns or modifies MIP's execution-standard files. MIP cannot
approve, supersede, correct, merge, or authorize either sibling task. No roadmap
audit or product-capability task is required to define this bounded standard
correction.

## Primary outcome

The authorized outcome replaces the exact one-line invocation-only prompt rule
with a Git-authoritative thin-launcher contract that:

- keeps all durable task meaning and authority in Git;
- allows only repository path, synchronization, repository reads, Git-declared
  branch resumption, continuation, remote durable terminal outcomes, and
  prohibited-operation reminders in execution and correction launchers;
- permits only the local path and externally approved exact head as merge
  instance values;
- explicitly makes orientation and progress updates non-terminal; and
- requires continuation until the remote feature branch records
  `ready_for_review` or a genuine `blocked` state.

The complete behavior, canonical launchers, allowed/prohibited prompt boundary,
owned paths, semantic tests, validation gate, publication contract, and deferred
successors are recorded in `docs/execution/ACTIVE_TASK.md`.

## Supersession and overlap decision

`MIP_P2_ROADMAP_AND_COORDINATION_RECONCILIATION_AFTER_GEOX_SUPERSESSION_001`
is not resumed or merged. Its branch remains historical only. This new task does
not update roadmap or coordination state and does not absorb any P2, MMM, or GeoX
capability work.

The current MMM adoption head implements the older standard. Its disposition is
an MMM-owned future decision after the new MIP standard is merged; no MMM state
is changed or authorized here. GeoX adoption is likewise separate and deferred.

## Task-authoring boundary

The authoring range starts at
`976d3a1daeae9c52c8772e5112574f698951a57c` and changes only:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The commit containing this report is the final task-authoring head. The
immediate next commit must be state-only, changing only
`docs/execution/EXECUTION_STATE.json` to record that exact head and authorize the
declared feature branch. The branch must be created from the resulting
synchronized state-only `main`.

## Validation requirement

The Tier-1 gate requires JSON and Markdown consistency, authoring-boundary and
exact changed-path verification, `git diff --check`, the focused repository
execution-handoff test, Ruff and configured mypy for the changed test, an
exact-tree publication receipt, and local/remote branch-head equality.
Docker-backed `make validate` and the full suite are `not_required` for this
documentation/governance-only surface.

## Authority and non-actions

This authorization changes only MIP repository-execution governance. It does
not modify or authorize product code, contracts, adapters, fixtures,
orchestration, LLM behavior, reporting, UI, analytical truth, sibling work,
live integration, real data, persistence, simulation, optimization,
recommendations, assignment, pilot, production, or package-side agents.

Merge authority, PR authority, correction authority, sibling authority, and
capability authority remain false. No implementation occurred during task
authoring.
