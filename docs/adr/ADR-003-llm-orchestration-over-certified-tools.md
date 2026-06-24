# ADR-003: LLM Orchestration Over Certified Tools

**Status:** Accepted  
**Date:** 2026-05-28  
**Deciders:** Platform architecture (initial constitution)

## Context

Large language models can parse intent, summarize results, and chain steps—but they also hallucinate statistics, invent citations, and bypass governance when used as end-to-end “analysts.” MIP is explicitly not a generic marketing chatbot. The platform must use LLMs where they add control-plane value without compromising causal integrity.

## Decision

1. **LLMs orchestrate certified tools** and explain their outputs. They invoke engines through the workflow planner with allowlisted tools and parameters.
2. **LLMs do not perform** causal estimation, optimization, calibration math, or unsupported statistical reasoning **directly** in the orchestration layer.
3. All numerical claims in **decision-grade** paths must originate from **engine output contracts** validated and tiered by the trust layer.
4. Natural language explanations **must not alter** contract field values; paraphrase and structure only.
5. Tool registry and workflow graphs are **versioned**; orchestration cannot call unregistered tools in decision paths.

## Consequences

### Positive

- Clear separation of concerns aligned with platform principles
- Easier evaluation: orchestration eval separate from MMM/experiment eval
- Reduced regulatory and audit risk from uncited model reasoning

### Negative

- Higher engineering cost for tool APIs and planner graphs before conversational UX feels “fluent”
- Some user questions cannot be answered without running engines (latency)
- Poorly designed tools force awkward multi-step workflows

### Operational

- `mip.orchestration` remains thin until phase 7; boundaries documented now
- Orchestration promotion gated separately from engine promotion (see release gates)

## Alternatives Considered

| Alternative | Why not chosen |
|-------------|----------------|
| **LLM-as-analyst (end-to-end)** | Violates compute/orchestrate split; untestable causal claims |
| **No LLM (API only)** | Sacrifices accessible workflow control plane for strategists |
| **LLM generates code to run ad hoc** | Unbounded execution risk; hard to gate and audit |
| **RAG over past reports as primary evidence** | Stale narrative; not a substitute for evidence registry |

## References

- [../architecture/ORCHESTRATION_BOUNDARIES.md](../architecture/ORCHESTRATION_BOUNDARIES.md)
- [../vision/PLATFORM_PRINCIPLES.md](../vision/PLATFORM_PRINCIPLES.md)
