# Stage A.3 Advisory Readiness Intake Adapter Plan 001

## 1. Title and status

| Field | Value |
|-------|-------|
| **Title** | Stage A.3 Advisory Readiness Intake Adapter Plan 001 |
| **Status** | Accepted adapter planning direction |
| **Type** | Fixture adapter / deterministic workflow mapping plan |
| **Base commit** | `4cf58c2` — calibration report builder/export helpers merged (PR #38) |
| **Date** | 2026-05-28 |
| **Scope** | Docs/planning only — **no advisory, readiness, intake, or governance adapter implementation in this phase** |

**Hard boundaries (unchanged):** No MMM/GeoX execution, no LLM providers, no production ingestion, no new FastAPI routes, no Streamlit behavior changes, no unsupported causal/ROI/power/MDE/matched-market claims. MIP remains the **control plane**, not the statistical engine.

---

## 2. Why this plan exists

Stage A.3 **calibration** fixture→workflow mapping is implemented because calibration fixtures embed `evidence` and `requirement` fields that align directly with `CalibrationEvidenceInput`, `CalibrationMappingRequirement`, and `map_evidence_to_calibration_signal`. The mapping is unambiguous and fail-closed.

**Advisory**, **readiness**, and **intake** fixtures use different shapes:

| Area | Fixture shape | Workflow input shape | Gap |
|------|---------------|----------------------|-----|
| Cold-start advisory | Business-profile JSON (`domain`, `objective`, `monthly_budget_usd`) | `ColdStartBusinessProfile` (`business_type`, `primary_objective` enum, `monthly_budget` string) | Field rename + enum mapping |
| Readiness | Governed **summary** JSON (`structural_support`, `missing_for_*`) | `CommonIntakeWorkbench` (built from demo tabular rows via `demo_profiling`) | No raw rows in fixtures |
| Intake/routing | Narrative JSON (`user_question`, `expected_safe_route`) | `MeasurementIntakeSession` (typed enums, grains, scopes) | No session builder exists |
| Governance | Educational examples array | No deterministic unsupported-claim workflow | Test/guidance only |

Without explicit input/output rules, Cursor agents and future implementers will **invent** schemas, guess workbench contents, or run workflows with incompatible inputs. This plan removes that ambiguity **before** any new adapter code ships.

**Relationship:** This plan narrows [MIP Report, Adapter, and Agent Contract Plan 001](MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md) §4 Stage A.3 from a broad sketch into concrete mapping tables, readiness verdicts, golden paths #1–#2, and acceptance criteria for the next implementation phase.

---

## 3. Existing implemented baseline

### Stage A fixtures

- **Location:** `examples/fixtures/stage_a/`
- **Manifest:** `examples/fixtures/stage_a/manifest.json` — 15 `fixture_id` entries across business profiles, readiness, calibration, intake, and governance
- **Properties:** All fixtures declare `synthetic: true` and `requires_mmm_or_geox_engine: false`

### Stage A.2 fixture loaders

- **Module:** `mip.examples.stage_a_fixtures`
- **Capabilities:** `list_stage_a_fixtures()`, `load_stage_a_fixture(fixture_id)`, manifest metadata access
- **Rule for all future adapters:** Load fixtures **only** through Stage A.2 helpers — never parse fixture paths ad hoc

### Deterministic report envelope contracts

- **Module:** `mip.contracts.deterministic_report`
- **Schema version:** `deterministic_report_v1`
- **Model:** `DeterministicReportEnvelope` with `ReportType`, `EvidenceMode`, `GovernanceStatus`, `ArtifactReference`, `ReportFinding`
- **Report types reserved for this plan:** `cold_start_advisory`, `readiness_assessment`, `intake_routing`, `governance_blocked_claim`

### Stage A.3 calibration adapter (implemented)

- **Module:** `mip.examples.stage_a_adapters`
- **Supported fixture IDs:** `experiment_readout_valid`, `experiment_readout_missing_se`, `experiment_readout_metric_mismatch`
- **Workflow:** `map_evidence_to_calibration_signal`
- **Helpers:** `build_calibration_input_from_stage_a_fixture`, `run_calibration_mapping_for_stage_a_fixture`
- **Golden paths #3–#5:** valid → `candidate`; missing SE → `needs_more_data`; metric mismatch → `incompatible`

### Calibration report builder/export helpers (implemented)

- **Modules:** `mip.reports.calibration_reports`, `mip.reports.deterministic_reports`
- **Helpers:** `build_calibration_report_from_stage_a_fixture`, `export_calibration_report_from_stage_a_fixture`, `report_to_json`, `write_report_json`
- **Pattern for future adapters:** Adapter runs workflow → envelope builder wraps output → optional JSON export

---

## 4. Fixture inventory by workflow area

### 4.1 Business profiles (cold-start advisory)

| fixture_id | Path | Intended workflow | Loader | Adapter | Missing mapping details |
|------------|------|-------------------|--------|---------|-------------------------|
| `local_fitness_studio` | `business_profiles/local_fitness_studio.json` | `build_cold_start_advisory_plan` | ✓ | ✗ | `domain` → `business_type`; `objective` → `ColdStartMediaObjective`; `monthly_budget_usd` → `monthly_budget` string; `tracking_state` → `existing_tracking` bool |
| `dtc_skincare_brand` | `business_profiles/dtc_skincare_brand.json` | same | ✓ | ✗ | `business_model` → `b2b_or_b2c`; `current_channels` → `organic_channels_available`; no traffic profile in fixture |
| `b2b_saas_hr_platform` | `business_profiles/b2b_saas_hr_platform.json` | same | ✓ | ✗ | B2B `objective` → enum; `sales_cycle_length` not in fixture (optional field) |

**Reference implementation pattern:** `app/demo_fixtures.resolve_advisory_demo_inputs` manually maps `ADVISORY_SAMPLE_LOCAL_FITNESS` and `ADVISORY_SAMPLE_DTC_SKINCARE` to `build_cold_start_business_profile` — adapters should follow the same field semantics, keyed by `fixture_id` not `sample_key`.

### 4.2 Readiness summaries

| fixture_id | Path | Intended workflow | Loader | Adapter | Missing mapping details |
|------------|------|-------------------|--------|---------|-------------------------|
| `national_weekly_channel_summary` | `readiness/national_weekly_channel_summary.json` | `build_workflow_readiness_reports` | ✓ | ✗ | Summary → `CommonIntakeWorkbench` bridge via `demo_profiling.DEMO_DATASET_NATIONAL_MEDIA_OUTCOME` (documented interim) or new `StageAReadinessSummary` → workbench contract |
| `geo_week_media_outcome_summary` | `readiness/geo_week_media_outcome_summary.json` | same (GeoX design route) | ✓ | ✗ | Bridge via `DEMO_DATASET_DMA_WEEK`; fixture claims **structural** GeoX readiness only — no power/MDE |
| `incomplete_missing_geo` | `readiness/incomplete_missing_geo.json` | same (blocked GeoX) | ✓ | ✗ | National-only summary; expect GeoX route blocked; national MMM may be structurally plausible |
| `incomplete_missing_outcome` | `readiness/incomplete_missing_outcome.json` | same (blocked measurement) | ✓ | ✗ | Spend-only; all measurement routes blocked |

**Critical constraint:** Readiness fixtures are **governed summaries**, not tabular uploads. Adapters must **not** fabricate row-level data. Acceptable strategies (pick one at implementation):

1. **Interim bridge (recommended first):** Map `summary_type` → `demo_profiling` dataset key → `build_common_intake_workbench` from synthetic demo rows; envelope `workflow_payload` cites both fixture summary and demo dataset provenance.
2. **Contract extension (later):** Add `build_minimal_workbench_from_readiness_summary(summary: dict)` that constructs a workbench from declared grains/channels/outcomes only, with explicit `synthetic_workbench: true` metadata.

### 4.3 Intake/routing examples

| fixture_id | Path | Intended workflow | Loader | Adapter | Missing mapping details |
|------------|------|-------------------|--------|---------|-------------------------|
| `beginner_sales_growth_question` | `intake/beginner_sales_growth_question.json` | `recommend_intake_path` | ✓ | ✗ | `user_question` → `business_question`; `expected_safe_route` → session `workflow_kind` / `intended_use` enums |
| `mmm_readiness_question` | `intake/mmm_readiness_question.json` | same | ✓ | ✗ | `available_data` → grains/scopes; route to MMM diagnostic readiness, not MMM execution |
| `geox_readiness_question` | `intake/geox_readiness_question.json` | same | ✓ | ✗ | Geo experiment design intent → `MeasurementWorkflowKind.GEOX` |
| `calibration_question` | `intake/calibration_question.json` | same | ✓ | ✗ | Experiment evidence intent → `MeasurementWorkflowKind.CALIBRATION_INTAKE` |

**Critical constraint:** Fixtures are **routing stories**, not `MeasurementIntakeSession` payloads. Implementation may use a **two-phase** approach: (a) routing-only envelope from fixture metadata when session fields cannot be inferred; (b) full session builder once mapping table is frozen.

### 4.4 Governance unsupported-claim examples

| fixture_id | Path | Intended use | Loader | Adapter | Missing mapping details |
|------------|------|--------------|--------|---------|-------------------------|
| `unsupported_claim_examples` | `governance/unsupported_claim_examples.json` | Education / tests | ✓ | ✗ | **No runtime workflow** — see §8 |

### 4.5 Calibration (implemented — baseline reference)

| fixture_id | Adapter | Status |
|------------|---------|--------|
| `experiment_readout_valid` | ✓ | `candidate` / MAPPED |
| `experiment_readout_missing_se` | ✓ | `needs_more_data` |
| `experiment_readout_metric_mismatch` | ✓ | `incompatible` |

---

## 5. Cold-start advisory adapter plan

### Future module location

Extend `mip.examples.stage_a_adapters` (same module as calibration) or add `mip.reports.advisory_reports` for envelope builders — **not in this planning phase**.

### Future helper names

| Function | Returns | Purpose |
|----------|---------|---------|
| `list_supported_advisory_fixture_ids()` | `list[str]` | Governed allowlist |
| `build_cold_start_input_from_stage_a_fixture(fixture_id)` | `ColdStartBusinessProfile` | Map fixture → workflow input |
| `run_cold_start_advisory_for_stage_a_fixture(fixture_id)` | `DeterministicReportEnvelope` | Run `build_cold_start_advisory_plan` and wrap envelope |
| `build_cold_start_advisory_report_from_stage_a_fixture(fixture_id)` | `DeterministicReportEnvelope` | Alias for report builder module |
| `export_cold_start_advisory_report_from_stage_a_fixture(fixture_id, output_path)` | `Path` | Local JSON export |

### Supported fixture category

**Business profiles only** — `workflow_area: cold_start_advisory` in manifest.

Allowlist: `local_fitness_studio`, `dtc_skincare_brand`, `b2b_saas_hr_platform`.

Fail closed: any other `fixture_id` raises `StageAAdapterError`.

### Required input fields (from fixture)

| Fixture field | Required | Maps to `ColdStartBusinessProfile` |
|---------------|----------|-------------------------------------|
| `fixture_id` | yes | `profile_id` = `stage-a-{fixture_id}` |
| `domain` | yes | `business_type` (string passthrough or lookup table) |
| `objective` | yes | `primary_objective` (`ColdStartMediaObjective` enum) |
| `geography` | yes | `geography` |
| `monthly_budget_usd` | yes | `monthly_budget` = `"${value}"` string |
| `business_model` | recommended | `b2b_or_b2c` (`b2c_dtc` → `b2c`, `b2b_saas` → `b2b`) |
| `tracking_state` | recommended | `existing_tracking` (see mapping table below) |
| `current_channels` | optional | `organic_channels_available` |
| `known_constraints` | optional | `constraints` |
| — | adapter-generated | `created_at` = UTC now (deterministic override param allowed) |
| — | default | `existing_website` = `True` when `tracking_state` implies website |

### Objective enum mapping (needs source inspection before implementation)

| Fixture `objective` | `ColdStartMediaObjective` |
|---------------------|---------------------------|
| `sales` | `SALES` |
| `lead_generation` | `LEAD_GENERATION` |
| `awareness` | `AWARENESS` |
| `traffic` | `TRAFFIC` |
| unknown / missing | `UNKNOWN` + warning in envelope |

### Tracking state mapping (needs source inspection)

| Fixture `tracking_state` | `existing_website` | `existing_tracking` |
|--------------------------|-------------------|---------------------|
| `website_without_full_paid_tracking` | `True` | `False` |
| `website_only_partial_utm` | `True` | `False` |
| `no_website` | `False` | `False` |
| other | `None` | `None` + warning |

### Workflow execution

```text
load_stage_a_fixture(fixture_id)
  → build_cold_start_input_from_stage_a_fixture(fixture_id)
  → build_cold_start_advisory_plan(profile)   # optional traffic_profile=None
  → build_cold_start_advisory_report_envelope(fixture_id, plan)
```

`source_workflow`: `build_cold_start_advisory_plan`

### Expected report envelope

| Field | Value |
|-------|-------|
| `report_type` | `cold_start_advisory` |
| `schema_version` | `deterministic_report_v1` |
| `evidence_mode` | `business_profile_only` |
| `governance_status` | `advisory_only` |
| `workflow_payload` | Serialized `ColdStartAdvisoryPlan` fields (status, evidence_mode, claim guards) |

### Required missing-data outputs

When profile is sparse (`infer_advisory_evidence_mode` → `general_knowledge_only`):

- `missing_data` entries for: target audience detail, margin/AOV, tracking setup, conversion definition
- `recommended_next_steps` from plan: tracking checklist, starter measurement plan, learning agenda items

### Forbidden outputs

Must **not** appear in envelope or `workflow_payload`:

- ROI estimates, causal lift, optimal mix, budget optimization
- MMM/GeoX fitted outputs, response curves, channel ROI ranking
- Power/MDE, matched markets, treatment assignment
- `TrustReport` authorization or decision recommendations
- `DecisionSurface`, optimizer, scenario-planner outputs

### Unclear fields (inspect before implementation)

- `b2b_saas_hr_platform.json` — confirm `objective` and `business_model` values against enum mapping
- Whether `primary_conversion` should map to a contract field (currently **no** — omit or add to `constraints` as note)
- Traffic-informed advisory (`DATA_INFORMED_ADVISORY`) — **out of scope** for Stage A business-profile fixtures unless a traffic fixture is added later

---

## 6. Readiness adapter plan

### Future helper names

| Function | Returns |
|----------|---------|
| `list_supported_readiness_fixture_ids()` | `list[str]` |
| `build_readiness_input_from_stage_a_fixture(fixture_id)` | `CommonIntakeWorkbench` |
| `run_readiness_assessment_for_stage_a_fixture(fixture_id)` | `DeterministicReportEnvelope` |
| `build_readiness_report_from_stage_a_fixture(fixture_id)` | `DeterministicReportEnvelope` |
| `export_readiness_report_from_stage_a_fixture(fixture_id, output_path)` | `Path` |

### Supported fixture category

**Readiness only** — `workflow_area: readiness_assessment`.

Allowlist: `national_weekly_channel_summary`, `geo_week_media_outcome_summary`, `incomplete_missing_geo`, `incomplete_missing_outcome`.

### Interim workbench bridge (recommended)

| fixture_id | `summary_type` | Demo dataset key (`demo_profiling`) | Expected routes exercised |
|------------|----------------|-------------------------------------|---------------------------|
| `national_weekly_channel_summary` | `national_weekly_media_outcome` | `DEMO_DATASET_NATIONAL_MEDIA_OUTCOME` | National MMM; GeoX blocked (no DMA) |
| `geo_week_media_outcome_summary` | `dma_week_media_outcome` | `DEMO_DATASET_DMA_WEEK` | Geo-level MMM + GeoX design diagnostics |
| `incomplete_missing_geo` | `national_weekly_only` | `DEMO_DATASET_NATIONAL_MEDIA_OUTCOME` | National MMM plausible; GeoX blocked |
| `incomplete_missing_outcome` | `media_spend_only` | **No full bridge** — adapter returns governed error or minimal blocked workbench | All measurement blocked |

**Language caution:** Reports may state **structural readiness** or **blocked at readiness layer**. They must **not** claim GeoX power/MDE results, matched-market selection, or treatment assignment unless the deterministic workflow explicitly produces only structural checks (current `build_geox_design_readiness_report` is structural/diagnostic).

### Per-fixture expected governance status

| fixture_id | Expected aggregate `governance_status` | Rationale |
|------------|----------------------------------------|-----------|
| `national_weekly_channel_summary` | `candidate` or `diagnostic_only` | National MMM structurally plausible; GeoX blocked |
| `geo_week_media_outcome_summary` | `candidate` or `diagnostic_only` | DMA-week structural plausibility pending sparsity review |
| `incomplete_missing_geo` | `blocked` or `needs_more_data` | GeoX blocked; national may pass |
| `incomplete_missing_outcome` | `blocked` | Missing outcome time series |

Map from `BaseWorkflowReadinessReport.status` aggregates — mirror calibration `_STATUS_TO_GOVERNANCE` pattern in implementation.

### Expected report envelope

| Field | Value |
|-------|-------|
| `report_type` | `readiness_assessment` |
| `evidence_mode` | `readiness_only` |
| `source_workflow` | `build_workflow_readiness_reports` |
| `workflow_payload` | List of readiness report summaries (MMM, GeoX design, calibration signal, decision review as applicable) |
| `missing_data` | Union of `missing_for_*` from fixture + workflow `missing_fields` |
| `blocked_claims` | `fitted_mmm_outputs`, `channel_roi_ranking`, `response_curves`, `causal_lift`, `power_mde_results`, `matched_market_selection` |

### Missing-data checklist behavior

Envelope `missing_data` must include fixture-declared gaps:

- `national_weekly_channel_summary`: `missing_for_geox` items (DMA-level media/outcome)
- `geo_week_media_outcome_summary`: `missing_for_calibration` if present
- `incomplete_missing_geo`: `blocking_reasons` from fixture
- `incomplete_missing_outcome`: `missing_outcome_metric_time_series`

### Forbidden outputs

Same as §5 forbidden list, plus:

- Claiming MMM model fit or channel coefficients
- Claiming GeoX design completion, power analysis, or matched markets
- Promoting readiness to decision evidence

### Implementation verdict drivers

- **needs_contract_update** if minimal workbench-from-summary is chosen over demo_profiling bridge
- **needs_source_inspection** for exact status enum mapping from `BaseWorkflowReadinessReport` to `GovernanceStatus`

---

## 7. Intake/routing adapter plan

### Future helper names

| Function | Returns |
|----------|---------|
| `list_supported_intake_fixture_ids()` | `list[str]` |
| `build_intake_input_from_stage_a_fixture(fixture_id)` | `MeasurementIntakeSession` or routing context `dict[str, Any]` |
| `run_intake_routing_for_stage_a_fixture(fixture_id)` | `DeterministicReportEnvelope` |
| `build_intake_routing_report_from_stage_a_fixture(fixture_id)` | `DeterministicReportEnvelope` |

### Supported fixture category

**Intake only** — `workflow_area: intake_routing`.

Allowlist: `beginner_sales_growth_question`, `mmm_readiness_question`, `geox_readiness_question`, `calibration_question`.

### Per-fixture routing intent

| fixture_id | `user_question` (summary) | Target session shape | `expected_safe_route` (fixture) |
|------------|---------------------------|----------------------|--------------------------------|
| `beginner_sales_growth_question` | Increase sales — where to start? | `workflow_kind=ADVISORY` or cold-start path | `cold_start_advisory` |
| `mmm_readiness_question` | Weekly spend/sales — national MMM? | `workflow_kind=MMM`, `intended_use=DIAGNOSTIC_READINESS` | `national_mmm_diagnostic_readiness` |
| `geox_readiness_question` | Geo experiment feasibility | `workflow_kind=GEOX`, `intended_use=GEO_EXPERIMENT_DESIGN` | `geox_design_readiness` |
| `calibration_question` | Experiment readout for MMM | `workflow_kind=CALIBRATION_INTAKE` | `calibration_mapping` |

### Session field mapping (draft — needs_source_inspection)

| Fixture field | `MeasurementIntakeSession` field |
|---------------|----------------------------------|
| `user_question` | `business_question` |
| `fixture_id` | `session_id` = `stage-a-intake-{fixture_id}` |
| `objective` | informs `desired_output` or `workflow_kind` selection |
| `available_data` | informs `time_grain`, `geo_grain`, `warnings` |
| — | `created_at` = UTC now |
| — | `intended_use`, `workflow_kind` from routing table above |

### Expected report envelope

| Field | Value |
|-------|-------|
| `report_type` | `intake_routing` |
| `evidence_mode` | `routing_only` |
| `governance_status` | `diagnostic_only` or `advisory_only` (beginner path) |
| `source_workflow` | `recommend_intake_path` |
| `workflow_payload` | `IntakePathRecommendation` summary |
| `recommended_next_steps` | `allowed_next_steps` from recommendation |
| `blocked_claims` | Fixture `blocked_claims` + recommendation `blocked_next_steps` |

### Expected output semantics

**Safe routing / data needs / blocked claims only** — not measurement conclusions:

- Route beginner questions to cold-start advisory or tracking setup
- Route MMM questions to readiness assessment path, **not** MMM execution
- Route GeoX questions to design readiness, **not** GeoX inference
- Route calibration questions to calibration mapping governance

### Forbidden outputs

- Fitted MMM outputs, response curves, channel ROI
- GeoX power/MDE, matched markets, lift estimates
- Optimizer or decision authorization
- Contradicting fixture `blocked_claims`

### Two-phase implementation recommendation

| Phase | Behavior |
|-------|----------|
| **Phase A** | Routing-only envelope built from fixture `expected_safe_route` + `blocked_claims` without calling `recommend_intake_path` if session mapping incomplete |
| **Phase B** | Full `build_intake_input_from_stage_a_fixture` → `recommend_intake_path` once enum mapping is tested |

---

## 8. Governance unsupported-claim adapter plan

### Recommendation: test/guidance fixtures first

`unsupported_claim_examples` should **not** be a runtime workflow input in Stage A.3.

| Role | Rationale |
|------|-----------|
| **Test fixtures** | Assert docs, adapters, and validators block forbidden claim language |
| **Guidance fixtures** | Educate notebook/demo authors on safe alternatives |
| **Future LLM guardrail examples** | Input to explanation-layer blocked-claim tests (deferred) |
| **Not adapter inputs** | No `build_governance_input_from_stage_a_fixture` until a deterministic `validate_unsupported_claim_request` workflow exists |

### Optional future report type

If a deterministic validator is added later:

- `report_type`: `governance_blocked_claim`
- `evidence_mode`: `educational_only`
- `governance_status`: `blocked`
- Envelope lists each `examples[]` entry as a `ReportFinding` with `safe_alternative`

**Do not implement** `GovernanceBlockedClaimReport` generator in the next adapter phase unless an existing workflow is identified.

### Test usage (allowed now)

- Architecture/docs tests reference fixture for forbidden-output vocabulary
- Golden-path negative tests: user request strings from fixture must not appear as allowed claims in advisory/readiness/intake envelopes

---

## 9. Report envelope mapping

All advisory, readiness, and intake adapters must produce `DeterministicReportEnvelope` consistent with calibration reports.

### Field population rules

| Field | Advisory | Readiness | Intake |
|-------|----------|-----------|--------|
| `report_id` | `stage-a-advisory-{fixture_id}-{timestamp_or_hash}` | `stage-a-readiness-{fixture_id}-...` | `stage-a-intake-{fixture_id}-...` |
| `report_type` | `cold_start_advisory` | `readiness_assessment` | `intake_routing` |
| `schema_version` | `deterministic_report_v1` | same | same |
| `source_workflow` | `build_cold_start_advisory_plan` | `build_workflow_readiness_reports` | `recommend_intake_path` |
| `source_input_ref` | `ArtifactReference` with `artifact_type=stage_a_fixture`, `source_fixture_id_or_payload_ref=fixture_id` | same pattern | same pattern |
| `evidence_mode` | `business_profile_only` | `readiness_only` | `routing_only` |
| `governance_status` | `advisory_only` | From readiness status aggregate | `diagnostic_only` or `advisory_only` |
| `summary` | One-line plan status + evidence mode | One-line readiness aggregate | One-line recommended path |
| `findings` | Plan warnings, blocking reasons, hypotheses (as `ReportFinding`) | Per-report blocking/missing fields | Recommendation warnings/blockers |
| `recommended_next_steps` | Plan allowed next steps | Safe data collection / reassessment | `allowed_next_steps` from recommendation |
| `missing_data` | Tracking/data gaps from plan | Fixture `missing_for_*` + workflow missing fields | `required_next_questions` + data gaps |
| `blocked_claims` | Standard P5b forbidden claims | Fixture + workflow blocked claims | Fixture `blocked_claims` |
| `allowed_downstream_uses` | `advisory_hypothesis`, `tracking_setup`, `learning_agenda` | `readiness_reassessment`, `data_collection` | `route_to_advisory`, `route_to_readiness`, `route_to_calibration_intake` |
| `forbidden_downstream_uses` | `decision_recommendation`, `budget_optimization`, `mmm_execution`, `causal_certification`, `roi_proof` | same + `fitted_mmm_outputs`, `geox_inference` | same |
| `artifact_refs` | `[source_input_ref, optional plan ref]` | `[source_input_ref, workbench ref if bridged]` | `[source_input_ref, session ref]` |
| `workflow_payload` | `ColdStartAdvisoryPlan` dict | Readiness report list summary | `IntakePathRecommendation` dict |

### Provenance requirements (match calibration)

- `source_input_ref.source_commit_or_version` = `default_package_version_label()` or explicit package version
- Preserve `synthetic: true` in metadata
- `content_hash_optional` may hash canonical fixture JSON from loader

### Default forbidden downstream (reuse calibration constants)

Align with `_DEFAULT_FORBIDDEN_DOWNSTREAM` and `_DEFAULT_BLOCKED_CLAIMS` in `stage_a_adapters.py` unless workflow-specific extensions are documented.

---

## 10. Golden paths #1–#2

### Golden path #1 — Beginner business profile → cold-start advisory

| Attribute | Value |
|-----------|-------|
| **Source fixture ID** | `local_fitness_studio` |
| **Expected adapter** | `build_cold_start_input_from_stage_a_fixture` → `run_cold_start_advisory_for_stage_a_fixture` |
| **Expected workflow** | `build_cold_start_advisory_plan` |
| **Expected report type** | `cold_start_advisory` |
| **Expected governance status** | `advisory_only` |
| **Expected missing-data fields** | Tracking setup, conversion definition, paid media history (from plan checklists) |
| **Expected blocked claims** | `causal_lift`, `roi_proof`, `budget_optimization`, `decision_authorization` |
| **Forbidden outputs** | ROI, lift, MMM/GeoX execution, optimizer, DecisionSurface |

**Acceptance test (future):** Load fixture → run adapter → assert envelope fields; scan payload for forbidden fragments.

### Golden path #2 — Partial weekly media data → readiness report

| Attribute | Value |
|-----------|-------|
| **Source fixture ID** | `national_weekly_channel_summary` |
| **Expected adapter** | `build_readiness_input_from_stage_a_fixture` → `run_readiness_assessment_for_stage_a_fixture` |
| **Expected workflow** | `build_workflow_readiness_reports` (via national demo workbench bridge) |
| **Expected report type** | `readiness_assessment` |
| **Expected governance status** | `candidate` or `diagnostic_only` (national MMM structurally plausible) |
| **Expected missing-data fields** | `dma_level_outcome`, `dma_level_media`, `geo_treatment_history` (from fixture `missing_for_geox`) |
| **Expected blocked claims** | `fitted_mmm_outputs`, `channel_roi_ranking`, `response_curves`, `causal_lift`, `power_mde_results` |
| **Forbidden outputs** | MMM fit, response curves, GeoX power/MDE, matched markets, causal lift |

**Acceptance test (future):** Assert GeoX route blocked in `workflow_payload`; assert national MMM readiness not blocked; no forbidden fields in envelope.

---

## 11. Implementation readiness verdict

| Adapter | Verdict | Rationale |
|---------|---------|-----------|
| **Calibration** | `ready_to_implement` (done) | Fixture embeds workflow inputs; adapter merged |
| **Cold-start advisory** | `ready_to_implement` | Field mapping table defined; `app/demo_fixtures` proves pattern; enum mapping needs minor source inspection |
| **Readiness** | `needs_contract_update` | Fixture summaries ≠ workbench; interim `demo_profiling` bridge documented but provenance dual-source must be specified in code |
| **Intake/routing** | `needs_source_inspection` | Session enum mapping from narrative fixtures requires inspection of `IntakeIntendedUse`, `MeasurementWorkflowKind`, `recommend_intake_path` branches |
| **Governance unsupported-claim** | `blocked` (for adapter) | No deterministic workflow; keep test/guidance only |

### Recommendation

1. **Implement cold-start advisory adapter first** — mapping is clearest; golden path #1 unblocks notebooks/demos.
2. **Implement readiness adapter second** — after choosing bridge vs minimal-workbench contract and documenting provenance in envelope.
3. **Implement intake adapter third** — Phase A routing-only acceptable until session builder is frozen.
4. **Keep `unsupported_claim_examples` test-only** unless deterministic validator workflow is added.

---

## 12. Acceptance criteria for future implementation

Future adapter PRs must satisfy:

- [ ] Adapters **fail closed** for wrong fixture categories (`StageAAdapterError` with fixture ID and supported list)
- [ ] Adapters preserve **source fixture provenance** in `source_input_ref` and `artifact_refs`
- [ ] Adapters use **Stage A.2 loaders** exclusively (`load_stage_a_fixture`)
- [ ] Adapters produce **`DeterministicReportEnvelope`** validated against `deterministic_report_v1`
- [ ] Envelopes include **`missing_data`** and **`blocked_claims`** (may be empty only when workflow confirms none)
- [ ] Adapters do **not** create ROI, causal lift, power/MDE, matched markets, treatment assignments, response curves, optimizer outputs, scenario plans, or DecisionSurface outputs
- [ ] Adapters do **not** call MMM/GeoX engines or `run_local_workflow` engine paths
- [ ] Tests scan envelope + `workflow_payload` for forbidden field names and claim fragments (mirror calibration tests)
- [ ] `list_supported_*_fixture_ids()` and `list_supported_fixture_workflow_mappings()` document allowlists
- [ ] No change to FastAPI service routes, Streamlit runtime, or LLM providers
- [ ] Golden paths #1–#2 have dedicated tests when respective adapters merge

---

## 13. Roadmap sequencing

Recommended sequence after this plan merges:

| Order | Item | Type |
|-------|------|------|
| 1 | **This adapter plan** (Stage A.3 advisory/readiness/intake) | Docs ✓ |
| 2 | Cold-start advisory adapter implementation | Code (if mapping confirmed) |
| 3 | Readiness adapter implementation | Code (after workbench bridge decision) |
| 4 | Intake adapter implementation | Code (routing-first acceptable) |
| 5 | Golden paths #1–#2 acceptance tests | Tests |
| 6 | Deterministic notebook plan | Docs |
| 7 | Notebook implementation | Code |
| 8 | Landing-page guided demo binding plan | Docs |
| 9 | LLM explanation contracts | Docs |

**Parallel allowed:** Advisory envelope builder can proceed while readiness bridge contract is finalized, but **do not** merge readiness adapter without documented provenance for demo-row bridge.

**Explicit blocks:**

- Notebooks before golden paths #1–#2 tests pass
- LLM runtime before explanation response contract
- Stage B engine visuals before certified outputs

---

## References

- [MIP Report, Adapter, and Agent Contract Plan 001](MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md)
- [Stage A fixtures README](../../examples/fixtures/stage_a/README.md)
- `mip.examples.stage_a_fixtures` — Stage A.2 loaders
- `mip.examples.stage_a_adapters` — Stage A.3 calibration adapter
- `mip.reports.calibration_reports` — calibration report builder pattern
- `mip.contracts.deterministic_report` — envelope contracts
- `mip.workflows.intake.advisory` — `build_cold_start_advisory_plan`
- `mip.workflows.intake.readiness` — `build_workflow_readiness_reports`
- `mip.workflows.intake.recommendation` — `recommend_intake_path`
- `app/demo_fixtures.resolve_advisory_demo_inputs` — manual advisory mapping reference
