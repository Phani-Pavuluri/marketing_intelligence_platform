# Agent Answerability and Fallback Contract Plan 001

## 1. Title and status

| Field | Value |
|-------|-------|
| **Title** | Agent Answerability and Fallback Contract Plan 001 |
| **Status** | Accepted contract planning direction; **partial implementation** — contracts + deterministic evaluator |
| **Type** | Agent governance / answerability / fallback / UX resilience plan |
| **Base commit** | `d47f913` — agent answerability plan merged (PR #41) |
| **Date** | 2026-05-28 |
| **Scope** | Plan + `AgentAnswerabilityState`/`AgentAnswerabilityDecision` contracts + `evaluate_agent_answerability` (no LLM runtime) |

**Hard boundaries (unchanged):** No MMM/GeoX execution, no LLM providers, no production ingestion, no notebooks, no new FastAPI routes, no Streamlit behavior changes, no unsupported causal/ROI/optimizer claims. MIP remains the **control plane**, not the statistical engine.

---

## 2. Problem statement

Future MIP agents must preserve UX when they do not know what to do, but must **not** hallucinate from limited tool context.

Two failure modes to prevent:

| Failure mode | Symptom | Root cause |
|--------------|---------|------------|
| **Too loose** | Agent invents causal lift, ROI, optimizer outputs, or core ML results from advisory/demo context | No typed answerability gate before response generation |
| **Too rigid** | Agent says "I don't know" whenever no exact hardcoded rule exists | Corner-case rule sprawl instead of contract-based classification |

The product needs a **middle layer**: agents may exercise judgment, but judgment must be **constrained by contracts** — claim taxonomy, evidence level, tool availability, report governance, and a small top-level state machine.

**Intended agent flow (future):**

```text
User question
  → classify intent + requested claim type
  → evaluate AgentAnswerabilityState (5-state machine)
  → check available artifacts, deterministic tools, core ML availability
  → produce AgentAnswerabilityDecision
  → generate response from typed source (report/tool output), not free-form guessing
```

---

## 3. Core principle

**Agents may reason over contracts, reports, tool availability, and evidence state.**

**Agents may not invent missing evidence, causal effects, ROI, optimizer outputs, or core ML results.**

Every agent answer passes through a typed decision gate:

| Gate question | Typical outcome |
|---------------|-----------------|
| Can answer from existing registered artifact/report? | `ANSWERABLE_FROM_REGISTERED_ARTIFACT` |
| Can a deterministic tool produce a safe report? | `ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT` |
| Does the claim require MMM/GeoX/core ML? | `NEEDS_CORE_DIAGNOSTIC_OR_ML` |
| Is required user/data input missing? | `NEEDS_USER_INPUT_OR_DATA` |
| Is the claim unsupported by governance? | `BLOCKED_BY_CLAIM_BOUNDARY` |

This is **not** about making the LLM smarter. It is about making agents **contract-aware** so they degrade gracefully without hallucinating.

---

## 4. Top-level answerability state machine

### `AgentAnswerabilityState` (required — exactly one per decision)

| State | Value | Meaning |
|-------|-------|---------|
| 1 | `ANSWERABLE_FROM_REGISTERED_ARTIFACT` | An existing registered artifact/report can answer the request |
| 2 | `ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT` | No artifact yet, but a deterministic workflow/tool can safely produce one |
| 3 | `NEEDS_CORE_DIAGNOSTIC_OR_ML` | Request requires MMM, GeoX, power/MDE, matched markets, response curves, optimizer, or certified DecisionSurface |
| 4 | `NEEDS_USER_INPUT_OR_DATA` | Request may be answerable after missing fields/data are supplied |
| 5 | `BLOCKED_BY_CLAIM_BOUNDARY` | Requested claim is unsupported or violates governance boundaries |

**Rule:** Every user request classifies into **exactly one** state. Answer modes (§5) are **secondary** labels derived from state, not a parallel top-level taxonomy.

### State semantics

#### 1. `ANSWERABLE_FROM_REGISTERED_ARTIFACT`

**When:** Existing `DeterministicReportEnvelope`, export JSON, or other registered governed artifact can answer.

**Examples:**
- Explain an existing calibration report
- Summarize an exported deterministic report
- Explain why a report is `needs_more_data` or `blocked`

**Allowed:** Explain artifact contents; cite report fields; preserve `governance_status` and `evidence_mode`.

**Forbidden:** Add causal/ROI/optimizer claims beyond artifact contents; upgrade `advisory_only` to decision support.

#### 2. `ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT`

**When:** No artifact exists yet, but a governed deterministic tool can produce a safe envelope.

**Examples:**
- Run cold-start advisory from business-profile fixture
- Run calibration mapping from valid readout fixture
- Export deterministic report JSON via `mip.reports.*`

**Allowed:** Run deterministic tool; return/report envelope; explain advisory/diagnostic status.

**Forbidden:** Infer MMM/GeoX outputs; create lift, ROI, MDE, matched markets, optimizer, or scenario outputs.

#### 3. `NEEDS_CORE_DIAGNOSTIC_OR_ML`

**When:** Claim requires core MMM, GeoX/panel_exp, power diagnostics, matched-market design, treatment assignment, response curves, optimizer, scenario planner, or certified DecisionSurface.

**Allowed:** Route to required core engine; explain what output is needed; list required inputs.

**Forbidden:** Answer from advisory/demo fixture alone; fabricate estimates or recommendations.

#### 4. `NEEDS_USER_INPUT_OR_DATA`

**When:** Request may be answerable, but required fields or data are missing or ambiguous.

**Examples:** No spend/outcome history; missing standard error; missing geo/time grain; missing KPI; ambiguous scope.

**Allowed:** Ask for missing data; provide safe checklist; explain why answer cannot be produced yet.

**Forbidden:** Fill missing data from assumptions; silently downgrade to unsupported estimates.

#### 5. `BLOCKED_BY_CLAIM_BOUNDARY`

**When:** Requested claim is unsupported by MIP governance regardless of available tools.

**Examples:** "Prove ROI" from advisory profile only; optimized budget without DecisionSurface; treatment DMA selection without GeoX engine.

**Allowed:** Block clearly; explain boundary; suggest safe alternative route.

**Forbidden:** Soften blocked claim into pseudo-answer; invent evidence.

---

## 5. Answerability decision contract

### Future contract: `AgentAnswerabilityDecision`

**Module:** `src/mip/contracts/agent_answerability.py` — **implemented**.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `decision_id` | `str` | yes | Stable unique ID for this classification |
| `state` | `AgentAnswerabilityState` | yes | One of five states (§4) |
| `user_intent` | `str` | yes | Normalized intent summary |
| `requested_claim_type` | `str` | yes | From claim taxonomy (§7) |
| `answer_mode` | `str` | no | Secondary label derived from state (§5b) |
| `evidence_level` | `str` | yes | From evidence levels (§6) |
| `source_artifact_ids` | `list[str]` | no | Registered artifacts available for explanation |
| `available_report_ids` | `list[str]` | no | `DeterministicReportEnvelope.report_id` values |
| `required_tool` | `str` | no | Deterministic tool name if state 2 |
| `required_core_engine` | `str` | no | `mmm`, `geox`, `decision_surface`, etc. if state 3 |
| `missing_inputs` | `list[str]` | no | Required fields/data not yet available |
| `blocked_claims` | `list[str]` | no | Claims that must not appear in response |
| `allowed_response_scope` | `list[str]` | yes | What the agent may say |
| `forbidden_response_scope` | `list[str]` | yes | What the agent must not say |
| `fallback_message` | `str` | no | UX-safe degradation message (§9) |
| `confidence_in_routing` | `str` | no | `high` / `medium` / `low` — confidence **state classification is correct**, not truth of business/causal claim |
| `artifact_refs` | `list[ArtifactReference]` | no | Provenance from `deterministic_report_v1` |

### 5b. Secondary answer modes (derived from state)

| State | Typical `answer_mode` |
|-------|----------------------|
| `ANSWERABLE_FROM_REGISTERED_ARTIFACT` | `direct_report_explanation` |
| `ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT` | `deterministic_tool_report`, `advisory_only_guidance` |
| `NEEDS_CORE_DIAGNOSTIC_OR_ML` | `route_to_mmm`, `route_to_geox`, `route_to_calibration`, `route_to_readiness`, `route_to_decision_surface` |
| `NEEDS_USER_INPUT_OR_DATA` | `missing_data_request` |
| `BLOCKED_BY_CLAIM_BOUNDARY` | `blocked_unsupported_claim` |

Additional secondary modes (tooling failures, scope):

| `answer_mode` | When |
|---------------|------|
| `tool_unavailable_fallback` | Deterministic tool exists in contract but runtime unavailable |
| `out_of_scope` | Request outside MIP product boundary |

For each answer mode, implementation must document: when allowed, required evidence, allowed response behavior, forbidden response behavior, and example safe response (see §9).

---

## 6. Evidence levels

| Level | Agent can say | Agent cannot say |
|-------|---------------|------------------|
| `general_knowledge` | General marketing concepts; questions to clarify intent | Measured lift, ROI, channel rankings, budget allocation |
| `business_profile_only` | Cold-start hypotheses; tracking/setup guidance; learning agenda | Causal proof; ROI; MMM/GeoX readiness certification |
| `synthetic_fixture` | Demo/fixture-scoped explanations with synthetic label | Production claims; certified measurement |
| `deterministic_workflow_report` | Contents of `DeterministicReportEnvelope` fields only | Claims beyond report `allowed_downstream_uses` |
| `calibration_candidate` | Structural mapping status; missing uncertainty fields | MMM calibration executed; causal certification |
| `diagnostic_only` | Structural readiness; missing-data checklists | Fitted model outputs; power/MDE; matched markets |
| `core_mmm_required` | What MMM inputs/outputs are needed; route to MMM | Channel ROI, response curves, optimizer mix from advisory |
| `core_geox_required` | What GeoX design/readout needs; route to GeoX | Matched markets, treatment assignment, lift without engine |
| `certified_decision_surface_required` | What DecisionSurface/approval prerequisites are | Budget optimization; production decision authorization |
| `unsupported` | Block with boundary explanation | Any measurement or decision claim |

Evidence level is **input to** state classification, not a substitute for it.

---

## 7. Claim taxonomy

| Claim type | Required evidence / tooling | Typical state |
|------------|----------------------------|---------------|
| `general_marketing_advice` | `general_knowledge` or `business_profile_only` | 2 or 4 |
| `tracking_or_data_readiness` | `deterministic_workflow_report` (readiness) or fixture | 1, 2, or 4 |
| `cold_start_advisory` | `business_profile_only` or advisory report | 1 or 2 |
| `measurement_readiness` | readiness report / workbench | 1, 2, or 4 |
| `experiment_calibration` | calibration mapping report | 1, 2, or 4 |
| `causal_lift` | certified experiment/GeoX readout | 3 or 5 |
| `roi` | certified MMM/experiment output | 3 or 5 |
| `budget_optimization` | governed DecisionSurface + optimizer governance | 3 or 5 |
| `scenario_planning` | scenario planner + certified inputs | 3 or 5 |
| `response_curve` | fitted MMM engine output | 3 or 5 |
| `matched_market_design` | GeoX/panel_exp engine | 3 or 5 |
| `power_mde` | GeoX power diagnostics | 3 or 5 |
| `treatment_assignment` | GeoX design engine | 3 or 5 |
| `production_recommendation` | TrustReport + approval | 3 or 5 |

**Mapping principle:** Classify `requested_claim_type` → required evidence → compare to available artifacts/tools → assign one of five states. **Do not** hardcode per-question rules.

---

## 8. Tool availability and fallback behavior

### Future contract: `ToolAvailabilityStatus`

| Field | Type | Description |
|-------|------|-------------|
| `tool_name` | `str` | e.g. `build_cold_start_advisory_plan`, `run_calibration_mapping_for_stage_a_fixture` |
| `tool_type` | `str` | `deterministic_workflow`, `report_export`, `core_mmm`, `core_geox` |
| `available` | `bool` | Whether tool can be invoked in current environment |
| `supports_claim_types` | `list[str]` | Claim types this tool may support |
| `unsupported_claim_types` | `list[str]` | Claim types that must not be inferred from this tool |
| `required_input_contract` | `str` | Pydantic contract or fixture category |
| `failure_mode` | `str` | `unavailable`, `missing_input`, `governance_blocked` |
| `fallback_answer_mode` | `str` | Secondary mode when tool fails |

### Fallback rules (deterministic evaluator — future)

1. **If deterministic report exists** → state 1; explain report (`direct_report_explanation`).
2. **If no report but deterministic tool available** → state 2; run tool or offer to run it.
3. **If workflow unavailable** → `tool_unavailable_fallback`; explain limitation; do not hallucinate.
4. **If claim requires core ML** → state 3; route to MMM/GeoX/DecisionSurface; never answer from advisory alone.
5. **If required data missing** → state 4; ask for missing inputs; provide checklist from report if present.
6. **If claim unsupported** → state 5; block with plain-language reason and safe alternative.
7. **If tool fails** → return failure packet + safe fallback; preserve `blocked_claims`.

---

## 9. UX-safe fallback responses

Conceptual templates (not exact copy — implementation may vary):

| Situation | Safe response pattern |
|-----------|----------------------|
| Advisory-only context | "I can give advisory guidance, but not causal proof." |
| Core ML required | "This needs a certified MMM/GeoX output — MIP can route you there when available." |
| Missing uncertainty | "The current data is missing uncertainty, so it cannot be used as calibration evidence." |
| Report explanation boundary | "I can explain the report, but I cannot create ROI from it." |
| Missing routing fields | "I need these fields before routing this safely: …" |
| Tool unavailable | "The deterministic workflow is not available in this environment; here is what would be required." |
| Blocked claim | "That claim is not supported from this evidence level. Safe next step: …" |

**Goal:** Graceful degradation, not silent failure or pseudo-answers.

---

## 10. Anti-hardcoding principle

The system must **not** hardcode every corner case.

Classification uses:

- `requested_claim_type` (§7)
- `AgentAnswerabilityState` (§4)
- `evidence_level` (§6)
- Available artifacts/reports (`source_artifact_ids`, `available_report_ids`)
- Available deterministic tools (`ToolAvailabilityStatus`)
- Report `governance_status`, `evidence_mode`, `blocked_claims`
- Report `allowed_downstream_uses`, `forbidden_downstream_uses`
- Missing input requirements from workflow contracts

New user questions route through the **same** `AgentAnswerabilityDecision` contract. Edge cases add taxonomy entries or evidence rules — not `if question contains "ROI"` branches in agent runtime.

---

## 11. Relationship to deterministic reports

**LLM/agents must consume `DeterministicReportEnvelope` and registered artifacts — not answer directly from raw fixture JSON when a report exists.**

Report fields that **constrain** agent answers:

| Field | Constraint |
|-------|------------|
| `governance_status` | e.g. `advisory_only` forbids decision/causal tone |
| `evidence_mode` | Caps evidence level for explanation |
| `blocked_claims` | Must be reflected in `forbidden_response_scope` |
| `allowed_downstream_uses` | Caps `allowed_response_scope` |
| `forbidden_downstream_uses` | Must appear in `forbidden_response_scope` |
| `missing_data` | Drives state 4 responses |
| `recommended_next_steps` | Safe alternatives for fallback |
| `workflow_payload` | Authoritative structured content for explanation |

**Future LLM path:**

```text
free-form user question
  → LLM extracts structured intent (not authoritative)
  → deterministic answerability evaluator → AgentAnswerabilityDecision
  → if state 1/2: run tool or load report
  → LLM explains deterministic report/decision only
```

The LLM must **not** directly generate the advisory/measurement report, invent causal claims, or override `governance_status`.

---

## 12. Relationship to core ML

Core MMM/GeoX engines (separate repos via adapters) are **required** for:

- Causal lift / incremental effect certification
- ROI and channel contribution rankings
- Power / MDE
- Matched markets and treatment assignment
- Response curves
- Optimizer and scenario-planner outputs
- Certified decision support

**Agent behavior:** Route (`NEEDS_CORE_DIAGNOSTIC_OR_ML`) or block (`BLOCKED_BY_CLAIM_BOUNDARY`) — **never fabricate**.

MIP control-plane outputs (advisory, readiness, calibration mapping, intake routing) are **structural/diagnostic** unless explicitly labeled otherwise in report contracts.

---

## 13. Evaluation harness plan

### Future contract: `AgentCapabilityEvalCase`

| Field | Description |
|-------|-------------|
| `case_id` | Stable eval ID |
| `user_question` | Natural language input |
| `available_reports` | List of report IDs / fixture exports |
| `available_tools` | Tool availability snapshot |
| `expected_state` | One of five `AgentAnswerabilityState` values |
| `expected_answer_mode` | Secondary mode (optional) |
| `expected_evidence_level` | From §6 |
| `expected_blocked_claims` | Claims that must not appear |
| `forbidden_phrases` | Substrings that fail eval |
| `expected_safe_fallback` | Conceptual fallback pattern |

### Required eval scenarios

| # | Scenario | Expected state |
|---|----------|----------------|
| 1 | User asks for ROI with only advisory report (default routing) | `NEEDS_CORE_DIAGNOSTIC_OR_ML` |
| 1b | User asserts ROI proof from advisory-only artifacts | `BLOCKED_BY_CLAIM_BOUNDARY` |
| 2 | User asks what to do next with business profile; advisory tool available | `ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT` |
| 3 | User asks to explain existing calibration report | `ANSWERABLE_FROM_REGISTERED_ARTIFACT` |
| 4 | User asks to use missing-SE experiment as calibration evidence | `NEEDS_USER_INPUT_OR_DATA` |
| 5 | User asks for matched markets from readiness summary | `NEEDS_CORE_DIAGNOSTIC_OR_ML` |
| 6 | Deterministic tool unavailable | `tool_unavailable_fallback` (secondary); no hallucination |
| 7 | User asks ambiguous "should I increase spend?" | `NEEDS_USER_INPUT_OR_DATA` or `NEEDS_CORE_DIAGNOSTIC_OR_ML` — never direct optimizer answer |
| 8 | User asks for unsupported causal proof from synthetic fixture | `BLOCKED_BY_CLAIM_BOUNDARY` |

Eval harness is **deterministic** — no LLM in v1 evaluator.

---

## 14. Implementation sequencing

| Order | Item | Type |
|-------|------|------|
| 1 | **This contract plan** | Docs ✓ |
| 2 | `AgentAnswerabilityState` + `AgentAnswerabilityDecision` Pydantic contracts | Code ✓ |
| 3 | Claim taxonomy and evidence-level enums (shared with advisory/report contracts) | Code ✓ |
| 4 | Deterministic answerability evaluator (`evaluate_agent_answerability(...)`) | Code ✓ |
| 5 | `AgentCapabilityEvalCase` harness + required scenarios | Tests ✓ |
| 6 | LLM explanation request/response contracts | Docs + code |
| 7 | LLM explanation implementation **over deterministic reports only** | Code |
| 8 | Agent runtime / tool registry (P17) | Code — later |
| 9 | BYOK / provider integration | Code — later |

**Explicit blocks:**

- LLM runtime before answerability contracts + evaluator
- LLM explanations before eval harness passes
- Agent tool registry before `AgentAnswerabilityDecision` gate exists
- Free-form agent answers without source reports

---

## 15. Stop/go criteria

### Safe now

- [x] Docs/contract planning (this document)
- [x] Typed `AgentAnswerabilityState` + `AgentAnswerabilityDecision` contracts
- [x] Deterministic answerability evaluator (no LLM)
- [x] Eval harness with required scenarios (structured inputs)

### Needs more detail before implementation

- LLM explanation copy/tone guidelines
- Agent runtime orchestration (P17 / LangGraph)
- UI chat binding and streaming behavior
- Provider-specific error handling

### Blocked

- Free-form agent answers without `AgentAnswerabilityDecision`
- Direct LLM access to raw tools without answerability gate
- ROI, optimizer, causal lift, power/MDE, matched markets, treatment assignment claims without core ML outputs
- LLM overriding `governance_status` or `blocked_claims` on reports

---

## 16. Deterministic evaluator implementation rules

**Implemented:** `mip.contracts.agent_answerability`, `mip.agents.answerability.evaluate_agent_answerability` (flat kwargs), `mip.workflows.agent.answerability` (request object).

### Structured inputs only

The evaluator uses `AgentAnswerabilityRequest` — not natural-language question matching. `user_intent` is metadata on the decision record only.

### Decision priority

1. `BLOCKED_BY_CLAIM_BOUNDARY`
2. `NEEDS_USER_INPUT_OR_DATA`
3. `ANSWERABLE_FROM_REGISTERED_ARTIFACT`
4. `ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT`
5. `NEEDS_CORE_DIAGNOSTIC_OR_ML`

Governance on available reports **overrides** tool availability.

### ROI nuance

- Default ROI with advisory-only report → `NEEDS_CORE_DIAGNOSTIC_OR_ML`
- ROI asserted from advisory artifacts (`assert_claim_authorized_by_available_artifacts=True`) → `BLOCKED_BY_CLAIM_BOUNDARY`

---

## References

- [MIP Report, Adapter, and Agent Contract Plan 001](MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md) — §7 agent packets, §8 LLM boundaries
- [MIP Agent Tooling and Roadmap Implementation Detail Audit 001](../audits/MIP_AGENT_TOOLING_AND_ROADMAP_IMPLEMENTATION_DETAIL_AUDIT_001.md)
- [Stage A.3 Advisory Readiness Intake Adapter Plan 001](STAGE_A3_ADVISORY_READINESS_INTAKE_ADAPTER_PLAN_001.md)
- `mip.contracts.deterministic_report` — `DeterministicReportEnvelope`, `governance_status`, `forbidden_downstream_uses`
- `mip.contracts.advisory` — advisory claim types and evidence modes
- `mip.contracts.agentic_workflow` — existing agent role contracts (P8b)
