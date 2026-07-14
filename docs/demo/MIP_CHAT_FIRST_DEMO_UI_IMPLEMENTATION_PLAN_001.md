# MIP Chat-First Demo UI Implementation Plan 001

**Artifact ID:** `MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001`  
**Type:** implementation plan / governance artifact only  
**Status:** plan complete; UI implementation deferred  
**Recommended implementation:** `MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_001`

## Purpose and scope

This artifact defines the future implementation plan for the chat-first demo UI. It does not implement UI code or app behavior.

It bridges `MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001` and a later, separately reviewed Streamlit/app implementation task. It turns the approved interaction design into discovery steps, candidate file categories, staged work, tests, and rollback controls without changing the current deterministic public demo.

## Preconditions

The future implementation may start only after confirming these artifacts remain present and consistent:

- `MIP_DEMO_DOMAIN_DATASETS_001`;
- `MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001`;
- `MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001`; and
- `MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001`.

Required commits in `main` history:

- `1662b92` — demo domain datasets;
- `0430e07` — MMM LLM response verifier audit;
- `fccb2fe` — demo onboarding guide; and
- `5616ac9` — chat-first demo UI design plan.

The fixture must remain available at `data/demo/domain_fixtures/saas_subscriptions/v1/`, and its JSON files must parse before UI work begins.

## App/file discovery plan

The implementation task must inspect the repository before choosing files. Run at minimum:

```bash
find app -maxdepth 4 -type f | sort
find src/mip -maxdepth 4 -type f | sort
rg "Streamlit|streamlit|st\.chat|demo|fixture|MMMResponseTemplateOutput" app src/mip tests
```

The inspection must:

- identify the current canonical Streamlit/app entrypoint;
- identify the existing demo UI shape and app routes;
- identify app, renderer, fixture, import, and smoke tests;
- search for existing response-template rendering code;
- search for existing fixture/demo loading utilities; and
- confirm that no provider-execution path is invoked by the proposed route.

Current inspection finds `app/streamlit_app.py` documented as the canonical deterministic entrypoint. `src/mip/app/streamlit_app.py` is a separate legacy compatibility shell that uses `MockLLMProvider`; it must not be assumed to be the target. The future task must re-confirm this state rather than treating these paths as permanent.

## Future files likely to be touched

These are candidate categories and paths, not edits authorized by this plan:

| Category | Candidate discovered now | Intended responsibility |
|---|---|---|
| Streamlit/demo entrypoint | `app/streamlit_app.py` | Isolated chat-first demo section or route, preserving existing tabs and safety banner. |
| Demo fixture loader/helper | `app/demo_fixtures.py` or a new focused helper under `app/` | Read and validate fixture metadata without engine/provider calls. |
| Readiness/evidence/guardrail renderers | `app/ui_renderers.py` or focused modules under `app/` | Convert deterministic fixture behavior into display-safe structures. |
| Canonical entrypoint regression | `tests/app/test_streamlit_entrypoint.py` | Confirm canonical/legacy separation and import safety. |
| App behavior and renderer tests | `tests/app/test_streamlit_app.py`, `tests/app/test_ui_renderers.py` | Test shell helpers, cards, panels, and blocked claims. |
| Fixture helper tests | `tests/app/test_demo_fixtures.py` or a new focused test | Test JSON loading, question lookup, and deterministic answer mapping. |
| Documentation | `README.md`, demo docs, roadmap | Explain the new isolated demo route and deterministic boundary. |

Likely helper responsibilities include readiness cards, blocked claims, evidence inspected, next required artifacts, and lifecycle walkthrough rendering. Exact module boundaries must follow the existing app style discovered at implementation time. Production contracts under `src/mip/` should not be changed merely to support presentation.

## Staged implementation sequence

### Phase 0 — app inspection only

- Re-run app and source discovery.
- Confirm the canonical Streamlit/app entrypoint and existing demo layout.
- Inventory app, fixture, renderer, import, deployment, and smoke tests.
- Identify any existing response-template display adapter.
- Trace imports to confirm the new route cannot invoke a live provider, prompt execution, MMM/GeoX runtime, optimizer, or legacy `MockLLMProvider` path.
- Record the final proposed file list before editing.

### Phase 1 — static demo fixture loading

- Load and validate `manifest.json`.
- Load and validate `sample_questions.json`.
- Load and validate `expected_answer_behavior.json`.
- Load and validate `lifecycle_walkthrough.json`.
- Optionally read CSV headers or bounded metadata when a panel label needs them; do not perform analysis or derive results.
- Build deterministic lookups by `question_id`, category, and lifecycle step.
- Reject missing, malformed, or mismatched fixture records with a safe UI error.
- Do not fit a model or call an LLM provider.

### Phase 2 — chat-first shell

- Add the “Marketing Intelligence Platform” header and “MMM + GeoX readiness copilot” subtitle within the isolated experience.
- Add the Start here demo entry.
- Render sample question chips from the fixture catalog.
- Keep selected question/history in local, static session state.
- Render the selected answer deterministically from `expected_answer_behavior.json` and related fixture metadata.
- Label the answer as readiness, explanation, refusal, or defer; do not imply it is provider-generated.

### Phase 3 — readiness and guardrail panels

- Render readiness cards with status, evidence, allowed summary, cannot-say, and next artifact.
- Render the EvidenceInspectedPanel from fixture references and provenance.
- Render CannotSayPanel and BlockedClaimsPanel prominently.
- Render NextRequiredArtifactPanel for blocked/deferred requests.
- Render LifecycleWalkthroughPanel with available, fixture-backed, blocked, future, and next-artifact state.
- Render human-review indicators and FutureIntegrationBadges without relying on color alone.

### Phase 4 — regression tests

- Add fixture JSON loading and cross-reference tests.
- Add pure UI-helper tests when helpers exist.
- Add no-provider/no-runtime import and safety tests.
- Verify all required blocked claims render for guarded questions.
- Verify normal answers cannot erase cannot-say text.
- Add an app import/smoke test if feasible without starting a server.
- Preserve existing public-demo deployment and canonical-entrypoint tests.

### Phase 5 — manual demo checklist

- Select the SaaS subscriptions demo.
- Ask an MMM readiness question and inspect evidence.
- Ask a GeoX readiness question and confirm readiness-only language.
- Ask a grain compatibility question and confirm the two grains and normalization rule.
- Ask for a budget recommendation and confirm refusal plus next artifact.
- Confirm ROI, contribution, recommendation, assignment, lift, readout, and causal claims remain visibly blocked.
- Confirm keyboard navigation, focus order, readable labels, narrow-screen behavior, and non-color status cues.

## Deterministic demo answer rule

The future implementation must render answers from governed fixture metadata and expected behavior, not from an LLM provider.

Allowed sources:

- `sample_questions.json`;
- `expected_answer_behavior.json`;
- `lifecycle_walkthrough.json`;
- `manifest.json`; and
- existing MIP response-template metadata, but only if it is already safely available without executing prompts or providers.

Blocked sources and actions:

- live LLM provider;
- runtime prompt execution;
- MMM fitting;
- GeoX estimator execution;
- optimizer/simulator execution; and
- generated or inferred ROI, ROAS, contribution, lift, assignment, or recommendation values.

The selected question must resolve to a known fixture behavior. Unknown free text should be safely unsupported or routed to documented sample choices; it must not trigger improvised model output.

## UI components to implement later

Conceptual components are:

- `StartHerePanel`;
- `SampleQuestionChips`;
- `ChatMessagePanel`;
- `ReadinessCards`;
- `EvidenceInspectedPanel`;
- `CannotSayPanel`;
- `BlockedClaimsPanel`;
- `NextRequiredArtifactPanel`;
- `LifecycleWalkthroughPanel`; and
- `FutureIntegrationBadges`.

These names are descriptive, not required class or function names. The implementation should use pure display-data helpers where possible and keep Streamlit calls thin.

## Claim-safety requirements

The future UI must surface, not hide, these blocked claims:

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

`cannot_say` dominates overlapping `can_say`. A readiness status must never be presented as model fit, causal validation, assignment approval, or recommendation readiness. Refusals must show the allowed bounded explanation, inspected evidence, blocked reason, and next required artifact.

## Next-required-artifact mapping

| Blocked intent | UI dependency message |
|---|---|
| ROI / ROAS | Requires `MMMExportBundle` and a governed ROI artifact. |
| Channel contribution | Requires a governed contribution artifact through the MMM export path. |
| Budget recommendation / optimized spend | Requires `MMMRecommendationContract` or MIP `RecommendationContract` plus governed optimizer evidence. |
| GeoX assignment | Requires a governed GeoX design artifact. |
| GeoX lift/readout | Requires a governed GeoX readout artifact. |
| Live LLM narrative | Requires a provider-execution boundary plus verifier; this deterministic route must remain separate. |

Missing dependencies are informational. The UI must not fabricate them, imply they are merely disabled, or offer execution controls.

## Validation plan for future implementation

At minimum, the later implementation must run:

- fixture loading and cross-reference tests;
- `tests/demo/test_mip_demo_domain_datasets_001.py`;
- `tests/governance/test_mmm_llm_response_verifier_audit_001.py`;
- `tests/governance/test_demo_onboarding_and_use_case_guide_001.py`;
- `tests/governance/test_chat_first_demo_ui_design_plan_001.py`;
- implementation-plan governance regression;
- relevant `tests/app/` helper, entrypoint, and import/smoke tests;
- the full test suite;
- targeted Ruff and mypy on changed Python files;
- global mypy;
- full-repo Ruff, reporting unrelated debt without expanding scope; and
- a safety grep for provider/runtime calls and overclaiming language in the changed route.

The safety grep should look for provider calls, prompt execution, engine/model execution, optimizer/simulator wiring, ROI/ROAS/contribution/lift calculations, and hidden treatment assignment. Manual verification must confirm each blocked question exposes its refusal and dependency.

## Rollback and safety plan

- Keep the new demo experience behind a feature flag, dedicated demo route, or isolated section if the app structure permits.
- Avoid replacing or reordering existing production/public-demo behavior in the first slice.
- Keep fixture loading and deterministic rendering in focused helpers with narrow imports.
- Do not wire provider execution or prompt assembly.
- Do not wire MMM, GeoX, optimizer, simulator, or recommendation runtime execution.
- Keep deterministic fixture-backed rendering separate from future live integrations.
- Make the change revertible by removing the isolated route/helper imports without requiring contract or data migrations.
- If safety or deployment regressions appear, disable the isolated entry and retain the existing deterministic app unchanged.

## Future integration placeholders

Document, but do not activate, placeholders for:

- MMM export adapter;
- MMM ROI/contribution artifact rendering;
- MMM optimizer / `RecommendationContract` rendering;
- GeoX design artifact rendering;
- GeoX readout artifact rendering;
- provider-backed LLM execution;
- uploaded-data workflow; and
- production `TrustReport` / `DecisionSurface` integration.

Every placeholder must be labeled “future integration,” contain no generated result, and require a separate reviewed artifact before activation.

## Non-goals

All of the following are false / not implemented by this artifact:

- no UI code;
- no Streamlit behavior change;
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

`MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_001`

This is the first actual UI implementation artifact and should begin only after this plan is reviewed and its Phase 0 file list and safety boundary are reconfirmed.
