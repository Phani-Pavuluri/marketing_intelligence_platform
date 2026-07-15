# MIP Conversational Capability Routing and Grounded Response Architecture 001

## Status and non-negotiable rules

This architecture defines the control plane for one persistent conversational workspace. It is documentation-only: no router runtime, retrieval index, LLM call, upload behavior, engine execution, fixture, or UI is implemented here.

> MIP maintains one persistent conversational workspace per user session. User messages, button clicks, links, uploads, mapping confirmations, workflow transitions, engine calls, dashboards, reports, and artifact views all enter the same interaction control plane. Navigation may change the active view, capability, or artifact, but must not implicitly reset or replace the conversation, router, retrieval pipeline, or governed session context.

> Chat is the persistent interaction layer across the platform. It is not a separate landing-page feature or one tile inside the workflow.

The canonical pipeline is:

```text
persistent workspace → interaction interpretation → capability routing
→ requirement/artifact resolution → optional governed retrieval
→ deterministic execution → evidence packet → grounded response
→ claim verification → same-session state and view update
```

**Verdict:** `CONVERSATIONAL_CONTROL_PLANE_ARCHITECTURE_COMPLETE_IMPLEMENTATION_PLAN_NEXT`

The next artifact is `MIP_CONVERSATIONAL_CONTROL_PLANE_IMPLEMENTATION_PLAN_001`.

## Current-state assessment and reuse

The current shell router in `src/mip/demo/guided_workspace_intents.py` normalizes text and applies ordered keyword rules for greetings, data, MMM/GeoX, planning, trust, sample, upload guidance, dataset context, ambiguity, and unsupported questions. It returns shell-level deterministic answers. It does not retain pending clarification slots, extract structured inputs, resolve capabilities, or produce evidence packets.

Current conversation state is an in-memory `product_flow` dictionary in Streamlit session state. It retains messages, active dataset/use case/stage, artifacts, and execution mode; it does not have a typed event log, workspace identity, pending clarification, slot provenance, rolling summary, or view/artifact continuity contract. Reset is explicit, but navigation and future views need a shared state owner.

The SaaS journey loader in `src/mip/demo/sample_journey.py` and deterministic fixtures remain authoritative for sample mode. Uploaded-session reuse should build on `src/mip/contracts/uploaded_csv_materialization.py`, `src/mip/workflows/uploaded_csv_materialization.py`, planning MMM uploaded-CSV contracts/workflows, GeoX uploaded-CSV adapters/bridges, intake mapping, and readiness reports. Existing evidence, trust, calibration, decision-surface, recommendation, and workflow-readiness contracts remain sources of truth.

The architecture supersedes answer-category-only routing conceptually, but does not delete the shell router: it becomes the deterministic fallback adapter behind the capability control plane.

## Three-layer architecture

### Interaction intelligence

Interprets text and typed UI events, extracts entities and available inputs, tracks pending clarification, maintains business/workflow context, and proposes the next clarification or action. It cannot authorize engines, claims, artifacts, or recommendations.

### Domain control plane

Validates proposed routes against a capability registry, resolves requirements and artifacts, enforces workflow prerequisites, invokes only allowed deterministic capabilities, constructs evidence packets, and applies execution and claim boundaries. This is authoritative.

### Language and explanation

Explains evidence, asks concise questions, compares artifacts, summarizes, and guides navigation. It may use an LLM only after deterministic grounding and verification. It cannot bypass the registry, requirement gaps, workflow graph, artifact resolver, or claim verifier.

## Unified interaction pipeline

All text, buttons, links, uploads, mapping confirmations, dashboard filters, report opens, and workflow actions follow the same sequence:

1. Receive a typed interaction event.
2. Load the workspace’s derived state, recent messages, summary, and active view/artifact.
3. Interpret intent, entities, slots, and requested action.
4. Apply precedence: explicit event/action, explicit domain/action, pending clarification, active context, deterministic interpretation, constrained LLM interpretation, clarification, unsupported response.
5. Validate the candidate capability against the registry.
6. Resolve required inputs, confirmed/inferred inputs, artifacts, and workflow prerequisites.
7. Produce a `RequirementGap` and either ask, block, or execute.
8. Invoke the allowed deterministic capability when ready.
9. Assemble an evidence packet.
10. Retrieve approved explanatory material with capability filters when useful.
11. Generate a deterministic or constrained grounded response.
12. Verify claims, sources, execution labels, and disclosures.
13. Append events and response to the same event log and recent transcript.
14. Update derived state, active capability/view/artifact, and available next actions.

No event path may bypass steps 5–12.

## Typed interaction events

Every interaction uses an envelope with:

`event_id`, `session_id`, `conversation_id`, `workspace_id`, `event_type`, `timestamp`, `source_view`, `source_component`, `requested_action`, `payload`, `active_artifact_id`, `correlation_id`, and `causation_id`.

Event types include `user_message`, `starter_prompt_selected`, `sample_use_case_selected`, `analyze_my_data_selected`, `file_uploaded`, `column_mapping_confirmed`, `business_goal_confirmed`, `workflow_action_selected`, `artifact_opened`, `dashboard_filter_changed`, `report_opened`, `capability_execution_requested`, `reset_requested`, `assistant_response`, and `system_result`.

A button or link is an event with an action and payload, not a direct navigation shortcut. Upload and mapping events carry file inventory fingerprints and mapping versions; chart events carry selected artifact/channel/filter context.

## Persistent workspace state

The typed state has:

```text
session_id, conversation_id, workspace_id
entry_mode, business_goal, planning_horizon
active_domain, active_capability, active_view, active_artifact_id
active_dataset_id, active_use_case_id, active_workflow_node
known_inputs, missing_inputs, confirmed_inputs, inferred_inputs
confirmed_column_mappings
uploaded_file_inventory, session_artifacts, available_artifact_ids
pending_intent, pending_clarification, clarification_history
completed_workflow_nodes, available_workflow_nodes, blocked_workflow_nodes
blocked_actions, conversation_summary, recent_messages, event_log_reference
execution_mode, claim_state
```

Initial state has generated identities, no entry mode, dataset, capability, artifact, workflow node, inputs, files, pending clarification, or completed nodes; empty recent messages and a deterministic execution mode.

Mutation ownership is explicit: interaction interpretation owns pending intent/slots; requirement resolution owns gaps; artifact resolution owns available artifacts; workflow control owns nodes/actions; view navigation owns active view/artifact; conversation service owns messages/summary/event references; verifier owns claim state.

Reset is an explicit typed event that clears conversation, pending dialogue, active capability/view/artifact, sample/upload context, derived inputs, and workflow progress. Switching sample/upload/live provider clears incompatible artifacts and inferred slots but preserves the workspace identity and records the transition. Navigation, dashboard filters, report opens, and artifact views preserve conversation, goal, inputs, mappings, files, artifacts, completed nodes, and pending clarifications. User corrections replace inferred values with confirmed values and invalidate dependent readiness/artifacts. Future tabs use the same workspace/conversation identity and optimistic version; conflicts become events, not silent resets.

## Event log and derived state

The append-only event log is the complete session history: messages, clicks, uploads, mappings, confirmations, capability requests, executions, artifacts, page changes, and assistant/system responses.

Derived state is a compact projection consumed by routing and execution. It includes the current slots, active context, requirement gap, workflow nodes, recent message window, rolling summary, and event-log reference. The router does not reread the full log each turn. The user-visible transcript remains complete; a future model context may use summary plus recent messages.

## Intent and dialogue model

The intent envelope is:

```text
domain, user_goal, intent, requested_action, candidate_capability
entities, known_inputs, missing_or_unknown_inputs
confidence, clarification_required, clarification_targets
```

The architecture routes `what data is needed to build an MMM model` directly to `mmm.intake.requirements`, never to MMM-versus-GeoX ambiguity. Precedence is:

1. explicit UI action;
2. explicit domain and action;
3. pending clarification resolution;
4. active capability and artifact context;
5. high-confidence deterministic interpretation;
6. constrained LLM interpretation;
7. clarification;
8. unsupported response.

Dialogue state retains the original question, routed intent, domain, pending capability, missing fields, clarification asked, user response, and resolution status. A follow-up such as “Paid conversions, weekly, January 2024 through June 2026” fills the pending KPI, frequency, and date slots instead of becoming a new unrelated intent.

## Slot and entity model

General slots include business question, decision type, historical/planning mode, horizon, KPI, channel/geography/segment scope, currency, constraints, and confidence goal.

MMM slots include date, frequency, history range, KPI/channel/spend/geography/segment columns, controls, promotions, calendar, pricing/product changes, and experiment evidence. GeoX slots include experiment question, candidate channel, treatment unit/markets, exclusions, pre-period, dates, duration, intervention, assignment constraints, and precision goal.

Every slot has provenance and status: detected, inferred, confirmed, missing, conflicted, or inapplicable. Only unresolved fields relevant to the active capability are requested. Confirmed user values override inference; conflicts are surfaced.

## Capability registry and requirement gaps

The capability registry is the authoritative descriptor of what MIP can do, required inputs/artifacts, outputs, claims, ownership, execution modes, next actions, documentation filters, and release gate. A descriptor contains:

```text
capability_id, version, owner, domain, status
supported_intents, supported_event_types
required_inputs, conditional_inputs, required_artifacts, produced_artifacts
allowed_claims, blocked_claims, execution_modes
next_capabilities, workflow_nodes, documentation_retrieval_filters, release_gate
```

Descriptors reference existing Pydantic models, schemas, adapters, and governed artifacts; a generated registry/index or contract metadata keeps them synchronized rather than creating a permanently separate handwritten truth.

Initial inventory and status:

| Capability | Status now |
| --- | --- |
| platform.onboarding; data.requirements.explain | available/deterministic |
| sample.use_case.activate | fixture-backed |
| uploaded_data.intake/profile/map_columns/assess_compatibility | readiness-only/future UI |
| mmm.intake.requirements/readiness | readiness-only |
| mmm.run.request; mmm.result.explain; mmm.channel_uncertainty.explain | fixture-backed or blocked by live engine |
| planning.readiness | blocked/readiness-only |
| planning.simulation.request; planning.recommendation.explain_blocked | blocked |
| geox.intake.requirements; geox.feasibility.explain | readiness-only/fixture-backed |
| geox.design_request.create; geox.readout.explain | external/readiness-only |
| calibration.compatibility.validate; calibration.signal.explain | available mapping/readiness |
| mmm.refresh.compare | fixture-backed comparison |
| decision_package.build; artifact.open; report.open; dashboard.context.update | planned control-plane capabilities |

A typed `RequirementGap` contains capability ID, satisfied/inferred/unconfirmed requirements, missing required/conditional inputs, conflicts, invalid inputs, missing artifacts, blocked actions, recommended clarifications, and next allowed actions. It drives readiness displays, clarification, blocked-state language, and deterministic/LLM response generation.

## Governed workflow graph

The shared graph is:

```text
Define decision → Bring data → Inspect and validate
→ Build and validate MMM → Understand channel results
→ Plan next quarter → Identify evidence gap → Design GeoX
→ Review GeoX evidence → Refresh MMM → Decision package
```

Each node has business purpose, supported questions, required capabilities/inputs/artifacts, available and blocked actions, display artifacts, execution mode, and next valid nodes. The graph prevents raw CSV → recommendation, raw spend → ROI, evidence gap → automatic GeoX assignment, and sample fixture → production recommendation. LLMs may select an existing node but cannot invent edges.

## One workflow across modes

Sample mode uses a deterministic fixture bundle; Analyze-my-data uses an uploaded-session workspace; future live mode uses governed engine outputs. All share workspace/session identity, event model, router, registry, workflow graph, requirement resolver, retrieval service, response contract, and verifier. They differ only in artifact provider and execution mode. No separate chat history, router, or RAG system is allowed.

## Navigation, dashboards, and artifact resolution

Views include home, intake, readiness, MMM results, planning, GeoX design/readout, calibration, and decision package. View changes may update active view, capability, artifact, selected chart/channel, and filters, but never clear conversation, goal, inputs, mappings, files, artifacts, nodes, or pending clarifications. Desktop uses a docked/adjacent conversation; narrow layouts use stacked/collapsible conversation. A new tab preserves workspace identity when supported.

A common artifact resolver locates sample fixtures, uploaded-session artifacts, readiness reports, MMM/GeoX/calibration/planning artifacts, reports, and dashboards. It returns identity, type, source, execution mode, dataset/KPI/time/geography scope, freshness, compatibility, claim eligibility, and lineage. Response generation never inspects arbitrary files directly.

## Evidence packet and response contract

Every response receives an evidence packet containing interaction, intent, conversation context, active view/artifact, business goal, known inputs, missing inputs, requirement gap, selected capability, execution status, resolved artifact summaries, allowed/blocked claims, disclosures, next action, clarifications, and filtered retrieval context.

The response contract contains:

```text
direct_answer, relevant_context, evidence_summary
known_inputs, missing_inputs, important_limitation, next_action
clarification_questions, contextual_follow_ups, navigation_target
active_artifact_reference, technical_details, claim_status
source_references, execution_disclosure
```

Primary copy is user-facing; IDs and contract details are progressive technical disclosure. The deterministic fallback consumes the same packet as future grounded generation and can handle MMM/GeoX requirements, data requirements, planning, trust, sample activation, upload guidance, clarification, and blocked actions.

## Retrieval and LLM boundaries

One governed retrieval service serves onboarding, MMM, GeoX, uploads, dashboards, and reports. RAG indexes approved documents and metadata for explanations, methodology, data rationale, examples, and governance. It is not authoritative for required inputs, artifact prerequisites, ownership, execution authorization, transitions, or claims. Metadata filters include domain, capability, document type, owner, version, status, method/production status, and effective date. Retrieval occurs after preliminary routing and capability filtering.

An LLM may interpret long-tail language, extract entities, ask clarifications, explain evidence, compare artifacts, summarize, and suggest valid navigation. Its structured route is registry-validated. It may not create capabilities, bypass inputs/edges, fit engines, choose markets, fabricate artifacts, authorize simulation/recommendations, or override verification. Deterministic routes handle explicit actions and high-confidence language; constrained LLM interpretation handles long-tail language only after dialogue/context resolution.

## Claim verifier

Verification checks numeric source coverage, input presence, capability status, fixture versus user/production scope, ROI/contribution boundaries, recommendation authorization, GeoX assignment ownership, calibration compatibility, uncertainty/disclosure requirements, intent/artifact match, and freshness. Outputs are `passed`, `blocked`, `rewritten`, `requires_clarification`, or `requires_human_review`. A response cannot be displayed as successful if verification fails.

## Evaluation strategy

Evaluation sets cover exact/paraphrased/overlapping routes, explicit domains, ambiguity, unsupported questions, clarification resolution, corrections, topic changes, navigation, sample/upload transitions, active-artifact questions, slot extraction, capability selection, grounding, stale/incompatible artifacts, recommendation overreach, and continuity through buttons, views, reports, and dashboards.

Metrics include route accuracy, slot precision/recall, clarification accuracy, capability/artifact selection accuracy, grounded-claim rate, unsafe-claim escape rate, and conversation continuity rate.

## Implementation phases and dependencies

A — typed interaction/event, intent, requirement gap, capability descriptor, evidence packet, response, and verifier contracts.

B — capability registry inventory synchronized to current contracts.

C — persistent workspace projection and shared event handling.

D — dialogue-aware deterministic router with explicit domains, precedence, slots, and pending clarification.

E — governed workflow graph and capability binding.

F — artifact and requirement resolver for fixture and uploaded-session sources.

G — readiness-only upload flow: upload → profile → map → clarify → validate → readiness.

H — deterministic grounded response layer.

I — governed explanatory retrieval service and metadata index.

J — constrained LLM interpretation/generation behind registry and verifier.

K — dashboard/report/multi-view continuity.

L — routing, dialogue, grounding, continuity, and release evaluation gates.

A–B may proceed in parallel after architecture sign-off. C depends on A; D depends on A–C; E depends on B–D; F depends on B/E; G depends on F and existing upload contracts; H depends on A/E/F; I depends on B/H; J depends on D/H/I; K depends on C/E/F; L follows H and is repeated at each release gate.

## Guided-workspace roadmap reconciliation

The vertical journey task is deferred until the control-plane implementation plan defines tile/node bindings, typed events, active artifact context, and continuity. It must not ship as visual-only cards.

The answer-layer task is superseded by the control-plane response/evidence architecture: its deterministic work becomes Phase H, and any provider seam becomes Phase J.

Upload readiness remains a Phase G capability on the shared workspace state; it is not a separate product branch or chat history. Additional domains remain deferred until the SaaS/common control plane passes continuity and claim-safety evaluation.

## Architecture decisions

1. One workspace owns one persistent conversation.
2. One router/control plane serves every view and entry mode.
3. One filtered retrieval service serves all explanatory domains.
4. Buttons and links are typed events.
5. Navigation never implicitly resets.
6. Sample, upload, and future live modes share workflow/state.
7. Workflow nodes are governed capabilities, not merely tiles.
8. RAG supplements typed contracts and gates.
9. LLM routes are constrained and registry-validated.
10. Claim verification is deterministic.
11. Event history and derived state are separate.
12. Dashboard context participates in routing.
13. Engine ownership stays outside the LLM.
14. Deterministic fallback consumes the same evidence packet.
15. Additional domains wait for the common control plane.

## Session persistence stages

The current local demo uses in-memory Streamlit session state. A later authenticated workspace adds a persistent session/artifact store. Future multi-page/tab support adds workspace/conversation identity, append-only events, optimistic versions, and conflict handling. Immediate implementation need not add persistence, but contracts must remain serializable and identity-aware.

## Architecture verdict

`CONVERSATIONAL_CONTROL_PLANE_ARCHITECTURE_COMPLETE_IMPLEMENTATION_PLAN_NEXT`

Next artifact: `MIP_CONVERSATIONAL_CONTROL_PLANE_IMPLEMENTATION_PLAN_001`.
