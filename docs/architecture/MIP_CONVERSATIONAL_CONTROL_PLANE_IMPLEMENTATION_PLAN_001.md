# MIP Conversational Control Plane Implementation Plan 001

## Purpose and boundaries

This plan turns the approved architecture and normative Phase A–L registry into independently reviewable runtime tasks. It is documentation-only: no runtime code, fixtures, dependencies, deployment configuration, MMM, GeoX, calibration, simulation, optimization, or recommendations are implemented here.

## Sequencing decision

Phase A is the only start gate. After A, B and C may proceed in parallel because the registry contracts and workspace event model have separate boundaries. D requires both B and C. E may begin after B and the workflow-node contract exists, but its integration join is after D. F requires B and E. H is deliberately before G because upload readiness must consume deterministic evidence packets. G then depends on C, D, F, and H. I depends on B, F, and H; J depends on D, F, H, I, and verifier evaluation; K depends on stable workspace state and artifact context; L closes every path.

Critical path: A → (B + C) → D → E → F → H → G → I → J → K → L. E has a bounded parallel start after B; all downstream joins are explicit. The vertical journey remains dependency-gated until E, F, and H. Additional sample domains remain deferred through L. Live MMM and GeoX integrations remain separate.

## Runtime task sequence

Each task is one independently reviewable commit.

1. **MIP_CONVERSATIONAL_CONTROL_PLANE_TYPED_CONTRACTS_001 (A)** — Define versioned, serializable InteractionEvent, IntentEnvelope, WorkspaceContext, DialogueState, RequirementGap, CapabilityDescriptor, WorkflowNode, ResolvedArtifact, EvidencePacket, ResponseContract, and VerificationResult. Reuse or compose existing canonical contracts; add fail-closed validation, compatibility rules, builders, and contract tests. No routing or execution. Commit: `Define conversational control plane typed contracts`.
2. **MIP_CONVERSATIONAL_CONTROL_PLANE_CAPABILITY_REGISTRY_001 (B)** — Add validated descriptors, status/execution modes, inventory for the required platform/MMM/GeoX/calibration/artifact/dashboard capabilities, schema links, discovery, and drift detection. Registration never authorizes execution. Commit: `Add conversational capability registry`.
3. **MIP_CONVERSATIONAL_CONTROL_PLANE_WORKSPACE_EVENTS_001 (C)** — Extend the initial in-memory Streamlit workspace with one conversation identity, append-only typed events, derived state, reducers, view/artifact context, mode changes, rolling-summary seam, reset, and stale-context protection. No authenticated persistence. Commit: `Add conversational workspace event state`.
4. **MIP_CONVERSATIONAL_CONTROL_PLANE_DETERMINISTIC_ROUTER_001 (D)** — Implement provider-free precedence, domain/view/artifact context, pending clarification resolution, slots, corrections, ambiguity, confidence, unsupported behavior, and fixtures for the required example prompts. Commit: `Add deterministic conversational router`.
5. **MIP_CONVERSATIONAL_CONTROL_PLANE_WORKFLOW_GRAPH_001 (E)** — Bind governed capabilities to the eleven named journey nodes, define transitions/prerequisites/blocked transitions, active-node state, sample/upload/live providers, and chat navigation. No LLM-created edges. Commit: `Bind conversational workflow graph`.
6. **MIP_CONVERSATIONAL_CONTROL_PLANE_ARTIFACT_RESOLVER_001 (F)** — Resolve fixture, uploaded-session, and future engine artifacts with identity, lineage, execution mode, scope, freshness, compatibility, conflicts, gaps, and claim eligibility. Responses consume resolved artifacts only. Commit: `Add conversational artifact resolver`.
7. **MIP_CONVERSATIONAL_CONTROL_PLANE_GROUNDED_RESPONSES_001 (H)** — Consume EvidencePacket and build deterministic intent responses with known/missing inputs, clarifications, next actions, technical disclosure, verifier, rewrite/block behavior, and safe provider-free fallback. Commit: `Add deterministic grounded responses`.
8. **MIP_CONVERSATIONAL_CONTROL_PLANE_UPLOAD_READINESS_001 (G)** — Implement common-control-plane upload → profile → map → clarify → validate → readiness for supported CSVs, limits, materialization, profiling, mapping, compatibility, missingness, duplicates, history, variation, MMM/GeoX readiness, privacy, cleanup, and reset. Live execution remains blocked. Commit: `Add uploaded data readiness workflow`.
9. **MIP_CONVERSATIONAL_CONTROL_PLANE_GOVERNED_RETRIEVAL_001 (I)** — Add approved corpus metadata, indexing/versioning, effective-date and deprecation filtering, capability/artifact scopes, empty/conflict behavior, citations, and retrieval evaluations. RAG cannot supply executable requirements. Commit: `Add governed conversational retrieval`.
10. **MIP_CONVERSATIONAL_CONTROL_PLANE_CONSTRAINED_LLM_001 (J)** — Add structured interpretation, registry validation, prompt/model/provider identity, timeouts/failure fallback, grounded response input, verification, and separate routing/slot/clarification/groundedness/safety/continuity datasets. No engine execution. Commit: `Add constrained conversational LLM boundary`.
11. **MIP_CONVERSATIONAL_CONTROL_PLANE_MULTI_VIEW_CONTINUITY_001 (K)** — Extend shared workspace identity across dashboards/reports/readiness, active view/artifact/chart/filter/navigation events, browser back/forward, narrow layout, docked chat, and future multi-tab seam without reset. Commit: `Add multi-view conversation continuity`.
12. **MIP_CONVERSATIONAL_CONTROL_PLANE_EVALUATION_RELEASE_001 (L)** — Define thresholds, fixtures, regression and adversarial suites, browser/local/hosted review, Docker/public-deployment regression, failure triage, release verdicts, rollback evidence, and gates for route/slots/clarifications/capabilities/transitions/artifacts/claims/safety/continuity/execution labels/recommendations. Commit: `Define conversational control plane release gates`.

## Browser and evaluation checkpoints

Browser review is mandatory (never replaced by AppTest) after C, D, E, H, G, K, and L: local and hosted review covers persistent conversation, navigation, vertical journey binding, grounded answers, upload readiness, multi-view continuity, narrow layout, back/forward behavior, and release acceptance. Evaluation checkpoints occur after D (routing/slots), E (transitions), F (artifact selection), H (groundedness/claim safety), G (sample/upload separation), I (retrieval), J (LLM safety/continuity), and L (full release gate).

## Migration plan

- Current shell intent router: wrap, then replace route selection after D; preserve fallback fixtures.
- Conversation state: extend into C reducers and event history; deprecate isolated widget state only after parity tests.
- Bounded transcript: reuse as a projection/rolling-summary seam; do not discard history.
- Sample activation: reuse and emit typed events; move capability selection to B/D.
- Fixture journey: wrap as E workflow nodes and retain fixtures.
- Starter answers: deprecate generic FAQ fallback after H; route through EvidencePacket.
- Uploaded-CSV adapters: reuse and wrap under G readiness; no fitting.
- Advanced tools: move_to_advanced behind explicit capability descriptors and blocked claims.

## Dependency gates and roadmap reconciliation

The vertical journey is retained but dependency-gated until E, F, and H. The answer layer is superseded by H's deterministic response task. Upload readiness is retained but superseded by G and gated by C/D/F/H. Governed retrieval, constrained LLM, and dashboards remain blocked by their listed joins. Additional domains remain deferred through L; live MMM and GeoX execution stay separate. The roadmap now points to these tasks rather than disconnected implementations.

## Phase completeness and authorization

The companion registry is normative and satisfies the existing PhaseDefinition contract for every task/phase. Its dependency graph is acyclic, all required fields are explicit, and the governance test rejects missing fields, unknown status, and incompatible positive verdicts. No implementation task is authorized until its predecessor exit criteria and browser/evaluation evidence are recorded.

## Plan verdict

`CONVERSATIONAL_CONTROL_PLANE_IMPLEMENTATION_SEQUENCE_READY`

Recommended next artifact: `MIP_CONVERSATIONAL_TURN_MODE_AND_LLM_HANDOFF_CONTRACTS_001`.

## LLM-first sequencing remediation

The prior plan's deterministic router is reclassified as a typed-action handler, hard-boundary detector, action-proposal validator, and provider-failure fallback. Free-form explanatory conversation is owned by the future LLM front door.

The amended sequence is A, B, C, D, E (complete), then CF1 → CF2 (parallel start permitted) → CF3 → CF4 → CF5. Phase F artifact resolution remains paused until CF5. Then H, G, later artifact-grounded LLM interpretation/action orchestration, K, and L proceed under their existing gates. Additional domains and live MMM/GeoX remain deferred.

CF1 is the immediate next artifact. CF1 defines interaction modes, TurnDecision, GovernedActionProposal, grounding and claim policies, provider disclosure, and fallback semantics without provider execution. CF2 may overlap CF1 because it assembles structured truth and approved user-facing corpus metadata. CF3 requires CF1 and CF2. CF4 requires CF1–CF3. CF5 gates Phase F. Governed action handoff may interpret and clarify before Phase F, but artifact interpretation and execution remain blocked. Broad read-only concepts such as knowledge.explain, knowledge.compare, platform.guide, workflow.guide, and artifact.explain are future registry considerations, not vocabulary-per-phrase capabilities.

Required regression corpus includes `test`, `whats MMM`, `whats GeoX`, `what data is needed`, `how can you help`, `measurement`, elliptical follow-ups, and governed action requests. Exact wording is not a release requirement; helpfulness, naturalness, factuality, grounding, safety, and fallback behavior are.
