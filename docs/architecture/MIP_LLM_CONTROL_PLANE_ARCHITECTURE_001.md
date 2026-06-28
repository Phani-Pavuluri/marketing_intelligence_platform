# MIP LLM Control Plane Architecture 001

## 1. Artifact identity

| Field | Value |
|-------|-------|
| **Artifact ID** | `MIP_LLM_CONTROL_PLANE_ARCHITECTURE_001` |
| **Status** | Accepted architecture / governance reconciliation |
| **Type** | MIP-level LLM control-plane architecture (docs/governance only) |
| **Base commit** | `000273a` — Agent capability eval fixtures merged (PR #44) |
| **Date** | 2026-05-28 |
| **Scope** | Docs/governance architecture only — **no runtime agents, orchestration, MMM/GeoX execution, or production behavior** |
| **Final verdict** | `mip_llm_control_plane_architecture_defined_no_runtime_agents_or_production_authorization` |

---

## 2. Why this architecture is needed

MIP is converging on a product direction where users interact primarily through natural language, while measurement truth remains in deterministic MMM and GeoX/panel_exp engines. Without a shared control-plane architecture, each package risks building redundant agents, conflicting routing policies, and incompatible claim boundaries.

Recent MIP work established foundational pieces:

- `DeterministicReportEnvelope` / `deterministic_report_v1`
- Five-state `AgentAnswerabilityState` machine + deterministic evaluator
- Agent capability eval fixtures (10 cases)
- P7b LLM provider-governance contracts
- P8b agent role / failure / manifest contracts

This artifact reconciles those pieces into one **MIP-level LLM control plane** that MMM and GeoX plug into through package-specific tool adapters — without rolling back completed deterministic work.

---

## 3. Current decision: LLM-first, deterministic-core

**Platform direction:**

| Layer | Role |
|-------|------|
| **LLM** | Default user-facing interface |
| **Deterministic MMM/GeoX tools** | Source of truth for measurement, design, inference, optimization |
| **Typed artifacts, contracts, report builders** | Evidence boundary |
| **Claim gates** | Prevent overclaiming |

The LLM **may**:

- understand user intent
- ask follow-up questions
- route to tools
- run low-risk tools when goals are clear and deterministic preconditions pass
- recover from failures
- invoke the deterministic reporting layer
- explain typed outputs conversationally
- store explicit session assumptions as structured state

The LLM **may not independently compute or authorize**:

- causal lift
- ROI
- power / MDE
- p-values / confidence intervals
- budget optimization
- treatment/control assignment
- method promotion
- MMM calibration acceptance
- production authorization

**Principle:** LLM explains and routes; deterministic contracts decide.

---

## 4. Shared MIP control plane and package-specific adapters

```text
┌─────────────────────────────────────────────────────────────────┐
│              MIP LLM Control Plane (shared)                      │
│  Intent+Answerability │ Routing │ Intake │ Explanation │ Recovery │
│  Report Invocation │ Session State │ Trace/Manifest              │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ MMM tool        │ │ GeoX/panel_exp  │ │ MIP control     │
│ adapters        │ │ tool adapters   │ │ plane tools     │
│ (mmm repo)      │ │ (panel_exp)     │ │ (intake, reports)│
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

**Avoid** separate unrelated MMM-agent and GeoX-agent systems unless package constraints force it. Package-specific logic lives in **tool adapters**; shared policy lives in the **MIP control plane**.

---

## 5. Relationship to MMM

MMM remains the **execution owner** for:

- model fitting, diagnostics, decomposition
- response curves, optimizer outputs
- Δμ / DecisionSurface production
- calibration application (when gated)

MIP control plane **does not** run MMM math. It:

- routes user intent to MMM readiness / intake / calibration workflows
- validates answerability before invoking MMM tools
- invokes deterministic MMM report builders
- explains MMM outputs via grounded LLM explanation (future)
- preserves `TrustReport` and promotion gates

MMM exposes typed tools and report envelopes through **MMM-specific adapters** registered in the MIP tool registry (future contract).

---

## 6. Relationship to GeoX / panel_exp

GeoX/panel_exp remains the **execution owner** for:

- power / MDE, matchability, design feasibility
- candidate design generation (when authorized)
- treatment/control assignment (when authorized)
- inference / readout
- design-based inference

MIP control plane **does not** run GeoX math. It:

- routes to GeoX readiness and design-intake workflows
- auto-runs low-risk GeoX diagnostics when preconditions pass
- invokes deterministic GeoX report builders
- explains GeoX outputs conversationally
- recovers from tool failures with safe fallbacks

### Compatible completed GeoX/panel_exp work (preserve)

| Artifact | Status | Compatibility |
|----------|--------|---------------|
| `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` | Completed (panel_exp `ea9178a`) | Golden paths + answerability recovery concepts align with control plane |
| `GEO_KPI_SPEND_DATA_PROFILER_001` | Completed (panel_exp `7b992f6`) | Low-risk diagnostic auto-run candidate |
| `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` | Completed (panel_exp `9b3c304`) | Low-risk diagnostic auto-run candidate |

This MIP artifact does **not** implement panel_exp. It defines the architecture panel_exp and MMM align to.

---

## 7. Deterministic source-of-truth principle

| Claim type | Source of truth |
|------------|-----------------|
| Structural readiness | MIP readiness reports, profiler diagnostics |
| Advisory hypotheses | Cold-start advisory reports (`advisory_only`) |
| Calibration mapping | Calibration mapping reports (`candidate` / `diagnostic`) |
| Causal lift, ROI, MDE | Certified GeoX/MMM engine outputs only |
| Budget optimization | Certified DecisionSurface + optimizer governance |
| Final stakeholder reports | Deterministic report builders only |

Typed artifacts (`DeterministicReportEnvelope`, `AgentAnswerabilityDecision`, `TrustReport`, engine contracts) are the evidence boundary. LLM prose is never authoritative.

---

## 8. Tool routing policy: LLM proposes, deterministic registry validates

**Safe routing pattern:**

```text
User message
  → LLM proposes tool/workflow route (intent classification)
  → Deterministic tool registry validates:
       - tool exists and is available
       - package scope (MMM vs GeoX vs MIP)
       - preconditions / required inputs
       - allowed claim level
  → Answerability gate classifies request (five-state machine)
  → If authorized: invoke tool or report builder
  → If blocked/missing: safe fallback (no hallucination)
```

The LLM **proposes** routes. The registry **validates**. The answerability evaluator **classifies**. No step may be skipped in decision-grade paths.

---

## 9. Answerability gate policy

Every user request passes through `evaluate_agent_answerability()` before tool invocation or LLM explanation.

| State | Control-plane behavior |
|-------|------------------------|
| `ANSWERABLE_FROM_REGISTERED_ARTIFACT` | Explain existing report; no new measurement |
| `ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT` | Run deterministic tool; explain output |
| `NEEDS_CORE_DIAGNOSTIC_OR_ML` | Route to MMM/GeoX/DecisionSurface; explain requirement |
| `NEEDS_USER_INPUT_OR_DATA` | Ask for missing inputs; checklist |
| `BLOCKED_BY_CLAIM_BOUNDARY` | Block with governance explanation; safe alternative |

**Implemented:** `mip.contracts.agent_answerability`, `mip.agents.answerability`, `examples/fixtures/agent_capability_eval/`.

**Future:** unify answerability + failure recovery in `MIP_AGENT_ANSWERABILITY_AND_RECOVERY_CONTRACT_001`.

---

## 10. Low-risk diagnostic auto-run policy

The LLM may **auto-run** low-risk deterministic diagnostics when:

1. User goal is clear (structured claim type resolved)
2. Deterministic preconditions pass
3. Tool registry marks tool as `low_risk_auto_run`
4. Answerability state permits tool output

**Examples (allowed auto-run):**

- schema / profiler checks (`GEO_KPI_SPEND_DATA_PROFILER_001`)
- data contract validation
- geo unit / market feasibility diagnostics (`GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001`)
- spend contrast diagnostics (when implemented)
- artifact lookup / registered report retrieval
- safe missing-input checks
- read-only structural diagnostics

**Auto-run does not** upgrade governance status or authorize high-stakes claims.

---

## 11. High-stakes action authorization policy

High-stakes actions require **deterministic authorization** and likely **user confirmation**:

| Action | Authorization |
|--------|---------------|
| Candidate design generation | GeoX engine + readiness gates + user confirm |
| Treatment/control assignment | GeoX design engine + explicit approval |
| Inference / readout | Certified readout path + trust tier |
| Budget recommendation | DecisionSurface + optimizer governance |
| Final report publication | Deterministic report builder + governance labels |
| External side effects | Human approval workflow |
| Production-impacting actions | Release gates + `TrustReport` |

LLM may **propose** these actions; it may not **authorize** them.

---

## 12. Final report invocation policy

**Rule:** Final official reports come from **deterministic report builders**. The LLM invokes the reporting layer and explains the result.

| Report type | Builder owner | LLM role |
|-------------|---------------|----------|
| Full MMM model reports | MMM deterministic builders | Explain only |
| Planning reports | MMM + DecisionSurface contracts | Explain only |
| GeoX design/readout reports | panel_exp deterministic builders | Explain only |
| Executive summaries | Deterministic summary builders | Explain only |
| MIP advisory/readiness/calibration | `mip.reports.*` | Explain only |

LLM must **not** independently generate final official reports as source-of-truth artifacts.

**Future contract:** `MIP_REPORT_INVOCATION_CONTRACT_001`.

---

## 13. Advisory mode policy

When data is missing or evidence is advisory-only, the LLM may explain:

- what MMM/GeoX can do
- what data is required
- how the user can proceed

**Advisory mode must be explicitly labeled** and cannot authorize:

- final feasibility
- design recommendation
- power/MDE
- p-values / CIs
- lift / ROI
- MMM calibration acceptance
- budget optimization
- production use

Maps to `AgentAnswerabilityState.NEEDS_USER_INPUT_OR_DATA`, `NEEDS_CORE_DIAGNOSTIC_OR_ML`, and advisory `governance_status` on reports.

---

## 14. Session state / assumption management policy

**Allowed:** explicit structured facts stored as auditable session state.

```text
kpi = conversions
geo_level = DMA
planned_test_start_date = 2026-07-01
manipulation_type = HEAVY_UP
goal = planning
package_intent = GeoX
mmm_grain = weekly
channel = paid_social
```

**Not allowed:** inferred probabilistic claims as facts.

```text
probably feasible
probably weekly
probably ROI positive
likely valid design
user wants ROI (unless explicitly stated)
```

Conversation-derived assumptions must be:

- auditable
- user-editable
- distinguishable from tool-derived facts

**Future contract:** `MIP_SESSION_STATE_AND_ASSUMPTION_CONTRACT_001`.

---

## 15. Necessary LLM capabilities / modules

These are **modules of one shared control plane**, not separate autonomous services:

| Module | Responsibility |
|--------|----------------|
| **Intent + Answerability** | Classify claim type; run answerability gate |
| **Tool Routing + Workflow Orchestration** | LLM proposes route; registry validates; planner sequences steps |
| **Data Intake + Clarification** | Missing-input collection; common intake workbench integration |
| **Grounded Explanation** | Explain deterministic reports/decisions with citations |
| **Failure Recovery** | Safe fallback on tool/registry/answerability failures |
| **Report Invocation** | Trigger deterministic report builders; pass envelopes to explanation |
| **Session State / Assumption Management** | Store explicit structured facts only |

---

## 16. Deferred / collapsed standalone agents

Do **not** promote these as active near-term package-side agents. Fold into control-plane modules or deterministic tools:

| Standalone agent | Control-plane disposition |
|------------------|---------------------------|
| Design Feasibility Interpreter Agent | Fold into Grounded Explanation + low-risk diagnostics |
| Method Selection Guard Agent | Fold into Answerability gate + claim taxonomy |
| Randomization Assignment Guard Agent | High-stakes authorization policy; GeoX engine owns assignment |
| Experiment Readout QA Agent | Deterministic readout validators + report explanation |
| Research Scout Agent | Deferred — not near-term |
| MLOps Agent | Deferred — platform ops, not measurement control plane |
| Feature Store Agent | Deferred — infrastructure, not near-term |
| Privacy/Security Agent | Deferred — governance overlay, revisit when runtime needs justify |

---

## 17. Ballpark standalone contract deferral

`BALLPARK_FEASIBILITY_MODE_CONTRACT_001` is **deferred** unless ballpark becomes a distinct user-facing planning workflow.

**Preserve** existing ballpark/provisional behavior inside:

- profiler / intake provisional modes
- advisory mode boundaries
- provisional-only claim boundaries
- golden path blocked/provisional cases (`PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001`)

Do **not** delete useful ballpark safeguards. Only defer the standalone roadmap artifact.

---

## 18. Artifact / report grounding requirements

Every LLM explanation must ground in:

- `AgentAnswerabilityDecision` (state, blocked claims, missing inputs)
- `DeterministicReportEnvelope` (when report exists)
- `ArtifactReference` provenance
- `allowed_downstream_uses` / `forbidden_downstream_uses`
- `TrustReport` tier (when decision-grade)

No orphan explanations. See [LLM Explanation Contract Plan 001](LLM_EXPLANATION_CONTRACT_PLAN_001.md) (when merged) and answerability plan §11.

**Future contract:** `MIP_LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001`.

---

## 19. Failure recovery requirements

On tool failure, registry miss, or answerability block:

1. Return structured failure (future: extend `AgentFailurePacket`)
2. Preserve `blocked_claims` and `forbidden_response_scope`
3. Surface safe fallback message from answerability decision
4. Never hallucinate missing tool outputs
5. Suggest allowed next steps from report `recommended_next_steps` only

Answerability eval fixtures include tool-unavailable and blocked-claim cases. Recovery is a **control-plane module**, not a separate agent.

---

## 20. Traceability / AgentRunManifest requirement

Every control-plane interaction that invokes tools or produces user-facing output must produce trace artifacts:

- `AgentRunManifest` (P8b — existing contract)
- `AgentStepManifest` per tool/report invocation
- `AgentFailurePacket` on failure
- `AgentValidationReport` before LLM explanation display (future)

**Future contract:** `MIP_AGENT_RUN_MANIFEST_AND_TRACE_CONTRACT_001`.

---

## 21. Claim-boundary principles

1. Claim type → required evidence → compare to available artifacts/tools → one answerability state.
2. Blocked claim boundaries override tool availability.
3. Governance status on reports caps explanation scope.
4. Advisory/diagnostic evidence cannot be promoted to decision evidence in LLM prose.
5. Numeric ROI/lift/MDE/optimizer values require certified source artifacts.
6. No per-question hardcoding — structured inputs only (see answerability plan §10).

---

## 22. Negative risks and mitigations

| Risk | Mitigation |
|------|------------|
| LLM as oracle (invents ROI/lift) | Answerability gate + claim boundaries + response validator |
| LLM reclassifies answerability | State is input to explanation request, not output |
| Duplicate MMM/GeoX agents | Shared control plane + package adapters |
| Auto-run overreach | Low-risk registry flag + preconditions + answerability check |
| Session state drift | Explicit structured facts only; user-editable |
| Orphan explanations | Require source report IDs / artifact IDs |
| Package roadmap conflict | This doc defers package execution; MIP owns routing/governance only |

---

## 23. Compatibility with completed GeoX/panel_exp work

**No rollback.** The following are compatible with LLM-first deterministic-core:

- `GEO_KPI_SPEND_DATA_PROFILER_001` — low-risk auto-run diagnostic
- `GEO_UNIT_AND_MARKET_FEASIBILITY_DIAGNOSTICS_001` — low-risk auto-run diagnostic
- `PANEL_EXP_GOLDEN_PATH_ACCEPTANCE_TESTS_001` — golden paths + provisional boundaries
- Ballpark provisional-only behavior inside profiler/golden paths
- Answerability/recovery concepts in panel_exp roadmap (`ea9178a`)

MIP exposes these through future GeoX tool adapters; panel_exp retains execution ownership.

---

## 24. Compatibility with MMM package roadmap

**No rollback** of MMM deterministic/contracts work. MMM continues:

- deterministic MMM contracts / diagnostics / report builders per existing roadmap
- Δμ / DecisionSurface production in MMM repo
- calibration and promotion gates

MIP control plane later exposes MMM tools/reports through **MMM-specific adapters**. MMM does not build a parallel LLM agent stack.

---

## 25. Active roadmap after this architecture

### MIP-level (control plane contracts — docs/code, no runtime yet)

| Order | Artifact |
|-------|----------|
| 1 | `MIP_TOOL_REGISTRY_AND_CAPABILITY_METADATA_CONTRACT_001` |
| 2 | `MIP_AGENT_ANSWERABILITY_AND_RECOVERY_CONTRACT_001` |
| 3 | `MIP_AGENT_RUN_MANIFEST_AND_TRACE_CONTRACT_001` |
| 4 | `MIP_LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001` |
| 5 | `MIP_SESSION_STATE_AND_ASSUMPTION_CONTRACT_001` |
| 6 | `MIP_REPORT_INVOCATION_CONTRACT_001` |
| 7 | `MIP_WORKFLOW_ORCHESTRATION_CONTRACT_001` |

Plus in-flight: LLM explanation request/response contracts (see answerability plan sequencing).

### Package-level (package-owned execution)

**GeoX/panel_exp:**

- `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` ← **recommended next**
- `SPEND_CONTRAST_AND_BUDGET_REALLOCATION_DIAGNOSTICS_001`
- `PORTFOLIO_TEST_TIERING_ENGINE_001`
- `CANDIDATE_DESIGN_GENERATOR_001`
- `SHARED_CONTROL_AND_MULTICELL_INFERENCE_CONTRACT_001`
- `DESIGN_BASED_INFERENCE_TOOLING_CONTRACT_001`
- `DESIGN_BASED_INFERENCE_FAST_PATH_001`

**MMM:**

- Continue deterministic MMM contracts/diagnostics/report builders
- Expose typed tools/reports through MIP adapters later

---

## 26. Deferred roadmap after this architecture

| Item | Status |
|------|--------|
| `BALLPARK_FEASIBILITY_MODE_CONTRACT_001` (standalone) | Deferred unless distinct user-facing workflow |
| Design Feasibility Interpreter Agent | Collapsed into control plane |
| Method Selection Guard Agent | Collapsed into control plane |
| Randomization Assignment Guard Agent | Collapsed into authorization policy |
| Experiment Readout QA Agent | Collapsed into validators + explanation |
| Research Scout Agent | Deferred |
| MLOps Agent | Deferred |
| Feature Store Agent | Deferred |
| Privacy/Security Agent | Deferred |
| LLM provider/BYOK runtime | Blocked until explanation validator exists |
| Production chat agent | Blocked until full contract stack |

---

## 27. Explicit non-goals

This artifact does **not**:

- implement runtime LLM agents or provider calls
- implement tool registry runtime or workflow orchestration
- change MMM or GeoX/panel_exp execution code
- change deterministic report builder behavior
- add FastAPI routes, Streamlit behavior, or notebooks
- grant production authorization or LLM decisioning authority
- roll back completed deterministic GeoX/MMM work
- activate standalone ballpark contract

---

## 28. Recommended next MIP-level artifacts

1. `MIP_TOOL_REGISTRY_AND_CAPABILITY_METADATA_CONTRACT_001`
2. `MIP_AGENT_ANSWERABILITY_AND_RECOVERY_CONTRACT_001`
3. `MIP_AGENT_RUN_MANIFEST_AND_TRACE_CONTRACT_001`
4. `MIP_LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001`
5. `MIP_SESSION_STATE_AND_ASSUMPTION_CONTRACT_001`
6. `MIP_REPORT_INVOCATION_CONTRACT_001`
7. `MIP_WORKFLOW_ORCHESTRATION_CONTRACT_001`

---

## 29. Recommended next package-level artifacts

**GeoX/panel_exp:** `SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001`

**MMM:** continue deterministic contracts/diagnostics/report builders; prepare adapter surface for MIP tool registry.

---

## 30. LLM control-plane eval strategy

LLM-first interface without a defined eval strategy is **incomplete architecture**. This artifact defines the **MIP-level LLM eval strategy** required to validate the control plane before any runtime LLM/provider layer is trusted.

**Scope of this section:** strategy and acceptance criteria only. **No** live LLM/provider eval implementation in this artifact.

### Why eval strategy belongs in MIP (not panel_exp)

| Eval class | Owner |
|------------|-------|
| MIP control-plane routing, answerability, claim boundaries, explanation faithfulness | **MIP** |
| GeoX spend-contrast feasibility tooling correctness | **panel_exp** (package execution) |
| MMM model/diagnostic/report builder correctness | **MMM** (package execution) |

`SPEND_CONTRAST_FEASIBILITY_TOOLING_CONTRACT_001` and other package contracts validate **deterministic tool outputs**. They do **not** substitute for MIP-level LLM control-plane evals.

### Eval layers (must remain distinct)

| Layer | Purpose | Status |
|-------|---------|--------|
| **Architecture eval requirements** | Define dimensions, acceptance criteria, gates | This artifact |
| **Deterministic eval fixtures** | Typed inputs → expected answerability/routing/claim decisions (no LLM) | Partial — `agent_capability_eval` (answerability only) |
| **LLM/provider eval harnesses** | Canned or live responses validated against contracts | Future — blocked until explanation contracts exist |
| **CI-safe mock evals** | Deterministic fixtures + mocked LLM responses; no provider keys | Future — required before CI enables LLM paths |
| **Human review / red-team evals** | Adversarial NL, policy drift, cross-package ambiguity | Future — required before production enablement |

**Principle:** answerability eval fixtures test **state routing**, not LLM prose. LLM explanation evals are a **separate harness** that validates generated text against typed requests, claim boundaries, and source artifacts.

---

## 31. Required eval dimensions

The following **14 dimensions** are required before the LLM control plane can be trusted at runtime. Each dimension has deterministic acceptance criteria; implementation is deferred to future contracts and harnesses.

### 1. Intent classification

Detect whether user intent is:

- GeoX planning
- GeoX readout
- MMM modeling
- MMM planning
- MMM calibration
- reporting
- advisory
- data intake
- unsupported request

Evals must be **capability-driven** (structured claim type + package scope), not exact natural-language prompt matching.

### 2. Answerability state classification

Classify whether the request is:

- answerable from registered artifact
- answerable from deterministic tool output
- needs core diagnostic/ML
- needs user input/data
- needs report invocation
- blocked by claim boundary

Maps to `evaluate_agent_answerability()` and `AgentAnswerabilityState`. Partial coverage exists via `examples/fixtures/agent_capability_eval/`.

### 3. Tool routing correctness

- Verify the LLM proposes the correct package/tool route for MMM vs GeoX requests.
- Verify **deterministic registry validation is required** before execution.
- Verify registry rejects out-of-scope, unavailable, or precondition-failing tools.

### 4. Deterministic registry validation compliance

- Verify no tool executes without registry validation.
- Verify `low_risk_auto_run` tools still pass preconditions and answerability.
- Verify high-stakes tools require explicit authorization path.

### 5. Missing-input question quality

- Verify the LLM asks the **smallest necessary** follow-up question.
- Verify it does **not** ask broad questionnaire-style follow-ups when a typed missing field is known.
- Verify missing-input prompts align with `missing_required_inputs` from answerability decisions.

### 6. Claim-boundary preservation

Verify the LLM does **not** claim lift, ROI, power, MDE, p-values, confidence intervals, design feasibility, calibration acceptance, budget optimization, or production readiness unless a deterministic artifact/report explicitly authorizes that claim.

### 7. Grounded explanation faithfulness

- Verify explanations are grounded in typed reports/artifacts.
- Verify explanations do not add unsupported causal/statistical conclusions.
- Verify citations reference `DeterministicReportEnvelope`, `ArtifactReference`, and `AgentAnswerabilityDecision`.

Future contract: `MIP_LLM_REPORT_GROUNDING_AND_CLAIM_BOUNDARY_CONTRACT_001` + `validate_llm_explanation_response()`.

### 8. Report invocation correctness

- Verify the LLM invokes deterministic report builders for official reports.
- Verify the LLM does **not** generate source-of-truth reports itself.
- Verify explanation-only role after builder invocation.

### 9. Session-state assumption correctness

- Verify explicit user-provided assumptions are stored as structured session state.
- Verify inferred assumptions are **not** stored as facts.
- Verify user-editable, auditable distinction between conversation assumptions and tool-derived facts.

### 10. Failure recovery behavior

- Verify typed tool failures lead to bounded recovery actions.
- Verify the LLM does **not** debug by inventing data or relaxing validation.
- Verify `blocked_claims` and `forbidden_response_scope` are preserved on failure.

### 11. Advisory-mode safety

- Verify advisory responses explain package capabilities and data requirements.
- Verify advisory responses do **not** claim feasibility, lift, ROI, power, or production readiness.
- Verify advisory labeling when `governance_status` is advisory/diagnostic only.

### 12. Cross-package routing

- Verify MMM questions route to MMM adapters.
- Verify GeoX questions route to GeoX/panel_exp adapters.
- Verify ambiguous requests ask clarification or present safe alternatives.

### 13. Unsupported causal/statistical claim refusal

- Verify refusal when evidence tier does not support causal or inferential claims.
- Verify no promotion of advisory/diagnostic evidence to decision-grade prose.
- Overlaps with claim-boundary preservation; evals must cover both structured routing and NL surface forms.

### 14. Rule-sprawl resistance

- Verify eval cases are **capability-driven** and **typed-contract-driven**.
- Verify evals are **not** hardcoded to fixture IDs or exact natural-language prompts.
- Verify new scenarios extend fixture schema, not branching `if question contains ...` logic.

---

## 32. Eval fixture strategy

### Current state (deterministic, partial)

| Fixture set | Dimensions covered | Location |
|-------------|-------------------|----------|
| `agent_capability_eval` (10 cases) | Answerability state classification (dim 2); partial claim-boundary (dim 6) | `examples/fixtures/agent_capability_eval/` |

### Required future fixture families (MIP-level)

| Fixture family | Primary dimensions | Notes |
|----------------|-------------------|-------|
| `agent_capability_eval` (extend) | 2, 6, 10, 11 | Structured inputs only; no LLM runtime |
| `llm_intent_routing_eval` | 1, 3, 12 | Typed intent envelopes + expected route |
| `llm_missing_input_eval` | 5 | Known missing field → minimal question contract |
| `llm_explanation_eval` | 6, 7, 13 | Canned `LLMExplanationResponse` + validator |
| `llm_report_invocation_eval` | 8 | Builder invocation records, not NL reports |
| `llm_session_state_eval` | 9 | Explicit vs inferred assumption cases |
| `llm_failure_recovery_eval` | 10 | Typed failure packets → bounded recovery |
| `llm_advisory_safety_eval` | 11 | Advisory-only governance labels |
| `llm_cross_package_routing_eval` | 12 | MMM vs GeoX ambiguity and clarification |

**Future implementation contract:** [MIP_LLM_CONTROL_PLANE_EVALUATION_STRATEGY_001](../evaluation/MIP_LLM_CONTROL_PLANE_EVALUATION_STRATEGY_001.md) defines fixture schemas, loaders, harness sequence, and CI-safe strategy. This architecture artifact defines **what** must be tested; the evaluation strategy artifact defines **how** to test it.

### Fixture design rules

1. Cases are JSON/YAML typed contracts, not prompt transcripts alone.
2. `user_question` fields are documentation metadata; evaluators branch on structured fields only.
3. Forbidden phrases check deterministic scopes, not LLM text, unless running explanation eval harness.
4. Package-specific execution fixtures stay in MMM/panel_exp repos; MIP fixtures test control-plane behavior only.

---

## 33. CI-safe deterministic/mock eval strategy

Before any provider key or live LLM call enters CI:

| Requirement | Rationale |
|-------------|-----------|
| All answerability/routing evals run **without** LLM | Deterministic regression on every PR |
| Explanation evals use **canned responses** | Validate `validate_llm_explanation_response()` without provider |
| Mock LLM adapter returns fixture responses | Test orchestration wiring without network |
| No API keys in CI for control-plane evals | Keys reserved for optional nightly/manual tiers |
| Eval failures block merge on governance dimensions | Same bar as contract/schema tests |

**Acceptance:** CI-safe mock eval suite passes with zero external LLM dependencies. Live provider evals are **optional** and **non-blocking** for default PR CI until explicitly gated.

---

## 34. Human review / red-team eval strategy

Deterministic fixtures cannot cover all natural-language adversarial surfaces. Before production LLM enablement:

| Review type | Focus |
|-------------|-------|
| **Policy red-team** | Claim-boundary bypass, advisory→decision promotion, unsupported causal language |
| **Cross-package ambiguity** | MMM vs GeoX routing under vague prompts |
| **Failure-mode probing** | Tool unavailable, partial data, contradictory session state |
| **Explanation drift** | Grounded explanation faithfulness under paraphrase |
| **Regression sampling** | Periodic human review of production traces (when runtime exists) |

Human review is **required** for production enablement but **not** a substitute for deterministic CI evals. Both gates must pass.

---

## 35. Eval gates before runtime LLM enablement

Runtime LLM/provider calls remain **blocked** until:

| Gate | Requirement |
|------|-------------|
| G1 | `MIP_TOOL_REGISTRY_AND_CAPABILITY_METADATA_CONTRACT_001` defined |
| G2 | Answerability eval fixtures pass (existing + extended) |
| G3 | `LLMExplanationRequest` / `LLMExplanationResponse` contracts + `validate_llm_explanation_response()` |
| G4 | Canned-response explanation eval harness passes in CI |
| G5 | Intent/routing eval fixtures pass (mock LLM, no provider) |
| G6 | Claim-boundary + advisory-safety explanation evals pass |
| G7 | Human review / red-team sign-off on sampled adversarial cases |
| G8 | `AgentRunManifest` trace coverage for control-plane interactions |

**Explicit non-gate:** package-level spend-contrast or GeoX feasibility tooling evals do **not** satisfy G3–G6. Those validate execution tools, not LLM control-plane behavior.

**Status:** G2 partial (answerability only). G1, G3–G8 not met. `runtime_llm_provider_eval_implemented` remains `false`.

---

## 36. Final verdict

**`mip_llm_control_plane_architecture_defined_no_runtime_agents_or_production_authorization`**

MIP adopts **LLM-first interface, deterministic-core execution** through a **shared LLM control plane** with **package-specific tool adapters**. The LLM proposes routes; the deterministic registry and answerability gate validate. Low-risk diagnostics may auto-run when goals are clear. High-stakes actions require authorization. Final reports come from deterministic builders. Advisory mode is bounded. Session assumptions are explicit structured facts only. **A 14-dimension MIP-level LLM eval strategy** (§30–35) defines acceptance criteria before runtime LLM enablement; implementation of eval fixtures and harnesses is deferred. Redundant package-side agents and standalone ballpark contract are deferred. Completed GeoX profiler/feasibility/golden-path work and MMM deterministic contracts are preserved and aligned — not rolled back.

---

## References

- [MIP LLM Control Plane Evaluation Strategy 001](../evaluation/MIP_LLM_CONTROL_PLANE_EVALUATION_STRATEGY_001.md)
- [Agent Answerability and Fallback Contract Plan 001](AGENT_ANSWERABILITY_AND_FALLBACK_CONTRACT_PLAN_001.md)
- [MIP Report, Adapter, and Agent Contract Plan 001](MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md)
- [ORCHESTRATION_BOUNDARIES.md](ORCHESTRATION_BOUNDARIES.md)
- [TRUST_ARCHITECTURE.md](TRUST_ARCHITECTURE.md)
- [REPO_INTEGRATION_STRATEGY.md](REPO_INTEGRATION_STRATEGY.md)
- [ADR-003: LLM Orchestration Over Certified Tools](../adr/ADR-003-llm-orchestration-over-certified-tools.md)
- `mip.contracts.agent_answerability` — implemented answerability gate
- `mip.evaluation.agent_capability_fixtures` — answerability eval regression
- `examples/fixtures/agent_capability_eval/` — 10 eval cases
