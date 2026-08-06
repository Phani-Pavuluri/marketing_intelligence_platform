# Program Current State

**Status:** current verified P2 capability snapshot
**Owner:** MIP program owner
**Last updated:** 2026-08-05
**Last verified:** 2026-08-05
**Verified against:** MIP `main` `c3897ed0b1ca096d186a9cabda36e1b926c4e71f`; MMM `main` `fe8e784923994406a2e4907d28debd872d61fd73`; GeoX `main` `b11646bab1f461964644a6526ef4967a8f04624d`
**Update trigger:** a merged capability checkpoint, completed validation or certification gate, consumer verification, or authority change.

## Current phase

The program remains at the fixture-only P2 preparation boundary. The current
missing checkpoint is `P2_GEOX_CALIBRATION_SOURCE_PRODUCER_CHECKPOINT`.
Long-range sequencing remains in the repository roadmaps; current capability
truth and dependency eligibility are recorded in
[`P2_CAPABILITY_CHECKPOINT_LEDGER.json`](P2_CAPABILITY_CHECKPOINT_LEDGER.json).
Execution authority remains repository-local in each repository's synchronized
`docs/execution/` files.

## Current capability position

| Capability | Implementation | Validation / certification | Downstream status |
|---|---|---|---|
| GeoX calibration-source generator | Merged on GeoX main | Component-validated; not producer-certified | Blocked |
| GeoX calibration-source validator | Present on GeoX main | Normal package-import execution and exact-tree certification remain unproven | Blocked |
| Combined GeoX calibration-source producer | Present on GeoX main | Incomplete and uncertified | Blocked |
| MMM provenance-linked compatibility fixtures | Not started | Requires a certified GeoX producer checkpoint | Blocked |
| MIP GeoX/MMM compatibility bridge | Parked at `480b32040ce185b8ff091435121c4bea6fc6c453` | Consumer verification unavailable | Blocked |
| D6 release-compatibility evidence | Not started | Requires the verified bridge | Blocked |
| Fixture-only planning-evidence journey | Not started | Requires D6 evidence | Blocked |

A merged implementation, component test result, producer certification,
consumer verification, and downstream eligibility are separate states. A
feature-branch head is never merged capability evidence.

## Next eligible work

Only `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001` is next
eligible for separate GeoX task authoring and authorization. It is not
authorized by MIP. Its bounded outcome is to prove normal package/import test
isolation for the existing generator and validator surfaces and record the
remaining certification gap. It must not certify the producer or change MMM or
MIP behavior.

The complete unauthorized sequence is maintained in
[`NEXT_EXECUTION_SEQUENCE.md`](NEXT_EXECUTION_SEQUENCE.md) and the machine-readable
ledger.

## Authority freezes

No sibling task, GeoX certification, MMM implementation, parked-bridge resume,
`CalibrationSignal` construction, simulation, optimization, planning,
recommendation, real-data use, runtime integration, pilot, or production action
is authorized by this snapshot.

Detailed sources: [Repository checkpoints](REPOSITORY_CHECKPOINTS.md),
[Authority and freeze matrix](AUTHORITY_AND_FREEZE_MATRIX.md), and
[the P2 consumer design](../roadmap/MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md).

Historical coordination provenance remains `18ab0d0c798dfcedd3f07034f4561320929477ea`
(MIP), `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421` (MMM), and
`ee9673c13e69082367c1727568946ac4c1a01015` (GeoX); it is not current P2
capability evidence.
