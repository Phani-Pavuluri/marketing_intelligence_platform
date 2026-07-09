# MIP GeoX Readout Input Requirements and Handoff Contract 001

## 1. Artifact metadata

| Field | Value |
|-------|-------|
| **artifact_id** | `MIP_GEOX_READOUT_INPUT_REQUIREMENTS_AND_HANDOFF_CONTRACT_001` |
| **artifact_type** | `mip_geox_readout_input_requirements_and_handoff_contract` |
| **status** | completed |
| **scope** | `mip_geox_readout_input_handoff_contract_defined_no_runtime_or_spend_computation` |
| **lane** | MIP ↔ GeoX readout handoff (Lane B — post-test KPI / spend / ROI readiness) |
| **date** | 2026-07-09 |
| **final_verdict** | `mip_geox_readout_input_handoff_contract_defined_no_runtime_or_spend_computation` |

**Depends on (panel_exp / GeoX package context):**

| GeoX artifact | Role |
|---------------|------|
| `FINAL_TEST_RESULTS_EXISTING_ARTIFACT_REUSE_AUDIT_001` | Existing artifact reuse audit |
| `GEOX_READOUT_DATAFLOW_AND_SPEND_EXTRACTION_PROCESS_AUDIT_001` | Readout dataflow and spend extraction audit |
| `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001` | Package-side post-test spend/ROI readiness (commit `eb9992a`) |
| `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` | Next package runtime (expected) |

**Related MIP governance (consume, do not bypass):**

- `TrustReport` — MIP explains readiness/blockers; does not authorize claims from numeric readiness alone
- `DecisionSurface` — budget/mix decisions require certified Δμ surface
- `RecommendationContract` — business recommendations require governed recommendation path

---

## 2. Why this contract exists

GeoX Lane B — **final trusted readout / spend / ROI readiness** — has been formalized package-side through `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001`. That contract defines how panel_exp validates post-test KPI panels, spend evidence, value mappings, and spend_delta readiness **after** correct datasets and mappings are supplied.

MIP is the **user-facing orchestration layer**. Before panel_exp can validate schemas, filter windows, join assignments, run counterfactual KPI / `delta_mu`, extract post-test spend, or assemble trusted readouts, MIP must:

1. Detect a GeoX readout request and classify readout intent
2. Inventory and classify user-provided datasets and source references
3. Ask for or resolve required post-test KPI data
4. Optionally ask for post-test spend and value/margin mapping when efficiency metrics are requested
5. Infer column mappings and request user confirmation when ambiguous or risky
6. Pass typed dataset references, confirmed mappings, and lineage into panel_exp

Without this MIP-side handoff contract, GeoX can only validate and extract spend **after** MIP passes the correct inputs — and MIP risks ad-hoc `spend_delta` or ROI/ROAS calculations that belong in panel_exp.

**This artifact is docs/tests-only.** No runtime orchestration, no panel_exp calls, no spend ingestion system.

**Stage 2A (implemented):** Typed contracts in `mip.contracts.geox_readout_input_resolution` and deterministic resolver skeleton `resolve_geox_readout_inputs()` in `mip.workflows.geox_readout_input_resolution`. Operates on **declared** dataset references only — no real file parsing, no warehouse/API calls, no panel_exp invocation, no MIP metric computation.

**Stage 2B (implemented):** Lightweight source inspection adapters in `mip.contracts.geox_readout_source_inspection` and `mip.workflows.geox_readout_source_inspection`. Inspects declared `DatasetReference` objects and emits metadata, semantic hints, and column mapping candidates — still no deep file parsing, no warehouse/API live calls, no panel_exp invocation.

**Stage 2C (implemented):** Inspection-to-resolution pipeline in `mip.contracts.geox_readout_input_resolution_pipeline` and `mip.workflows.geox_readout_input_resolution_pipeline`. Runs `inspect_geox_readout_sources()`, enriches resolver-ready `DatasetReference` objects and column mappings, then calls `resolve_geox_readout_inputs()` — still without panel_exp calls or GeoX metric computation.

---

## 3. Optimized 3-stage GeoX handoff lane

The GeoX readout handoff lane is **three stages**, not 5–8 fragmented artifacts. Future implementation should stay within this lane unless complexity later proves a split is necessary.

### Stage 1 — `MIP_GEOX_READOUT_INPUT_REQUIREMENTS_AND_HANDOFF_CONTRACT_001` (this artifact)

**Purpose:** Boundary, required inputs, MIP/panel_exp ownership split, and `GeoXReadoutInputHandoff` concept.

**Status:** completed (docs/tests only).

### Stage 2 — `MIP_GEOX_READOUT_INPUT_RESOLUTION_RUNTIME_001`

**Purpose:** One MIP input intelligence runtime.

**Stage 2A (implemented on main):** Typed contracts + deterministic `resolve_geox_readout_inputs()` skeleton. Declared dataset refs only; no file parsing; no panel_exp calls.

**Stage 2B (implemented on main):** `inspect_geox_readout_sources()` / `inspect_dataset_reference()` — deterministic metadata inspection of declared refs, semantic hints, and mapping candidates. No deep file parsing; no warehouse/API live calls.

**Stage 2C (implemented on main):** `resolve_geox_readout_inputs_with_source_inspection()` — enriches refs/mappings from inspection output, then calls `resolve_geox_readout_inputs()`. Stage 2A resolver brain unchanged when called directly.

| Component | Responsibility |
|-----------|----------------|
| Readout intent detection | Classify intent even when user does not say "readout" |
| Dataset/source inventory | Uploaded files, tables, API refs, registered artifacts |
| Dataset semantic classification | KPI / spend / assignment / value / design / unknown |
| Column mapping inference | Propose date, geo, metric, spend, assignment bindings |
| User confirmation | Required when mappings are ambiguous or risky |
| Experiment metadata resolution | Gather refs from design artifacts and user input |
| Missing-input detection | Typed blockers per readout intent |
| Full vs partial readiness | Lift-only vs efficiency metrics |
| Handoff builder | Emit `GeoXReadoutInputHandoff` |

**Implementation components (not separate roadmap lanes):** dataset resolver, column mapper, metadata resolver, readiness gate, handoff builder — all live under Stage 2.

### Stage 3 — `MIP_GEOX_READOUT_PANEL_EXP_INTEGRATION_001`

**Purpose:** panel_exp integration once package runtime exists.

**Stage 3A (implemented):** Adapter boundary in `mip.contracts.geox_panel_exp_integration` and `mip.workflows.geox_panel_exp_integration`. Maps `GeoXReadoutInputHandoff` to `GeoXPostTestSpendAdapterInputPlan` and materialization blockers. Records GeoX runtime API handoff (`9fe4b92` / `b400912` / `9039fda`). No `panel_exp` import/call; no `PostTestSpendInput` instantiation.

**Stage 3B (implemented):** Runtime call slice (`MIP_GEOX_READOUT_PANEL_EXP_RUNTIME_CALL_001B`) — fixture-materialized inputs only via `call_geox_post_test_spend_runtime_for_fixture()`. Lazy `panel_exp` import; builds `PostTestSpendInput`, calls `build_post_test_spend_evidence` and `build_trusted_readout_spend_handoff`; returns MIP readiness artifacts with package-computed `spend_delta` labeled under `package_computed_spend_delta`. No production loader; claim authorization delegated to `CLAIM_AUTHORIZATION_RUNTIME_001`.

**Optional `panel_exp` dependency:** `panel_exp` is **not** listed in MIP `pyproject.toml`. Stage 3B is an optional fixture/runtime integration path: the runtime-call workflow lazy-imports `panel_exp` only when `allow_runtime_call=True` and fixture materialization checks pass. Workflow tests use `pytest.importorskip("panel_exp")` — they skip when the sibling GeoX package is not installed. To exercise the full fixture runtime path locally, install the sibling repo editable (e.g. `poetry run pip install -e /path/to/panel_exp`). MIP core installs and CI without `panel_exp` remain valid; blocking-path tests do not require the package.

**Fixture materialization (implemented):** `MIP_GEOX_READOUT_FIXTURE_MATERIALIZATION_ADAPTER_001` — narrow local CSV fixture materialization via `materialize_geox_readout_fixtures()` for controlled test paths. Not a production materialized input provider.

**Result ingestion and explanation (implemented):** `MIP_GEOX_READOUT_RESULT_INGESTION_AND_EXPLANATION_001` — ingests Stage 3B `GeoXPostTestSpendEvidenceArtifact` and `GeoXTrustedReadoutSpendHandoffArtifact` via `ingest_geox_readout_result_for_explanation()` and returns a MIP-facing `GeoXReadoutResultEnvelope`. Explains package readiness, blockers, warnings, and claim boundaries without `panel_exp` import, metric recomputation, or claim authorization.

**Trust routing (implemented):** `MIP_GEOX_READOUT_TRUST_ROUTING_001` — routes `GeoXReadoutResultEnvelope` via `route_geox_readout_result_to_trust_boundaries()` into TrustReport / DecisionSurface / RecommendationContract readiness metadata. No metric recomputation, no claim authorization, no business recommendations.

| Component | Responsibility |
|-----------|----------------|
| Handoff adapter | Pass `GeoXReadoutInputHandoff` to panel_exp |
| Result ingestion | Receive trusted readout / spend readiness output |
| Artifact registration | Register returned artifact in MIP evidence registry |
| MIP-facing explanation | Convert readiness into user-facing readiness/blocker messaging |
| Decision routing | Route business-decision requests through `TrustReport` / `DecisionSurface` / `RecommendationContract` |

**Implementation components (not separate roadmap lanes):** adapter, result ingestion, explanation surfacing — all live under Stage 3.

### Anti-sprawl rule

Do **not** create separate future artifact lanes for dataset resolver, column mapper, metadata resolver, readiness gate, handoff builder, adapter, and result explainer unless implementation later proves they need to be split. Record that decision in a follow-on contract amendment — not as parallel roadmap tracks.

---

## 4. Package / MIP ownership split

| Responsibility | MIP owner? | panel_exp owner? | Notes |
|----------------|------------|------------------|-------|
| User request interpretation | yes | no | MIP / orchestration |
| Ask for KPI dataset | yes | no | Required for readout |
| Ask for spend dataset | yes | no | Only when spend-derived metrics requested |
| Ask for value/margin mapping | yes | no | Only when ROAS/profit ROI requested |
| Resolve uploaded file/table/API/source refs | yes | no | When available |
| Classify provided datasets | yes | no | MIP input intelligence (Stage 2) |
| Infer column mappings | yes | no | MIP proposes; user confirms when risky |
| Resolve experiment metadata refs | yes | no | MIP gathers refs; panel_exp validates |
| Validate KPI schema | no | yes | panel_exp |
| Validate spend schema | no | yes | panel_exp |
| Filter KPI/spend to test window | no | yes | panel_exp |
| Treatment/control assignment join | no | yes | panel_exp |
| Compute counterfactual KPI / `delta_mu` | no | yes | Estimator runtime |
| Compute spend_delta readiness | no | yes | GeoX spend readiness adapter |
| Assemble trusted readout | no | yes | `TRUSTED_READOUT_REPORT_*` |
| Authorize claims | no | yes (package) | `CLAIM_AUTHORIZATION_RUNTIME_001` |
| TrustReport / user explanation | yes | consumes | MIP interprets returned readiness |

**Critical boundary:** MIP must **not** compute `spend_delta` casually. MIP passes dataset references and declared/confirmed mappings; panel_exp owns derivation, alignment, and readiness.

---

## 5. MIP readout intent detection

MIP classifies user requests into readout intent categories before handoff. The user does **not** have to explicitly say "readout."

| Intent | Description | Minimum data path |
|--------|-------------|-------------------|
| `READOUT_KPI_ONLY` | Post-test KPI panel / counts | KPI + experiment metadata |
| `READOUT_WITH_LIFT` | Incremental lift / counterfactual KPI | KPI + assignment + dates + design ref |
| `READOUT_WITH_COST_PER` | Cost per incremental unit / media efficiency | KPI + lift path + **post-test spend** |
| `READOUT_WITH_ROAS` | Return on ad spend | KPI + lift path + spend + **revenue/value mapping** |
| `READOUT_WITH_PROFIT_ROI` | Profit ROI | KPI + lift path + spend + **margin/profit mapping** |
| `READOUT_WITH_DECISION_RECOMMENDATION_REQUEST` | Budget reallocation / production decision | Route to `RecommendationContract` / `DecisionSurface` / `TrustReport` |
| `READOUT_UNCLEAR_METRIC_REQUEST` | Ambiguous metric ask | Clarify intent before handoff |

### Routing rules

1. ROI, cost-per, ROAS, and profit requests **imply** readout intent plus spend/value requirements — user need not say "readout."
2. **KPI-only / lift** requires KPI data, experiment metadata, assignment, and date windows.
3. **Cost-per** requires KPI path **plus** post-test spend evidence aligned to experiment geos and test window.
4. **ROAS** requires incremental revenue or explicit revenue mapping **plus** spend evidence.
5. **Profit ROI** requires margin/profit mapping **plus** spend evidence.
6. If user **already provided spend**, MIP must **not** ask for spend again — use the provided spend dataset ref and mapping, subject to confirmation/readiness.
7. If user requests ROI but spend is missing, MIP asks for spend and may allow **partial KPI/lift readout** when possible (`PARTIAL_READOUT_ALLOWED`).
8. **Decision recommendation requests** must route through `RecommendationContract`, `DecisionSurface`, and `TrustReport` — not direct GeoX readout.
9. MIP must **not** require spend for plain increment/lift readout unless the selected readout template explicitly requires efficiency metrics.

---

## 6. Dataset / source inventory and semantic classification expectations

**Future Stage 2 behavior** — expectations only; no runtime in this artifact.

### Source types MIP should inventory

| Source type | Example |
|-------------|---------|
| `uploaded_csv` | User-uploaded CSV |
| `uploaded_excel` | User-uploaded Excel |
| `uploaded_parquet` | User-uploaded Parquet |
| `warehouse_table` | Snowflake/BigQuery table ref |
| `api_reference` | Platform API export handle |
| `registered_artifact` | Governed artifact in evidence registry |
| `manual_user_entry` | Structured user-declared fields |

### Semantic dataset types

| Type | Role |
|------|------|
| `KPI_PANEL` | Post-test outcome panel |
| `SPEND_PANEL` | Post-test spend panel |
| `ASSIGNMENT_TABLE` | Treatment/control/cell assignment |
| `EXPERIMENT_METADATA` | Design, dates, experiment identity |
| `VALUE_MAPPING` | Revenue/value mapping |
| `MARGIN_MAPPING` | Margin/profit mapping |
| `DESIGN_ARTIFACT` | Experiment design export |
| `UNKNOWN_DATASET` | Unclassified — requires user confirmation |

### Per-dataset inventory fields (minimum)

| Field | Description |
|-------|-------------|
| `dataset_ref_id` | Stable inventory identifier |
| `source_type` | One of source types above |
| `source_uri_or_handle` | Path, URI, or handle |
| `file_name_or_table_name` | Human-readable name |
| `declared_or_detected_columns` | Column list |
| `semantic_dataset_type` | One of semantic types above |
| `classification_confidence` | high / medium / low |
| `user_confirmation_status` | pending / confirmed / rejected |
| `lineage` | Provenance chain |
| `warnings` | Non-blocking classification warnings |

---

## 7. Column mapping inference and confirmation expectations

**Future Stage 2 behavior** — expectations only.

MIP may infer likely column mappings but **must ask for confirmation** when ambiguous or risky.

### Mapping status values

| Status | Meaning |
|--------|---------|
| `INFERRED_HIGH_CONFIDENCE` | Strong signal; may proceed with explicit user ack |
| `INFERRED_LOW_CONFIDENCE` | Requires confirmation before handoff |
| `USER_CONFIRMED` | User explicitly confirmed |
| `USER_REJECTED` | User rejected inference; re-prompt |
| `MISSING` | No candidate column found |
| `AMBIGUOUS` | Multiple candidates; user must choose |

### KPI mapping candidates

- date/week column
- geo/unit column
- KPI metric column
- KPI metric name/unit

### Spend mapping candidates

- date/week column
- geo/unit column
- spend amount column
- currency column
- campaign/channel/platform columns (when available)
- treatment/cell/campaign join keys (when available)

### Assignment mapping candidates

- geo/unit column
- cell column
- treatment/control label
- experiment_id

### Value/margin mapping candidates

- KPI-to-revenue mapping
- value per incremental KPI
- margin/profit mapping
- currency
- value window

MIP passes **declared/confirmed** mappings to panel_exp. panel_exp owns deterministic schema and alignment validation.

---

## 8. Required MIP inputs for any GeoX readout

| Field | Required | Notes |
|-------|----------|-------|
| `experiment_id` | yes | Stable experiment identifier |
| `experiment design artifact/reference` | yes | Design artifact ref or governed export |
| `test_start_date` | yes | Inclusive test window start |
| `test_end_date` | yes | Inclusive test window end |
| `post_period_start` | yes | Readout post-period start |
| `post_period_end` | yes | Readout post-period end |
| `pre_period_start` / `pre_period_end` | conditional | When estimator requires pre-period |
| `geo/unit assignment artifact/reference` | yes | Assignment provenance |
| `treatment/control/cell assignment` | yes | Or resolvable from design artifact |
| `KPI dataset reference or source reference` | yes | Upload ref, warehouse ref, or API ref |
| `KPI date/week column mapping` | yes | Semantic column binding |
| `KPI geo/unit column mapping` | yes | Must align to assignment geos |
| `KPI metric column mapping` | yes | Outcome column(s) |
| `KPI metric name/unit` | yes | Declared metric identity |
| `estimator/inference identity` | optional | User may specify; otherwise package decides |

---

## 9. Conditional MIP inputs for spend-derived metrics

Required when user asks for cost-per, ROI, ROAS, media efficiency, payback, business value, or similar.

| Field | Required | Notes |
|-------|----------|-------|
| `spend dataset reference or upstream spend source reference` | yes | Not computed in MIP |
| `spend date/week column` | yes | Alignable to test window |
| `spend geo/unit column or geo mapping` | yes | Must join to experiment geos |
| `spend amount column` | yes | Currency-denominated spend |
| `campaign/channel/platform columns` | when available | Improves join fidelity |
| `treatment/cell/campaign join keys` | when available | Cell-level spend alignment |
| `currency` | yes | ISO or declared code |
| `spend source` | yes | e.g. ad platform export, finance ledger |
| `spend scope` | yes | e.g. test geos only |
| `spend window` | yes | Must cover post-test readout window |
| `baseline/BAU spend definition` | when available | User-declared; panel_exp validates |
| `planned spend or counterfactual spend reference` | when available | **Not** substituted for observed post-test spend |

MIP must **not** convert planning `required_spend_delta` into observed post-test `spend_delta`.

---

## 10. Conditional MIP inputs for value/margin mapping

Required when user asks for ROAS/profit ROI and KPI is not already revenue/profit.

| Field | Required | Notes |
|-------|----------|-------|
| `value_per_incremental_kpi` | conditional | When single scalar mapping declared |
| `revenue mapping source` | for ROAS | Lineage required |
| `margin/profit mapping source` | for profit ROI | Lineage required |
| `currency` | yes | Consistent with spend |
| `value window` | yes | Must be compatible with KPI window |
| `compatibility with KPI window` | yes | MIP declares; panel_exp validates |
| `source lineage` | yes | User upload, finance ref, or declared assumption |

---

## 11. MIP missing-input prompts

### KPI data missing

> Please provide the post-test KPI panel or a data-source reference with geo/unit, date/week, and KPI columns.

### Spend data missing but ROI/cost-per requested

> I can run increment/lift readout with KPI data, but cost-per/ROI/ROAS requires post-test spend data or a spend-source reference aligned to the experiment geos and test window.

### Value mapping missing

> I can compute incremental KPI and spend efficiency if spend is provided, but ROAS/profit ROI requires revenue/value or margin mapping.

### Assignment missing

> Please provide the treatment/control/cell assignment or the experiment design artifact used for this test.

### Dates missing

> Please provide test start/end dates and the post-period window for readout.

### Mapping confirmation needed

> I inferred the likely geo/date/KPI/spend column mappings. Please confirm these mappings before I prepare the GeoX handoff.

### Unclear metric request

> Please clarify whether you need incremental lift only, cost-per efficiency, ROAS, or profit ROI so I can request the right datasets.

### Decision recommendation misrouted

> Budget reallocation and production spend decisions require a governed recommendation path. I can help with GeoX readout metrics first, then route certified outputs through decision review.

---

## 12. Typed handoff object

**Future contract:** `GeoXReadoutInputHandoff`

| Field | Description |
|-------|-------------|
| `request_id` | Stable MIP request identifier |
| `user_request` | Documentation metadata |
| `readout_intent` | One of §5 categories |
| `experiment_id` | Experiment identifier |
| `design_artifact_ref` | Design provenance |
| `assignment_artifact_ref` | Assignment provenance |
| `kpi_dataset_ref` | KPI panel or warehouse/API ref |
| `kpi_column_mapping` | Date, geo, metric bindings |
| `spend_dataset_ref_optional` | Present when efficiency metrics requested |
| `spend_column_mapping_optional` | Spend column bindings |
| `spend_baseline_definition_optional` | User-declared BAU/baseline semantics |
| `value_mapping_optional` | Revenue/margin mapping when required |
| `requested_metrics` | lift, cost_per, roas, profit_roi, … |
| `missing_inputs` | Typed missing field IDs |
| `mip_resolution_status` | One of §13 |
| `panel_exp_target_contract` | `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001` |
| `panel_exp_expected_runtime` | `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` |
| `lineage` | Source refs for all user-resolved inputs |
| `warnings` | Non-blocking resolution warnings |

**Handoff invariant:** No embedded `spend_delta`, ROI, ROAS, or lift numeric outputs.

---

## 13. MIP resolution statuses

| Status | Meaning |
|--------|---------|
| `READY_FOR_GEOX_READOUT` | All required inputs for requested intent present |
| `READY_FOR_KPI_ONLY_READOUT` | KPI path complete |
| `READY_FOR_LIFT_ONLY_READOUT` | Lift path complete |
| `READY_FOR_COST_PER_READOUT` | Cost-per path complete (KPI + spend) |
| `PARTIAL_READOUT_ALLOWED` | Lift/KPI possible; efficiency metrics blocked |
| `BLOCKED_MISSING_KPI_DATA` | KPI dataset or mapping missing |
| `BLOCKED_MISSING_EXPERIMENT_METADATA` | experiment_id or design ref missing |
| `BLOCKED_MISSING_ASSIGNMENT` | Assignment missing |
| `BLOCKED_MISSING_DATES` | Test or post-period windows missing |
| `BLOCKED_MISSING_SPEND_FOR_EFFICIENCY` | Spend required for cost-per/ROI/ROAS |
| `BLOCKED_MISSING_VALUE_MAPPING_FOR_ROAS` | Revenue mapping missing |
| `BLOCKED_MISSING_MARGIN_MAPPING_FOR_PROFIT_ROI` | Margin mapping missing |
| `BLOCKED_MAPPING_CONFIRMATION_REQUIRED` | Inferred mappings need user confirmation |
| `BLOCKED_UNCLEAR_USER_INTENT` | Cannot classify readout intent |
| `BLOCKED_NO_GEOX_RUNTIME_AVAILABLE` | Package runtime not wired (Stage 3 gate) |

---

## 14. MIP-to-panel_exp rules

1. MIP may pass raw dataset refs and column mappings.
2. MIP may pass upstream spend evidence refs when available.
3. MIP may pass user-provided baseline/BAU spend definitions with lineage.
4. MIP must **not** silently infer `spend_delta` without lineage.
5. MIP must **not** convert planning `required_spend_delta` into observed post-test `spend_delta`.
6. MIP must let panel_exp validate post-test spend scope, window, geo, and cell alignment.
7. MIP must preserve lineage for all user-uploaded or warehouse-resolved inputs.
8. MIP must **not** ask for spend again if a spend dataset was already provided — confirm/refine mapping and pass the ref.
9. MIP calls panel_exp only when `mip_resolution_status` is `READY_*` (or explicit partial policy) **and** Stage 3 runtime exists.

---

## 15. Trust / claim boundary

| Rule | Detail |
|------|--------|
| MIP explains readiness/blockers | From resolution status and package responses |
| Numeric ROI readiness ≠ claim authorization | panel_exp readiness does not authorize business claims |
| Package claim authorization | `CLAIM_AUTHORIZATION_RUNTIME_001` |
| Business decisions | `TrustReport`, `DecisionSurface`, `RecommendationContract` |
| Budget reallocation asks | Route to `DecisionSurface` / `RecommendationContract` |
| No TrustReport bypass | No promotion to decision-grade without TrustReport path |
| No DecisionSurface bypass | Mix/budget decisions require certified Δμ surface |
| No RecommendationContract bypass | Structured recommendations require contract |

---

## 16. Runtime follow-up plan

### Stage 2 — `MIP_GEOX_READOUT_INPUT_RESOLUTION_RUNTIME_001` (in progress)

| Responsibility |
|----------------|
| Detect GeoX readout intent even when user does not say "readout" |
| Inspect available inputs (session, registry, uploads) |
| Classify uploaded/resolved datasets |
| Infer and request confirmation for mappings |
| Resolve experiment metadata |
| Ask for missing KPI/spend/value inputs |
| Create `GeoXReadoutInputHandoff` |
| Return partial-readout messaging when spend/value missing |

**Stage 2A:** resolver skeleton on declared refs (`resolve_geox_readout_inputs`).

**Stage 2B:** source inspection adapters (`inspect_geox_readout_sources`).

**Stage 2C:** inspection-to-resolution pipeline (`resolve_geox_readout_inputs_with_source_inspection`).

### Stage 3 — `MIP_GEOX_READOUT_PANEL_EXP_INTEGRATION_001` (after panel_exp runtime)

| Responsibility |
|----------------|
| Pass handoff to panel_exp when `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` exists |
| Ingest trusted readout / spend readiness output |
| Register returned artifact |
| Expose MIP-facing readiness / explanation |
| Route decision recommendations through `TrustReport` / `DecisionSurface` / `RecommendationContract` |

**Required panel_exp runtime:** `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001`

---

## 17. Non-goals

This artifact does **not**:

- implement runtime orchestration
- call panel_exp runtime
- create a spend ingestion system
- compute `spend_delta` in MIP
- compute ROI or ROAS in MIP
- duplicate GeoX claim authorization
- authorize business claims or decision recommendations
- bypass `TrustReport`, `DecisionSurface`, or `RecommendationContract`
- modify LLM control-plane docs or contracts
- implement provider/runtime prompt work

---

## 18. Validation flags

See [summary JSON](archives/MIP_GEOX_READOUT_INPUT_REQUIREMENTS_AND_HANDOFF_CONTRACT_001_summary.json).

---

## References

- [REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [TRUST_ARCHITECTURE.md](../architecture/TRUST_ARCHITECTURE.md)
- [MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md](../architecture/MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md)
- GeoX package: `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001` (panel_exp `eb9992a`)
