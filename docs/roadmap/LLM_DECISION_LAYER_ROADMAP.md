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

## 17. Phase 6: MMM-focused dashboard/report demo (full product)

**Deliver:**

- Channel ROI and response curve views
- Data diagnostics panel
- TrustReport panel
- Calibration/evidence placeholder panel
- HTML report export
- Follow-up Q&A over structured artifacts (MockLLM or rules)

Fixture-based MMM artifacts allowed if **clearly labeled demo fixtures**.

**Exit:** End-to-end local demo without real MMM repo required.

## 18. Phase 7: Measurement gap and experiment opportunity layer

**Deliver:**

- Formal surfacing of MMM measurement gaps
- `MeasurementRecommendation` / `ExperimentOpportunity` artifacts
- Dashboard panel + LLM explanation of why experiment needed

**Future concepts:** `MeasurementGapReport`.

**Exit:** Gap → recommendation → TrustReport → UI path demonstrated.

## 19. Phase 8: Engine orchestration through adapters

**Deliver:**

- MMM and GeoX via `mip.adapters.*`
- No private engine imports
- Register outputs in `EvidenceRegistry`
- `TrustReport` from gate outcomes

**Exit:** Real or pinned engine outputs pass contract + gate tests.

## 20. Phase 9: Scenario workbench

**Deliver:**

- Dashboard scenario controls (sliders, bounds, objectives, risk mode)
- Scenario trust/eligibility labels
- Diagnostic vs. decision-ready separation

**Future concepts:** `ScenarioRequest`, `ScenarioResult`, `ScenarioComparison`, `ScenarioEligibility`.

**Exit:** Scenario exploration with tier enforcement.

## 21. Phase 10: Governed recommendations and approval workflow

**Deliver:**

- `RecommendationContract` generation
- Human approval workflow
- Production export eligibility
- Blocked/research-only safeguards

**Exit:** No decision-grade export without approval record.

## 22. Phase 11: Hosted/team mode

**Deliver (later):**

- FastAPI backend
- Persistent artifact store
- Auth and team dashboards
- Optional cloud deployment and cloud LLM

**Exit:** Multi-user pilot; not required for initial local demo.

## 23. Future: Within-channel tactical optimization

Deferred scope:

- MTA-like diagnostics, platform data
- Campaign/audience/creative/keyword recommendations
- Experiment-calibrated attribution, tactical signals
- No immediate implementation

## 24. Deferred / non-goals

- Autonomous budget execution
- Ad-platform bidding
- LLM-as-estimator
- Raw experiment → MMM without `CalibrationSignal`
- Hiding blocked tiers in narrative or UI
- Production recommendations without human approval where policy requires

## 25. Open questions

- Streamlit vs. FastAPI timing for Phase 5–6
- When to introduce real Ollama vs. keep MockLLM through Phase 7
- Single vs. multi-domain intake catalogs at launch
- Approval workflow integration (in-app vs. external)

## Related documents

- [LLM_DECISION_LAYER_VISION.md](../architecture/LLM_DECISION_LAYER_VISION.md)
- [LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md](../architecture/LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md)
- [ROADMAP.md](./ROADMAP.md)
