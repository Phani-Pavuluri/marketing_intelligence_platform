# Active Task

**Status:** blocked
**Task ID:** `MIP_P2_CAPABILITY_CHECKPOINT_LEDGER_RECOVERY_001`
**Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
**Pre-authoring evidence base:** `9762afccca0790dd897f833d4dbea2f847aa6401`
**Feature branch:** `docs/mip-p2-capability-checkpoint-ledger-recovery-001`
**Execution mode:** `branch_and_fast_forward`
**Risk tier:** Tier 3
**Capability authority changed:** `false`
**Unresolved execution-blocking design questions:** none

## Objective

Create one machine-readable P2 capability-checkpoint ledger and align MIP
program-navigation documents. The ledger distinguishes implementation on main,
component validation, producer certification, consumer verification, and
downstream eligibility. This is program tracking only: it does not modify or
certify GeoX/MMM, resume the parked bridge, construct CalibrationSignal, alter
TrustReport/DecisionSurface, or authorize analytical, runtime, planning,
recommendation, real-data, pilot, or production behavior.

## North-star and control

`certified GeoX producer evidence -> provenance-linked MMM compatibility fixtures -> MIP GeoX/MMM compatibility bridge -> D6 release-compatibility evidence -> fixture-only planning-evidence journey`

Current missing checkpoint: `P2_GEOX_CALIBRATION_SOURCE_PRODUCER_CHECKPOINT`
Next eligible (unauthorized) milestone:
`GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001` in
`Phani-Pavuluri/panel_exp`.

## Verified source checkpoints

- MIP: `9762afccca0790dd897f833d4dbea2f847aa6401`; parked bridge
  `feat/mip-p2-geox-mmm-compatibility-fixture-bridge-001` at
  `480b32040ce185b8ff091435121c4bea6fc6c453`, blocked by
  `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`.
- MMM: `fe8e784923994406a2e4907d28debd872d61fd73`; compatibility contract and
  existing fixtures are not a provenance-linked GeoX/MMM pair; no MMM task is
  authorized.
- GeoX: `b11646bab1f461964644a6526ef4967a8f04624d`, disposition
  `superseded_without_merge`; generator `d0f0ba937c79528abd34d7ff89eb4601080805e9`,
  validator lineage `c1d1311494e7cc637141b09097ef929567a960f6`, rejected
  implementation `89c3ded7620b85e382cecec5243ca84f8fb93c95`, rejected head
  `c18f56341b50c58505b59fc6cacf2337ca7f9fc4`, divergent historical head
  `2b6745b9cbcf5a17196796231a39fec4336b5d1f`.

## Owned paths

The implementation may modify only the P2 ledger JSON, current-state,
checkpoint, sequence and context-index documents, the new governance test, and
the three execution files. Source/runtime code, existing tests/fixtures,
coordination history, standards, CI/Docker/dependencies, MMM, GeoX, and the
parked bridge are prohibited. No PR, merge, squash, rebase, force-push or merge
commit is authorized.

## Ledger contract and classifications

Create `docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json` with schema
`mip_p2_capability_checkpoint_ledger_v1`, program
`causal_marketing_intelligence_platform`, phase `P2`, missing checkpoint above,
`last_verified: 2026-08-05`, ordered source precedence from synchronized mains
through chat summaries, exactly `mip`, `mmm`, `geox` observations, the exact
six-item sequence, seven acyclic capability records, and an authority object
whose sibling-task, GeoX-certification, MMM, bridge, CalibrationSignal,
simulation, optimization, planning, recommendation, real-data, runtime, pilot
and production flags are all false.

Required capability states are: GeoX generator merged/component-validated;
GeoX validator present on main but incomplete/uncertified and blocked; combined
GeoX producer present but blocked/uncertified; MMM linked fixtures not started
and blocked; parked MIP bridge blocked at its exact head; D6 evidence and the
planning journey not started and blocked. Dependencies must resolve and be
acyclic; feature branches are not merged evidence.

The six-item sequence is exactly:

1. `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001`
2. `GEOX_CALIBRATION_SOURCE_MANIFEST_CERTIFICATION_RECOVERY_001`
3. `P2_MMM_PROVENANCE_LINKED_COMPATIBILITY_FIXTURES`
4. `P2_MIP_GEOX_MMM_COMPATIBILITY_BRIDGE`
5. `P2_D6_RELEASE_COMPATIBILITY_EVIDENCE`
6. `P2_MIP_PLANNING_EVIDENCE_JOURNEY`

All are unauthorized; only the first is next eligible.

## Governance and validation

Create the standard-library governance test covering exact schema/constants,
repository pins and SHA format, seven capability keys, vocabularies, resolved
acyclic dependencies, false authority, unauthorized next milestone,
certification/validation invariants, parked bridge head, sequence, document
alignment and stale-pin rejection. Required execution validation is JSON
parsing, focused pytest, Ruff, mypy, `git diff --check`, and `make validate` on
the frozen feature tree. Task-owned failures must be corrected, not hidden as
environment blockers. Publish `ready_for_review` only after the complete gate;
otherwise publish an evidenced `blocked` result. No sibling authority changes.

## Blocked execution result

Implementation is present at
`4fd95a3b9075ca38a5469b591bb346df1552c19c`. JSON parsing, focused governance
pytest (`5 passed`), and changed-file `git diff --check` passed after correcting
task-owned trailing whitespace. Required Ruff, mypy, repository Docker
`make validate`, and exact-tree receipt could not run in the available execution
environment because no complete checkout is mounted, direct GitHub DNS access
is unavailable, and Docker/Ruff/mypy binaries are absent.

Resolution condition: resume this exact branch in a synchronized repository
environment, verify the implementation head and current branch ancestry, run the
complete declared Tier 3 gate on the frozen task-owned tree, and publish either
`ready_for_review` or a new evidenced blocked state. Do not alter task meaning,
sibling state, analytical behavior, or capability authority.
