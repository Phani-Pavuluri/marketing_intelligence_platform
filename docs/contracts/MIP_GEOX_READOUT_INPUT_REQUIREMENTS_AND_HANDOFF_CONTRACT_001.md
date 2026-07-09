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
2. Ask for or resolve required post-test KPI data
3. Optionally ask for post-test spend and value/margin mapping when efficiency metrics are requested
4. Pass typed dataset references, column mappings, and lineage into panel_exp

Without this MIP-side handoff contract, GeoX can only validate and extract spend **after** MIP passes the correct inputs — and MIP risks ad-hoc `spend_delta` or ROI/ROAS calculations that belong in panel_exp.

**This artifact is docs/tests-only.** No runtime orchestration, no panel_exp calls, no spend ingestion system.

---

## 3. Package / MIP ownership split

| Responsibility | MIP owner? | panel_exp owner? | Notes |
|----------------|------------|------------------|-------|
| User request interpretation | yes | no | MIP / orchestration |
| Ask for KPI dataset | yes | no | Required for any readout |
| Ask for spend dataset | yes | no | Only when spend-derived metrics requested |
| Ask for value/margin mapping | yes | no | Only when ROAS/profit ROI requested |
| Resolve warehouse/API/source refs | yes | no | When available |
| Validate KPI schema | no | yes | panel_exp deterministic validation |
| Validate spend schema | no | yes | panel_exp deterministic validation |
| Filter KPI/spend to test window | no | yes | panel_exp |
| Treatment/control assignment join | no | yes | panel_exp |
| Compute counterfactual KPI / `delta_mu` | no | yes | Estimator runtime (`ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001`) |
| Compute spend_delta readiness | no | yes | `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` |
| Assemble trusted readout | no | yes | `TRUSTED_READOUT_REPORT_*` |
| Authorize claims | no | yes (package) | `CLAIM_AUTHORIZATION_RUNTIME_001` |
| TrustReport / user explanation | yes | consumes | MIP interprets returned readiness; does not bypass gates |

**Critical boundary:** MIP must **not** compute `spend_delta` casually. MIP passes dataset references and declared mappings; panel_exp owns derivation, alignment, and readiness.

---

## 4. MIP readout intent detection

MIP classifies user requests into readout intent categories before handoff.

| Intent | Description | Minimum data path |
|--------|-------------|-------------------|
| `READOUT_KPI_ONLY` | Post-test KPI panel / counts without lift inference framing | KPI + experiment metadata |
| `READOUT_WITH_LIFT` | Incremental lift / counterfactual KPI readout | KPI + assignment + dates + design ref |
| `READOUT_WITH_COST_PER` | Cost per incremental unit / media efficiency | KPI + lift path + **post-test spend** |
| `READOUT_WITH_ROAS` | Return on ad spend | KPI + lift path + spend + **revenue/value mapping** |
| `READOUT_WITH_PROFIT_ROI` | Profit ROI | KPI + lift path + spend + **margin/profit mapping** |
| `READOUT_WITH_DECISION_RECOMMENDATION_REQUEST` | Budget reallocation / production decision | Route to `RecommendationContract` / `DecisionSurface` / `TrustReport` — **not** raw GeoX readout |
| `READOUT_UNCLEAR_METRIC_REQUEST` | Ambiguous metric ask | Clarify intent before handoff |

### Routing rules

1. **KPI-only / lift** requires KPI data, experiment metadata, assignment, and date windows.
2. **Cost-per** requires KPI path **plus** post-test spend evidence aligned to experiment geos and test window.
3. **ROAS** requires incremental revenue or explicit revenue mapping **plus** spend evidence.
4. **Profit ROI** requires margin/profit mapping **plus** spend evidence.
5. **Decision recommendation requests** (`"should we reallocate budget?"`, `"what should we spend next quarter?"`) must route through `RecommendationContract`, `DecisionSurface`, and `TrustReport` gates — not direct GeoX readout invocation.
6. MIP must **not** require spend for plain increment/lift readout unless the selected readout template explicitly requires efficiency metrics.

---

## 5. Required MIP inputs for any GeoX readout

These fields are required before MIP may create a `GeoXReadoutInputHandoff` for any readout intent (except blocked/unclear states).

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
| `estimator/inference identity` | optional | User may specify; otherwise package resolves from design/readout plan |

MIP resolves references; panel_exp validates schema and alignment.

---

## 6. Conditional MIP inputs for spend-derived metrics

Required when user intent is `READOUT_WITH_COST_PER`, `READOUT_WITH_ROAS`, `READOUT_WITH_PROFIT_ROI`, or user asks for cost-per, ROI, ROAS, media efficiency, payback, business value, or similar efficiency metrics.

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
| `spend scope` | yes | e.g. test geos only, campaign scope |
| `spend window` | yes | Must cover post-test readout window |
| `baseline/BAU spend definition` | when available | User-declared; panel_exp validates |
| `planned spend or counterfactual spend reference` | when available | **Not** substituted for observed post-test spend |

MIP must **not** convert planning `required_spend_delta` into observed post-test `spend_delta`. Planning spend profiling (`GEO_KPI_SPEND_DATA_PROFILER_001`, `SPEND_REQUIREMENT_AND_MANIPULATION_FEASIBILITY_DIAGNOSTICS_001`) is pre-test; readout spend is post-test and package-owned.

---

## 7. Conditional MIP inputs for value/margin mapping

Required when user intent is `READOUT_WITH_ROAS` or `READOUT_WITH_PROFIT_ROI`, or when KPI is not already revenue/profit denominated.

| Field | Required | Notes |
|-------|----------|-------|
| `value_per_incremental_kpi` | conditional | When single scalar mapping declared |
| `revenue mapping source` | for ROAS | Lineage required |
| `margin/profit mapping source` | for profit ROI | Lineage required |
| `currency` | yes | Consistent with spend |
| `value window` | yes | Must be compatible with KPI window |
| `compatibility with KPI window` | yes | MIP declares; panel_exp validates |
| `source lineage` | yes | User upload, finance ref, or declared assumption |

MIP collects and passes mappings; panel_exp validates compatibility and applies in readout assembly.

---

## 8. MIP missing-input prompts

Canonical user-facing messages when handoff is blocked. Wording may be adapted for UI; semantics are fixed.

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

### Unclear metric request

> Please clarify whether you need incremental lift only, cost-per efficiency, ROAS, or profit ROI so I can request the right datasets.

### Decision recommendation misrouted

> Budget reallocation and production spend decisions require a governed recommendation path. I can help with GeoX readout metrics first, then route certified outputs through decision review.

---

## 9. Typed handoff object

**Future contract:** `GeoXReadoutInputHandoff` — conceptual MIP object passed to panel_exp after input resolution.

| Field | Type (conceptual) | Description |
|-------|-------------------|-------------|
| `request_id` | `str` | Stable MIP request identifier |
| `user_request` | `str` | Documentation metadata — not used for package branching |
| `readout_intent` | `ReadoutIntent` | One of §4 categories |
| `experiment_id` | `str` | Experiment identifier |
| `design_artifact_ref` | `ArtifactReference` | Design provenance |
| `assignment_artifact_ref` | `ArtifactReference` | Assignment provenance |
| `kpi_dataset_ref` | `DataSourceRef` | KPI panel or warehouse/API ref |
| `kpi_column_mapping` | `ColumnMapping` | Date, geo, metric bindings |
| `spend_dataset_ref_optional` | `DataSourceRef \| null` | Present when efficiency metrics requested |
| `spend_column_mapping_optional` | `ColumnMapping \| null` | Spend column bindings |
| `spend_baseline_definition_optional` | `str \| null` | User-declared BAU/baseline semantics |
| `value_mapping_optional` | `ValueMappingRef \| null` | Revenue/margin mapping when required |
| `requested_metrics` | `list[str]` | Declared metric asks (lift, cost_per, roas, profit_roi, …) |
| `missing_inputs` | `list[str]` | Typed missing field IDs |
| `mip_resolution_status` | `MipResolutionStatus` | One of §10 |
| `panel_exp_target_contract` | `str` | `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001` |
| `panel_exp_expected_runtime` | `str` | `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001` |
| `lineage` | `dict` | Source refs for all user-resolved inputs |
| `warnings` | `list[str]` | Non-blocking resolution warnings |

**Handoff invariant:** MIP passes references and mappings only. No embedded `spend_delta`, ROI, ROAS, or lift numeric outputs in the handoff object.

---

## 10. MIP resolution statuses

| Status | Meaning |
|--------|---------|
| `READY_FOR_GEOX_READOUT` | All required inputs for requested intent present |
| `READY_FOR_KPI_ONLY_READOUT` | KPI path complete; efficiency metrics not requested |
| `READY_FOR_LIFT_ONLY_READOUT` | Lift path complete; spend/value not required |
| `BLOCKED_MISSING_KPI_DATA` | KPI dataset or mapping missing |
| `BLOCKED_MISSING_EXPERIMENT_METADATA` | experiment_id or design ref missing |
| `BLOCKED_MISSING_ASSIGNMENT` | Treatment/control/cell assignment missing |
| `BLOCKED_MISSING_DATES` | Test or post-period windows missing |
| `BLOCKED_MISSING_SPEND_FOR_EFFICIENCY` | Spend required for cost-per/ROI/ROAS ask |
| `BLOCKED_MISSING_VALUE_MAPPING_FOR_ROAS` | Revenue mapping missing for ROAS |
| `BLOCKED_MISSING_MARGIN_MAPPING_FOR_PROFIT_ROI` | Margin mapping missing for profit ROI |
| `BLOCKED_UNCLEAR_USER_INTENT` | Cannot classify readout intent |
| `BLOCKED_NO_GEOX_RUNTIME_AVAILABLE` | Package runtime not wired (future gate) |
| `PARTIAL_READOUT_ALLOWED` | Lift/KPI readout possible; efficiency metrics blocked pending spend/value |

---

## 11. MIP-to-panel_exp rules

1. MIP may pass raw dataset refs and column mappings.
2. MIP may pass upstream spend evidence refs when available (platform exports, finance feeds).
3. MIP may pass user-provided baseline/BAU spend definitions with lineage.
4. MIP must **not** silently infer `spend_delta` without lineage.
5. MIP must **not** convert planning `required_spend_delta` into observed post-test `spend_delta`.
6. MIP must let panel_exp validate post-test spend scope, window, geo, and cell alignment.
7. MIP must preserve lineage for all user-uploaded or warehouse-resolved inputs.
8. MIP calls panel_exp only when `mip_resolution_status` is a `READY_*` state (or explicit partial handoff policy for `PARTIAL_READOUT_ALLOWED`).
9. Estimator execution remains package-owned (`ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001`); estimator-to-readout mapping via `estimator_readout_adapter_001.py`.

---

## 12. Trust / claim boundary

| Rule | Detail |
|------|--------|
| MIP explains readiness/blockers | User-facing messaging from resolution status and package readiness responses |
| Numeric ROI readiness ≠ claim authorization | Spend/ROI **readiness** from panel_exp does not authorize business claims in MIP |
| Package claim authorization | `CLAIM_AUTHORIZATION_RUNTIME_001` in panel_exp |
| Business decisions | `TrustReport`, `DecisionSurface`, `RecommendationContract` govern promotion and recommendations |
| Budget reallocation asks | Route to `DecisionSurface` / `RecommendationContract` — not raw GeoX readout |
| No TrustReport bypass | MIP cannot promote readout outputs to decision-grade without TrustReport path |
| No DecisionSurface bypass | Mix/budget decisions require certified Δμ surface |
| No RecommendationContract bypass | Structured recommendations require recommendation contract |

---

## 13. Runtime follow-up plan

**Next MIP runtime artifact:** `MIP_GEOX_READOUT_INPUT_RESOLUTION_RUNTIME_001`

| Responsibility | Owner |
|----------------|-------|
| Detect GeoX readout intent | MIP runtime |
| Inspect available inputs (session, registry, uploads) | MIP runtime |
| Ask for missing KPI/spend/value inputs | MIP runtime |
| Create `GeoXReadoutInputHandoff` | MIP runtime |
| Call panel_exp only after required inputs present | MIP runtime |
| Return partial-readout messaging when spend/value missing | MIP runtime |

**Required panel_exp runtime:** `GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001`

Package-side sequencing (already owned in panel_exp):

- `TRUSTED_READOUT_REPORT_*` — final report assembly
- `ESTIMATOR_INFERENCE_EXECUTION_RUNTIME_001` — estimator execution
- `estimator_readout_adapter_001.py` — estimator-to-readout mapping
- `CLAIM_AUTHORIZATION_RUNTIME_001` — claim authorization

---

## 14. Non-goals

This artifact does **not**:

- implement runtime orchestration
- call panel_exp runtime
- create a spend ingestion system
- compute `spend_delta` in MIP
- compute ROI or ROAS in MIP
- duplicate GeoX claim authorization
- authorize business claims or decision recommendations
- bypass `TrustReport`
- bypass `DecisionSurface`
- bypass `RecommendationContract`

---

## 15. Validation flags

See [summary JSON](archives/MIP_GEOX_READOUT_INPUT_REQUIREMENTS_AND_HANDOFF_CONTRACT_001_summary.json).

---

## References

- [REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md) — MIP ↔ panel_exp sibling integration
- [TRUST_ARCHITECTURE.md](../architecture/TRUST_ARCHITECTURE.md) — TrustReport tiers
- [MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md](../architecture/MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md) — adapter boundaries
- GeoX package: `GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001` (panel_exp `eb9992a`)
