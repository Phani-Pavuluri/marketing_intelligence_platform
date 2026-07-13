# SaaS subscriptions demo fixture v1

**Artifact:** `MIP_DEMO_DOMAIN_DATASETS_001`  
**Domain:** `saas_subscriptions`  
**Path:** `data/demo/domain_fixtures/saas_subscriptions/v1/`

## Purpose

Tiny deterministic fixtures for chat-first demos covering:

- MMM readiness inspection
- GeoX design readiness inspection
- grain compatibility (week×DMA×channel spend vs week×DMA KPI)
- budget-planning guardrails (ROI/recommendations stay blocked)

## Files

| File | Role |
|------|------|
| `raw_spend_week_dma_channel.csv` | Illustrative raw spend (week × DMA × channel) |
| `raw_kpi_week_dma.csv` | Raw KPI (week × DMA) |
| `controls_week_dma.csv` | Controls (week × DMA) |
| `geo_metadata_dma.csv` | DMA metadata / eligibility |
| `mmm_weekly_dma_panel.csv` | Canonical MMM-ready-ish panel (not fitted) |
| `geox_design_weekly_dma_panel.csv` | GeoX design-intake panel (no assignment/lift) |
| `calibration_signals.json` | Demo prior context only |
| `sample_questions.json` | Demo question catalog |
| `expected_answer_behavior.json` | Allowed/blocked answer contracts |
| `lifecycle_walkthrough.json` | Raw → readiness → blocked ROI/budget story |
| `manifest.json` | Fixture manifest + claim boundaries |

## Scale

- 8 DMAs
- 14 weeks starting `2024-01-01`
- Channels: Search, Meta, YouTube
- KPIs: `paid_conversions`, `arr`

## Hard boundaries

Does **not** include MMM fitting, ROI/ROAS, budget optimization, GeoX treatment/control assignment, or GeoX lift readout.

ROI and budget recommendations remain blocked until MIP consumes governed MMM export artifacts (`MMM-EXPORT-001/002/003`).
