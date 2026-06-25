# Roadmap Execution Sequence

Condensed implementation sequence derived from [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md).

**Current main:** `5db32a1`  
**Immediate next phase:** **P5** — Workflow-specific readiness reports

## What is already implemented

| Layer | Status |
|-------|--------|
| P1 intake session + path recommendation (I1–I2) | ✓ |
| P2 required data assets + sample schemas (I3) | ✓ |
| P3 DataSourceRef + intake manifest (I5) | ✓ |
| P4 column mapping + semantic confirmation (I6) | ✓ |
| P4b experiment design objective + data requirements (I6b) | ✓ |
| P4c common intake workbench + preliminary profiling (I6c) | ✓ |
| Contracts, gates, TrustReport, evidence registry | ✓ |
| LLM Phase 1–5D (safety, intake, readiness, configs, orchestrator, CLI, MockLLM, Streamlit shell) | ✓ |
| Adapters 6A–6C, orchestration 7A–7C, static sibling bridge 8A–8F | ✓ |
| Roadmap docs: 8G–8N, P1–P13, S1–S12, G1–G20, I1–I15 | ✓ documented |

## Platform principles

**Common intake first, workflow-specific readiness second.**

MIP uses **one Common Data Intake Workbench** for MMM, GeoX/experiment design, CalibrationSignal intake, and decision-review workflows. Data is uploaded, connected, or declared **once**; MIP profiles, maps, snapshots, and routes it into workflow-specific readiness checks.

The user should **not** need separate MMM and GeoX upload flows. The LLM is the **conversational interface** over common intake and workflow-specific readiness—not the owner of raw data analysis or causal design decisions.

**Explicitly rejected:**

- Separate MMM upload flow · separate GeoX upload flow
- Duplicated column mapping logic · duplicated profiling logic
- LLM answers from raw files

The LLM must answer data-grounded questions only from governed profile summaries, readiness reports, diagnostic reports, and `TrustReport`s. LangGraph may route workflow state but must not expose raw dataframes to the LLM.

## Execution themes → roadmap tracks

| Theme | Tracks | Phase |
|-------|--------|-------|
| T1 Core semantics | S1–S12 | P4+ |
| T2 LLM-guided intake | I1–I3 | **P1–P2** |
| T3 Manifests | I4–I5, P8 | P3 |
| T4 Experiment design intake | I6b, MMM→GeoX bridge | **P4b** |
| T5 Common intake workbench | I6c, workflow support assessment | **P4c** |
| T6 Workflow-specific readiness | I7–I8 | **P5** |
| T7 CalibrationSignal | I9 | P6 |
| T8 Product UI | I10, I15 | P7 |
| T9 Demo profiling impl | I4, I7 | P8 |
| T10 LangGraph orchestration | Agentic governance | **P17** |
| T11 Lifecycle / current-state | P1, G11, G16 | P11 |
| T12 LLM answer governance | 8G–8N, G12–G20 | P12 |
| T13 Refresh governance | I12, P1 | P10 |
| T14 Golden scenarios | G1–G3, 8N | P13 |
| T15 Production hardening | I11, I13–I14 | P9 (table-ref design) |
| T16 Live execution / optimizer | Phase 8+, P14–P15 | P15–P16 deferred |

## Dependency chain (summary)

```text
P1 session/path
  → P2 required assets/sample schemas
  → P3 data source refs/manifests
  → P4 column mapping/semantic confirmation
  → P4b experiment design objective/KPI/data requirement contracts
  → P4c Common Data Intake Workbench + preliminary profiling contracts
  → P5 workflow-specific readiness reports (MMM / GeoX / CalibrationSignal / decision-review)
  → P6 CalibrationSignal intake mapping
  → P7 Streamlit/local workflow shell
  → P8 local/demo profiling implementation
  → P17 LangGraph/stateful orchestration skeleton (after contracts stabilize)
  → later panel_exp/MMM diagnostic execution / export handoff (gated)
```

## Implementation phases (P0–P17)

| Phase | Goal | Runtime allowed |
|-------|------|-----------------|
| **P0** | Roadmap audit ✓ | None |
| **P1** | I1–I2 intake session + path recommendation | Contracts/fixtures only | ✓ implemented |
| **P2** | I3 required data assets | Contracts/fixtures only | ✓ implemented |
| **P3** | I5 DataSourceRef + manifest | In-memory records | ✓ implemented |
| **P4** | I6 column mapping + semantic confirmation | Contracts/fixtures only | ✓ implemented |
| **P4b** | Experiment design objective + KPI/data requirement contracts | Contracts/fixtures only | ✓ implemented |
| **P4c** | **Common Data Intake Workbench** + preliminary profiling contracts | Summary records only; shared by MMM and GeoX | ✓ implemented |
| **P5** | **Workflow-specific** readiness report contracts (I7–I8) | Builds on P4c workbench |
| **P6** | I9 CalibrationSignal mapping | Fixture validation |
| **P7** | I10 Streamlit/local workflow shell | Display only |
| **P8** | I4 demo upload + profiling implementation | Sandbox CSV only |
| **P9** | I11 production table-ref design | Design only |
| **P10** | I12 refresh governance | No model execution |
| **P11** | P1/G11/G16 lifecycle selection | Registry metadata |
| **P12** | 8G–8H LLM answer governance | MockLLM only |
| **P13** | G1–G3 golden harness | Fixture tests |
| **P14** | S6/G9 decision packet | Assembly only |
| **P15** | P6–P7 optimizer governance | **No optimizer execution** |
| **P16** | Live execution gate review | **Deferred** |
| **P17** | LangGraph / stateful workflow orchestration skeleton | Governed tool routing only |

> **Note:** Integer **P9** remains production table-reference design. LangGraph orchestration is **P17**.

## Common Data Intake Workbench (P4c)

**Purpose:** One shared intake layer before workflow-specific readiness branches.

**Shared responsibilities (future):**

Source registration · upload/connect/declaration modes · data source refs · intake manifests · column mapping · semantic confirmation · snapshot metadata · basic profiling summaries · time/geo coverage · metric/media/control availability · missingness summaries · grain/scope detection · LLM-safe data summary reports · **WorkflowSupportAssessment**

**Supports readiness for:** MMM · GeoX/experiment design · CalibrationSignal intake · decision-review

**Future contracts:**

`CommonIntakeWorkbench` · `CommonDataIntakeSession` · `DataSnapshot` · `SourceIngestionRecord` · `IngestionMode` · `IngestedAssetRecord` · `CommonDataProfileSummary` · `MetricAvailabilitySummary` · `GeoCoverageSummary` · `TimeCoverageSummary` · `MediaCoverageSummary` · `ControlCoverageSummary` · `WorkflowSupportAssessment` · `WorkflowReadinessRoute` · `LLMAnswerGroundingContext` · `PreliminaryAnalysisReport`

**WorkflowSupportAssessment** answers: which workflows can this data support? which are blocked? what grain/KPI/source is missing? what diagnostic should run next?

Example statuses: `supports_national_mmm` · `supports_geo_level_mmm` · `supports_geox_design_diagnostics` · `supports_calibration_signal_intake` · `blocked_needs_geo_level_outcome` · `blocked_needs_geo_level_media` · `blocked_needs_calibration_uncertainty` · `blocked_needs_metric_mapping`

**Important distinction:** Common profiling assesses **structural suitability** for the next step. It must **not** claim experiment design is valid, powered, or feasible. **panel_exp/GeoX** owns power, MDE, matchability, and design feasibility. **MMM** owns MMM model and calibration diagnostics.

### Same data, different workflow support (examples)

**National weekly data** (`week, country, product, channel, spend, impressions, conversions`):

> May support national MMM intake. Does **not** support DMA-level GeoX design—DMA/geo-level outcome and media are missing.

**DMA-week data** (`week, dma, product, platform, campaign, spend, impressions, visits, conversions`):

> May support GeoX design diagnostics for a DMA-level test. May support geo-level MMM if enough history and media variation exist. For awareness objectives, visits may be usable but BSV/branded search is not present. For conversion objectives, conversions are present but sparsity must be profiled.

**Experiment readout data** (`experiment_id, metric_id, estimand_id, channel, geo_scope, effect_estimate, standard_error, time_window`):

> May support CalibrationSignal intake if metric, estimand, scope, effect, and uncertainty are valid. **Not** sufficient alone for MMM modeling or new GeoX design.

## P5 — Workflow-specific readiness branching

After common intake/profiling (P4c), readiness **branches by workflow**:

| Branch | Decides |
|--------|---------|
| **MMM readiness** | Time grain; historical coverage; media channels over time; outcome/media scope alignment; controls/promos/seasonality; calibration evidence; national vs geo-level vs calibrated vs refresh vs decision-surface candidate |
| **GeoX / experiment-design readiness** | Geo/DMA/market grain; outcome at geo-time level; media at geo-time level; pre-period data for design diagnostics; geo coverage; KPI vs objective alignment; whether panel_exp should run design diagnostics |
| **CalibrationSignal readiness** | Effect estimate + uncertainty; metric/estimand/channel/geo/time mapping; structured enough for `CalibrationSignal`; governed vs stale vs blocked |
| **Decision-review readiness** | `TrustReport` present; evidence alignment; metric/estimand/scope/freshness; human approval; blocked vs diagnostic vs decision-supporting |

## P4b — Experiment design objective and data requirement contracts

**Entry paths:** MMM-driven (uncertainty, calibration gap, evidence conflict) · standalone GeoX design.

**Future contracts:** `ExperimentDesignObjective` · `ExperimentDesignIntake` · `MMMToGeoXDesignBridge` · `StandaloneGeoXDesignRequest` · `ExperimentDiagnosticRequest` · (see [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md) I6b)

**Objective-to-KPI families (deterministic, future):** awareness · demand creation · conversion · retention/usage · MMM calibration (must match MMM metric/estimand/scope).

## Diagnostic ownership split

| Owner | Responsibility |
|-------|----------------|
| **Common MIP intake/profiling** | Upload/connect/declaration; source registration; snapshots; mapping; semantic confirmation; structural profiling; workflow support assessment; LLM-safe summaries |
| **MMM** | MMM data sufficiency; media time-series; channel coverage; calibration use; model refresh; decision surface diagnostics |
| **GeoX / panel_exp** | Design feasibility; pre-period sufficiency; power/MDE; matchability; treatment/control; duration sensitivity; readout |
| **LLM** | Clarify intent; explain required data; explain insufficiency; summarize governed reports—**no** diagnostic computation or certification |

## LLM role in common intake (allowed vs disallowed)

**May say:**

> You asked for DMA-level GeoX design, but your uploaded data is national-week only. GeoX design needs geo/DMA-level outcome and media data.

> You asked for an awareness test. Your data includes visits and conversions but not BSV or branded search. Visits may be a proxy, but the platform should confirm whether traffic is acceptable as the primary KPI.

**Must not say:** this test is powered · use 8 weeks · these are the matched markets · the design is valid · move budget to this channel

## Future acceptance criteria

### Common intake workbench (P4c)

- User provides data **once** through common intake
- Same data evaluated for MMM, GeoX, CalibrationSignal, and decision-review support
- Platform reports grain (national, geo, DMA, weekly, daily, monthly)
- Platform explains when more granular data is needed for GeoX
- Platform explains when longer history is needed (without claiming final feasibility)
- Platform explains KPI gaps for awareness/demand/conversion goals
- LLM explains workflow-specific gaps from governed reports only
- Common layer cannot produce lift, MDE, power, matched markets, or budget recommendations

### Experiment design intake (P4b)

- MMM-driven and standalone GeoX requests; objective→KPI mapping; `ExperimentDiagnosticRequest` without executing panel_exp

### LangGraph (P17)

- Route intent to governed nodes; typed graph state; approved tools only; human approval for decision-support transitions; audit trail; no bypass of readiness/`TrustReport`/engine boundaries

## Capability blockers (quick reference)

| Capability | Blocked until |
|------------|---------------|
| Workflow-specific readiness | P4c workbench + P5 contracts |
| Experiment design diagnostics | P4b + P4c + P5 + panel_exp gated handoff |
| LLM current-performance answers | P11 + P12 + S1–S3 + TrustReport + G11–G20 |
| LangGraph runtime | P4b, P4c, P5, P8 contracts stable |
| Live engine execution | P13, P12, 8G–8N, G3, explicit signoff |

## Do not build yet

Model execution, optimizer execution, sibling imports, actual file upload/parsing, production connectors, power/MDE/matching, LangGraph runtime (until P17 prerequisites), raw-file LLM grounding, lift/budget/design-validity claims from common intake alone.

## Canonical ownership (overlaps)

| Concept | Owner doc |
|---------|-----------|
| Common intake workbench | This doc P4c; Conversational intake I6c |
| Workflow-specific readiness | Conversational intake I7–I8; P5 |
| Experiment design intake | Conversational intake I6b; P4b |
| LangGraph orchestration | Agentic workflow governance P17 |

## Related documents

- [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
- [LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md](./LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md)
- [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](../architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md)
- [REPO_INTEGRATION_STRATEGY.md](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md)
