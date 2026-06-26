# Marketing Intelligence Platform (MIP)

Causal marketing intelligence **control plane** for governed experimentation, MMM calibration, budget planning, explainable recommendations, and—eventually—a conversational workbench over certified analytical engines.

## Public Demo

**Hosted demo:** [https://marketingintelligenceplatform.streamlit.app/](https://marketingintelligenceplatform.streamlit.app/)

| | |
|---|---|
| **Mode** | Deterministic — no LLM provider configured or required |
| **Data** | Synthetic/local demo fixtures only |
| **Secrets / external services** | None |

**Workflows shown:** cold-start advisory · demo profiling / readiness · calibration mapping · intake overview

**What it is:** A governed **control-plane / workflow shell** that demonstrates MIP contracts, evidence labels, blocked-claim guardrails, and readiness-style reports over built-in fixtures.

**What it is not:** A production app, API service, or measurement engine. It does **not** run MMM or GeoX engines, call LLM providers, persist uploads, or claim causal lift, ROI, power/MDE, matched markets, treatment assignment, or optimized budgets.

**Deployment record:** [PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md](docs/demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md)

## What this is

MIP is the **control-plane layer** for causal marketing intelligence. It owns contracts, evidence, release gates, `TrustReport` assembly, orchestration boundaries, and the planned LLM Decision Layer. Statistical engines compute estimands, run inference, and emit artifacts; MIP governs what may be trusted, promoted, or explained.

**MMM** and **GeoX/panel_exp** remain **separate analytical engine repositories**. MIP connects to those engines through **versioned adapters and governed contracts**—not by vendoring engine source inside this repo.

The intended product direction is a **local-first causal marketing intelligence workbench**: users describe a business goal, provide data, receive guidance on KPIs and controls, run diagnostics, draft configs, execute MMM and GeoX workflows through adapters, inspect governed artifacts, view dashboards and reports, and ask follow-up questions—all through an LLM-guided interface that routes to certified tools rather than inventing causal effects.

## Current implemented spine

The following is **implemented and tested** in this repository today:

| Area | Status |
|------|--------|
| **Contracts** | Pydantic models for estimands, experiment evidence, calibration signals, decision surfaces, recommendations, and `TrustReport` |
| **Evidence registry** | In-memory registry with add/get/list/find and trust-report helpers |
| **Evaluation gates** | Release gates for evidence, calibration, decision surfaces, recommendations, and trust reports |
| **TrustReport assembly/router** | Gate-driven confidence tiers, trust report construction, artifact routing |
| **Calibration audit** | Trace and audit calibration signals against source evidence |
| **Model calibration readiness** | Evaluate whether a model has compatible, non-blocked calibration signals |
| **LLM safety layer (Phase 1)** | Deterministic intent classification, confidence-tier action policies, and `TrustReport` explanation context—**no real LLM calls** |
| **Objective intake framework (Phase 2)** | Deterministic mapping of business objectives to data requirements, declared availability checks, and feasibility reports—**no LLM calls** |
| **Data readiness diagnostics (Phase 3)** | Structural dataset profiling from records, readiness checks, and `DataReadinessReport` with optional objective feasibility integration—**no LLM calls or engine execution** |
| **Config drafting (Phase 4)** | Deterministic `MMMConfigDraft` and `GeoXConfigDraft` from objective, feasibility, and readiness—**no engine execution** |
| **Local workflow orchestrator (Phase 5A)** | `run_local_workflow()` wires intake → readiness → config draft into `WorkflowRunSummary`—**no UI or engine execution** |
| **Local CLI demo runner (Phase 5B)** | `mip-demo` reads JSON input and prints/saves a governed `WorkflowRunSummary`—**no Streamlit, LLM, or engine execution** |
| **Mock LLM explanation (Phase 5C)** | `MockLLMProvider` explains `WorkflowRunSummary` conversationally and deterministically—**no real LLM APIs or engine execution** |
| **Streamlit demo shell (Phase 5D, legacy)** | `mip-app` runs the legacy JSON + MockLLM shell in `mip.app.streamlit_app`—**canonical local/public demo is `app/streamlit_app.py`** |
| **Adapter interface contracts (Phase 6A)** | `mip.adapters` defines governed MMM/GeoX input/output bundle shapes—**no engine imports or model results** |
| **Adapter governance wiring (Phase 6B)** | Placeholder adapter outputs map to `ExperimentEvidence` / `DecisionSurface` fixtures, gates, and `TrustReport`—**no engine execution** |
| **MMM fixture dashboard/report (Phase 6C)** | `mip.reports.mmm_fixture` + Streamlit section show governed MMM placeholder flow—**no model execution** |
| **Workflow run manifest (Phase 7A)** | `mip.orchestration` defines `WorkflowRunManifest`, deterministic plan/manifest builders, and safety assertions—**no autonomous agents or LLM planning** |
| **Governed planner/router (Phase 7B)** | `mip.orchestration.router` selects allowed/blocked next actions from manifests—**display and routing only; no execution** |
| **Human approval checkpoints (Phase 7C)** | `mip.orchestration.approvals` tracks local approval requests and enforces `blocked_until_approved`—**no automatic approval or execution** |
| **Fixture engine orchestration (Phase 8A)** | `mip.orchestration.engine_fixtures` orchestrates MMM/GeoX adapter fixture paths—**placeholder outputs only** |
| **Pinned sibling fixture imports (Phase 8B)** | `mip.adapters.sibling_fixtures` reads committed sibling-repo export JSON fixtures through adapter governance—**no live engine execution** |
| **Read-only sibling export hooks (Phase 8C)** | `mip.adapters.sibling_export_hooks` discovers static JSON exports from explicit directories—**no sibling code execution** |
| **Sibling repo compatibility registry (Phase 8D)** | `mip.adapters.sibling_compatibility` validates configured export paths and schema contracts before discovery—**read-only** |
| **Local sibling export path wiring (Phase 8E)** | `mip.adapters.local_sibling_paths` wires default local `mmm`/`panel_exp` export directories through compatibility checks—**read-only JSON only** |
| **Sibling export producer specs (Phase 8F)** | `docs/integrations/*_PRODUCER_SPEC.md` and `mip.adapters.sibling_producer_specs` define the sibling-side JSON writer contract—**no sibling code execution** |
| **Architecture and roadmap docs** | Vision, ADRs, glossary, operating model, multi-repo integration, LLM vision, semantic/decision-readiness, critical invariants, conversational intake, and **governed agent role registry** (P8b) / agentic workflow governance roadmaps |

**Not implemented yet:** MMM/GeoX engine execution, dashboards, reports, cloud or Ollama LLM providers, APIs, statistical model diagnostics, or autonomous agents. No fake statistical results or placeholder estimators in engine paths.

## Target product experience

The long-term user flow MIP is designed to support:

```text
User business question
  → domain / objective intake
  → data requirement guidance (KPIs, controls, granularity)
  → data readiness diagnostics
  → MMM / GeoX config draft
  → engine execution via adapters
  → governed artifacts (evidence, surfaces, recommendations)
  → TrustReport
  → dashboard / report
  → follow-up Q&A over structured artifacts
```

Users should eventually be able to:

- Describe a business goal and receive guidance on required KPIs, controls, and data granularity
- Upload or point to local data and run readiness diagnostics
- Draft MMM and GeoX configurations for engine validation and execution
- Inspect outputs with tier-appropriate language, warnings, and blockers
- View local dashboards and export governed reports
- Ask follow-up questions grounded in artifacts, lineage, and `TrustReport`

This experience is **planned**, not shipped. The governance spine above exists so future UI and LLM layers can be contract-driven from day one.

## LLM Decision Layer

The **LLM Decision Layer lives in MIP**, not inside the MMM or GeoX engine repos. It is intended to become the **primary interaction layer** for users: guiding intake, routing workflows, drafting configs, summarizing artifacts, and explaining `TrustReport` verdicts.

### What LLMs will do

- Guide users through objective and data intake
- Configure and route approved workflows
- Summarize diagnostics, gates, and uncertainty
- Explain `TrustReport`, evidence quality, and calibration readiness
- Surface measurement gaps and experiment opportunities
- Draft MMM/GeoX configs for engine validation
- Support follow-up Q&A over governed artifacts

### What LLMs will not do

- Estimate causal effects or run GeoX inference directly
- Train MMM models or invent statistical results
- Certify evidence or upgrade confidence tiers
- Override `TrustReport` verdicts or bypass `CalibrationSignal` governance
- Send raw experiment evidence into MMM
- Approve production recommendations or bypass release gates

Production-facing results must pass evaluation gates and be labeled by **confidence tier** (`decision_ready`, `directional`, `diagnostic_only`, `research_only`, `blocked`).

### LLM implementation status

| Phase | Status |
|-------|--------|
| Phase 0 — Documentation and scope lock | **Done** |
| Phase 1 — Deterministic safety and explanation context | **Done** (`mip.llm`: intents, safety rules, `context_from_trust_report`) |
| Phase 2 — Business objective intake and data requirements | **Done** (`mip.workflows.intake`) |
| Phase 3 — Data readiness diagnostics | **Done** (`mip.workflows.readiness`) |
| Phase 4 — MMM/GeoX config drafting | **Done** (`mip.workflows.configs`) |
| Phase 5A — Local workflow orchestrator | **Done** (`mip.workflows.orchestrator`) |
| Phase 5B — Local CLI demo runner | **Done** (`mip.cli.demo`, `mip-demo`) |
| Phase 5C — MockLLM explanation provider | **Done** (`mip.llm.providers`, `mip.llm.explanations`) |
| Phase 5D — Streamlit demo shell (legacy) | **Done** (`mip.app.streamlit_app`, `mip-app`; canonical demo: `app/streamlit_app.py`) |
| Phase 6A — Adapter interface contracts | **Done** (`mip.adapters`) |
| Phase 6B — Adapter fixture governance wiring | **Done** (`mip.adapters.governance`) |
| Phase 6C — MMM fixture dashboard/report demo | **Done** (`mip.reports.mmm_fixture`) |
| Phase 7A — Workflow run manifest governance | **Done** (`mip.orchestration`) |
| Phase 7B — Governed planner/router | **Done** (`mip.orchestration.router`) |
| Phase 7C — Human approval checkpoints | **Done** (`mip.orchestration.approvals`) |
| Phase 8A — Fixture engine orchestration | **Done** (`mip.orchestration.engine_fixtures`) |
| Phase 8B — Pinned sibling fixture adapter imports | **Done** (`mip.adapters.sibling_fixtures`) |
| Phase 8C — Read-only sibling export hooks | **Done** (`mip.adapters.sibling_export_hooks`) |
| Phase 8D — Sibling repo compatibility registry | **Done** (`mip.adapters.sibling_compatibility`) |
| Phase 8E — Local sibling export path wiring | **Done** (`mip.adapters.local_sibling_paths`) |
| Phase 8F — Sibling export producer specs | **Done** (`docs/integrations/`, `mip.adapters.sibling_producer_specs`) |
| Semantic/decision-readiness tracks S1–S12 | **Documented** ([addendum](docs/roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)); not implemented |
| Critical invariants + artifact selection G1–G20 | **Documented** ([addendum](docs/roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md)); final governance roadmap layer |
| Conversational intake + data handoff I1–I15 | **Documented** ([roadmap](docs/roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)); not implemented |
| Intake session contracts I1–I3 | **First product implementation** |
| Phase 8G+ — LLM explanation payload, usage policy | **Next implementation** (G11–G20 as design constraints) |
| Live engine adapters | **Planned** (blocked until golden scenarios + 8G–8H) |

Provider order for **product surface (P7b):** **`disabled`/deterministic first** (default; no LLM required), then `local_ollama` for local dev, then `bring_your_own_key`, then optional `hosted_open_source` (experimental), then `platform_managed_key_later` (gated). **Canned/sample explanation modes are excluded** (`canned_demo`, `sample_explanation`, `template_llm_explanation`)—the platform should be either honestly deterministic or actually LLM-backed through an explicit provider.

Phase 5C `MockLLMProvider` remains for early deterministic workflow tests; P7b product surface does **not** use canned explanations for user-facing demos.

The public product surface should work without paid LLM infrastructure. Deterministic mode is the default. Optional LLM-backed explanations may use hosted open-source models, local Ollama for local use, or bring-your-own-key providers.

**The LLM explains governed MIP outputs; it does not create measurement authority.**

See [docs/architecture/LLM_DECISION_LAYER_VISION.md](docs/architecture/LLM_DECISION_LAYER_VISION.md), [docs/roadmap/LLM_DECISION_LAYER_ROADMAP.md](docs/roadmap/LLM_DECISION_LAYER_ROADMAP.md), [docs/roadmap/LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md](docs/roadmap/LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md), [docs/roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](docs/roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md), [docs/roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](docs/roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md), and [docs/roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](docs/roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md) for delivery phases, semantic readiness, artifact selection policies (G11–G20), intake/data handoff (I1–I15), and design constraints for 8G/8H.

## Local-first workbench and UI access

Initial product direction is **local-first**, with a **verified public hosted demo** on Streamlit Community Cloud.

### UI access modes

**Local UI** — user runs the app locally (e.g. `streamlit run`); access through `localhost`; best for development, private demos, debugging, and demo recordings.

**Public hosted UI** — [deterministic public demo](https://marketingintelligenceplatform.streamlit.app/) on Streamlit Community Cloud; best for portfolio demos, stakeholder review, and lightweight product validation. Demo-safe, no paid infrastructure required. **Not production readiness.**

```text
poetry install
  → mip demo / mip app   (planned CLI entry points)
  → localhost UI opens (P7)
  → optional public URL (P9)
  → user provides local or demo data
  → diagnostics, workflows, dashboards, reports run locally
  → follow-up Q&A over governed report payloads (deterministic or explicit LLM provider)
```

- **Streamlit/Gradio** is planned first for demo speed and iteration (P7 local UI, P9 public demo)
- **FastAPI / Docker** is a later service/deployment layer (P10–P11), not required for the first UI demo
- Marketing data stays on the user's machine in early releases
- Reports export to local run folders (HTML first, Markdown second, PDF later)

No cloud accounts, remote data upload, or autonomous production actions are required for the initial experience.

See [docs/architecture/LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md](docs/architecture/LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md).

## Repository architecture

Three-repo model:

| Repository | Role |
|------------|------|
| **MIP** (this repo) | Control plane: contracts, evidence, gates, `TrustReport`, orchestration, LLM layer, workflows, dashboards, reports, adapters |
| **mmm** | MMM analytical engine: training, Δμ surfaces, diagnostics |
| **panel_exp / GeoX** | Experimentation engine: geo/panel lift, design and inference diagnostics |

MIP consumes engine outputs through **`src/mip/adapters/{mmm,geox}/`** (planned). Engines expose integration hooks under their own repos (e.g. `mmm/integrations/mip/`, `panel_exp/integrations/mip/`). MIP does not vendor engine source.

See [docs/architecture/REPO_INTEGRATION_STRATEGY.md](docs/architecture/REPO_INTEGRATION_STRATEGY.md).

## Governance principles

- **`TrustReport`** is the sole trust verdict on engine and recommendation outputs; every production-facing path is tier-labeled.
- **`CalibrationSignal`** is the only governed path from experiment evidence into MMM calibration—not raw experiment payloads.
- **Release gates** block or downgrade artifacts that fail diagnostics, compatibility, or evidence requirements.
- **Research vs production:** `research_only` and `diagnostic_only` tiers may inform exploration but not production automation without explicit human review.
- **Full-panel Δμ** is the decision estimand for mix-level budget decisions (see ADR-001).
- **LLMs explain and route**; statistical systems compute and certify.

## Current status

**Platform spine: largely complete.** Contracts, gates, trust assembly, evidence registry, calibration audit, model calibration readiness, and LLM Phase 1–5D deterministic workflow layers are implemented with passing tests.

**Product surface:** **P7** local deterministic Streamlit shell (`app/streamlit_app.py`) plus **P7b** LLM provider/explanation governance contracts. Phase 5D `mip-app` legacy shell remains for earlier workflow demos. See [Product entrypoint and demo experience plan](docs/product/PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md) for the planned single-page, chat-first product direction. See [Synthetic demo dataset strategy](docs/product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md) for canonical MIP-owned demo fixtures, industry reference schemas, and when to introduce engine-backed MMM/GeoX visuals.

**Near-term focus:** **P10c** Docker local smoke complete on feature branch; **P11** API hardening next. Public demo: https://marketingintelligenceplatform.streamlit.app/

## Roadmap

| Document | Contents |
|----------|----------|
| [Platform roadmap](docs/roadmap/ROADMAP.md) | Phased delivery across contracts, engines, trust, APIs, orchestration |
| [LLM Decision Layer vision](docs/architecture/LLM_DECISION_LAYER_VISION.md) | Product vision, responsibilities, and hard boundaries |
| [LLM Decision Layer roadmap](docs/roadmap/LLM_DECISION_LAYER_ROADMAP.md) | Phased LLM and workbench delivery |
| [LLM reasoning and model guidance](docs/roadmap/LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md) | Phases 8G–8N: explanation payloads, usage policy, eval harness |
| [Semantic and decision-readiness roadmap](docs/roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md) | S1–S12: metrics, estimands, scope, actions, decision packets |
| [Critical invariants and golden scenarios](docs/roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md) | G1–G20: product proof, artifact selection, ambiguity policies |
| [Conversational intake and data handoff](docs/roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md) | I1–I15: LLM conversation → upload/connect → readiness → export handoff |
| [Platform completion gaps](docs/roadmap/PLATFORM_COMPLETION_GAPS_ROADMAP.md) | P1–P13: lifecycle, audit, certification |
| [Roadmap execution sequence](docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md) | Consolidated P0–P20 implementation phases |
| [Roadmap execution audit](docs/audits/ROADMAP_EXECUTION_AUDIT_001.md) | Theme grouping, blockers, canonical ownership |
| [Local-first app strategy](docs/architecture/LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md) | `mip demo` / `mip app`, Streamlit, providers, local artifacts |
| [Repo integration strategy](docs/architecture/REPO_INTEGRATION_STRATEGY.md) | Three-repo boundaries and adapter contracts |

**P1 implemented:** deterministic intake session and path recommendation contracts (`MMMIntakeSession`, `GeoXIntakeSession`, `IntakePathRecommendation`, `recommend_intake_path`).

**P2 implemented:** required data asset and sample schema expectation contracts (`IntakePlan`, `RequiredDataAsset`, `build_intake_plan`). After a path recommendation, MIP can show the expected data shape before upload/connect.

**P3 implemented:** `DataSourceRef` and intake manifest contracts (`MMMIntakeManifest`, `GeoXIntakeManifest`, `build_intake_manifest`). MIP can represent user-selected data source modes and tie them to session/recommendation/plan.

**P4 implemented:** column mapping and semantic confirmation contracts (`ColumnMappingProposal`, `ColumnMappingConfirmation`, `SemanticMappingReport`, `build_semantic_mapping_report`).

**P4b implemented:** experiment design objective and data requirement contracts (`ExperimentDesignObjective`, `ExperimentDesignIntake`, `MMMToGeoXDesignBridge`, `StandaloneGeoXDesignRequest`, `ExperimentDiagnosticRequest`, `build_experiment_design_intake`, `build_experiment_diagnostic_request`). MIP can represent MMM-driven and standalone GeoX design intent, map objectives to candidate KPI families, list objective-specific data requirements, and prepare future panel_exp diagnostic requests without executing design diagnostics.

**P4c implemented:** common data intake workbench and preliminary profiling contracts (`CommonIntakeWorkbench`, `CommonDataProfileSummary`, `WorkflowSupportAssessment`, `LLMAnswerGroundingContext`, `build_common_intake_workbench`, `build_workflow_support_assessment`). MIP can represent shared intake metadata, governed profile summaries, workflow support assessment, and LLM-safe grounding context across MMM, GeoX, CalibrationSignal, and decision-review workflows. Actual ingestion, file parsing, table connectors, profiling computation, and engine diagnostics remain deferred.

**P5 implemented:** workflow-specific readiness report contracts (`MMMDataReadinessReport`, `GeoXDesignReadinessReport`, `CalibrationSignalReadinessReport`, `DecisionReviewReadinessReport`, `build_workflow_readiness_reports`). MIP can now branch from common intake/workflow support assessment into MMM data readiness, GeoX design readiness, CalibrationSignal readiness, and decision-review readiness. These reports assess structural readiness only; engine diagnostics, CalibrationSignal transformation, TrustReport approval, and decision recommendations remain deferred.

**P5b implemented:** general advisory and cold-start planning contracts (`ColdStartBusinessProfile`, `ColdStartAdvisoryPlan`, `WebsiteTrafficSourceProfile`, `build_cold_start_advisory_plan`). MIP can now represent advisory-only marketing guidance for users without formal measurement readiness, including business-profile-driven channel hypotheses, website traffic/source-informed hypotheses, tracking setup checklists, starter measurement plans, and learning agendas. Outputs are labeled by evidence mode and claim type and cannot claim ROI, causal lift, optimal mix, or decision authorization.

**P6 implemented:** CalibrationSignal intake mapping contracts (`CalibrationEvidenceInput`, `CalibrationMappingRequirement`, `CalibrationMappingReport`, `map_evidence_to_calibration_signal`). MIP can now validate governed experiment evidence for CalibrationSignal compatibility, preserve source lineage, and map structurally valid evidence into `CalibrationSignal` contracts. This does not execute MMM calibration, estimate effects, certify causality, or approve decisions.

**P7 implemented:** Local deterministic Streamlit workflow shell (`app/streamlit_app.py`). The UI exposes cold-start advisory, workflow readiness, CalibrationSignal mapping, and intake overview flows using sample fixtures and MIP core helpers. Deterministic mode only—no LLMs, MMM, GeoX, external APIs, or public hosting.

**P7b implemented:** Pluggable LLM provider and explanation-governance contracts (`LLMProviderConfig`, `LLMExplanationRequest`, `LLMExplanationPlan`, `mip.workflows.intake.llm_explanation`). Represents disabled/deterministic, local Ollama, hosted open-source, BYOK, and future platform-managed-key modes. No LLM provider calls; governed input boundaries and explanation plans only.

**P8 implemented:** Local/demo profiling for small synthetic tabular datasets (`mip.contracts.demo_profile`, `mip.workflows.intake.demo_profiling`). Demo profiles summarize website traffic, national media/outcome, DMA-week media/outcome, and experiment readout-like data into governed summaries used by advisory, readiness, and CalibrationSignal mapping workflows. Demo-only: no production ingestion, external connectors, raw-row LLM access, MMM/GeoX execution, or persistent storage.

**P8b implemented:** Governed agent role, run manifest, failure packet, resolution plan, validation report, retry policy, escalation policy, and handoff packet contracts (`mip.contracts.agentic_workflow`, `mip.workflows.intake.agentic_recovery`). Prepares future agentic orchestration without LangGraph, runtime agents, LLM calls, autonomous retries, MMM execution, or GeoX execution. Agents remain reasoning/recovery surfaces, not measurement authorities.

**P8c implemented:** Canonical Streamlit entrypoint clarified before public hosting. `app/streamlit_app.py` is the local/public deterministic demo app. Legacy `mip.app.streamlit_app` / `mip-app` remain for Phase 5D JSON workflow compatibility only.

**P9 implemented:** Deterministic public demo preparation. `requirements.txt`, `runtime.txt`, and `.streamlit/config.toml` support Streamlit Community Cloud hosting of `app/streamlit_app.py` without LLM providers, secrets, FastAPI, Docker, or external services.

**P9b implemented:** Deterministic public demo deployed and smoke-tested on Streamlit Community Cloud. Deployment record: [PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md](docs/demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md). This is a **non-production** deterministic demo using synthetic fixtures—not a production app or measurement service.

**P10a implemented:** FastAPI service shell at `mip.service` with `GET /health` and `GET /version`.

**P10b implemented:** Deterministic workflow API routes (`POST /advisory/cold-start`, `/readiness/assess`, `/calibration/map`, `/intake/overview`) using demo fixture keys.

**P10b.1 implemented:** Service boundary cleanup—routes call `mip.workflows.*` directly; `app.demo_fixtures` limited to sample input resolution. See [Deterministic usage modes](docs/service/DETERMINISTIC_USAGE_MODES.md).

**P10c (feature branch):** Dockerfile for local deterministic FastAPI smoke testing. See [P10c Docker smoke report](docs/service/P10C_DOCKER_SERVICE_SMOKE_REPORT.md).

**Next (implementation):** See [Roadmap execution sequence](docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md). **P11** — hosted API hardening after P10c merge.

1. **P11** — Hosted API hardening (auth, rate limits, privacy, cost controls)
2. **P17** — LangGraph orchestration skeleton (after P8b contracts stabilize)

Live engine execution remains blocked until golden scenarios and safety evaluations exist.

## Repository layout

```text
marketing_intelligence_platform/
  README.md
  pyproject.toml
  requirements.txt   # P9 Streamlit Community Cloud runtime dependencies
  runtime.txt        # Python 3.11 for hosted demo
  .streamlit/        # Headless demo UI config (no secrets)
  app/               # Canonical local/public Streamlit demo (P7/P8/P9)
  docs/
    vision/           # Vision and principles
    architecture/     # Layers, boundaries, trust, LLM, local-first
    roadmap/          # Phased delivery
    audits/           # Roadmap execution audits
    adr/              # Architecture decision records
    glossary/         # Estimands and measurement terms
    operating_model/  # Intake, evaluation, release gates
  src/mip/
    contracts/        # Governed Pydantic contracts
    evidence/         # Registry, calibration audit, readiness
    evaluation/       # Release gates
    trust/            # TrustReport assembly and routing
    llm/              # Deterministic safety and explanation context (Phase 1)
    workflows/        # Workflow intake, readiness, configs, orchestrator (Phase 2–5A)
      intake/         # Business objectives, data requirements, feasibility
      readiness/      # Dataset profiling and readiness reports
      configs/        # MMM and GeoX config drafts
      orchestrator/   # Local workflow runner and summary
    orchestration/    # Workflow manifest, planner router, approvals, fixture engines (Phase 7A–8A)
    app/              # Legacy Phase 5D Streamlit shell (`mip-app`); canonical demo is `app/`
    dashboard/        # Planned: tier-aware views
    reports/          # Planned: governed report export
  tests/              # Pytest suites
```

## Documentation index

- [Platform vision](docs/vision/PLATFORM_VISION.md)
- [Platform principles](docs/vision/PLATFORM_PRINCIPLES.md)
- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Orchestration boundaries](docs/architecture/ORCHESTRATION_BOUNDARIES.md)
- [Trust architecture](docs/architecture/TRUST_ARCHITECTURE.md)
- [LLM Decision Layer vision](docs/architecture/LLM_DECISION_LAYER_VISION.md)
- [Local-first app strategy](docs/architecture/LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md)
- [Repo integration strategy](docs/architecture/REPO_INTEGRATION_STRATEGY.md)
- [Public demo deployment record (P9b)](docs/demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md)
- [P10 FastAPI/Docker wrapper plan](docs/service/P10_FASTAPI_DOCKER_WRAPPER_PLAN.md)
- [P10c Docker service smoke report](docs/service/P10C_DOCKER_SERVICE_SMOKE_REPORT.md)
- [Product entrypoint and demo experience plan](docs/product/PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md)
- [Synthetic demo dataset strategy](docs/product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md)
- [Deterministic usage modes](docs/service/DETERMINISTIC_USAGE_MODES.md)
- [Agentic workflow governance roadmap](docs/architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md)
- [Roadmap](docs/roadmap/ROADMAP.md)
- [LLM Decision Layer roadmap](docs/roadmap/LLM_DECISION_LAYER_ROADMAP.md)
- [LLM reasoning and model guidance](docs/roadmap/LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md)
- [Semantic and decision-readiness roadmap](docs/roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [Critical invariants and golden scenarios](docs/roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md)
- [Conversational intake and data handoff](docs/roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
- [Platform completion gaps](docs/roadmap/PLATFORM_COMPLETION_GAPS_ROADMAP.md)
- [Roadmap execution sequence](docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
- [Roadmap execution audit](docs/audits/ROADMAP_EXECUTION_AUDIT_001.md)
- ADRs: [001 Δμ](docs/adr/ADR-001-full-panel-delta-mu-decision-surface.md) · [002 Experiments](docs/adr/ADR-002-experiments-as-calibration-evidence.md) · [003 LLM orchestration](docs/adr/ADR-003-llm-orchestration-over-certified-tools.md)

## Run local UI (canonical)

**Canonical local demo app:**

```bash
poetry run streamlit run app/streamlit_app.py
```

`app/streamlit_app.py` is the local/public deterministic demo entrypoint for P7/P8 workflows (advisory, readiness, calibration mapping, demo profiling, intake overview).

The app runs in **deterministic mode by default**. It does not require LLM providers, API keys, FastAPI, Docker, or external services.

**Legacy Phase 5D workflow shell** (JSON input + MockLLM over `run_local_workflow()`): retained for backward compatibility only.

```bash
poetry run mip-app
```

This launches `src/mip/app/streamlit_app.py`—a separate shell from the canonical demo above.

## Public demo deployment

**Hosted demo:** [https://marketingintelligenceplatform.streamlit.app/](https://marketingintelligenceplatform.streamlit.app/)

**Canonical app entrypoint:** `app/streamlit_app.py`

**Local command:**

```bash
poetry run streamlit run app/streamlit_app.py
```

**Hosting:** Streamlit Community Cloud — main file `app/streamlit_app.py`, Python 3.11 (`runtime.txt`), dependencies from `requirements.txt`.

The public demo is **deterministic-only** and requires **no secrets**, API keys, LLM providers, FastAPI, Docker, databases, or external services. It is **not production-ready**—a governed workflow shell over synthetic demo fixtures.

**Deployment record:** [PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md](docs/demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md) (P9b verified; commit `96cf98c`).

**Re-deploy checklist:**

- `poetry run pytest` passes
- `poetry run ruff check .` passes
- `poetry run mypy src tests app` passes
- No secrets committed (no `.env`, `secrets.toml`, or tokens in repo)
- `requirements.txt` present at repository root
- Canonical app path confirmed: `app/streamlit_app.py`
- Deterministic mode and Public Demo Safety copy visible in the app
- No LLM provider selector or API-key fields exposed in the canonical app

**Optional secondary host:** [Hugging Face Spaces](https://huggingface.co/docs/hub/spaces) can host a Streamlit demo later. Prefer the simple Streamlit Community Cloud path first. Docker-based Spaces belong to the later FastAPI/Docker phase (P10c) unless needed sooner.

## Local API shell (P10a–P10b.1)

Streamlit remains the **canonical public demo**. The FastAPI shell (`mip.service`) exposes deterministic workflow routes.

```bash
poetry run uvicorn mip.service.app:app --reload --host 127.0.0.1 --port 8000
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/version
curl -X POST http://127.0.0.1:8000/advisory/cold-start -H 'Content-Type: application/json' -d '{"sample_key":"dtc_skincare_ecommerce"}'
```

Deterministic mode only — no LLM, secrets, external services, persistence, or measurement engine execution.

## Local Docker smoke (P10c)

Packages the **FastAPI service only** for local smoke testing. Does not run Streamlit, enable LLM mode, or imply production deployment.

```bash
docker build -t mip-service:p10c .
docker run --rm -p 8000:8000 mip-service:p10c
# another shell:
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/version
```

If port 8000 is busy, map another host port: `docker run --rm -p 8001:8000 mip-service:p10c`.

See [P10c Docker service smoke report](docs/service/P10C_DOCKER_SERVICE_SMOKE_REPORT.md).

## Development setup

Requires Python ≥ 3.11. Uses Poetry-compatible `pyproject.toml`.

```bash
cd marketing_intelligence_platform
poetry install
poetry run pytest
poetry run ruff check src tests
poetry run mypy src
```

Minimal runtime dependencies: `pydantic`, `pandas`, `numpy`. Dev tools: `pytest`, `ruff`, `mypy`.

## License

TBD.
