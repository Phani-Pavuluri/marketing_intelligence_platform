# Architecture

MIP is organized in layers. Upper layers coordinate; lower layers compute. Cross-cutting **trust** and **evaluation** attach to every path that can influence decisions.

## Conceptual Layers

### Conversational orchestration layer

Entry point for user intent expressed in natural language. Parses goals, disambiguates within policy, and delegates to the workflow planner. Does not execute numerical analysis.

Future home: `mip.orchestration`, `mip.workflows`, and the **LLM Decision Layer** (`mip.llm`)—see [LLM_DECISION_LAYER_VISION.md](./LLM_DECISION_LAYER_VISION.md). The LLM layer routes, configures, and explains; it does not estimate or certify. Local-first app and dashboard strategy: [LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md](./LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md).

### Workflow planner / tool router

Deterministic graph of allowed steps: which engine to call, in what order, with which parameters, under which approval gates. Maps intents to certified tool invocations and aggregates contract outputs.

### Certified analytical engines (external repos)

Versioned engines in **separate repositories** (`panel_exp`, `mmm`). MIP consumes their outputs through `adapters/`—see [REPO_INTEGRATION_STRATEGY.md](./REPO_INTEGRATION_STRATEGY.md).

- **GeoX / panel_exp:** design, inference, validation → `ExperimentEvidence`
- **MMM:** modeling, diagnostics, optimization → `DecisionSurface` (Δμ); consumes `CalibrationSignal`

Optional engine-side export helpers live in each repo under `integrations/mip/`.

### Experimentation ingestion (MIP)

Registers adapter-mapped experiment evidence, runs quality gates, and surfaces trust reports. Does not run SCM/TBR/DID math.

### MMM / planning coordination (MIP)

Loads certified Δμ surfaces via adapters, evaluates calibration readiness, and coordinates planning workflows. Does not train models inside MIP.

### Optimization coordination (MIP)

Invokes MMM optimization through adapters and attaches trust to allocation outputs. Does not implement solvers inside MIP.

### Evidence / calibration engine

Maintains the evidence registry: experiment results, replay outcomes, compatibility matrices, freshness. Applies rules for which signals may adjust model parameters or priors.

### Trust / explanation layer

Enriches engine outputs with confidence tiers, rationale templates, uncertainty presentation, and workflow trace IDs. Blocks or downgrades outputs that fail release gates.

### Evaluation / reliability layer

Synthetic benchmarks, replay validation, regression suites, and orchestration eval harnesses. Feeds release gates and research intake exit criteria.

## ASCII Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Conversational Orchestration Layer                       │
│              (intent → workflow request; no causal math)                     │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                   Workflow Planner / Tool Router                             │
│         (deterministic steps, approvals, certified tool calls)             │
└───────────────────────────────────┬─────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
┌───────────────┐         ┌─────────────────┐         ┌─────────────────┐
│ Experimentation│         │  MMM / Planning  │         │  Optimization   │
│    Engine      │         │     Engine       │         │     Engine      │
└───────┬───────┘         └────────┬─────────┘         └────────┬────────┘
        │                          │                            │
        └──────────────────────────┼────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  Evidence / Calibration Engine │
                    │     (registry, gates)        │
                    └──────────────┬──────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌─────────────────┐         ┌─────────────────┐
│    Trust /     │         │   Contracts      │         │  Evaluation /   │
│  Explanation   │◄───────►│   (schemas)      │◄───────►│   Reliability   │
└───────────────┘         └─────────────────┘         └─────────────────┘
```

## Data and Control Flow (Typical Planning Workflow)

1. User asks for a budget scenario via orchestration.
2. Planner loads current MMM production artifact (Δμ surface) if promotion gates pass.
3. Planner optionally pulls registered experiment evidence; calibration engine validates compatibility.
4. Optimization engine solves on Δμ with stated constraints.
5. Trust layer assigns confidence tier, attaches diagnostics and evidence pointers.
6. Recommendation contract returned; orchestration explains without altering numbers.

## Module Mapping (MIP repository)

| Concern | Package | Status |
|---------|---------|--------|
| Contracts | `mip.contracts` | Implemented |
| Evidence / calibration | `mip.evidence` | Implemented |
| Evaluation / gates | `mip.evaluation` | Implemented |
| Trust | `mip.trust` | Implemented |
| Engine adapters | `mip.adapters.geox`, `mip.adapters.mmm` | Planned |
| Orchestration | `mip.orchestration` | Placeholder |
| LLM control plane | `mip.llm` | Planned — see [MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md](./MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md) |
| Workflows | `mip.workflows.*` | Planned |
| App / dashboard / reports | `mip.app`, `mip.dashboard`, `mip.reports` | Planned |

Statistical engines live in `panel_exp` and `mmm` repos—not as copied trees inside MIP. See [REPO_INTEGRATION_STRATEGY.md](./REPO_INTEGRATION_STRATEGY.md).

## Related Documents

- [MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md](./MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001.md)
- [LLM_DECISION_LAYER_VISION.md](./LLM_DECISION_LAYER_VISION.md)
- [LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md](./LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md)
- [REPO_INTEGRATION_STRATEGY.md](./REPO_INTEGRATION_STRATEGY.md)
- [ORCHESTRATION_BOUNDARIES.md](./ORCHESTRATION_BOUNDARIES.md)
- [TRUST_ARCHITECTURE.md](./TRUST_ARCHITECTURE.md)
- [../roadmap/LLM_DECISION_LAYER_ROADMAP.md](../roadmap/LLM_DECISION_LAYER_ROADMAP.md)
- [../adr/ADR-001-full-panel-delta-mu-decision-surface.md](../adr/ADR-001-full-panel-delta-mu-decision-surface.md)
