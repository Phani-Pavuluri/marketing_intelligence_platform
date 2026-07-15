# Conversational Control Plane Dialogue Router 001

Phase D adds `src/mip/control_plane/dialogue_router.py`, a deterministic provider-free router operating on `InteractionEvent`, `WorkspaceContext`, `DialogueState`, and `DEFAULT_CAPABILITY_REGISTRY`. `DialogueRouter.route` returns a validated `RoutingResult` containing `IntentEnvelope`, updated dialogue state, slot updates, clarification targets, selected descriptor, and stable routing-rule identity.

Precedence is centralized as typed UI actions, pending clarification resolution, explicit domain rules, active artifact/view context, deterministic language rules, clarification, then unsupported. Typed actions are never reclassified by text. Explicit MMM requirements route to `mmm.intake.requirements`, not MMM-vs-GeoX comparison. MMM readiness extracts only stated spend/channel/geography and reports missing KPI, frequency, and date fields. Date/frequency/KPI follow-ups resolve pending state; corrections replace prior inferred values. GeoX, planning, trust, navigation, greetings, and unsupported routes are covered. Candidate capabilities are registry-validated and selection never executes anything.

Slot extraction is conservative: business goal, KPI, frequency, date range, spend, channel, geography, controls, planning horizon, and experiment timing are represented as detected/inferred updates. No schema inference, artifact resolution, workflow traversal, upload parsing, response generation, RAG, LLM, or engine execution is present.

The Streamlit shell now routes free-form messages through the canonical router and uses a small transitional response adapter. The old keyword/exact-prompt classifier remains only as an unused compatibility import path and can be removed after downstream response-layer migration. Typed UI actions continue through the shared workspace event pipeline. Transcript rendering derives solely from `workspace.visible_messages()`; the bounded transcript container is absent until a real message exists and disappears after reset.

Browser review was unavailable in this agent environment. AppTest and automated/Docker/public checks passed; browser visual verification remains pending user verification.

Next artifact: `MIP_CONVERSATIONAL_CONTROL_PLANE_WORKFLOW_GRAPH_AND_BINDING_001`.
