# MIP Consumer-Readiness Map

Observed October 15, 2026. Pins: MIP `421dd57` (authorized task head;
this map's baseline is the merged main behind it), GeoX `3c2f7ec`,
MMM `a9db646`. Sibling contents were read from checkouts at exactly
those pins with no fetch, no writes, and no sibling changes. Live
remote equality of both sibling pins was confirmed before reading.
Contract meaning for consumer views lives in the P2
consumer/fixture-journey design and the contract modules cited below;
this map adds only the evidence-readiness rows, restating no producer
definitions.

## Requirement → evidence rows

| # | Pinned consumer requirement (MIP path) | Merged producer evidence or MISSING | Missing owner decision | Future acceptance case |
|---|---|---|---|---|
| 1 | Envelope presence fields including `provenance` (`src/mip/contracts/geox_envelope_consumer.py`, `REQUIRED_FIELDS`; missing → `REJECTED`) | GeoX manifest `provenance` vocabulary present on GeoX main (`panel_exp/contracts/geox_calibration_source_manifest.py` — `source_repo`, `source_commit`, `producer_package_version`, `created_by`) | GeoX owner: which values count as certified | Accept envelope iff provenance matches the certified definition |
| 2 | Value-validated envelope statuses (`evaluate_geox_envelope_for_mip_consumption`: kind ∈ `KNOWN_KINDS`, auth and consumption enums; capped at diagnostic/answerability context) | Implemented MIP-side; producer certified meanings unresolved | GeoX owner: certified-value meanings | Value acceptance once certified meanings are defined |
| 3 | Required sibling export labels (`src/mip/adapters/sibling_producer_specs.py`: `static_export_file_only`, `not_live_engine_execution`, `not_real_model_result`, `diagnostic_only`, `not_decision_ready`) | MISSING on both live pins: neither `mmm/integrations/mip/exports/` nor `panel_exp/integrations/mip/exports/` exists, and the labels occur nowhere in either repo | Sibling owners: export-surface provision | Label check passes once sibling exports exist |
| 4 | Compatibility-state fixtures for pair tests | Five MMM goldens exist (`MMM/tests/fixtures/mip_export/calibration_compatibility_v1/`: compatible, compatible_with_warning, incompatible, stale, blocked) with synthetic-only lineage (no `source_commit`, no GeoX repo reference, no certification marker) | — (goldens usable as-is for state coverage) | State-matrix coverage with these goldens now |
| 5 | Certified GeoX-provenance-linked pairs (parked bridge `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`) | MISSING: no golden pairs any compatibility state with a certified GeoX source commit | GeoX owner: certified provenance event; MMM owner: paired fixtures | Pair acceptance only after certified GeoX; paired work cannot start before it. Bridge stays parked |
| 6 | R12 diagnostic curves as bridge input | EXCLUDED: zero R12 references in MIP adapters, envelope consumer, and capability ledger; MMM's own response-surface contract states R12 independence of bridge order | None (not a prerequisite) | Never a bridge prerequisite |

Notes: `certification_status` occurs only in GeoX manifest vocabulary
(verified absent from the MIP envelope consumer); its certified
meanings are unresolved in GeoX and are not defined here. The parked
compatibility bridge (`480b320`, blocked) is preserved unchanged.

## Unverified assumption (non-blocking)

Synthetic lineage-namespace isolation (MMM golden IDs such as
`evaluation-001` never colliding with real artifact namespaces) is
unverified and stays an assumption, not a blocker: no consumer
invariant branches on lineage IDs — presence checks cover
`REQUIRED_FIELDS` only and value checks cover kind/auth/consumption
exclusively. It becomes a blocker only if a concrete consumer
invariant ever touches those IDs.

## Evidence

- MIP consumer contract and validators: `src/mip/contracts/geox_envelope_consumer.py` at `421dd57`.
- MIP producer-label requirements: `src/mip/adapters/sibling_producer_specs.py` at `421dd57`.
- MIP parked bridge record: `docs/execution/EXECUTION_STATE.json` parked workstream at `421dd57`.
- GeoX manifest vocabulary: `panel_exp/contracts/geox_calibration_source_manifest.py` at `3c2f7ec`.
- MMM goldens: `MMM/tests/fixtures/mip_export/calibration_compatibility_v1/` (five states) at `a9db646`.
- MMM response-surface status: authorized definition-publication task at `a9db646` (proposal only, not adopted).
- Design meaning (referenced, not restated): `docs/roadmap/MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md`.
