# Repository Integration Strategy

## 1. Purpose

This document records how the Marketing Intelligence Platform (MIP) integrates with external analytical engine repositories—GeoX/panel experimentation and MMM—without absorbing their source trees.

The goal is to prevent architecture drift: monorepo creep, vendored copies, ad-hoc imports of private engine internals, and ambiguous ownership of contracts and adapters.

## 2. Decision summary

**MIP will not absorb MMM and GeoX as copied subdirectories.**

Instead:

- **GeoX / panel_exp** remains an independent experimentation engine repository.
- **MMM** remains an independent modeling and planning engine repository.
- **MIP** consumes both through **versioned dependencies** and **adapter interfaces**.
- MIP depends on **public engine outputs** (contract-shaped artifacts), not internal implementation details.
- **Local development** uses editable path dependencies.
- **Stable integration** uses Git tags or commit pins.
- **Long-term compatibility** is enforced through hooks, CI, and contract tests.

## 3. Repository roles

### `marketing_intelligence_platform` (MIP)

Control plane and governance layer:

- Contracts (`Estimand`, `ExperimentEvidence`, `CalibrationSignal`, `DecisionSurface`, `RecommendationContract`, `TrustReport`)
- Evidence registry and calibration governance
- Release and readiness gates
- Trust assembly and artifact trust router
- Model calibration readiness
- Orchestration and future LLM decision workflows
- Cross-system recommendations

MIP does **not** own geo matching, SCM/TBR/DID inference, MMM fitting, or portfolio optimization math.

### Common Data Intake Workbench

**Common intake first, workflow-specific readiness second.** MIP owns one shared intake workbench (source registration, manifests, mapping, snapshots, structural profiling, `WorkflowSupportAssessment`). Users do not maintain separate MMM and GeoX upload flows. After common intake, readiness branches: MMM-specific · GeoX/experiment-design · CalibrationSignal · decision-review. Users **not** ready for formal measurement route to **general advisory / cold-start planning** (P5b).

| Layer | Owns | Does not own |
|-------|------|--------------|
| **MIP common intake** | Workbench, snapshots, mapping, profiling summaries, workflow support assessment, LLM grounding context | Power, MDE, matching, model fitting |
| **MIP advisory / cold-start (P5b)** | Business profile capture, channel hypotheses, traffic-source advisory, tracking checklists, learning agendas, evidence/claim labeling | Channel ROI models, budget optimization, causal certification |
| **MMM** | MMM sufficiency, media time-series, calibration, refresh diagnostics | Geo design execution |
| **panel_exp / GeoX** | Power/MDE, matchability, design feasibility, readout | Intake workbench, readiness tier certification |
| **LLM** | Clarification, labeled advisory hypotheses, explanation of governed reports | Raw-file analysis, feasibility certification, ROI/optimal-mix claims without evidence |

**Advisory evidence hierarchy:** general knowledge → business profile → customer data summaries → measured diagnostics → `TrustReport`-authorized decision support. Referral, organic, social, email, CRM, and sales summaries may inform cold-start hypotheses but do not authorize causal or ROI claims.

See [ROADMAP_EXECUTION_SEQUENCE.md](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md) P4c, P5b and [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](../roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md) I6c, I8b.

### Product surface architecture layers (P7–P11)

| Layer | Role |
|-------|------|
| **Core MIP package** | Contracts, gates, readiness reports, advisory plans, CalibrationSignal mapping, `TrustReport`, deterministic validators |
| **UI layer** | Streamlit/Gradio: chat, forms, uploads, workflow selection, report cards, warnings, evidence labels |
| **FastAPI layer** | HTTP boundary for programmatic access, auth, rate limits, frontend/backend separation (P10) |
| **Docker layer** | Portable deployment across local, Hugging Face Spaces, Render, Railway (P10) |

```text
First demo path:     User → UI → MIP core package
Later production:    User → UI → FastAPI → MIP core package
Docker wraps UI/API/package for portable deployment.
```

**Canonical Streamlit entrypoint (P8c):** `app/streamlit_app.py` — run with `poetry run streamlit run app/streamlit_app.py`. Deterministic mode by default; no LLM providers, API keys, FastAPI, Docker, or external services required. Legacy Phase 5D shell (`src/mip/app/streamlit_app.py`, `mip-app`) retained for JSON workflow + MockLLM compatibility only.

**Public demo preparation (P9):** `requirements.txt`, `runtime.txt` (Python 3.11), and `.streamlit/config.toml` prepare Streamlit Community Cloud hosting of the canonical deterministic app. The first public hosted demo is deterministic-only—no LLM providers, BYOK, secrets, FastAPI, Docker, databases, persistent storage, or external connectors. Hugging Face Spaces is documented as an optional secondary host; Docker-based Spaces belong to P10.

**Public demo deployment (P9b):** Deterministic public demo verified on Streamlit Community Cloud (commit `96cf98c`). **Hosted URL:** https://marketingintelligenceplatform.streamlit.app/ — record: [PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md](../demo/PUBLIC_DEMO_DEPLOYMENT_RECORD_P9B.md). Non-production demo shell over synthetic fixtures—not a measurement engine or production service.

**Service wrapper (P10–P11):** [P10_FASTAPI_DOCKER_WRAPPER_PLAN.md](../service/P10_FASTAPI_DOCKER_WRAPPER_PLAN.md) and [P11_API_HARDENING_AND_SERVICE_PACKAGING_PLAN_001.md](../service/P11_API_HARDENING_AND_SERVICE_PACKAGING_PLAN_001.md) define the FastAPI/Docker boundary and next API hardening direction. **P10a–P10c** implemented (`GET /health`, `GET /version`, workflow `POST` routes, service boundary cleanup, local Docker smoke). **P11** plan accepted—contract/OpenAPI/error stability before SDK examples. Hosted auth/rate limits remain deferred. Streamlit remains the canonical public demo.

FastAPI is not required for the first UI demo. Docker is not the app—it packages the app for consistent deployment. P10 must not duplicate MIP business logic.

**Product entrypoint direction (docs):** [PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md](../product/PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md) records the accepted future UX: single-page landing, chat-first Ask MIP, guided demo journeys, output previews, and data-needed-by-decision education. [SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md](../product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md) records canonical MIP-owned synthetic demo fixtures (Stage A deterministic, Stage B engine-backed), industry schema references, and the no-mock-final-dashboard rule. The current Streamlit app remains a deterministic governance console and will evolve toward that layout in later phases—not in docs-only steps.

**UI access:** Local (`localhost`) for dev/private demos; public URL (Streamlit Community Cloud, Hugging Face Spaces) for portfolio/stakeholder demos. Public demo must work without platform-paid LLM dependency.

See [ROADMAP_EXECUTION_SEQUENCE.md](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md) P7–P11.

### Governed agent roles vs engine execution (P8b)

MIP may add **governed specialist agents** (intake routing, data readiness, advisory, MMM/GeoX/calibration specialists, failure recovery, evaluator/validator) as reasoning and recovery surfaces. Agents use typed handoff contracts (`AgentRunManifest`, `AgentFailurePacket`, `AgentResolutionPlan`, `AgentValidationReport`, etc.) documented in P8b.

| Layer | Owns execution | MIP agent role |
|-------|----------------|----------------|
| **MMM** | Model fitting, diagnostics, refresh, calibration math | Explain readiness, blocked paths, failures; propose safe remediation |
| **panel_exp / GeoX** | Power/MDE, matchability, design feasibility, readout inference | Explain structural support/blocks; route to diagnostics when readiness allows |
| **MIP contracts** | Readiness, advisory claim guards, CalibrationSignal mapping, TrustReport, gates | Authoritative status; agents may not override |

Agents are **not** measurement authorities. LangGraph/stateful orchestration (P17) implements routing using P8b contracts—it does not replace engine execution or gate logic.

See [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](./AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md).

### `panel_exp` / GeoX

Experimentation engine repository:

- Experiment design
- Matching
- Power / MDE
- SCM, TBR, DID, and related methods
- Experiment diagnostics
- Emits **ExperimentEvidence-compatible** artifacts (via adapter mapping)

### `mmm`

Modeling and planning engine repository:

- Data validation and transforms
- Model training
- Replay calibration
- Full-panel Δμ simulation (production decision surface per ADR-001)
- Optimization
- Reliability diagnostics
- Emits **DecisionSurface-compatible** artifacts
- Consumes **CalibrationSignal-compatible** inputs (governed, not raw experiment dumps)

## 4. Dependency strategy

Integration proceeds in three phases.

### Phase 1: Local editable path dependencies

During active cross-repo development, MIP declares engines as path dependencies:

```toml
panel-exp = { path = "../panel_exp", develop = true }
mmm-package = { path = "../mmm", develop = true }
```

Use when engineers iterate on MIP adapters and engine outputs together on one machine.

### Phase 2: Git dependencies pinned to commit or tag

For reproducible builds and CI:

```toml
panel-exp = { git = "git@github.com:ORG/panel_exp.git", tag = "v0.3.0" }
mmm-package = { git = "git@github.com:ORG/mmm.git", tag = "v0.4.0" }
```

Pins are upgraded only after contract tests and compatibility gates pass.

### Phase 3: Optional shared `mip-contracts` package

Once schemas stabilize, core Pydantic contracts may be extracted to a small shared package consumed by MIP and engines. Until then, **MIP owns contract definitions**; engines align outputs through adapters and validation tests.

## 5. Adapter strategy

Adapters live in **MIP** and translate engine-native outputs into platform contracts. Engines may expose optional thin export helpers under `integrations/mip/`; those helpers produce engine-native DTOs or JSON—not MIP orchestration imports.

### Target layout (three repos)

```text
marketing_intelligence_platform/
  src/mip/
    contracts/          # shared platform contracts (owned here today)
    evidence/           # registry, calibration audit, model readiness
    evaluation/         # release gates
    trust/              # trust assembly, artifact router
    orchestration/      # workflow run manifest, plan builders (Phase 7A); planner/router (future)
    llm/                # LLM control plane (future)
      providers/
      prompts/
      safety/
      schemas/
    workflows/          # deterministic workflow graphs (future)
      intake/
      readiness/
      mmm/
      geox/
      scenario/
    dashboard/          # operator views (future)
    reports/            # structured report assembly (future)
    app/                # application entrypoints (future)
    adapters/           # engine → contract mapping (MIP-owned)
      mmm/
      geox/

mmm/
  src/mmm/
    modeling/
    diagnostics/
    optimization/
    integrations/mip/   # optional thin MIP export adapter (engine-owned)

panel_exp/
  panel_exp/
    design/
    inference/
    validation/
    integrations/mip/   # optional thin MIP export adapter (engine-owned)
```

### Boundary rule

| Side | Owns |
|------|------|
| **MIP `adapters/`** | Inbound mapping to `ExperimentEvidence`, `DecisionSurface`, registry registration, gate/trust hooks |
| **Engine `integrations/mip/`** | Outbound serialization of engine results into a stable export shape consumed by MIP adapters |
| **MIP `contracts/`** | Canonical schemas until optional `mip-contracts` extraction |

MIP adapters (Phase 6A — interface contracts implemented):

```text
src/mip/adapters/
  __init__.py
  base.py             # AdapterInputBundle, AdapterOutputBundle, validation
  mmm.py              # build_mmm_adapter_input, MMM placeholders
  geox.py             # build_geox_adapter_input, GeoX placeholders
```

These contracts define governed input/output bundle shapes only. They do not import engine packages, run MMM/GeoX, or emit model estimates.

**Phase 6B (implemented):** `mip.adapters.governance` maps completed placeholder `AdapterOutputBundle` artifacts into:

- GeoX → `ExperimentEvidence` fixture → experiment evidence gate → `TrustReport` → `EvidenceRegistry`
- MMM → `DecisionSurface` diagnostic fixture → decision surface gate → `TrustReport`

Failed/blocked adapter outputs produce blocked `TrustReport` values and are not registered as decision-ready artifacts. No engine execution or numeric effect claims.

**Phase 6C (implemented):** `mip.reports.mmm_fixture` and Streamlit MMM Fixture Governance Demo section show the governed MMM product shape from workflow summary through adapter placeholders to `DecisionSurface` fixture and `TrustReport`. No model execution.

**Phase 8B (implemented):** `mip.adapters.sibling_fixtures` loads pinned sibling-repo export JSON committed under `tests/fixtures/sibling_exports/`, validates structural metadata only, converts to `AdapterOutputBundle`, and routes through existing governance (`validate_adapter_output`, `register_adapter_output`, `TrustReport`). No sibling-repo Python imports or live engine execution.

**Phase 8C (implemented):** `mip.adapters.sibling_export_hooks` discovers `.json` files from explicitly provided sibling export directories (no symlinks by default), loads each through the Phase 8B schema, and registers valid exports through the same governance path. Malformed JSON and expectation mismatches produce blocked/invalid hook results without exception leakage.

**Phase 8D (implemented):** `mip.adapters.sibling_compatibility` adds a governed `SiblingRepoExportConfig` registry that resolves repo export paths, checks schema/source/engine compatibility via Phase 8C discovery, and only registers exports when status is `compatible` or `compatible_with_warnings`. No sibling code execution.

**Phase 8E (implemented):** `mip.adapters.local_sibling_paths` provides default local path wiring for sibling `mmm` and `panel_exp` export directories, builds compatibility registries, and registers exports only when compatible. Missing local repos return safe `not_found` results without crashing.

**Phase 8F (implemented):** Producer-side export specifications in `docs/integrations/` define the JSON contract sibling repos must write to `integrations/mip/exports/`. MIP is ready to consume static sibling exports via the 8B–8E read-only bridge. Next sibling-repo work should implement producer writers emitting the documented contract. This remains a file-based handoff—not a Python dependency or execution path. Live engine execution remains blocked on the MIP side.

**Semantic and decision-readiness tracks (documented, not implemented):** [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](../roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md) defines S1–S12: metric/KPI registry, estimand registry, scope alignment, business action ontology, role/decision rights, decision review packets, explanation templates, red-team prompts, export completeness scoring, source-of-truth policy, failure-mode catalog, and package release gates.

**Critical invariants and golden scenarios (documented, not implemented):** [PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](../roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md) defines G1–G10: golden end-to-end scenarios, demo artifacts, sibling conformance suite, schema compatibility, severity normalization, no-silent-upgrade invariant, local persistence, explanation rubric, decision packet gates, and roadmap dependency graph.

**Conversational intake and data handoff (documented, not implemented):** [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](../roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md) defines I1–I15: LLM-guided intake session → data source modes (upload/connect/local/production) → manifest → profiling → readiness report → refresh request → sibling export import. LLM guides; MIP validates; MMM/GeoX execute externally.

Engine integrations (optional, thin):

- `panel_exp/integrations/mip/` — export experiment result payloads
- `mmm/integrations/mip/` — export Δμ surfaces and accept calibration inputs

MIP must not import `mmm.modeling.*` or `panel_exp.inference.*` directly—only adapter surfaces and pinned package public APIs.

### Responsibilities

| Direction | Mapping |
|-----------|---------|
| GeoX output → MIP | `ExperimentEvidence` via `adapters/geox/` |
| MMM output → MIP | `DecisionSurface` (full-panel Δμ for production) via `adapters/mmm/` |
| MIP governance → MMM | `CalibrationSignal` via compatibility and readiness gates—not raw `ExperimentEvidence` |

Adapters are thin: field mapping, tier/status defaults, and registration into `EvidenceRegistry`. They do not reimplement statistical methods.

### MIP package status (current vs target)

| Package | Status |
|---------|--------|
| `contracts/`, `evidence/`, `evaluation/`, `trust/` | **Implemented** (constitution, gates, registry, readiness) |
| `experimentation/`, `mmm/`, `optimization/` | Placeholder stubs; logic stays in engine repos |
| `orchestration/` | Phase 7A–7C manifest, planner/router, approvals; Phase 8A fixture engine orchestration |
| `adapters/` | **Interface contracts + governance wiring implemented**; Phase 8A–8F fixture/export/compatibility/local-path/producer-spec paths |
| `reports/` | **MMM fixture governance report implemented** (`mmm_fixture.py`); HTML export deferred |
| `llm/`, `workflows/`, `app/` | **Implemented** (deterministic workflow spine + local demo shell) |
| `dashboard/`, `reports/` | **Not yet created** |

## 6. Local development workflow

1. Clone MIP, panel_exp, and mmm as sibling directories (or use a meta-workspace tool).
2. Point MIP `pyproject.toml` at local path dependencies (Phase 1).
3. Run engine in its repo; run adapter tests in MIP.
4. Register adapter outputs in `EvidenceRegistry` and validate with gates and `build_trust_report_for_artifact`.
5. Use pre-commit in each repo for hygiene (ruff, mypy, fast pytest).

MIP must remain importable and testable without engines installed when adapter tests use fixtures only.

## 7. Stable release workflow

1. Engine repo tags a release (e.g. `panel_exp v0.3.0`, `mmm v0.4.0`).
2. MIP updates Git pins in `pyproject.toml` / lockfile.
3. MIP runs full contract and adapter test suite.
4. CI matrix verifies pinned versions.
5. Promotion of integration to “supported” is recorded in release notes and optionally in a compatibility matrix doc.

Breaking engine output changes require a MIP adapter bump and contract test updates before pin upgrade merges.

## 8. Contract compatibility gates

Integration is protected by automation, not informal checks.

**Pre-commit (per repo, local hygiene):**

- ruff
- mypy
- pytest (fast subset)
- import / packaging checks where applicable

**CI (MIP, enforced compatibility):**

- Install pinned MMM and GeoX dependencies
- Run MIP contract tests
- Verify GeoX adapter produces valid `ExperimentEvidence`
- Verify MMM adapter produces valid `DecisionSurface`
- Verify `CalibrationSignal` and `TrustReport` gates
- Block merges on incompatible dependency upgrades without passing adapter tests

**Release gates (platform):**

- Experiment evidence usage
- Model calibration readiness
- MMM artifact / decision surface promotion
- Recommendation and orchestration promotion

See [../operating_model/RELEASE_GATES.md](../operating_model/RELEASE_GATES.md).

## 9. Future extraction of shared contracts

Today, contracts live in `src/mip/contracts/`. Extraction to `mip-contracts` is optional and deferred until:

- Field sets stabilize across engine releases
- Adapter tests cover all required variants
- Versioning policy (semver) is agreed across three repos

Until extraction, engines SHOULD NOT take a runtime dependency on full MIP—only on shared schemas or duplicate-validated shapes via tests.

## 10. Non-goals

- Do **not** copy engine source trees into MIP.
- Do **not** let MIP call private or internal engine functions directly.
- Do **not** duplicate MMM or GeoX statistical methods inside MIP.
- Do **not** let LLM orchestration bypass contracts or gates.
- Do **not** allow raw experiment evidence to enter MMM outside governed `CalibrationSignal` paths.
- Do **not** allow research-only or diagnostic outputs into production planning without promotion gates.

## 11. Open questions

| Topic | Question |
|-------|----------|
| Package names | Final PyPI/git package names for `panel-exp` and `mmm-package` |
| Org URLs | Canonical Git remotes and tag conventions |
| `mip-contracts` timing | Trigger for extraction (e.g. after Phase 4 calibration loop is stable) |
| CI topology | Single MIP workflow vs. reusable workflow called from engine repos |
| Adapter versioning | Whether adapters are versioned per engine pin or per MIP release only |

## 12. Recommended implementation phases

1. **Keep repos separate** — use local path dependencies during active development.
2. **Define adapter interfaces** in MIP (`src/mip/adapters/geox/`, `src/mip/adapters/mmm/`).
3. **Align GeoX** to emit shapes mappable to `ExperimentEvidence`.
4. **Align MMM** to emit `DecisionSurface` (Δμ) and accept `CalibrationSignal`.
5. **Add contract and adapter tests** in MIP (validation + gate smoke paths).
6. **Switch to Git dependency pins** for CI and releases.
7. **Add CI matrix** and block incompatible upgrades.
8. **Optionally extract `mip-contracts`** when schemas are stable.

## Related documents

- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [ORCHESTRATION_BOUNDARIES.md](./ORCHESTRATION_BOUNDARIES.md)
- [../adr/ADR-001-full-panel-delta-mu-decision-surface.md](../adr/ADR-001-full-panel-delta-mu-decision-surface.md)
- [../adr/ADR-002-experiments-as-calibration-evidence.md](../adr/ADR-002-experiments-as-calibration-evidence.md)
- [../roadmap/ROADMAP.md](../roadmap/ROADMAP.md)
- [../roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](../roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [../roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](../roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md)
- [../roadmap/ROADMAP_EXECUTION_SEQUENCE.md](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
- [../audits/ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md)
- [../roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](../roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
