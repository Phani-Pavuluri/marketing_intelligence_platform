# Conversational Intake and Data Handoff Roadmap

Product and workflow roadmap for the full user path from **LLM-guided conversation** to **production-grade MMM/GeoX data intake**, validation, readiness reporting, and governed export handoff.

Complements:

- [LLM Decision Layer Roadmap](./LLM_DECISION_LAYER_ROADMAP.md) — deterministic intake (Phase 2–3), workflow orchestrator (5A), Streamlit shell (5D)
- [LLM Reasoning and Model Guidance Roadmap](./LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md) — explanation payloads, usage policy (8G–8N)
- [Platform Semantic and Decision Readiness Roadmap](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md) — metric/estimand/scope registries (S1–S12)
- [Platform Critical Invariants and Golden Scenarios](./PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md) — artifact selection (G11–G20)
- [MIP Sibling Export Producer Spec](../integrations/MIP_SIBLING_EXPORT_PRODUCER_SPEC.md) — static export handoff (8F)

## 1. Product workflow (end-to-end)

```text
LLM gathers business goals
  → LLM recommends modeling / measurement path
  → MIP creates structured intake session
  → user confirms scope, KPI, intended use, data needs
  → user chooses data source mode (Streamlit upload, local folder, governed table, sibling export)
  → MIP profiles and validates data compatibility
  → MIP produces readiness report
  → MIP drafts config / refresh request
  → MMM or GeoX executes externally
  → MIP imports governed export and TrustReport
```

## 2. Required framing

### 2.1 LLM is the intake guide, not the intake mechanism

The **LLM conversation is an intake guide**, not the intake mechanism itself.

The LLM may:

- Gather business intent
- Explain requirements
- Recommend a modeling path
- Draft an intake plan

**MIP must validate** uploaded or connected data through contracts, profiling, semantic mapping, readiness gates, and audit trails before any model config or refresh request is considered usable.

### 2.2 Demo vs production intake

| Mode | Acceptable for | Requirements |
|------|----------------|--------------|
| **CSV upload in chat or Streamlit** | Demos, local analyst workflows, debugging | Sandbox/demo mode labels |
| **Production-grade intake** | Governed decision support | Manifest-driven, source-referenced, versioned, validated, auditable |

### 2.3 Ownership

| Responsibility | Owner |
|----------------|-------|
| Intake orchestration, data compatibility validation, semantic mapping, readiness reporting, refresh request governance | **MIP** |
| Model or experiment execution | **MMM** / **panel_exp / GeoX** |
| Conversational guidance only (must not certify data or model readiness) | **LLM** |

**Shared boundary:** contract conformance plus `TrustReport`-governed export handoff. MIP does not execute models; sibling engines do not bypass readiness gates.

### 2.4 Hard boundaries (unchanged)

This addendum is **documentation only**. No runtime code, Streamlit changes, connector implementation, model execution, optimizer execution, sibling imports, subprocesses, LLM provider calls, or production recommendations.

## 3. Required platform decisions

1. **The LLM conversation is an intake guide, not a data validation authority.**
2. **Source of truth for intake** is the manifest, not the conversation transcript.
3. **Source of truth for compatibility** is the readiness report, not the LLM summary.
4. **Source of truth for execution** is the sibling engine export, not the intake plan.
5. **Production intake** must use governed source references or approved manifests—not ad hoc chat uploads.
6. **Uploaded files** are allowed for demo, sandbox, local analyst workflow, and debugging, but not automatically for production decision support.
7. **Experiment evidence** must enter MMM through `CalibrationSignal`, not loose documents or free-text summaries.

## 4. Intake and data-handoff tracks

### Track I1 — Conversational Intake Session

**Why:** Capture user goals in structured form before any file or table intake.

**Future session objects:** `MMMIntakeSession` · `GeoXIntakeSession` · `MeasurementIntakeSession`

**Required fields:**

`session_id` · `business_question` · `intended_use` · `decision_context` · `measurement_goal` · `candidate_package` · `candidate_workflow` · `metric_id` · `estimand_id` · `time_grain` · `geo_grain` · `channel_scope` · `platform_scope` · `campaign_scope` · `product_scope` · `audience_scope` · `reporting_window` · `desired_output` · `unresolved_questions` · `recommended_next_step`

**Allowed `intended_use` values:**

`diagnostic_only` · `calibrated_mmm` · `geo_experiment_design` · `geo_experiment_readout` · `decision_surface_candidate` · `decision_review_packet` · `optimizer_candidate` · `historical_explanation` · `current_performance_summary`

**Rules:**

- LLM must collect enough context before recommending a package path.
- LLM must distinguish MMM, GeoX, calibration/evidence integration, and decision-review workflows.
- LLM must not recommend production decisioning when required evidence is unavailable.

**Example:**

> User: “I want to understand Meta and Display impact on US conversions.”  
> LLM: “Recommended starting path: weekly national diagnostic MMM. Geo-level MMM requires geo-level KPI and media data. Decision-support MMM requires calibration and certified decision surface.”

**Ownership:** **MIP** owns session contracts; **LLM** drafts session fields for user confirmation.

**P1 status:** Implemented in `mip.contracts.intake` and `mip.workflows.intake.recommendation`.

---

### Track I2 — Modeling / Measurement Path Recommendation

**Why:** Route users to the right workflow before data collection begins.

**Candidate paths:**

`national_diagnostic_mmm` · `geo_level_mmm` · `calibrated_mmm` · `experiment_calibration_intake` · `geo_experiment_design` · `geo_experiment_readout` · `decision_surface_certification` · `decision_review_packet` · `blocked_needs_more_data`

**Recommendation inputs:** business goal · available data grain · KPI type · channel scope · decision urgency · need for causal claim · need for budget recommendation · presence of experiment evidence · freshness needs

**Recommendation outputs:** `recommended_path` · `why_this_path` · `why_other_paths_are_blocked` · `required_data_assets` · `optional_data_assets` · `minimum_readiness_needed` · `next_user_action`

**Rules:**

- Causal lift without experiment/calibration → diagnostic or experiment-design workflow.
- Budget recommendation → certified decision surface + optimizer governance; otherwise block.
- National weekly KPI/spend only → do not recommend geo-level MMM.
- Experiment readout for MMM calibration → route through `CalibrationSignal`.

**Ownership:** **MIP** owns path taxonomy and gating; **LLM** proposes paths from structured session.

**P1 status:** `IntakePathRecommendation` and `recommend_intake_path()` implemented deterministically.

---

### Track I3 — Intake Plan + Required Data Assets

**Why:** Users need a checklist before upload/connect—not ad hoc file drops.

**Future objects:** `IntakePlan` · `RequiredDataAsset` · `OptionalDataAsset` · `DataAssetPurpose`

**Required asset types:**

`outcome_kpi_data` · `media_spend_data` · `media_exposure_data` · `control_data` · `calendar_seasonality_data` · `pricing_promo_data` · `channel_mapping` · `geo_mapping` · `product_mapping` · `metric_mapping` · `calibration_signal_data` · `experiment_export_data` · `model_config_seed`

**Per-asset fields:** `asset_type` · `required_for_paths` · `minimum_grain` · `required_columns` · `optional_columns` · `accepted_source_modes` · `semantic_mapping_needed` · `freshness_requirement` · `blocks_if_missing`

**Readiness examples:**

| Path | Requirements |
|------|--------------|
| Diagnostic national MMM | outcome + media spend required; calendar controls required or warning; channel mapping required; calibration optional |
| Calibrated MMM | all diagnostic + `CalibrationSignal`-compatible evidence; freshness and estimand alignment |
| Decision-support MMM | calibrated + decision surface certification; `TrustReport` non-blocked; approval |

**Ownership:** **MIP** owns asset catalog; builds on Phase 2 `DataRequirement` patterns.

---

### Track I4 — Data Source Mode Selection

**Why:** Different environments need different intake surfaces with the same governance spine.

**Supported modes:**

| Mode | Typical use |
|------|-------------|
| `streamlit_file_upload` | Local demo UI |
| `chat_file_upload` | Conversational demo |
| `local_dropzone_folder` | Repeatable local analyst workflow |
| `local_file_path_manifest` | CLI / scripted local runs |
| `governed_table_reference` | Production table snapshot |
| `warehouse_connection` | Production warehouse read |
| `sibling_repo_static_export` | MMM/GeoX **result** handoff (not raw modeling data) |
| `sample_demo_data` | Onboarding and tests only |

**UI options (future):** Upload files · Connect governed tables · Use local folder · Use sample/demo data · Import sibling export

**Rules:**

- Streamlit/chat upload = sandbox/local/demo modes.
- Governed table / warehouse = production-level modes.
- Sibling static export = result handoff only.
- MIP maps selected mode to `DataSourceRef`.

**Ownership:** **MIP** owns mode taxonomy and `DataSourceRef` mapping.

---

### Track I5 — DataSourceRef + Intake Manifest

**Why:** Reproducible, auditable intake requires manifests—not chat memory.

**Future objects:**

`DataSourceRef` · `TableSourceRef` · `FileSourceRef` · `DropzoneSourceRef` · `UploadedFileSourceRef` · `SiblingExportSourceRef` · `MMMIntakeManifest` · `GeoXIntakeManifest`

**`DataSourceRef` fields:**

`source_id` · `source_mode` · `source_type` · `uri_or_table_ref` · `asset_type` · `schema_version` · `declared_owner` · `declared_grain` · `declared_scope` · `created_at` · `data_snapshot_id` · `checksum_or_version` · `read_only` · `contains_sensitive_data`

**`MMMIntakeManifest` fields:**

`manifest_id` · `session_id` · `business_question` · `intended_use` · `recommended_path` · `metric_id` · `estimand_id` · `time_grain` · `geo_grain` · `reporting_window` · `outcome_source` · `media_source` · `control_source` · `mapping_sources` · `calibration_signal_sources` · `created_by` · `created_at` · `manifest_version` · `approval_status`

**Rules:**

- Manifest is the reproducible source of truth for data intake.
- LLM may draft manifest; user/MIP validation must confirm.
- Production refreshes must be manifest-driven.

**Ownership:** **MIP** owns manifest contracts and validation.

---

### Track I6 — Column Mapping + Semantic Confirmation

**Why:** Uploaded columns must map to canonical semantics (S1–S3) before decision support.

**Future objects:** `ColumnProfile` · `ColumnMappingProposal` · `ColumnMappingConfirmation` · `SemanticMappingReport`

**Mapping dimensions:** date · geo · channel · platform · campaign · product · metric · spend · exposure · control columns · currency · timezone/week definition

**Rules:**

- LLM may propose mappings from column names.
- MIP must require confirmation for ambiguous mappings.
- Metric, channel, geo, product must resolve to canonical registries before decision-support use.
- Do not silently map same-named metrics/channels across systems.

**Example UI copy:**

> Detected `media.csv` columns: `week` → date, `channel` → channel, `spend` → spend, `impressions` → exposure. Please confirm or edit before validation.

**Ownership:** **MIP** owns mapping validation; **LLM** proposes only.

---

### Track I7 — Data Profiling + Compatibility Validation

**Why:** Compatibility is path-specific and contract-driven—not LLM judgment.

**Future objects:** `UploadedFileProfile` · `DataCompatibilityReport` · `DataQualityFinding` · `DataGrainValidationReport` · `ScopeValidationReport` · `FreshnessValidationReport`

**Checks:** required source exists · required columns · date range complete · grain matches path · duplicates · missing values · spend sanity · KPI sanity · channel/geo coverage · scope consistency · currency consistency · week definition · mapping completeness · freshness · leakage warnings · control availability

**Compatibility statuses:**

`compatible` · `compatible_with_warnings` · `needs_mapping_confirmation` · `needs_user_clarification` · `blocked_missing_required_asset` · `blocked_schema_mismatch` · `blocked_grain_mismatch` · `blocked_scope_mismatch` · `blocked_metric_ambiguity` · `blocked_freshness_failure`

**Rules:**

- LLM must not declare data compatible by inspection alone.
- Compatibility is produced by MIP validation.
- Data ready for diagnostic MMM may be blocked for calibrated/decision-support MMM.

**Ownership:** **MIP** owns profiling and compatibility gates; builds on Phase 3 `DataReadinessReport`.

---

### Track I8 — MMM Data Readiness Report

**Why:** Readiness is tied to intended use—not a single global flag.

**Future object:** `MMMDataReadinessReport`

**Fields:** `report_id` · `manifest_id` · `session_id` · `candidate_path` · `readiness_tier` · `compatible_assets` · `missing_assets` · `warnings` · `blocking_reasons` · `metric_status` · `estimand_status` · `scope_status` · `grain_status` · `freshness_status` · `calibration_signal_status` · `recommended_next_action` · `allowed_next_steps` · `blocked_next_steps`

**Readiness tiers:**

`not_ready` · `ready_for_data_profiling_only` · `ready_for_diagnostic_mmm` · `ready_for_calibrated_mmm_candidate` · `ready_for_decision_surface_candidate` · `ready_for_refresh_request` · `blocked`

**Rules:**

- Readiness is path-specific.
- Report must explain what is missing and how to remediate.

**Ownership:** **MIP** owns readiness report; extends existing `DataReadinessReport` / model calibration readiness.

---

### Track I9 — CalibrationSignal Intake Mapping

**Why:** Experiment evidence must not enter MMM as loose text.

**Accepted evidence sources:** GeoX export · CLS export · A/B summary · holdout · replay · manual calibration draft

**Future objects:** `CalibrationSignalIntakeCandidate` · `CalibrationSignalMappingReport` · `CalibrationSignalReadinessReport`

**Required fields:** `source` · `metric_id` · `estimand_id` · `effect_estimate` · `standard_error_or_interval` · `time_window` · `geo_scope` · `channel_scope` · `product_scope` · `causal_validity_status` · `freshness_status` · `allowed_use`

**Rules:**

- Map to `CalibrationSignal` contract—not free text.
- Pass metric, estimand, scope, freshness, and causal validity checks.
- Misaligned evidence may be `TrustReport`-only or blocked from calibration.

**Ownership:** **MIP** owns mapping and gates; **GeoX** provides governed exports.

---

### Track I10 — Streamlit / Local Product Workflow

**Why:** Define the product UX spine from conversation to handoff.

**Future steps:**

1. Conversation Intake  
2. Intake Summary  
3. Recommended Path  
4. Data Source Selection  
5. Upload / Connect / Local Folder  
6. Column Mapping Confirmation  
7. Data Profiling  
8. Data Readiness Report  
9. Config Draft  
10. Refresh Request / Export Import Handoff  

**Future panels:** Business Question · Recommended Workflow · Required Data Checklist · Upload/Connect Data · Column Mapping · Compatibility Findings · Readiness Tier · Missing Data Remediation · Next Safe Action

**Rules:**

- LLM explains panels and guides user.
- UI owns upload/connect/confirm actions.
- MIP owns validation and readiness status.

**Ownership:** **MIP** owns workflow orchestration; extends Phase 5D Streamlit shell.

---

### Track I11 — Production Data Connection Workflow

**Why:** Production intake must be manifest-driven and auditable.

**Flow:**

```text
user selects governed table connection
  → MIP creates TableSourceRef
  → MIP validates schema and access
  → MIP snapshots source version / data_snapshot_id
  → MIP validates semantic mapping
  → MIP creates locked intake manifest
  → MIP produces readiness report
  → approval if required
  → refresh request generated
```

**Production requirements:** source ownership · schema version · `data_snapshot_id` · access policy · PII flag · freshness SLA · lineage · audit log · read-only validation · approval status

**Rules:**

- Production intake must be manifest-driven.
- Production must not rely on raw chat uploads.
- Connectors must not bypass semantic validation or readiness gates.

**Ownership:** **MIP** owns production intake governance.

---

### Track I12 — Config Draft + Refresh Request Handoff

**Why:** Readiness becomes an executable **request**—not MIP execution.

**Future objects:** `MMMConfigDraft` · `GeoXConfigDraft` · `ModelRefreshRequest` · `ExperimentDesignRequest`

**`ModelRefreshRequest` fields:** `request_id` · `manifest_id` · `readiness_report_id` · `intended_use` · `candidate_path` · `model_family` · `data_snapshot_id` · `config_draft_id` · `approval_required` · `approval_status` · `created_at` · `blocked_reasons`

**Rules:**

- Config drafts are not execution.
- Refresh requests are not execution.
- MMM executes refresh externally; GeoX executes design/readout externally.
- MIP produces governed requests and later validates static exports (8F).

**Ownership:** **MIP** owns request contracts; **MMM/GeoX** execute externally.

---

### Track I13 — Conversation-to-Manifest Audit Trail

**Why:** Reconstruct how a user goal became a model request.

**Required lineage:**

`conversation_intake_summary` · `session_id` · `intake_plan_id` · `manifest_id` · `data_source_refs` · `column_mapping_confirmations` · `readiness_report_id` · `config_draft_id` · `refresh_request_id` · `sibling_export_id` · `TrustReport_id` · `LLM_answer_ids`

**Rules:**

- LLM answers about readiness/compatibility must cite readiness report or manifest state.
- Platform must reconstruct full lineage.

**Ownership:** **MIP** owns audit semantics; relates to Track G7 / P9 persistence.

---

### Track I14 — Security / Privacy / File Safety

**Why:** Upload and connection surfaces are security boundaries.

**Rules:**

- No secret-bearing files without redaction policy.
- PII/sensitive-data flag required.
- File size and type limits defined.
- Safe bounded CSV/Excel parsing.
- No symlink following in local/dropzone intake.
- Production connections read-only for validation.
- Raw uploaded data must not go to external LLM providers by default.
- LLM sees profiles/summaries, not unrestricted raw data, unless explicitly allowed.

**Future checks:** `file_type_allowed` · `file_size_allowed` · `schema_safe` · `path_safe` · `no_symlink` · `no_secret_pattern` · `pii_flag` · `read_only_connection` · `audit_event_created`

**Ownership:** **MIP** owns ingestion safety; relates to Track P12 / G12.

---

### Track I15 — Demo / Sandbox / Production Mode Separation

**Why:** Mode must be visible; demo artifacts must not drive production guidance.

| Mode | Behavior |
|------|----------|
| `demo_mode` | Sample data; no production claims |
| `sandbox_mode` | User uploads/local files; diagnostic only unless explicitly governed |
| `production_mode` | Governed table refs, manifests, validation, approvals, audit |

**Rules:**

- Mode visible to user.
- LLM must not use demo/sandbox artifacts for production guidance.
- Production requires manifest, source refs, `data_snapshot_id`, validation, approval where required.

**Ownership:** **MIP** owns mode policy and UI labeling.

## 5. Track summary

| Track | Focus |
|-------|--------|
| I1 | Conversational intake session |
| I2 | Modeling / measurement path recommendation |
| I3 | Intake plan + required data assets |
| I4 | Data source mode selection |
| I5 | DataSourceRef + intake manifest |
| I6 | Column mapping + semantic confirmation |
| I7 | Data profiling + compatibility validation |
| I8 | MMM data readiness report |
| I9 | CalibrationSignal intake mapping |
| I10 | Streamlit / local product workflow |
| I11 | Production data connection workflow |
| I12 | Config draft + refresh request handoff |
| I13 | Conversation-to-manifest audit trail |
| I14 | Security / privacy / file safety |
| I15 | Demo / sandbox / production mode separation |

## 6. Relationship to existing phases

| Existing | Intake roadmap extends |
|----------|------------------------|
| Phase 2 `mip.workflows.intake` | I1 session, I2 path recommendation, I3 assets |
| Phase 3 `mip.workflows.readiness` | I7 profiling, I8 readiness report |
| Phase 4 `mip.workflows.configs` | I12 config draft |
| Phase 5D Streamlit shell | I10 product workflow panels |
| Phase 8F sibling exports | I4 sibling export mode, I12 handoff |
| S1–S3 semantic registries | I6 mapping, I7/I8 validation |
| G11–G20 artifact selection | I2 path gating, I8 tier semantics |

## 7. Next implementation phase

**P1 complete (I1–I2).** First implementation after P1:

1. `IntakePlan` + `RequiredDataAsset` catalog (P2 / I3)

Keep upload/connect UI **separate** until contracts are validated. Then I5 manifest, I6 mapping, I7–I8 validation.

## 8. Related documents

- [LLM_DECISION_LAYER_ROADMAP.md](./LLM_DECISION_LAYER_ROADMAP.md)
- [LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md](./LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md)
- [PLATFORM_COMPLETION_GAPS_ROADMAP.md](./PLATFORM_COMPLETION_GAPS_ROADMAP.md)
- [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](./PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md)
- [REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](../architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md)
- [ROADMAP_EXECUTION_SEQUENCE.md](./ROADMAP_EXECUTION_SEQUENCE.md)
- [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md)
