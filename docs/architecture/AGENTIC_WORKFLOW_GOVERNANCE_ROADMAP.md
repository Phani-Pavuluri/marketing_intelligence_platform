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

7B  Governed planner/router
      Route to existing deterministic steps; no new execution paths

7C  Human approval checkpoints
      Approval metadata on manifest steps; blocked_until_approved semantics

8   Fixture engine orchestration through adapters
      Orchestrate placeholder/MMM fixture paths; still no real engine claims

Later  Real engine adapters
      Only after manifest, gates, and approval lineage remain intact
```

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
  → (optional) build_manifest_with_mmm_fixture()
  → TrustReport / UI / report
```

The manifest records lineage; it does not replace `WorkflowRunSummary`, `TrustReport`, or release gates.

## Related documents

- [ORCHESTRATION_BOUNDARIES.md](./ORCHESTRATION_BOUNDARIES.md)
- [LLM_DECISION_LAYER_VISION.md](./LLM_DECISION_LAYER_VISION.md)
- [LLM_DECISION_LAYER_ROADMAP.md](../roadmap/LLM_DECISION_LAYER_ROADMAP.md)
- [REPO_INTEGRATION_STRATEGY.md](./REPO_INTEGRATION_STRATEGY.md)
