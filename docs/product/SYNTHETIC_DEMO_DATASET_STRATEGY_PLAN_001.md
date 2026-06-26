# Synthetic Demo Dataset Strategy Plan 001

## 1. Title and status

| Field | Value |
|-------|-------|
| **Title** | Synthetic Demo Dataset Strategy Plan 001 |
| **Status** | Accepted product/data-demo direction |
| **Type** | Product demo / synthetic data / roadmap strategy |
| **Baseline** | Current public demo uses in-code deterministic fixtures (`app/demo_fixtures.py`, `mip.workflows.intake.demo_profiling`). Future product demos and notebooks should use MIP-owned synthetic datasets aligned to governed journeys. |
| **Related docs** | [Product entrypoint and demo experience plan](PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md), [Roadmap execution sequence](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md), [Deterministic usage modes](../service/DETERMINISTIC_USAGE_MODES.md) |

This document records **strategy only**. It does **not** authorize dataset creation, notebook implementation, or UI changes in this phase.

## 2. Core decision

MIP will maintain **custom MIP-owned synthetic datasets** as canonical product demo fixtures because demos must exercise MIP’s **governed user journeys**, not merely reproduce an external MMM or geo-experiment package example.

Industry-standard examples (Robyn-style MMM schemas, Meridian-style MMM schemas, GeoLift-style geo experiment schemas) may be used as **reference schemas and benchmarks**, but they should **not** be the default product story unless they fit the MIP governance journey end-to-end.

MIP is the **control plane**, not the statistical engine. Demo data should teach routing, readiness, calibration, blocking, and evidence tiers—not impersonate certified model output.

## 3. Why custom synthetic datasets

Custom synthetic data lets MIP demonstrate:

- **User maturity progression** — beginner, intermediate, sophisticated paths
- **Data-needed-by-decision education** — what each dataset unlocks or blocks
- **Readiness checks** — national vs geo-week structural suitability
- **Calibration mapping** — valid evidence, missing uncertainty, metric mismatch
- **Blocked claims** — explicit governance boundaries in artifacts
- **Evidence modes** — `general_knowledge_only` through measured diagnostic tiers
- **Governed routing** — question → data summary → workflow → artifact
- **Future LLM extraction** — structured profiles from conversational intake
- **API / SDK / notebook usage** — same fixtures across surfaces
- **Eventual handoff** — to certified MMM/GeoX engines when wired

Synthetic fixtures are **product narrative instruments**, not training data for measurement engines.

## 4. Why not rely only on public examples

Public MMM and geo-experiment examples are valuable but often **do not include** the exact fields and story beats MIP needs:

| Gap in typical public examples | MIP demo need |
|-------------------------------|---------------|
| Business profile context | Cold-start advisory, maturity routing |
| Incomplete-data journeys | Missing geo, missing uncertainty, partial tracking |
| Readiness blocking examples | GeoX blocked on national-only data |
| Experiment readouts with/without SE | Calibration mapping pass/fail |
| Metric/estimand mismatch | Incompatible evidence reports |
| Geo-week readiness | DMA-level structural checks |
| Calibration metadata lineage | `source_artifact_id`, requirement alignment |
| TrustReport / governance artifacts | Decision authorization boundaries |
| Beginner/intermediate journeys | Starter tracking, learning agenda |

Public datasets can inform **schema realism**; MIP-owned synthetics own the **product story**.

## 5. Reference examples

MIP may keep reference mappings to familiar industry patterns:

| Reference family | Purpose |
|------------------|---------|
| **Robyn-style MMM schemas** | Channel spend + outcome time series; media variable conventions |
| **Meridian-style MMM schemas** | Hierarchical/geo MMM field patterns; KPI alignment |
| **GeoLift-style geo experiment schemas** | Geo-level treatment/readout structure; experiment metadata |

**Uses of references (allowed):**

- Keep synthetic schemas realistic and recognizable to sophisticated users
- Guide future adapters between external formats and MIP contracts
- Compare MIP intake/readiness contracts against known MMM/geo patterns

**Not allowed:**

- Mandatory runtime dependency on Robyn, Meridian, GeoLift, or their sample data
- Treating reference schemas as canonical MIP demo fixtures by default
- Implying MIP executes those packages when only referencing schema shape

## 6. Two-stage demo dataset strategy

### Stage A — near-term deterministic demo datasets

**Status:** ✓ implemented — canonical fixtures under `examples/fixtures/stage_a/` with `manifest.json`, README, and validation tests (`tests/examples/test_stage_a_synthetic_fixtures.py`).

**When:** Implemented after P12 SDK/API usage examples (see §10).

**Purpose:** Exercise **implemented** MIP deterministic workflows without MMM/GeoX execution.

**Implemented fixture files:**

| Fixture | Role |
|---------|------|
| `business_profiles/local_fitness_studio.json` | Beginner / local business advisory |
| `business_profiles/dtc_skincare_brand.json` | DTC cold-start journey |
| `business_profiles/b2b_saas_hr_platform.json` | B2B lead-gen advisory |
| `readiness/national_weekly_channel_summary.json` | National weekly readiness (MMM path) |
| `readiness/geo_week_media_outcome_summary.json` | DMA-week geo readiness |
| `readiness/incomplete_missing_geo.json` | GeoX blocked — missing geo |
| `readiness/incomplete_missing_outcome.json` | Measurement blocked — missing outcome |
| `calibration/experiment_readout_valid.json` | Successful calibration mapping |
| `calibration/experiment_readout_missing_se.json` | Blocked — missing uncertainty |
| `calibration/experiment_readout_metric_mismatch.json` | Blocked — incompatible metric |
| `intake/*.json` | Intake/routing request examples |
| `governance/unsupported_claim_examples.json` | Educational blocked-claim examples |

**Supported outputs (deterministic, no engine execution):**

- Cold-start advisory artifacts
- Intake / routing reports
- Readiness reports
- Calibration mapping reports
- Blocked claims and missing-data checklists
- Governance summaries
- API / SDK examples
- Deterministic notebook flows

**No MMM fitting or GeoX design/inference required.**

### Stage B — later real engine-driven datasets

**When:** Only after MMM and GeoX package paths are **certified and wired** through governed adapters.

**Purpose:** Generate **real** output artifacts from actual engines—not mocks.

**Outputs may include (when actually produced):**

- Channel contribution summaries
- ROI / range summaries (with evidence tier labels)
- Response curves and saturation diagnostics
- Scenario planner outputs
- Budget allocation guardrails
- GeoX design / readout artifacts
- Calibrated DecisionSurface artifacts

**Rule:** Show these as product visuals **only** when outputs are produced by governed MMM/GeoX package paths and pass TrustReport / certification gates. MIP routes and governs; engines compute.

## 7. No mock final dashboards

MIP must **avoid mock final dashboards** for advanced business-critical outputs:

| Output type | Before engine readiness | After certified engine wiring |
|-------------|-------------------------|-------------------------------|
| Channel ROI / contribution charts | **Not allowed** as fake product visuals | Allowed from real model outputs + labels |
| Optimizer recommendations | **Not allowed** as fake UI | Allowed from governed DecisionSurface |
| Response curves / saturation | **Not allowed** as fake charts | Allowed from certified MMM diagnostics |
| Scenario planner screenshots | **Not allowed** as fake product | Allowed from governed scenario artifacts |

**Allowed before engine readiness:**

- Textual descriptions of **future** outputs (clearly labeled)
- Data-needed-by-decision matrix and education copy
- Deterministic readiness, advisory, and calibration artifacts
- Output preview **placeholders** labeled “illustrative / requires certified evidence” (per product entrypoint plan)

**Not allowed:**

- Fake ROI charts that look like production analytics
- Fake optimizer recommendations presented as actionable
- Fake response curves implying fitted MMM behavior
- Fake scenario planner screenshots implying DecisionSurface support

Advanced visuals are **trust-sensitive**. MIP should not blur demo fiction with measurement authority.

## 8. Relationship to product entrypoint plan

[PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md](PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md) defines the **single-page landing + chat-first** experience, guided demo journeys, and output preview categories.

This synthetic dataset plan defines **what data powers** those journeys behind the product surface:

| Product entrypoint element | Dataset strategy support |
|----------------------------|-------------------------|
| Guided Demo 1 (starter sales) | Stage A business profiles + advisory fixtures |
| Guided Demo 2 (weekly spend/sales) | Stage A weekly summary + readiness |
| Guided Demo 3 (calibration) | Stage A experiment readout fixtures |
| Guided Demo 4 (budget preview) | **Text / placeholder only** until Stage B |
| Data-needed-by-decision section | Stage A matrix + future Stage B unlocks |
| Ask MIP / LLM workbench (future) | Stage A structured extraction targets |

**Current rule:** Landing page and guided demo work should show **implemented deterministic outputs first**. Advanced visual outputs wait for **real engine-backed artifacts** (Stage B).

## 9. Future notebook strategy

Notebooks are **planned, not created** in this phase.

### Near-term deterministic notebooks (Stage A)

| Notebook | Purpose |
|----------|---------|
| `01_cold_start_advisory.ipynb` | Business profile → advisory plan |
| `02_check_data_readiness.ipynb` | Summary data → readiness reports |
| `03_map_experiment_evidence.ipynb` | Readout JSON → calibration mapping |
| `04_api_service_usage.ipynb` | FastAPI / SDK calls with fixture keys |

### Later engine-backed notebooks (Stage B)

| Notebook | Purpose |
|----------|---------|
| `05_run_or_load_certified_mmm_outputs.ipynb` | Real MMM diagnostics / contribution (gated) |
| `06_geox_readiness_and_readout_flow.ipynb` | GeoX design handoff and readout governance |
| `07_decision_surface_and_scenario_planning.ipynb` | DecisionSurface / scenario artifacts (gated) |

Notebooks should call `mip.workflows.*` and `mip.contracts.*`—not duplicate business logic in notebook cells.

## 10. Recommended roadmap placement

Recommended sequence (engineering and product):

| Step | Milestone |
|------|-----------|
| 1 | **P10c** — Docker / local service smoke |
| 2 | **P11** — API hardening / service packaging plan |
| 3 | **P12** — SDK / API / package usage examples |
| 4 | **SYNTHETIC_DEMO_DATASET_STRATEGY_PLAN_001** — this plan (docs ✓) |
| 5 | **Stage A** — synthetic deterministic fixture files + loaders | ✓ fixtures implemented; **Stage A.2 loaders** in `mip.examples.stage_a_fixtures` |
| 6 | Deterministic notebook flows |
| 7 | Landing-page guided demo integration using **implemented deterministic outputs** |
| 8 | Later real MMM/GeoX engine-backed demo outputs (Stage B) |
| 9 | Advanced dashboard visuals **after** certified outputs exist |

Stage A fixture files and **Stage A.2 loader helpers** (`mip.examples.stage_a_fixtures`) are implemented. Helpers are deterministic, local, and do not run MMM/GeoX engines. Stage B engine-backed visuals remain deferred.

## 11. Acceptance criteria

This docs task is complete when:

- [x] Custom synthetic datasets are established as canonical demo fixtures (strategy)
- [x] Industry examples are positioned as references/benchmarks only
- [x] Near-term deterministic dataset stage (Stage A) is defined
- [x] Later engine-backed dataset stage (Stage B) is defined
- [x] No-mock-final-dashboard rule is explicit
- [x] Relationship to product entrypoint plan is documented
- [x] Roadmap sequence is updated
- [x] No runtime behavior changes are made

## Related documents

- [Product entrypoint and demo experience plan](PRODUCT_ENTRYPOINT_AND_DEMO_EXPERIENCE_PLAN_001.md)
- [Roadmap execution sequence](../roadmap/ROADMAP_EXECUTION_SEQUENCE.md)
- [Repo integration strategy](../architecture/REPO_INTEGRATION_STRATEGY.md)
- [P10 FastAPI/Docker wrapper plan](../service/P10_FASTAPI_DOCKER_WRAPPER_PLAN.md)
