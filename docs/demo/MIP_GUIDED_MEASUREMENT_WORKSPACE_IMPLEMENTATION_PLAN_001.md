# MIP Guided Measurement Workspace Implementation Plan 001

## Decision and scope

This plan turns the approved guided-workspace design into small, reviewable runtime tasks. It preserves the deterministic SaaS fixture chain and claim gates while replacing the state-menu presentation with a user decision journey:

```text
business goal → data → readiness → MMM evidence → planning
→ evidence gap → GeoX evidence → learning loop → decision package
```

This plan authorizes no runtime change itself. It does not authorize live engines, recommendations, providers, persistence, or additional domains.

**Plan verdict:** `GUIDED_WORKSPACE_IMPLEMENTATION_SEQUENCE_READY`

P1 can begin: the product copy, entry modes, sample fixture chain, deployment contract, and required UI boundary are settled. P4 has an implementation gate for upload lifecycle/disclosure, but that does not block P1–P3.

## Current implementation assessment

| Classification | Evidence and decision |
| --- | --- |
| Reuse unchanged | `src/mip/demo/sample_journey.py` fixture loader, journey IDs/stage ordering, contextual prompts, fixture provenance and claim labels; `data/demo/domain_fixtures/saas_subscriptions` remains authoritative. |
| Extend | `src/mip/demo/product_flow.py` state transitions and deterministic `product_answer`; `src/mip/demo/chat_first_demo.py` presentation models; `app/streamlit_app.py` chat-first tab and AppTest coverage. |
| Reorganize | Move presentation-facing guided-workspace state, tile view models, and answer models out of monolithic `app/streamlit_app.py` into focused demo modules. Preserve stable internal IDs. |
| Replace after migration | The primary “Select a sample dataset” and “Choose a sample journey stage” controls. Retire them only after primary actions, active context, and vertical tiles offer equivalent access. |
| Advanced tools | Existing advisory, readiness, calibration mapping, profiling, and intake tabs remain available under Advanced tools; they are not removed or presented as the primary guided journey. |
| Upload reuse | `src/mip/contracts/uploaded_csv_materialization.py`, `src/mip/workflows/uploaded_csv_materialization.py`, `planning_mmm_uploaded_csv_*.py`, `geox_uploaded_csv_*.py`, intake mapping/readiness modules and their tests. |
| Upload gaps | No public Streamlit upload entry, verified browser-session lifecycle, file limits, multi-file inventory UX, profile/mapping confirmation UX, cleanup proof, or truthful persistence disclosure exists. |

The current entrypoint is `app/streamlit_app.py`; current state modules are `src/mip/demo/product_flow.py`, `chat_first_demo.py`, and `sample_journey.py`. The plan favors new `guided_workspace.py` and `guided_workspace_answers.py` modules to keep UI composition thin. A dedicated upload view-model module is warranted only in P4 after lifecycle decisions are proven.

## Dependency map

```text
existing deterministic SaaS fixtures
              │
              ▼
P1 workspace shell ──► P2 vertical journey ──► P3 answer layer
              │                 │                    │
              └──────────────── browser checkpoint ───┘
                                                    │
                                                    ▼
                                        P4 upload readiness
                                                    │
                                                    ▼
                                      P5 integrated manual review
                                                    │
                                                    ▼
                                      P6 external release audit

MMM_MIP_HANDOFF_V1 → live MMM export ingestion → governed simulation
                   → future recommendation workflow       (deferred)

GeoX/panel_exp governed handoff → live feasibility/design → evidence ingestion
                                                           (deferred)

grounded LLM governance → optional generation after deterministic stabilization
                                                            (deferred)
```

The sequence is P1 → P2 → P3 → browser checkpoint → P4 → P5 → P6. P2 precedes P3 because a tile/navigation contract is the context that makes answers testably relevant; P3 then binds to stable tile IDs. Upload does not begin before the vertical SaaS journey passes a browser checkpoint. Grounded LLM integration is deferred until after P6, and additional domains remain deferred. Live MMM export ingestion and GeoX execution remain blocked by their package-side handoffs and release gates.

## Common implementation contract

### State model

| Field | Initial value / owner | Transition and reset |
| --- | --- | --- |
| `entry_mode` | `None`; shell reducer | Set by primary action; changing mode clears dataset, tile, answer navigation, and incompatible upload state. |
| `business_goal` | `None`; chat/shell reducer | Set from explicit goal capture only; reset clears it. |
| `planning_horizon` | `None`; shell/chat reducer | Optional structured value; dataset/entry changes retain only if still relevant. |
| `active_dataset_id` | `None`; sample or upload reducer | Sample selection sets SaaS ID; upload mode uses no fixture ID. Change clears artifacts/tile completion. |
| `active_use_case_id` | `None`; sample reducer | Set to SaaS growth planning; reset clears. |
| `active_tile_id` | `None`; tile/navigation reducer | Chat navigation validates eligibility before focus/scroll; reset clears. |
| `completed_tile_ids` | empty set; journey reducer | Derived from viewed/acknowledged eligible evidence, never mistaken for live execution; reset clears. |
| `available_artifact_ids` | empty set; fixture resolver | Recomputed on dataset change; never carried across use cases. |
| `uploaded_file_state` | empty; P4 upload reducer | Ephemeral session metadata only; clear/reset deletes state and any managed temporary materialization. |
| `column_mapping_state` | empty; P4 mapping reducer | Valid only for current file inventory fingerprint; any file change invalidates it. |
| `readiness_state` | `not_started`; P4 readiness reducer | Recomputed after confirmed mapping; stale or failed state is fail-closed. |
| `conversation_messages` | empty list; chat reducer | Store role, answer category, context fingerprint, and navigation target; reset clears. |
| `last_answer_category` | `None`; answer reducer | Used for relevant follow-ups, not a claim source. |
| `navigation_target` | `None`; answer reducer | Consumed once by UI then cleared to prevent rerun loops. |
| `execution_mode` | deterministic fixture / readiness-only | Rendered from evidence, never user-editable. |

No persistent storage or serialization is required. Streamlit reruns must reconstruct view models from serializable state plus fixture resolution. Every dataset/entry-mode/file-inventory change invalidates artifact, mapping, readiness, and navigation context that belongs to the prior context.

### Shared validation contract

Every runtime phase must run `git diff --check`, focused pytest, Ruff and mypy on changed files, `make validate`, and `make validate-public-deployment`. The latter two are Docker-backed requirements; no host fallback substitutes for them. Each phase adds unit tests and Streamlit AppTest where applicable, followed by the named browser gate.

## P1 — Guided workspace shell and business-value entry

**Task ID:** `MIP_GUIDED_MEASUREMENT_WORKSPACE_SHELL_001`

**Objective and visible outcome:** Replace the generic landing inside the chat-first tab with the canonical hero, Measure/Plan/Experiment/Learn framing, immediate composer, active-context display, and two primary actions: **Explore a sample use case** and **Analyze my data**. The latter enters a clearly non-live readiness placeholder until P4.

The hero and welcome copy are canonical in `MIP_GUIDED_MEASUREMENT_WORKSPACE_PRODUCT_DESIGN_001.md`. Freeze the four distinct starter responses:

| Question | Required deterministic outcome |
| --- | --- |
| What can MIP help my marketing team do? | Measure/Plan/Experiment/Learn explanation and boundaries. |
| What data would I need to analyze channel performance? | Outcome, spend/channel, time, controls, and optional geography; no upload claim. |
| Should I use MMM, GeoX, or both? | Decision/context distinction and evidence-gap criteria. |
| Show me how MIP supports next-quarter planning. | SaaS decision constraints and explicit blocked optimization/recommendation boundary. |

**Likely files:** `app/streamlit_app.py`, `src/mip/demo/product_flow.py`, `src/mip/demo/chat_first_demo.py`, new `src/mip/demo/guided_workspace.py`, `src/mip/demo/__init__.py`, focused `tests/app/test_streamlit_app.py` and `tests/demo/test_guided_workspace_shell_001.py`.

**Reuse/dependencies:** initial product state, `product_answer`, SaaS fixture loader, widget-key conventions. Depends on this plan only.

**Non-goals:** vertical tiles, actual upload controls/parsing, live models, LLM providers, recommendations.

**Acceptance:** no internal stage language as the primary model; no active dataset by default; actions differ; four answers are distinct and substantive; composer remains visible; Advanced tools remain accessible; no duplicate keys; no dataset-specific claims without explicit sample activation.

**Focused checks:** reducer/answer tests and AppTest for hero, actions, prompts, composer, reset, and Advanced tools. **Browser check:** landing hierarchy, keyboard order, narrow layout. **Commit:** `Build guided measurement workspace shell`. **Next:** P2. **Stop/rollback:** revert to the prior chat-first presentation if fixture selection/claim gating or unique widget keys regress; do not merge if primary actions are ambiguous.

## P2 — Vertical SaaS journey and chat-to-tile navigation

**Task ID:** `MIP_GUIDED_MEASUREMENT_WORKSPACE_VERTICAL_JOURNEY_001`

**Objective and visible outcome:** Present the SaaS growth-planning journey as ten stacked summary cards with one expanded active detail panel. This progressive-expansion pattern is Streamlit-compatible, limits initial page length, keeps the narrative vertical, and avoids ten full artifacts rendering simultaneously.

Tiles are: Define decision; Bring data; Inspect and validate; Build and validate MMM; Understand channel results; Plan next quarter; Close an evidence gap with GeoX; Review GeoX evidence; Recalibrate MMM; Decision package. Each view model includes stable ID, title, eligibility, summary, evidence/provenance, capability label, status (`upcoming/current/completed/blocked/future`), technical disclosure, and safe action.

**Likely files:** `app/streamlit_app.py`, `src/mip/demo/product_flow.py`, `src/mip/demo/sample_journey.py`, new `src/mip/demo/guided_workspace.py`, potentially `src/mip/demo/guided_workspace_tiles.py`, `src/mip/demo/__init__.py`, `tests/demo/test_guided_workspace_vertical_journey_001.py`, `tests/app/test_streamlit_app.py`.

**Reuse/dependencies:** P1 state shell, `ordered_stages`, `contextual_prompts`, available artifact IDs, execution labels. Keep stage IDs internal and map them to user-facing tiles. P2 depends on P1.

**Behavior:** active tile updates from card action or validated chat navigation; UI highlights/focuses it and consumes the navigation target once. GeoX gap is eligible only after stated evidence-gap artifacts; GeoX evidence only after the gap. Planning always appears, marked blocked with missing capability and safe preparation. Reset clears tile and progress state. Technical lineage stays in expanders. On narrow screens cards remain single-column with concise summaries; all controls have labels and keyboard access.

**Non-goals:** change fixture semantics, execute MMM/GeoX/calibration, simulate plans, solve answer quality comprehensively.

**Acceptance:** all ten tiles defined; primary menu removed after migration; one active detail panel; no stale tile after reset/dataset change; planning visibly blocked; GeoX timing conditional; accessible labels; fixture-backed facts visibly labeled.

**Focused checks:** tile eligibility/state transitions, fixture resolution, navigation target consumption, AppTest card expansion/navigation/reset/no duplicate keys. **Browser checkpoint:** sample activation, scroll/highlight behavior, tile density, desktop and narrow layouts; P4 cannot start until it passes. **Commit:** `Add guided vertical SaaS journey`. **Next:** P3. **Stop/rollback:** do not remove the old control until cards reach all previously available fixtures; stop if a fixture resolves to an unsupported claim.

## P3 — Rich deterministic answer layer

**Task ID:** `MIP_GUIDED_MEASUREMENT_WORKSPACE_ANSWER_LAYER_001`

**Objective and visible outcome:** Make chat a context-aware controller of the workspace with substantive, differentiated, claim-safe answers and tile navigation.

The answer view model contains `direct_answer`, `relevant_context`, `evidence_summary`, `important_limitation`, `next_action`, `contextual_follow_ups`, `technical_details`, `claim_status`, and `navigation_target`.

Intent taxonomy: platform capability, data requirements, method choice, trust/governance, planning, sample structure, MMM readiness, MMM result explanation, Meta uncertainty, GeoX need, calibration, planning blocker, current decision package, unsupported question, and dataset-required question. Required context is the state fingerprint plus eligible fixture artifacts. Answers retrieve only approved fixture/readiness evidence and invoke existing claim gates before display. Technical details remain collapsible.

**Likely files:** `src/mip/demo/product_flow.py`, `src/mip/demo/chat_first_demo.py`, new `src/mip/demo/guided_workspace_answers.py`, `src/mip/demo/guided_workspace.py`, `app/streamlit_app.py`, `src/mip/demo/__init__.py`, `tests/demo/test_guided_workspace_answers_001.py`, `tests/app/test_streamlit_app.py`.

**Dependencies:** P2 tile IDs and view-model eligibility. **Non-goals:** provider calls, prompt execution, RAG, live results.

**Acceptance:** each required category receives a distinct relevant answer; unsupported questions fail closed; dataset-required questions request explicit context; answer navigation targets only eligible tiles; no forbidden recommendation, ROI, lift, or “optimal” claim escapes; follow-ups vary by answer category.

**Future seam (not implemented):** `question → context resolution → deterministic evidence package → claim eligibility → optional grounded generation → verifier`. Provider integration is deferred until after P6 and requires separate governance approval.

**Focused checks:** intent classification, answer snapshot differentiation, evidence/claim gates, navigation, stale context, and AppTest prompt/chat paths. **Browser check:** perceived differentiation and technical-detail readability. **Commit:** `Add guided workspace deterministic answers`. **Next:** browser checkpoint then P4. **Stop/rollback:** preserve current fallback if any response cannot identify an evidence source or passes a blocked claim.

## P4 — Readiness-only uploaded-data workspace

**Task ID:** `MIP_GUIDED_MEASUREMENT_WORKSPACE_UPLOAD_READINESS_001`

**Objective and visible outcome:** Turn **Analyze my data** into the smallest safe multi-file intake for channel spend CSV, KPI outcomes CSV, controls CSV, and optional experiment-evidence CSV. It supports explanation, structural profiling, mapping, compatibility, MMM/GeoX intake readiness, and next-step guidance only.

**Reusable paths:** `src/mip/contracts/uploaded_csv_materialization.py`, `src/mip/workflows/uploaded_csv_materialization.py`; `src/mip/contracts/planning_mmm_uploaded_csv_adapter.py`, `planning_mmm_uploaded_csv_input_plan.py`, `planning_mmm_uploaded_csv_workflow_readiness.py` and matching workflows; `geox_uploaded_csv_adapter.py`, `geox_uploaded_csv_runtime_bridge.py`; `src/mip/contracts/intake_mapping.py`, `intake_sources.py`, `workflow_readiness.py`, and `src/mip/workflows/readiness/{profile,checks,report}.py`.

**Prerequisite decision inside P4:** establish the actual file-lifecycle design before exposing upload. It must set accepted MIME/CSV encoding, per-file and aggregate limits, temporary materialization location, session cleanup, error handling, and browser-verified persistence disclosure. If that cannot be proven, create a lifecycle prerequisite artifact and stop; do not display “not persisted.”

**Likely files:** new `src/mip/demo/guided_workspace_upload.py` only if UI view models cannot remain in `guided_workspace.py`; `app/streamlit_app.py`; narrowly necessary demo glue; focused tests under `tests/demo/` and `tests/app/`. Do not duplicate or weaken contracts.

**Flow:** inventory files → fail-closed materialization → schema profile → candidate role mapping → explicit confirmation → date/geo/KPI/spend/control detection → grain/missingness/duplicates checks → readiness report and safe next action. File changes invalidate mapping/readiness; reset clears session data and managed temporary materialization. Unsupported formats, malformed CSV, missing mandatory roles, incompatible grains, and unclear lifecycle fail closed.

**Blocked:** live MMM fitting/ROI/contribution, live GeoX design/assignment, calibration, simulation, recommendations. **Focused checks:** materialization boundary, limits, inventory fingerprint, profile/mapping confirmation, compatibility blockers, cleanup, AppTest upload entry when supported. **Browser check:** privacy text, error recovery, upload reset, narrow layout. **Commit:** `Add guided upload readiness workspace`. **Next:** P5. **Stop/rollback:** no merge if persistence disclosure, cleanup, or raw-data scope is unverified.

## P5 — Integrated browser review and UX remediation

**Artifact:** `MIP_GUIDED_MEASUREMENT_WORKSPACE_MANUAL_REVIEW_RESULT_001`

Run local and hosted review with screenshots of landing, selected sample, data, MMM results, planning, GeoX, calibration, upload intake, and narrow layout. Checklist: hero value, welcome quality, distinct starter answers, both entry modes, business-goal capture, vertical narrative, chat navigation, reset, labels, planning blocker, GeoX timing, calibration explanation, technical disclosures, responsive layout, local/hosted behavior, and runtime errors.

Pass requires all screenshots, no duplicate keys/errors, coherent vertical story, honest fixture/readiness labels, and verified upload lifecycle wording. Fail records exact defects and routes a narrowly scoped remediation task. **Commit:** `Record guided workspace manual review`. **Next:** P6. **Stop:** hosted verification unavailable means no external-ready claim.

## P6 — External demo release-readiness audit

**Artifact:** `MIP_GUIDED_MEASUREMENT_WORKSPACE_RELEASE_READINESS_AUDIT_001`

Require local and hosted browser passes, canonical Docker validation, public deployment regression, no provider requirement, claim safety, fixture labels, upload safety, accurate persistence disclosure, no live-model implication, and no production recommendation implication. Valid verdicts are `INTERNAL_GUIDED_DEMO_READY`, `EXTERNAL_GUIDED_DEMO_READY`, `EXTERNAL_RELEASE_BLOCKED`, and `PRODUCTION_CLAIMS_NOT_AUTHORIZED`.

**Commit:** `Audit guided measurement workspace release readiness`. **Stop:** any missed browser gate, Docker failure, deployment regression, or claim/persistence defect yields a blocking verdict; no unrelated runtime fix is bundled.

## File-impact and test plan

| Phase | Runtime boundaries | Focused tests | Required browser gate |
| --- | --- | --- | --- |
| P1 | app shell, product flow, demo view models | state/actions, four distinct prompts, AppTest hero/actions | landing and narrow layout |
| P2 | guided tile view models, fixture mapping, app rendering | eligibility, active tile, reset, AppTest cards/navigation | sample journey/scroll |
| P3 | answer models/templates, product flow, app chat | intent/claim/differentiation/navigation | answer quality/details |
| P4 | upload view model plus existing adapters/workflows | profiling/mapping/readiness/cleanup | upload/privacy/errors |
| P5 | documentation only | screenshot/checklist evidence | full local + hosted review |
| P6 | documentation only | release/deployment/governance evidence | external-ready gates |

All P1–P4 commits must preserve `requirements.txt` line 3 as `-e .`, keep `app/streamlit_app.py` a thin renderer, and avoid modifications outside phase scope.

## Stop/go gates

**Global stop:** prerequisite artifact missing; main diverged from origin; changes beyond scoped files; Docker unavailable; fixture-chain inconsistency; duplicate widget key; dataset-specific claim without active context; recommendation escaping claim gates; a runtime path requiring unapproved engine behavior.

**P1 go:** deterministic no-dataset behavior and four differentiated answers pass focused tests/AppTest.

**P2 go:** all tiles resolve only approved artifacts; old selection controls have a migration path; browser checkpoint passes.

**P3 go:** answer snapshots demonstrate relevance/difference and verification blocks unsafe language.

**P4 go:** actual upload lifecycle, cleanup, limits, and disclosure are verified; otherwise stop and create the prerequisite task.

**P5 go:** local and hosted screenshots/checklist pass; otherwise record failure and remediate only the identified defect.

**P6 go:** Docker/deployment/browser/claim/upload gates pass. External readiness is not production authorization.

## Recommended next artifact

`MIP_GUIDED_MEASUREMENT_WORKSPACE_SHELL_001`
