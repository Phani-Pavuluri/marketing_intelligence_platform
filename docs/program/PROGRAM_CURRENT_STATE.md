# Program Current State

**Status:** current verified snapshot
**Owner:** MIP program owner
**Last updated:** 2026-07-31
**Last verified:** 2026-07-31
**Verified against:** MIP `3520176126d129e9288a9ce37591299ec856650a`; MMM `origin/main` `1b75d1d3c9f49d40f2b7ab71f524fbd2dc6d1421`; GeoX `origin/main` `ee9673c13e69082367c1727568946ac4c1a01015`
**Update trigger:** a merged checkpoint, completed gate, or changed authority state.

## Current phase

The program is at the fixture-only P2 preparation boundary: the MIP consumer
contract and fixture-journey design is merged, while package integration remains
blocked. P0–P8 and R0–R6 are canonical in
[`ROADMAP.md`](../roadmap/ROADMAP.md).

The cross-repository coordination control plane is merged and closed at MIP
`3520176`; its pinned state remains informative only and fails closed when a
sibling remote main changes. The active post-merge reconciliation is MIP-only
governance and does not reopen that workstream; see
[Coordination State](CROSS_REPOSITORY_COORDINATION_STATE.json).

## Verified checkpoints and completed milestone

| Repository | Verified checkpoint | Current verified evidence |
|---|---|---|
| MIP | `3520176` prior coordination closure | P0–P8 consolidation, P2 consumer design, and the merged coordination control plane. |
| MMM | `1b75d1d` | `MMMPublicSimulationExport`, compatibility contract/fixtures, and closed V2 workflow reconciliation. |
| GeoX | `ee9673c` observed / `e0cef94` prior V2 closure | numerical-truth validation, governed-readout contract/fixtures, and one authorized producer-owned builder task covering temporal/version semantics plus builder/package entrypoint. |

The current first evidence tranche remains: certified GeoX experiment evidence
→ MMM calibration compatibility → MMM bounded baseline-versus-candidate
comparison → MIP planning-evidence journey → concrete D6 evidence.

## Eligible next MIP work and blockers

`MIP_ACTIVE_TASK_CONTEXT_RESOLVER_001` may be considered only through separate
authorization after this reconciliation is merged; it is not authorized by this
packet. Fixture-only P2 consumer work also remains separately unauthorized.

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
