# MIP_SHARED_UPLOADED_DATA_AND_PLANNING_INPUT_AUDIT_001

## 1. Purpose

Audit existing MIP contracts and workflows around user-provided data, declared/uploaded dataset references, common intake, GeoX readout inputs, planning/MMM readiness, and governance surfaces (`TrustReport`, `DecisionSurface`, `RecommendationContract`).

**Goal:** Decide how to introduce a **shared uploaded-data/materialization core** that supports two downstream lanes without duplicating CSV parsing, inspection, or policy logic:

```text
Shared uploaded data/materialization core
  → GeoX readout input resolver
  → Planning/MMM input resolver
```

**This artifact is audit/documentation/test-only.** No shared materialization runtime, no lane-specific CSV parsers, no panel_exp changes, and no new upload API routes were added.

---

## 2. Current repository checkpoint

| Field | Value |
|-------|-------|
| **Base commit (main)** | `f3154cf` — Add GeoX readout trust routing |
| **Audit branch** | `audit/shared-uploaded-data-planning-input-audit-001` |
| **Date** | 2026-07-09 |

**GeoX readout path on main (implemented):**

```text
DatasetReference
  → inspect_geox_readout_sources()
  → enrich + resolve_geox_readout_inputs() / resolve_geox_readout_inputs_with_source_inspection()
  → GeoXReadoutInputHandoff
  → GeoXPostTestSpendAdapterInputPlan
  → materialize_geox_readout_fixtures()
  → call_geox_post_test_spend_runtime_for_fixture()
  → GeoXPostTestSpendEvidenceArtifact + GeoXTrustedReadoutSpendHandoffArtifact
  → ingest_geox_readout_result_for_explanation()
  → GeoXReadoutResultEnvelope
  → route_geox_readout_result_to_trust_boundaries()
  → GeoXReadoutTrustRoutingEnvelope
```

**Note:** An unmerged feature branch (`feature/mip-geox-uploaded-csv-materialization-001`) exists with GeoX-only uploaded CSV materialization. This audit recommends **not merging that approach as-is** because it duplicates fixture materialization and forecloses a shared core.

---

## 3. Existing user-provided data abstractions

### 3.1 Cross-lane declared data (no file I/O)

| Contract / module | Role | File I/O? |
|-------------------|------|-----------|
| `DataSourceRef` (`intake_sources.py`) | Declared source for intake assets: mode, type, URI, grain, status | No |
| `SourceIngestionRecord` (`common_intake.py`) | Ingestion metadata tied to common workbench | No |
| `DataSnapshot` (`common_intake.py`) | Snapshot record for declared data | No |
| `IntakeManifest` (`intake_sources.py`) | Manifest of required assets and source refs | No |
| `ColumnMappingProposal` (`intake_mapping.py`) | Semantic column mapping proposals | No |
| `DataAssetType` (`intake_assets.py`) | Asset categories (outcome KPI, media spend, calibration signal, etc.) | No |

**Upload modes declared but not executed in core workflows:** `IngestionMode.STREAMLIT_FILE_UPLOAD`, `CHAT_FILE_UPLOAD`, `LOCAL_FILE_PATH_MANIFEST`, `LOCAL_DROPZONE_FOLDER` (`common_intake.py`, `intake_sources.py`).

### 3.2 GeoX lane declared data

| Contract / module | Role | File I/O? |
|-------------------|------|-----------|
| `DatasetReference` (`geox_readout_input_resolution.py`) | Declared dataset ref with `source_type`, `semantic_type`, columns, lineage | No (Stage 2A) |
| `DatasetSourceType` | Includes `UPLOADED_CSV`, `REGISTERED_ARTIFACT`, warehouse/API types | Metadata only |
| `GeoXReadoutSourceInspection*` (`geox_readout_source_inspection.py`) | Header/column hints from **declared** columns | No |
| `GeoXMaterializedDataset` (`geox_fixture_materialization.py`) | In-memory materialized dataset wrapper | Yes — fixture path only |
| `GeoXFixtureMaterialization*` | Controlled local CSV read under allowed fixture roots | Yes — narrow |

### 3.3 Demo / Stage A paths (not production upload)

| Module | Role | File I/O? |
|--------|------|-----------|
| `demo_profiling.py` | Profiles in-memory row sequences into `DemoDatasetProfile` | No `read_csv` |
| `stage_a_fixtures.py` | Loads JSON/CSV from `examples/fixtures/stage_a/` | Yes — demo fixtures only |

### 3.4 Materialization reality on main

**Only one production-adjacent CSV reader exists today:**

- `mip/workflows/geox_fixture_materialization.py` — `pd.read_csv()` under `GeoXFixtureMaterializationPolicy` (allowed roots, extensions, max rows).

There is **no** shared uploaded-file reference contract, **no** shared CSV policy module, and **no** planning/MMM file materialization workflow on main.

---

## 4. Existing GeoX readout data/input lane

### 4.1 Contracts (reusable)

| Artifact | Location | Reuse for shared layer |
|----------|----------|------------------------|
| `DatasetReference` | `geox_readout_input_resolution.py` | **Partial** — lane-specific semantic types; shared layer should emit compatible refs |
| Source inspection | `geox_readout_source_inspection.py` | **Partial** — column hints are GeoX-oriented; shared inspection can feed declared columns |
| Input resolution / handoff | `geox_readout_input_resolution.py`, pipeline | **Lane-specific** — intent, metrics, experiment metadata |
| Fixture materialization | `geox_fixture_materialization.py` | **Extract CSV policy/inspection** — refactor candidate, not duplicate |
| `GeoXMaterializedInputAvailability` | `geox_panel_exp_integration.py` | **Lane-specific availability flags** — pattern reusable |
| Runtime / trust routing | Stage 3B–trust routing | **Lane-specific** — do not move to shared core |

### 4.2 Workflows

| Function | Purpose |
|----------|---------|
| `inspect_geox_readout_sources()` | Declared-column inspection |
| `resolve_geox_readout_inputs()` | Deterministic resolver on declared refs |
| `resolve_geox_readout_inputs_with_source_inspection()` | Inspection → enrich → resolve |
| `prepare_geox_panel_exp_integration()` | Adapter plan, no panel_exp call |
| `materialize_geox_readout_fixtures()` | Fixture CSV → `GeoXMaterializedDataset` |
| `build_materialized_input_availability_from_fixture_result()` | Availability metadata for Stage 3A |

### 4.3 GeoX required roles (lane-specific)

- KPI panel CSV
- Spend panel CSV (conditional on efficiency intent)
- Assignment/design table
- Experiment metadata
- Value/margin mapping (conditional)

---

## 5. Existing planning/MMM/budget/DecisionSurface lane

### 5.1 Intake and readiness (structural, no CSV materialization)

| Area | Contracts / workflows | Notes |
|------|----------------------|-------|
| Common intake workbench | `common_intake.py`, `common_workbench.py` | Declared sources, profile summaries |
| Asset requirements | `intake_assets.py`, `requirements.py` | Required asset types per path |
| Column mapping | `intake_mapping.py`, `mapping.py` | Semantic dimensions (date, spend, channel, geo, …) |
| Workflow readiness | `workflow_readiness.py`, `readiness.py` | `MMMDataReadinessReport`, `GeoXDesignReadinessReport`, `CalibrationSignalReadinessReport`, `DecisionReviewReadinessReport` |
| MMM config draft | `workflows/configs/mmm.py` — `MMMConfigDraft` | Field names for outcome/spend/date/channel/geo |
| Cold-start advisory | `advisory.py` | Hypothesis/planning before measurement |
| Calibration intake | `calibration_intake.py`, `calibration_mapping.py` | Maps external evidence → `CalibrationSignal` |

### 5.2 Governance and planning surfaces (not input materialization)

| Contract | Location | Role |
|----------|----------|------|
| `DecisionSurface` | `decision_surface.py` | Certified/diagnostic model surface for planning |
| `RecommendationContract` | `recommendation.py` | Gated recommendations (e.g. `BUDGET_SHIFT`) |
| `TrustReport` | `trust.py` | User-facing trust/explanation boundary |
| `ModelCalibrationReadiness` | `evidence/model_readiness.py` | MMM calibration readiness from evidence registry |

### 5.3 Planning lane required roles (lane-specific, not yet materialized from uploads)

- Historical spend / media exposure
- Historical KPI / outcome
- Channel / geo / product taxonomy mappings
- Budget constraints and scenario assumptions (future)
- Calibration priors / `CalibrationSignal` refs
- Model artifacts and readiness refs (`ModelCalibrationReadiness`)

### 5.4 Gap

Planning/MMM has **rich declared-intake and readiness contracts** but **no uploaded CSV materialization workflow** parallel to GeoX fixture materialization. Demo profiling consumes in-memory rows, not user upload paths.

---

## 6. Existing overlap and duplication risk

| Risk | Evidence | Severity |
|------|----------|----------|
| **Parallel source reference models** | `DataSourceRef` (intake) vs `DatasetReference` (GeoX) | Medium — different enums and fields; need adapter, not third model |
| **GeoX-only CSV reader** | `geox_fixture_materialization.py` already implements policy + `read_csv` | High if copied for uploads |
| **Unmerged GeoX upload slice** | Feature branch duplicates fixture logic under new names | High — exactly the sprawl this audit prevents |
| **Declared vs materialized split** | Stage 2A explicitly avoids file I/O; Stage 3 fixture adds I/O only under roots | Medium — shared core should sit between declaration and lane resolvers |
| **Demo vs user upload** | `demo_profiling` and Stage A loaders are fixture-scoped | Low — keep separate from shared user-upload core |

**Verdict:** `duplicate_csv_parser_risk_identified = true`. Building `MIP_GEOX_READOUT_UPLOADED_CSV_MATERIALIZATION_001` (or merging the existing feature branch) before a shared core would create a second CSV stack beside fixture materialization and a future planning parser.

---

## 7. Shared uploaded-data layer candidate

### 7.1 What should become shared infrastructure

| Component | Proposed shared contract / behavior |
|-----------|-----------------------------------|
| Uploaded file reference | `UploadedDataSourceRef` — path/handle, original filename, `source_type=uploaded_csv`, lineage (no warehouse/registry in v1) |
| CSV policy | Max file size, max rows, allowed extensions (`.csv` only), optional local-test roots |
| CSV inspection | Headers, row/column counts, file size, normalized column names, issue codes |
| Materialized dataset wrapper | Generic `MaterializedTabularDataset` (dataframe + columns + counts + lineage) — generalize pattern from `GeoXMaterializedDataset` |
| Validation issue codes | Shared enums: missing upload, malformed, empty, row limit, unsupported type |
| Role hints | Optional `semantic_role_hint` — lanes map hints to their own enums |
| DatasetReference adapter | `build_dataset_reference_from_materialized_source()` for GeoX compatibility |
| DataSourceRef adapter | `build_data_source_ref_from_materialized_source()` for common intake compatibility |

### 7.2 What must NOT be in the shared core

- GeoX readout intent resolution
- panel_exp / PostTestSpendInput construction
- MMM config drafting
- DecisionSurface optimization
- RecommendationContract generation
- Claim authorization
- Warehouse/API/registry ingestion

---

## 8. Lane-specific resolver candidates

### 8.1 GeoX readout lane

**Keep lane-specific:**

- `GeoXReadoutIntent`, metric requirements, experiment metadata refs
- `inspect_geox_readout_sources()` GeoX column semantics
- `resolve_geox_readout_inputs*()` handoff builder
- `GeoXPostTestSpendAdapterInputPlan`, panel_exp runtime call, result ingestion, trust routing
- Role mapping: KPI panel, spend panel, assignment table, experiment metadata

**Refactor to use shared core:**

- Replace duplicated CSV read/policy in fixture materialization with shared materialization + GeoX fixture root policy
- Future user-upload path: shared materialize → GeoX resolver (not a GeoX-only parser)

### 8.2 Planning/MMM lane

**Keep lane-specific:**

- `MMMConfigDraft`, workflow readiness reports, calibration mapping
- `DecisionSurface` / `RecommendationContract` / `TrustReport` gates
- `ModelCalibrationReadiness` and evidence registry traces
- Asset requirements per `DataAssetType` and intake path

**Add after shared core:**

- `resolve_planning_mmm_inputs_from_materialized_sources()` (future) — maps materialized spend/outcome/mapping tables to intake manifest + readiness inputs
- Scenario/budget constraint refs (deferred)

---

## 9. Recommended architecture

```text
User upload / local CSV path (dev/test)
  ↓
Shared uploaded data/materialization core
  - UploadedDataSourceRef
  - CSV policy (size, rows, extension)
  - Header/shape inspection
  - MaterializedTabularDataset + lineage
  - Shared validation issue codes
  ↓
  ├─→ GeoX readout input resolver lane
  │     - DatasetReference + source inspection (existing)
  │     - GeoXReadoutInputHandoff → panel_exp adapter plan → runtime (existing)
  │
  └─→ Planning/MMM input resolver lane
        - DataSourceRef / IntakeManifest alignment (new resolver, future)
        - MMM readiness + config draft + calibration intake (existing)
        - DecisionSurface / RecommendationContract (existing governance, no bypass)
```

**Adapter strategy:** Shared core produces materialized datasets + inspection metadata. Each lane adapter maps to its existing declared-reference contract (`DatasetReference` or `DataSourceRef`) without re-parsing CSV.

---

## 10. Recommended next implementation artifact

### **`MIP_SHARED_UPLOADED_CSV_MATERIALIZATION_CORE_001`**

**Justification:**

1. Main already has exactly one CSV reader (`geox_fixture_materialization.py`); extracting a shared core avoids a GeoX-only upload module and a future planning-only parser.
2. `DatasetReference` and `DataSourceRef` already cover **declaration**; the missing piece is **shared materialization**, not another lane-specific parser.
3. GeoX fixture materialization can be refactored to call the shared core with stricter fixture-root policy — preserving existing tests.
4. Planning/MMM lane has intake/readiness contracts but no materialization; it should consume the same core, not precede it with a separate upload stack.

**Not recommended next:**

| Artifact | Why not now |
|----------|-------------|
| `MIP_GEOX_READOUT_UPLOADED_CSV_MATERIALIZATION_001` | Duplicates fixture materialization; forecloses shared layer |
| `MIP_PLANNING_UPLOADED_CSV_INPUT_RESOLUTION_001` | No shared materialization to resolve from; would duplicate CSV parsing |

---

## 11. Explicitly deferred scope

- Warehouse / API table ingestion
- Artifact registry / production credential handling
- FastAPI / Streamlit upload route implementation
- Excel / Parquet / JSON upload support
- General production loader / arbitrary file types
- panel_exp runtime changes
- DecisionSurface execution / optimization
- RecommendationContract generation / business recommendation authorization
- Claim authorization duplication or bypass
- LLM / provider runtime changes
- MIP-side spend_delta, delta_mu, lift, ROI, ROAS computation

---

## 12. Acceptance criteria for next artifact (`MIP_SHARED_UPLOADED_CSV_MATERIALIZATION_CORE_001`)

1. Single shared module pair: `mip.contracts.shared_uploaded_csv_materialization` + `mip.workflows.shared_uploaded_csv_materialization` (names may vary but must be lane-neutral).
2. Supports `.csv` only with configurable policy limits (file size, row count).
3. Produces `MaterializedTabularDataset` + inspection metadata + lineage without lane-specific roles in the core.
4. Provides adapters to build `DatasetReference` and/or `DataSourceRef` from materialized output (no second CSV read).
5. Refactors `materialize_geox_readout_fixtures()` to delegate CSV read/validation to shared core where possible without changing external GeoX contract behavior.
6. No panel_exp import, no PostTestSpendInput, no metric computation, no recommendations.
7. Contract + workflow tests for shared core; GeoX fixture materialization regression tests still pass.

---

## 13. Final recommendation

**Proceed with `MIP_SHARED_UPLOADED_CSV_MATERIALIZATION_CORE_001` before any lane-specific uploaded CSV artifact.**

Do **not** merge GeoX-only uploaded CSV materialization as the long-term architecture. If short-term GeoX upload proof is needed, implement it as a thin wrapper over the shared core in a follow-on artifact (`MIP_GEOX_READOUT_UPLOADED_CSV_RUNTIME_BRIDGE_001` or similar), not as a standalone parser.

The repository already has sufficient **declared-reference** abstractions (`DatasetReference`, `DataSourceRef`, intake manifests, column mapping). The gap is a **single shared materialization layer** between user-provided files and lane-specific resolvers — not additional per-lane CSV parsers.

---

## 14. Implementation status (2026-07-09)

**`MIP_SHARED_UPLOADED_CSV_MATERIALIZATION_CORE_001` — implemented on main.**

| Component | Location |
|-----------|----------|
| Shared contracts | `mip.contracts.uploaded_csv_materialization` |
| Shared workflow | `mip.workflows.uploaded_csv_materialization` |
| Generic fixtures | `examples/fixtures/uploaded_csv_materialization/` |

**`MIP_GEOX_READOUT_UPLOADED_CSV_ADAPTER_001` — implemented on feature branch `feature/mip-geox-readout-uploaded-csv-adapter-001`.**

| Component | Location |
|-----------|----------|
| GeoX adapter contracts | `mip.contracts.geox_uploaded_csv_adapter` |
| GeoX adapter workflow | `mip.workflows.geox_uploaded_csv_adapter` |
| Adapter fixtures | `examples/fixtures/geox_uploaded_csv_adapter/` |

Maps shared `MaterializedTabularDataset` + `UploadedCSVInspection` outputs to GeoX roles, `DatasetReference`, and source inspection / input-resolution compatibility metadata. Does not re-read CSVs or invoke panel_exp.

**Deferred follow-ons:**

- `MIP_GEOX_READOUT_UPLOADED_CSV_RUNTIME_BRIDGE_001` — bridge adapter outputs into existing GeoX package runtime call path
- `MIP_PLANNING_MMM_UPLOADED_CSV_ADAPTER_001` — map shared outputs → planning/MMM intake refs

**Reference branch (not merged):** `feature/mip-geox-uploaded-csv-materialization-001` (`8931a29`) — generic concepts extracted into shared core; GeoX role enums intentionally excluded.
