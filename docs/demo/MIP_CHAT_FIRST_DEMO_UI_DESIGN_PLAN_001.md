# MIP Chat-First Demo UI Design Plan 001

**Artifact ID:** `MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001`  
**Type:** design plan / governance artifact only  
**Fixture:** `data/demo/domain_fixtures/saas_subscriptions/v1/`  
**Depends on:** `MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001`  
**Status:** design complete; implementation deferred

## Purpose and scope

This artifact defines the future chat-first demo UI design. It does not implement UI code or app behavior.

The experience should make MIP feel like a measurement copilot, not a static dashboard. A user starts with a business question; the interface then makes the evidence, readiness result, cannot-say boundary, and next required artifact visible beside the answer. The design translates `sample_questions.json`, `expected_answer_behavior.json`, `lifecycle_walkthrough.json`, and the onboarding guide into a future application experience.

## Primary interaction model

Chat is the primary workflow.  
Demo shortcuts guide the user into chat.  
Evidence and guardrail panels make the chat answer auditable.

Shortcuts must populate or select governed fixture-backed questions rather than create a parallel dashboard workflow. Supporting panels respond to the active conversation and disclose why an answer is allowed, blocked, or deferred.

## Recommended screen structure

| Region | Content and behavior |
|---|---|
| Header | “Marketing Intelligence Platform” |
| Subtitle | “MMM + GeoX readiness copilot” |
| Start here area | Left sidebar on wide screens or a compact top section on narrow screens. Loads the fixture and sends users into chat. |
| Main chat | Primary question-and-answer history, with answer state visibly labeled as readiness, explanation, refusal, or defer. |
| Sample question chips | Fixture-derived shortcuts beneath the empty state and near the composer. |
| Readiness cards | Compact MMM, GeoX, grain, calibration, recommendation, and readout statuses linked to the current question. |
| Evidence inspected panel | Source files, grain, lifecycle step, provenance, and lineage used for the answer. |
| Cannot-say / blocked-claims panel | Persistent, explicit restrictions relevant to the active answer. |
| Next required artifact panel | The governed dependency that would be needed to move past a block. |
| Lifecycle walkthrough panel | Ten-step progress view with available, fixture-backed, blocked, and future states. |
| Learn-more links | Onboarding guide, fixture documentation, verifier audit, and governance explanations. |

Panels may collapse on small screens, but blocked claims and human-review indicators must never disappear or be represented only by color.

## Start-here flow

The future Start here area should offer these entry actions:

1. **Try SaaS subscriptions demo dataset** — select `data/demo/domain_fixtures/saas_subscriptions/v1/` and show its manifest.
2. **Evaluate MMM readiness** — load “Can this dataset support MMM readiness?”
3. **Evaluate GeoX readiness** — load “Can I run a DMA-level GeoX experiment for Meta?”
4. **Explain grain compatibility** — load “Explain the grain difference between raw spend and KPI.”
5. **Ask budget planning guardrail** — load “Can I use this to recommend a budget shift next quarter?”
6. **Review full lifecycle walkthrough** — open the ten-step fixture journey and place its explanation question in chat.

Every action must reference the demo fixture path, a question from `sample_questions.json` or `lifecycle_walkthrough.json`, the corresponding allowed and blocked behavior in `expected_answer_behavior.json`, and its `next_required_artifact`. Selecting an entry does not authorize a claim or execute an engine.

## Sample question chips

Question chips should preserve the fixture categories and exact demo wording:

| Category | Chips |
|---|---|
| `mmm_readiness` | “Can this dataset support MMM readiness?” · “What data is missing for MMM?” |
| `geox_readiness` | “Can I run a DMA-level GeoX experiment for Meta?” |
| `grain_compatibility` | “Explain the grain difference between raw spend and KPI.” |
| `budget_planning_guardrail` | “Can I use this to recommend a budget shift next quarter?” |
| `calibration_context` | “What does the calibration signal let me say?” |
| `data_missingness` | “What can you safely say from this data?” · “What can you not say yet?” |

Clicking a chip should submit or stage the associated question in the main chat. Category labels help users understand whether they are exploring readiness, data structure, context, or a deliberate guardrail.

## Readiness cards

The design includes six cards:

- MMM readiness;
- GeoX readiness;
- Grain compatibility;
- Calibration context;
- Recommendation readiness; and
- GeoX assignment/readout readiness.

Each card must contain the same auditable fields:

- **Status:** available, readiness-only, fixture-context-only, blocked, deferred, or future integration.
- **Evidence inspected:** fixture files and governed artifact references used.
- **Allowed summary:** the bounded descriptive or diagnostic statement.
- **Cannot-say:** explicit claims that must not be inferred from the status.
- **Next required artifact:** the dependency needed to proceed, or “none for this explanation.”

Recommendation and GeoX assignment/readout cards should default to blocked for this fixture. A green readiness card must never imply model fit, causal validity, or decision approval.

## Evidence inspected panel

The evidence panel should render a structured list, not raw data tables by default. It should show:

- fixture files inspected;
- raw spend grain: `week × DMA × channel`;
- raw KPI grain: `week × DMA`;
- canonical MMM panel: `mmm_weekly_dma_panel.csv`;
- canonical GeoX panel: `geox_design_weekly_dma_panel.csv`;
- calibration signal fixture: `calibration_signals.json`;
- the active lifecycle step from `lifecycle_walkthrough.json`; and
- source provenance and lineage supplied by the governed response package.

The panel should distinguish “present in fixture,” “inspected for readiness,” and “produced by an engine.” In this demo, none of the fixture files is an engine-produced result.

## Cannot-say / blocked-claims panel

The UI must clearly surface blocked claims, not hide them. The panel must list the restrictions relevant to the active response and offer a plain-language reason. The complete fixture boundary includes:

- channel ROI;
- ROAS;
- incremental contribution;
- channel contribution;
- budget shift recommendation;
- future spend recommendation;
- optimized spend;
- MMM model fit result;
- MMM posterior/effect result;
- GeoX treatment/control assignment;
- GeoX lift;
- GeoX readout; and
- causal claim.

Blocked requests should still receive a useful refusal: what can be said, why the requested claim is unavailable, what evidence was inspected, and which artifact is needed next. `cannot_say` must dominate overlapping `can_say` text.

## Next-required-artifact panel

For blocked or deferred questions, the UI should display a specific dependency and explain that the artifact is absent rather than merely saying “not available.” Example mappings:

| Question intent | Next required artifact |
|---|---|
| ROI / channel contribution | `MMMExportBundle` plus a governed ROI/contribution artifact. |
| Budget recommendation / optimized spend | `MMMRecommendationContract` or MIP `RecommendationContract`, supported by governed optimizer output. |
| GeoX treatment/control assignment | Governed GeoX design artifact. |
| GeoX lift/readout | Governed GeoX readout artifact. |
| Live recommendation exposed in chat | MIP adapter plus a safe LLM exposure boundary, with review and provenance preserved. |

The panel may link to planned integration documentation, but it must not offer a disabled-looking action that implies the computation already exists.

## Lifecycle walkthrough panel

The panel should read `lifecycle_walkthrough.json` and display these steps:

1. Select demo dataset.
2. Inspect raw spend and KPI grain.
3. Use canonical MMM-ready panel.
4. Evaluate MMM readiness.
5. Ask for channel ROI.
6. Ask for budget shift.
7. Evaluate GeoX readiness.
8. Ask for GeoX assignment.
9. Review calibration context.
10. Explain full MMM + GeoX lifecycle.

Each step must show `available now`, `fixture-backed`, `blocked`, `future integration`, and `next required artifact`. Steps 5, 6, and 8 are deliberate refusal demonstrations. Steps 7 and 9 are available only as readiness/context. Step 10 may explain the lifecycle while keeping all decision claims blocked.

## LLM response boundary integration

The future UI should render governed outputs from the existing response chain:

```text
MMMPlanningRenderedResponse
→ MMMLLMResponseBoundary
→ MMMResponseBoundaryApplicationOutput
→ MMMResponseTemplateOutput
```

This design does not change the chain. The UI adapter must preserve and visibly represent:

- `can_say`;
- `cannot_say`;
- `safe_response_guidance`;
- readiness flags, including whether normal prompt assembly is allowed;
- lineage and provenance; and
- human-review indicators.

If the application package is not ready for normal prompt assembly, the UI must present refusal/defer-only behavior rather than silently converting it to a normal answer. Presentation logic must not widen the governed claim boundary.

## Future integration placeholders

Reserve clearly labeled, inactive integration locations for:

- MMM export adapter;
- MMM ROI/contribution artifact rendering;
- MMM optimizer / `RecommendationContract` rendering;
- GeoX design artifact rendering;
- GeoX readout artifact rendering;
- provider-backed LLM execution;
- uploaded-data workflow; and
- production `TrustReport` / `DecisionSurface` integration.

Placeholders must say “future integration” and must not contain invented values, simulated authorization, or controls that appear operational. Each requires its own implementation and governance review.

## Non-goals

All of the following are false / not implemented by this artifact:

- no UI code;
- no Streamlit changes;
- no LLM provider execution;
- no prompt execution;
- no MMM fitting;
- no MMM export adapter;
- no ROI/ROAS computation;
- no channel contribution computation;
- no optimizer/simulator;
- no budget recommendation;
- no GeoX assignment;
- no GeoX lift/readout;
- no `CalibrationSignal` runtime ingestion;
- no `DecisionSurface` generation; and
- no `RecommendationContract` generation.

## Recommended next artifact

`MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001`

That artifact should define an implementation checklist, component boundaries, fixture adapters, accessibility requirements, and governance acceptance tests before any Streamlit implementation begins.
