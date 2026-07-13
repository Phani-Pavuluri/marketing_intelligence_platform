# MIP Demo Onboarding and Use Case Guide 001

**Artifact ID:** `MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001`  
**Audience:** new demo users  
**Demo fixture:** `data/demo/domain_fixtures/saas_subscriptions/v1/`  
**Status:** guide complete; no runtime or UI implementation

## What this demo is

The MIP demo is a chat-first measurement readiness copilot for MMM and GeoX workflows.

It uses deterministic SaaS subscriptions demo fixtures to show how MIP explains readiness, checks grain compatibility, identifies what can be answered safely, and blocks unsupported decision claims. It does not run a live MMM model, run GeoX design or readout, execute an LLM provider or prompt, or generate recommendations.

Think of this demo as a governed walkthrough of the questions and evidence that come before measurement execution—not as an MMM or experimentation engine.

## Start here

1. Load or select the SaaS subscriptions demo fixture.
2. Ask an MMM readiness question.
3. Ask a GeoX readiness question.
4. Ask a grain compatibility question.
5. Ask a budget planning question.
6. Review what MIP can and cannot safely say.

A useful first pass is to ask one question from each category below. Readiness answers should explain the available evidence. Requests for ROI, recommendations, assignment, or lift should produce a clear blocked reason and name the next required artifact.

## Demo fixture files

All files are under `data/demo/domain_fixtures/saas_subscriptions/v1/`.

| File | What it is for |
|---|---|
| `raw_spend_week_dma_channel.csv` | Illustrative long-form spend at `week × DMA × channel`; it exposes the normalization requirement. |
| `raw_kpi_week_dma.csv` | KPI observations at `week × DMA`; the KPI must remain once per time-geo. |
| `controls_week_dma.csv` | Promotion, holiday, launch, and competitor controls at `week × DMA`. |
| `geo_metadata_dma.csv` | DMA eligibility and geographic context. |
| `mmm_weekly_dma_panel.csv` | Canonical wide-spend, once-per-`week × DMA` panel for MMM readiness inspection only. |
| `geox_design_weekly_dma_panel.csv` | Meta example design-intake panel with KPI, spend, eligibility, and pre/test-candidate periods; no assignment or lift. |
| `calibration_signals.json` | Fixture/demo calibration context only; it is not runtime-ingested or applied to a live model. |
| `sample_questions.json` | Suggested questions grouped by safe-answerability category. |
| `expected_answer_behavior.json` | Per-question allowed summaries, cannot-say boundaries, blocked claims, evidence, and next artifacts. |
| `lifecycle_walkthrough.json` | Ten-step raw-data-to-readiness walkthrough with explicit blocked and future steps. |

`manifest.json` is the fixture index and governance summary. It records grain, allowed claims, forbidden claims, and the missing MMM export dependency.

## Suggested demo questions

The question set in `sample_questions.json` covers six categories:

| Category | Try asking |
|---|---|
| `mmm_readiness` | “Can this dataset support MMM readiness?” or “What data is missing for MMM?” |
| `geox_readiness` | “Can I run a DMA-level GeoX experiment for Meta?” |
| `grain_compatibility` | “Explain the grain difference between raw spend and KPI.” |
| `budget_planning_guardrail` | “Can I use this to recommend a budget shift next quarter?” |
| `calibration_context` | “What does the calibration signal let me say?” |
| `data_missingness` | “What can you safely say from this data?” or “What can you not say yet?” |

The companion `expected_answer_behavior.json` defines what a safe response may include, what it cannot say, what evidence supports it, whether human review is required, and which artifact must come next.

## What MIP can safely say

For this fixture, MIP may provide these answer types:

- readiness status based on fixture structure;
- grain compatibility between spend, KPI, controls, and canonical panels;
- normalization requirements, including pivoting channel spend wide and keeping KPI once per `week × DMA`;
- missing-data or missing-artifact explanations;
- GeoX design-readiness explanations based on the design-intake panel;
- calibration context as fixture/demo context only;
- the reason a requested claim is blocked; and
- the next required governed artifact.

These are descriptive, diagnostic, and readiness explanations. They do not establish model performance, causal impact, or a decision recommendation.

## What MIP must block

The demo must not claim or calculate:

- channel ROI;
- ROAS;
- incremental contribution;
- channel contribution;
- a budget shift recommendation;
- a future spend recommendation;
- optimized spend;
- an MMM model fit result;
- an MMM posterior/effect result;
- GeoX treatment/control assignment;
- GeoX lift;
- GeoX readout; or
- any causal claim.

A blocked answer is expected behavior. It should explain why the evidence is insufficient and identify the governed artifact needed to proceed.

## Why budget recommendations are blocked

The canonical panel is readiness input, not a fitted model export. MIP cannot recommend budget shifts until a governed MMM export plus `RecommendationContract` path exists. That future path requires:

- `MMMExportBundle`;
- `MMMChannelROIArtifact` or an equivalent governed ROI export;
- `MMMOptimizerResultArtifact` or an equivalent governed optimizer export;
- `MMMRecommendationContract` or the MIP `RecommendationContract`; and
- `MIP_MMM_EXPORT_ADAPTER_CONTRACT_001`.

Until those artifacts are verified and adapted into MIP, channel ROI/ROAS, contribution, optimizer output, future spend, and budget recommendations remain blocked. Fixture values must not be used to invent them.

## Why GeoX assignment and lift are blocked

The demo can inspect whether the GeoX design panel contains readiness inputs such as a weekly DMA KPI, Meta and total spend, eligibility, geography, and pre/test-candidate periods. It does not create treatment/control assignment, execute a design algorithm, or compute a readout or lift.

Moving beyond readiness requires:

- a governed GeoX design artifact;
- a governed GeoX readout artifact;
- package-side GeoX adapter outputs; and
- a MIP adapter/explanation boundary.

Until that future integration exists, MIP must refuse market assignment, powered-design guarantees, expected or realized lift, and causal readout claims.

## Lifecycle walkthrough

`lifecycle_walkthrough.json` represents this ten-step journey:

| Step | What the user does | Available now | Fixture-backed | Blocked | Future integration |
|---|---|---:|---:|---:|---|
| 1 | Select the demo dataset. | Yes | Yes | No | None. |
| 2 | Inspect raw spend and KPI grain. | Yes | Yes | No | None for explanation; ROI/ROAS/lift remain unavailable. |
| 3 | Use the canonical MMM-ready panel. | Yes | Yes | No | Model fitting/export is separate and future. |
| 4 | Evaluate MMM readiness. | Yes | Yes | No | `MMMExportBundle` through a MIP export adapter is required for governed results. |
| 5 | Ask for channel ROI. | No | Yes | Yes | Governed `MMMExportBundle` and channel ROI artifact. |
| 6 | Ask for a budget shift. | No | Yes | Yes | Governed optimizer output and `RecommendationContract` path. |
| 7 | Evaluate GeoX readiness. | Yes, readiness only | Yes | No | Governed GeoX design is required beyond intake readiness. |
| 8 | Ask for GeoX assignment. | No | Yes | Yes | Governed GeoX design/assignment artifact. |
| 9 | Review calibration context. | Yes, as context only | Yes | No | `CalibrationSignal` runtime intake and mapped model run. |
| 10 | Explain the full MMM + GeoX lifecycle. | Yes, explanation only | Yes | Decision claims remain blocked | MMM export and GeoX design/readout integrations. |

The lifecycle deliberately includes blocked questions. This lets a new user see the complete story: raw inputs → canonical panels → readiness → governed refusal → future engine/export artifacts.

## Future chat-first UI implications

A future chat-first interface should expose:

- a Start here card;
- sample question chips;
- MMM and GeoX readiness cards;
- blocked-claim explanations;
- a next-required-artifact panel; and
- an evidence inspected panel.

This artifact does not implement UI. These are design implications only; no Streamlit or other interface behavior is changed here.

## Boundary check

This guide implements none of the following: UI, LLM provider execution, prompt execution, MMM fitting, an MMM export adapter, ROI/ROAS or channel-contribution computation, optimizer/simulator execution, budget recommendations, GeoX assignment, GeoX lift/readout, `CalibrationSignal` runtime ingestion, `DecisionSurface` generation, or `RecommendationContract` generation.

## Recommended next artifact

`MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001`

A design plan should define the user flow and evidence/refusal presentation before any direct Streamlit implementation.
