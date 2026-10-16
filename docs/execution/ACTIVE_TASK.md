<!-- BEGIN MIP TASKCTL EXECUTION VIEW -->
# Active Task

**Status:** proposed

_Generated from `EXECUTION_STATE.json`; do not edit._

- **Task ID:** `MIP_FIXTURE_JOURNEY_RESOLVER_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Execution mode:** `branch_and_fast_forward`
- **Base SHA:** `5f7862b8bf5dc611afc7f18b360f852d5996d55b`
- **Authorization provenance:** `5f7862b8bf5dc611afc7f18b360f852d5996d55b`
- **Feature branch:** `feat/mip-fixture-journey-resolver-001`
- **Feature branch created:** `false`
- **Task execution authorized:** `false`
- **Correction execution authorized:** `false`
- **Merge authorized:** `false`
- **PR creation authorized:** `false`
- **Implementation commit:** `null`
- **Reviewed head:** `null`
- **Rejected review head:** `null`
- **Rejected implementation commit:** `null`
- **Approval commit:** `null`
- **Blockers:** `none`
- **Maximum correction cycles:** `1`
- **Correction cycles completed:** `0`
- **Correction cycles remaining:** `1`
- **Review decision:** `proposed`
- **Local feature-branch cleanup:** `null`
- **Remote feature-branch cleanup:** `null`
- **Capability authorizations changed:** `false`
<!-- END MIP TASKCTL EXECUTION VIEW -->

## MIP_FIXTURE_JOURNEY_RESOLVER_001

Deliver one independently reviewable, fixture-only resolver for the adopted MIP evidence-first direction. The resolver must derive its result from producer-shaped normalized inputs and preserve every simultaneous issue while selecting the strongest headline under the fixed precedence below. It must not change live consumers or grant analytical, recommendation, bridge, certification, production, sibling or capability authority.

The owned implementation is limited to `src/mip/evidence/fixture_journey.py` and `tests/evidence/test_fixture_journey.py`; lifecycle files are changed only through native `taskctl`. The module has no importers in this task and is additive with a single-commit rollback path.

### Contract

`resolve_fixture_journey(inputs)` is pure, deterministic and never raises on producer data. It accepts one top-level `schema_version` equal to `mip_fixture_journey_input_v1`, optional closed mappings `geox_readout`, `mmm_compat`, `mmm_sim`, and optional closed `context`; at least one producer view is required and extra keys are rejected as `unmapped_literal`. There is no caller-claimed row.

`geox_readout` mirrors the verified GeoX readout contract: required identity, version, KPI/estimand/effect-scale, freshness, uncertainty, method/readout/handoff statuses, reason lists, lineage, provenance, replay metadata and all-false authorization flags; optional producer metadata and finite analytical values remain opaque. `mmm_compat` mirrors `MMMCalibrationCompatibilityResult` with its required source/model context, lineage, decisions, compatibility state, unique reason codes and warning/blocker objects, including the producer state invariants. `mmm_sim` mirrors `MMMPublicSimulationExport` with fixed schema/package/kind literals, baseline and candidate plans, comparison metrics and range evaluations, terminal status, references, typed failure packet when blocked/failed, matching run manifest, and artifact identity containing the run ID. Unknown versions, missing required fields, unsupported literals, true authorization flags, invalid producer invariants and unsupported consumption return typed admission failures.

`context` is closed to `consumption` (`diagnostic_context_only`, `answerability_context_only`, `blocked`), `static_labels` from the verified static label set, and `supersedes` containing an artifact ID and source commit. Diagnostic and research-only single rows are admitted only from the static/context path; a compatibility method mark co-fires producer `BLOCKED` and therefore remains a blocked co-match with the mark retained.

The result has fixed row IDs, a closed twelve-literal `report_status`, matrix-order `matched_rows`, one deterministic headline, deduplicated stable issue/warning/limitation unions, verbatim lineage/version fields, `human_review_required=True`, and permitted/prohibited claim IDs composed by all-match intersection. Admission failures return typed `{code, detail}` failures; contradictory known evidence returns the conflict row rather than an admission failure. No default success is fabricated.

### Rows and precedence

The fixed rows are `r01_success`, `r02_success_with_warning`, `r03_stale`, `r04_incompatible`, `r05_blocked_handoff`, `r06_blocked_simulation`, `r07_producer_failure`, `r08_diagnostic_only`, `r09_research_only`, `r10_unavailable_uncertainty`, `r11_range_restriction`, and `r12_conflict_superseded`. Headline precedence is conflict/superseded, producer failure, blocked, incompatible, stale, diagnostic-only, research-only, unavailable uncertainty, range restriction, success-with-warning, success. Same-severity ties are deterministic. Issues are never discarded; all restrictions remain active in claim intersection. The twelve fixtures must cover all rows plus unknown-version, missing-field, unmapped-literal, and four collision cases, including failure-plus-lineage conflict, failure-plus-successor supersession, stale-plus-warning, warned-plus-unavailable, and research-only-plus-warning.

### Required validation

Run focused resolver tests, native `taskctl check`, JSON parsing, `git diff --check`, the full repository pytest suite, Ruff, mypy, and Docker-backed `make validate` on the exact frozen tree; rerun the required gate after fast-forward. Native exact-head review must name commit/tree and preserve an implementation-parent receipt. Docker is required for this Tier 2 package surface. No gate is waived and no live consumer is modified.

The task is definition-ready and remains unexecuted until native Git authorization is recorded. Muse owns implementation choices and execution after authorization.
