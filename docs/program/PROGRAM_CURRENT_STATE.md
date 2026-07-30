# Program Current State

**Status:** current verified snapshot
**Owner:** MIP program owner
**Last updated:** 2026-07-30
**Last verified:** 2026-07-30
**Verified against:** MIP `89caf56e73e814b6f5e0d0584536f8705ac97803`; MMM `origin/main` `9a3aa5cb9a48c9a59d45e266685228835237f328`; GeoX `origin/main` `860182386c39f487747de5f43e67a31e9978e57c`
**Update trigger:** a merged checkpoint, completed gate, or changed authority state.

## Current phase

The program is at the fixture-only P2 preparation boundary: the MIP consumer
contract and fixture-journey design is merged, while package integration remains
blocked. P0–P8 and R0–R6 are canonical in
[`ROADMAP.md`](../roadmap/ROADMAP.md).

## Verified checkpoints and completed milestone

| Repository | Verified checkpoint | Current verified evidence |
|---|---|---|
| MIP | `89caf56` | P0–P8 consolidation and the P2 consumer/fixture design, including GeoX handoff and MMM compatibility state vocabulary. |
| MMM | `9a3aa5c` | `MMMPublicSimulationExport`, bounded Ridge fixture comparison, supported-range evidence, and `MMMCalibrationCompatibilityResult` with five compatibility fixtures. |
| GeoX | `8601823` | numerical-truth generator/validation, `GeoXGovernedExperimentReadout` contract, and certified governed-readout fixtures. |

The current first evidence tranche remains: certified GeoX experiment evidence
→ MMM calibration compatibility → MMM bounded baseline-versus-candidate
comparison → MIP planning-evidence journey → concrete D6 evidence.

## Eligible next MIP work and blockers

The next MIP-owned work that may be considered for separate authorization is a
fixture-only P2 consumer and planning-evidence journey implementation, using
only certified producer fixtures and the merged MIP design. It is not yet
authorized by this packet.

Immediate blockers are: GeoX's governed readout builder/package entrypoint and
temporal/freshness/record-envelope/package-version semantics; MMM's strict GeoX
readout normalization adapter and certified cross-repository compatibility
fixtures; and final D6 version, compatibility, release, rollback, migration,
failure, and owner evidence.

## Authority freezes

Runtime package integration, live MMM/GeoX, real customer data, uploads,
persistent customer/product artifacts, jobs, simulation runtime, optimization,
recommendation lifecycle, treatment assignment, pilot, and production remain
blocked. See [Authority and Freeze Matrix](AUTHORITY_AND_FREEZE_MATRIX.md) and
[Next Execution Sequence](NEXT_EXECUTION_SEQUENCE.md).

Detailed sources: [MIP P2 consumer design](../roadmap/MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md),
[Repository checkpoints](REPOSITORY_CHECKPOINTS.md), and
[Decision register](DECISION_REGISTER.md).
