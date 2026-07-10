# MMM Model Artifact and Existing Model Availability Audit 001

**Artifact ID:** `MIP_MMM_MODEL_ARTIFACT_AND_EXISTING_MODEL_AVAILABILITY_AUDIT_001`  
**Type:** audit / governance checkpoint only  
**Repo checkpoint:** `a5074ad` (includes `70968b3` tabular source reuse completion audit)  
**Status:** completed  
**Scope:** audit-only — no production code changes

---

## 1. Purpose

Determine whether MIP can already answer:

> Given a user planning question, can MIP find an existing MMM model artifact that is fresh, promoted, scope-matching, metric-matching, channel-compatible, diagnostics-passed, and authorized for the intended use — or determine that a new model run is required?

This audit inspects contracts, registries, gates, and workflow layers only. It does not implement new functionality.

---

## 2. Scope

**In scope:** contracts, evidence registry, evaluation gates, trust/decision/recommendation paths, MMM config/adapter placeholders, workflow readiness, Planning/MMM uploaded CSV and tabular intake lanes.

**Out of scope:** implementing model registries, model execution, optimizers, LLM behavior changes.

---

## 3. Audit questions answered

### 3.1 Do we already have an MMM model artifact contract?

**Partially, not as a first-class MMM model artifact.**

| Artifact | Location | What it covers |
|----------|----------|----------------|
| `DecisionSurface` | `mip.contracts.decision_surface` | `model_id`, `surface_type`, `certification_status`, `artifact_fingerprint`, `decision_estimand`, diagnostics via gates |
| `MMMAdapterOutputPlaceholder` | `mip.adapters.mmm` | Placeholder only; explicitly not model execution |
| `MMMConfigDraft` | `mip.workflows.configs.mmm` | Draft config fields (outcome/spend/date/channel/geo), not a fitted model artifact |
| `WorkflowArtifactRef` | `mip.orchestration.manifest` | Generic manifest ref (`artifact_type`, `artifact_id`, `uri`) |
| `ArtifactReference` | `mip.contracts.deterministic_report` | Report linkage, not MMM model registry |

There is **no** `MMMModelArtifact`, `ModelArtifact`, or equivalent contract storing training window, channel coverage, promotion record, and artifact URI for a fitted MMM.

### 3.2 Do we already have a model registry or artifact registry?

| Registry | Location | Stores MMM model artifacts? |
|----------|----------|----------------------------|
| `EvidenceRegistry` | `mip.evidence.registry` | **No** — `ExperimentEvidence`, `CalibrationSignal` only |
| Model registry | — | **Not implemented** |
| `WorkflowRunManifest.artifact_refs` | `mip.orchestration.manifest` | Run-scoped refs including `mmm_fixture_report`; not a searchable model catalog |

`EvidenceRegistry.find_evidence()` and `find_calibration_signals()` support experiment/calibration lookup by metric, scope, freshness, status — **not** MMM model artifact lookup.

### 3.3 Do we already track model artifact metadata?

| Metadata dimension | Supported for MMM model artifact? | Where (if anywhere) |
|--------------------|-----------------------------------|---------------------|
| Model type | No dedicated field | `DecisionSurface.surface_type`, `AdapterRunKind.MMM` |
| Region / geo scope | Partial on evidence | `Estimand.scope`, `find_evidence(scope_contains=...)` |
| Product / business unit | No on model artifact | Intake profiling only |
| Channels included | No on model artifact | `MMMConfigDraft.channel_field`, calibration `channel_mapping` |
| KPI / metric modeled | Partial | `Estimand.target_metric`, evidence `target_metric` filter |
| Training time window | No on model artifact | `Estimand.time_window` on surfaces/evidence |
| Data freshness | Partial | `ExperimentEvidence.freshness_score`, `CalibrationSignal.freshness_decay` |
| Calibration signals used | Partial | `ModelCalibrationReadiness`, `evaluate_model_calibration_readiness()` |
| Diagnostic status | Partial | `DiagnosticSummary`, gate `check_decision_surface_gate`, `check_experiment_evidence_gate` |
| Promotion status | Partial | `ArtifactStatus` on evidence/surfaces; `RELEASE_GATES.md` documents MMM promotion policy |
| Allowed downstream uses | Partial | `CalibrationSignal.allowed_usage` / `blocked_usage`; not on `DecisionSurface` |
| Artifact URI | Partial | `ExperimentEvidence.artifact_uri`; `DecisionSurface.artifact_fingerprint` (not URI) |

Metadata exists across **governance artifacts**, not as a unified **MMM model artifact record**.

### 3.4 Do we already have a gate that answers whether an existing model can be used for a user request?

**No end-to-end gate.**

Existing per-artifact gates (`mip.evaluation.gates`):

- `check_decision_surface_gate()` — if you already have a `DecisionSurface`, checks certification, surface type, reliability scorecard for budget planning
- `check_calibration_signal_gate()` — calibration signal eligibility
- `check_experiment_evidence_gate()` — experiment evidence eligibility
- `check_recommendation_gate()` — recommendation eligibility

`evaluate_model_calibration_readiness()` audits calibration signals for a **known** `target_model_id`.

**Missing:** a function that, given a planning question / scope / metric / channels / intended use, searches registered MMM models and returns usable vs requires-new-run.

### 3.5 Do we already have statuses for model reuse decisions?

**Not as a dedicated existing-model availability enum.**

Related statuses exist in other layers:

| Desired status | Closest existing | Gap |
|----------------|------------------|-----|
| Usable existing model | `GateDecision.PASS`, `WorkflowReadinessStatus.READY` | No model selection |
| Stale model | `R.LOW_FRESHNESS_SCORE`, calibration stale mapping | Not tied to MMM model artifact |
| Diagnostics failed | `R.DIAGNOSTICS_FAILED` | Per-artifact, not selection |
| Not promoted | `R.NOT_VALIDATED_OR_CERTIFIED`, `ArtifactStatus.DRAFT` | No model promotion registry |
| Scope mismatch | `ReadinessBlockingReason.SCOPE_MISMATCH` | Data readiness, not model reuse |
| Metric mismatch | Evidence metric filter mismatch | No model-level matcher |
| Channel mismatch | Not implemented | — |
| Use not allowed | `CalibrationSignal.blocked_usage` | Not on MMM model |
| Requires new model run | Not implemented | — |

### 3.6 Do TrustReport / DecisionSurface / RecommendationContract / EvidenceRegistry cover this?

| Component | Coverage | Notes |
|-----------|----------|-------|
| `EvidenceRegistry` | **Partial** | Experiment + calibration registry/search; no MMM model store |
| `TrustReport` | **Partial** | Built per known artifact via `build_trust_report_for_artifact()`; no discovery |
| `DecisionSurface` | **Partial** | Model surface contract + gates; placeholder mapping from adapter fixtures only |
| `RecommendationContract` | **Partial** | Requires `decision_surface_ids`; assumes surfaces already chosen |

Together they govern **known** artifacts. They do **not** implement **existing model discovery and eligibility** for a planning question.

### 3.7 What is missing before the LLM can safely decide use existing / refresh / new run / block?

1. **MMM model artifact contract** with scope, metric, channels, training window, freshness, promotion, diagnostics, allowed uses, artifact URI
2. **MMM model registry** (or extension of a governed registry) with `find_mmm_models(...)` semantics
3. **Existing model availability gate** returning structured statuses (usable, stale, scope mismatch, requires new run, etc.)
4. **Linkage** from Planning/MMM data readiness + calibration intake to model candidates (today `ModelCalibrationReadiness` is deferred in uploaded CSV workflow readiness)
5. **LLM-safe orchestration contract** exposing gate outcomes without bypassing TrustReport / DecisionSurface / RecommendationContract

Planning/MMM tabular lanes (`adapt_tabular_sources_for_planning_mmm`, workflow readiness, readiness report adapter, calibration signal tabular intake) address **input data readiness only**, not fitted model reuse.

---

## 4. Evidence table

| File / symbol | Role |
|---------------|------|
| `mip.contracts.decision_surface.DecisionSurface` | Closest model-surface contract (`model_id`, `certification_status`) |
| `mip.contracts.evidence.ExperimentEvidence` | Experiment artifact with freshness, diagnostics, `artifact_uri` |
| `mip.contracts.calibration.CalibrationSignal` | Model-targeted calibration with `target_model_id`, `allowed_usage` |
| `mip.evidence.registry.EvidenceRegistry` | In-memory evidence + calibration registry with `find_*` |
| `mip.evidence.model_readiness.ModelCalibrationReadiness` | Calibration readiness for known `target_model_id` |
| `mip.evaluation.gates` | Per-artifact gates (`check_decision_surface_gate`, etc.) |
| `mip.contracts.workflow_readiness.MMMDataReadinessReport` | Structural **data** readiness, not model reuse |
| `mip.workflows.planning_mmm_readiness_report_adapter` | Metadata bridge to `MMMDataReadinessReport` semantics |
| `mip.adapters.mmm` | Config draft → adapter placeholder; no model registry |
| `mip.adapters.governance.adapter_output_to_decision_surface` | Fixture placeholder → `DecisionSurface` |
| `mip.reports.mmm_fixture` | Demo fixture report; explicitly not model execution |
| `mip.orchestration.manifest.WorkflowArtifactRef` | Run manifest artifact refs |
| `docs/operating_model/RELEASE_GATES.md` | Normative MMM promotion policy (not fully implemented as registry) |

---

## 5. Regression / related lanes (unchanged by this audit)

Planning/MMM uploaded CSV, tabular source adapters, workflow readiness, readiness report adapter, and calibration signal tabular intake remain **data-intake and readiness** layers. They do not answer existing fitted-model availability.

---

## 6. Final audit verdict

**MISSING_NEEDS_NEW_EXISTING_MODEL_AVAILABILITY_GATE** *(at audit time; addressed by `MIP_MMM_EXISTING_MODEL_AVAILABILITY_GATE_001`)*

MIP had strong **per-artifact governance** (evidence registry, calibration readiness, decision-surface gates, trust reports) and **data-readiness** bridges for Planning/MMM inputs. It did **not** have a searchable MMM model artifact catalog or a gate that selects an existing model vs requires a new model run for a user planning question.

**Follow-up (implemented):** `mip.contracts.mmm_existing_model_availability` and `mip.workflows.mmm_existing_model_availability` add a metadata-only existing-model availability gate with `MMMModelArtifact`, `MMMModelArtifactQuery`, and structured statuses (`USABLE_EXISTING_MODEL`, `REQUIRES_MODEL_REFRESH`, `REQUIRES_NEW_MODEL_RUN`, etc.). No model execution, artifact loading, or TrustReport/DecisionSurface construction.

---

## 7. Recommended next artifact

**`MIP_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AND_READINESS_001`**

Map calibration intake into readiness metadata and align signals with model/use requirements before model-run eligibility.

**Alternative:** `MIP_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_001`

Do **not** recommend Databricks/warehouse/API connectors for this gap.

---

## 8. Audit deliverable scope statement

This artifact added:

- `docs/audits/MIP_MMM_MODEL_ARTIFACT_AND_EXISTING_MODEL_AVAILABILITY_AUDIT_001.md` (this document)
- `docs/audits/archives/MIP_MMM_MODEL_ARTIFACT_AND_EXISTING_MODEL_AVAILABILITY_AUDIT_001_summary.json`
- `tests/governance/test_mmm_model_artifact_existing_model_availability_audit_001.py`

This artifact did not add or modify production code under `src/mip/`.
