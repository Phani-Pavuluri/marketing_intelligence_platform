# Agentic Workflow Governance Roadmap

This document defines how MIP will eventually support **governed agentic workflow**—and why Phase 7A is **not** autonomous agent execution.

## Why MIP needs agentic workflow eventually

Marketing intelligence work is conversational, iterative, and cross-functional. Users ask business questions, supply partial data, need guidance on KPIs and controls, and want explanations tied to governed artifacts—not raw model dumps.

A durable **workflow lineage** (what was requested, planned, executed, blocked, and produced) is required before any LLM can safely:

- Route users to the right deterministic workflow
- Explain why a step was skipped or blocked
- Prepare review packages for human approvers
- Audit what automation did versus what a human approved

Phase 7A introduces that lineage as contracts and deterministic manifest builders. Future phases add a planner/router and human approval checkpoints on top of the same spine.

## Why Phase 7A is not autonomous agent execution

Phase 7A deliberately excludes:

- LangGraph or other autonomous agent frameworks
- Real LLM planning or tool selection
- External tool execution
- MMM or GeoX engine execution
- Budget actions or production recommendations
- Causal, lift, ROI, or model-result claims

Every manifest is built **deterministically** from `WorkflowRunSummary` (and optional MMM fixture reports). `agentic_planning_enabled` is always `false`. `execution_mode` is `deterministic_local_no_agent`. No field may imply that an LLM autonomously chose or executed steps.

## Safe definition of “agentic” for MIP

In MIP, **agentic** means:

> A governed assistant that explains, routes, requests missing inputs, proposes the next **safe** deterministic step, and prepares human review packages—while **never** certifying causal effects, overriding `TrustReport`, or bypassing release gates.

Agentic behavior is **advisory and routing**, not statistical computation or production automation.

> **P8b principle:** The platform may become agentic, but agents are **not autonomous authorities**. Agents diagnose, route, explain, recover, and propose next steps. MIP contracts, readiness reports, CalibrationSignal mapping reports, TrustReports, validators, and human approval gates remain authoritative.

> **Agents are specialized reasoning and recovery surfaces, not measurement authorities.**

Agents may inspect governed summaries, run manifests, failure packets, typed validation errors, stack traces, allowed next steps, and blocked next steps. Agents may propose safe resolutions and user questions. Agents may **not** override MIP contracts, readiness reports, CalibrationSignal mapping status, TrustReport status, advisory claim guards, or human approval gates.

The platform will use governed specialist agents only where they add distinct expertise, tool access, or failure-handling value. The goal is not many agents; the goal is controlled specialization with typed handoffs, explicit permission boundaries, and validation gates.

**Agentic workflows are recovery-aware and explainable, not autonomous measurement authorities.**

### Governed agent hierarchy (P8b)

```text
User request
  → Intake/Routing Agent
  → Specialist Agent or deterministic workflow
  → MIP contracts / gates / validators
  → Evaluator & Validator Agent
  → user-facing explanation or safe retry plan
```

## P8b — Governed agent role registry (planned)

**Status:** ✓ implemented — `src/mip/contracts/agentic_workflow.py`, `src/mip/workflows/intake/agentic_recovery.py`. Contracts and deterministic helpers only; no LangGraph runtime, no agent classes, no tool execution.

**Placement:** After P8 local/demo profiling; before P9 public hosted demo and **before** P17 LangGraph/stateful orchestration.

**Rationale:** P8b defines governed agent contracts before any stateful agent runtime. P17 implements LangGraph using those contracts—avoiding free-form autonomous agents.

### First-wave governed agent roles

#### 1. Intake & Routing Agent

**Purpose:** Classify the user’s request and route to the correct workflow.

**Responsibilities:** cold-start advisory routing · MMM readiness routing · GeoX/experiment readiness routing · CalibrationSignal mapping routing · decision review routing · data profiling routing · LLM explanation routing

**Allowed:** ask clarifying questions · select governed workflow path · explain why a workflow is or is not appropriate

**Not allowed:** estimate effects · declare design feasibility · approve decisions · recommend optimized budgets

#### 2. Data Profiling / Data Readiness Agent

**Purpose:** Inspect governed data summaries and determine what data exists, what is missing, and which workflows are structurally supported.

**Responsibilities:** column semantic roles · time/geo/media/outcome coverage · traffic-source summaries · calibration fields · missingness · grain mismatch · workflow support/blocked routes

**Allowed:** summarize data readiness · ask for missing data · route to common intake/readiness/advisory

**Not allowed:** estimate lift · estimate ROI · run MMM · run GeoX · infer missing data silently

**Note:** Do not call this a Feature Store Explorer Agent yet. The current platform has intake/profiling/manifests, not a production feature store.

#### 3. Cold-Start Advisory Agent

**Purpose:** Help users who are not measurement-ready but need safe marketing guidance.

**Responsibilities:** business-profile intake · channel hypothesis explanation · traffic-source-informed advisory · tracking checklist · starter measurement plan · learning agenda

**Allowed:** produce advisory-only hypotheses · ask for business details · ask for tracking/data inputs · explain evidence and claim labels

**Not allowed:** claim optimal mix · claim ROI · claim causal lift · claim final budget allocation · claim decision authorization

#### 4. MMM Specialist Agent

**Purpose:** Reason about MMM readiness, diagnostics, calibration needs, and MMM workflow failures.

**Responsibilities:** MMM data requirements · channel/time/granularity issues · calibration evidence requirements · refresh readiness · model diagnostic interpretation · Ridge vs Bayesian governance status · decision-surface prerequisites

**Allowed:** explain MMM readiness · explain blocked MMM paths · propose safe remediation · summarize MMM diagnostics when governed outputs exist

**Not allowed:** run model internals directly · silently impute missing spend · change model assumptions without trace · declare Bayesian production readiness · approve budget recommendations · override decision-surface gates

**Boundary:** The **MMM package** owns MMM modeling and execution. MIP agents explain, route, validate, recover, and govern.

#### 5. GeoX / Experiment Specialist Agent

**Purpose:** Reason about experiment design readiness, GeoX/panel data requirements, experiment diagnostics, and panel_exp workflow failures.

**Responsibilities:** geo/time panel structure · objective/KPI alignment · power/MDE diagnostic prerequisites · matchability prerequisites · treatment/control feasibility prerequisites · readout-to-CalibrationSignal handoff

**Allowed:** explain why GeoX is structurally supported or blocked · ask for missing DMA/state/geo/time/outcome/media fields · propose safe next steps · route to panel_exp diagnostics when readiness allows

**Not allowed:** invent matched markets · declare design feasibility without diagnostic output · estimate lift · calculate power/MDE unless delegated to governed package diagnostics · assign treatment/control without governed workflow

**Boundary:** **panel_exp/GeoX** owns experiment design, diagnostics, and inference execution. MIP agents explain, route, validate, recover, and govern.

#### 6. CalibrationSignal Specialist Agent

**Purpose:** Govern experiment/readout evidence → CalibrationSignal compatibility and mapping.

**Responsibilities:** metric/estimand alignment · scope/time-window alignment · effect estimate presence · uncertainty presence · freshness/staleness · causal flag requirement · source lineage · MMM calibration eligibility

**Allowed:** explain why evidence can or cannot map to CalibrationSignal · ask for missing uncertainty or scope fields · summarize mapping reports

**Not allowed:** estimate missing uncertainty · certify causality · execute MMM calibration · promote diagnostic evidence to decision support

#### 7. Failure Recovery / Debugging Agent

**Purpose:** Consume run manifests, typed errors, stack traces, and failure packets to propose safe resolution plans.

**Responsibilities:** stack trace summarization · typed error diagnosis · safe retry plan · blocked retry plan · user-facing failure explanation · issue/TODO proposal (later)

**Allowed:** explain what failed · identify likely failing step · ask user for missing/corrected data · recommend safe retry · recommend fallback route

**Not allowed:** retry risky jobs indefinitely · bypass gates · silently change assumptions · patch data without user confirmation · approve partial failed runs

**Example:** If CalibrationSignal mapping fails because `standard_error` is missing, the agent may ask for SE or supported uncertainty. It must **not** infer uncertainty from the point estimate.

#### 8. Evaluator & Validator Agent

**Purpose:** Independently check whether agent outputs are valid, safe, and claim-compliant before user-facing delivery.

**Responsibilities:** forbidden claim detection · TrustReport requirement checks · readiness/report consistency · CalibrationSignal mapping consistency · advisory vs causal claim separation · LLM output validation · golden scenario checks

**Allowed:** block unsafe responses · rewrite or request rewrite of explanations · flag missing labels/warnings · enforce allowed/blocked next steps

**Not allowed:** invent results · create new causal claims · override underlying report status · approve decisions

**Requirement:** The Evaluator & Validator Agent runs **after** specialist agent output and **before** user-facing decision-supporting explanations.

### Future optional agents (deferred)

Added only when platform capabilities require them.

| Role | Trigger condition | Summary |
|------|-------------------|---------|
| **A. Feature Store Explorer** | Feast/Tecton/Databricks Feature Store or equivalent integrated | Feature catalog, lineage, freshness, entity/grain consistency — **not needed yet** (intake/profiling/manifests only today) |
| **B. ML Engineering / MLOps Specialist** | Production schedulers, MLflow/registry, Dockerized services, API deployment, refresh jobs, monitoring | Deployment/scheduler/registry/runtime diagnostics — may not change causal assumptions or approve measurement outputs |
| **C. Research Scout** | Core product workflows stable; continuous method scouting needed | Scan MMM/GeoX/causal/LLM research; propose investigation tickets — may not replace production methods |
| **D. Data Connector / Integration** | Production connectors introduced | Warehouse/GA4/ads connector status, schema drift, credential failures — must not expose secrets |
| **E. Privacy / Security Review** | Before persistent uploads, public BYOK, platform-managed keys, customer workspaces, multi-user deployment | PII/secrets detection, retention, provider input boundaries — may block unsafe flows |
| **F. Product / UX Guide** | Hosted UI becomes multi-workflow with onboarding needs | Walk through workflow/mode selection — may not make measurement claims |

### Typed handoff contracts (P8b implementation)

| Contract | Purpose |
|----------|---------|
| `AgentRoleDefinition` | Role identity, responsibilities, capability list |
| `AgentCapability` | Typed capability a role may invoke |
| `AgentPermissionBoundary` | Explicit allowed/blocked action sets |
| `AgentTask` | Unit of work with governed input references |
| `AgentRunManifest` | Workflow, step, input/artifact refs, package/version metadata, status, `started_at`/`ended_at`, warnings, blocking reasons |
| `AgentObservation` | Governed step observation (summaries only by default) |
| `AgentFailurePacket` | Workflow, step, `error_type`, `error_message`, `stack_trace`, typed validation failures, `safe_context`, `allowed_retry_actions`, `blocked_retry_actions`, affected artifacts |
| `AgentResolutionPlan` | Diagnosis, recommended user questions, safe/blocked next steps, retry eligibility, human approval requirement, expected downstream impact |
| `AgentValidationReport` | Claim compliance, forbidden-claim findings, missing evidence labels, TrustReport requirement status, readiness/calibration consistency, final approval/block status |
| `AgentHandoffPacket` | Typed inter-agent handoff with governed references |
| `AgentRetryPolicy` | Safe retry rules, caps, and escalation triggers |
| `AgentEscalationPolicy` | When to require human review or block automation |

### Example flows

**Example 1 — GeoX missing geo column**

User wants experiment design. Data Readiness Agent detects week/outcome/media but no DMA/state/geo. GeoX Specialist says GeoX design is blocked. Failure/Recovery Agent proposes: ask for geo column · confirm whether market column is geo · route to national MMM/advisory path. **Blocked:** invent geo mapping · proceed with GeoX design · estimate lift. Evaluator confirms no feasibility claim is made.

**Example 2 — MMM missing spend weeks**

MMM workflow fails because Meta spend has missing weeks. Failure/Recovery Agent proposes: ask user to provide missing spend · confirm true zero spend · exclude channel with warning if governed policy allows. **Blocked:** silently impute spend · continue without recording assumption. MMM Specialist explains downstream impact. Evaluator blocks ROI/budget claims until valid diagnostics exist.

**Example 3 — CalibrationSignal missing uncertainty**

Experiment readout has `effect_estimate` but no `standard_error`. CalibrationSignal Specialist explains mapping is `needs_more_data`. Failure/Recovery Agent asks for SE or supported uncertainty field. **Blocked:** infer SE from point estimate · certify evidence as causal · execute MMM calibration.

**Example 4 — LLM output unsafe claim**

LLM explanation says “Meta is the highest ROI channel.” Evaluator & Validator Agent detects forbidden ROI claim. Response is blocked or rewritten as: “Meta is a hypothesis to test based on advisory evidence; ROI is not proven.”

### P8b acceptance criteria

- Defines first-wave agent roles and boundaries
- Defines future/deferred agent roles and trigger conditions
- Defines typed handoff contracts for agent tasks, manifests, failures, resolution plans, validation reports, and retry policies
- Separates agent reasoning from measurement authority
- Ensures MMM package and panel_exp/GeoX retain execution ownership
- Ensures agents cannot override TrustReport/readiness/calibration/advisory gates
- Requires Evaluator & Validator Agent before decision-supporting user-facing explanations
- Captures stack trace/failure recovery pattern without adding runtime execution
- Documents safe retry and blocked retry concepts

## Allowed future agent behaviors

| Behavior | Description |
|----------|-------------|
| **Explain** | Summarize workflow status, gates, warnings, and `TrustReport` in tier-appropriate language |
| **Route** | Map user intent to an existing deterministic workflow (intake → readiness → config → adapters) |
| **Request missing data** | Surface data requirements and readiness gaps from contracts |
| **Propose next safe step** | Suggest the next governed step when blockers are resolved; never skip gates |
| **Prepare review package** | Assemble manifest, artifacts, and approval context for human reviewers |

## Blocked agent behaviors

| Behavior | Why blocked |
|----------|-------------|
| Estimate causal impact | Statistical engines and certified adapters own estimands |
| Override `TrustReport` | Trust verdicts are gate-driven, not narrative-driven |
| Approve budget action | Human approval workflow required for production paths |
| Fabricate model results | No placeholder may be presented as engine output |
| Bypass gates | Release gates and calibration governance are non-negotiable |

## Proposed delivery sequence

```text
7A  Run manifest + contracts (this phase)
      WorkflowPlan, WorkflowRunManifest, deterministic builders, safety assertions

7B  Governed planner/router (this phase)
      PlannerRoute, route_next_actions, display-only next safe action guidance

7C  Human approval checkpoints (this phase)
      ApprovalRequest, blocked_until_approved enforcement, display-only UI status

8F  Sibling export producer specifications (this phase)
      docs/integrations/*_PRODUCER_SPEC.md, sibling_producer_specs helpers

S1–S12  Semantic and decision-readiness tracks (documented addendum; not implemented)
      metrics, estimands, scope, actions, decision packets, completeness scoring

G1–G10  Critical invariants and golden scenarios (documented addendum)
      golden scenarios, conformance suite, no-silent-upgrade, dependency graph

Next  Phase 8G/8H implementation (explanation payload + usage policy)

I1–I15  Conversational intake + data handoff (documented product workflow)

P4b–P4c  Experiment design intake + Common Data Intake Workbench (documented; next implementation)

P5b  General advisory and cold-start planning contracts (after P5)

P7   Local Streamlit/Gradio workflow shell (deterministic mode default)

P7b  Pluggable LLM provider contracts + explanation governance (no canned explanations)

P8   Demo fixtures and local/demo profiling ✓

P8b Agent role registry, run manifest, failure packet, resolution plan contracts (implemented)

P9   Public hosted demo (Streamlit Community Cloud / Hugging Face Spaces)

P10  FastAPI/Docker service wrapper

P11  Hosted API hardening (auth, rate limits, privacy, cost controls)

P17  LangGraph / stateful workflow orchestration skeleton (after P8b contracts stabilize)
```

## Common Data Intake Workbench (P4c — planned)

**Principle:** Common intake first, workflow-specific readiness second. One workbench for MMM, GeoX, CalibrationSignal, and decision-review—no separate upload flows.

The workbench owns source registration, manifests, mapping, snapshots, structural profiling, `WorkflowSupportAssessment`, and LLM-safe summaries. Readiness then branches by workflow (P5). Users not ready for formal measurement route to **general advisory / cold-start planning** (P5b).

## P5b — General advisory and cold-start planning (planned)

**Purpose:** Pre-measurement advisory lane. P5 readiness reports fork **measurement-ready** vs **advisory-only**. P5b provides labeled channel hypotheses, tracking checklists, learning agendas, and business-profile-driven guidance.

**Key invariant:** Every answer labeled by `AdvisoryEvidenceMode`, `AdvisoryClaimType`, and `EvidenceLevel`. LLM general knowledge allowed for advisory; `TrustReport` required for causal/decision claims.

**Future graph nodes (P17):** `ColdStartProfileNode` · `AdvisoryChannelHypothesisNode` · `TrafficSourceAdvisoryNode` · `TrackingReadinessNode` · `LearningAgendaNode` · `AdvisoryToMeasurementRoutingNode` (routes to P5/P6 when ready)

**Boundaries:** No channel ROI model · no budget optimizer · no web search · no causal certification without governed measurement

See [ROADMAP_EXECUTION_SEQUENCE.md](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md) P5b.

## P17 — LangGraph / stateful workflow orchestration (planned)

**Purpose:** LangGraph (or equivalent) routes users through governed intake, workbench profiling, workflow-specific readiness, and diagnostic-request stages. It is a **workflow controller**, not the measurement brain.

```text
LLM + LangGraph = conversation router / workflow controller
MIP contracts     = state, gates, audit trail
Common profiling  = preliminary data summaries
MMM               = MMM diagnostics / calibration context
panel_exp / GeoX  = design diagnostics, power, MDE, readout
```

**Graph state holds governed objects only** — `MeasurementIntakeSession`, `IntakePathRecommendation`, `IntakePlan`, manifests, `SemanticMappingReport`, `ExperimentDesignIntake`, `PreliminaryAnalysisReport`, `WorkflowSupportAssessment`, `ReadinessReport`, `TrustReport`. Not raw dataframes.

**Future nodes:** `IntentClassifierNode` · `ClarificationNode` · `IntakeSessionNode` · `PathRecommendationNode` · `RequiredDataPlanNode` · `DataSourceManifestNode` · `ColumnMappingNode` · `ExperimentDesignRequirementNode` · `PreliminaryProfilingNode` · `ReadinessReportNode` · `ColdStartAdvisoryNode` · `PanelExpDiagnosticRequestNode` · `MMMRefreshRequestNode` · `LLMAnswerGroundingNode` · `HumanApprovalNode`

**Approved typed tools (future):** `recommend_intake_path()` · `build_intake_plan()` · `build_intake_manifest()` · `build_semantic_mapping_report()` · `build_experiment_design_requirements()` · `run_common_profile_summary()` · `build_readiness_report()` · `build_panel_exp_diagnostic_request()` · gated engine diagnostic calls

**Boundaries:** LangGraph may choose the next governed module; must not let LLM write arbitrary analysis code; must not expose raw files to LLM; must not bypass `TrustReport`, readiness gates, or human approval; must not produce causal/budget/design-validity claims without engine outputs.

**Timing:** Do not implement LangGraph runtime before P4b, P4c, P5, P5b, P7, P8, and **P8b** agent contracts stabilize. Integer phase **P12** is production table-reference design; orchestration is **P17**. Product surface (P7–P9) precedes LangGraph so user flow and LLM provider boundaries exist first; **P8b precedes P17** so agent roles and handoff contracts exist before stateful runtime.

See [ROADMAP_EXECUTION_SEQUENCE.md](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md).

## Phase 8A artifacts

| Module | Role |
|--------|------|
| `mip.orchestration.engine_fixtures` | `FixtureEngineRunResult`, `orchestrate_mmm_fixture_engine`, `orchestrate_geox_fixture_engine` |

Fixture engine orchestration wires manifest → planner/router → approval checkpoints → adapter input/output placeholders → governance artifacts → TrustReport. All outputs are labeled `fixture_engine_orchestration_only` and `not_real_engine_execution`.

## Phase 8B artifacts

| Module | Role |
|--------|------|
| `mip.adapters.sibling_fixtures` | `SiblingFixtureExport`, `load_sibling_fixture_export`, `register_sibling_fixture_export` |

Pinned sibling-repo fixture imports read committed JSON exports only (no live repo connection). Exports validate structural metadata, convert to `AdapterOutputBundle`, and flow through existing adapter governance. Required labels include `pinned_sibling_repo_fixture_only` and `not_live_engine_execution`. Blocked/invalid fixtures produce blocked `TrustReport` values and are not registered as usable evidence.

## Phase 8C artifacts

| Module | Role |
|--------|------|
| `mip.adapters.sibling_export_hooks` | `SiblingExportDirectoryRef`, `discover_sibling_export_files`, `register_sibling_exports_from_directory` |

Read-only sibling export hooks scan explicit local directories for `.json` export files, validate via Phase 8B contracts, and register through adapter governance. Required labels include `readonly_sibling_export_hook_only` and `static_export_file_only`. No sibling code imports, subprocess execution, or file watching.

## Phase 8D artifacts

| Module | Role |
|--------|------|
| `mip.adapters.sibling_compatibility` | `SiblingRepoExportConfig`, `check_sibling_repo_compatibility`, `build_sibling_repo_compatibility_registry` |

Sibling repo compatibility registry resolves configured export directories, validates schema/source/engine expectations before Phase 8C discovery, and blocks registration when incompatible. Required labels include `sibling_repo_compatibility_check_only` and `readonly_export_contract_only`.

## Phase 8E artifacts

| Module | Role |
|--------|------|
| `mip.adapters.local_sibling_paths` | `LocalSiblingRepoPathDefaults`, `build_local_sibling_compatibility_registry`, `register_compatible_local_sibling_exports` |

Local sibling export path wiring configures default absolute paths for sibling `mmm` and `panel_exp` export directories, runs Phase 8D compatibility checks, and registers static JSON exports read-only. Required labels include `local_sibling_export_path_wiring_only` and `readonly_export_contract_only`.

## Phase 8F artifacts

| Module / docs | Role |
|---------------|------|
| `docs/integrations/MIP_SIBLING_EXPORT_PRODUCER_SPEC.md` | Canonical sibling export producer contract |
| `docs/integrations/MMM_MIP_EXPORT_PRODUCER_SPEC.md` | MMM producer writer guidance |
| `docs/integrations/PANEL_EXP_MIP_EXPORT_PRODUCER_SPEC.md` | panel_exp producer writer guidance |
| `mip.adapters.sibling_producer_specs` | `required_producer_labels`, `assert_valid_producer_spec_example` |

Producer specifications document the JSON contract for `integrations/mip/exports/`. Read-only consumer bridge (8B–8E) is complete. Live engine execution remains blocked.

## Semantic and decision-readiness tracks (S1–S12)

Documented in [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](../roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md). MIP owns metric/estimand registries, scope alignment, business action ontology, decision review packets, explanation templates, and completeness scoring. Sibling repos tag exports with semantic metadata—they do not authorize business actions.

Structurally valid exports are not sufficient for decision guidance; semantic completeness is required before decision-support workflows.

## Critical invariants, golden scenarios, and artifact selection (G1–G20)

Documented in [PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](../roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md). Golden scenarios prove end-to-end product behavior; G6 enforces no silent readiness upgrade; G3 defines sibling conformance suite; G11–G20 define artifact selection and ambiguity policies.

## Conversational intake and data handoff (I1–I15)

Documented in [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](../roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md). Product workflow from LLM conversation → structured intake → data profiling → readiness report → refresh request → static export import. **First implementation:** I1–I3 session/plan contracts.

## Phase 7C artifacts

| Module | Role |
|--------|------|
| `mip.orchestration.approvals` | `ApprovalRequest`, `ApprovalCheckpoint`, `enforce_approval_for_route`, `apply_approval_decision` |

Approval state is **local in-memory contract state only**. No database, auth/RBAC, external approval systems, or automatic approval. Approved actions may move to `allowed` in the router for visibility only—they are **not executed**.

## Phase 7B artifacts

| Module | Role |
|--------|------|
| `mip.orchestration.router` | `PlannerRoute`, `route_next_actions`, `planner_route_from_summary`, `format_planner_route_for_display` |

The router reads `WorkflowRunManifest` state and returns allowed, blocked, and approval-gated next actions. It does **not** execute workflow steps or enable autonomous planning (`agentic_planning_enabled` remains `false`).

## Phase 7A artifacts

| Module | Role |
|--------|------|
| `mip.orchestration.manifest` | Pydantic contracts, enums, `assert_safe_workflow_manifest` |
| `mip.orchestration.plans` | `build_plan_from_workflow_summary`, `build_manifest_from_workflow_summary`, `build_manifest_with_mmm_fixture` |

### Workflow step statuses

`planned`, `running`, `completed`, `warning`, `blocked`, `skipped`, `requires_approval`

### Workflow action types (deterministic spine)

`parse_input`, `classify_intent`, `profile_data`, `evaluate_feasibility`, `build_readiness_report`, `draft_config`, `build_adapter_input`, `build_adapter_output_fixture`, `map_to_governance_artifact`, `build_trust_report`, `render_report`, `request_human_approval`

Production, budget, and recommendation action types **must not** exist until explicit later phases.

## Integration with current product flow

```text
JSON input
  → run_local_workflow()
  → WorkflowRunSummary
  → build_manifest_from_workflow_summary()   [Phase 7A]
  → route_next_actions() / planner_route_from_summary()   [Phase 7B]
  → enforce_approval_for_route() / approval checkpoints   [Phase 7C]
  → orchestrate_*_fixture_engine()                          [Phase 8A]
  → load_sibling_fixture_export() / register_sibling_fixture_export()   [Phase 8B]
  → discover_sibling_export_files() / register_sibling_exports_from_directory()   [Phase 8C]
  → check_sibling_repo_compatibility() / register_exports_for_compatible_repo()   [Phase 8D]
  → build_local_sibling_compatibility_registry() / register_compatible_local_sibling_exports()   [Phase 8E]
  → sibling producer JSON in integrations/mip/exports/ per docs/integrations/*_PRODUCER_SPEC.md   [Phase 8F]
  → (optional) build_manifest_with_mmm_fixture()
  → TrustReport / UI / report
```

The manifest records lineage; it does not replace `WorkflowRunSummary`, `TrustReport`, or release gates.

## Related documents

- [ORCHESTRATION_BOUNDARIES.md](./ORCHESTRATION_BOUNDARIES.md)
- [LLM_DECISION_LAYER_VISION.md](./LLM_DECISION_LAYER_VISION.md)
- [LLM_DECISION_LAYER_ROADMAP.md](../roadmap/LLM_DECISION_LAYER_ROADMAP.md)
- [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](../roadmap/PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](../roadmap/PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md)
- [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](../roadmap/CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
- [ROADMAP_EXECUTION_SEQUENCE.md](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
- [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md)
- [REPO_INTEGRATION_STRATEGY.md](./REPO_INTEGRATION_STRATEGY.md)
