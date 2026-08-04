# Active Task

**Status:** blocked
**Owner:** MIP integration and consumer-contract owner
**Last updated:** 2026-08-03
**Last verified:** 2026-08-03

## Identity

- **Task ID:** `MIP_P2_GEOX_MMM_COMPATIBILITY_FIXTURE_BRIDGE_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `f8fb482e51697f004d3fa2a6b229f6729d423cef`
- **Feature branch:** `feat/mip-p2-geox-mmm-compatibility-fixture-bridge-001`
- **Execution mode:** `branch_and_fast_forward`
- **Roadmap phase:** P2 certified planning-evidence lifecycle
- **Risk tier:** Tier 3 — cross-repository producer-contract and certified-fixture integration
- **Capability authorizations changed:** `false`

## Primary independently mergeable outcome

Implement the first executable P2 producer-consumer bridge in MIP:

```text
certified GeoX governed-readout fixture
→ authoritative MMM calibration-compatibility fixture
→ strict MIP consumer views and terminal bridge state
```

The bridge proves that MIP can consume and reconcile producer-owned experiment-readout and model-compatibility artifacts without recomputing GeoX truth, constructing compatibility itself, or weakening either producer state.

This task does not yet consume `MMMPublicSimulationExport`, construct `PlanningEvidenceReport`, call either sibling package at runtime, construct `CalibrationSignal`, build `TrustReport` or `DecisionSurface`, generate recommendations, or enable real data.

## Live prerequisite evidence

Connected GitHub established before authorization:

- MIP `main`: `f8fb482e51697f004d3fa2a6b229f6729d423cef`.
- GeoX `main`: `e9b7d311ecaf5a90e227d8299f745a0e8f332368`; no executable GeoX task is active.
- GeoX canonical producer contract: `panel_exp/contracts/geox_governed_experiment_readout.py`.
- GeoX certified governed-readout fixtures exist under `tests/fixtures/geox_governed_readouts/`; source checkpoint includes `860182386c39f487747de5f43e67a31e9978e57c` and current live main is authoritative.
- MMM `main`: `f2e0eade0ad917c1b28ab5521e6d35a35047d988`; its current thin-launcher proposal is non-executable and does not overlap this task.
- MMM canonical compatibility contract: `mmm/contracts/calibration_compatibility.py` with schema `mmm_calibration_compatibility_result_v1` and terminal states `compatible`, `compatible_with_warning`, `stale`, `incompatible`, and `blocked`.
- MMM producer fixtures exist under `tests/fixtures/mip_export/calibration_compatibility_v1/`; live MMM `main` is authoritative for their exact paths and content.
- Existing MIP method-promotion handoff, GeoX envelope consumer, calibration-readiness metadata, MMM runtime-ingestion, governance-routing, planning-answer, and LLM-response-boundary chains are already merged. Do not duplicate them.
- MIP P2 design is `docs/roadmap/MIP_P2_CONSUMER_CONTRACT_AND_FIXTURE_JOURNEY_DESIGN_001.md`.

Before implementation, re-fetch all three repositories and fail closed if these mains, contracts, fixture locations, task ownership, or terminal-state vocabularies have changed materially.

## Exact observable behavior

### 1. MIP-owned consumer views

Add a focused MIP contract module defining:

- `GeoXReadoutConsumerView`
- `MMMCompatibilityConsumerView`
- `P2CompatibilityBridgeStatus`
- `P2CompatibilityBridgeResult`

The views are MIP consumer projections, not copies of full producer models. They must preserve producer values and expose only fields needed for routing, lineage, explanation, and the next P2 checkpoint.

`GeoXReadoutConsumerView` must preserve at minimum:

- readout, experiment, artifact, schema/readout, package, and producer-commit identity;
- KPI, units, estimand, effect scale, channel/tactic, geography, grain, and time scope;
- method family, instrument identity, method status, readout/feasibility/freshness status;
- effect and uncertainty fields exactly as supplied, including unavailable values;
- handoff eligibility, warnings, blockers/failures, provenance, lineage, replay metadata;
- all producer authorization flags verbatim.

`MMMCompatibilityConsumerView` must preserve at minimum:

- compatibility-result and schema identity;
- linked normalized source-readout identity and version;
- model/run/configuration/panel/evaluation lineage;
- KPI/unit/estimand/effect-scale/channel/geography/grain identities;
- overlap, freshness, uncertainty, and final compatibility decisions;
- reason codes, warnings, blockers, canonical evaluated-rule order;
- producer package/commit references when available.

### 2. Strict parsing and version behavior

Implement strict parsers/builders for both consumer views.

- Accept only explicitly supported schema/artifact versions recorded in the committed fixture manifest.
- Reject unknown or missing versions; do not guess or silently coerce them.
- Preserve null/unavailable uncertainty and effect fields.
- Reject unknown producer terminal states.
- Reject any producer payload that sets a decision, recommendation, TrustReport, calibration-signal, assignment, optimization, LLM, or similar authorization flag to true.
- Producer parse failures must become typed MIP bridge failures; do not expose stack traces or silently drop fields.

### 3. Cross-producer identity and lineage reconciliation

Implement `resolve_p2_geox_mmm_compatibility(...)` or an equivalently named pure deterministic function.

It must verify, at minimum:

- MMM `source_readout_id` equals the GeoX `readout_id`;
- MMM `source_readout_version` is compatible with the GeoX readout/artifact version recorded in the manifest;
- MMM lineage `evidence_artifact_id` refers to the consumed GeoX artifact/readout identity;
- KPI, unit, estimand, effect scale, channel, geography, and grain identities agree between the two producer artifacts;
- the fixture manifest pins exact GeoX and MMM repository SHAs and source paths;
- no conflicting/superseded artifact pair is treated as successful.

MIP must not run the MMM evaluator or derive a replacement compatibility state. The MMM result is authoritative when the identity/lineage pair is valid.

### 4. Terminal bridge states

The bridge must emit deterministic states covering at least:

- `evidence_ready`
- `evidence_ready_with_warning`
- `stale_evidence`
- `incompatible_evidence`
- `blocked_evidence`
- `producer_failure`
- `diagnostic_only`
- `research_only`
- `conflicting_or_superseded_evidence`
- `unsupported_producer_version`

Required precedence:

1. parse/version/identity conflicts fail closed;
2. GeoX failed or blocked/ineligible handoff cannot become ready because MMM says compatible;
3. GeoX diagnostic-only or research-only status remains non-planning evidence;
4. for an otherwise eligible pair, preserve MMM `compatible`, `compatible_with_warning`, `stale`, `incompatible`, or `blocked` exactly;
5. warnings, blockers, limitations, and producer states remain attached and are never softened.

The result must include `human_review_required: true` for ready and warning outcomes and must expose explicit permitted/prohibited claims. It must not contain a recommendation, approval, simulation result, full-panel delta-mu, ROI/ROAS, budget allocation, or treatment assignment.

### 5. Certified fixture snapshots

Commit a bounded MIP-owned fixture set under:

`tests/fixtures/p2/geox_mmm_compatibility_bridge_v1/`

Include:

- one manifest with exact MIP, GeoX, and MMM pins, source paths, schema versions, fixture identities, checksums when practical, and non-production labels;
- paired producer snapshots for the required terminal cases;
- expected MIP bridge result for each pair.

Every producer snapshot must be copied verbatim from an existing certified sibling fixture or generated solely by invoking the sibling producer parser/serializer at the exact pinned main. Do not invent analytical values or hand-edit producer numerical truth. Record the source path and SHA for every snapshot.

Minimum cases:

1. eligible GeoX + MMM compatible;
2. eligible GeoX + compatible with warning;
3. stale compatibility;
4. incompatible compatibility;
5. GeoX blocked/ineligible handoff;
6. producer failure;
7. diagnostic-only method/readout;
8. research-only method/readout;
9. identity/lineage conflict;
10. unsupported version.

If an exact sibling fixture does not exist for a required case, stop and publish `blocked` with the missing producer evidence and a concrete owner-repository resolution condition. Do not synthesize new producer truth in MIP.

### 6. Public package surface

Export the new MIP contracts and resolver through the narrowest existing package surface. Do not modify existing method-promotion, GeoX-envelope, MMM-runtime, planning-answer, or LLM boundary behavior beyond additive imports required for the new module.

## Owned paths

Implementation may modify only:

1. `src/mip/contracts/p2_geox_mmm_compatibility_bridge.py`
2. `src/mip/workflows/p2_geox_mmm_compatibility_bridge.py`
3. `src/mip/contracts/__init__.py`
4. `src/mip/workflows/__init__.py` only if the repository already uses it for public workflow exports
5. `tests/contracts/test_p2_geox_mmm_compatibility_bridge.py`
6. `tests/fixtures/p2/geox_mmm_compatibility_bridge_v1/**`
7. `docs/integrations/MIP_P2_GEOX_MMM_COMPATIBILITY_FIXTURE_BRIDGE_001.md`
8. `docs/integrations/archives/MIP_P2_GEOX_MMM_COMPATIBILITY_FIXTURE_BRIDGE_001_summary.json`
9. `docs/execution/ACTIVE_TASK.md`
10. `docs/execution/EXECUTION_STATE.json`
11. `docs/execution/LATEST_COMPLETION_REPORT.md`

If `src/mip/workflows/__init__.py` is absent or not an export surface, do not create or modify it.

## Prohibited scope

Do not modify MMM or GeoX repositories. Do not modify existing producer fixture content. Do not:

- import sibling package classes into the persistent MIP runtime contract;
- evaluate MMM compatibility inside MIP;
- construct or apply `CalibrationSignal`;
- fit, refresh, load, or mutate an MMM model;
- run MMM simulation or optimization;
- construct `DecisionSurface`, `TrustReport`, `RecommendationContract`, or planning recommendation;
- calculate lift, uncertainty, delta-mu, ROI/ROAS, spend movement, or assignment;
- modify LLM, UI, app, orchestration router, persistence, security, deployment, roadmap, or coordination files;
- create a PR, merge, squash, rebase, force-push, or merge commit.

## Named acceptance evidence

The focused test file must separately verify:

1. strict GeoX projection and exact field preservation;
2. strict MMM projection and exact terminal-state preservation;
3. version rejection and safe typed failures;
4. identity/lineage reconciliation across producers;
5. terminal-state precedence for all minimum cases;
6. diagnostic/research evidence cannot become planning-ready;
7. authorization flags and prohibited output fields remain false/absent;
8. fixture manifest pins and source-path provenance;
9. deterministic replay and JSON round trips;
10. no existing method-promotion, envelope-consumer, runtime-ingestion, or planning-answer behavior is changed.

Tests must compare actual fixture outputs, not only search documentation text.

## Validation gate

This Tier-3 task requires on the final frozen task-owned tree:

- parse all changed JSON files;
- `git diff --check`;
- exact owned-path verification;
- focused pytest for `tests/contracts/test_p2_geox_mmm_compatibility_bridge.py` with exact count;
- existing directly adjacent consumer-contract tests for method-promotion handoff and GeoX envelope consumption;
- Ruff on all changed Python files;
- configured mypy on all changed MIP Python files;
- Docker-backed `make validate` with exact pass/fail counts;
- deterministic fixture replay twice with byte-identical normalized outputs;
- exact-tree publication receipt;
- clean worktree except permitted local-only paths;
- local/remote feature-branch equality after push.

Focused success does not hide full-suite debt. If Docker/full validation cannot complete, publish a truthful `blocked` state with diagnostics and a live resolution condition.

## Task-authoring and authorization boundary

- Pre-authoring base: `f8fb482e51697f004d3fa2a6b229f6729d423cef`.
- The task-authoring range may change only `docs/execution/ACTIVE_TASK.md` and `docs/execution/LATEST_COMPLETION_REPORT.md`.
- The final authoring commit is recorded as `authorization_head_sha` by the immediate next state-only commit.
- The immediate next commit may change only `docs/execution/EXECUTION_STATE.json` and authorizes the exact feature branch.
- Create the feature branch from the resulting synchronized state-only main head.

## Publication contract

On success publish one exact remote `ready_for_review` head containing:

- one implementation SHA and one exact-tree publication receipt;
- exact producer pins and copied/generated fixture provenance;
- exact changed paths;
- focused and adjacent test counts;
- Ruff, mypy, JSON, diff-check, deterministic replay, and Docker `make validate` results;
- GitHub-observed evidence separated from locally reported validation;
- limitations, validation debt, sibling impact, and consumer-verification status;
- empty blockers;
- task execution true, correction execution false, merge and PR authority false;
- no capability-authority change;
- exact local/remote branch-head equality.

A genuine missing producer fixture, incompatible live producer contract, external Git/authentication/filesystem obstruction, or required-validation failure may publish Git-durable `blocked` with exact diagnostics and a live resolution condition. Task-owned implementation or focused-test failures are unfinished work and must be corrected within scope.

## Next checkpoint after successful merge

`MIP_P2_MMM_PUBLIC_SIMULATION_AND_PLANNING_EVIDENCE_FIXTURE_JOURNEY_001` may be considered only after this bridge is externally reviewed, merged, and closed. It is not authorized here.

**Unresolved execution-blocking design questions: none.**

## Blocked execution result

- **Status:** `blocked`
- **Blocker:** `BLOCK-P2-GEOX-MMM-CERTIFIED-PAIR-PROVENANCE-001`
- **Resolution condition:** GeoX and MMM owners must publish a certified,
  provenance-linked governed-readout and calibration-compatibility fixture pair
  at exact merged producer pins, including matching readout and evidence lineage
  identities and the required terminal cases.
- **Authority impact:** unchanged; no MIP bridge implementation occurred.
