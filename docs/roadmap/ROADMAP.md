# Roadmap

Phased delivery for MIP. Phases are sequential in dependency order; some work may overlap within a phase but not skip gates.

## Canonical ratified governance amendment (2026-07-19)

This section is authoritative for post-audit sequencing and supersedes any older
near-term or “next authorized” wording that conflicts with it. It incorporates
the ratified D1–D10 decisions in
[MIP roadmap audit ratification brief 001](MIP_ROADMAP_AUDIT_RATIFICATION_BRIEF_001.md).
The historical phases below are retained as context; they are not execution
authority where they conflict with R0–R6 or the freezes below.

### Authoritative milestones and governed lanes

R0–R6 are the dependency sequence. Work may be organized in parallel lanes only
when its R milestone and all prerequisites permit it. Every lane item must record
its governing milestone, state, owner, prerequisites (including commits/artifacts
on `main`), entry/exit criteria, evidence packet, blocked/cross-repository
dependencies, stop/rollback conditions, and promotion/release boundary.

| Milestone | Scope and gate | State | Required exit evidence |
|---|---|---|---|
| R0 | Ownership, authority, and four-environment foundations | APPROVED | Environment/capability matrix, owners, entry/exit/rollback rules |
| R1 | Core LLM benchmark and provider-promotion governance | APPROVED | Versioned benchmark design, thresholds/rollback/LKG definition; promotion remains separately authorized |
| R2 | Resolver and artifact lifecycle | APPROVED | Contract/lifecycle design after R1 design; fixture implementation only after benchmark-v1 gate |
| R3 | Artifact-grounded benchmark | APPROVED | Engine-certified truth, governed lifecycle, grounded evaluation evidence |
| R4 | Cross-repository integration and release governance | APPROVED | Gate 1 design plus Gate 2 runtime/rollback evidence; runtime remains separately authorized |
| R5 | Security, data lifecycle, operations, and pilot readiness | APPROVED | Security/access/lifecycle, jobs/recovery/SLO/incident/support evidence |
| R6 | Limited-pilot evidence and production authorization | APPROVED | Explicit pilot/production decision, success/support/release/rollback evidence |

| Governed lane | Governing milestones | Required owner role | Current boundary |
|---|---|---|---|
| Governance, ownership, and authorization | R0–R6 | MIP program/governance owner | No approval is execution authorization |
| Benchmarks, evaluation, and numerical truth | R1, R3 | MIP benchmark owner; MMM/GeoX truth owners | MIP does not certify statistical truth |
| MIP product and control-plane architecture | R0–R3 | MIP product/control-plane owner | No runtime authority from design |
| Resolver and artifact lifecycle | R2–R3 | MIP artifact-lifecycle owner | No user-facing artifact capability |
| MMM/GeoX integration and release governance | R4 | MIP, MMM, GeoX release owners | No live-engine authority from Gate 1/2 alone |
| Security, data lifecycle, platform, and operations | R0, R5 | MIP platform/security owner | No real data or persistent product artifacts before controls |
| Pilot, production, and recommendation authorization | R5–R6 | Named human/governance owners | Proposal, approval, execution, and release are separate |

The unified state model is `OBSERVED → PROPOSED → APPROVED →
AUTHORIZED_FOR_EXECUTION`. Each later task must cite its authorizing roadmap
section and evidence, and verify prerequisite commits/artifacts on `main`.

### Ratified decision gates

- **D1–D2:** Provider/model/prompt promotion requires a versioned benchmark,
  target-environment operational acceptance, and explicit promotion approval.
  Acceptance-004 is operational-only and remains frozen.
- **D3–D4:** Resolver design follows amendment plus benchmark-design approval;
  fixture implementation follows benchmark-v1. Persistent customer/product
  artifacts, uploads, and real data require implemented security, lifecycle,
  access, retention/deletion, audit, and operational controls. Isolated sanitized
  non-customer test evidence is a separate, later gated storage category.
- **D5–D6:** Certified fixture-backed package integration is contained; private
  real-data execution is separately authorized. R4 uses Gate 1 contract/release
  design and Gate 2 runtime certification/tested rollback with versioned release
  packets. MMM and GeoX do not orchestrate each other; MIP is the control plane.
- **D7:** MMM and GeoX/panel_exp own certified numerical truth suites; MIP owns
  registry/scenario wrappers/scoring, not statistical truth.
- **D8:** Environments are Public Fixture Demo, Internal Fixture-Backed
  Integration, Limited Pilot, and Production. MIP/LLM do not replace engine-owned
  computation or approval-owned decisions; a capability-authority matrix governs
  computation, validation, invocation, explanation, proposal, approval, and
  execution.
- **D9:** Recommendation-lifecycle and `RecommendationContract` design are
  roadmap items only. Simulation is not a recommendation; optimization is a
  candidate; proposal is not approval; approval is not execution.
- **D10:** R0–R6 plus governed lanes is the canonical structure.

### Retained freezes and execution-rebase boundary

The following remain **APPROVED but not AUTHORIZED_FOR_EXECUTION**: acceptance-004;
provider promotion; resolver/artifact implementation; artifact-grounded benchmark
implementation; fixture package integration; isolated test-evidence storage;
R4 Gate 1/2 implementation; private real-data integration; uploads; persistent
customer/product artifacts; live MMM/GeoX; simulation; optimization;
recommendation proposal/approval/execution; external actions; automated decisions;
treatment assignment; pilot; and production.

Execution rebase is not authorized. A future separately authorized rebase must
inventory pending/paused/frozen tasks, classify each as retain/modify/reorder/
replace/retire/remain blocked, cite this amendment and evidence, verify
prerequisites on `main`, preserve cross-repository order, and grant no task
authority unless explicitly retained and reauthorized.

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
