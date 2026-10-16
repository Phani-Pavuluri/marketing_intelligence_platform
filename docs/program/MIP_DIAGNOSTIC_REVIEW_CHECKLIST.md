# MIP Diagnostic Review Checklist

Review aid for the PROPOSED MMM diagnostic response-surface evidence
definition (`MMM/docs/05_validation/mmm_response_surface_evidence_contract.md`
at `e99768a8`) against existing MIP consumer invariants. This checklist
reviews a proposal; it adopts no interface, grants no certification, and
adds no parser, schema, fixture, or analytical capability. Producer
meanings belong to their repository owners — a mismatch is recorded for
the owning producer, never resolved here.

Observation pins: MIP `b0e7650` (task base and normative consumer
sources; verified byte-identical through `46eecad` — intermediate
commits touched only execution files, proven by an empty diff on all
source paths below), MMM `e99768a8` (proposal document object
verified present), GeoX `2ff493c`. Sibling live mains observed at
MMM `4ccf8ca` and GeoX `2ff493c`; sibling contents below were read at
exactly the cited pins.

## 1. Quantity and units

**Question:** does every curve quantity map to a MIP `CausalQuantity`
with matching units, without silent conversion?
**Existing rule:** `src/mip/contracts/estimand.py` (`Estimand` requires
non-empty `target_metric`, `unit`, `treatment_definition`,
`aggregation_level`); `src/mip/contracts/enums.py`
(`CausalQuantity`: lift, incremental_impact, delta_mu, contribution,
elasticity, roi, iroas). The proposal's own §3 states the grid is RAW
spend while response is modeling-scale, forbids double-transform, and
requires matching `(unit, scale, transformation_id)` for range
comparison, with `TRANSFORMED`-scale bounds not comparable in v1.
**Evidence required:** per-quantity mapping to `CausalQuantity` values
plus the proposal's transform-semantics note.
**Mismatch/unknown:** unmapped quantity, mixed scales, or a resolved
`transformation_id` scheme presented as canonical (none exists in
merged code) → record for MMM; do not map units silently.

## 2. Scope and range

**Question:** are supported scenarios, constraints, and range
references present and record-scoped?
**Existing rule:** `src/mip/contracts/decision_surface.py`
(`supported_scenarios`, `constraints_supported`); proposal §1
(record-level range labels with validators) and §5 (explicitly
proposed per-point fields, length-matched, derived only against
comparable bounds).
**Evidence required:** referenced bounds with matching scale;
per-point arrays length-matched to the grid where claimed.
**Mismatch/unknown:** per-grid-point evaluation asserted from
record-level labels, or missing bounds → record for MMM.

## 3. Uncertainty availability

**Question:** is availability resolved from referenced artifacts
rather than assumed?
**Existing rule:** merged MMM pattern carried in the proposal
(`uncertainty_available: bool` requires an artifact reference;
`MMMSimulationUncertaintyStatus` with `UNAVAILABLE` default) — not
axiomatically unavailable and not axiomatically available.
**Evidence required:** artifact reference for every `AVAILABLE` claim;
absence stays unavailable.
**Mismatch/unknown:** availability without artifact, or assumed
semantics → record for MMM.

## 4. Terminal failures and restrictions

**Question:** do terminal status, failure codes, and restrictions
propagate without conversion to success?
**Existing rule:** proposal §4 (separate typed failures;
`UNSUPPORTED_EXTRAPOLATION` requires a `BLOCKED`/`RESTRICTED` claim
effect); MIP consumer rule that failure evidence never converts into
success (envelope `BLOCKED` handling).
**Evidence required:** failure/stage/disposition codes and restriction
effects preserved verbatim.
**Mismatch/unknown:** extrapolation presented as numeric position, or
blocked/restricted converted → record for MMM.

## 5. Provenance

**Question:** are artifact, model, run, and version identities
non-empty and traceable?
**Existing rule:** `decision_surface.py` `non_empty_ids`
(`surface_id`, `model_id`, `artifact_fingerprint`); envelope
`provenance` presence rule; proposal lineage fields.
**Evidence required:** non-empty identity/version/lineage values;
missing values fail closed, never defaulted.
**Mismatch/unknown:** empty or defaulted identity → record for MMM.

## 6. Diagnostic certification boundaries

**Question:** does the proposal stay diagnostic-only with no
certified claims?
**Existing rule:** `decision_surface.py`
`surface_certification_rules` (diagnostic curves and decomposition
cannot be certified; certified requires full-panel delta-mu plus
scorecard); deterministic-report forbidden claim fragments include
`response_curve` and `causal_lift`; proposal preamble marks itself
PROPOSED with strict `extra="forbid"` and version policy.
**Evidence required:** explicit PROPOSED marking, no certified
language, no adoption claim.
**Mismatch/unknown:** any certified/adopted/production claim →
record for MMM; a positive checklist result is documentation review
only, never certification or adoption.

## 7. Independence from calibration-bridge prerequisites

**Question:** is R12 kept out of bridge readiness?
**Existing rule:** zero R12 references in MIP adapters, envelope
consumer, and capability ledger (verified); MMM's own proposal
states R12 independence of bridge order.
**Evidence required:** no bridge-prerequisite claim on R12 in either
direction.
**Mismatch/unknown:** any R12-as-prerequisite claim → record for the
owning side; paired-fixture work still cannot start before certified
GeoX provenance.

## What this checklist does not do

No interface adoption, schema/parser/fixture work, analytical
execution, threshold or meaning changes, bridge execution, runtime
integration, or capability grants. Findings belong to producer
owners; MIP records them and reports them to the owner.

## Mapped evidence (read-only, October 16, 2026)

Each cited rule resolves below by exact path, pin, and blob SHA, all
read with `git rev-parse <pin>:<path>`, `git show`, `git cat-file
-e`, or `git ls-remote` — no fetch, no writes. Re-run any entry to
confirm it independently.

MIP consumer sources at `b0e7650` (verified byte-identical through
`46eecad`):

- `src/mip/contracts/geox_envelope_consumer.py`, blob
  `b37a78809f505997c3e9f032aa27bc7e89d1d4e5` — `REQUIRED_FIELDS`
  presence rule (missing → `REJECTED`) including `provenance`;
  value-checked enums for `artifact_kind`, `authorization_status`,
  `mip_consumption_status`; outcomes capped at diagnostic or
  answerability context with `_CANNOT_SAY` bounds. Covers the
  envelope BLOCKED and provenance rows.
- `src/mip/contracts/deterministic_report.py`, blob
  `6a2156643d3a6a638f1b947c953610a29a6ac172` —
  `_FORBIDDEN_CLAIM_FRAGMENTS` includes `response_curve` and
  `causal_lift`; deterministic agent reports cannot claim them.
- `src/mip/contracts/decision_surface.py`, blob
  `ee18ced61c50cea00c412d25be18cbdfcb90b5dc` —
  `surface_certification_rules`: diagnostic curves and decomposition
  cannot be certified; certified requires full-panel delta-mu plus a
  reliability scorecard; `supported_scenarios` and
  `constraints_supported` fields.
- `src/mip/contracts/enums.py`, blob
  `ffd8f392c9af96eb4665dadc4fb0d35b79d3a556` — `CausalQuantity`
  values and `ArtifactStatus` lifecycle.
- `src/mip/contracts/estimand.py`, blob
  `55553406fd709488b20ad883de715a3b187e7f4e` — `Estimand` with
  non-empty `target_metric`, `unit`, `treatment_definition`,
  `aggregation_level`.

Zero-R12 transcript (both commands exit 0; first prints nothing):

```
$ grep -rn "R12" src/mip/adapters/ src/mip/contracts/geox_envelope_consumer.py docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json
(no output)
```

MMM proposal at `e99768a8`: document
`docs/05_validation/mmm_response_surface_evidence_contract.md`,
object presence verified (`git cat-file -e
e99768a8:docs/05_validation/mmm_response_surface_evidence_contract.md`).
Sections 1–9 per the proposal (existing/proposed names, ownership,
coordinate scales, scope failures, per-record shape, units/claims,
curve-bundle recommendation, acceptance examples, reserved
decisions). Proposal-dependent checks that cannot be replayed from
merged MIP evidence are labeled unknown in the rows above and routed
to the owning producer; nothing is asserted from the proposal beyond
its PROPOSED status and section topics.
