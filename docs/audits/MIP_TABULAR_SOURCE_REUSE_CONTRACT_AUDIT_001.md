# MIP Tabular Source Reuse Contract Audit 001

**Artifact ID:** `MIP_TABULAR_SOURCE_REUSE_CONTRACT_AUDIT_001`  
**Type:** audit / control-plane only  
**Repo checkpoint:** `f54a950` — Add Planning MMM workflow readiness from uploaded CSV  
**Status:** completed (audit/documentation/governance-test only; no connector implementation)

---

## 1. Purpose

This audit exists to ensure the uploaded CSV foundation can evolve into a reusable tabular source abstraction **without losing** the current GeoX and Planning/MMM lanes.

The uploaded CSV path is already a working two-lane architecture:

- a **shared materialization core** that produces inspection + optional in-memory tabular datasets
- **lane-specific adapters** that map source outputs into GeoX or Planning/MMM semantics
- **downstream runtime or readiness layers** that consume lane adapter output

Future source types — Databricks tables, warehouse tables, API extracts, registered artifact tables — must **reuse** those downstream lanes rather than reimplementing role mapping, input planning, workflow readiness, trust routing, or governance boundaries.

This artifact is **audit/design only**. It defines:

1. **Reuse contract** — what future source adapters must emit
2. **Non-divergence rules** — what the current uploaded-CSV lane must not change
3. **Return-to-lane checkpoint** — the exact next artifact after this audit

---

## 2. Current source-to-lane architecture

### Shared uploaded CSV core

```
UploadedCSVSource
  → materialize_uploaded_csvs()
  → UploadedCSVMaterializationResult
      ├─ UploadedCSVInspection (per source: columns, row_count, lineage)
      └─ MaterializedTabularDataset (optional: in-memory DataFrame + metadata)
```

**Contracts:** `mip.contracts.uploaded_csv_materialization`  
**Workflow:** `mip.workflows.uploaded_csv_materialization`  
**Artifact:** `MIP_SHARED_UPLOADED_CSV_MATERIALIZATION_CORE_001`

### GeoX uploaded CSV lane

```
materialize_uploaded_csvs()
  → adapt_uploaded_csvs_for_geox_readout()
  → GeoXUploadedCSVAdapterResult
      ├─ role mappings (kpi_panel, spend_panel, assignment_table, …)
      └─ DatasetReference per mapped source
  → call_geox_post_test_spend_runtime_for_uploaded_csvs()
  → GeoXPostTestSpendEvidenceArtifact + GeoXTrustedReadoutSpendHandoffArtifact
  → ingest_geox_readout_result_for_explanation()
  → route_geox_readout_result_to_trust_boundaries()
```

**Adapter contracts/workflow:** `geox_uploaded_csv_adapter`  
**Runtime bridge:** `geox_uploaded_csv_runtime_bridge`  
**Downstream:** `geox_readout_result_ingestion`, `geox_readout_trust_routing`

### Planning/MMM uploaded CSV lane

```
materialize_uploaded_csvs()
  → adapt_uploaded_csvs_for_planning_mmm()
  → PlanningMMMUploadedCSVAdapterResult
      ├─ role mappings (historical_spend, historical_outcome, …)
      └─ DataSourceRef per mapped source
  → build_planning_mmm_uploaded_csv_input_plan()
  → PlanningMMMUploadedCSVInputPlanResult
  → evaluate_planning_mmm_workflow_readiness_from_uploaded_csv()
  → PlanningMMMUploadedCSVWorkflowReadinessResult
```

**Adapter contracts/workflow:** `planning_mmm_uploaded_csv_adapter`  
**Input plan:** `planning_mmm_uploaded_csv_input_plan`  
**Workflow readiness:** `planning_mmm_uploaded_csv_workflow_readiness`

### Existing cross-lane intake references

| Concept | Location | Role |
|---------|----------|------|
| `DataSourceRef` | `mip.contracts.intake_sources` | Planning/MMM intake source reference |
| `DatasetReference` | `mip.contracts.geox_readout_input_resolution` | GeoX readout dataset reference |
| `SourceIngestionRecord` | `mip.contracts.common_intake` | Intake workbench ingestion record |
| `MMMDataReadinessReport` | `mip.contracts.workflow_readiness` | Structural MMM readiness (metadata) |
| `ModelCalibrationReadiness` | `mip.evidence.model_readiness` | Calibration readiness object |
| `CalibrationSignal` | evidence/intake contracts | Calibration signal intake |

---

## 3. Reusable downstream boundary

Future source adapters must target this **stable reusable boundary** (audit contract; not implemented in this task):

### TabularSourceReference

Source-neutral pointer to a tabular origin. Must carry:

- `source_id` (stable within a request/session)
- `source_kind` (e.g. `uploaded_csv`, `databricks_table`, `warehouse_table`, `api_extract`, `registered_table`)
- `uri_or_table_ref` (file path, table FQN, endpoint ref, registry artifact id)
- `source_mode` / access policy metadata
- `lineage` (provenance chain)

**Compatibility target:** aligns with `DataSourceRef` fields where Planning/MMM lane consumes references; aligns with `DatasetReference` fields where GeoX lane consumes references.

### TabularSourceInspection

Source-neutral header/shape inspection. Must carry:

- `source_id`, `source_kind`
- `columns`, `normalized_columns`
- `row_count`, `column_count` (when known without full pull)
- `declared_role_hint` (optional, adapter-supplied)
- `issues`, `warnings`, `lineage`

**Compatibility target:** superset of `UploadedCSVInspection` semantics without CSV-specific type names.

### TabularSourceSchema

Column-level schema metadata:

- column names, normalized names, dtypes (when known)
- required/optional column declarations
- schema validation level (`presence_only` vs `required_columns`)

### TabularSourceLineage

Structured provenance:

- materialization stage, adapter stage, upstream system identifiers
- no credential payloads

### TabularSourceAvailability

Boolean/feature flags for downstream lane entry:

- role presence flags (lane adapters still own role mapping)
- optional gap flags
- execution-disallowed flags (must remain false at source layer)

### Optional MaterializedTabularDataset

In-memory materialization is **optional** and source-dependent:

- uploaded CSV: may materialize local file into DataFrame (current behavior)
- Databricks/warehouse/API: should default to metadata/sample inspection, not full pandas pull

### DataSourceRef compatibility

Planning/MMM lane adapters ultimately emit `DataSourceRef`. Future source adapters must produce inspection/reference payloads that lane adapters can convert into `DataSourceRef` **without** re-reading or re-parsing when a reference already exists.

---

## 4. Future adapter rule

Future source adapters are responsible **only** for source-specific:

- authentication/credential resolution (outside MIP core; not in this repo slice)
- connection / metadata inspection
- optional bounded sample or staging materialization
- emission of `TabularSourceReference` + `TabularSourceInspection` (+ optional materialized dataset)

They must **not** reimplement:

| Forbidden in source adapters | Owned by |
|------------------------------|----------|
| GeoX role mapping | `adapt_uploaded_csvs_for_geox_readout` (future: generic tabular GeoX adapter) |
| Planning/MMM role mapping | `adapt_uploaded_csvs_for_planning_mmm` (future: generic tabular Planning adapter) |
| Planning/MMM input plan | `build_planning_mmm_uploaded_csv_input_plan` |
| Planning/MMM workflow readiness | `evaluate_planning_mmm_workflow_readiness_from_uploaded_csv` |
| GeoX runtime bridge / package evidence | `call_geox_post_test_spend_runtime_for_uploaded_csvs` |
| Trust routing | `route_geox_readout_result_to_trust_boundaries` |
| DecisionSurface logic | decision/recommendation lane |
| Recommendation logic | `RecommendationContract` lane |
| Claim authorization | trust/governance lane |
| Model fitting / optimization / simulation | MMM execution lane (deferred) |

---

## 5. Source-specific expectations (deferred implementation)

### Uploaded CSV (implemented)

- May materialize local CSV into pandas DataFrame
- Owns file extension, header, row-limit, and malformed-file policy
- Existing `materialize_uploaded_csvs()` remains canonical
- Must keep passing all uploaded CSV regression tests

### Databricks table (deferred)

- Inspect schema/table metadata and bounded sample only
- Must not pull full table into pandas by default
- Emit source reference + schema + lineage
- No Databricks SDK in MIP until a dedicated adapter artifact is approved

### Warehouse table (deferred)

- Inspect schema/table metadata and bounded sample only
- Must not execute broad `SELECT *`
- Emit source reference + schema + lineage
- No warehouse client (Snowflake/BigQuery/Redshift/etc.) in MIP until dedicated artifact

### API extract (deferred)

- Inspect endpoint/payload schema or staged extract metadata
- Emit source reference + schema + lineage
- No live API calls in MIP core until dedicated artifact

### Registered artifact/table (deferred)

- Resolve registry metadata only
- Emit source reference + schema + lineage
- No artifact registry runtime in MIP until dedicated artifact

---

## 6. CSV-specific leakage audit

Search scope: `src/mip`, `tests`, `docs` for `UploadedCSV`, `uploaded_csv`, `MaterializedTabularDataset`, `UploadedCSVInspection`, `declared_role_hint`, `DataSourceRef`, `DatasetReference`.

### Acceptable CSV-specific layer

| Location | Why acceptable |
|----------|----------------|
| `mip.contracts.uploaded_csv_materialization` | Canonical CSV materialization contracts |
| `mip.workflows.uploaded_csv_materialization` | Canonical CSV materialization workflow |
| `mip.contracts.geox_uploaded_csv_adapter` | GeoX lane adapter naming reflects current source |
| `mip.contracts.planning_mmm_uploaded_csv_adapter` | Planning lane adapter naming reflects current source |
| `mip.workflows.geox_uploaded_csv_*` | GeoX uploaded CSV path |
| `mip.workflows.planning_mmm_uploaded_csv_*` | Planning uploaded CSV path |
| `tests/**/test_*uploaded_csv*` | Lane regression coverage |
| `docs/contracts/archives/MIP_*_UPLOADED_CSV_*` | Artifact summaries |
| `examples/fixtures/planning_mmm_uploaded_csv_adapter/` | Fixture data |

### Needs future compatibility bridge

| Finding | Risk | Bridge artifact |
|---------|------|-----------------|
| Lane adapters accept `UploadedCSVMaterializationResult` directly | New source types cannot plug in without CSV materialization | `MIP_UPLOADED_CSV_TO_TABULAR_SOURCE_COMPATIBILITY_001` |
| `MaterializedTabularDataset.source_type` is `UploadedCSVSourceType` | Type leakage into runtime bridge | Generic `TabularSourceKind` + compatibility view |
| `planning_mmm_uploaded_csv_*` module names | Semantically source-generic readiness/plan logic | `MIP_PLANNING_MMM_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001` |
| `geox_uploaded_csv_*` adapter contracts | Semantically source-generic role mapping | `MIP_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001` |
| `declared_role_hint` on CSV source/inspection | Reasonable generic hint; name is CSV-coupled | Map to `TabularSourceInspection.declared_role_hint` |
| `build_data_source_ref_from_uploaded_csv_inspection` helper naming | Planning adapter helper is CSV-named | Rename/wrap behind generic inspection bridge |

### Should not be generalized now

| Component | Reason |
|-----------|--------|
| `call_geox_post_test_spend_runtime_for_uploaded_csvs` | Working GeoX package runtime boundary; uses materialized DataFrames by design |
| GeoX panel_exp integration boundary | Package-specific runtime; separate artifact lane |
| Planning/MMM workflow readiness behavior | Correct governance layer; only input contract should generalize |
| Uploaded CSV file policy (extensions, row limits) | CSV-specific by definition |
| Trust routing / explanation ingestion | Downstream of runtime; not a source concern |

---

## 7. Proposed future extraction path

Incremental, non-breaking sequence:

### Step 1: `MIP_TABULAR_SOURCE_REFERENCE_AND_INSPECTION_001`

Define generic tabular source reference/inspection contracts (`TabularSourceReference`, `TabularSourceInspection`, schema, lineage, availability). No connector runtime.

### Step 2: `MIP_UPLOADED_CSV_TO_TABULAR_SOURCE_COMPATIBILITY_001`

Add compatibility view from existing `UploadedCSVInspection` / `MaterializedTabularDataset` / `UploadedCSVMaterializationResult` to generic tabular source inspection. Uploaded CSV path remains canonical; no CSV core rewrite.

### Step 3: `MIP_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001`

Let GeoX lane adapter consume generic tabular source inspection while preserving uploaded CSV adapter as a thin wrapper.

### Step 4: `MIP_PLANNING_MMM_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001`

Let Planning/MMM lane adapter consume generic tabular source inspection while preserving uploaded CSV adapter as a thin wrapper.

### Step 5: Source-specific adapters (later, separate artifacts)

- `MIP_DATABRICKS_TABULAR_SOURCE_ADAPTER_001` (deferred)
- `MIP_WAREHOUSE_TABULAR_SOURCE_ADAPTER_001` (deferred)
- `MIP_API_TABULAR_SOURCE_ADAPTER_001` (deferred)
- `MIP_REGISTERED_TABLE_TABULAR_SOURCE_ADAPTER_001` (deferred)

Each source adapter emits only the common boundary from Section 3, then calls existing lane adapters.

---

## 8. Non-divergence checkpoint

**This audit does not authorize connector implementation.**

After this audit, the default next implementation **returns to the current Planning/MMM uploaded CSV lane** unless the user explicitly chooses source generalization next.

### Default next artifact (lane continuation)

**`MIP_PLANNING_MMM_READINESS_REPORT_ADAPTER_001`**

Map `PlanningMMMUploadedCSVWorkflowReadinessResult` into existing `MMMDataReadinessReport`-compatible contracts where safe. Metadata-only bridge. Still forbidden: model fitting, optimization, simulator, budget recommendation, DecisionSurface execution, claim authorization.

### Alternative next artifact (source reuse foundation)

**`MIP_TABULAR_SOURCE_REFERENCE_AND_INSPECTION_001`**

Define generic tabular source reference/inspection contracts before adding Databricks/API/warehouse adapters.

### Decision rule

| Goal | Next artifact |
|------|---------------|
| Finish uploaded CSV Planning/MMM readiness integration | `MIP_PLANNING_MMM_READINESS_REPORT_ADAPTER_001` |
| Prepare for Databricks/API/warehouse reuse before further lane work | `MIP_TABULAR_SOURCE_REFERENCE_AND_INSPECTION_001` |

### Return-to-current-lane checkpoint

The uploaded CSV lanes documented in Section 2 remain **canonical** and must keep passing all regression tests. No future work may rewrite them as part of source generalization; only add compatibility layers in front of them.

---

## 9. Architecture guardrails

1. **Current uploaded CSV lane remains canonical** — all `test_*uploaded_csv*` regression tests must pass after any future source work.
2. **Future source adapters target the common source boundary** (Section 3) — not lane adapters directly with vendor-specific types.
3. **Lane adapters eventually depend on source-neutral inspection/reference contracts** — via compatibility bridges, not rewrites.
4. **No future source adapter may bypass** `TrustReport` / `DecisionSurface` / `RecommendationContract` boundaries.
5. **No source adapter may fit models, optimize budgets, simulate scenarios, or compute recommendations.**
6. **No credentials, network calls, Spark, SQL execution, JDBC/ODBC, or vendor SDKs** in MIP until explicitly scoped adapter artifacts are approved.
7. **GeoX and Planning/MMM lanes stay separate** — shared source core only; no merged role enum across lanes.

---

## 10. Recommended next step

**Default (lane continuation):** `MIP_PLANNING_MMM_READINESS_REPORT_ADAPTER_001`

Bridge uploaded CSV workflow-readiness output into existing `MMMDataReadinessReport` contracts where safe. Completes the Planning/MMM uploaded CSV readiness integration without opening connector scope.

**Source-reuse foundation (when prioritized):** `MIP_TABULAR_SOURCE_REFERENCE_AND_INSPECTION_001`

Define generic tabular source contracts so Databricks/warehouse/API adapters have a governed target without diverging from current lanes.

---

## Audit deliverable scope statement

This artifact added:

- `docs/audits/MIP_TABULAR_SOURCE_REUSE_CONTRACT_AUDIT_001.md` (this document)
- `docs/audits/archives/MIP_TABULAR_SOURCE_REUSE_CONTRACT_AUDIT_001_summary.json`
- `tests/governance/test_tabular_source_reuse_contract_audit_001.py`

This artifact did **not** add:

- Databricks, warehouse, API, or registered-table adapter modules
- live connector runtime, credentials, network calls, Spark, SQL, JDBC/ODBC, or vendor SDK dependencies
- CSV core rewrite, GeoX lane rewrite, or Planning/MMM lane rewrite
- model fitting, optimizer, simulator, recommendation generation, DecisionSurface execution, or claim authorization

---

## Implementation update: `MIP_TABULAR_SOURCE_REFERENCE_AND_INSPECTION_001`

**Status:** implemented on main (feature branch `feature/tabular-source-reference-inspection-001` until merged).

| Component | Location |
|-----------|----------|
| Generic tabular source contracts | `mip.contracts.tabular_source_reference` |
| Tabular source inspection helpers | `mip.workflows.tabular_source_inspection` |

Adds generic `TabularSourceReference`, `TabularSourceInspection`, schema, lineage, and availability contracts plus `build_tabular_source_inspection_from_uploaded_csv_materialization()` compatibility view. Does not modify GeoX or Planning/MMM lane adapters. Uploaded CSV lanes remain canonical.

**Default next artifact (lane continuation):** `MIP_PLANNING_MMM_READINESS_REPORT_ADAPTER_001`

**Source-compatibility follow-up:** `MIP_PLANNING_MMM_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001`
