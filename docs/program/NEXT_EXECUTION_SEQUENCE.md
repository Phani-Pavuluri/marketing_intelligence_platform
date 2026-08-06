# Next Execution Sequence

**Status:** dependency order only; no step is authorized by this file  
**Owner:** MIP program owner with GeoX and MMM repository owners  
**Last updated:** 2026-08-05  
**Last verified:** 2026-08-05  
**Verified against:** MIP `main` `c3897ed0b1ca096d186a9cabda36e1b926c4e71f`; MMM `main` `fe8e784923994406a2e4907d28debd872d61fd73`; GeoX `main` `b11646bab1f461964644a6526ef4967a8f04624d`  
**Update trigger:** a prerequisite merge, certification, consumer verification, D6 packet, or explicit repository-local task authorization.

1. `GEOX_MAIN_TEST_ISOLATION_AND_CHECKPOINT_CONTEXT_RECOVERY_001`
   - Owner: GeoX.
   - State: next eligible, unauthorized.
   - Outcome: prove normal package/import test isolation and establish exact
     component-validation context without claiming producer certification.

2. `GEOX_CALIBRATION_SOURCE_MANIFEST_CERTIFICATION_RECOVERY_001`
   - Owner: GeoX.
   - State: blocked and unauthorized.
   - Dependency: step 1 merged with its declared evidence.
   - Outcome: certify the combined producer on an exact frozen GeoX tree.

3. `P2_MMM_PROVENANCE_LINKED_COMPATIBILITY_FIXTURES`
   - Owner: MMM.
   - State: blocked and unauthorized.
   - Dependency: certified GeoX producer evidence at an exact merged pin.
   - Outcome: provenance-linked compatibility fixtures under MMM numerical truth.

4. `P2_MIP_GEOX_MMM_COMPATIBILITY_BRIDGE`
   - Owner: MIP.
   - State: blocked and unauthorized.
   - Dependencies: certified GeoX producer and merged MMM provenance-linked fixtures.
   - Outcome: consumer verification and the canonical fixture-only bridge.

5. `P2_D6_RELEASE_COMPATIBILITY_EVIDENCE`
   - Owner: MIP coordination with producer-owner verification.
   - State: blocked and unauthorized.
   - Dependency: verified MIP bridge.
   - Outcome: pins, compatibility matrix, failure semantics, release/rollback
     order, owners, and consumer verification.

6. `P2_MIP_PLANNING_EVIDENCE_JOURNEY`
   - Owner: MIP.
   - State: blocked and unauthorized.
   - Dependency: D6 release-compatibility evidence.
   - Outcome: first complete fixture-only planning-evidence workflow.

No step may absorb its successor. GeoX certification is separate from test
isolation; MMM fixture production is separate from MIP consumer mapping; D6 is
separate from the planning journey. No live package integration, real data,
`CalibrationSignal` construction, simulation, optimization, recommendation,
pilot, or production work is authorized.

Machine-readable state and dependency evidence are in
[`P2_CAPABILITY_CHECKPOINT_LEDGER.json`](P2_CAPABILITY_CHECKPOINT_LEDGER.json).
