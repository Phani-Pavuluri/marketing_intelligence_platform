# MIP Diagnostic Review Checklist

Review aid for the PROPOSED MMM diagnostic response-surface evidence
definition (`MMM/docs/05_validation/mmm_response_surface_evidence_contract.md`
at `e99768a8`) against existing MIP consumer invariants. This checklist
reviews a proposal; it adopts no interface, grants no certification, and
adds no parser, schema, fixture, or analytical capability. Producer
meanings belong to their repository owners — a mismatch is recorded for
the owning producer, never resolved here.

Observation pins: MIP `2b3ff4c` (task base and normative consumer
sources; verified byte-identical from `b0e7650` through current main
for every source path below — all intervening commits touched only
execution or program-report files, proven by empty diffs on source
paths), MMM `e99768a8` (proposal document object verified present),
GeoX `2ff493c` (manifest vocabulary; live main `104a745` carries a
provenance/finality definition task with no certified output).
Sibling live mains observed at MMM `c907841` (exclusive-endpoint
recovery authorized; response-surface proposal still unadopted) and
GeoX `104a745`; sibling contents below were read at exactly the
cited pins. Sibling canonical state is read from remote-main blobs,
never from possibly stale local checkouts.

## Evidence provenance legend

Each row is tagged. **[M] merged evidence:** replayable from the
reviewed MIP tree or a cited merged sibling blob via the listed
command. **[P] proposal-dependent:** verified read-only at pin
`e99768a8` only; absent from the reviewed tree's manifest, so the
reviewer re-verifies with `git cat-file -e
e99768a8:docs/05_validation/mmm_response_surface_evidence_contract.md`
(or the listed sibling command) and routes any mismatch to MMM.
Nothing here is asserted from the proposal beyond its PROPOSED
status, section topics, and read-verified semantics.

## 1. Diagnostic quantity versus causal estimand [M+P]

**Question:** is a diagnostic modeling-scale response (or slope)
distinguished from a causal estimand or level-space ROI, with no
silent conversion between them?
**Existing rule:** a diagnostic quantity need not map to
`CausalQuantity`; lack of such mapping alone is not a producer
mismatch. Causal-estimand mapping is required only where causal
meaning is claimed: `src/mip/contracts/estimand.py` (`Estimand`
requires non-empty `target_metric`, `unit`,
`treatment_definition`, `aggregation_level`) and
`src/mip/contracts/enums.py` (`CausalQuantity` values). The
proposal's own §3 states the grid is RAW spend while response is
modeling-scale, forbids double-transform, requires matching `(unit,
scale, transformation_id)` for range comparison, and leaves
`TRANSFORMED`-scale bounds not comparable in v1.
**Evidence required:** each claimed quantity labeled diagnostic or
causal; causal claims carry a `CausalQuantity` mapping, diagnostic
slopes carry RAW-scale transform semantics only.
**Mismatch/unknown:** diagnostic slope presented as a causal
estimand or level-space ROI, mixed scales, a resolved
`transformation_id` scheme presented as canonical (none exists in
merged code), or causal meaning claimed without mapping → record
for MMM; do not map units silently and do not demand causal
mapping where none is claimed.

## 2. Scope and range [M+P]

**Question:** are supported scenarios, constraints, and range
references present and record-scoped?
**Existing rule:** `src/mip/contracts/decision_surface.py`
(`supported_scenarios`, `constraints_supported`); proposal §1
(record-level range labels with validators) and §5 (explicitly
proposed per-point fields, length-matched, derived only against
comparable bounds; verified absent from merged MMM code, so
proposed-only status is confirmed, not assumed).
**Evidence required:** referenced bounds with matching scale;
per-point arrays length-matched to the grid where claimed.
**Mismatch/unknown:** per-grid-point evaluation asserted from
record-level labels, or missing bounds → record for MMM.

## 3. Uncertainty availability [M]

**Question:** is availability resolved from referenced artifacts
rather than assumed?
**Existing rule (merged MMM code at `4ccf8ca`, reconfirmed at
`00cad45` lineage):** `mmm/contracts/supported_range.py`
(`uncertainty_available: bool` with invariant: available requires
`uncertainty_artifact_reference`; unavailable cannot claim artifact
or semantics) and `MMMSimulationUncertaintyStatus` defaulting
`UNAVAILABLE` — not axiomatically unavailable and not axiomatically
available.
**Evidence required:** artifact reference for every `AVAILABLE` claim;
absence stays unavailable.
**Mismatch/unknown:** availability without artifact, or assumed
semantics → record for MMM.

## 4. Terminal failures and restrictions [M+P]

**Question:** do terminal status, failure codes, and restrictions
propagate without conversion to success?
**Existing rule:** merged `mmm/contracts/mip_failure.py`
(`MMMFailureCode` vocabulary) plus proposal §4 (separate typed
failures; `UNSUPPORTED_EXTRAPOLATION` requires a
`BLOCKED`/`RESTRICTED` claim effect — proposal-dependent); MIP
consumer rule that failure evidence never converts into success
(envelope `BLOCKED` handling).
**Evidence required:** failure/stage/disposition codes and restriction
effects preserved verbatim.
**Mismatch/unknown:** extrapolation presented as numeric position, or
blocked/restricted converted → record for MMM.

## 5. Provenance [M]

**Question:** are artifact, model, run, and version identities
non-empty and traceable?
**Existing rule:** `decision_surface.py` `non_empty_ids`
(`surface_id`, `model_id`, `artifact_fingerprint`); envelope
`provenance` presence rule; proposal lineage fields (shape only,
values producer-owned).
**Evidence required:** non-empty identity/version/lineage values;
missing values fail closed, never defaulted.
**Mismatch/unknown:** empty or defaulted identity → record for MMM.

## 6. Diagnostic certification boundaries [M]

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

## 7. Independence from calibration-bridge prerequisites [M]

**Question:** is R12 kept out of bridge readiness?
**Existing rule:** zero R12 references in MIP adapters, envelope
consumer, and capability ledger (verified); MMM's own proposal
states R12 independence of bridge order.
**Evidence required:** no bridge-prerequisite claim on R12 in either
direction.
**Mismatch/unknown:** any R12-as-prerequisite claim → record for the
owning side; paired-fixture work still cannot start before certified
GeoX provenance.

## 8. Artifact-kind distinction [M]

**Question:** does proposed evidence declare its artifact kind,
validated against the consumer vocabulary and distinct from
simulation, contribution/ROI, recommendation, TrustReport, and
certified decision artifacts?
**Existing rule:** envelope `KNOWN_KINDS` allow-list
(`src/mip/contracts/geox_envelope_consumer.py`; unknown kind →
`BLOCKED`); diagnostic-only kinds context from row 6 rules;
MMM simulation exports and TrustReport/recommendation classes are
separate owning-contract types, never interchangeable with
diagnostic response-surface evidence.
**Evidence required:** declared kind present in `KNOWN_KINDS` or
explicitly routed as unknown→`BLOCKED`; kind ≠ simulation,
contribution/ROI, recommendation, TrustReport, or certified
decision artifact unless the artifact actually is that class per
its owning contract.
**Mismatch/unknown:** unknown kind silently accepted, or
diagnostic evidence presented as another class → record for MMM.

## What this checklist does not do

No interface adoption, schema/parser/fixture work, analytical
execution, threshold or meaning changes, bridge execution, runtime
integration, or capability grants. Findings belong to producer
owners; MIP records them and reports them to the owner.

## Mapped evidence (read-only, October 16, 2026)

MIP consumer sources at task base `2b3ff4c` (identical blobs at
`b0e7650` and `46eecad` for every path below — all intervening
commits touched only execution or program-report files, proven by
empty diffs on source paths):

- `src/mip/contracts/geox_envelope_consumer.py`, blob
  `b37a78809f505997c3e9f032aa27bc7e89d1d4e5` — `REQUIRED_FIELDS`
  presence rule (missing → `REJECTED`) including `provenance`;
  value-checked enums for `artifact_kind`, `authorization_status`,
  `mip_consumption_status`; outcomes capped at diagnostic or
  answerability context with `_CANNOT_SAY` bounds.
- `src/mip/contracts/deterministic_report.py`, blob
  `6a2156643d3a6a638f1b947c953610a29a6ac172` —
  `_FORBIDDEN_CLAIM_FRAGMENTS` includes `response_curve` and
  `causal_lift`.
- `src/mip/contracts/decision_surface.py`, blob
  `ee18ced61c50cea00c412d25be18cbdfcb90b5dc` —
  `surface_certification_rules`, `supported_scenarios`,
  `constraints_supported`, `non_empty_ids`.
- `src/mip/contracts/enums.py`, blob
  `ffd8f392c9af96eb4665dadc4fb0d35b79d3a556` — `CausalQuantity`
  values and `ArtifactStatus` lifecycle.
- `src/mip/contracts/estimand.py`, blob
  `55553406fd709488b20ad883de715a3b187e7f4e` — `Estimand`
  required strings for metric, unit, treatment, aggregation.
- `KNOWN_KINDS` allow-list (11 entries: `geox_request`,
  `geox_result`, `assignment_candidate`, `assignment_manifest`,
  `run_manifest`, `readout_packet`, `failure_packet`,
  `post_test_spend_evidence`, `trusted_readout_spend_handoff`,
  `experiment_evidence_candidate`,
  `calibration_signal_candidate`); unknown kind → `BLOCKED`.
- MMM `mmm/contracts/public_simulation.py`, blob
  `bc19e9cfa04172484a39618531cfffddb0b28012` at live `c907841`
  (simulation export type, separate owning contract — never
  interchangeable with diagnostic response-surface evidence).

MMM proposal at `e99768a8`: document
`docs/05_validation/mmm_response_surface_evidence_contract.md`,
object presence verified (`git cat-file -e
e99768a8:docs/05_validation/mmm_response_surface_evidence_contract.md`).
Sections 1–9 per the proposal (existing/proposed names, ownership,
coordinate scales, scope failures, per-record shape, units/claims,
curve-bundle recommendation, acceptance examples, reserved
decisions). Proposal-dependent checks that cannot be replayed from
merged MIP evidence are labeled unknown in the rows above and routed
to MMM. Zero-R12 check for MIP: `grep -rn "R12"
src/mip/adapters/ src/mip/contracts/geox_envelope_consumer.py
docs/program/P2_CAPABILITY_CHECKPOINT_LEDGER.json` exits 1 with
empty output.

These snapshots are point-in-time reads. Re-run the listed commands
against the cited pins to confirm them independently; newer pins
supersede these values without changing the row structure above.
