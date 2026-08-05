# Active Task

**Status:** authorized
**Task ID:** `MIP_P2_CAPABILITY_CHECKPOINT_LEDGER_RECOVERY_001`
**Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
**Pre-authoring base:** `9762afccca0790dd897f833d4dbea2f847aa6401`
**Feature branch:** `docs/mip-p2-capability-checkpoint-ledger-recovery-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 3
**Capability authority changed:** `false`
**Unresolved execution-blocking design questions:** none

## Primary outcome

Create one authoritative machine-readable P2 capability-checkpoint ledger and
align current MIP program-navigation documents with it. This repairs program
tracking only; it does not modify GeoX or MMM, certify GeoX, authorize the
blocked bridge, construct CalibrationSignal, or authorize analytical,
runtime, planning, recommendation, pilot, or production behavior.

## Program control

North-star sequence: certified GeoX producer evidence → provenance-linked MMM
compatibility fixtures → MIP compatibility bridge → D6 release evidence →
fixture-only planning-evidence journey.

Current phase: `P2 certified producer-consumer evidence preparation`
Current missing checkpoint: `P2_GEOX_CALIBRATION_SOURCE_PRODUCER_CHECKPOINT`
Next eligible milestone (unauthorized):
`GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001`

## Verified repositories

- MIP main: `9762afccca0790dd897f833d4dbea2f847aa6401`; blocked bridge head:
  `480b32040ce185b8ff091435121c4bea6fc6c453`.
- MMM main: `fe8e784923994406a2e4907d28debd872d61fd73`.
- GeoX main: `b11646bab1f461964644a6526ef4967a8f04624d`; current status
  `superseded_without_merge`; no next task authorized.

The existing bridge and divergent historical branches are not recreated,
reused, cherry-picked, or reauthorized.

## Owned paths

`docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json`, aligned current-state,
checkpoint, sequence, context-index documents, the new governance test, and
the three execution files. Do not modify source/runtime code, existing
fixtures, coordination state/history, standards, CI/Docker/dependencies, or
MMM/GeoX.

## Required ledger and validation

Create the `mip_p2_capability_checkpoint_ledger_v1` ledger with the exact P2
repository pins, seven ordered capability records, acyclic dependencies,
false authority flags, blocked/uncertified classifications, and one
unauthorized next milestone specified by the authoring contract. Align the
three program documents and context index without granting authority. Add the
standard-library governance tests for schema, pins, vocabularies, dependency
acyclicity, authority safety, sequence, and document alignment.

Run the declared JSON, focused pytest, Ruff, mypy, diff, and `make validate`
gates on the feature branch. Publish `ready_for_review` only after the frozen
tree passes; otherwise publish an evidenced `blocked` state. No PR or merge is
authorized.
