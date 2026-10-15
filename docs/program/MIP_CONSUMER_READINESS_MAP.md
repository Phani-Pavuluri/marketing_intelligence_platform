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

## Evidence snapshots (read-only, October 15, 2026)

Full pins: MIP `421dd57da7d1ef66a975762c8791a79b8784c06d`, GeoX
`3c2f7ec3dfb196c3308e8fb8f67c68d8ff5dc69e`, MMM
`a9db6469ed2654e19c20464c28717767990740ce`. Each blob below was read
with `git rev-parse <commit>:<path>` / `git show` / `git ls-remote`
against those pins; nothing was fetched, written, or modified.

MIP consumer surface at `421dd57`:

- `src/mip/contracts/geox_envelope_consumer.py`, blob
  `b37a78809f505997c3e9f032aa27bc7e89d1d4e5`. `REQUIRED_FIELDS`
  includes `provenance`, `release_gate_status`,
  `downstream_eligibility`, `mip_consumption_status`,
  `authorization_status` (absence → `REJECTED`); value-checked enums
  are `artifact_kind` ∈ `KNOWN_KINDS`, `authorization_status` ∈
  {`not_authorized`, `blocked`}, `mip_consumption_status` ∈
  {`diagnostic_context_only`, `answerability_context_only`,
  `blocked`}; outcomes capped at diagnostic/answerability context.
  `certification_status` occurs nowhere in this file.
- `src/mip/adapters/sibling_producer_specs.py`, blob
  `37d4948c232f4bbcb9c2873f999f01b99e180bdf`. Required labels:
  `static_export_file_only`, `not_live_engine_execution`,
  `not_real_model_result`, `diagnostic_only`, `not_decision_ready`;
  canonical sibling dirs `mmm/integrations/mip/exports/` and
  `panel_exp/integrations/mip/exports/`.

GeoX manifest at `3c2f7ec`, blob
`367aeffe04b97e0baa0108cf0287c5b235f14618`: required-keys tuple
present (fixture/evidence/readout/experiment IDs, versions,
`certification_status`, KPI/estimand/channel/scope/window/method
keys, status keys, producer version/commit, governed paths);
provenance validated only as non-empty strings for `source_repo`,
`source_commit`, `producer_package_version`, `created_by`;
`certification_status` occurs 3 times as vocabulary with no
certified-value definition in this file.

MMM goldens at `a9db646` (all five share top-level keys and the same
five lineage keys; lineage IDs are synthetic):

| File | Blob SHA | `compatibility_state` | Lineage keys |
|---|---|---|---|
| `compatible.json` | `f6a760fac8e0be1f760376d99b72573505d9cd4f` | `compatible` | `configuration_hash`, `evaluation_id`, `evidence_artifact_id`, `model_artifact_id`, `panel_id` |
| `compatible_with_warning.json` | `fa19b83f62a8fde9ca4c5f1185d6574a7c9270a5` | `compatible_with_warning` | same five |
| `incompatible.json` | `34cf5d204da71a034deb065ba71e3c2f23e5ac65` | `incompatible` | same five |
| `stale.json` | `92bb63606afc4c5346dc77334fedd47f2360ba48` | `stale` | same five |
| `blocked.json` | `905e1addc148d46822b97ca4f09933db37a6b250` | `blocked` | same five |

No golden contains `source_commit`, a GeoX repo reference, or a
certification marker (verified by content search), so none pairs any
state with certified GeoX provenance.

Sibling export-label absence (both live pins), commands and outputs:

- `ls mmm/integrations/mip/exports/` → `No such file or directory`;
  `ls panel_exp/integrations/mip/exports/` → `No such file or
  directory`.
- Repo-wide search for `static_export_file_only` in both clones'
  source and docs trees → no matches.

These snapshots are point-in-time reads. Re-run the listed commands
against the cited pins to confirm them independently; newer pins
supersede these values without changing the row structure above.
