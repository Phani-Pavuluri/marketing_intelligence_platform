# Orchestration Boundaries

This document defines what LLM-based orchestration may and must not do, where deterministic workflows are required, and where human approval is mandatory.

## What LLM Orchestration May Do

- **Interpret user intent** within an allowlisted set of workflows (e.g., “compare two budget scenarios,” “summarize last quarter’s geo test for calibration”).
- **Select and parameterize certified tools** from a registry when inputs are complete and policy permits.
- **Sequence pre-approved workflow steps** defined in the workflow planner (not ad-hoc replanning that bypasses gates).
- **Explain engine outputs** by mapping contract fields to natural language without changing values.
- **Surface diagnostics and confidence tiers** and prompt for missing inputs or approvals.
- **Route to human review** when outputs are directional, diagnostic-only, research-only, or blocked.

## What LLM Orchestration Must Not Do

- **Perform causal estimation** (lift, incremental impact, Δμ, elasticities) without calling a certified engine.
- **Run optimization** (budget allocation, solver logic) in the LLM; all allocation math lives in `mip.optimization`.
- **Override release gates** or promote models, experiments, or recommendations programmatically via prompt tricks.
- **Invent evidence** or cite experiments, metrics, or model versions not present in the evidence registry.
- **Collapse diagnostic outputs into decision-grade claims** (e.g., presenting decomposition as incremental ROI for signing).
- **Execute unsupported statistical reasoning** (“the channel is clearly incremental because…”) without contract-backed estimands.
- **Autonomously commit budget changes** to production systems without explicit human approval workflows.

## Where Deterministic Workflows Are Required

| Workflow segment | Requirement |
|------------------|-------------|
| Engine invocation | Fixed API, versioned artifact, logged parameters |
| Gate checks | Code-defined rules; no LLM discretion to skip |
| Δμ-based planning | Must use promoted MMM artifact per ADR-001 |
| Calibration application | Evidence engine rules only |
| Optimization | Solver inputs/outputs validated against contracts |
| Audit trail | Immutable step log with tool IDs and contract hashes |

The workflow planner is the source of truth for step order. LLMs may not insert steps not in the planner graph for decision-grade paths.

## Where Human Approval Is Required

- **Promotion** of MMM models, calibration signals, or recommendation templates to production tiers.
- **Decision-ready recommendations** that imply material budget reallocation (thresholds defined in release gates).
- **Use of stale or downgraded experiment evidence** for any calibration-affecting action.
- **Override of blocked confidence tier** (blocked outputs must not proceed without explicit waiver recorded).
- **Introduction of new tools or engines** into the certified registry.

## Where Agentic Autonomy Is Dangerous

Autonomy is dangerous when the system can **act on marketing spend or model state** without reversible, inspectable checkpoints:

- Closed-loop budget execution tied to live ad platforms
- Self-modifying model priors from unvetted experiment reads
- Multi-step “research agents” that chain statistical steps without per-step contracts
- Retry loops that re-prompt until a desired narrative appears
- Hidden tool use (calling engines not disclosed in the decision trace)

MIP’s controlled autonomy phase (roadmap phase 10) applies only after safe APIs, monitoring, and gates exist—and still excludes platform bidding.

## Failure Modes and Safe Defaults

| Condition | Orchestration behavior |
|-----------|-------------------------|
| Missing input for tool | Ask user; do not guess parameters |
| Engine returns blocked tier | Explain block; no workaround narrative |
| Conflicting evidence | Present conflict; do not reconcile in LLM |
| Out-of-registry citation request | Refuse; point to evidence registry |

## Product surface and LLM provider boundaries (P7b)

The UI and orchestration layers must respect explicit `LLMProviderMode` contracts. Deterministic mode is default; canned/sample explanation modes are excluded. The LLM explains governed MIP outputs—it does not create measurement authority. If LLM narrative conflicts with MIP contracts, readiness reports, or `TrustReport` status, the deterministic MIP result wins.

See [ROADMAP_EXECUTION_SEQUENCE.md](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md) P7–P11 and [LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md](../roadmap/LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md) §8.

See [TRUST_ARCHITECTURE.md](./TRUST_ARCHITECTURE.md) and [../operating_model/RELEASE_GATES.md](../operating_model/RELEASE_GATES.md).

## Governed agent authority boundaries (P8b)

**Principle:** Agents are specialized reasoning and recovery surfaces, not measurement authorities. Agentic workflows are recovery-aware and explainable, not autonomous measurement authorities.

The platform may become agentic, but agents are **not** autonomous authorities. Agents diagnose, route, explain, recover, and propose next steps. MIP contracts, readiness reports, CalibrationSignal mapping reports, TrustReports, validators, and human approval gates remain authoritative.

```text
User request
  → Intake/Routing Agent
  → Specialist Agent or deterministic workflow
  → MIP contracts / gates / validators
  → Evaluator & Validator Agent
  → user-facing explanation or safe retry plan
```

| Agents may | Agents must not |
|------------|-----------------|
| Inspect governed summaries, run manifests, failure packets, typed errors, stack traces, allowed/blocked next steps | Override MIP contracts, readiness reports, CalibrationSignal mapping status, TrustReport status, advisory claim guards, or human approval gates |
| Propose safe resolutions and user questions | Estimate effects, declare design feasibility, approve decisions, recommend optimized budgets without governed outputs |
| Summarize failures and safe retry plans | Retry risky jobs indefinitely, bypass gates, silently change assumptions, patch data without user confirmation |

**Execution ownership:** The MMM package owns MMM modeling and execution; panel_exp/GeoX owns experiment design, diagnostics, and inference. MIP agents explain, route, validate, recover, and govern.

**Evaluator gate:** The Evaluator & Validator Agent runs after specialist output and before user-facing decision-supporting explanations.

See [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](./AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md) (P8b) and [ROADMAP_EXECUTION_SEQUENCE.md](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md) P8b.
