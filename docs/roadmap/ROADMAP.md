# Roadmap

Phased delivery for MIP. Phases are sequential in dependency order; some work may overlap within a phase but not skip gates.

## Phase 1: Platform Constitution and Contracts

**Goal:** Shared language and typed boundaries before engines grow.

- Estimand and measurement glossary ratified
- Core Pydantic contracts for evidence, MMM outputs, recommendations (schemas only)
- ADRs accepted; release gate definitions drafted
- CI: import smoke tests, lint, type check

**Exit:** Contracts validate; no production estimators required.

## Phase 2: Reliability-First MMM Foundation

**Goal:** MMM engine skeleton with Δμ decision surface per ADR-001.

- Data ingestion contracts for panel inputs
- Model artifact versioning and promotion hooks
- Diagnostic-only curves and decomposition paths
- Synthetic and replay benchmark harness stubs

**Exit:** Promoted artifact can emit Δμ with diagnostics; curves not used for signing.

## Phase 3: Unified Experimentation Evidence Layer

**Goal:** Experiment registry and quality metadata.

- Ingestion for geo, panel, and standard lift designs
- Experiment quality and compatibility fields
- Freshness and registry APIs

**Exit:** Experiments queryable with tiers; no automatic calibration yet.

## Phase 4: MMM + Experimentation Calibration Loop

**Goal:** Evidence-driven calibration with gates.

- Compatibility checks between experiment and model panel
- Calibration events auditable in evidence registry
- Block/downgrade paths for weak signals

**Exit:** Calibration runs only when gates pass; failures are blocked, not silent.

## Phase 5: Trust and Explanation Platform

**Goal:** Tiering, rationale, decision traces, unsupported claims.

- Trust layer attaches to all engine contracts
- Recommendation contract template
- Trace storage format

**Exit:** End-to-end path from engine to `decision-ready` or `blocked` with trace.

## Phase 6: Safe Analytical APIs

**Goal:** Stable, versioned HTTP or RPC APIs over engines.

- Authn/z, rate limits, idempotency for planning calls
- No LLM in the critical path for API clients

**Exit:** External systems can call optimization and MMM read APIs with contracts.

## Phase 7: Conversational Workflow Orchestration

**Goal:** LLM orchestration over certified tools only.

- Workflow planner graphs for approved scenarios
- Orchestration eval harness
- Strict boundaries per ORCHESTRATION_BOUNDARIES.md

**Exit:** Demo workflows with full traces; no autonomous spend actions.

## Phase 8: Recommendation Engine

**Goal:** Structured recommendations from multi-engine outputs.

- Scenario comparison, constraint summaries
- Human approval hooks for material reallocations

**Exit:** Recommendations are contract-complete; tier enforced.

## Phase 9: Monitoring and Measurement Health

**Goal:** Operational visibility.

- Data freshness, model drift proxies, experiment pipeline health
- Alerting on gate regressions

**Exit:** Dashboards for operators (not a replacement for trust contracts on user outputs).

## Phase 10: Controlled Autonomy

**Goal:** Bounded automation where gates and reversibility exist.

- Pre-approved auto-rerun of diagnostics
- Optional scheduled replanning with human sign-off queues
- Explicit non-goals: platform bidding, silent budget commits

**Exit:** Autonomy documented, gated, and off by default.

## Current Status

**Phase 1 (largely complete):** Platform constitution, core contracts, release gates, trust assembly, evidence registry, calibration audit, and model calibration readiness are implemented. Engine adapters and external repo integration are not yet wired.

## Architecture: Multi-Repo Integration

Document and enforce multi-repo integration strategy: GeoX and MMM remain **separate analytical engine repos** consumed by MIP through **versioned dependencies and adapter contracts**—not as copied subdirectories inside MIP.

See [../architecture/REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md).

## Near-Term (Next 4–6 Weeks)

1. Define experimentation and MMM adapter interfaces under `src/mip/adapters/geox/` and `src/mip/adapters/mmm/` per integration strategy
2. Add adapter contract tests with fixture engine outputs (no vendored engine source)
3. Pilot local path dependencies to panel_exp and mmm sibling repos
4. Extend CI plan for pinned engine versions and compatibility gates
5. Wire adapter outputs into `EvidenceRegistry` and readiness evaluation paths

See [../operating_model/RESEARCH_INTAKE_PROCESS.md](../operating_model/RESEARCH_INTAKE_PROCESS.md) and [../architecture/REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md).

## LLM Decision Layer and Local-First Workbench

LLM Decision Layer and local-first workbench roadmap documented. The LLM layer is the **guided interaction layer** for business objective intake, data requirements, diagnostics, MMM/GeoX configuration, `TrustReport` explanation, measurement gap surfacing, scenario dashboards, reports, and follow-up Q&A.

Initial implementation will be **deterministic and local-first**: Streamlit demo app, `MockLLMProvider`, SaaS/subscription sample workflow, and **no autonomous production decisioning**.

- [LLM Decision Layer vision](../architecture/LLM_DECISION_LAYER_VISION.md)
- [LLM Decision Layer roadmap](./LLM_DECISION_LAYER_ROADMAP.md)
- [Local-first app and deployment strategy](../architecture/LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md)
