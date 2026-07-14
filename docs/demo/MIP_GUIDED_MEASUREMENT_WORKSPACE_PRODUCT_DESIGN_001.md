# MIP Guided Measurement Workspace Product Design 001

## Decision

This design replaces the sample-stage menu with one persistent conversation, one vertical SaaS measurement journey, and one readiness-only user-data entry path. It is a product and interaction contract, not a runtime implementation. It does not authorize model fitting, optimization, GeoX execution, calibration, upload parsing, or provider-backed LLM answers.

The journey is:

```text
business goal → data intake → readiness → MMM evidence → planning
→ GeoX evidence gap → calibration → refreshed evidence → decision package
```

The current browser review remains failed: the application mechanics worked, but the experience is not externally demo-ready until this design is implemented and reviewed.

## Product positioning

MIP helps growth teams turn marketing data into trustworthy spend decisions. It shows channel performance, incremental impact and ROI only where evidence supports them, next-quarter planning context, scenario-comparison readiness, MMM evidence gaps, GeoX design readiness, and the path from experiment evidence to a recalibrated MMM. It prevents unsupported recommendations by labeling what is supported, uncertain, blocked, and next.

The hero is frozen for the implementation task:

> **Turn marketing data into trustworthy spend decisions.**
> Understand channel performance, see where evidence is strong or weak, and move from measurement to a decision-ready next step without overclaiming.

The welcome message is frozen as: “Tell me the business decision you need to make. I will guide the measurement journey, explain the evidence available, and keep unsupported conclusions visibly blocked.”

The four jobs are:

| Job | User outcome | Workspace response |
| --- | --- | --- |
| Measure | Understand observed and incremental channel performance. | Organize data/readiness and expose fixture-backed MMM evidence with its limits. |
| Plan | Prepare a future-quarter spend decision. | Show a planning card and scenario inputs, while keeping live optimization blocked. |
| Experiment | Close a material evidence gap. | Explain why GeoX is relevant only after the gap is identified and show design/readiness evidence. |
| Learn | Incorporate trustworthy new evidence over time. | Show the recalibration path and clearly mark live calibration as future work. |

## Entry modes and state

There are exactly two primary entry modes:

1. **Explore a sample use case** starts the curated SaaS subscriptions sample.
2. **Analyze my data** starts a readiness-only intake flow; it must not imply live model fitting or a recommendation.

The workspace maintains visible context: `business_goal`, `dataset_mode`, `dataset_identity`, `time_period`, `measurement_question`, `current_tile`, `evidence_state`, `uncertainty`, and `next_safe_action`. Reset clears the context. Dataset selection is replaced by the active-data summary after a selection is made; it is not left as a repeated control above the journey.

Sample SaaS planning card copy is frozen:

> **SaaS growth planning: decide how to prepare next quarter’s spend.**
> Review the fixture-backed channel evidence, compare the decision constraints, and identify what must be validated before a budget recommendation. Live optimization is not available in this demo.

## Vertical analytical journey

The page presents the following stacked narrative, with chat able to open, focus, summarize, or advance a tile. A tile is a meaningful measurement question, not an implementation stage selector.

| # | Tile | User question and content | Current classification |
| --- | --- | --- | --- |
| 1 | Define decision | What decision, KPI, market, horizon, constraints, and owner matter? | Fixture-backed intake |
| 2 | Bring data | What data is available, preloaded, or ready for intake? | Sample live; user path readiness-only |
| 3 | Inspect and validate | Are periods, channels, outcomes, mapping, and quality sufficient for the question? | Authored/precomputed readiness evidence |
| 4 | Build and validate MMM | What fixture-backed MMM evidence exists, and what validation limits apply? | Existing fixture-backed evidence; no live fitting |
| 5 | Channel results | What channel signal, uncertainty, and evidence label can be shown? | Existing fixture-backed evidence |
| 6 | Plan next quarter | What decision constraints and scenario questions should guide planning? | Visible but blocked for live optimization |
| 7 | GeoX evidence gap | Is a material decision still unsupported enough to justify an experiment? | Conditional, shown only after a stated gap |
| 8 | GeoX evidence | What design/readiness evidence is available for an experiment? | Readiness/precomputed only; no live execution |
| 9 | Recalibrate MMM | How could validated experiment evidence update future measurement? | Future path; no live calibration |
| 10 | Decision package | What can be decided now, what is uncertain, blocked, and next? | Composed from evidence labels, never a budget recommendation |

The planning tile always exists, because planning is the user’s job even when optimization is unavailable. Its blocked state names the missing capability, the safe preparatory action, and the evidence it would require. The GeoX tiles do not appear merely because an experiment feature exists: Tile 7 follows a visible, decision-relevant evidence gap; Tile 8 follows only if Tile 7 finds GeoX relevant.

## Conversation contract

Chat is the workspace controller, not a separate generic chatbot. It can explain the focused tile, navigate to a relevant tile, record a business goal, summarize evidence, and propose a safe next action. It must not silently change data, execute a model, calculate an unverified result, or represent an authored fixture as a live analysis.

Every answer has these layers:

1. direct answer to the question;
2. current business and data context;
3. evidence and source classification;
4. uncertainty, limitation, or blocked capability;
5. one safe next action; and
6. relevant follow-on questions.

The four onboarding questions must produce substantively distinct deterministic answers:

| Prompt | Required answer focus | Tile action |
| --- | --- | --- |
| “Which channels are contributing to growth?” | Explain fixture-backed channel results, distinction between observed and incremental evidence, and uncertainty. | Focus Channel results. |
| “How should I plan next quarter’s spend?” | Explain planning constraints and inputs; explicitly state that optimization and recommendations are blocked. | Focus Plan next quarter. |
| “Where is our measurement weakest?” | Identify the evidence gap, why it matters for the decision, and whether GeoX readiness is relevant. | Focus GeoX evidence gap. |
| “What should I do next?” | Give the decision-package summary: supported, uncertain, blocked, and next safe action. | Focus Decision package. |

A future grounded-LLM path may be added only after governed tools, approved context, provenance, claim labels, and runtime controls exist. It must use the same layered-answer contract. Until then, the deterministic fallback maps each intent to a distinct, context-aware response and remains visibly limited to available fixture and readiness evidence. Claim verification is mandatory: “incremental,” “ROI,” “lift,” “recommended,” and “optimal” require actual approved evidence; otherwise the response describes the gap or block.

## Readiness-only Analyze my data design

The future user-data path supports file intake, profiling, mapping, compatibility checks, and readiness reporting only. It accepts CSV first, with a future explicit schema contract for supported outcome, channel/spend, time, and optional geography fields. The flow is:

```text
choose Analyze my data → select file → inspect profile → map columns
→ run compatibility/readiness checks → review limitations and safe next action
```

No implementation may show a persistence claim until the actual runtime has a verified file lifecycle. The future disclosure must accurately state the verified behavior, including whether a file is session-only, retained, or sent elsewhere; it must not currently promise “not persisted.” The initial result is not MMM fitting, model output, scenario simulation, GeoX execution, or a budget recommendation.

Reusable MIP infrastructure includes uploaded-CSV planning/MMM adapters, input plans, workflow readiness contracts, and GeoX uploaded-CSV bridge/runtime modules. The missing implementation is the Streamlit entry, controlled parsing and profiling, session lifecycle, mapping UX, compatibility presentation, claim-safe readiness result, and browser-verified disclosure. Those gaps keep the entire user-data path readiness-only.

## Text wireframes

1. **Landing:** hero, trust boundary, two entry buttons, and the first question.
2. **Sample activation:** active SaaS context replaces dataset selector; chat introduces the decision.
3. **Define decision:** goal/KPI/horizon/constraints summary beside chat follow-up.
4. **Bring data:** preloaded sample provenance and available field summary.
5. **Inspect and validate:** readiness checks with pass, caution, and blocked labels.
6. **MMM and channel results:** evidence cards, provenance, uncertainty, and chat explanation link.
7. **Plan next quarter:** SaaS growth planning card, decision constraints, and blocked live-optimization banner.
8. **Evidence gap and GeoX:** gap rationale followed conditionally by GeoX readiness card.
9. **Recalibrate:** directional loop from experiment evidence to future refreshed MMM, marked future.
10. **Decision package / user-data entry:** supported, uncertain, blocked, next; Analyze my data opens the readiness-only intake flow.

## Runtime fixture and capability matrix

| Workspace element | Present source | Mode | Missing capability / boundary | Owner for implementation |
| --- | --- | --- | --- | --- |
| SaaS journey | `saas_subscriptions` journey fixtures | Existing fixture-backed | Vertical rendering and context binding | Guided workspace UI task |
| Readiness summary | Authored/precomputed sample artifacts | Existing fixture-backed | Runtime inspection of user files | Intake task |
| MMM/channel evidence | Authored fixture artifacts | Existing fixture-backed | Live fitting, validation, ROI claims beyond evidence | MMM governance task |
| Planning | Sample planning context | Blocked | Scenario simulation, optimization, recommendation | Planning engine task |
| GeoX gap/readiness | Existing readiness contracts/fixtures | Readiness-only | Design/execution/readout | GeoX workflow task |
| Recalibration | Conceptual workflow | Future | Validated signal ingestion and live calibration | Calibration task |
| Conversation | Deterministic product-flow responses | Existing fixture-backed | Governed grounded provider path | Conversation governance task |
| Analyze my data | Contract-level reusable modules | Readiness-only future UI | UI, parser, mapping, lifecycle verification | Upload intake task |

## Implementation sequence

1. Create a guided-workspace implementation plan that maps every tile to a supported artifact and state transition.
2. Implement the frozen hero, entry modes, active context, and vertical tile shell without changing evidence semantics.
3. Bind sample fixtures to Tiles 1–6 and the decision package with provenance and status labels.
4. Replace repetitive onboarding replies with the deterministic answer map and chat-to-tile actions.
5. Implement conditional GeoX gap/readiness presentation, keeping execution blocked.
6. Add a separately reviewed readiness-only upload UI only after lifecycle, parsing, mapping, and disclosure contracts are specified.
7. Conduct manual product review and deployment validation before declaring the experience externally demo-ready.

## Acceptance criteria for the next implementation task

1. No internal “Choose a sample journey stage” menu is visible.
2. The frozen hero and welcome message communicate concrete business value.
3. Exactly two primary entry modes are visible.
4. No dataset is active before an explicit entry choice.
5. Active sample context replaces repeated dataset-selection material.
6. All ten narrative tiles have a defined state.
7. Planning is visible and clearly blocked where live optimization is absent.
8. GeoX is conditional on an identified evidence gap.
9. Every tile exposes provenance and a capability label.
10. Chat focuses, explains, or navigates tiles rather than duplicating them.
11. Chat stores and displays business-goal context.
12. Four onboarding answers are substantively distinct.
13. Every answer follows the six-layer contract.
14. Fixture-backed evidence is not described as live analysis.
15. Unsupported decision claims remain blocked.
16. The decision package separates supported, uncertain, blocked, and next.
17. The SaaS planning card is enabled and includes its optimization boundary.
18. Analyze my data is visibly readiness-only.
19. Upload intake contains no model-fitting or recommendation claim.
20. File persistence disclosure is conditional on verified runtime behavior.
21. No live MMM fitting is introduced.
22. No live GeoX execution or recalibration is introduced.
23. No scenario simulation or budget optimization is introduced.
24. No ungoverned LLM provider call is introduced.
25. A new manual review verifies the vertical product story before external-demo claims.

## Design verdict

`GUIDED_WORKSPACE_DESIGN_COMPLETE_IMPLEMENTATION_PLAN_NEXT`

The product decision, state model, vertical journey, answer boundaries, upload contract, implementation order, and acceptance criteria are sufficiently defined for the next planning artifact. The recommended next artifact is `MIP_GUIDED_MEASUREMENT_WORKSPACE_IMPLEMENTATION_PLAN_001`.
