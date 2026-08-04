# Program Current State

**Status:** current live-overlay snapshot; no capability authority
**Owner:** MIP program governance
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03
**Verified against:** MIP `main` `976d3a1daeae9c52c8772e5112574f698951a57c`; MMM `origin/main` `b8878dfa4bcd178a0472c3b812492a5bb4ac0b45`; GeoX `origin/main` `d17bb81c9dbc67f773fd71068c26b14c92989f42`

## Current phase

The program remains at the fixture-only P2 preparation boundary. P0–P8 remains
the product lifecycle and R0–R6 remain binding cross-cutting gates in
[`ROADMAP.md`](../roadmap/ROADMAP.md). This current-state reconciliation does
not alter either lifecycle or authorize product/runtime work.

MIP is executing the MIP-only governance task
`MIP_P2_ROADMAP_AND_COORDINATION_RECONCILIATION_AFTER_GEOX_SUPERSESSION_001`.
The stale resolver branch is superseded without merge and is historical partial
evidence only; resolver reauthoring is deferred and unauthorized.

## Live sibling overlay

| Repository | Live `origin/main` | Current execution evidence | Dependency meaning |
|---|---|---|---|
| MIP | `976d3a1` | Reconciliation task authorized on its declared MIP branch. | Governance snapshot only; no P2 implementation authority. |
| MMM | `b8878df` | `MMM_REPOSITORY_EXECUTION_PROTOCOL_ADOPTION_001` is authorized. The former MMM protocol task is absorbed, not separately executable. | No merged MMM normalization or fixture evidence exists. |
| GeoX | `d17bb81` | `GEOX_EXECUTION_BRANCH_BINDING_001` is authorized at `dc68853` on `feat/geox-execution-branch-binding-001`. The prior lean-delivery task and builder are superseded without merge. | Authorization is not merge completion. No GeoX governance or producer successor is merged. |

## P2 critical path and blockers

The former single GeoX builder task is not active execution. GeoX has authorized
its branch-binding governance task, which must still merge and close before
GeoX can separately declare and complete the following proposed outcomes: a
governed-readout temporal lifecycle contract; typed producer builder; certified
fixture generation with hashes and replay semantics; and optional envelope plus
final handoff/integration validation. MIP does not assign task IDs or authorize
those owner-repository successors.

`P2-GEOX-TEMPORAL-VERSION-SEMANTICS` and
`P2-GEOX-READOUT-BUILDER-ENTRYPOINT` remain open. MMM normalization and
certified cross-repository fixtures remain proposed until the exact merged GeoX
producer sequence, full producer validation, and MMM consumer verification
exist. The MIP P2 fixture-only planning-evidence journey remains proposed and
unauthorized until exact merged GeoX and MMM evidence, declared MIP consumer
verification, and D6 release/compatibility evidence exist.

## Authority freezes

Runtime package integration, live MMM/GeoX, real customer data, uploads,
persistent customer/product artifacts, jobs, simulation runtime, optimization,
recommendations, treatment assignment, pilot, and production remain blocked.
See [Authority and Freeze Matrix](AUTHORITY_AND_FREEZE_MATRIX.md) and
[Coordination State](CROSS_REPOSITORY_COORDINATION_STATE.json).
