# Repository Checkpoints

**Status:** verified remote-main P2 inventory
**Owner:** MIP program owner; each repository owns its analytical and execution truth
**Last updated:** 2026-08-05
**Last verified:** 2026-08-05
**Verified against:** MIP `main` `c3897ed0b1ca096d186a9cabda36e1b926c4e71f`; MMM `main` `fe8e784923994406a2e4907d28debd872d61fd73`; GeoX `main` `b11646bab1f461964644a6526ef4967a8f04624d`
**Update trigger:** a relevant sibling-main change, capability transition, or D6 evidence packet.

| Repository | Verified main | Current P2 evidence | Unresolved work | Authority boundary |
|---|---|---|---|---|
| MIP | `c3897ed0b1ca096d186a9cabda36e1b926c4e71f` | P2 consumer design, coordination protocol, and the authorized capability-ledger recovery contract | Parked bridge at `480b32040ce185b8ff091435121c4bea6fc6c453`; D6 and planning journey blocked | MIP owns coordination, consumer contracts, reporting, LLM behavior, and UX; it cannot certify GeoX or determine MMM compatibility truth |
| MMM | `fe8e784923994406a2e4907d28debd872d61fd73` | Calibration compatibility contract and existing package fixtures | No certified provenance-linked GeoX/MMM fixture pair; no active implementation task | MMM owns model, compatibility, simulation, optimization, and MMM numerical truth |
| GeoX | `b11646bab1f461964644a6526ef4967a8f04624d` | Generator, strict validator surface, governed-readout source manifest, and 12-case generated manifest | Normal package-import test isolation and exact-tree producer certification are missing; prior task was superseded without merge | GeoX owns experiment design, inference, governed readouts, handoff eligibility, and experiment numerical truth |

## GeoX checkpoint detail

- Generator implementation checkpoint:
  `d0f0ba937c79528abd34d7ff89eb4601080805e9`.
- Validator main-line implementation lineage:
  `c1d1311494e7cc637141b09097ef929567a960f6`.
- Rejected and divergent historical heads
  `89c3ded7620b85e382cecec5243ca84f8fb93c95`,
  `c18f56341b50c58505b59fc6cacf2337ca7f9fc4`, and
  `2b6745b9cbcf5a17196796231a39fec4336b5d1f` are diagnostic history only.
  They must not be merged, cherry-picked, reused, or treated as certification
  evidence.

## Capability ledger relationship

[`P2_CAPABILITY_CHECKPOINT_LEDGER.json`](P2_CAPABILITY_CHECKPOINT_LEDGER.json)
records current implementation, validation, certification, consumer-verification,
and downstream-eligibility states. Repository roadmaps retain long-range
technical priorities. Repository execution files retain the single active task
and branch lifecycle. This checkpoint file summarizes verified main evidence
without replacing any of those authorities.
