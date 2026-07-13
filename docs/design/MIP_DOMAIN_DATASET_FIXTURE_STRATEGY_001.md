# MIP Domain Dataset Fixture Strategy 001

**Artifact ID:** `MIP_DOMAIN_DATASET_FIXTURE_STRATEGY_001`  
**Type:** strategy / design only (no dataset generation)  
**Repo checkpoint:** `17be95a` (MMM LLM response template checkpoint passed)  
**Status:** completed  
**Scope:** strategy/docs/tests only — did not generate datasets or modify production code under `src/mip/`  
**Depends on:** `MIP_MMM_LLM_RESPONSE_TEMPLATE_CHECKPOINT_AUDIT_001`

---

## 1. Purpose

Define MIP-owned **domain dataset fixture strategy** for realistic spend / KPI / control / calibration / GeoX / MMM demo and evaluation scenarios that can feed:

```text
MMMPlanningRenderedResponse
→ MMMLLMResponseBoundary
→ MMMResponseBoundaryApplicationOutput
→ MMMResponseTemplateOutput
```

and adjacent readiness / CalibrationSignal / GeoX handoff / method-promotion answerability paths.

This strategy does **not** generate datasets, connectors, MMM fitting, GeoX estimators, prompt execution, or provider integration.

---

## 2. Verdict

**`DOMAIN_FIXTURE_STRATEGY_READY_FOR_SCHEMA_CONTRACT`**

**Domain dataset fixture strategy ready for schema contract:** **yes**

**Recommended next artifact:** `MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_001`

**Why:** Stage A advisory/readiness/calibration fixtures already exist, and the MMM LLM template lane is checkpoint-passed. What is missing is a **canonical multi-domain spend/KPI/control/calibration fixture strategy** with expected allowed/blocked planning and LLM behaviors. Inventory is sufficient to proceed; no further blocking audit is required before typed schema/manifest contracts.

---

## 3. Checkpoint presence

| Commit / artifact | Present? |
|-------------------|----------|
| `17be95a` — Audit MMM response template checkpoint | **yes** (BASE) |
| `bb721a3` — Add MMM response template from application package | **yes** |
| `03a3428` — Fix method-promotion and application package typing | **yes** |

---

## 4. What already exists (inventory)

| Existing asset | Role | Gap relative to this strategy |
|----------------|------|-------------------------------|
| `docs/product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md` | Stage A advisory/readiness/calibration demo fixtures | Not a full domain spend/KPI panel + LLM planning-answer fixture strategy |
| `examples/fixtures/stage_a/` | Business profiles, readiness summaries, calibration readouts | Tiny/journey fixtures; not multi-domain MMM panels |
| `app/demo_fixtures.py` / Stage A loaders | Deterministic advisory keys (`dtc_skincare_ecommerce`, etc.) | Not planning-answer / template-eval panels |
| GeoX uploaded CSV / tabular adapters + fixtures | CSV materialization / readout handoff | Package snapshots remain separate (Tier 3) |
| MMM planning eligibility → envelope → renderer → boundary → application → template | Safe LLM packaging chain | Needs realistic domain inputs + expected can_say/cannot_say outcomes |
| Sibling export fixtures (`tests/fixtures/sibling_exports/`) | Pinned package-shaped snapshots | Tier 3 consumption pattern already proven |

**Conclusion:** inventory exists; strategy can proceed to schema contract without a separate inventory-first audit.

---

## 5. Ownership split (three-repo model)

| Owner | Owns | Does not own |
|-------|------|--------------|
| **MIP** | Tier 1 tiny fixtures; Tier 2 realistic synthetic domain panels; scenario manifests; expected sufficiency / allowed-blocked / can_say-cannot_say / human-review outcomes; mapping into MIP gates and LLM packages | MMM fitting; GeoX estimators; causal/statistical simulation engines; production connectors; budget optimization; ROI/ROAS/lift/incrementality computation; spend recommendations |
| **MMM package** | Tier 3 MMM method-simulation generation and native diagnostics | MIP product journeys, LLM response safety, demo narrative packaging |
| **GeoX / panel_exp package** | Tier 3 GeoX/experiment method-simulation generation and native readout artifacts | MIP control-plane gates, CalibrationSignal product mapping story, LLM template packaging |
| **LLM** | Narrator/interface only (consumes packaged slots later) | Authoritative claims, fitting, optimization |

---

## 6. Fixture tiers

### Tier 1 — tiny deterministic unit/demo fixtures

- **Owner:** MIP  
- **Size:** few rows / compact JSON  
- **Purpose:** unit tests, governance tests, CI, LLM template refusal/defer demos  
- **Examples:** incomplete panels, missing controls, missing SE calibration, blocked recommendation scenarios  
- **Rule:** always labeled demo/eval fixtures; never presented as production measurement

### Tier 2 — realistic synthetic domain panels

- **Owner:** MIP  
- **Size:** multi-week / multi-channel synthetic panels with domain narrative  
- **Purpose:** product demos, eval harnesses, planning-answer / template end-to-end dry runs  
- **Examples:** SaaS subscription weekly spend+KPI; e-commerce channel mix; mobile app install/retention; B2B pipeline; geo/local experiment panels  
- **Rule:** synthetic and MIP-authored; may borrow *schema realism* from Robyn/Meridian/GeoLift references without depending on those packages

### Tier 3 — package-exported method simulation snapshots

- **Owner:** MMM / GeoX packages generate; MIP consumes governed snapshots only  
- **Purpose:** optional later demos of certified engine-shaped artifacts  
- **Rule:** MIP never regenerates Tier 3 via fitting/estimators in-repo; consume pinned exports with TrustReport / governance labels (`pinned_sibling_repo_fixture_only`, etc.)

---

## 7. Domains (required)

### 7.1 SaaS subscriptions

| Aspect | Strategy |
|--------|----------|
| Primary KPI | Paid subscriptions, MRR, trial→paid conversion |
| Secondary KPI | Activation rate, churn, expansion ARR |
| Spend channels | Paid search, paid social, content syndication, webinars |
| Controls | Seasonality, pricing changes, sales capacity, competitor index |
| Calibration / experiment | Pricing/geo promo lift with SE; onboarding experiment readout |
| Expected MIP behaviors | Explain descriptive spend share; block budget reallocation; require human review for decisioning; CalibrationSignal map or block on missing SE |

### 7.2 E-commerce

| Aspect | Strategy |
|--------|----------|
| Primary KPI | Revenue, orders, contribution margin |
| Secondary KPI | New customers, AOV, repeat purchase |
| Spend channels | Paid search, paid social, affiliates, email, display |
| Controls | Promo calendar, price index, stockouts, seasonality |
| Calibration / experiment | DMA or holdout promo test with uncertainty |
| Expected MIP behaviors | National weekly readiness for MMM path; block ROI/ROAS claims without gates; cannot_say spend movement |

### 7.3 Mobile app

| Aspect | Strategy |
|--------|----------|
| Primary KPI | Installs, Day-7 retention, in-app purchases |
| Secondary KPI | CPI, LTV proxy (diagnostic-only), session depth |
| Spend channels | UA paid social, UA paid search, incentivized networks |
| Controls | OS version mix, app store rank, creative flighting |
| Calibration / experiment | Geo UA lift test; SKAN/ATT-limited evidence with explicit blockers |
| Expected MIP behaviors | Block causal LTV claims; defer when attribution incomplete; template refusal-only when not ready |

### 7.4 B2B pipeline

| Aspect | Strategy |
|--------|----------|
| Primary KPI | Qualified pipeline $, opportunities created |
| Secondary KPI | SQLs, win rate (diagnostic), sales cycle length |
| Spend channels | Paid search, LinkedIn, events, content |
| Controls | SDR headcount, product launches, seasonality, ICP mix |
| Calibration / experiment | Event/region pilot with SE; CRM attribution caveats |
| Expected MIP behaviors | Block closed-won ROI optimization; allow governance context explain; human review for planning questions |

### 7.5 Geo / local experiments

| Aspect | Strategy |
|--------|----------|
| Primary KPI | Geo-level outcome (sales, foot traffic, leads) |
| Secondary KPI | Power/MDE diagnostics (labels only until engine-certified) |
| Spend channels | Local media, geo-targeted digital, OOH (metadata) |
| Controls | Weather, local events, store openings |
| Calibration / experiment | Treated/control geos, treatment dates, effect + SE |
| Expected MIP behaviors | GeoX readiness pass/fail; incomplete geo blocks GeoX; valid readout maps to CalibrationSignal or blocks mismatch |

---

## 8. Dataset families (required)

| Family | MIP ownership | Purpose |
|--------|---------------|---------|
| **MMM spend/KPI panels** | Tier 1 + Tier 2 | Weekly (or daily) spend + KPI + optional geo grain for planning readiness |
| **GeoX calibration signal fixtures** | Tier 1 + Tier 2 metadata; Tier 3 optional package snapshots | Effect, SE, metric/estimand refs for CalibrationSignal mapping demos |
| **Control-signal catalog fixtures** | MIP | Declared controls per domain; availability/missingness for sufficiency |
| **Experiment metadata fixtures** | MIP (+ Tier 3 package exports later) | Design/readout metadata without estimator execution |
| **Data sufficiency / readiness fixtures** | MIP | Expected readiness statuses and blockers |
| **LLM demo/eval scenario fixtures** | MIP | Question → expected eligibility → expected can_say/cannot_say → expected template mode (refusal/defer/normal-metadata) |

---

## 9. Common fields (all domain fixtures)

Every future domain fixture (schema contract next) should include or reference:

- `fixture_id`, `domain`, `tier`, `grain` (e.g. week, geo-week)  
- `entity_scope` (brand/app/geo set)  
- `time_range`  
- `kpi_primary`, `kpi_secondary[]`  
- `spend_channels[]` with currency and units  
- `controls[]` with availability status  
- `calibration_evidence_refs[]` (optional)  
- `experiment_metadata_refs[]` (optional)  
- `labels[]` (`synthetic_demo_fixture`, `not_production_measurement`, etc.)  
- `lineage` / `provenance`  
- `expected_outcomes` (see §10)

---

## 10. Required expected outcomes

Each fixture must eventually carry expected outcomes for:

| Outcome | Examples |
|---------|----------|
| Data sufficiency | ready / needs_more_data / blocked |
| Schema compatibility | compatible / incompatible field set |
| Control availability | available / partial / missing |
| Calibration compatibility | mapped / needs_more_data / blocked (e.g. missing SE, metric mismatch) |
| MMM model-run eligibility | eligible / blocked / deferred |
| Existing model availability / refresh vs new-run | available / stale / unavailable / refresh_recommended (metadata only) |
| Planning-answer eligibility | explain / defer / block modes |
| can_say / cannot_say expectations | explicit strings for template eval |
| Blocked / deferred reasons | gate names, missing evidence codes |
| Human review requirements | required / not_required |
| Forbidden recommendation behavior | no spend reallocation, no ROI/ROAS claims, no optimizer/simulator output |

These outcomes wire into eligibility → envelope → renderer → boundary → application package → template without inventing claims.

---

## 11. Connections to MIP lanes

| Lane | How fixtures connect |
|------|----------------------|
| MMM readiness / tabular intake | Tier 1–2 panels as uploaded/tabular source refs |
| MMM planning answer eligibility | Expected answer modes from fixture outcomes |
| CalibrationSignal intake/mapping | Calibration + experiment fixtures with SE/metric variants |
| GeoX readout / handoff | Geo panels + metadata; Tier 3 package snapshots optional |
| Method-promotion handoff answerability | Package handoff snapshots remain governance-context-only |
| LLM response boundary / template | LLM scenario fixtures assert can_say/cannot_say, refusal/defer-only when not ready |

---

## 12. Explicitly blocked from this strategy

- Dataset generation in this artifact  
- Production connectors / live ingestion  
- MMM fitting, Bayesian fitting, priors/likelihood/posterior  
- GeoX estimator / design-power engines  
- Causal validation engines presented as product truth  
- DecisionSurface construction/execution  
- TrustReport bypass  
- RecommendationContract generation  
- Optimizer / simulator execution  
- Budget allocation / ROI / ROAS / lift / incrementality computation  
- Fake advanced dashboards that look like certified engine output  
- LLM provider calls / prompt execution / verifier implementation  

---

## 13. Strategy questions answered

1. **Existing docs/contracts:** Stage A synthetic demo plan + fixtures; GeoX/MMM tabular adapters; calibration fixtures; sibling exports; LLM template/application packages.  
2. **Canonical spend/KPI/control/calibration strategy?** Partially via Stage A; **not** as a unified multi-domain planning/LLM fixture strategy — this doc defines it.  
3. **MIP tiers:** Tier 1 + Tier 2.  
4. **Package tiers:** Tier 3 generation.  
5. **Domains first:** SaaS, e-commerce, mobile app, B2B pipeline, geo/local experiments.  
6. **Common fields:** §9.  
7. **Expected outcomes:** §10.  
8. **Connections:** §11.  
9. **Blocked:** §12.  
10. **Next artifacts:** schema contract → demo datasets → verifier audit → prompt/provider/demo path.

---

## 14. Recommended sequence after this strategy

1. **`MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_001`** — typed schemas/manifests for tiers, domains, families, expected outcomes  
2. **`MIP_DEMO_DOMAIN_DATASETS_001`** — generate Tier 1 (+ selected Tier 2) fixtures only after schema contract  
3. **`MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001`** — harden template/slot verification against real fixture outcomes  
4. Prompt / provider / demo path (still gated; no claim invention)

---

## 15. Gaps

### Blocking gaps

None for proceeding to schema contract.

### Deferred nonblocking gaps

- Domain dataset schema contract not yet implemented  
- Domain demo datasets not yet generated  
- Tier 3 package snapshot catalog expansion  
- Verifier / prompt execution / provider / UI demos  
- Full-repo ruff unrelated pre-existing lint debt  

### Known validation limitations

- Global mypy passes.  
- Full-repo ruff may fail on unrelated pre-existing UP035 / UP038 / E501 / F811 issues.

---

## 16. Boundary check (this artifact)

- No production contracts/workflows: **yes**  
- No dataset generation: **yes**  
- No connector implementation: **yes**  
- No MMM fitting: **yes**  
- No GeoX estimator logic: **yes**  
- No LLM/provider/prompt execution: **yes**  
- No verifier/orchestration/UI: **yes**  
- No DecisionSurface/TrustReport/RecommendationContract: **yes**  
- No optimizer/simulator/spend/ROI/lift computation: **yes**  

---

## 17. Evidence paths

- `docs/product/SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001.md`  
- `examples/fixtures/stage_a/`  
- `docs/audits/MIP_MMM_LLM_RESPONSE_TEMPLATE_CHECKPOINT_AUDIT_001.md`  
- `docs/design/MIP_MMM_LLM_RESPONSE_TEMPLATE_RESCOPING_001.md`  
- `src/mip/llm/mmm_response_template.py`  
- `src/mip/llm/mmm_response_boundary_application.py`  
- `docs/architecture/REPO_INTEGRATION_STRATEGY.md`  
- `docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md`  
