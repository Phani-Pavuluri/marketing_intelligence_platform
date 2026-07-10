# MMM Runtime Adapter Contract Audit 001

**Artifact ID:** `MIP_MMM_RUNTIME_ADAPTER_CONTRACT_AUDIT_001`  
**Type:** audit / governance checkpoint only  
**Repo checkpoint:** `ee1ccc8` (includes Planning MMM trusted input and model run eligibility)  
**Status:** completed  
**Scope:** audit-only — no production code changes

---

## 1. Purpose

Determine whether MIP already has MMM runtime request/response contracts, run manifests, adapter placeholders, governance mappings, or fixture contracts that should be **reused** before implementing `MIP_MMM_RUNTIME_ADAPTER_CONTRACT_001`.

This audit inspects contracts, workflows, adapters, reports, orchestration, and integration docs only. It does not implement new functionality.

---

## 2. Audit questions answered

### 2.1 Do we already have MMM runtime request contracts?

**No.**

| Artifact | Location | Role |
|----------|----------|------|
| `GeoXPanelExpRuntimeCallRequest` | `mip.contracts.geox_panel_exp_runtime_call` | GeoX external runtime request (reference pattern only) |
| `PlanningMMMModelRunEligibilityRequest` | `mip.contracts.planning_mmm_trusted_input_model_run_eligibility` | Upstream eligibility gate input — not a runtime call envelope |
| `MMMAdapterInput` / `AdapterInputBundle` | `mip.adapters.mmm`, `mip.adapters.base` | Config-draft adapter input — not external runtime request |
| `MMMExistingModelAvailabilityRequest` | `mip.contracts.mmm_existing_model_availability` | Existing-model selection query — not runtime invocation |

There is **no** `MMMRuntimeCallRequest`, `MMMRuntimeAdapterRequest`, or equivalent contract describing a metadata-safe handoff to an external MMM engine for new run, refresh, or reuse execution.

### 2.2 Do we already have MMM runtime response contracts?

**No.**

| Artifact | Location | Role |
|----------|----------|------|
| `GeoXPanelExpRuntimeCallResult` | `mip.contracts.geox_panel_exp_runtime_call` | GeoX runtime response envelope (reference pattern) |
| `MMMAdapterOutputPlaceholder` | `mip.adapters.mmm` | Fixture placeholder only — explicitly not model execution |
| `PlanningMMMModelRunEligibilityResult` | `mip.contracts.planning_mmm_trusted_input_model_run_eligibility` | Eligibility decision — not runtime execution outcome |
| `MMMExistingModelAvailabilityResult` | `mip.contracts.mmm_existing_model_availability` | Model reuse decision — not runtime response |

No contract captures `runtime_called`, external run status, produced artifact locations, runtime diagnostics references, or structured failure packets for an MMM engine invocation.

### 2.3 Do we already have MMM run manifests or execution manifests?

**Partially — generic workflow manifests only; no MMM runtime execution manifest.**

| Artifact | Location | MMM runtime manifest? |
|----------|----------|----------------------|
| `WorkflowRunManifest` | `mip.orchestration.manifest` | Generic workflow steps and `WorkflowArtifactRef` — includes `mmm_fixture_report` refs, not external runtime execution |
| `build_manifest_with_mmm_fixture` | `mip.orchestration.plans` | Adds fixture report artifact refs to workflow manifest |
| `AgentRunManifest` | `mip.contracts.agentic_workflow` | Agentic orchestration — not MMM runtime |
| Intake manifest compatibility | `mip.workflows.planning_mmm_uploaded_csv_adapter` | `build_intake_manifest_compatibility_from_uploaded_csv_adapter_result` — metadata compatibility only; full manifest construction **deferred** |

There is **no** MMM-specific run manifest contract analogous to a runtime execution record with external system ID, run type, and artifact handoff slots.

### 2.4 Do we already have adapter placeholders in `mip.adapters.mmm`?

**Yes.**

`src/mip/adapters/mmm.py` provides:

- `MMMAdapterInput` — governed input from `MMMConfigDraft`
- `MMMAdapterOutputPlaceholder` — placeholder output metadata (`artifact_type: mmm_adapter_placeholder`)
- `build_mmm_adapter_input()` — builds `AdapterInputBundle` with `AdapterRunKind.MMM`
- `build_mmm_adapter_output_placeholder()` — builds completed placeholder `AdapterOutputBundle`

These are **fixture/demo placeholders**, not live runtime bridge contracts. They explicitly state no model execution.

### 2.5 Do we already have MMM fixture/report placeholders?

**Yes.**

| Component | Location | Role |
|-----------|----------|------|
| `MMMFixtureReport` | `mip.reports.mmm_fixture` | Governed fixture report bundle for dashboard rendering |
| `build_mmm_fixture_report()` | `mip.reports.mmm_fixture` | Builds report from `WorkflowRunSummary` + config draft |
| `orchestrate_mmm_fixture_engine` | `mip.orchestration.engine_fixtures` | Fixture engine orchestration |
| `planner_route_with_mmm_fixture` | `mip.orchestration.router` | Routes manifests containing `mmm_fixture_report` |
| Sibling export producer spec | `docs/integrations/MMM_MIP_EXPORT_PRODUCER_SPEC.md` | Static JSON export handoff — no live execution |

### 2.6 Do governance adapters map MMM placeholders to DecisionSurface, TrustReport, or other governed artifacts?

**Yes — for placeholder outputs only.**

`src/mip/adapters/governance.py`:

- `adapter_output_to_decision_surface()` — maps completed `AdapterRunKind.MMM` placeholder to `DecisionSurface` (`DIAGNOSTIC_CURVE`, `DRAFT` certification)
- `trust_report_for_adapter_output()` — builds `TrustReport` via existing gate paths
- `register_adapter_output()` — MMM surfaces registered with `registered_in_registry=False`
- `adapter_lineage_assumptions()` — preserves adapter lineage metadata

`src/mip/reports/mmm_fixture.py` consumes these mappings for fixture demo reports. This path does **not** represent post-runtime MMM engine output ingestion.

### 2.7 Do existing contracts already represent required runtime handoff fields?

| Field | Supported? | Evidence |
|-------|----------|----------|
| Trusted input package reference | **Yes** | `PlanningMMMTrustedInputPackage` in `planning_mmm_trusted_input_model_run_eligibility` |
| Model-run eligibility decision | **Yes** | `PlanningMMMModelRunEligibilityDecision`, `PlanningMMMModelRunEligibilityResult` |
| Requested run type (new vs refresh vs reuse) | **Partial** | Eligibility result flags (`use_existing_model`, `requires_model_refresh`, `requires_new_model_run`) — no runtime request `run_type` field |
| Model config reference | **Partial** | `model_config_id`, `model_config_present` on eligibility request/package; `MMMConfigDraft` in `mip.workflows.configs.mmm` |
| Calibration readiness reference | **Yes** | `calibration_readiness_result` on eligibility request; status/request_id on trusted input package |
| Existing model availability reference | **Yes** | `existing_model_availability_result` on eligibility request; `existing_model_selected_id` on package |
| Runtime request ID | **No** | Generic `request_id` on eligibility — no dedicated MMM runtime call request ID |
| External runtime/system ID | **No** | GeoX has `GeoXPanelExpRuntimeReference`; MMM has no equivalent |
| Run status | **No** | `AdapterRunStatus` covers adapter bundles; no `MMMRuntimeCallStatus` |
| Artifact locations | **Partial** | `MMMModelArtifact.artifact_uri` on artifact metadata; no runtime response artifact envelope |
| Diagnostics references | **Partial** | `MMMModelDiagnosticStatus` on `MMMModelArtifact`; no runtime diagnostics reference contract |
| Failure packets/errors | **No** | Eligibility `blocked_reasons` and adapter `reason` exist; no structured MMM runtime failure packet |
| Lineage/provenance | **Yes** | `lineage` dicts on eligibility, existing model availability, adapter governance assumptions |

### 2.8 What is missing before MIP can safely request an external MMM runtime run?

1. **MMM runtime adapter request contract** — metadata-safe envelope referencing trusted input package, eligibility decision, run type (reuse / refresh / new), model config, and external runtime reference
2. **MMM runtime adapter response contract** — run status, `runtime_called` consistency, artifact location references, diagnostics references, structured warnings/issues, failure packet
3. **MMM external runtime reference** — analogous to `GeoXPanelExpRuntimeReference` (system/module/callable metadata without importing sibling code)
4. **Runtime call workflow** — metadata-only orchestration entry (like `call_geox_post_test_spend_runtime_for_fixture`) that does **not** execute MMM inside MIP by default
5. **Bridge from eligibility → runtime request** — consume `PlanningMMMModelRunEligibilityResult` when `eligible_to_request_model_run` or refresh/reuse paths apply
6. **MMM runtime run manifest / handoff record** — optional but useful for orchestration audit trail distinct from generic `WorkflowRunManifest` fixture steps
7. **Post-runtime artifact ingestion contract** (future) — separate from this artifact; not present today

Upstream readiness is largely complete (`ee1ccc8`); the **runtime boundary envelope** is the gap.

### 2.9 Recommended next step

**Verdict: `PARTIALLY_COVERED_NEEDS_THIN_ADAPTER`**

Existing functionality is **not** sufficient to request an external MMM runtime run end-to-end. However, substantial reusable layers exist:

- Adapter placeholders (`mip.adapters.mmm`, `mip.adapters.base`)
- Governance mapping (`mip.adapters.governance`)
- Fixture/report path (`mip.reports.mmm_fixture`, orchestration plans/router)
- Upstream gates (`planning_mmm_trusted_input_model_run_eligibility`, `mmm_existing_model_availability`, calibration mapping readiness)
- GeoX runtime call pattern (`geox_panel_exp_runtime_call`, `geox_uploaded_csv_runtime_bridge`) as structural reference
- Sibling static export spec (`docs/integrations/MMM_MIP_EXPORT_PRODUCER_SPEC.md`) for file-based handoff

The next artifact should be a **thin new runtime adapter contract + metadata-only workflow** that wraps these existing pieces — not a rewrite of eligibility or adapter placeholders.

**Recommended next artifact:** `MIP_MMM_RUNTIME_ADAPTER_CONTRACT_001`

---

## 3. Relevant existing files (evidence index)

### Contracts

- `src/mip/contracts/planning_mmm_trusted_input_model_run_eligibility.py` — trusted input package + model-run eligibility
- `src/mip/contracts/mmm_existing_model_availability.py` — `MMMModelArtifact`, availability gate
- `src/mip/contracts/planning_mmm_calibration_signal_mapping_readiness.py` — calibration readiness metadata
- `src/mip/contracts/planning_mmm_readiness_report_adapter.py` — data readiness bridge
- `src/mip/contracts/geox_panel_exp_runtime_call.py` — **reference runtime call pattern (GeoX)**
- `src/mip/orchestration/manifest.py` — generic `WorkflowRunManifest`

### Workflows

- `src/mip/workflows/planning_mmm_trusted_input_model_run_eligibility.py` — `evaluate_planning_mmm_trusted_input_and_model_run_eligibility`
- `src/mip/workflows/mmm_existing_model_availability.py` — `evaluate_mmm_existing_model_availability`
- `src/mip/workflows/geox_panel_exp_runtime_call.py` — **reference runtime workflow (GeoX)**

### Adapters / reports / governance

- `src/mip/adapters/mmm.py` — MMM adapter input/output placeholders
- `src/mip/adapters/base.py` — `AdapterInputBundle`, `AdapterOutputBundle`, `AdapterRunStatus`
- `src/mip/adapters/governance.py` — placeholder → `DecisionSurface` / `TrustReport`
- `src/mip/reports/mmm_fixture.py` — fixture report placeholders

### Tests

- `tests/workflows/test_planning_mmm_trusted_input_model_run_eligibility.py`
- `tests/workflows/test_mmm_existing_model_availability.py`
- `tests/adapters/test_mmm.py`
- `tests/reports/test_mmm_fixture.py`

### Docs / integration

- `docs/integrations/MMM_MIP_EXPORT_PRODUCER_SPEC.md` — static sibling export handoff
- `docs/contracts/archives/MIP_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_001_summary.json`

---

## 4. Answer to key question

**Can MIP currently create a metadata-safe request/response contract for an external MMM runtime run?**

**Partially.** MIP has complete upstream metadata (trusted input, eligibility, calibration, existing model availability, adapter placeholders, governance mappings) and a proven GeoX runtime-call pattern to follow. It does **not** yet have the MMM-specific runtime request/response contracts or workflow boundary needed to safely hand off to an external engine.

---

## 5. Boundaries respected

This audit did not add or modify production code under `src/mip/`. No MMM execution, model fitting, artifact loading, optimizer, simulator, recommendation generation, DecisionSurface execution, TrustReport construction, or claim authorization was introduced.

---

## 6. Coverage assessment

| Assessment | Value |
|------------|-------|
| Existing functionality full enough? | **No** — runtime envelope missing |
| Existing functionality partial? | **Yes** — placeholders, governance, eligibility, GeoX pattern reusable |
| Recommended approach | Thin runtime adapter contract on top of existing layers |
| Verdict | `PARTIALLY_COVERED_NEEDS_THIN_ADAPTER` |
| Next artifact | `MIP_MMM_RUNTIME_ADAPTER_CONTRACT_001` |
