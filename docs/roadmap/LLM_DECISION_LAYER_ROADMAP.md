# LLM Decision Layer Roadmap

Phased plan for the LLM Decision Layer and local-first product experience. Aligns with platform roadmap Phase 7+ but details LLM-specific delivery.

## 1. Roadmap summary

Delivery order: **document → deterministic safety → intake/feasibility → readiness → config drafts → local demo app → MMM dashboard/report → measurement gaps → adapter orchestration → scenario workbench → governed recommendations → hosted mode**.

No autonomous agents or production decision automation in early phases.

## 2. Current status

**Phase 0 (done):** Vision, roadmap, and local-first deployment strategy documented.

**Phase 1 (done):** Deterministic LLM safety and explanation context in `mip.llm`.

**Phase 2 (done):** Deterministic business objective intake, data requirement catalog, declared availability profiles, and feasibility evaluation in `mip.workflows.intake`.

**Phase 3 (done):** Deterministic dataset profiling from records, structural readiness checks, and `DataReadinessReport` in `mip.workflows.readiness`, with optional integration to `ObjectiveFeasibilityReport`.

**Phase 4 (done):** Deterministic `MMMConfigDraft` and `GeoXConfigDraft` generation in `mip.workflows.configs` from objective, feasibility, and readiness artifacts. No engine execution.

**Phase 5A (done):** Local deterministic workflow orchestrator in `mip.workflows.orchestrator` via `run_local_workflow()` returning `WorkflowRunSummary`. No UI, CLI, LLM, or engine execution.

**Phase 5B (done):** Local CLI demo runner in `mip.cli.demo` via `mip-demo` reading JSON input and printing/saving governed summaries. No Streamlit, LLM, or engine execution.

**Phase 5C (done):** Deterministic `MockLLMProvider` in `mip.llm.providers` explaining `WorkflowRunSummary` via `mip.llm.explanations`. No real LLM APIs, Streamlit, or engine execution.

**Phase 5D (done):** Thin Streamlit shell in `mip.app.streamlit_app` via `mip-app` over `run_local_workflow()` and `MockLLMProvider`. No new workflow logic, real LLM APIs, or engine execution.

**Phase 6A (done):** Adapter interface contracts in `mip.adapters` for MMM and GeoX input/output bundles. No engine imports, execution, or model estimates.

**Phase 6B (done):** Adapter placeholder governance wiring in `mip.adapters.governance` into fixtures, gates, `TrustReport`, and registry paths. No engine execution.

**Phase 6C (done):** MMM fixture dashboard/report demo in `mip.reports.mmm_fixture` with Streamlit integration. Governed placeholders only; no model execution.

**Platform prerequisites (largely done):** contracts, gates, `TrustReport` assembly, evidence registry, calibration audit, model calibration readiness.

**Not started:** real engine orchestration, real LLM providers (Ollama/cloud).

## 3. Current agreed defaults

| Area | Default |
|------|---------|
| Demo domain | SaaS/subscription marketing |
| Initial workflow | MMM channel ROI + calibration readiness + TrustReport + dashboard/report |
| Initial UI | Local Streamlit app |
| LLM backend | Provider-agnostic; `MockLLMProvider` first |
| Local LLM | Ollama or similar after deterministic contracts |
| Cloud LLM | Optional later |
| Execution | No autonomous agents initially |
| Reports | HTML first, Markdown second, PDF later |
| Data policy | User-provided data and controls; external control fetch deferred |
| Dashboard | MMM-focused: TrustReport, diagnostics, calibration/evidence placeholders |
| GeoX UI | After MMM-focused demo |

## 4. Phase 0: Documentation and scope lock

**Deliver:** This roadmap, [LLM_DECISION_LAYER_VISION.md](../architecture/LLM_DECISION_LAYER_VISION.md), [LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md](../architecture/LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md).

**Exit:** Requirements and boundaries agreed; no LLM implementation yet.

## 5. Phase 1: Deterministic safety and explanation context

**Deliver:**

- Intent classification (workflow vs. question vs. unsafe)
- Risk classification
- `TrustReport` explanation context builder
- Allowed/blocked action lists
- No real LLM API calls

**Future code:** `WorkflowIntent`, `IntentRiskLevel`, `IntentClassification`, `LLMExplanationContext`, `context_from_trust_report`.

**Exit:** Deterministic tests for explanation templates and blocked intents.

## 6. Phase 2: Business objective intake and data requirement framework

**Status: implemented** in `mip.workflows.intake`.

**Deliver:**

- Catalog mapping objective → KPI / controls / grain
- Feasibility check from declared available data profile
- Fallback when objective unsupported by available fields
- Follow-up intake questions for missing fields

**Implemented:** `BusinessObjective`, `BusinessObjectiveType`, `ObjectiveDataRequirement`, `DataAvailabilityProfile`, `ObjectiveFeasibilityReport`, `evaluate_objective_feasibility`, `recommended_next_questions`.

**Exit:** SaaS demo objectives covered with deterministic feasibility responses. Achieved for declared-field profiles; upload inference deferred to Phase 3.

## 7. Phase 3: Data readiness and workflow feasibility

**Status: implemented** in `mip.workflows.readiness`.

**Deliver:**

- `DatasetProfile` inference from in-memory records
- Structural readiness diagnostics (rows, date field, grain, history, missingness, breakdowns)
- `DataReadinessReport` with block/warn/pass paths
- Integration with `ObjectiveFeasibilityReport` via `build_readiness_from_records`

**Implemented:** `DatasetProfile`, `profile_from_records`, `profile_to_availability`, `run_readiness_checks`, `DataReadinessReport`, `build_data_readiness_report`, `build_readiness_from_records`.

**Exit:** Block/warn/pass paths tested without engines. Statistical model diagnostics (collinearity, sparsity) deferred.

## 8. Phase 4: Config drafting for MMM and GeoX

**Status: implemented** in `mip.workflows.configs`.

**Deliver:**

- `MMMConfigDraft` and `GeoXConfigDraft` schemas
- `ConfigDraftValidationReport` and `DraftConfigStatus`
- `draft_mmm_config`, `draft_geox_config`, `draft_config_for_objective`
- No engine execution

**Implemented:** governed drafts with production eligibility flags, warnings, blocking reasons, and deterministic `generated_marker`.

**Exit:** Draft + validate round-trip tests; configs blocked when feasibility or readiness is blocked.

## 9. Phase 5A: Local workflow orchestrator

**Status: implemented** in `mip.workflows.orchestrator`.

**Deliver:**

- `run_local_workflow(objective, records)` end-to-end pipeline
- `WorkflowRunSummary` with profile, feasibility, readiness, config draft, status, warnings, blockers, next questions/fixes, narrative summary
- No UI, CLI, LLM, or engine execution

**Exit:** Deterministic local demo backbone ready for CLI runner (Phase 5B).

## 10. Phase 5B: Local CLI demo runner

**Status: implemented** in `mip.cli.demo`.

**Deliver:**

- `load_demo_input`, `run_demo_from_file`, `format_workflow_summary`
- `mip-demo` console script reading JSON objective + records
- Optional `-o/--output` to save formatted summary
- No Streamlit, LLM, or engine execution

**Exit:** Stable command surface for local demos and future Streamlit shell.

## 11. Phase 5C: MockLLM conversational explanation wrapper

**Status: implemented** in `mip.llm.providers` and `mip.llm.explanations`.

**Deliver:**

- `LLMProviderName`, `LLMProviderResponse`, `MockLLMProvider`
- `explain_workflow_summary`, `explain_blockers`, `explain_next_steps`
- Deterministic conversational text from `WorkflowRunSummary` fields only
- Execution disclaimer and forbidden-phrase safety checks
- No cloud, Ollama, or engine execution

**Exit:** Conversational explanation over orchestrator output without real LLM APIs.

## 12. Phase 5D: Streamlit shell

**Status: implemented** in `mip.app.streamlit_app`.

**Deliver:**

- `parse_json_input`, `run_streamlit_workflow_from_json`, `summary_sections`, `format_status_badge`
- `mip-app` console script for local Streamlit demo
- Paste/upload JSON, run workflow on button click, render summary + mock explanation
- No new workflow logic, real LLM APIs, or engine execution

**Exit:** Browser-based local demo over deterministic workflow stack.

## 13. Phase 6A: Adapter interface contracts

**Status: implemented** in `mip.adapters`.

**Deliver:**

- `AdapterRunStatus`, `AdapterRunKind`, `AdapterInputBundle`, `AdapterOutputBundle`, `AdapterValidationReport`
- `build_mmm_adapter_input`, `build_geox_adapter_input`, `validate_adapter_output`
- Governed placeholders only; blocked drafts cannot build executable input
- No engine imports, execution, or model estimates

**Exit:** Stable adapter-shaped contracts for fixture tests and future engine wiring.

## 14. Phase 6B: Adapter fixture governance wiring

**Status: implemented** in `mip.adapters.governance`.

**Deliver:**

- `adapter_output_to_experiment_evidence`, `adapter_output_to_decision_surface`
- `trust_report_for_adapter_output`, `register_adapter_output`
- GeoX placeholders → evidence registry + gates + TrustReport
- MMM placeholders → DecisionSurface gate + TrustReport (registry path for surfaces deferred)
- Blocked/failed outputs → blocked TrustReport without decision-ready registration

**Exit:** Adapter placeholders enter the MIP trust spine without engine execution.

## 15. Phase 6C: MMM fixture dashboard/report demo

**Status: implemented** in `mip.reports.mmm_fixture` and `mip.app.streamlit_app`.

**Deliver:**

- `build_mmm_fixture_report`, `mmm_fixture_report_sections`, safety assertions
- Streamlit MMM Fixture Governance Demo section
- Workflow → MMM config → adapter placeholders → DecisionSurface fixture → TrustReport
- Clear placeholder labels and missing production requirements list
- No model execution, ROI/lift claims, or budget recommendations

**Exit:** Product-facing governed MMM demo shape without engine connection.

## 16. Phase 7A: Workflow run manifest and agentic governance roadmap

**Status: implemented** in `mip.orchestration`.

**Deliver:**

- `WorkflowPlan`, `WorkflowRunManifest`, step/action/approval contracts
- Deterministic builders: `build_plan_from_workflow_summary`, `build_manifest_from_workflow_summary`, `build_manifest_with_mmm_fixture`
- `assert_safe_workflow_manifest` — rejects forbidden causal/model/agent claims
- [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](../architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md)

**Not in scope:** LangGraph, autonomous agents, real LLM planning, engine execution, budget actions.

**Exit:** Durable workflow lineage for future planner/router; manifests clearly marked `deterministic_local_no_agent`.

## 17. Phase 7B: Governed planner/router

**Status: implemented** in `mip.orchestration.router` and Streamlit display section.

**Deliver:**

- `PlannerDecision`, `PlannerRoute`, `route_next_actions`, `planner_route_from_summary`
- `planner_route_with_mmm_fixture`, `assert_safe_planner_route`, `format_planner_route_for_display`
- Streamlit **Governed Planner / Next Safe Actions** panel (display-only)

**Not in scope:** LangGraph, autonomous agents, real LLM planning, engine execution, automatic approval.

**Exit:** Safe next actions are explicit, auditable, and blocked when unsafe; `agentic_planning_enabled` remains `false`.

## 18. Phase 7C: Human approval checkpoints

**Status: implemented** in `mip.orchestration.approvals` and Streamlit display section.

**Deliver:**

- `ApprovalRequest`, `ApprovalCheckpoint`, `ApprovalDecision`, `apply_approval_decision`
- `create_approval_request`, `enforce_approval_for_route`, `checkpoint_for_action`
- Streamlit **Human Approval Checkpoints** panel (display-only)

**Not in scope:** automatic approval, external approval systems, auth/RBAC, persistence, execution behind gates.

**Exit:** Approval state is explicit and auditable; `blocked_until_approved` enforced in router output.

## 19. Phase 8A: Fixture engine orchestration through adapters

**Status: implemented** in `mip.orchestration.engine_fixtures` and Streamlit display section.

**Deliver:**

- `FixtureEngineRunResult`, `orchestrate_mmm_fixture_engine`, `orchestrate_geox_fixture_engine`
- Manifest → planner/router → approval checkpoints → adapter fixtures → governance artifacts → TrustReport
- Required labels: `fixture_engine_orchestration_only`, `not_real_engine_execution`
- Streamlit **Fixture Engine Orchestration** panel (display-only)

**Not in scope:** real MMM/GeoX package imports, model training, ROI/lift claims, automatic approval.

**Exit:** Governed fixture engine path proven end-to-end without real engine execution.

## 19b. Phase 8B: Pinned sibling-repo fixture adapter integration

**Status: implemented** in `mip.adapters.sibling_fixtures`, committed fixture JSON under `tests/fixtures/sibling_exports/`, and Streamlit **Pinned Sibling-Repo Fixture Import** panel (display-only).

**Deliver:**

- `SiblingFixtureExport`, `load_sibling_fixture_export`, `sibling_fixture_to_adapter_output`
- `validate_sibling_fixture_export`, `trust_report_for_sibling_fixture`, `register_sibling_fixture_export`
- Pinned JSON → `AdapterOutputBundle` → governance artifact → `TrustReport` / registry
- Required labels: `pinned_sibling_repo_fixture_only`, `not_live_engine_execution`, `not_real_model_result`, `diagnostic_only`, `not_decision_ready`

**Not in scope:** real mmm/panel_exp imports, subprocess execution, model training, ROI/lift claims, live repo connection.

**Exit:** Sibling-repo export shape validated and wired through existing adapter governance without live engines.

## 19c. Phase 8C: Read-only sibling export hooks

**Status: implemented** in `mip.adapters.sibling_export_hooks` and Streamlit **Read-Only Sibling Export Hook** panel (display-only).

**Deliver:**

- `SiblingExportDirectoryRef`, `SiblingExportDiscoveryResult`, `discover_sibling_export_files`
- `load_sibling_exports_from_directory`, `register_sibling_exports_from_directory`
- Explicit directory → JSON discovery → Phase 8B schema validation → adapter governance path
- Required labels: `readonly_sibling_export_hook_only`, `static_export_file_only`, `not_live_engine_execution`

**Not in scope:** sibling Python imports, subprocess, file watching, model training, ROI/lift claims.

**Exit:** Static export directories can be scanned and imported read-only without executing sibling code.

## 19d. Phase 8D: Sibling repo compatibility registry

**Status: implemented** in `mip.adapters.sibling_compatibility` and Streamlit **Sibling Repo Compatibility** panel (display-only).

**Deliver:**

- `SiblingRepoExportConfig`, `SiblingRepoCompatibilityReport`, `SiblingRepoCompatibilityRegistry`
- `check_sibling_repo_compatibility`, `build_sibling_repo_compatibility_registry`
- `compatibility_report_to_directory_ref`, `register_exports_for_compatible_repo`
- Config → path resolution → Phase 8C discovery → Phase 8B validation → adapter governance
- Required labels: `sibling_repo_compatibility_check_only`, `readonly_export_contract_only`

**Not in scope:** sibling Python imports, subprocess, live engine execution, ROI/lift claims.

**Exit:** MIP can verify where sibling exports should be read from and whether they are compatible before import.

## 19e. Phase 8E: Local sibling export path wiring

**Status: implemented** in `mip.adapters.local_sibling_paths` and Streamlit **Local Sibling Export Paths** panel (display-only).

**Deliver:**

- `LocalSiblingRepoPathDefaults`, `LocalSiblingPathRegistryResult`, `build_local_sibling_compatibility_registry`
- Default paths for local `mmm` and `panel_exp` export directories (`integrations/mip/exports`)
- `register_compatible_local_sibling_exports` through Phase 8D/8C/8B governance path
- Required labels: `local_sibling_export_path_wiring_only`, `readonly_export_contract_only`

**Not in scope:** sibling Python imports, subprocess, live engine execution, ROI/lift claims.

**Exit:** Local sibling export directories can be wired and validated read-only without executing sibling code.

## 19f. Phase 8F: Sibling-side export producer specifications

**Status: implemented** in `docs/integrations/` and `mip.adapters.sibling_producer_specs`.

**Deliver:**

- `MIP_SIBLING_EXPORT_PRODUCER_SPEC.md`, `MMM_MIP_EXPORT_PRODUCER_SPEC.md`, `PANEL_EXP_MIP_EXPORT_PRODUCER_SPEC.md`
- Minimal valid producer examples under `tests/fixtures/sibling_exports/`
- `expected_export_directory_for_source_repo`, `required_producer_labels`, `assert_valid_producer_spec_example`

**Not in scope:** Poetry path dependencies, sibling Python imports, subprocess, live engine execution.

**Exit:** Canonical producer contract documented; sibling repos can implement JSON writers to `integrations/mip/exports/`. Read-only consumer bridge (8B–8E) complete. Live engine execution remains blocked.

## 19h. Semantic and decision-readiness tracks (S1–S12)

**Status: documented** in [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md). **No runtime implementation.**

Beyond governance ingestion and platform completion, MIP needs metric/estimand registries, scope alignment, business action ontology, decision review packets, explanation templates, red-team prompts, export completeness scoring, source-of-truth policy, failure-mode catalog, and package release gates.

**Key decision:** Structurally valid exports are not sufficient for decision guidance—semantic completeness (metric, estimand, scope, usage policy, `TrustReport`, evidence readiness, approval) is required.

**Ownership:** MIP owns semantic control plane; sibling repos tag exports with `metric_id`, `estimand_id`, scope metadata, and diagnostic codes.

## 19i. Critical invariants, golden scenarios, and artifact selection (G1–G20)

**Status: documented** in [PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](./PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md). **No runtime implementation.**

Covers golden scenarios (G1–G2), conformance suite (G3), severity normalization (G5), no-silent-upgrade (G6), and **artifact selection + ambiguity policies (G11–G20)**: temporal selection, scope/metric/estimand ambiguity, comparability gates, claim-level governance, counterfactual eligibility, freshness decomposition, and missing-vs-zero-effect distinctions.

**Key invariant:** Governance-valid ≠ answer-valid. The LLM must not select artifacts by registry availability alone.

**Next implementation:** Phase 8G/8H with G11–G20 as design constraints—not more roadmap docs.

## 19j. Conversational intake and data handoff (I1–I15)

**Status: documented** in [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md). **No runtime implementation.**

Product/workflow roadmap from LLM-guided conversation → structured intake session → data source selection (upload/connect/local/production) → profiling → readiness report → config/refresh request → sibling export handoff.

**Key framing:** LLM is intake guide, not validation authority. Manifest is intake source of truth; readiness report is compatibility source of truth.

**First implementation:** I1–I3 (`MMMIntakeSession`, `IntakePlan`, `RequiredDataAsset`)—before upload/connect UI.

## 20. Phase 6: MMM-focused dashboard/report demo (full product)

**Deliver:**

- Channel ROI and response curve views
- Data diagnostics panel
- TrustReport panel
- Calibration/evidence placeholder panel
- HTML report export
- Follow-up Q&A over structured artifacts (MockLLM or rules)

Fixture-based MMM artifacts allowed if **clearly labeled demo fixtures**.

**Exit:** End-to-end local demo without real MMM repo required.

## 21. Phase 7: Measurement gap and experiment opportunity layer

**Deliver:**

- Formal surfacing of MMM measurement gaps
- `MeasurementRecommendation` / `ExperimentOpportunity` artifacts
- Dashboard panel + LLM explanation of why experiment needed

**Future concepts:** `MeasurementGapReport`.

**Exit:** Gap → recommendation → TrustReport → UI path demonstrated.

## 22. Phase 8: Engine orchestration through adapters

**Deliver:**

- MMM and GeoX via `mip.adapters.*`
- No private engine imports
- Register outputs in `EvidenceRegistry`
- `TrustReport` from gate outcomes

**Exit:** Real or pinned engine outputs pass contract + gate tests.

## 22. Phase 9: Scenario workbench

**Deliver:**

- Dashboard scenario controls (sliders, bounds, objectives, risk mode)
- Scenario trust/eligibility labels
- Diagnostic vs. decision-ready separation

**Future concepts:** `ScenarioRequest`, `ScenarioResult`, `ScenarioComparison`, `ScenarioEligibility`.

**Exit:** Scenario exploration with tier enforcement.

## 23. Phase 10: Governed recommendations and approval workflow

**Deliver:**

- `RecommendationContract` generation
- Human approval workflow
- Production export eligibility
- Blocked/research-only safeguards

**Exit:** No decision-grade export without approval record.

## 24. Phase 11: Hosted/team mode

**Deliver (later):**

- FastAPI backend
- Persistent artifact store
- Auth and team dashboards
- Optional cloud deployment and cloud LLM

**Exit:** Multi-user pilot; not required for initial local demo.

## 25. Future: Within-channel tactical optimization

Deferred scope:

- MTA-like diagnostics, platform data
- Campaign/audience/creative/keyword recommendations
- Experiment-calibrated attribution, tactical signals
- No immediate implementation

## 26. Deferred / non-goals

- Autonomous budget execution
- Ad-platform bidding
- LLM-as-estimator
- Raw experiment → MMM without `CalibrationSignal`
- Hiding blocked tiers in narrative or UI
- Production recommendations without human approval where policy requires

## 27. Open questions

- Streamlit vs. FastAPI timing for Phase 5–6
- When to introduce real Ollama vs. keep MockLLM through Phase 7
- Single vs. multi-domain intake catalogs at launch
- Approval workflow integration (in-app vs. external)

## Related documents

- [LLM_DECISION_LAYER_VISION.md](../architecture/LLM_DECISION_LAYER_VISION.md)
- [LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md](./LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md)
- [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
- [PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](./PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md)
- [LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md](../architecture/LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md)
- [ROADMAP.md](./ROADMAP.md)
