# MMM / GeoX Industry Data Feed Alignment and Intake Policy 001

**Artifact ID:** `MIP_MMM_GEOX_INDUSTRY_DATA_FEED_ALIGNMENT_AND_INTAKE_POLICY_001`  
**Type:** research / policy (docs + governance only)  
**Repo checkpoint:** `fdb06f9` (domain dataset grain compatibility contract)  
**Status:** completed  
**Scope:** policy-only — did not add or modify production code under `src/mip/`  
**Depends on:** `MIP_DOMAIN_DATASET_GRAIN_COMPATIBILITY_CONTRACT_001`, `MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_CHECKPOINT_AUDIT_001`

---

## 1. Purpose

Clarify how MIP communicates data requirements to users and how it handles uploaded datasets with different grains, unclear geo labels, missing mappings, or non-canonical raw feeds — **before** demo dataset generation.

This artifact defines a two-layer intake stance:

1. **Raw source inspection layer** — messy uploaded files, separate spend/KPI/control/mapping feeds, unclear labels, partial overlaps.
2. **Normalized engine-ready layer** — MMM-ready canonical panel and GeoX-ready canonical panel.

MIP does **not** try to automatically solve all raw-data issues now.

---

## 2. Industry alignment finding

### 2.1 What open MMM and GeoX practice expects

Public package and developer docs converge on **aggregated modeling panels**, not raw multi-file platform exports:

| Practice area | Typical expectation | Sources |
|---------------|---------------------|---------|
| MMM (Robyn) | Weekly (common) time-series with KPI/outcome, paid media spend and/or exposure columns, organic/context controls, holiday/trend handles | [Robyn Analysts Guide](https://facebookexperimental.github.io/Robyn/docs/analysts-guide-to-MMM/), [`robyn_inputs`](https://rdrr.io/cran/Robyn/man/robyn_inputs.html) |
| MMM (Meridian) | KPI, media (exposure + spend), controls; preferably **geo × time**; summable metrics; weekly preferred | [Meridian: Collect and organize your data](https://developers.google.com/meridian/docs/pre-modeling/collect-data), [Meridian: Input data](https://developers.google.com/meridian/docs/advanced-modeling/input-data) |
| Geo experiments (GeoLift) | Historical conversions by geographic unit: **location × time × outcome (Y)**; treatment window; pre-period power design; optional covariates | [GeoLift Walkthrough](https://facebookincubator.github.io/GeoLift/docs/GettingStarted/Walkthrough/), [GeoLift Walkthrough (source)](https://github.com/facebookincubator/GeoLift/blob/main/vignettes/GeoLift_Walkthrough.md) |

**There is no single universal industry schema.** Libraries differ on national vs geo panels, spend vs exposure as primary media input, and exact control catalogs. What is shared:

- **MMM** generally expects aggregated time-series (often week × optional geo) with KPI/outcome, media variables, and controls.
- **Geo experiments** generally expect time × geo outcome panels with treatment/test period markers, adequate pre-period, eligibility/location metadata, and (for design/power) spend or CPIC context.

### 2.2 MIP decision

**MIP aligns with industry practice by accepting messy raw sources for inspection, but requiring normalized canonical panels for engine-ready MMM/GeoX handoff.**

Raw uploads may be long-format, split across files, or incompletely labeled. Those feeds support **readiness and grain-compatibility messaging** (see `MIP_DOMAIN_DATASET_GRAIN_COMPATIBILITY_CONTRACT_001`). They are **not** passed directly to MMM or GeoX engines unless normalized into the canonical panels below.

Demo datasets (`MIP_DEMO_DOMAIN_DATASETS_001`) should ship as **canonical normalized panels**, not as unresolved raw feeds.

---

## 3. Two-layer architecture

### Layer A — Raw source inspection

Purpose: profile, map roles, report grain/overlap gaps, ask for mappings.

Inputs may include separate feeds (see §5). Outputs: inspection/readiness findings, grain comparability status, blocked reasons, user upload requests.

### Layer B — Normalized engine-ready

Purpose: only panels that satisfy grain and uniqueness rules for method handoff.

Outputs:

- **MMM-ready canonical panel** (§4)
- **GeoX-ready canonical panel** (§4)

Conversion from A → B follows grain compatibility + this intake policy (§6–§8). Runtime normalization is **deferred** to `MIP_SOURCE_NORMALIZATION_FROM_RAW_MARKETING_DATA_001`.

---

## 4. Canonical engine-ready intake

### 4.1 Canonical MMM-ready intake

| Dimension | Requirement |
|-----------|-------------|
| Panel grain | **time × geo** |
| KPI grain | **once per time-geo** (no channel-repeated KPI) |
| Media | spend and/or impressions **wide by channel** |
| Controls | joined at a **compatible** time/geo grain |

Example columns:

```text
week, dma,
search_spend, meta_spend, youtube_spend,
paid_conversions, arr,
promo_flag, holiday_flag
```

Rationale: matches industry MMM panel shape (time series + media columns + controls; Meridian explicitly prefers geo×time). Aligns with MIP grain rule that `TIME_GEO_CHANNEL` raw panels with `TIME_GEO` KPI require pivot + keep-KPI-once before MMM.

### 4.2 Canonical GeoX-ready intake

| Dimension | Requirement |
|-----------|-------------|
| Panel grain | **time × geo** |
| Primary KPI | **once per time-geo** |
| Treatment media | test-channel spend (filtered/designed) |
| Optional | total spend; eligibility/exclusion; pre/test period markers; geo metadata (region, population) |

Example columns:

```text
week, dma,
paid_conversions,
meta_spend, total_spend,
eligible, region, population, period
```

Rationale: matches GeoLift-style location × time × outcome requirements, plus MIP grain rule that long channel panels become GeoX design panels via filter-to-test-channel / aggregate-to-total — not by dumping raw channel-long rows into the estimator.

---

## 5. Raw source inspection inputs

Allowed raw uploaded feeds (inspection/readiness only):

| Feed | Typical grain | Role |
|------|---------------|------|
| Spend | time × geo × channel | media activity long format |
| KPI | time × geo | outcomes unique at time-geo |
| Controls | time or time × geo | confounders / calendars |
| Geo metadata | geo | population, region, eligibility |
| Mapping / crosswalk | finer_geo → coarser_geo | required when grains differ |
| Calendar / events | time | holidays, launches |

**Raw sources are inspection/readiness inputs, not directly model-ready unless normalized.**

If a single uploaded file already matches a canonical panel (§4), intake may mark it engine-ready after grain confirmation. Otherwise MIP reports gaps and asks for mapping or re-aggregation — it does not invent joins.

---

## 6. Grain comparability policy

### 6.1 Status vocabulary

| Status | Meaning |
|--------|---------|
| `MATCHED_GRAIN` | Geo/time grains confirmed comparable; join eligible subject to overlap |
| `SAME_GRAIN_PARTIAL_OVERLAP` | Same declared grain; key overlap incomplete |
| `DIFFERENT_GRAIN_MAPPING_REQUIRED` | Grains differ; crosswalk needed, not provided |
| `DIFFERENT_GRAIN_MAPPING_AVAILABLE` | Grains differ; user-provided crosswalk present |
| `UNKNOWN_GEO_COMPARABILITY` | Labels/types insufficient to compare grains |
| `BLOCKED_NO_MAPPING` | Different grain and no usable mapping |
| `BLOCKED_UNSAFE_DISAGGREGATION` | Requested roll-down / allocation |
| `USER_CONFIRMATION_REQUIRED` | Inferrence low confidence or labels unclear |

### 6.2 Rules

1. **Direct join allowed only** when geo/time grains are confirmed comparable (`MATCHED_GRAIN`) and overlap is sufficient.
2. **Partial overlap** (`SAME_GRAIN_PARTIAL_OVERLAP`) must be surfaced as a **warning**; continue on matched keys only — never silently ignore missing keys.
3. **Different grain requires user-provided mapping/crosswalk** (`DIFFERENT_GRAIN_MAPPING_REQUIRED` / `DIFFERENT_GRAIN_MAPPING_AVAILABLE`).
4. MIP supports **roll-up only**: finer observed feed → coarser target grain, and **only with mapping**.
5. **Roll-down / allocation is blocked** (`BLOCKED_UNSAFE_DISAGGREGATION`).
6. **Unknown labels** require user confirmation or mapping (`UNKNOWN_GEO_COMPARABILITY` / `USER_CONFIRMATION_REQUIRED`).
7. MIP **must not infer global mappings for all countries** and must not fetch a global geo dictionary as source of truth.

Operating summary:

```text
same grain + high overlap     → join allowed
same grain + partial overlap  → warn; continue on matched keys only
different grain + mapping     → roll finer feed up to coarser grain
different grain + no mapping  → ask user / block
unclear grain                 → ask user to label geo type or provide mapping
roll down / allocation        → blocked for now
```

---

## 7. Coarser vs finer grain policy

MIP may infer likely finer/coarser direction using:

- declared metadata
- recognized geo type (e.g., ZIP vs DMA vs STATE)
- cardinality / uniqueness hints

Confidence statuses:

| Status | Meaning |
|--------|---------|
| `GRAIN_CONFIRMED` | User-declared or previously confirmed |
| `GRAIN_INFERRED_HIGH_CONFIDENCE` | Strong metadata/signals |
| `GRAIN_INFERRED_LOW_CONFIDENCE` | Weak signals |
| `GRAIN_UNKNOWN_USER_CONFIRMATION_REQUIRED` | Must ask user |

**Important rule:** High confidence alone is not enough to roll up. A **mapping/crosswalk must exist** unless the same grain is directly joinable (`MATCHED_GRAIN`).

Low confidence or unknown labels → `USER_CONFIRMATION_REQUIRED` before any join plan is presented as safe.

---

## 8. Mapping / crosswalk policy

User-provided mapping is required when grains differ. Examples:

- city → state  
- DMA → state/share  
- ZIP → DMA  
- market → region  
- store → market  
- country_subdivision → country  

MIP does **not**:

- invent DMA/state/city mappings  
- treat fuzzy string geo matching as source of truth  
- download/auto-apply a global crosswalk encyclopedia  

### User-facing message examples

**Generic grain mismatch:**

> Your spend data appears more granular than your KPI data. I can roll spend up to the KPI grain, but I need a mapping table from the spend geo values to the KPI geo values. Please upload a mapping table or upload spend already aggregated to the KPI grain.

**DMA-specific:**

> Your spend appears DMA-level and KPI appears state-level. Because DMA-to-state is not always one-to-one, please provide a DMA-to-state crosswalk or upload state-level spend. I cannot safely infer this mapping.

---

## 9. User-facing intake explanation

Standard response shape:

1. **What I found**  
2. **What is missing or ambiguous**  
3. **What I can safely do next**  
4. **What is blocked**  
5. **What to upload next**

### Example

> I found spend by week, market, and channel, and KPI by week and state. These grains do not directly match. I can roll spend up to state only if you provide a market-to-state mapping table. Until then, I can inspect the files and report readiness gaps, but I cannot build a normalized MMM panel.

This shape keeps LLM-visible messaging **metadata/guidance only** (consistent with grain compatibility: LLM status is metadata-only).

---

## 10. Boundary / non-goals

This artifact does **not** implement:

| Non-goal | Status |
|----------|--------|
| Automatic global geo dictionary fetching | **rejected / false** |
| Fuzzy geo resolution as source of truth | **rejected / false** |
| Roll-down allocation | **blocked / false** |
| Invented DMA/state/city mapping | **rejected / false** |
| Dataset generation | **false** |
| Production connector | **false** |
| MMM fitting | **false** |
| GeoX estimator logic | **false** |
| CalibrationSignal runtime change | **false** |
| DecisionSurface / TrustReport / RecommendationContract generation | **false** |
| Optimizer / simulator | **false** |
| ROI / ROAS / lift / incrementality computation | **false** |
| LLM provider or prompt execution | **false** |
| UI implementation | **false** |
| Raw source normalization runtime | **deferred** |

---

## 11. Relationship to existing MIP contracts

| Artifact | Role |
|----------|------|
| `MIP_DOMAIN_DATASET_FIXTURE_STRATEGY_001` | Domains/tiers for demo fixtures |
| `MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_001` | Typed fixture manifests / expectations |
| `MIP_DOMAIN_DATASET_GRAIN_COMPATIBILITY_CONTRACT_001` | Typed raw→convertible/blocked→MMM/GeoX/LLM decisions |
| **This policy** | Human/user intake policy + industry alignment + mapping rules |

Demo fixtures remain **canonical normalized panels**. Raw-feed normalization runtime is later.

---

## 12. Roadmap decision

| Artifact | Decision |
|----------|----------|
| **Current** | `MIP_MMM_GEOX_INDUSTRY_DATA_FEED_ALIGNMENT_AND_INTAKE_POLICY_001` |
| **Next** | `MIP_DEMO_DOMAIN_DATASETS_001` |
| **Later / deferred** | `MIP_SOURCE_NORMALIZATION_FROM_RAW_MARKETING_DATA_001` |

After this policy, do **not** expand intake into an uncontrolled geo-resolution project. Proceed to demo datasets under schema + grain contracts and this policy.

---

## 13. Citations (public sources)

1. Meta Marketing Science — [An Analyst's Guide to MMM (Robyn)](https://facebookexperimental.github.io/Robyn/docs/analysts-guide-to-MMM/)  
2. Robyn — [`robyn_inputs` documentation](https://rdrr.io/cran/Robyn/man/robyn_inputs.html)  
3. Google Meridian — [Collect and organize your data](https://developers.google.com/meridian/docs/pre-modeling/collect-data)  
4. Google Meridian — [Input data](https://developers.google.com/meridian/docs/advanced-modeling/input-data)  
5. Meta GeoLift — [Getting Started Walkthrough](https://facebookincubator.github.io/GeoLift/docs/GettingStarted/Walkthrough/)  
6. Meta GeoLift — [Walkthrough vignette (source)](https://github.com/facebookincubator/GeoLift/blob/main/vignettes/GeoLift_Walkthrough.md)  

---

## 14. Boundary check (this artifact)

- No production contracts/workflows: **yes**  
- No dataset generation: **yes**  
- No raw source normalization runtime: **yes**  
- No automatic global geo dictionary fetching: **yes**  
- No fuzzy geo resolution as source of truth: **yes**  
- No roll-down allocation: **yes**  
- No production connector: **yes**  
- No MMM fitting: **yes**  
- No GeoX estimator logic: **yes**  
- No CalibrationSignal runtime change: **yes**  
- No DecisionSurface/TrustReport/RecommendationContract: **yes**  
- No optimizer/simulator: **yes**  
- No ROI/ROAS/lift/incrementality computation: **yes**  
- No LLM/provider/prompt execution: **yes**  
- No UI/demo: **yes**  
