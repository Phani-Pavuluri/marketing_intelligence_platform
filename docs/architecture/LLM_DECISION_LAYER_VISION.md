# LLM Decision Layer Vision

## 1. Executive summary

The LLM Decision Layer is MIP's intended **ultimate user-facing interaction layer** for measurement setup, MMM and GeoX workflows, diagnostics, scenario planning, dashboards, reports, and follow-up analysis.

It is **not** a free-form marketing chatbot and **not** a statistical estimator. Statistical systems compute; LLMs guide, configure, explain, route, and summarize over **governed artifacts**—contracts, gates, `TrustReport`, and engine outputs accessed through adapters.

## 2. Product vision

The LLM Decision Layer should eventually help users:

- Understand what data is needed for MMM and experiments
- Clarify business goals and map them to measurable KPIs
- Decide whether MMM, GeoX, calibration, diagnostics, or scenario planning is appropriate
- Identify domain context and recommend domain-specific control variables
- Accept user-provided industry/domain controls (external control fetching is future scope)
- Assess whether provided data is sufficient for the stated objective
- Run or orchestrate data diagnostics and readiness checks
- Generate analysis **config drafts** for MMM and GeoX (engines validate and execute)
- Surface MMM/GeoX outputs conversationally with tier-appropriate language
- Generate governed dashboards and reports
- Answer follow-up questions over structured artifacts with provenance
- Recommend when experiments are needed due to weak evidence or high uncertainty

Initial demo focus: **SaaS/subscription marketing**, MMM channel ROI, calibration readiness, `TrustReport`, and local dashboard/report—see [../roadmap/LLM_DECISION_LAYER_ROADMAP.md](../roadmap/LLM_DECISION_LAYER_ROADMAP.md).

## 3. Core responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Guided intake** | Progressive questions; map objectives to workflows |
| **Feasibility** | Objective ↔ data fit; block or narrow scope when data insufficient |
| **Config assistance** | Draft MMM/GeoX configs; engines validate |
| **Orchestration** | Route to certified tools/workflows via planner—not ad-hoc math |
| **Explanation** | Narrate `TrustReport`, gates, diagnostics, uncertainty |
| **Surfacing gaps** | Measurement recommendations and experiment opportunities |
| **Dashboard/report UX** | Tier-aware display; scenario workbench interaction |
| **Follow-up Q&A** | Answers grounded in artifacts and lineage |
| **Approval routing** | Surface human approval needs; never self-approve |

## 4. Non-responsibilities and hard boundaries

The LLM layer must **never**:

- Estimate causal effects
- Train MMM models or run GeoX inference directly
- Certify evidence or upgrade confidence tiers
- Override `TrustReport` verdicts
- Bypass `CalibrationSignal` governance
- Send raw experiment evidence into MMM
- Approve production recommendations
- Make unsupported causal claims
- Hide missing data, weak diagnostics, or blocked status

See [ORCHESTRATION_BOUNDARIES.md](./ORCHESTRATION_BOUNDARIES.md) and [../vision/PLATFORM_PRINCIPLES.md](../vision/PLATFORM_PRINCIPLES.md).

## 5. Guided user intake

Intake is **progressive**, not a giant form. High-value questions first:

1. What decision are you trying to make?
2. What outcome/KPI do you care about?
3. What domain are you operating in?
4. What data grain do you have?
5. What media breakdown do you have?
6. What geography/market segmentation do you have?
7. What time period/history is available?
8. Which controls are available?
9. Channel-level, geo-level, product-level, or within-channel analysis?

Then recommend feasible workflows with explicit tier expectations.

## 6. Business objective and data requirement framework

**Principle:** The LLM layer must not assume the user's objective is measurable from the data provided. It maps objectives to required KPIs, controls, granularity, and workflow eligibility. If data is insufficient, it recommends a narrower feasible analysis or requests additional data.

| User objective | Data requirement (examples) |
|----------------|----------------------------|
| Conversion ROI | Spend + conversions; conversion-level MMM if diagnostics pass |
| Revenue ROI | Revenue or order value required |
| New customer acquisition | New customer / first-purchase KPI required |
| Awareness | Upper-funnel KPIs: brand search, reach, impressions, survey/brand lift, site visits, platform brand-lift evidence |
| Retention | Renewal, churn, repeat-purchase data required |
| Profit | Revenue, margin, discount, and cost inputs required |

**Future contracts (planned):** `BusinessObjective`, `DecisionObjective`, `MeasurementGoal`, `KPIRequirement`, `DataRequirement`, `DataAvailabilityProfile`, `ObjectiveFeasibilityReport`, `WorkflowRecommendation`.

## 7. Domain-aware control recommendation

Phase 1 uses **user-provided controls** and domain-aware suggestions. Automatic external control fetching is deferred.

| Domain | Example controls |
|--------|------------------|
| SaaS / subscription | Pricing changes, promotions, product launches, trial-flow changes, sales-assisted campaigns, renewals, seasonality, competitive events, macro/business-cycle |
| E-commerce | Discounts, promotions, holidays, inventory, shipping delays, competitor pricing, site/app outages |
| Mobile apps | App releases, app-store rank, platform policy changes, organic installs, seasonality, device/platform mix |
| Retail | Store traffic, weather, local events, holidays, inventory, store openings/closures |

## 8. Data readiness and workflow feasibility

Before MMM or GeoX, MIP classifies workflow eligibility:

| Class | Meaning |
|-------|---------|
| Feasible | May proceed with gates |
| Feasible with warnings | Directional or diagnostic paths |
| Diagnostic only | Explain/explore; no production planning |
| Research only | Prototype/benchmark context |
| Blocked | Cannot proceed; surface blockers |

**Example blockers/warnings:** too few weeks or geos; missing KPI or spend; no pre-period; collinear channels; non-separable treatment; KPI definition changed; insufficient variation; sparse spend; missing controls; inconsistent time grain; missing region/DMA for geo workflows.

**Future concepts:** `DataReadinessReport`, `WorkflowFeasibilityReport`, `AnalysisReadinessReport`.

## 9. Granularity and analysis-level recommendation

Recommend analysis level based on objective, KPI availability, history, grain, geo count, media variation, spend sparsity, collinearity, segmentation, and decision horizon:

- National-week MMM
- Geo-week MMM
- Product-week / segment-week MMM
- DMA/state/region GeoX
- Channel-level analysis
- Within-channel campaign/product/strategy diagnostics (future tactical scope)

**Future concepts:** `GranularityRecommendation`, `AnalysisLevelReadiness`, `VariableSeparabilityReport`.

### Variable separability and roll-up/drop/restrict policy

When broken-down spend exists but variables are too correlated, sparse, or unstable, MIP recommends one of:

- **Roll up** (e.g., combine correlated channel splits for production MMM)
- **Drop** (exclude unstable or unidentifiable variables)
- **Restrict to diagnostic-only** (show splits without decision-grade claims)
- **Collect more data**
- **Run an experiment**
- **Use calibration evidence** if available and gated

**Example:** “Paid Social prospecting and retargeting spend move together in 94% of weeks. The model cannot reliably separate their effects. Recommendation: roll up for production MMM, keep split-level views diagnostic-only, and run an experiment if split-level allocation is decision-critical.”

## 10. MMM and GeoX workflow configuration

LLM **drafts** configs; **engines validate and execute**.

**MMM config draft fields:** KPI/outcome, time grain, modeling level, channels, controls, calibration signals, train/test period, decision objective, scenario constraints, output preferences.

**GeoX config draft fields:** treatment units, control pool, pre/test periods, outcome metric, matching method, inference method, MDE/power target, exclusions, business constraints.

**Future concepts:** `MMMConfigDraft`, `ExperimentConfigDraft`, `ConfigValidationReport`.

## 11. Engine orchestration role

The LLM layer sits above contracts, gates, registry, and adapters. It:

- Selects approved workflow steps from the planner
- Passes parameters to adapter-backed tool calls
- Aggregates contract outputs for explanation
- Does not call private engine internals

Engine repos remain separate per [REPO_INTEGRATION_STRATEGY.md](./REPO_INTEGRATION_STRATEGY.md).

## 12. TrustReport and claim-policy role

`TrustReport` is the **only trust verdict layer**. LLM explanations must:

- Reflect tier, reason codes, warnings, unsupported claims
- Never upgrade or soften blocked/diagnostic states
- Classify narrative claims (causal, calibrated, directional, diagnostic, correlational, unsupported, blocked)

**Bad:** “Display caused $2M incremental revenue.”

**Better:** “The MMM estimates Display contributed $2M, but the TrustReport classifies this as directional because recent experiment calibration is missing.”

**Future concepts:** `ClaimPolicy`, `AllowedClaim`, `BlockedClaim`, `NarrativeSafetyCheck`.

## 13. Measurement gap and experiment opportunity surfacing

MMM suggestions about where experiments are needed must surface through **governed artifacts**, not casual report prose.

```
MMM diagnostics / uncertainty / decision gaps
  → MIP Measurement Gap Detector
  → ExperimentOpportunity / MeasurementRecommendation
  → TrustReport
  → LLM + dashboard surface
  → GeoX designs recommended experiment
```

**Triggers:** high marginal ROI uncertainty; large spend recommendation with weak calibration; high modeled contribution without experiment anchor; uncertain saturation on scale-up; MMM/experiment conflict; collinearity; new channel; high financial-risk decision; stale/incompatible `CalibrationSignal`; model readiness directional/diagnostic-only.

**Future concepts:** `MeasurementRecommendation`, `ExperimentOpportunity`, `MeasurementGapReport`.

## 14. Scenario workbench and dashboard interaction

Users interact with MMM results in a dashboard: adjust spend, lock budgets, min/max constraints, compare scenarios, optimize for conversions/revenue/profit, select risk mode, inspect uncertainty, view blocked/directional/decision-ready labels.

**Governance:** exploratory scenarios may be diagnostic; production recommendations require `DecisionSurface` + `TrustReport` gates; all outputs labeled by trust tier.

**Future concepts:** `ScenarioRequest`, `ScenarioResult`, `ScenarioComparison`, `ScenarioEligibility`, `ScenarioWorkbench`.

## 15. Reports and narrative generation

Reports export locally (HTML first, Markdown second, PDF later). Narrative sections are generated from contracts and `TrustReport`—not invented metrics.

Sections respect `ReportSectionPolicy` and confidence tiers.

### Dashboard and report governance

| Tier | Display policy |
|------|----------------|
| decision_ready | Normal recommendation display allowed |
| directional | Recommendation with warnings |
| diagnostic_only | Charts allowed; production recommendation blocked |
| research_only | Watermark / label as research |
| blocked | Show blockers; do not show decision recommendation |

**Future concepts:** `DashboardViewPolicy`, `ReportSectionPolicy`, `ExportEligibility`.

## 16. Follow-up conversational Q&A

Follow-up questions answer over **structured artifacts** with provenance: model run, evidence IDs, calibration events, `TrustReport` ID, data version.

**Future concepts:** `WorkflowRun`, `ArtifactLineage`, `RunManifest`, `ResultProvenance`.

### Provenance and audit trail

Every dashboard number and LLM statement should trace to artifacts. Users should be able to ask:

- Where did this ROI number come from?
- Which model run produced this?
- Which experiment calibrated it?
- Which TrustReport allowed this claim?
- Which data version was used?

## 17. Human approval and production decision boundaries

Human approval required for:

- Approving production recommendations
- Promoting research methods
- Using Bayesian output in planning (when applicable)
- Launching experiments
- Publishing decision-grade reports
- Exporting production decision recommendations

**Future concepts:** `ApprovalRequest`, `ApprovalStatus`, `PromotionGate`, `DecisionSignoff`.

## 18. LLM provider strategy

- Provider-agnostic interface (`mip.llm.providers`)
- `MockLLMProvider` first for tests and deterministic phases
- Local open-source LLM (e.g. Ollama) for private demo mode
- Optional cloud provider later
- LLM receives structured context; cannot invent model outputs

See [LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md](./LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md).

## 19. Local-first product experience

Primary product shape: install package → run local command → browser UI → upload data → diagnostics/config/workflows → local dashboards/reports → follow-up Q&A. No autonomous production decisioning in initial releases.

## 20. Future hosted/team mode

Later: FastAPI backend, persistent store, auth, team dashboards, scheduled workflows, optional cloud deployment and cloud LLM—not immediate priority.

## 21. Open questions

| Topic | Question |
|-------|----------|
| Intake depth | How many turns before blocking vs. continuing diagnostic-only? |
| Domain packs | Ship SaaS-only control catalog first or multi-domain stubs? |
| Scenario UX | Streamlit-only vs. early FastAPI split |
| Claim policy | Rule-based vs. LLM-assisted classification with audit |
| Approval UX | In-app signoff vs. external workflow tool integration |

## Related documents

- [LLM_DECISION_LAYER_ROADMAP.md](../roadmap/LLM_DECISION_LAYER_ROADMAP.md)
- [LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md](./LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md)
- [ORCHESTRATION_BOUNDARIES.md](./ORCHESTRATION_BOUNDARIES.md)
- [TRUST_ARCHITECTURE.md](./TRUST_ARCHITECTURE.md)
