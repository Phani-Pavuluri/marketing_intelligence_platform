# TASK_AUTHORIZATION_REPORT

## Current decision

- **Current decision:** `authorized`
- **Task ID:** `MIP_P2_GEOX_MMM_COMPATIBILITY_FIXTURE_BRIDGE_001`
- **Repository:** `Phani-Pavuluri/marketing_intelligence_platform`
- **Pre-authoring base:** `f8fb482e51697f004d3fa2a6b229f6729d423cef`
- **Feature branch:** `feat/mip-p2-geox-mmm-compatibility-fixture-bridge-001`
- **Risk tier:** Tier 3 cross-repository producer-contract and certified-fixture integration
- **Implementation SHA:** not yet created
- **Capability authority:** unchanged

## Orientation and eligibility evidence

Live GitHub orientation verified:

- MIP `main` at `f8fb482e51697f004d3fa2a6b229f6729d423cef` before authoring; the prior thin-launcher task is superseded without merge and has no remaining authority.
- GeoX `main` at `e9b7d311ecaf5a90e227d8299f745a0e8f332368`; no GeoX execution task is authorized. GeoX owns governed-readout truth and has certified readout fixtures and a canonical `GeoXGovernedExperimentReadout` contract.
- MMM `main` at `f2e0eade0ad917c1b28ab5521e6d35a35047d988`; its current governance proposal is non-executable. MMM owns calibration compatibility through `MMMCalibrationCompatibilityResult` schema `mmm_calibration_compatibility_result_v1` and certified producer fixtures.
- MIP already contains the method-promotion consumer, GeoX envelope consumer, calibration-readiness metadata, MMM runtime-result ingestion, governance/use-readiness, planning-answer, and LLM-response-boundary chains. The originally named method-promotion consumer task is complete and was not duplicated.
- The canonical P2 design requires certified GeoX evidence followed by authoritative MMM compatibility before simulation and the MIP planning-evidence report.

No active or proposed executable work in MIP, MMM, or GeoX owns this exact MIP consumer-bridge surface.

## Authorized outcome

Implement a strict fixture-backed MIP bridge that consumes:

1. an exact certified GeoX governed-readout producer snapshot; and
2. its authoritative MMM calibration-compatibility producer snapshot;

then projects them into MIP-owned consumer views and resolves one deterministic bridge state without recomputing either producer's analytical decision.

The task covers strict versions, producer identity and lineage reconciliation, terminal-state preservation, non-authorization enforcement, deterministic fixture replay, and typed fail-closed outcomes.

It does not authorize package runtime calls, `CalibrationSignal` construction, MMM compatibility evaluation, simulation, optimization, `DecisionSurface`, `TrustReport`, recommendation, real data, pilot, or production.

## Fixture and consumer-verification boundary

Producer snapshots must be copied verbatim from certified sibling fixtures or generated only through producer parser/serializer code at the exact pinned sibling main. MIP may not invent or hand-edit analytical values.

The bridge must cover compatible, warning, stale, incompatible, blocked/ineligible, failure, diagnostic-only, research-only, identity-conflict, and unsupported-version cases. Missing certified producer evidence is a real blocker requiring owner-repository resolution; it is not permission for MIP to synthesize producer truth.

## Task-authoring boundary

The authoring range starts at `f8fb482e51697f004d3fa2a6b229f6729d423cef` and changes only:

- `docs/execution/ACTIVE_TASK.md`
- `docs/execution/LATEST_COMPLETION_REPORT.md`

The commit containing this report is the final task-authoring head. The immediate next commit must change only `docs/execution/EXECUTION_STATE.json`, record this exact authoring head as `authorization_head_sha`, and authorize the declared feature branch. The branch must be created from the resulting synchronized state-only main head.

## Validation requirement

The frozen task requires exact owned-path verification; JSON parsing; `git diff --check`; focused and adjacent consumer tests; Ruff; configured mypy; deterministic replay twice; Docker-backed `make validate`; an exact-tree publication receipt; clean worktree; and local/remote branch-head equality.

Focused-test success cannot hide Docker/full-suite validation debt. Required validation failure must produce a truthful Git-durable `blocked` state.

## Authority and non-actions

Task execution is authorized only after the immediate state-only authorization commit. Correction, merge, PR, sibling, analytical, release, real-data, live-engine, simulation, optimization, recommendation, assignment, pilot, production, and capability authority remain false.

The next simulation and `PlanningEvidenceReport` fixture journey remains a separate successor and is not authorized by this report.
