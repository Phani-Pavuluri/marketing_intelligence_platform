# Program Current State

**Status:** current verified snapshot
**Owner:** MIP program owner
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31
**Verified against:** MIP `631763cfb75fc42f8b1bf7025c5bce34c39097b5`; MMM `origin/main` `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`; GeoX `origin/main` `e0cef94c063b03b29e1e1760fb1c2320ce497b56`
**Update trigger:** a merged checkpoint, completed gate, or changed authority state.

## Current phase

The program is at the fixture-only P2 preparation boundary: the MIP consumer
contract and fixture-journey design is merged, while package integration remains
blocked. P0–P8 and R0–R6 are canonical in
[`ROADMAP.md`](../roadmap/ROADMAP.md).

The current MIP task establishes the cross-repository coordination control
plane. Its pinned state is informative only and fails closed when a sibling
remote main changes; see [Coordination State](CROSS_REPOSITORY_COORDINATION_STATE.json).

## Verified checkpoints and completed milestone

| Repository | Verified checkpoint | Current verified evidence |
|---|---|---|
| MIP | `631763c` observed / `4ddbe83` program checkpoint | P0–P8 consolidation, P2 consumer design, and the authorized coordination task. |
| MMM | `1b75d1d` | `MMMPublicSimulationExport`, compatibility contract/fixtures, and closed V2 workflow reconciliation. |
| GeoX | `e0cef94` | numerical-truth validation, governed-readout contract/fixtures, and an authorized producer-owned builder task. |

The current first evidence tranche remains: certified GeoX experiment evidence
→ MMM calibration compatibility → MMM bounded baseline-versus-candidate
comparison → MIP planning-evidence journey → concrete D6 evidence.

## Eligible next MIP work and blockers

The next MIP-owned work that may be considered for separate authorization is a
fixture-only P2 consumer and planning-evidence journey implementation, using
only certified producer fixtures and the merged MIP design. It is not yet
authorized by this packet.

Current P2 blockers are `P2-GEOX-TEMPORAL-VERSION-SEMANTICS`,
`P2-GEOX-READOUT-BUILDER-ENTRYPOINT`, `P2-MMM-GEOX-NORMALIZATION`,
`P2-MMM-CROSS-REPOSITORY-FIXTURES`, and
`P2-D6-RELEASE-COMPATIBILITY-EVIDENCE`. Their owners, evidence, and consumer
verification conditions are in the coordination state; none is resolved by a
producer task report alone.

## Authority freezes

Runtime package integration, live MMM/GeoX, real customer data, uploads,
persistent customer/product artifacts, jobs, simulation runtime, optimization,
recommendation lifecycle, treatment assignment, pilot, and production remain
blocked. See [Authority and Freeze Matrix](AUTHORITY_AND_FREEZE_MATRIX.md) and
[Next Execution Sequence](NEXT_EXECUTION_SEQUENCE.md).

Detailed sources: [MIP P2 consumer design](../roadmap/MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md),
[Repository checkpoints](REPOSITORY_CHECKPOINTS.md), and
[Decision register](DECISION_REGISTER.md).
