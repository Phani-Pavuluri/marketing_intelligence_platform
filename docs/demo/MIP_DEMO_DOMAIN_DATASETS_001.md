# Demo Domain Datasets 001

**Artifact ID:** `MIP_DEMO_DOMAIN_DATASETS_001`  
**Type:** demo fixtures + docs/governance  
**Repo checkpoint:** `14ac3d0` (intake policy) / builds on grain + schema contracts  
**Status:** completed  
**Primary fixture:** `data/demo/domain_fixtures/saas_subscriptions/v1/`

---

## 1. Purpose

Create the first canonical MIP demo domain dataset layer for chat-first demos:

- MMM readiness questions
- GeoX readiness questions
- data/grain compatibility questions
- budget planning guardrail questions
- lifecycle walkthrough from raw-ish feeds → readiness → blocked/allowed next steps

This artifact does **not** fit MMM models, compute ROI/ROAS, optimize budgets, assign GeoX markets, or produce lift readouts.

---

## 2. Files created

Under `data/demo/domain_fixtures/saas_subscriptions/v1/`:

| File | Description |
|------|-------------|
| `README.md` | Fixture overview |
| `manifest.json` | Manifest + allowed/forbidden claims + MMM export dependency |
| `raw_spend_week_dma_channel.csv` | week × DMA × channel spend |
| `raw_kpi_week_dma.csv` | week × DMA KPI |
| `controls_week_dma.csv` | week × DMA controls |
| `geo_metadata_dma.csv` | DMA metadata |
| `mmm_weekly_dma_panel.csv` | Canonical MMM-ready panel |
| `geox_design_weekly_dma_panel.csv` | Canonical GeoX design panel |
| `calibration_signals.json` | Demo calibration context |
| `sample_questions.json` | Sample questions by category |
| `expected_answer_behavior.json` | Per-question allowed/blocked behavior |
| `lifecycle_walkthrough.json` | 10-step product lifecycle |

Also:

- `docs/demo/MIP_DEMO_DOMAIN_DATASETS_001.md` (this doc)
- `docs/demo/archives/MIP_DEMO_DOMAIN_DATASETS_001_summary.json`
- `tests/demo/test_mip_demo_domain_datasets_001.py`

---

## 3. Canonical MMM-ready panel

`mmm_weekly_dma_panel.csv` is **week × DMA** with:

- wide channel spend/impressions (`search_*`, `meta_*`, `youtube_*`)
- `paid_conversions` and `arr` **once** per week-DMA
- controls + geo metadata joined

This supports readiness demos only. Presence of a panel **does not** imply an MMM model has been fit.

---

## 4. Canonical GeoX-ready panel

`geox_design_weekly_dma_panel.csv` assumes **Meta** as the example test channel and includes:

- `primary_kpi`, `meta_spend`, `total_spend`
- `eligible`, `region`, `population`
- `period` ∈ `{pre, test_candidate}`

No treatment/control assignment columns. No lift/readout columns.

---

## 5. Raw-ish illustrative feeds

Raw feeds intentionally show the industry-common messiness:

- spend long by channel (`TIME_GEO_CHANNEL`)
- KPI at `TIME_GEO`

Per grain compatibility + intake policy:

- long spend is **not** MMM-ready as-is
- conversion requires pivot of spend wide + keep KPI once per time-geo

---

## 6. Sample question categories

Defined in `sample_questions.json`:

- `mmm_readiness`
- `geox_readiness`
- `grain_compatibility`
- `budget_planning_guardrail`
- `calibration_context`
- `data_missingness`

---

## 7. Lifecycle walkthrough

`lifecycle_walkthrough.json` covers:

1. Select demo dataset — available now  
2. Inspect raw grain — available now  
3. Canonical MMM panel — available now  
4. Evaluate MMM readiness — available now  
5. Ask channel ROI — **blocked** pending `MMMExportBundle` / `ChannelROIArtifact`  
6. Ask budget shift — **blocked** pending `RecommendationContract`  
7. GeoX readiness for Meta — readiness only  
8. GeoX assignment — **blocked** pending governed design artifact  
9. Calibration context — fixture-backed context only  
10. Full lifecycle explanation — explanatory allowed; decision claims blocked  

---

## 8. Allowed claims

- readiness  
- grain compatibility  
- missing data  
- normalization requirement  
- evidence availability  
- blocked reason  
- next required artifact  

---

## 9. Blocked / forbidden claims

- ROI / ROAS  
- lift / incrementality  
- channel contribution  
- budget recommendation / budget reallocation plan  
- GeoX assignment / readout  
- causal claims from these fixtures alone  
- MMM model fit results  

---

## 10. Relationship to MMM-EXPORT-001/002/003

MMM package export contracts are continuing separately (`MMM-EXPORT-001`, `MMM-EXPORT-002`, `MMM-EXPORT-003`).

Until MIP has a governed **MMM export adapter** that can ingest export bundles into Channel ROI / Recommendation artifacts:

- all ROI/ROAS/channel contribution claims remain blocked
- all budget shift / future spend recommendations remain blocked
- fixtures may only teach readiness and refusal language

---

## 11. Why ROI/recommendations remain blocked

Demo panels are synthetic readiness inputs. They do not include fitted posteriors, export bundles, or recommendation contracts. Inventing ROI or budget advice from tables alone would violate MIP decision boundaries.

---

## 12. Recommended next artifact

`MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001` — harden response verification against these fixture-backed expected answer behaviors.

Deferred alternative: `MIP_MMM_EXPORT_READINESS_TRACKER_001` once export adapter work lands.

---

## 13. Boundary check

- No MMM fitting: **yes**  
- No MMM export adapter: **yes**  
- No channel ROI / ROAS / incremental contribution computation: **yes**  
- No budget planning engine / recommendation generation: **yes**  
- No GeoX assignment / lift readout: **yes**  
- No CalibrationSignal runtime ingestion: **yes**  
- No LLM/provider/prompt execution: **yes**  
- No UI demo implementation: **yes**  
