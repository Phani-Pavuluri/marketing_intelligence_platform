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

See [TRUST_ARCHITECTURE.md](./TRUST_ARCHITECTURE.md) and [../operating_model/RELEASE_GATES.md](../operating_model/RELEASE_GATES.md).
