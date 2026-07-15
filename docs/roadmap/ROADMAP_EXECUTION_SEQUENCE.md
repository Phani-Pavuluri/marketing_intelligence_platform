# Roadmap Execution Sequence

Condensed implementation sequence derived from [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md).

**Current main:** `000273a`
**Immediate next phase:** MIP tool registry + LLM explanation contracts (no LLM runtime yet)

> **Product direction:** [PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001](../product/PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md) — accepted product direction for single-page landing + chat-first UX, guided demos, output previews, and data-needed-by-decision education. [SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001](../product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md) — accepted strategy for MIP-owned synthetic demo fixtures, industry reference schemas, deterministic demo datasets (Stage A), and later real MMM/GeoX-backed visuals (Stage B). Docs-only; does not change current Streamlit runtime.

> **Phase note:** P7–P11 cover product surface (local UI, LLM providers, demo profiling, **agent role contracts**, public demo, FastAPI/Docker, API hardening). Former P9–P16 integer phases shift to **P12–P20** (table-ref, refresh, lifecycle, LLM governance, golden harness, LangGraph, decision packet, optimizer, live gate). LangGraph remains **P17** and must use P8b agent contracts.

## What is already implemented

| Layer | Status |
|-------|--------|
| P1 intake session + path recommendation (I1–I2) | ✓ |
| P2 required data assets + sample schemas (I3) | ✓ |
| P3 DataSourceRef + intake manifest (I5) | ✓ |
| P4 column mapping + semantic confirmation (I6) | ✓ |
| P4b experiment design objective + data requirements (I6b) | ✓ |
| P4c common intake workbench + preliminary profiling (I6c) | ✓ |
| P5 workflow-specific readiness reports (I7–I8) | ✓ |
| P5b general advisory / cold-start planning (I8b) | ✓ |
| P6 CalibrationSignal intake mapping (I9) | ✓ |
| P7 local deterministic Streamlit workflow shell (I10) | ✓ |
| P7b pluggable LLM provider + explanation governance contracts | ✓ |
| P8 local/demo profiling contracts + helpers | ✓ |
| P8b agent role registry + failure/recovery contracts | ✓ |
| P8c canonical Streamlit entrypoint cleanup | ✓ |
| P9 deterministic public demo preparation | ✓ |
| P9 deploy — Streamlit Community Cloud (deterministic) | ✓ |
| P9b public demo deployment record | ✓ |
| Contracts, gates, TrustReport, evidence registry | ✓ |
| LLM Phase 1–5D (safety, intake, readiness, configs, orchestrator, CLI, MockLLM, Streamlit shell) | ✓ |
| Adapters 6A–6C, orchestration 7A–7C, static sibling bridge 8A–8F | ✓ |
| Roadmap docs: 8G–8N, P1–P13, S1–S12, G1–G20, I1–I15 | ✓ documented |
| Product entrypoint / demo experience plan 001 | ✓ documented (accepted direction; implementation deferred) |
| Synthetic demo dataset strategy plan 001 | ✓ documented; **Stage A fixtures + Stage A.2 loaders** (`mip.examples.stage_a_fixtures`) |
| P11 API hardening / service packaging | ✓ implemented (PR #31) |
| P12 SDK / API usage examples 001 | ✓ implemented (PR #32) |
| Agent tooling / roadmap detail audit 001 | ✓ documented — [MIP_AGENT_TOOLING_AND_ROADMAP_IMPLEMENTATION_DETAIL_AUDIT_001.md](../audits/MIP_AGENT_TOOLING_AND_ROADMAP_IMPLEMENTATION_DETAIL_AUDIT_001.md) |
| Report / adapter / agent contract plan 001 | ✓ documented — [MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md](../architecture/MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md) |
| Deterministic report contracts + Stage A.3 calibration adapter | ✓ implemented — `deterministic_report_v1`, golden paths #3–#5 |
| Calibration report builder/export helpers | ✓ implemented — `mip.reports.calibration_reports` |
| Stage A.3 advisory/readiness/intake adapter plan 001 | ✓ documented — [STAGE_A3_ADVISORY_READINESS_INTAKE_ADAPTER_PLAN_001.md](../architecture/STAGE_A3_ADVISORY_READINESS_INTAKE_ADAPTER_PLAN_001.md) |
| Stage A.3 cold-start advisory adapter | ✓ implemented — golden path #1 (`local_fitness_studio`) |
| Agent answerability and fallback contract plan 001 | ✓ documented — [AGENT_ANSWERABILITY_AND_FALLBACK_CONTRACT_PLAN_001.md](../architecture/AGENT_ANSWERABILITY_AND_FALLBACK_CONTRACT_PLAN_001.md) |
| Agent answerability contracts + deterministic evaluator | ✓ implemented — `mip.contracts.agent_answerability`, `mip.agents.answerability`, `mip.workflows.agent.answerability` |
| Agent capability eval fixtures 001 | ✓ implemented — `examples/fixtures/agent_capability_eval`, `mip.evaluation.agent_capability_fixtures` |
| MIP LLM control plane architecture 001 | ✓ documented — [MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md](../architecture/MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md) |
| MIP GeoX readout input handoff contract 001 | ✓ documented — [MIP_GEOX_READOUT_INPUT_REQUIREMENTS_AND_HANDOFF_CONTRACT_001.md](../contracts/MIP_GEOX_READOUT_INPUT_REQUIREMENTS_AND_HANDOFF_CONTRACT_001.md) (3-stage lane: boundary → input resolution → panel_exp integration) |
| MIP GeoX readout input resolution runtime 001A | ✓ implemented — `mip.contracts.geox_readout_input_resolution`, `mip.workflows.geox_readout_input_resolution` (declared refs only; no file parsing; no panel_exp) |
| MIP GeoX readout source inspection adapters 001B | ✓ implemented — `mip.contracts.geox_readout_source_inspection`, `mip.workflows.geox_readout_source_inspection` (metadata inspection; no resolver auto-integration; no panel_exp) |
| MIP GeoX readout input resolution runtime 001C | ✓ implemented — `mip.contracts.geox_readout_input_resolution_pipeline`, `mip.workflows.geox_readout_input_resolution_pipeline` (inspection → enrich → resolve; no panel_exp) |
| MIP GeoX readout panel_exp integration 001A | ✓ implemented — `mip.contracts.geox_panel_exp_integration`, `mip.workflows.geox_panel_exp_integration` (adapter boundary / materialization plan; no panel_exp call) |
| MIP GeoX readout fixture materialization adapter 001 | ✓ implemented — `mip.contracts.geox_fixture_materialization`, `mip.workflows.geox_fixture_materialization` (controlled local CSV fixtures; no panel_exp) |
| MIP GeoX readout panel_exp runtime call 001B | ✓ implemented — `mip.contracts.geox_panel_exp_runtime_call`, `mip.workflows.geox_panel_exp_runtime_call` (fixture-only panel_exp runtime call; optional `panel_exp` sibling dependency; no production loader) |
| MIP GeoX readout result ingestion and explanation 001 | ✓ implemented — `mip.contracts.geox_readout_result_ingestion`, `mip.workflows.geox_readout_result_ingestion` (MIP-facing package artifact explanation; no panel_exp; no metric recomputation) |
| MIP GeoX readout trust routing 001 | ✓ implemented — `mip.contracts.geox_readout_trust_routing`, `mip.workflows.geox_readout_trust_routing` (governance routing metadata; no TrustReport/DecisionSurface/RecommendationContract bypass) |
| MIP method promotion handoff consumer contract 001 | ✓ documented — [MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001.md](../contracts/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001.md) (MIP consumes panel_exp `MethodPromotionGenericAdapterMIPHandoff` as governance context only; no runtime; no DecisionSurface/TrustReport/RecommendationContract authorization) |
| MIP method promotion handoff consumer runtime contract 001 | ✓ documented — [MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001.md](../contracts/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001.md) (typed MIP validator/normalizer contract for handoff → consumer record; runtime implementation deferred; no DecisionSurface/TrustReport/RecommendationContract/planning authorization) |
| MIP method promotion handoff consumer runtime 001 | ✓ implemented — `mip.contracts.method_promotion_handoff_consumer` ([MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001.md](../contracts/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001.md); validator/normalizer only; governance context; no DecisionSurface/TrustReport/RecommendationContract/planning authorization) |
| MIP method promotion handoff consumer runtime application checkpoint 001 | ✓ documented — [MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_APPLICATION_CHECKPOINT_001.md](../contracts/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_APPLICATION_CHECKPOINT_001.md) (runtime stable for routing/answerability contract planning; no integration; no DecisionSurface/TrustReport/RecommendationContract authorization) |
| MIP method promotion handoff routing answerability contract 001 | ✓ documented — [MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_CONTRACT_001.md](../contracts/MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_CONTRACT_001.md) (where consumer records may appear in routing/answerability; governance context only; no runtime integration; no answer eligibility) |
| MIP method promotion handoff routing answerability runtime contract 001 | ✓ documented — [MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_CONTRACT_001.md](../contracts/MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_CONTRACT_001.md) (typed deterministic routing/answerability guard API; runtime implementation deferred; no answer eligibility) |
| MIP method promotion handoff routing answerability runtime 001 | ✓ implemented — `mip.contracts.method_promotion_handoff_routing_answerability` ([MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_001.md](../contracts/MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_001.md); deterministic guard; explain/defer/block only; no LLM; no answer eligibility) |
| MIP method promotion handoff routing answerability runtime application 001 | ✓ implemented — `mip.contracts.method_promotion_handoff_answerability_application` ([MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_APPLICATION_001.md](../contracts/MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_APPLICATION_001.md); narrow validate→guard application path; no LLM; no answer eligibility) |
| MIP roadmap state audit after handoff answerability application 001 | ✓ documented — [MIP_ROADMAP_STATE_AUDIT_AFTER_HANDOFF_ANSWERABILITY_APPLICATION_001.md](MIP_ROADMAP_STATE_AUDIT_AFTER_HANDOFF_ANSWERABILITY_APPLICATION_001.md) (handoff lane safe to pause; next boundary = LLM response boundary audit lane, not another handoff checkpoint) |
| MIP shared uploaded CSV materialization core 001 | ✓ implemented — `mip.contracts.uploaded_csv_materialization`, `mip.workflows.uploaded_csv_materialization` (lane-neutral CSV materialization; GeoX/Planning adapters deferred) |
| MIP GeoX readout uploaded CSV adapter 001 | ✓ implemented — `mip.contracts.geox_uploaded_csv_adapter`, `mip.workflows.geox_uploaded_csv_adapter` (maps shared materialization → GeoX roles / DatasetReference; no CSV re-read) |
| MIP GeoX readout uploaded CSV runtime bridge 001 | ✓ implemented — `mip.contracts.geox_uploaded_csv_runtime_bridge`, `mip.workflows.geox_uploaded_csv_runtime_bridge` (bridges uploaded CSV materialization → package runtime; no CSV re-read; no production loader) |
| MIP Planning/MMM uploaded CSV adapter 001 | ✓ implemented — `mip.contracts.planning_mmm_uploaded_csv_adapter`, `mip.workflows.planning_mmm_uploaded_csv_adapter` (maps shared materialization → Planning/MMM roles / DataSourceRef; no CSV re-read; no model fitting) |
| MIP Planning/MMM uploaded CSV input plan 001 | ✓ implemented — `mip.contracts.planning_mmm_uploaded_csv_input_plan`, `mip.workflows.planning_mmm_uploaded_csv_input_plan` (governed input plan + readiness metadata; no model execution) |
| MIP Planning/MMM workflow readiness from uploaded CSV 001 | ✓ implemented — `mip.contracts.planning_mmm_uploaded_csv_workflow_readiness`, `mip.workflows.planning_mmm_uploaded_csv_workflow_readiness` (evaluates input plan against MMM workflow-readiness gates; no model execution) |
| MIP tabular source reuse contract audit 001 | ✓ implemented — `docs/audits/MIP_TABULAR_SOURCE_REUSE_CONTRACT_AUDIT_001.md` (reuse contract + non-divergence checkpoint; no connector implementation) |
| MIP tabular source reference and inspection 001 | ✓ implemented — `mip.contracts.tabular_source_reference`, `mip.workflows.tabular_source_inspection` (generic tabular source boundary + uploaded CSV compatibility view; no connector implementation) |
| MIP Planning/MMM tabular source adapter compatibility 001 | ✓ implemented — `mip.contracts.planning_mmm_tabular_source_adapter`, `mip.workflows.planning_mmm_tabular_source_adapter` (generic tabular source → Planning/MMM adapter; uploaded CSV path preserved) |
| MIP Planning/MMM readiness report adapter 001 | ✓ implemented — `mip.contracts.planning_mmm_readiness_report_adapter`, `mip.workflows.planning_mmm_readiness_report_adapter` (workflow readiness → MMMDataReadiness metadata bridge; no model execution) |
| MIP GeoX tabular source adapter compatibility 001 | ✓ implemented — `mip.contracts.geox_tabular_source_adapter`, `mip.workflows.geox_tabular_source_adapter` (generic tabular source → GeoX readout adapter; uploaded CSV path preserved) |
| MIP tabular source reuse completion audit 001 | ✓ implemented — `docs/audits/MIP_TABULAR_SOURCE_REUSE_COMPLETION_AUDIT_001.md` (milestone checkpoint: reusable tabular framework complete; connector adapters deferred) |
| MIP Planning/MMM calibration signal tabular intake 001 | ✓ implemented — `mip.contracts.planning_mmm_calibration_signal_tabular_intake`, `mip.workflows.planning_mmm_calibration_signal_tabular_intake` (metadata-safe calibration intake from generic tabular source; no model execution) |
| MIP MMM model artifact and existing model availability audit 001 | ✓ implemented — `docs/audits/MIP_MMM_MODEL_ARTIFACT_AND_EXISTING_MODEL_AVAILABILITY_AUDIT_001.md` (audit: existing MMM model reuse gate missing; EvidenceRegistry/gates partial only) |
| MIP MMM existing model availability gate 001 | ✓ implemented — `mip.contracts.mmm_existing_model_availability`, `mip.workflows.mmm_existing_model_availability` (metadata-only gate: reuse vs refresh vs new model run; no model execution) |
| MIP Planning/MMM calibration signal mapping and readiness 001 | ✓ implemented — `mip.contracts.planning_mmm_calibration_signal_mapping_readiness`, `mip.workflows.planning_mmm_calibration_signal_mapping_readiness` (map tabular intake to calibration readiness metadata; no calibration math) |
| MIP Planning/MMM trusted input and model run eligibility 001 | ✓ implemented — `mip.contracts.planning_mmm_trusted_input_model_run_eligibility`, `mip.workflows.planning_mmm_trusted_input_model_run_eligibility` (combine data/calibration/model availability into model-run eligibility gate; no model execution) |
| MIP MMM runtime adapter contract audit 001 | ✓ implemented — `docs/audits/MIP_MMM_RUNTIME_ADAPTER_CONTRACT_AUDIT_001.md` (audit: adapter placeholders + eligibility exist; MMM runtime request/response contracts missing; thin runtime adapter contract recommended) |
| MIP MMM runtime adapter contract 001 | ✓ implemented — `mip.contracts.mmm_runtime_adapter`, `mip.workflows.mmm_runtime_adapter` (metadata-only runtime handoff from eligibility; no external execution) |
| MIP MMM runtime result ingestion and diagnostics audit 001 | ✓ implemented — `docs/audits/MIP_MMM_RUNTIME_RESULT_INGESTION_AND_DIAGNOSTICS_AUDIT_001.md` (audit: handoff URIs exist; dedicated ingestion/diagnostics contracts missing; thin ingestion adapter recommended) |
| MIP MMM runtime result ingestion and diagnostics contract 001 | ✓ implemented — `mip.contracts.mmm_runtime_result_ingestion`, `mip.workflows.mmm_runtime_result_ingestion` (metadata-only runtime result ingestion; no artifact loading) |
| MIP MMM artifact governance routing gate audit 001 | ✓ implemented — `docs/audits/MIP_MMM_ARTIFACT_GOVERNANCE_ROUTING_GATE_AUDIT_001.md` (audit: ingestion candidates + model promotion metadata exist; dedicated routing/use-readiness gate missing; separate promotion gate not needed) |
| MIP MMM artifact governance and use readiness gate 001 | ✓ implemented — `mip.contracts.mmm_artifact_governance_use_readiness`, `mip.workflows.mmm_artifact_governance_use_readiness` (thin metadata-only governance routes + planning/diagnostic use readiness; no TrustReport/DecisionSurface construction) |
| MIP MMM runtime orchestration lane completion audit 001 | ✓ implemented — `docs/audits/MIP_MMM_RUNTIME_ORCHESTRATION_LANE_COMPLETION_AUDIT_001.md` (audit: runtime/control-plane lane closed with deferred nonblocking gaps; next: DecisionSurface/planning-answer eligibility) |
| MIP MMM DecisionSurface planning-answer eligibility audit 001 | ✓ implemented — `docs/audits/MIP_MMM_DECISION_SURFACE_PLANNING_ANSWER_ELIGIBILITY_AUDIT_001.md` (audit: DecisionSurface/Trust/Recommendation gates exist; question-level planning-answer eligibility missing; thin eligibility gate recommended) |
| MIP MMM planning answer eligibility gate 001 | ✓ implemented — `mip.contracts.mmm_planning_answer_eligibility`, `mip.workflows.mmm_planning_answer_eligibility` (question-level answer modes from use-readiness + gate refs; no DecisionSurface/Recommendation construction) |
| MIP MMM planning answer eligibility gate checkpoint audit 001 | ✓ implemented — `docs/audits/MIP_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_CHECKPOINT_AUDIT_001.md` (audit: eligibility checkpoint passed; next: planning-answer envelope audit) |
| MIP MMM planning answer envelope audit 001 | ✓ implemented — `docs/audits/MIP_MMM_PLANNING_ANSWER_ENVELOPE_AUDIT_001.md` (audit: eligibility + generic report/agent envelopes exist; MMM planning-answer envelope missing; thin envelope recommended) |
| MIP MMM planning answer envelope 001 | ✓ implemented — `mip.contracts.mmm_planning_answer_envelope`, `mip.workflows.mmm_planning_answer_envelope` (metadata-only can-say/cannot-say package from eligibility; no DecisionSurface/Recommendation construction) |
| MIP MMM planning answer envelope checkpoint audit 001 | ✓ implemented — `docs/audits/MIP_MMM_PLANNING_ANSWER_ENVELOPE_CHECKPOINT_AUDIT_001.md` (audit: envelope checkpoint passed; next: planning response rendering audit) |
| MIP MMM planning response rendering audit 001 | ✓ implemented — `docs/audits/MIP_MMM_PLANNING_RESPONSE_RENDERING_AUDIT_001.md` (audit: envelope exists; no deterministic planning-response renderer; thin renderer recommended) |
| MIP MMM planning response renderer 001 | ✓ implemented — `mip.reports.mmm_planning_response_renderer` (deterministic envelope → safe response sections; no LLM/math/DecisionSurface/Recommendation) |
| MIP MMM planning response renderer checkpoint audit 001 | ✓ implemented — `docs/audits/MIP_MMM_PLANNING_RESPONSE_RENDERER_CHECKPOINT_AUDIT_001.md` (audit: renderer checkpoint passed; next: LLM response boundary audit) |
| MIP MMM LLM response boundary audit 001 | ✓ implemented — `docs/audits/MIP_MMM_LLM_RESPONSE_BOUNDARY_AUDIT_001.md` (audit: renderer + adjacent llm.safety exist; no boundary consumes rendered planning sections; thin MMM LLM boundary recommended) |
| MIP MMM LLM response boundary 001 | ✓ implemented — `mip.contracts.mmm_llm_response_boundary`, `mip.workflows.mmm_llm_response_boundary` (metadata-only section policies/refusals over rendered sections; no provider/prompt/orchestration) |
| MIP MMM LLM response boundary checkpoint audit 001 | ✓ implemented — `docs/audits/MIP_MMM_LLM_RESPONSE_BOUNDARY_CHECKPOINT_AUDIT_001.md` (audit: boundary checkpoint passed; next: LLM response template audit) |
| MIP MMM LLM response template audit 001 | ✓ implemented — `docs/audits/MIP_MMM_LLM_RESPONSE_TEMPLATE_AUDIT_001.md` (audit: boundary exists; no template consumes it; thin MMM LLM response template recommended) |
| MIP MMM LLM response boundary application readiness audit 001 | ✓ documented — [MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_READINESS_AUDIT_001.md](MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_READINESS_AUDIT_001.md) (boundary ready for narrow application packaging; not full orchestration; not hardening) |
| MIP MMM LLM response boundary application 001 | ✓ implemented — `mip.llm.mmm_response_boundary_application` ([MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001.md](../contracts/MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001.md); metadata-only packaging of rendered sections; no LLM/prompt/orchestration) |
| MIP MMM GeoX LLM layering reconciliation audit 001 | ✓ implemented — `docs/audits/MIP_MMM_GEOX_LLM_LAYERING_RECONCILIATION_AUDIT_001.md` (audit: application package exists; template missing; rescope template to consume application package before implement; dataset strategy nonblocking) |
| MIP MMM LLM response template rescoping 001 | ✓ implemented — `docs/design/MIP_MMM_LLM_RESPONSE_TEMPLATE_RESCOPING_001.md` (rescope: template consumes `MMMResponseBoundaryApplicationOutput`; refusal-only when `ready_for_llm_prompt_assembly=false`; next: `MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001`) |
| MIP method-promotion and application package mypy cleanup 001 | ✓ implemented — typing-only fix for 5 known global mypy errors (method-promotion handoff consumer + MMM response boundary application); no semantic changes; next: `MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001` |
| MIP MMM LLM response template from application package 001 | ✓ implemented — `mip.llm.mmm_response_template` (metadata-only instruction slots from `MMMResponseBoundaryApplicationOutput`; refusal/defer-only when not ready; no prompt execution/provider/orchestration) |
| MIP MMM LLM response template checkpoint audit 001 | ✓ implemented — `docs/audits/MIP_MMM_LLM_RESPONSE_TEMPLATE_CHECKPOINT_AUDIT_001.md` (checkpoint passed; next: `MIP_DOMAIN_DATASET_FIXTURE_STRATEGY_001` for demo fixtures before verifier/prompt-execution) |
| MIP domain dataset fixture strategy 001 | ✓ implemented — `docs/design/MIP_DOMAIN_DATASET_FIXTURE_STRATEGY_001.md` (Tier 1–2 MIP / Tier 3 packages; five domains; expected can_say/cannot_say outcomes; next: `MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_001`) |
| MIP domain dataset schema contract 001 | ✓ implemented — `mip.contracts.domain_dataset_fixtures` (typed manifests/expectations only; no dataset generation; next: `MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_CHECKPOINT_AUDIT_001`) |
| MIP domain dataset schema contract checkpoint audit 001 | ✓ implemented — `docs/audits/MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_CHECKPOINT_AUDIT_001.md` (checkpoint passed; ready for `MIP_DEMO_DOMAIN_DATASETS_001`) |
| MIP domain dataset grain compatibility contract 001 | ✓ implemented — `mip.contracts.domain_dataset_grain_compatibility` (raw→convertible/blocked→MMM/GeoX/LLM metadata; KPI double-count blocked; next: `MIP_DEMO_DOMAIN_DATASETS_001`) |
| MIP MMM GeoX industry data feed alignment and intake policy 001 | ✓ implemented — `docs/intake/MIP_MMM_GEOX_INDUSTRY_DATA_FEED_ALIGNMENT_AND_INTAKE_POLICY_001.md` (raw inspection vs canonical engine-ready; roll-up-only with mapping; next: `MIP_DEMO_DOMAIN_DATASETS_001`; deferred: `MIP_SOURCE_NORMALIZATION_FROM_RAW_MARKETING_DATA_001`) |
| MIP demo domain datasets 001 | ✓ implemented — `data/demo/domain_fixtures/saas_subscriptions/v1/` (canonical MMM/GeoX panels + sample Qs/lifecycle; ROI/budget blocked pending MMM export; next: `MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001`) |
| MIP MMM LLM response verifier audit 001 | ✓ implemented — `docs/audits/MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001.md` (checkpoint passed; demo-safe readiness/refusal behavior fits the response chain; next: `MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001`) |
| MIP demo onboarding and use case guide 001 | ✓ implemented — `docs/demo/MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001.md` (new-user fixture journey, safe questions, blocked claims, and future artifact gates; next: `MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001`) |
| MIP chat-first demo UI design plan 001 | ✓ implemented — `docs/demo/MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001.md` (chat-primary layout, auditable evidence/guardrail panels, and deferred integrations; no UI code; next: `MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001`) |
| MIP chat-first demo UI implementation plan 001 | ✓ implemented — `docs/demo/MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001.md` (staged deterministic UI work, candidate app paths, safety tests, and rollback controls; no app changes; next: `MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_001`) |
| MIP chat-first demo UI implementation 001 | ✓ implemented — `mip.demo.chat_first_demo` + isolated canonical Streamlit tab (fixture-backed questions, deterministic answers, evidence/guardrail/lifecycle panels; no provider or model execution; next: `MIP_CHAT_FIRST_DEMO_UI_SMOKE_VALIDATION_001`) |
| MIP chat-first demo UI smoke validation 001 | ✓ validated — deterministic fixture/answer/panel/lifecycle and app-import smoke coverage; Docker tests passed but full Docker validation did not pass because the strict Ruff gate found 21 known pre-existing findings; next: `MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_CHECKLIST_001` |
| MIP chat-first demo UI manual review checklist 001 | ✓ documented — human-visible launch, question, answer, claim-safety, panel, lifecycle, no-runtime, Docker, and verdict checklist; no UI/runtime changes; next: `MIP_CHAT_FIRST_DEMO_UI_RELEASE_READINESS_AUDIT_001` |
| MIP chat-first demo UI release readiness audit 001 | ✓ audited — internal demo ready pending manual review; external release blocked pending recorded manual review and full Docker gate decision; production claims not authorized; next: `MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_RESULT_001` |
| MIP Streamlit editable install deployment contract 001 | ✓ documented — `requirements.txt` requires `-e .` because the current fixture loader needs repository-level demo assets; clean Python 3.11 Docker import/fixture regression added; next: `MIP_CHAT_FIRST_DEMO_UI_UX_ALIGNMENT_REMEDIATION_001` |
| MIP chat-first demo UI UX alignment remediation 001 | ✓ implemented — canonical app now defaults to deterministic chat-first MMM + GeoX measurement-copilot interaction; legacy tools remain secondary; next: `MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_RESULT_001` |
| MIP chat-first demo UI manual review result 001 | ✓ recorded — local review failed because duplicate sample-prompt widget keys stopped rendering before chat input; first-time onboarding prompt relevance also failed; next: `MIP_CHAT_FIRST_DEMO_UI_WIDGET_KEY_HOTFIX_001` |
| MIP chat-first demo UI widget-key hotfix 001 | ✓ implemented — deterministic, namespaced prompt keys remove the duplicate-widget runtime blocker and AppTest covers canonical render/rerun; manual review result 001 remains failed pending onboarding redesign; next: `MIP_CHAT_FIRST_DEMO_UI_ONBOARDING_CONVERSATION_REDESIGN_001` |
| MIP chat-first demo product flow and sample journey design 001 | ✓ designed — explicit no-dataset context, SaaS golden journey, fixture-gap plan, contextual progress, ownership, and acceptance criteria; next: `MIP_CHAT_FIRST_DEMO_SAMPLE_JOURNEY_FIXTURES_001` |
| MIP chat-first demo sample journey fixtures 001 | ✓ implemented — deterministic SaaS golden journey fixtures, typed loader, integrity validation, contextual prompt eligibility, and blocked planning boundary; next: `MIP_CHAT_FIRST_DEMO_PRODUCT_FLOW_IMPLEMENTATION_001` |
| MIP chat-first demo product flow implementation 001 | ✓ implemented — explicit dataset and journey context, stage-aware fixture replay, contextual progress/prompts, and no hidden readiness claims; next: `MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_RESULT_002` |
| MIP chat-first demo UI manual review result 002 | ✓ recorded — runtime mechanics work but business-value positioning, answer quality, vertical journey, upload entry, and chat/journey integration require redesign; next: `MIP_GUIDED_MEASUREMENT_WORKSPACE_PRODUCT_DESIGN_001` |

## Platform principles

**Common intake first, workflow-specific readiness second.**

MIP uses **one Common Data Intake Workbench** for MMM, GeoX/experiment design, CalibrationSignal intake, and decision-review workflows. Data is uploaded, connected, or declared **once**; MIP profiles, maps, snapshots, and routes it into workflow-specific readiness checks.

The user should **not** need separate MMM and GeoX upload flows. The LLM is the **conversational interface** over common intake and workflow-specific readiness—not the owner of raw data analysis or causal design decisions.

**Explicitly rejected:**

- Separate MMM upload flow · separate GeoX upload flow
- Duplicated column mapping logic · duplicated profiling logic
- LLM answers from raw files

The LLM must answer data-grounded questions only from governed profile summaries, readiness reports, diagnostic reports, and `TrustReport`s. LangGraph may route workflow state but must not expose raw dataframes to the LLM.

## Execution themes → roadmap tracks

| Theme | Tracks | Phase |
|-------|--------|-------|
| T1 Core semantics | S1–S12 | P4+ |
| T2 LLM-guided intake | I1–I3 | **P1–P2** |
| T3 Manifests | I4–I5, P8 | P3 |
| T4 Experiment design intake | I6b, MMM→GeoX bridge | **P4b** |
| T5 Common intake workbench | I6c, workflow support assessment | **P4c** |
| T6 Workflow-specific readiness | I7–I8 | **P5** |
| T6b General advisory / cold-start | I8b | **P5b** |
| T7 CalibrationSignal | I9 | P6 |
| T8 Product UI + public demo | I10, I15, P7–P9 | **P7–P9** |
| T8b Pluggable LLM providers | P7b, 8G–8H | **P7b** |
| T9 Demo profiling impl | I4, I7 | P8 ✓ |
| T9b Governed agent role registry + handoff contracts | Agentic governance | **P8b** ✓ |
| T9c Service/deployment | P10–P11 | P10–P11 |
| T10 LangGraph orchestration | Agentic governance | **P17** |
| T11 Lifecycle / current-state | P1, G11, G16 | P14 |
| T12 LLM answer governance | 8G–8N, G12–G20 | P15 |
| T13 Refresh governance | I12, P1 | P13 |
| T14 Golden scenarios | G1–G3, 8N | P16 |
| T15 Production hardening | I11, I13–I14 | P12 (table-ref design) |
| T16 Live execution / optimizer | Phase 8+, P18–P19 | P19–P20 deferred |

## Dependency chain (summary)

```text
P1 session/path
  → P2 required assets/sample schemas
  → P3 data source refs/manifests
  → P4 column mapping/semantic confirmation
  → P4b experiment design objective/KPI/data requirement contracts
  → P4c Common Data Intake Workbench + preliminary profiling contracts
  → P5 workflow-specific readiness reports (MMM / GeoX / CalibrationSignal / decision-review)
  → P5b general advisory and cold-start planning contracts
  → P6 CalibrationSignal intake mapping
  → P7 local Streamlit/Gradio workflow shell
  → P7b pluggable LLM provider contracts and explanation governance
  → P8 demo fixtures and local/demo profiling
  → P8b agent role registry, run manifest, failure packet, and resolution plan contracts
  → P8c canonical Streamlit entrypoint cleanup (app/streamlit_app.py)
  → P9 public hosted demo (Streamlit Community Cloud / Hugging Face Spaces)
  → P10 FastAPI/Docker service wrapper
  → P11 hosted API hardening (auth, rate limits, privacy, cost controls)
  → P17 LangGraph/stateful orchestration skeleton (after P8b contracts stabilize)
  → later panel_exp/MMM diagnostic execution / export handoff (gated)
```

## Implementation phases (P0–P20)

| Phase | Goal | Runtime allowed |
|-------|------|-----------------|
| **P0** | Roadmap audit ✓ | None |
| **P1** | I1–I2 intake session + path recommendation | Contracts/fixtures only | ✓ implemented |
| **P2** | I3 required data assets | Contracts/fixtures only | ✓ implemented |
| **P3** | I5 DataSourceRef + manifest | In-memory records | ✓ implemented |
| **P4** | I6 column mapping + semantic confirmation | Contracts/fixtures only | ✓ implemented |
| **P4b** | Experiment design objective + KPI/data requirement contracts | Contracts/fixtures only | ✓ implemented |
| **P4c** | **Common Data Intake Workbench** + preliminary profiling contracts | Summary records only; shared by MMM and GeoX | ✓ implemented |
| **P5** | **Workflow-specific** readiness report contracts (I7–I8) | Builds on P4c workbench | ✓ implemented |
| **P5b** | **General advisory** and cold-start planning contracts (I8b) | Routes users not ready for formal measurement | ✓ implemented |
| **P6** | I9 CalibrationSignal mapping | Fixture validation | ✓ implemented |
| **P7** | I10 local Streamlit/Gradio workflow shell | Display only; deterministic mode default | ✓ implemented |
| **P7b** | Pluggable LLM provider contracts + explanation governance | Provider modes; no canned explanations | ✓ implemented |
| **P8** | I4 demo fixtures + local/demo profiling | Sandbox in-memory only; no production ingestion | ✓ implemented |
| **P8b** | Agent role registry + run manifest + failure/recovery contracts | Contracts/helpers only; no LangGraph runtime | ✓ implemented |
| **P8c** | Canonical Streamlit entrypoint cleanup | Docs/tests only; no hosting | ✓ implemented |
| **P9** | Deterministic public demo preparation | Deployment metadata + safety copy; no secrets/LLM | ✓ implemented |
| **P9 deploy** | Streamlit Community Cloud deterministic public demo | Smoke-tested; no secrets/LLM | ✓ verified |
| **P9b** | Public demo deployment record | Docs-only verification record | ✓ implemented |
| **P10** | FastAPI/Docker service wrapper plan | Design doc; implementation split P10a–P10c | ✓ planned |
| **P10a** | FastAPI skeleton + health/version routes | `GET /health`, `GET /version` only | ✓ implemented |
| **P10b** | Deterministic workflow API routes | Demo fixture keys; no raw rows | ✓ implemented |
| **P10b.1** | Service boundary cleanup + usage modes doc | Routes call `mip.workflows.*`; fixtures inputs-only | ✓ implemented |
| **P10c** | Dockerfile + local container smoke test | No public API hosting | ✓ implemented |
| **P11** | API hardening + service packaging | OpenAPI/response/error contract tests; route metadata | ✓ implemented |
| **P12** | SDK / API / package usage examples | curl, Python, Docker; no production ingestion | On branch |
| **P12 (platform)** | I11 production table-ref design | Design only | Planned |
| **P13** | I12 refresh governance | No model execution | Planned |
| **P14** | P1/G11/G16 lifecycle selection | Registry metadata | Planned |
| **P15** | 8G–8H LLM answer governance | MockLLM + provider contracts | Planned |
| **P16** | G1–G3 golden harness | Fixture tests | Planned |
| **P17** | LangGraph / stateful workflow orchestration skeleton | Governed tool routing only | Planned |
| **P18** | S6/G9 decision packet | Assembly only | Planned |
| **P19** | Optimizer governance | **No optimizer execution** | Deferred |
| **P20** | Live execution gate review | **Deferred** | Deferred |

> **Rationale:** P7 before P9 establishes local user flow before public hosting. P7b before P9 sets explicit LLM provider and explanation-mode boundaries. **P8b before P17** defines governed agent contracts before any stateful agent runtime—avoiding free-form autonomous agents. P10/P11 follow UI/demo because FastAPI/Docker are service/deployment layers—not prerequisites for proving product flow.

> **Product decision:** The platform should be either **honestly deterministic** or **actually LLM-backed** through an explicit provider. **Canned/sample explanations are excluded** (`canned_demo`, `sample_explanation`, `template_llm_explanation`) because they blur that boundary and weaken trust.

## Common Data Intake Workbench (P4c)

**Purpose:** One shared intake layer before workflow-specific readiness branches.

**Shared responsibilities (future):**

Source registration · upload/connect/declaration modes · data source refs · intake manifests · column mapping · semantic confirmation · snapshot metadata · basic profiling summaries · time/geo coverage · metric/media/control availability · missingness summaries · grain/scope detection · LLM-safe data summary reports · **WorkflowSupportAssessment**

**Supports readiness for:** MMM · GeoX/experiment design · CalibrationSignal intake · decision-review

**Future contracts:**

`CommonIntakeWorkbench` · `CommonDataIntakeSession` · `DataSnapshot` · `SourceIngestionRecord` · `IngestionMode` · `IngestedAssetRecord` · `CommonDataProfileSummary` · `MetricAvailabilitySummary` · `GeoCoverageSummary` · `TimeCoverageSummary` · `MediaCoverageSummary` · `ControlCoverageSummary` · `WorkflowSupportAssessment` · `WorkflowReadinessRoute` · `LLMAnswerGroundingContext` · `PreliminaryAnalysisReport`

**WorkflowSupportAssessment** answers: which workflows can this data support? which are blocked? what grain/KPI/source is missing? what diagnostic should run next?

Example statuses: `supports_national_mmm` · `supports_geo_level_mmm` · `supports_geox_design_diagnostics` · `supports_calibration_signal_intake` · `blocked_needs_geo_level_outcome` · `blocked_needs_geo_level_media` · `blocked_needs_calibration_uncertainty` · `blocked_needs_metric_mapping`

**Important distinction:** Common profiling assesses **structural suitability** for the next step. It must **not** claim experiment design is valid, powered, or feasible. **panel_exp/GeoX** owns power, MDE, matchability, and design feasibility. **MMM** owns MMM model and calibration diagnostics.

### Same data, different workflow support (examples)

**National weekly data** (`week, country, product, channel, spend, impressions, conversions`):

> May support national MMM intake. Does **not** support DMA-level GeoX design—DMA/geo-level outcome and media are missing.

**DMA-week data** (`week, dma, product, platform, campaign, spend, impressions, visits, conversions`):

> May support GeoX design diagnostics for a DMA-level test. May support geo-level MMM if enough history and media variation exist. For awareness objectives, visits may be usable but BSV/branded search is not present. For conversion objectives, conversions are present but sparsity must be profiled.

**Experiment readout data** (`experiment_id, metric_id, estimand_id, channel, geo_scope, effect_estimate, standard_error, time_window`):

> May support CalibrationSignal intake if metric, estimand, scope, effect, and uncertainty are valid. **Not** sufficient alone for MMM modeling or new GeoX design.

## P5 — Workflow-specific readiness branching

**Status:** ✓ implemented — structural readiness reports only (`MMMDataReadinessReport`, `GeoXDesignReadinessReport`, `CalibrationSignalReadinessReport`, `DecisionReviewReadinessReport`, `build_workflow_readiness_reports`). Engine diagnostics, CalibrationSignal transformation, TrustReport approval, and decision recommendations remain deferred.

After common intake/profiling (P4c), readiness **branches by workflow**:

| Branch | Decides |
|--------|---------|
| **MMM readiness** | Time grain; historical coverage; media channels over time; outcome/media scope alignment; controls/promos/seasonality; calibration evidence; national vs geo-level vs calibrated vs refresh vs decision-surface candidate |
| **GeoX / experiment-design readiness** | Geo/DMA/market grain; outcome at geo-time level; media at geo-time level; pre-period data for design diagnostics; geo coverage; KPI vs objective alignment; whether panel_exp should run design diagnostics |
| **CalibrationSignal readiness** | Effect estimate + uncertainty; metric/estimand/channel/geo/time mapping; structured enough for `CalibrationSignal`; governed vs stale vs blocked |
| **Decision-review readiness** | `TrustReport` present; evidence alignment; metric/estimand/scope/freshness; human approval; blocked vs diagnostic vs decision-supporting |

**Why P5b follows P5:** P5 workflow-specific readiness reports determine whether the user is structurally ready for MMM, GeoX, CalibrationSignal, or decision-review workflows. If the user is **not** ready for formal measurement but still needs guidance, MIP should route them to **advisory/cold-start planning** rather than forcing an MMM or GeoX workflow.

## P5b — General advisory and cold-start planning

**Status:** ✓ implemented — advisory contracts and deterministic helpers (`build_cold_start_advisory_plan`, `build_cold_start_business_profile`, `infer_advisory_evidence_mode`, `build_traffic_source_signals`, `suggest_channel_candidates`, `build_channel_hypotheses`, `build_tracking_readiness_checklist`, `build_starter_measurement_plan`, `build_learning_agenda`). Outputs are labeled by evidence mode and claim type; ROI, causal lift, optimal mix, and decision authorization remain blocked.

**Purpose:** Broader advisory lane for users who are not yet measurement-ready. Covers SMB paid media, no-data channel planning, business-profile-driven hypotheses, website traffic/source-informed advisory, tracking setup, and learning agendas—not only formal MMM/GeoX paths.

### Architecture statement

The platform supports **advisory reasoning before formal measurement exists**. LLM general knowledge may be used to ask better questions and produce clearly labeled advisory hypotheses. When governed customer data summaries exist, data analysis modules may make the answer data-informed. MMM, GeoX, CalibrationSignal, and `TrustReport` remain required for measured, causal, or decision-supporting claims.

**Evidence hierarchy:**

```text
General knowledge
  → business profile
  → customer data summaries
  → measured diagnostics
  → TrustReport-authorized decision support
```

Referral traffic, organic search, direct traffic, email traffic, CRM data, and sales summaries may inform cold-start hypotheses, but they do **not** authorize causal or ROI claims. Advisory outputs must be labeled as **hypotheses to test** unless supported by measured diagnostics and `TrustReport` governance.

The LLM is allowed to use general marketing knowledge when no customer data exists, but the answer must say that it is **advisory-only** and should identify what data or tracking would increase confidence.

### Advisory evidence modes

`AdvisoryEvidenceMode`:

| Mode | Definition |
|------|------------|
| `general_knowledge_only` | LLM uses broad marketing knowledge and customer-provided business details. No customer data is available. |
| `business_profile_only` | LLM uses structured business profile details such as product, audience, geography, budget, margin, sales cycle, and objective. |
| `data_informed_advisory` | LLM uses governed customer data summaries such as website traffic source profile, CRM summary, sales summary, or common intake profile. Still not causal. |
| `measured_diagnostic` | LLM explains governed MMM, GeoX, calibration, or readiness diagnostic outputs. |
| `causal_decision_support` | LLM explains `TrustReport`-authorized decision-supporting outputs only. |

### Claim types

`AdvisoryClaimType`:

| Claim type | Allowed when |
|------------|--------------|
| `general_marketing_guidance` | General advisory |
| `hypothesis_to_test` | General advisory |
| `data_informed_hypothesis` | Data-informed advisory |
| `measured_observation` | Measured diagnostic |
| `diagnostic_explanation` | Measured diagnostic |
| `causal_claim` | `TrustReport`-authorized workflows only |
| `decision_recommendation` | `TrustReport`-authorized workflows only |

### Evidence levels

`EvidenceLevel`:

`no_customer_data` · `business_profile_signal` · `organic_interest_signal` · `organic_conversion_signal` · `search_intent_signal` · `referral_interest_signal` · `crm_signal` · `sales_signal` · `paid_test_signal` · `experiment_signal` · `mmm_signal` · `trust_report_authorized`

**Rules:**

- Recommendations based on business details alone → `no_customer_data` or `business_profile_signal`.
- Recommendations based on website traffic → `organic_interest_signal`, `organic_conversion_signal`, `search_intent_signal`, or `referral_interest_signal`.
- Recommendations based on paid test data → `paid_test_signal`.
- Only experiment/MMM/`TrustReport` outputs → measurement-backed or decision-supporting labels.

### Cold-start readiness statuses

`ColdStartAdvisoryStatus`:

`needs_business_details` · `needs_tracking_setup` · `advisory_plan_ready` · `ready_for_basic_tracking` · `ready_for_starter_test` · `not_ready_for_mmm` · `not_ready_for_geox` · `ready_for_data_collection` · `ready_for_reassessment`

### Readiness-to-measure ladder

```text
Advisory
  → tracking setup
  → starter test
  → paid readout
  → experiment / MMM later
```

### Future contracts

**Business profile and objectives:**

- `ColdStartBusinessProfile` — `business_type`, `product_or_service`, `B2B_or_B2C`, `average_order_value`, `gross_margin`, `sales_cycle_length`, `geography`, `target_audience`, `monthly_budget`, `primary_objective`, `secondary_objectives`, `existing_website`, `existing_tracking`, `creative_assets_available`, `customer_list_available`, `organic_channels_available`, `seasonality_context`, `constraints`
- `ColdStartMediaObjective` — awareness · traffic · lead_generation · sales · app_installs · store_visits · retention · repeat_purchase · market_launch · product_launch

**Channel suitability:**

- `ChannelCandidate` · `ChannelSuitabilityAssessment` · `ColdStartChannelHypothesis` · `StarterMediaMixHypothesis`

Channel candidates include: Google Search · Google Performance Max · Meta/Instagram · TikTok · YouTube · LinkedIn · Pinterest · Reddit · Display · CTV · Email/CRM · SEO/content · Creators/influencers · Affiliate/partnerships · Retargeting · Local listings/maps · Marketplaces

**Rules:** Channel hypotheses are advisory only unless backed by measured diagnostics. The platform may say a channel is a reasonable test candidate. The platform must **not** say a channel is ROI-optimal without measured evidence.

**Website traffic source advisory** (Organic Demand Signal Assessment):

- `WebsiteTrafficSourceProfile` · `TrafficSourceSignal` · `OrganicDemandSignal` · `ReferralInterestSignal` · `SearchIntentSignal` · `TrafficConversionSignal`

Allowed inputs (later): source/medium · default channel group · landing page · geography · device · new vs returning · sessions · engaged sessions · conversion events · leads · purchases · revenue · conversion rate · organic search queries · referral domains · social referrals · email traffic · direct traffic · UTM coverage

**Guardrail:** Website referral/social/organic traffic can suggest where to test first, but it cannot prove paid channel ROI or optimal media mix.

**Allowed example:** *Instagram referral traffic shows organic audience interest, so Meta/Instagram may be a reasonable small paid test candidate. Paid performance is unproven and should be validated with tracking and a limited test.*

**Disallowed example:** *Instagram referral traffic proves Meta is your best paid channel.*

**Tracking and learning agenda:**

- `TrackingReadinessChecklist` · `StarterMeasurementPlan` · `LearningAgenda` · `ReassessmentPlan`

Covers: UTM setup · pixel/tag setup · conversion events · lead capture · CRM/customer list · landing-page readiness · budget/timebox for initial test · primary KPI · secondary KPI · guardrail metrics · weekly reporting cadence · criteria for scaling/stopping · when to reassess · when to route to GeoX/MMM later

### Budget maturity handling

$500/month and $50K/month need different advice. Budget maturity should influence channel mix hypotheses, test scope, and learning agenda—not ROI claims.

### Example flows

**Example 1 — No data, business profile only**

User: *I sell handmade skincare online. I have $2,000/month. What channels should I start with?*

Allowed: Ask for target audience, margin, AOV, geography, creative assets, tracking, and objective. Produce advisory-only channel hypotheses (Meta/Instagram, TikTok, Google Search, SEO/content, email capture). Label: `business_profile_signal`, `hypothesis_to_test`, not ROI-proven.

**Example 2 — Website traffic exists, no paid media history**

Traffic summaries: organic search converts well · Instagram referral has traffic but weak conversion · email traffic converts well · direct traffic is high but attribution unclear.

Allowed: Search may be a strong first test candidate (organic intent). Meta/Instagram may be a small awareness or retargeting test, but paid social is unproven. Improve UTM tracking and list capture before scaling. Label: `data_informed_hypothesis`, not causal, requires paid test.

**Example 3 — No measurement readiness**

User: *Can I run MMM or GeoX?*

Allowed: Use P5 readiness reports. If not ready, route to cold-start advisory or tracking setup. Do not force MMM/GeoX.

**Example 4 — Broad non-channel advisory**

User: *What KPI should I use for this campaign?*

Allowed: Use general knowledge + objective ontology. Ask for business objective and funnel stage. If data exists, use metric availability summaries. Label KPI recommendation as advisory unless confirmed by semantic/readiness reports.

### LLM behavior (P5b)

**May:** ask for specific business details · ask for data that would improve the answer · use general marketing knowledge when no data exists · use governed data-analysis summaries when available · recommend channels as hypotheses to test · suggest starter tracking setup · suggest a learning agenda · explain what would be needed before MMM or GeoX

**Must not:** claim optimal media mix · claim channel ROI · claim causal effect · claim expected lift · claim final budget allocation · claim MMM/GeoX readiness without readiness reports · claim design feasibility without panel_exp diagnostics · claim decision authorization without `TrustReport`

### Future acceptance criteria (P5b)

- Can answer advisory marketing questions when no customer data exists
- Can ask for business details needed to improve channel recommendations
- Can ask for data that would make the answer more grounded
- Can label advisory answers by evidence mode and claim type
- Can use website traffic/source summaries to produce data-informed hypotheses
- Can distinguish organic/referral/social traffic signals from paid ROI evidence
- Can produce starter channel hypotheses without claiming optimality
- Can produce tracking setup checklist and learning agenda
- Can route users to MMM/GeoX only when readiness reports indicate eligibility
- Can block causal, ROI, lift, optimized budget, and decision-supporting claims without governed measurement evidence

### Hard boundaries (P5b)

No web search integration · no file parsing · no data profiling computation · no MMM/GeoX execution · no budget optimizer · no channel ROI model · no causal effect estimation · no automatic recommendation approval

## P6 — CalibrationSignal intake mapping

**Status:** ✓ implemented — `CalibrationEvidenceInput`, `CalibrationMappingRequirement`, `CalibrationMappingReport`, `validate_calibration_evidence_input`, `map_evidence_to_calibration_signal`. Maps governed experiment evidence into existing `CalibrationSignal` contracts with fixture validation. MMM calibration execution, effect estimation, causal certification, and decision approval remain deferred.

**Purpose:** Bridge governed experiment/readout evidence to MMM-consumable calibration signals after P5 readiness and P5b advisory lanes.

**Key behaviors:**

- Validates effect estimate, uncertainty (`standard_error`; CI alone does not auto-derive SE), metric/estimand, scope, and time window alignment
- Preserves lineage via `source_artifact_id`, `source_readout_id`, `source_experiment_id`, `source_trust_report_id`
- Blocks stale/non-causal evidence when requirements disallow them
- Maps valid evidence to `CalibrationSignal` with `DIAGNOSTIC_ONLY` tier and blocked decision/refresh usage

## P7–P11 — Product surface, LLM providers, and public demo hosting

**P7 status:** ✓ implemented — `app/streamlit_app.py` local deterministic Streamlit shell.

**P7b status:** ✓ implemented — `src/mip/contracts/llm_provider.py` and `src/mip/workflows/intake/llm_explanation.py`. Provider modes, governed input boundaries, explanation plans, and blocked canned/sample explanation modes. No LLM provider calls.

**Remaining (P9–P11):** Planned.

### Architecture layers

| Layer | Role |
|-------|------|
| **Core MIP package** | Contracts, gates, readiness reports, advisory plans, CalibrationSignal mapping, `TrustReport` logic, deterministic validators |
| **UI layer** | Human-facing Streamlit/Gradio interface: chat, forms, uploads, workflow selection, report cards, warnings, evidence labels, next steps |
| **FastAPI layer** | HTTP service boundary for programmatic access, external apps, future auth, rate limits, clean frontend/backend separation |
| **Docker layer** | Portable deployment package for consistent runs across local machines, Hugging Face Spaces, Render, Railway, or other cloud hosts |

**Hierarchy (first demo path):**

```text
User → UI → MIP core package
```

**Later production path:**

```text
User → UI → FastAPI → MIP core package
Docker wraps the UI/API/package for portable deployment.
```

FastAPI is **not** required for the first UI demo. FastAPI becomes useful when MIP needs external programmatic access, multiple frontends, auth/rate limits, integration with other apps, or a hosted service boundary. Docker is **not** the app—it is the portable runtime package that makes the app/API run consistently across hosting environments. P10 should wrap the core package and optionally the UI/API for portable deployment without duplicating MIP logic.

### UI access modes

**Local UI**

- User runs the app locally (e.g. `streamlit run`).
- Access through `localhost`.
- Best for development, private demos, debugging, and demo recordings.

**Public hosted UI**

- App deployed to Streamlit Community Cloud, Hugging Face Spaces, or similar.
- User accesses a public URL.
- Best for public demos, portfolio demos, stakeholder review, and lightweight product validation.

The **first public demo should be demo-safe** and should **not require paid infrastructure**.

Public hosting is **not** the same as production readiness. Public demo mode can be free or low-cost, but production use later requires auth, rate limits, privacy controls, monitoring, storage policy, abuse prevention, and cost controls.

### Public hosting strategy

**Public demo hosting targets:**

- **Streamlit Community Cloud** — simple Streamlit app
- **Hugging Face Spaces** — Streamlit/Gradio/Docker ML-style app

**Optional later:**

- **Render** — FastAPI/web service deployment
- **Railway / Fly / other cloud** — only after cost controls are clear

**Product stance:** P9 public demo should work **without platform-paid LLM dependency**. The public demo must **not** expose a platform-owned LLM API key unless auth, rate limits, monitoring, abuse controls, and cost controls exist.

### P7 — Local Streamlit/Gradio workflow shell

**Status:** ✓ implemented — `app/streamlit_app.py`, `app/demo_fixtures.py`, `app/ui_renderers.py`. Deterministic mode default; sample fixtures for advisory, readiness, and calibration mapping; evidence/claim labels and blocked-claim guardrails visible. No LLM, upload parsing, MMM, or GeoX execution.

### P7b — Pluggable LLM provider contracts and explanation governance

**Status:** ✓ implemented — `LLMProviderConfig`, `LLMGovernedInputReference`, `LLMExplanationRequest`, `LLMExplanationPlan`, and deterministic helpers in `mip.workflows.intake.llm_explanation`. Supports disabled, local Ollama, hosted open-source, BYOK, and platform-managed-key-later modes. Excludes canned/sample explanation modes. No LLM calls, API keys, or provider SDKs.

**Future concept — `LLMProviderMode`:**

| Mode | Definition |
|------|------------|
| `disabled` | No LLM call. UI shows deterministic MIP contracts, readiness reports, advisory plans, warnings, evidence labels, claim labels, allowed next steps, and blocked next steps. |
| `local_ollama` | Local Mac/dev mode. User runs an open-source model locally through Ollama or compatible runtime. For local/private demos; not required for public hosting. |
| `hosted_open_source` | Public-hosted experimental mode. Hosted app uses an open-source model if latency, memory, and cost are acceptable. Must be clearly labeled experimental. |
| `bring_your_own_key` | User supplies API key for a supported provider (OpenAI, Anthropic, Gemini, Mistral, Groq, etc.). User responsible for provider usage and cost. |
| `platform_managed_key_later` | Future paid/controlled mode. **Not allowed** in public demo until auth, rate limits, monitoring, abuse prevention, key management, privacy policy, and cost controls exist. |

**Explicitly excluded:** `canned_demo` · `sample_explanation` · `template_llm_explanation`

**Product decision:** The platform should be either **honestly deterministic** or **actually LLM-backed** through an explicit provider. Canned/sample explanations blur that boundary and weaken trust.

The public product surface should work without paid LLM infrastructure. Deterministic mode is the default. Optional LLM-backed explanations may use hosted open-source models, local Ollama for local use, or bring-your-own-key providers. Canned/sample explanations are excluded because the platform should be either honestly deterministic or actually LLM-backed through an explicit provider.

**The LLM explains governed MIP outputs; it does not create measurement authority.**

**Future concept — `LLMUseCase`:**

`intake_question_generation` · `missing_data_question_generation` · `readiness_explanation` · `advisory_plan_explanation` · `calibration_mapping_explanation` · `blocked_claim_explanation` · `trust_report_explanation` · `report_summarization` · `chat_response`

LLM use cases are explanation/routing/intake surfaces. They do **not** authorize causal or decision-supporting claims.

**LLM authority boundary**

The LLM is **not** the authority. MIP contracts, readiness reports, advisory claim guards, CalibrationSignal mapping reports, `TrustReport`s, and deterministic validators remain authoritative.

**The LLM may:** ask follow-up questions · ask for missing data · explain governed outputs · summarize readiness reports · explain blocked claims · translate structured findings into user-facing language · produce advisory-only hypotheses when evidence mode allows

**The LLM must not:** override readiness reports · override `TrustReport` status · override advisory claim guards · override CalibrationSignal mapping status · invent causal effects · invent ROI · invent lift · invent power/MDE · invent matched markets · invent budget optimization · promote advisory hypotheses to decision recommendations · hide evidence/claim labels

**LLM input boundary**

LLM input should be **governed summaries and report payloads**, not raw rows by default.

**Allowed examples:** `CommonIntakeWorkbench` summaries · `WorkflowReadinessReport` · `ColdStartAdvisoryPlan` · `CalibrationMappingReport` · `TrustReport` summary · `allowed_next_steps` · `blocked_next_steps` · claim type labels · evidence level labels · warnings · blocking reasons

**Blocked by default:** raw uploaded rows · private customer secrets · unbounded file contents · unvalidated source data · credentials · API keys · PII-heavy exports

If raw data access is ever introduced, it must be a separate governed capability with explicit user consent, row/size limits, privacy policy, retention policy, and redaction controls.

**Public-hosted LLM strategy (P9 prerequisite)**

For public Streamlit/Hugging Face demos, supported explanation modes:

1. `disabled` / deterministic mode — **default**
2. `hosted_open_source` — experimental if performance acceptable
3. `bring_your_own_key` — optional

Canned/sample explanation mode is **not** supported. The hosted public demo must remain useful in deterministic mode even when no LLM provider is configured. Hosted open-source mode is optional and experimental because open-source model weights may be free, but public inference still requires compute. The system must **not** depend on hosted open-source inference for core functionality.

**Local Mac/dev LLM strategy**

For local Mac/dev usage, supported explanation modes:

1. `disabled` / deterministic mode
2. `local_ollama`
3. `bring_your_own_key`

Local Ollama mode avoids platform-paid LLM calls and keeps inference local. Local mode must still obey the same MIP claim boundaries as hosted mode.

**Future UI behavior**

The UI must display active mode: **Deterministic** · **Local Ollama** · **Hosted Open Source (experimental)** · **Bring Your Own Key** · **Platform Managed Key (later only)**

In deterministic mode, the UI shows structured reports and deterministic text derived directly from contract fields—it does **not** pretend to be chat/model reasoning. In LLM-backed modes, the UI displays provider mode and preserves evidence labels, claim labels, warnings, blocked claims, and allowed next steps. If LLM output conflicts with MIP contract/report constraints, the **deterministic MIP result wins**.

**Acceptance criteria (P7b):**

- Defines provider mode contracts
- Excludes canned/sample explanation mode
- Supports disabled/deterministic mode as default
- Supports `local_ollama` for local dev
- Supports `hosted_open_source` as experimental
- Supports `bring_your_own_key`
- Defines `platform_managed_key_later` as gated future mode only
- Prevents LLM from overriding MIP contracts/reports/`TrustReport`s
- Ensures LLM receives governed summaries, not raw rows by default
- Requires UI to show active explanation/provider mode
- Requires public hosted demo to work without paid LLM dependency
- Blocks platform-managed public LLM keys until auth, rate limits, monitoring, and abuse controls exist

### P8 — Demo fixtures and local/demo profiling

**Purpose:** Sandbox profiling for local and demo paths (now follows P7/P7b).

**P8 status:** ✓ implemented — `src/mip/contracts/demo_profile.py` and `src/mip/workflows/intake/demo_profiling.py`. P8 implemented local/demo profiling for small synthetic tabular datasets. Demo profiles can summarize website traffic, national media/outcome, DMA-week media/outcome, and experiment readout-like data into governed summaries used by advisory, readiness, and CalibrationSignal mapping workflows. P8 is demo-only and does not add production ingestion, external connectors, raw-row LLM access, MMM/GeoX execution, or persistent storage.

### P8b — Agent role registry, run manifest, failure packet, and resolution plan contracts

**Purpose:** Define governed specialist agent roles, permission boundaries, and typed handoff contracts **before** LangGraph or any stateful agent runtime is introduced.

**Roadmap status:** ✓ documented and **implemented** — `src/mip/contracts/agentic_workflow.py`, `src/mip/workflows/intake/agentic_recovery.py`.

**P8b implemented:** Governed agent role, run manifest, failure packet, resolution plan, validation report, retry policy, escalation policy, and handoff packet contracts. These contracts prepare future agentic orchestration without introducing LangGraph, runtime agents, LLM calls, autonomous retries, MMM execution, or GeoX execution. Agents remain reasoning/recovery surfaces, not measurement authorities.

**Rationale:** P8b defines the governed agent contracts before any stateful agent runtime is introduced. P17 can later implement LangGraph/stateful orchestration using those contracts. This avoids free-form autonomous agents and keeps MMM/GeoX/calibration workflows governed.

**Core principle:** Agents are specialized reasoning and recovery surfaces, not measurement authorities. Agentic workflows are recovery-aware and explainable, not autonomous measurement authorities.

The platform will use governed specialist agents only where they add distinct expertise, tool access, or failure-handling value. The goal is not many agents; the goal is controlled specialization with typed handoffs, explicit permission boundaries, and validation gates.

**Hierarchy:**

```text
User request
  → Intake/Routing Agent
  → Specialist Agent or deterministic workflow
  → MIP contracts / gates / validators
  → Evaluator & Validator Agent
  → user-facing explanation or safe retry plan
```

**First-wave agent roles (planned):** Intake & Routing · Data Profiling / Data Readiness · Cold-Start Advisory · MMM Specialist · GeoX / Experiment Specialist · CalibrationSignal Specialist · Failure Recovery / Debugging · Evaluator & Validator

**Future optional agents (deferred):** Feature Store Explorer · ML Engineering / MLOps Specialist · Research Scout · Data Connector / Integration · Privacy / Security Review · Product / UX Guide — each with explicit trigger conditions.

**Future contract names (P8b implementation):**

| Contract | Purpose |
|----------|---------|
| `AgentRoleDefinition` | Role identity, responsibilities, allowed/blocked actions |
| `AgentCapability` | Typed capability surface for a role |
| `AgentPermissionBoundary` | Explicit allow/deny boundaries |
| `AgentTask` | Unit of work with input references |
| `AgentRunManifest` | Workflow, step, input/artifact refs, package/version metadata, status, timestamps, warnings, blocking reasons |
| `AgentObservation` | Governed observation from a step (no raw rows by default) |
| `AgentFailurePacket` | Workflow, step, error type/message, stack trace, typed validation failures, safe context, allowed/blocked retry actions, affected artifacts |
| `AgentResolutionPlan` | Diagnosis, recommended user questions, safe/blocked next steps, retry eligibility, human approval requirement, expected downstream impact |
| `AgentValidationReport` | Claim compliance, forbidden-claim findings, missing evidence labels, TrustReport requirement status, readiness/calibration consistency, final approval/block status |
| `AgentHandoffPacket` | Typed handoff between agents with governed references |
| `AgentRetryPolicy` | Safe retry rules and caps |
| `AgentEscalationPolicy` | When to escalate to human review |

**Execution ownership boundaries:**

- The **MMM package** owns MMM modeling and execution. MIP agents explain, route, validate, recover, and govern.
- **panel_exp / GeoX** owns experiment design, diagnostics, and inference execution. MIP agents explain, route, validate, recover, and govern.

**Acceptance criteria (P8b):**

- Defines first-wave agent roles and boundaries
- Defines future/deferred agent roles and trigger conditions
- Defines typed handoff contracts for agent tasks, manifests, failures, resolution plans, validation reports, and retry policies
- Separates agent reasoning from measurement authority
- Ensures MMM package and panel_exp/GeoX retain execution ownership
- Ensures agents cannot override TrustReport/readiness/calibration/advisory gates
- Requires Evaluator & Validator Agent before decision-supporting user-facing explanations
- Captures stack trace/failure recovery pattern without adding runtime execution
- Documents safe retry and blocked retry concepts

See [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](../architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md) for role details, examples, and failure-recovery flows.

### P8c — Canonical Streamlit entrypoint cleanup

**Purpose:** Make the local/public demo Streamlit entrypoint unambiguous before P9 public hosting.

**P8c status:** ✓ implemented — `app/streamlit_app.py` is the canonical local/public deterministic demo app.

**P8c implemented:** P8c clarified the canonical Streamlit entrypoint before public hosting. `app/streamlit_app.py` is the public/local demo app; any legacy Streamlit shell (`src/mip/app/streamlit_app.py`, `mip-app`) is compatibility/deprecated only.

**Canonical command:**

```bash
poetry run streamlit run app/streamlit_app.py
```

The app runs in deterministic mode by default. It does not require LLM providers, API keys, FastAPI, Docker, or external services.

**Legacy compatibility:** `poetry run mip-app` launches the Phase 5D JSON workflow shell (`run_local_workflow()` + `MockLLMProvider`) for backward compatibility. It is not the canonical P7/P8 demo surface.

### P9 — Deterministic public demo preparation

**Purpose:** Prepare the repository for a first public hosted demo on Streamlit Community Cloud (primary) or Hugging Face Spaces (secondary), using the canonical deterministic app.

**P9 status:** ✓ implemented — `requirements.txt`, `runtime.txt`, `.streamlit/config.toml`, public demo safety copy in `app/streamlit_app.py`, deployment README, and readiness tests.

**P9 implemented:** P9 prepares the deterministic Streamlit demo for public hosting. The public demo uses `app/streamlit_app.py` as the canonical app entrypoint, includes deployment dependency metadata, preserves deterministic/no-LLM mode, and documents Streamlit Community Cloud as the first hosting path. It does not introduce LLM providers, BYOK, FastAPI, Docker, external APIs, production connectors, persistent storage, or public secrets.

**Primary hosting path:** Streamlit Community Cloud — main file `app/streamlit_app.py`, dependencies from `requirements.txt`, Python 3.11 via `runtime.txt`.

**Secondary documented option:** Hugging Face Spaces (simple Streamlit path first; Docker Spaces deferred to P10).

**First hosted demo scope (deterministic-only):**

- No LLM provider, API key, BYOK, or Ollama integration in the public app
- No FastAPI, Docker, database, or persistent storage
- Synthetic demo fixtures only; no file upload persistence
- Public Demo Safety copy visible on landing

**Manual deploy:** Complete — see hosted URL above.

**Deferred beyond first deploy:** `hosted_open_source`, `bring_your_own_key`, platform-managed keys (require P11 controls).

### P9 deploy — Streamlit Community Cloud (verified)

**Purpose:** Deploy demo-safe public URL on Streamlit Community Cloud.

**P9 deploy status:** ✓ verified — deterministic public demo smoke-tested at commit `96cf98c`. **Hosted URL:** https://marketingintelligenceplatform.streamlit.app/

### P9b — Public demo deployment record

**Purpose:** Record deployed state, smoke-test results, safety boundaries, and next-step guidance in repo history.

**P9b status:** ✓ complete — [PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md](../demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md) (hosted URL recorded).

**Privacy/cost controls (public demo safe by default):**

- No persistent storage by default
- No platform-owned LLM key by default
- Optional BYOK only
- Uploaded data cleared after session or explicitly documented
- Sample/demo data available
- File size limits before upload support
- No raw rows sent to LLM by default
- Active provider mode visible
- Advisory/measurement/decision-support labels visible

Platform-managed LLM keys deferred until: authentication · rate limits · spend limits · abuse monitoring · secure provider secrets · privacy and retention policy · explicit user consent

**Acceptance criteria (P9):**

- Deploys to Streamlit Community Cloud or Hugging Face Spaces
- Works in deterministic mode without paid LLM dependency
- Optionally supports `hosted_open_source` if performance is acceptable
- Optionally supports `bring_your_own_key`
- Does not expose platform-owned LLM API keys
- Uses sample/demo data by default
- Clearly labels non-production/demo status
- Shows active provider mode
- Shows evidence/claim labels and blocked claims

### P10 — FastAPI/Docker service wrapper

**Purpose:** HTTP boundary for programmatic access; portable deployment.

**P10 planning status:** ✓ documented — [P10_FASTAPI_DOCKER_WRAPPER_PLAN.md](../service/P10_FASTAPI_DOCKER_WRAPPER_PLAN.md). Design only; no FastAPI package, Dockerfile, or routes in repo yet.

**P10 plan summary:** Thin wrapper over existing deterministic MIP helpers (advisory, readiness, calibration, intake). Streamlit public demo remains canonical. **P10c** adds local Docker smoke for FastAPI only. Auth/secrets/rate limits deferred to **P11**.

**Implementation split:**

| Sub-phase | Scope | Status |
|-----------|-------|--------|
| **P10a** | FastAPI skeleton; `GET /health`, `GET /version` | ✓ implemented |
| **P10b** | `POST` workflow routes (demo fixture keys) | ✓ implemented |
| **P10b.1** | Service boundary cleanup; `docs/service/DETERMINISTIC_USAGE_MODES.md` | ✓ implemented |
| **P10c** | Dockerfile + local container smoke test | ✓ implemented |
| **P11** | API hardening / service packaging | ✓ implemented |
| **P12** | SDK / API usage examples | On branch |

**Acceptance criteria (P10 implementation, future):**

- Exposes core MIP workflows through API endpoints
- Keeps MIP package as source of truth
- Does not duplicate business logic in API layer
- Includes health check
- Includes Dockerfile or deployment container
- Keeps secrets out of repo
- Prepares for auth/rate limits later

### P11 — API hardening and service packaging

**Purpose:** Make the deterministic FastAPI service predictable, testable, documented, and safe as a service surface before SDK examples, synthetic fixtures, uploads, or hosted deployment.

**P11 plan status:** ✓ documented — [P11_API_HARDENING_AND_SERVICE_PACKAGING_PLAN_001.md](../service/P11_API_HARDENING_AND_SERVICE_PACKAGING_PLAN_001.md)

**P11 implementation status:** ✓ merged — OpenAPI contract tests, response contract tests, error behavior tests, route metadata polish. `api_phase` remains `P10b.1`.

**P12 status:** ✓ merged — [P12_SDK_API_USAGE_EXAMPLES_001.md](../examples/P12_SDK_API_USAGE_EXAMPLES_001.md). Notebooks deferred.

**Stage A status:** ✓ implemented — synthetic deterministic fixtures at `examples/fixtures/stage_a/` with manifest, README, and validation tests. **Stage A.2** adds `mip.examples.stage_a_fixtures` loader helpers (PR #34). No MMM/GeoX execution outputs. Stage B engine-backed visuals remain deferred.

**Agent tooling audit (001):** ✓ documented — executability gaps, Cursor checklist, stop/go criteria. Verdict: mostly ready for deterministic Cursor work; needs detail before LLM/agent runtime. See [audit](../audits/MIP_AGENT_TOOLING_AND_ROADMAP_IMPLEMENTATION_DETAIL_AUDIT_001.md).

**Report / adapter / agent contract plan (001):** ✓ merged — defines adapters, report envelopes, provenance, agent/LLM boundaries, golden paths. See [contract plan](../architecture/MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md).

**Deterministic report contracts + Stage A.3 calibration adapter:** ✓ merged — `mip.contracts.deterministic_report`, `mip.examples.stage_a_adapters`, golden paths #3–#5.

**Calibration report builder/export helpers:** ✓ merged — `mip.reports.deterministic_reports` and `mip.reports.calibration_reports` for local JSON export (calibration path only).

**Stage A.3 advisory/readiness/intake adapter plan (001):** ✓ documented — fixture→workflow mapping. See [plan](../architecture/STAGE_A3_ADVISORY_READINESS_INTAKE_ADAPTER_PLAN_001.md).

**Stage A.3 cold-start advisory adapter:** ✓ implemented — `mip.examples.stage_a_adapters`, `mip.reports.advisory_reports`, golden path #1.

**Agent answerability contracts + evaluator:** ✓ implemented. **Agent capability eval fixtures:** ✓ implemented — 10 file-backed cases.

**MIP LLM control plane architecture (001):** documented — [MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md](../architecture/MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md). LLM-first interface, deterministic-core; shared control plane + package adapters.

**Next:** `MIP_TOOL_REGISTRY_AND_CAPABILITY_METADATA_CONTRACT_001`; LLM explanation contracts; readiness adapter remains `needs_contract_update`.

### P11 — Hosted API hardening (later)

**Purpose (deferred):** Auth, rate limits, privacy, cost controls for **hosted** public API path.

### Example flows

**Example 1 — Public demo, no LLM**

User opens hosted Streamlit/Hugging Face app. Provider mode is `disabled`/deterministic. User enters cold-start business profile. MIP returns `ColdStartAdvisoryPlan` with `evidence_mode=business_profile_only` and `claim_type=hypothesis_to_test`. UI displays deterministic report cards and does **not** pretend an LLM generated the answer.

**Example 2 — Public demo, BYOK**

User selects `bring_your_own_key` and enters provider key. MIP builds governed report payload. LLM explains the report but must preserve evidence labels, claim labels, warnings, allowed next steps, and blocked next steps. User pays their own provider usage.

**Example 3 — Local Mac, Ollama**

Developer runs app locally. Provider mode is `local_ollama`. The local model explains MIP reports using governed summaries only. MIP validators remain authoritative.

**Example 4 — Hosted open-source model**

Hosted demo enables `hosted_open_source` as experimental. If latency or memory is unacceptable, the app falls back to deterministic mode. Core workflow functionality must not depend on hosted model availability.

## P4b — Experiment design objective and data requirement contracts

**Entry paths:** MMM-driven (uncertainty, calibration gap, evidence conflict) · standalone GeoX design.

**Future contracts:** `ExperimentDesignObjective` · `ExperimentDesignIntake` · `MMMToGeoXDesignBridge` · `StandaloneGeoXDesignRequest` · `ExperimentDiagnosticRequest` · (see [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md) I6b)

**Objective-to-KPI families (deterministic, future):** awareness · demand creation · conversion · retention/usage · MMM calibration (must match MMM metric/estimand/scope).

## Diagnostic ownership split

| Owner | Responsibility |
|-------|----------------|
| **Common MIP intake/profiling** | Upload/connect/declaration; source registration; snapshots; mapping; semantic confirmation; structural profiling; workflow support assessment; LLM-safe summaries |
| **MMM** | MMM data sufficiency; media time-series; channel coverage; calibration use; model refresh; decision surface diagnostics |
| **GeoX / panel_exp** | Design feasibility; pre-period sufficiency; power/MDE; matchability; treatment/control; duration sensitivity; readout |
| **LLM** | Clarify intent; explain required data; explain insufficiency; summarize governed reports—**no** diagnostic computation or certification |

## LLM role in common intake (allowed vs disallowed)

**May say:**

> You asked for DMA-level GeoX design, but your uploaded data is national-week only. GeoX design needs geo/DMA-level outcome and media data.

> You asked for an awareness test. Your data includes visits and conversions but not BSV or branded search. Visits may be a proxy, but the platform should confirm whether traffic is acceptable as the primary KPI.

**Must not say:** this test is powered · use 8 weeks · these are the matched markets · the design is valid · move budget to this channel

## Future acceptance criteria

### Common intake workbench (P4c)

- User provides data **once** through common intake
- Same data evaluated for MMM, GeoX, CalibrationSignal, and decision-review support
- Platform reports grain (national, geo, DMA, weekly, daily, monthly)
- Platform explains when more granular data is needed for GeoX
- Platform explains when longer history is needed (without claiming final feasibility)
- Platform explains KPI gaps for awareness/demand/conversion goals
- LLM explains workflow-specific gaps from governed reports only
- Common layer cannot produce lift, MDE, power, matched markets, or budget recommendations

### Experiment design intake (P4b)

- MMM-driven and standalone GeoX requests; objective→KPI mapping; `ExperimentDiagnosticRequest` without executing panel_exp

### LangGraph (P17)

- Route intent to governed nodes; typed graph state; approved tools only; human approval for decision-support transitions; audit trail; no bypass of readiness/`TrustReport`/engine boundaries

## Capability blockers (quick reference)

| Capability | Blocked until |
|------------|---------------|
| Workflow-specific readiness | P4c workbench + P5 contracts |
| General advisory / cold-start | P5b contracts + evidence/claim labeling |
| CalibrationSignal intake mapping | P6 contracts + fixture validation |
| Experiment design diagnostics | P4b + P4c + P5 + panel_exp gated handoff |
| LLM current-performance answers | P14 + P15 + S1–S3 + TrustReport + G11–G20 |
| LangGraph runtime | P4b, P4c, P5, P5b, P7, P8, **P8b** agent contracts stable |
| Live engine execution | P16, P15, 8G–8N, G3, explicit signoff |

## Do not build yet

Model execution, optimizer execution, sibling imports, actual file upload/parsing, production connectors, power/MDE/matching, LangGraph runtime (until P17 prerequisites), raw-file LLM grounding, lift/budget/design-validity claims from common intake alone.

## Canonical ownership (overlaps)

| Concept | Owner doc |
|---------|-----------|
| Common intake workbench | This doc P4c; Conversational intake I6c |
| Workflow-specific readiness | Conversational intake I7–I8; P5 |
| General advisory / cold-start | Conversational intake I8b; P5b |
| Product surface + public demo | P7–P9; Conversational intake I10 |
| Pluggable LLM providers | P7b; LLM reasoning roadmap §8 |
| Experiment design intake | Conversational intake I6b; P4b |
| LangGraph orchestration | Agentic workflow governance **P8b**, **P17** |

## Related documents

| MIP conversational capability routing and grounded response architecture 001 | ✓ amended — LLM-first free-form conversation with deterministic governed handoff; next: `MIP_CONVERSATIONAL_TURN_MODE_AND_LLM_HANDOFF_CONTRACTS_001` |

| MIP guided workspace chat foundation remediation 001 | ✓ implemented — bounded transcript, deterministic free-form routing, and plain-language onboarding; next: `MIP_GUIDED_MEASUREMENT_WORKSPACE_VERTICAL_JOURNEY_001` |

| MIP guided measurement workspace shell remediation 001 | ✓ implemented — concise welcome, compact starters, one selected answer, and no premature SaaS references; next: `MIP_GUIDED_MEASUREMENT_WORKSPACE_VERTICAL_JOURNEY_001` |

| MIP guided measurement workspace shell 001 | ✓ implemented — business-value entry, distinct deterministic starters, explicit sample/readiness modes, and active context; next: `MIP_GUIDED_MEASUREMENT_WORKSPACE_VERTICAL_JOURNEY_001` |

| MIP guided measurement workspace implementation plan 001 | ✓ planned — P1 shell, P2 vertical journey, P3 deterministic answers, browser checkpoint, P4 upload readiness, P5 review, P6 release audit; next: `MIP_GUIDED_MEASUREMENT_WORKSPACE_SHELL_001` |

| MIP guided measurement workspace product design 001 | ✓ designed — persistent conversation, vertical SaaS journey, and readiness-only upload path; next: `MIP_GUIDED_MEASUREMENT_WORKSPACE_IMPLEMENTATION_PLAN_001` |

- [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
- [LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md](./LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md)
- [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](../architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md)
- [REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md)
- Phase-definition completeness policy and audit (A–L registry): `docs/governance/MIP_PHASE_DEFINITION_COMPLETENESS_POLICY_001.md`, `docs/architecture/MIP_CONVERSATIONAL_CONTROL_PLANE_PHASE_COMPLETENESS_AUDIT_001.md`.
- Next authorized artifact: `MIP_CONVERSATIONAL_TURN_MODE_AND_LLM_HANDOFF_CONTRACTS_001`.
- Implementation sequence: `docs/architecture/MIP_CONVERSATIONAL_CONTROL_PLANE_IMPLEMENTATION_PLAN_001.md` with twelve gated tasks from typed contracts through release gates.
- Phase A complete: `MIP_CONVERSATIONAL_CONTROL_PLANE_TYPED_CONTRACTS_001`; next authorized artifact is `MIP_CONVERSATIONAL_CONTROL_PLANE_CAPABILITY_REGISTRY_001`.
- Phase B complete: `MIP_CONVERSATIONAL_CONTROL_PLANE_CAPABILITY_REGISTRY_001`; next authorized artifact is `MIP_CONVERSATIONAL_CONTROL_PLANE_PERSISTENT_WORKSPACE_AND_EVENTS_001`.
- Phase C complete: `MIP_CONVERSATIONAL_CONTROL_PLANE_PERSISTENT_WORKSPACE_AND_EVENTS_001`; next authorized artifact is `MIP_CONVERSATIONAL_CONTROL_PLANE_DIALOGUE_ROUTER_001`.
- Phase D complete: `MIP_CONVERSATIONAL_CONTROL_PLANE_DIALOGUE_ROUTER_001`; next authorized artifact is `MIP_CONVERSATIONAL_CONTROL_PLANE_WORKFLOW_GRAPH_AND_BINDING_001`.
- Phase E complete: `MIP_CONVERSATIONAL_CONTROL_PLANE_WORKFLOW_GRAPH_AND_BINDING_001`; next authorized artifact is `MIP_CONVERSATIONAL_CONTROL_PLANE_ARTIFACT_AND_REQUIREMENT_RESOLVER_001`.
- LLM-first front-door remediation: CF1 turn-mode/handoff contracts, CF2 structured platform truth and approved corpus, CF3 read-only retrieval, CF4 read-only LLM front door, and CF5 quality/safety gate precede Phase F; next authorized artifact is `MIP_CONVERSATIONAL_TURN_MODE_AND_LLM_HANDOFF_CONTRACTS_001`.
- CF1 complete: `MIP_CONVERSATIONAL_TURN_MODE_AND_LLM_HANDOFF_CONTRACTS_001`; typed modes, grounding, claim, fallback, and provider-disclosure boundaries are implemented without provider execution. Next authorized artifact: `MIP_CONVERSATIONAL_PLATFORM_TRUTH_AND_KNOWLEDGE_CORPUS_001`.
- CF2 complete: `MIP_CONVERSATIONAL_PLATFORM_TRUTH_AND_KNOWLEDGE_CORPUS_001`; structured platform truth and ten approved packaged knowledge documents are available without retrieval or provider execution. Next authorized artifact: `MIP_CONVERSATIONAL_READ_ONLY_RETRIEVAL_001`.
- CF3 complete: `MIP_CONVERSATIONAL_READ_ONLY_RETRIEVAL_001`; deterministic approved-corpus lexical retrieval with filters, context hints, and traceable passages is available without providers or execution. Next authorized artifact: `MIP_LLM_READ_ONLY_CONVERSATIONAL_FRONT_DOOR_001`.
- `MIP_GUIDED_MEASUREMENT_WORKSPACE_VERTICAL_JOURNEY_001`, `MIP_GUIDED_MEASUREMENT_WORKSPACE_ANSWER_LAYER_001`, and `MIP_GUIDED_MEASUREMENT_WORKSPACE_UPLOAD_READINESS_001` remain retained but dependency-gated or superseded by the control-plane tasks; no disconnected implementation may proceed.
