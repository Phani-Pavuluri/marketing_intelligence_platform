# Repository Context Index

**Status:** active navigation index  
**Owner:** MIP program owner  
**Last updated:** 2026-08-05  
**Last verified:** 2026-08-05  
**Verified against:** MIP `main` `c3897ed0b1ca096d186a9cabda36e1b926c4e71f`; MMM `main` `fe8e784923994406a2e4907d28debd872d61fd73`; GeoX `main` `b11646bab1f461964644a6526ef4967a8f04624d`  
**Update trigger:** canonical source-path, repository pin, capability checkpoint, or bootstrap change.

## Fresh chat bootstrap

Use connected GitHub and synchronized Git as the source of truth. Read the root
`AGENTS.md`, then `docs/execution/EXECUTION_STATE.json`, `ACTIVE_TASK.md`, this
index, and `LATEST_COMPLETION_REPORT.md`. Read the P2 capability ledger and
relevant program files before interpreting roadmaps or proposing work. Verify
all affected sibling main SHAs and execution evidence. Stop rather than infer
through stale pins, branch conflicts, unresolved ownership, or missing authority.

## Current P2 navigation

- `docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json` — machine-readable current
  capability, dependency, validation, certification, consumer-verification, and
  downstream-eligibility state.
- `docs/program/PROGRAM_CURRENT_STATE.md` — concise current program position.
- `docs/program/REPOSITORY_CHECKPOINTS.md` — verified repository-main evidence.
- `docs/program/NEXT_EXECUTION_SEQUENCE.md` — exact six-step dependency order;
  sequencing only, not authorization.
- `docs/program/AUTHORITY_AND_FREEZE_MATRIX.md` — blocked and permitted authority.
- `docs/program/CROSS_REPOSITORY_COORDINATION_PROTOCOL.md` — ownership,
  precedence, live-overlay, and consumer-verification rules.
- `docs/program/CROSS_REPOSITORY_COORDINATION_STATE.json` — historical
  coordination snapshot; apply the protocol's live overlay when pins are stale.

## Roadmaps

- `docs/roadmap/ROADMAP.md` — long-range MIP capability phases.
- `docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md` — roadmap-level sequencing.
- `docs/roadmap/MIP_DECISION_LIFECYCLE_ROADMAP_CONSOLIDATION_001.md` — lifecycle
  consolidation.
- `docs/roadmap/MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md` — P2
  consumer and fixture-journey design.

Roadmaps describe future capability direction. They do not replace the P2
capability ledger or repository execution state.

## Execution handoff

- `docs/program/LEAN_REPOSITORY_DELIVERY_STANDARD.md`
- `docs/execution/TASK_EXECUTION_STANDARD.md`
- `docs/execution/EXECUTION_STATE.json`
- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

Execution files define exactly one repository-local milestone. The capability
ledger never authorizes a task, merge, analytical behavior, or sibling change.

## Connected repositories

- `Phani-Pavuluri/MMM`
- `Phani-Pavuluri/panel_exp`

Current verified pins are recorded above and in the P2 ledger. A feature branch
never satisfies a merged dependency. Reported completion without exact merged
repository evidence and required consumer verification remains blocked.
