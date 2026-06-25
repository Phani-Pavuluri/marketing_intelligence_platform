# Roadmap Execution Sequence

Condensed implementation sequence derived from [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md).

**Current main:** `6cc48bc`  
**Immediate next phase:** **P4b** — Experiment design objective and data requirement contracts

## What is already implemented

| Layer | Status |
|-------|--------|
| P1 intake session + path recommendation (I1–I2) | ✓ |
| P2 required data assets + sample schemas (I3) | ✓ |
| P3 DataSourceRef + intake manifest (I5) | ✓ |
| P4 column mapping + semantic confirmation (I6) | ✓ |
| Contracts, gates, TrustReport, evidence registry | ✓ |
| LLM Phase 1–5D (safety, intake, readiness, configs, orchestrator, CLI, MockLLM, Streamlit shell) | ✓ |
| Adapters 6A–6C, orchestration 7A–7C, static sibling bridge 8A–8F | ✓ |
| Roadmap docs: 8G–8N, P1–P13, S1–S12, G1–G20, I1–I15 | ✓ documented |

## Platform principle

The platform uses the LLM as a **conversational interface**, not as the measurement brain. Objective interpretation, KPI-family explanation, and clarification questions may be LLM-assisted, but valid data requirements, readiness status, diagnostic eligibility, and decision claims are governed by **deterministic contracts** and **engine-produced reports**.

The LLM must **not** answer data-grounded questions from raw files. It may answer only from governed profile summaries, readiness reports, diagnostic reports, and `TrustReport`s.

LangGraph or equivalent orchestration may route workflow state and invoke approved tools, but it must **not** turn the LLM into an autonomous analyst over raw data.

## Execution themes → roadmap tracks

| Theme | Tracks | Phase |
|-------|--------|-------|
| T1 Core semantics | S1–S12 | P4+ |
| T2 LLM-guided intake | I1–I3 | **P1–P2** |
| T3 Manifests | I4–I5, P8 | P3 |
| T4 Experiment design intake | I6b, MMM→GeoX bridge | **P4b** |
| T5 Common profiling | I7a preliminary analysis | **P4c** |
| T6 Readiness | I7–I8 | P4c → **P5** |
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
  → P4c common data snapshot/preliminary profiling contracts
  → P5 readiness report contracts (I7–I8)
  → P6 CalibrationSignal intake mapping
  → P7 Streamlit/local workflow shell
  → P8 local/demo profiling implementation
  → P17 LangGraph/stateful orchestration skeleton (after contracts stabilize)
  → later panel_exp diagnostic execution / export handoff (gated)
```

Full semantic chain:

```text
S1–S3 → I1–I3 → I5 manifest → I6 mapping → P4b experiment design → P4c profiling
  → I7–I8 readiness → I12 refresh → 8F sibling export → P11/G11 lifecycle
  → 8G–8H → G1 golden → S6/G9 packet → P14–P15 → live (deferred)
```

## Implementation phases (P0–P17)

| Phase | Goal | Runtime allowed |
|-------|------|-----------------|
| **P0** | Roadmap audit ✓ | None |
| **P1** | I1–I2 intake session + path recommendation | Contracts/fixtures only | ✓ implemented |
| **P2** | I3 required data assets | Contracts/fixtures only | ✓ implemented |
| **P3** | I5 DataSourceRef + manifest | In-memory records | ✓ implemented |
| **P4** | I6 column mapping + semantic confirmation | Contracts/fixtures only | ✓ implemented |
| **P4b** | Experiment design objective + KPI/data requirement contracts | Contracts/fixtures only |
| **P4c** | Common data intake profiling + preliminary analysis contracts | Summary records only |
| **P5** | I7–I8 readiness report contracts | Builds on P4c summaries |
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

> **Note:** Integer **P9** remains production table-reference design. LangGraph orchestration is **P17** to avoid renumbering completed phases. Logical orchestration order: after P8.

## P4b — Experiment design objective and data requirement contracts

**Purpose:** Translate an experiment goal into a governed experiment-design intake object **before** generic readiness reports.

**Entry paths:**

1. **MMM-driven experiment design** — MMM output, uncertainty, calibration gap, decision-surface ambiguity, or recommendation suggests validating a channel/tactic/product/geography/KPI with GeoX.
2. **Standalone experiment design** — User directly asks to design a geo experiment (platform, tactic, product, geography, or business objective).

**Example user requests (future):**

- MMM says Meta effect is uncertain for Creative Cloud. Should we design a geo test?
- MMM recommends validating YouTube demand creation for Photoshop. What data do we need?
- I want a DMA-level Meta awareness test for Acrobat.
- I want to test YouTube demand creation for Photoshop in US markets.
- I want a conversion-focused TikTok test for Lightroom trials.
- I want to validate Pinterest incrementality for funnel traffic.

**Future contracts (not implemented in P4b docs task):**

`ExperimentDesignObjective` · `ExperimentDesignUseCase` · `ExperimentObjectiveCategory` · `ExperimentKpiFamily` · `ExperimentDesignIntake` · `ExperimentDesignDataRequirement` · `ExperimentDesignClarificationQuestion` · `ExperimentDiagnosticRequest` · `MMMToGeoXDesignBridge` · `StandaloneGeoXDesignRequest` · `MMMExperimentRecommendationSource` · `ExperimentValidationNeed` · `CalibrationGapReason` · `ExperimentDesignTrigger`

**MMM→GeoX bridge (future):** Capture source MMM artifact/report ID, channel/tactic/product/geography/KPI needing validation, reason (uncertainty, calibration gap, evidence conflict, support issue, decision-surface ambiguity), map to `ExperimentDesignIntake`, require readout to be `CalibrationSignal`-compatible when intended for MMM calibration. **Do not** execute GeoX or claim design feasibility.

**Standalone GeoX design (future):** Clarify objective category, platform/tactic/product/geography, suggest candidate KPI family via deterministic rules, ask missing questions, build experiment design data requirements, prepare `ExperimentDiagnosticRequest` for panel_exp. **Do not** run power, MDE, matching, or design execution.

## P4c — Common data intake profiling and preliminary analysis contracts

**Purpose:** Represent ingested/snapshotted data summaries before the LLM answers data-grounded questions. Supports **both** MMM and GeoX/experiment design.

**Future contracts:**

`DataSnapshot` · `SourceIngestionRecord` · `IngestionMode` · `DataProfileSummary` · `MetricAvailabilitySummary` · `GeoCoverageSummary` · `TimeCoverageSummary` · `MediaCoverageSummary` · `ControlCoverageSummary` · `PreliminaryAnalysisReport` · `LLMAnswerGroundingContext`

**Preliminary analysis summaries (deterministic, future):**

Available date range · weeks/months count · geos/DMAs/markets count · missingness by metric · metric sparsity · geo coverage · media coverage · spend variation · pre-period length · outlier weeks · campaign overlap · KPI at required grain · media at required grain · scope alignment · structural sufficiency for MMM validation or GeoX design diagnostics

**Important distinction:**

- Common preliminary profiling may say whether data is **structurally suitable** for the next diagnostic step.
- It must **not** say the experiment design is valid, powered, or feasible.
- **panel_exp/GeoX** owns power, MDE, matchability, design feasibility, and readout diagnostics.
- **MMM** owns MMM-specific model and calibration diagnostics.

## Objective-to-KPI family mapping (deterministic rules, future)

| Objective category | Candidate KPIs | Required data (minimum) |
|--------------------|----------------|-------------------------|
| **Awareness** | BSV, branded search, direct traffic, site visits, visitors, reach proxy | Geo-week/DMA-week KPI, platform spend/exposure, campaign dates, geo mapping |
| **Demand creation** | Visits, trials, leads, product-page visits, signups, assisted conversion proxies | Geo-week/DMA-week funnel metrics, spend/exposure, controls, campaign/tactic mapping |
| **Conversion** | Conversions, orders, sales, ARR/GNARR, trials-to-paid | Geo-week/DMA-week conversion/sales outcome, media spend/exposure, promos/pricing, seasonality |
| **Retention / usage** | Active users, usage events, renewal, churn | Geo-time panel of usage/retention metrics and relevant exposure/treatment history |
| **MMM calibration** | Must match MMM metric/estimand/channel/scope | Experiment design/readout path producing `CalibrationSignal`-compatible effect estimate and uncertainty |

The LLM may **explain** these mappings and ask clarifying questions. **Deterministic platform rules** decide valid KPI/data requirement mappings. The final primary KPI is **not certified** until semantic confirmation, data availability, and relevant diagnostics exist.

## Diagnostic ownership split

| Owner | Responsibility |
|-------|----------------|
| **LLM** | Clarify objective; ask follow-ups; explain KPI/data requirements; summarize intake/readiness/diagnostic outputs; **does not** compute diagnostics or certify decisions |
| **MIP / common intake** | Intake contracts; required data assets; source refs/manifests; semantic mappings; data snapshot/profiling summaries; readiness reports; LLM answer grounding context |
| **Common profiling / analysis** | Time coverage; missingness; geo coverage; duplicate rows; grain checks; basic metric availability; media/outcome overlap; structural sufficiency summaries |
| **panel_exp / GeoX** | Power/MDE diagnostics; market matchability; design feasibility; duration sensitivity; treatment/control assignment; experiment readout; governed export back to MIP |
| **MMM** | Model-driven experiment recommendation source; calibration gap/uncertainty driver; MMM refresh/calibration diagnostics; post-readout `CalibrationSignal` usage |

## LLM answer grounding (allowed sources)

The LLM may answer data-grounded questions only from:

- Intake session · path recommendation · intake plan · manifest · semantic mapping report
- Preliminary analysis report · readiness report
- MMM diagnostic report · GeoX diagnostic report · `TrustReport`

**Allowed example (after preliminary analysis exists):**

> Your data has 104 weeks, 210 DMAs, and Meta spend in 190 DMAs. For a DMA-level Meta awareness test, BSV is available but missing in 35 DMAs. Traffic has better coverage. This appears structurally ready for GeoX design diagnostics, but panel_exp must still estimate match quality and MDE.

**Disallowed:** lift guarantees · week recommendations · matched markets · design validity claims · budget moves

## P17 — LangGraph / stateful workflow orchestration skeleton

**Purpose:** Route the user through governed modules. LangGraph is a **workflow controller**, not the measurement brain.

```text
LLM + LangGraph = conversation router / workflow controller
MIP contracts     = state, gates, audit trail
Common profiling  = preliminary data summaries
MMM package       = MMM diagnostics / recommendations / calibration context
panel_exp / GeoX  = experiment design diagnostics, power, MDE, readout
LLM               = explains governed outputs back to the user
```

**Future graph nodes:** `IntentClassifierNode` · `ClarificationNode` · `IntakeSessionNode` · `PathRecommendationNode` · `RequiredDataPlanNode` · `DataSourceManifestNode` · `ColumnMappingNode` · `ExperimentDesignRequirementNode` · `PreliminaryProfilingNode` · `ReadinessReportNode` · `PanelExpDiagnosticRequestNode` · `MMMRefreshRequestNode` · `LLMAnswerGroundingNode` · `HumanApprovalNode`

**Graph state (governed objects only):** `MeasurementIntakeSession` · `IntakePathRecommendation` · `IntakePlan` · `MMMIntakeManifest` / `GeoXIntakeManifest` · `SemanticMappingReport` · `ExperimentDesignIntake` · `PreliminaryAnalysisReport` · `ReadinessReport` · `ExperimentDiagnosticRequest` · `TrustReport` — **not** raw dataframe content.

**Approved typed tools (future):** `recommend_intake_path()` · `build_intake_plan()` · `build_intake_manifest()` · `build_semantic_mapping_report()` · `build_experiment_design_requirements()` · `run_common_profile_summary()` · `build_readiness_report()` · `build_panel_exp_diagnostic_request()` · `call_panel_exp_power_diagnostics()` (gated) · `call_mmm_refresh_diagnostics()` (gated)

**LangGraph boundaries:** May decide which governed tool to call next; must not let LLM write arbitrary analysis code; must not expose raw files/dataframes to LLM; must not bypass `TrustReport`, readiness gates, or human approval; must not produce causal/budget/design-validity claims without governed engine outputs.

**Timing:** Do not implement LangGraph runtime before P4b, P4c, P5, and P8 contracts stabilize.

## Future acceptance criteria

### Experiment design intake (P4b)

- Represent MMM-driven and standalone GeoX design requests
- Map objective to candidate KPI family; list objective-specific required data
- Identify required geo/time grain; ask missing clarification questions
- Produce `ExperimentDiagnosticRequest` without executing panel_exp
- Distinguish awareness, demand creation, conversion, retention, MMM calibration objectives
- Block optimizer/budget/design claims until diagnostics exist

### Preliminary profiling (P4c)

- Represent ingested/snapshotted source without exposing raw data to LLM
- Summarize time/geo/metric/media coverage, missingness, grain
- Assess structural suitability for requested workflow; produce LLM-safe grounding context
- Separate structural readiness from design feasibility
- Route GeoX feasibility to panel_exp; route MMM feasibility to MMM diagnostics

### LangGraph orchestration (P17)

- Route intent to governed workflow nodes; preserve typed graph state
- Invoke only approved typed tools; stop at blocked states
- Produce LLM grounding context from governed reports
- Require human approval for decision-supporting transitions; preserve audit trail
- Cannot bypass readiness, `TrustReport`, approval, or engine ownership boundaries

## Capability blockers (quick reference)

| Capability | Blocked until |
|------------|---------------|
| LLM current-performance answers | P11 + P12 + S1–S3 + TrustReport + G11–G20 |
| Experiment design diagnostics | P4b + P4c + P5 + panel_exp gated handoff |
| MMM refresh | P3, P5, P10, 8F handoff, G6 |
| Production data intake | P3, P5, P9, I13–I14 |
| Budget recommendations | P14, P15, G15, G1, approval |
| LangGraph runtime | P4b, P4c, P5, P8 contracts stable |
| Live engine execution | P13, P12, 8G–8N, G3, explicit signoff |

## Do not build yet

Model execution, optimizer execution, sibling imports, scheduled refresh, production connectors, external LLM providers, decision-ready budget actions, automatic artifact promotion, power/MDE/matching execution, LangGraph runtime (until P17 prerequisites), raw-file LLM grounding.

## Canonical ownership (overlaps)

| Concept | Owner doc |
|---------|-----------|
| Metric/estimand/scope | Semantic S1–S3 |
| Experiment design intake | Conversational intake P4b |
| Preliminary profiling | Conversational intake P4c |
| Current vs historical selection | Critical invariants G11, G16 |
| Upload/manifest workflow | Conversational intake I4–I5 |
| LLM safe answering | LLM reasoning 8G–8N + G12–G20 |
| Sibling handoff | Repo integration + 8F |
| LangGraph orchestration | Agentic workflow governance P17 |
| Optimizer/budget | Platform completion P14–P15 + G15 |

## Related documents

- [ROADMAP_EXECUTION_AUDIT_001.md](../audits/ROADMAP_EXECUTION_AUDIT_001.md) — full audit
- [CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md](./CONVERSATIONAL_INTAKE_AND_DATA_HANDOFF_ROADMAP.md)
- [LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md](./LLM_REASONING_AND_MODEL_GUIDANCE_ROADMAP.md)
- [PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md](./PLATFORM_SEMANTIC_AND_DECISION_READINESS_ROADMAP.md)
- [AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md](../architecture/AGENTIC_WORKFLOW_GOVERNANCE_ROADMAP.md)
- [PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md](./PLATFORM_CRITICAL_INVARIANTS_AND_GOLDEN_SCENARIOS.md)
- [PLATFORM_COMPLETION_GAPS_ROADMAP.md](./PLATFORM_COMPLETION_GAPS_ROADMAP.md)
