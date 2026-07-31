# Active Task

**Status:** authorized
**Owner:** MIP program governance
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31

## Identity

- **Task ID:** `MIP_P2_CROSS_REPOSITORY_READINESS_RECONCILIATION_001`
- **Pre-authoring base:** `main` / `38f88467f55d5bc4cc64e5a58b0f08f1639a40d0`
- **Feature branch:** `docs/mip-p2-cross-repository-readiness-reconciliation-001`
- **Execution mode:** `branch_and_fast_forward`
- **Current MIP checkpoint:** `38f88467f55d5bc4cc64e5a58b0f08f1639a40d0`
- **Current MMM checkpoint:** `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`
- **Current GeoX checkpoint:** `e0cef94c063b03b29e1e1760fb1c2320ce497b56`
- **Capability authorizations changed:** `false`

## Purpose

Reconcile MIP program memory with the current remote `main` state of MIP, MMM,
and GeoX after all three repositories completed repository-native execution
handoff V2. Replace stale pre-migration checkpoints, distinguish execution-
workflow completion from analytical/product readiness, verify each previously
recorded P2 dependency against current Git evidence, and publish the exact
cross-repository sequence required before fixture-only P2 implementation.

This is a documentation, governance, and focused consistency-test task. It does
not implement P2 consumer views, planning reports, adapters, package calls,
engine normalization, simulations, recommendations, or runtime integration.

## Prerequisites and source evidence

Before modifying anything, complete the mandatory bootstrap in `AGENTS.md` and
prove local `main == origin/main` at the synchronized post-authoring task head.
Verify these exact remote checkpoints:

- MIP: `Phani-Pavuluri/marketing_intelligence_platform@38f88467f55d5bc4cc64e5a58b0f08f1639a40d0`;
- MMM: `Phani-Pavuluri/MMM@1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`;
- GeoX: `Phani-Pavuluri/panel_exp@e0cef94c063b03b29e1e1760fb1c2320ce497b56`.

Read and reconcile at minimum:

- MIP `docs/program/PROGRAM_CURRENT_STATE.md`;
- MIP `docs/program/REPOSITORY_CHECKPOINTS.md`;
- MIP `docs/program/NEXT_EXECUTION_SEQUENCE.md`;
- MIP `docs/program/DECISION_REGISTER.md`;
- MIP `docs/roadmap/MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md`;
- MMM `docs/execution/EXECUTION_STATE.json` and
  `docs/execution/LATEST_COMPLETION_REPORT.md`;
- MMM `mmm/contracts/calibration_compatibility.py`;
- GeoX `docs/execution/EXECUTION_STATE.json` and
  `docs/execution/LATEST_COMPLETION_REPORT.md`;
- GeoX `panel_exp/contracts/geox_governed_experiment_readout.py`.

Use connected GitHub and synchronized Git as authority. Do not infer capability
completion from newer workflow-only commits. Verify changed paths between the
old MIP-recorded engine checkpoints and current engine `main`.

## Owned files

Execution may modify only:

- `docs/roadmap/MIP_P2_CROSS_REPOSITORY_READINESS_RECONCILIATION_001.md`;
- `docs/program/PROGRAM_CURRENT_STATE.md`;
- `docs/program/REPOSITORY_CHECKPOINTS.md`;
- `docs/program/NEXT_EXECUTION_SEQUENCE.md`;
- `docs/program/DECISION_REGISTER.md`;
- `docs/execution/REPOSITORY_CONTEXT_INDEX.md`;
- `tests/test_mip_p2_cross_repository_readiness_reconciliation.py`;
- `docs/execution/ACTIVE_TASK.md`;
- `docs/execution/EXECUTION_STATE.json`;
- `docs/execution/LATEST_COMPLETION_REPORT.md`.

No other path is authorized.

## Required reconciliation

1. Add
   `docs/roadmap/MIP_P2_CROSS_REPOSITORY_READINESS_RECONCILIATION_001.md`
   containing:
   - exact current repository pins;
   - old versus current checkpoint comparison;
   - workflow-governance status for each repository;
   - product/contract readiness status for each repository;
   - verified P2 dependency matrix with evidence paths;
   - blocker versus deferred-debt classification;
   - exact follow-on task sequence and ownership;
   - authority boundary and final verdict.
2. Update `PROGRAM_CURRENT_STATE.md` to current pins and state. It must state
   that repository-native execution V2 is complete across all three repos while
   P2 fixture implementation remains blocked by narrow engine contract work.
3. Update `REPOSITORY_CHECKPOINTS.md` with current exact pins and evidence. Do
   not claim engine product changes from workflow-only commits.
4. Update `NEXT_EXECUTION_SEQUENCE.md` to the following governed order:
   - GeoX temporal, freshness, envelope, schema, and package-version semantics;
   - GeoX governed-readout builder/package entrypoint;
   - MMM strict GeoX-readout normalization and certified cross-repository
     compatibility fixtures;
   - MIP fixture-only P2 planning-evidence journey implementation;
   - cross-repository D6 reconciliation and fixture-only dry run;
   - separate authorization before any live package integration.
5. Update `DECISION_REGISTER.md` only with decisions supported by this
   reconciliation. Preserve prior decisions and do not rewrite history.
6. Update `REPOSITORY_CONTEXT_INDEX.md` so its verification metadata and
   connected-repository orientation reflect the current MIP canonical pin and
   exact current MMM/GeoX checkpoints.
7. Add a focused test that verifies:
   - all three exact current pins appear in the reconciliation artifact and
     relevant program checkpoint files;
   - stale engine pins `9a3aa5cb9a48c9a59d45e266685228835237f328`
     and `860182386c39f487747de5f43e67a31e9978e57c` are not presented as current;
   - the required engine blocker evidence paths and ordered follow-on tasks are
     present;
   - workflow completion is not equated with product/capability readiness;
   - runtime integration, recommendations, optimization, production, and
     package-side-agent authority remain false or explicitly blocked.
8. Preserve the existing P2 consumer design. Do not alter its producer/consumer
   ownership split or safe-claim policy.

## Verified blocker classification to test, not assume

The reconciliation must verify and record whether current Git still supports
these blockers:

### GeoX

- governed-readout temporal boundaries remain insufficiently typed for D6;
- freshness/expiry semantics are not yet deterministic and complete;
- record envelope kind/schema and producer package-version semantics remain
  incomplete;
- no canonical production-ready governed-readout builder/package entrypoint is
  established;
- unresolved full-suite repository validation debt remains separate from the
  focused workflow migration result.

### MMM

- `MMMNormalizedCalibrationReadout` remains an MMM-owned normalized boundary,
  intentionally independent of the GeoX schema;
- no strict canonical GeoX governed-readout-to-MMM normalization adapter is
  established;
- certified cross-repository GeoX-to-MMM compatibility fixture mappings remain
  absent;
- D6 compatibility/release pins remain incomplete.

If current Git disproves any listed blocker, update the reconciliation based on
the actual evidence and explain the change. Do not preserve stale statements for
consistency.

## Follow-on task identities

Record these as proposed sequencing only; do not authorize or create them:

1. `GEOX_GOVERNED_READOUT_TEMPORAL_VERSION_AND_ENVELOPE_SEMANTICS_001`;
2. `GEOX_GOVERNED_READOUT_BUILDER_ENTRYPOINT_001`;
3. `MMM_GEOX_READOUT_NORMALIZATION_AND_CROSS_REPOSITORY_FIXTURES_001`;
4. `MIP_P2_FIXTURE_ONLY_PLANNING_EVIDENCE_JOURNEY_001`;
5. later D6 reconciliation and fixture-only cross-repository dry run.

## Validation gate

Run:

- the new focused reconciliation test;
- relevant existing documentation and governance tests;
- JSON parsing and Markdown/path consistency checks;
- Ruff and mypy for changed Python files;
- `git diff --check`;
- exact changed-path verification;
- Docker-backed `make validate` on the exact feature-branch tree.

Record exact pass/skip/warning counts. If Docker or any prerequisite fails,
publish an accurate `blocked` state with typed blockers and stop.

## State transition and completion

On success:

- publish `ready_for_review`;
- set `implementation_commit_sha` to the full implementation SHA;
- keep `task_execution_authorized: true`;
- keep `merge_authorized: false`;
- keep reviewed and approval SHAs null;
- keep blockers empty;
- keep `capability_authorizations_changed: false`;
- push and verify the exact remote feature head;
- stop without a PR, merge, or branch deletion.

On failure, publish `blocked` with specific evidence. Never guess.

## Acceptance criteria

- MIP program memory uses current exact MIP/MMM/GeoX pins.
- Old engine checkpoints are clearly historical, not current.
- Every P2 dependency is reverified against current Git.
- True blockers are separated from workflow migration and general validation
  debt.
- The next cross-repository sequence is explicit and ownership-correct.
- No P2 implementation or engine capability is introduced.
- No analytical, recommendation, optimization, treatment-assignment, live
  integration, pilot, production, or agent authority changes.
- Full validation passes or the task stops blocked.

## Prohibited actions

Do not modify MMM or GeoX. Do not create a PR. Do not merge, squash, rebase,
force-push, or delete branches. Do not implement consumer contracts, adapters,
package entrypoints, orchestration, LLM behavior, persistence, uploads, real
data, simulations, recommendations, optimization, or production paths.
