# LLM Decision Layer Roadmap

Phased plan for the LLM Decision Layer and local-first product experience. Aligns with platform roadmap Phase 7+ but details LLM-specific delivery.

## 1. Roadmap summary

Delivery order: **document → deterministic safety → intake/feasibility → readiness → config drafts → local demo app → MMM dashboard/report → measurement gaps → adapter orchestration → scenario workbench → governed recommendations → hosted mode**.

No autonomous agents or production decision automation in early phases.

## 2. Current status

**Phase 0 (in progress):** Vision, roadmap, and local-first deployment strategy documented.

**Platform prerequisites (largely done):** contracts, gates, `TrustReport` assembly, evidence registry, calibration audit, model calibration readiness.

**Not started:** `mip.llm`, `mip.workflows`, `mip.app`, dashboards, LLM providers, intake schemas.

## 3. Current agreed defaults

| Area | Default |
|------|---------|
| Demo domain | SaaS/subscription marketing |
| Initial workflow | MMM channel ROI + calibration readiness + TrustReport + dashboard/report |
| Initial UI | Local Streamlit app |
| LLM backend | Provider-agnostic; `MockLLMProvider` first |
| Local LLM | Ollama or similar after deterministic contracts |
| Cloud LLM | Optional later |
| Execution | No autonomous agents initially |
| Reports | HTML first, Markdown second, PDF later |
| Data policy | User-provided data and controls; external control fetch deferred |
| Dashboard | MMM-focused: TrustReport, diagnostics, calibration/evidence placeholders |
| GeoX UI | After MMM-focused demo |

## 4. Phase 0: Documentation and scope lock

**Deliver:** This roadmap, [LLM_DECISION_LAYER_VISION.md](../architecture/LLM_DECISION_LAYER_VISION.md), [LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md](../architecture/LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md).

**Exit:** Requirements and boundaries agreed; no LLM implementation yet.

## 5. Phase 1: Deterministic safety and explanation context

**Deliver:**

- Intent classification (workflow vs. question vs. unsafe)
- Risk classification
- `TrustReport` explanation context builder
- Allowed/blocked action lists
- No real LLM API calls

**Future code:** `WorkflowIntent`, `IntentRiskLevel`, `IntentClassification`, `LLMExplanationContext`, `context_from_trust_report`.

**Exit:** Deterministic tests for explanation templates and blocked intents.

## 6. Phase 2: Business objective intake and data requirement framework

**Deliver:**

- Catalog mapping objective → KPI / controls / grain
- Feasibility check from available data profile
- Fallback when objective unsupported

**Future concepts:** `BusinessObjective`, `MeasurementGoal`, `KPIRequirement`, `DataRequirement`, `ObjectiveFeasibilityReport`.

**Exit:** SaaS demo objectives covered with deterministic feasibility responses.

## 7. Phase 3: Data readiness and workflow feasibility

**Deliver:**

- `DataAvailabilityProfile` inference from uploads
- Readiness diagnostics (weeks, geos, KPI, spend, controls, grain)
- Workflow eligibility classification

**Future concepts:** `DataReadinessReport`, `WorkflowFeasibilityReport`, `AnalysisReadinessReport`.

**Exit:** Block/warn/pass paths tested without engines.

## 8. Phase 4: Config drafting for MMM and GeoX

**Deliver:**

- `MMMConfigDraft` and `ExperimentConfigDraft` schemas
- `ConfigValidationReport`
- No engine execution

**Exit:** Draft + validate round-trip tests; GeoX draft stub acceptable.

## 9. Phase 5: Local-first demo app

**Deliver:**

- Local command: `mip demo` or `mip app`
- Streamlit UI
- Sample SaaS data path
- Deterministic readiness + config workflows
- No production decision automation

**Exit:** User can complete intake → readiness → config draft locally.

## 10. Phase 6: MMM-focused dashboard/report demo

**Deliver:**

- Channel ROI and response curve views
- Data diagnostics panel
- TrustReport panel
- Calibration/evidence placeholder panel
- HTML report export
- Follow-up Q&A over structured artifacts (MockLLM or rules)

Fixture-based MMM artifacts allowed if **clearly labeled demo fixtures**.

**Exit:** End-to-end local demo without real MMM repo required.

## 11. Phase 7: Measurement gap and experiment opportunity layer

**Deliver:**

- Formal surfacing of MMM measurement gaps
- `MeasurementRecommendation` / `ExperimentOpportunity` artifacts
- Dashboard panel + LLM explanation of why experiment needed

**Future concepts:** `MeasurementGapReport`.

**Exit:** Gap → recommendation → TrustReport → UI path demonstrated.

## 12. Phase 8: Engine orchestration through adapters

**Deliver:**

- MMM and GeoX via `mip.adapters.*`
- No private engine imports
- Register outputs in `EvidenceRegistry`
- `TrustReport` from gate outcomes

**Exit:** Real or pinned engine outputs pass contract + gate tests.

## 13. Phase 9: Scenario workbench

**Deliver:**

- Dashboard scenario controls (sliders, bounds, objectives, risk mode)
- Scenario trust/eligibility labels
- Diagnostic vs. decision-ready separation

**Future concepts:** `ScenarioRequest`, `ScenarioResult`, `ScenarioComparison`, `ScenarioEligibility`.

**Exit:** Scenario exploration with tier enforcement.

## 14. Phase 10: Governed recommendations and approval workflow

**Deliver:**

- `RecommendationContract` generation
- Human approval workflow
- Production export eligibility
- Blocked/research-only safeguards

**Exit:** No decision-grade export without approval record.

## 15. Phase 11: Hosted/team mode

**Deliver (later):**

- FastAPI backend
- Persistent artifact store
- Auth and team dashboards
- Optional cloud deployment and cloud LLM

**Exit:** Multi-user pilot; not required for initial local demo.

## 16. Future: Within-channel tactical optimization

Deferred scope:

- MTA-like diagnostics, platform data
- Campaign/audience/creative/keyword recommendations
- Experiment-calibrated attribution, tactical signals
- No immediate implementation

## 17. Deferred / non-goals

- Autonomous budget execution
- Ad-platform bidding
- LLM-as-estimator
- Raw experiment → MMM without `CalibrationSignal`
- Hiding blocked tiers in narrative or UI
- Production recommendations without human approval where policy requires

## 18. Open questions

- Streamlit vs. FastAPI timing for Phase 5–6
- When to introduce real Ollama vs. keep MockLLM through Phase 7
- Single vs. multi-domain intake catalogs at launch
- Approval workflow integration (in-app vs. external)

## Related documents

- [LLM_DECISION_LAYER_VISION.md](../architecture/LLM_DECISION_LAYER_VISION.md)
- [LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md](../architecture/LOCAL_FIRST_APP_AND_DEPLOYMENT_STRATEGY.md)
- [ROADMAP.md](./ROADMAP.md)
