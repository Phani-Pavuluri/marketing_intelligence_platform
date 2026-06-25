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
```

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
- [REPO_INTEGRATION_STRATEGY.md](./REPO_INTEGRATION_STRATEGY.md)
