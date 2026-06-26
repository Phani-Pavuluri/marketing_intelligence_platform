# LLM Explanation Contract Plan 001

## 1. Title and status

| Field | Value |
|-------|-------|
| **Title** | LLM Explanation Contract Plan 001 |
| **Status** | Accepted contract planning direction |
| **Type** | LLM explanation / answerability preservation / deterministic report explanation plan |
| **Base commit** | `000273a` — Agent capability eval fixtures merged (PR #44) |
| **Date** | 2026-05-28 |
| **Scope** | Docs/contract planning only — **no LLM runtime, providers, or generated explanations in this phase** |

**Hard boundaries (unchanged):** No MMM/GeoX execution, no LLM provider calls, no production prompt templates, no agent runtime, no new FastAPI routes, no Streamlit behavior changes, no notebooks, no unsupported causal/ROI/optimizer claims. MIP remains the **control plane**, not the statistical engine.

**Prerequisites (merged):**

- [Agent Answerability and Fallback Contract Plan 001](AGENT_ANSWERABILITY_AND_FALLBACK_CONTRACT_PLAN_001.md) — five-state `AgentAnswerabilityState` machine + deterministic evaluator
- `examples/fixtures/agent_capability_eval/` — 10 file-backed answerability eval cases
- `mip.contracts.deterministic_report` — `DeterministicReportEnvelope`, `deterministic_report_v1`
- P7b `LLMExplanationRequest` / `LLMExplanationPlan` in `mip.contracts.llm_provider` (provider-governance layer; superseded for report explanation by contracts in this plan)

---

## 2. Problem statement

Future LLM layers must make MIP easier to understand without becoming a source of measurement truth.

Users will ask natural-language questions. The product must respond in plain language while preserving governed evidence boundaries. If the LLM is allowed to improvise, MIP will appear to certify claims it never measured.

Two failure modes to prevent:

| Failure mode | Symptom | Root cause |
|--------------|---------|------------|
| **LLM as oracle** | Model invents ROI, causal lift, optimizer mix, matched markets, or MDE from advisory/demo context | No typed explanation contract bound to `AgentAnswerabilityDecision` and `DeterministicReportEnvelope` |
| **LLM as gatekeeper** | Model reclassifies answerability, upgrades governance, or softens blocked claims in prose | LLM allowed to alter `AgentAnswerabilityState` or `governance_status` |

The LLM may **explain** deterministic reports and answerability decisions. It must **not**:

- decide answerability
- invent missing facts
- create new measurement outputs
- override blocked/governance states
- turn advisory/demo evidence into causal or decision evidence

---

## 3. Core principle

**LLM explains; deterministic contracts decide.**

```text
User question
  → deterministic answerability evaluator → AgentAnswerabilityDecision
  → (if answerable) load DeterministicReportEnvelope / artifact refs
  → LLMExplanationRequest (state + sources are inputs)
  → LLM generates LLMExplanationResponse (explanation only)
  → validate_llm_explanation_response(...) before display
```

The LLM **consumes**:

| Input | Role |
|-------|------|
| `AgentAnswerabilityDecision` | Authoritative routing state — **input, not output** |
| `DeterministicReportEnvelope` | Authoritative structured content for explanation |
| Registered artifact/report references | Provenance and citation targets |
| `allowed_downstream_uses` / `forbidden_downstream_uses` | Response scope caps |
| `blocked_claims` | Claims that must not appear as conclusions |
| `missing_inputs` | Missing-data checklist for state 4 responses |

The LLM does **not** consume raw fixture JSON directly when a `DeterministicReportEnvelope` exists. Fixtures are upstream of report builders; explanations cite reports and decisions.

---

## 4. LLM explanation request contract

### Future contract: `LLMExplanationRequest` (report-explanation v1)

**Module (future):** `src/mip/contracts/llm_explanation.py` — **not implemented in this plan**.

This contract is **distinct from** P7b `mip.contracts.llm_provider.LLMExplanationRequest`, which plans provider-governed explanation at the intake layer. Report-explanation v1 binds explicitly to answerability decisions and deterministic reports.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `request_id` | `str` | yes | Stable unique ID |
| `answerability_decision` | `AgentAnswerabilityDecision` | yes | **Input** — evaluator output; LLM must not recalculate |
| `source_report_ids` | `list[str]` | yes* | `DeterministicReportEnvelope.report_id` values |
| `source_artifact_ids` | `list[str]` | yes* | `ArtifactReference.artifact_id` values |
| `source_reports` | `list[DeterministicReportEnvelope]` | no | Full envelopes when available for citation |
| `user_question` | `str` | yes | Original user question (metadata for tone/audience only) |
| `requested_explanation_style` | `str` | no | e.g. `plain_language`, `technical_summary` |
| `audience_level` | `str` | no | e.g. `executive`, `analyst`, `operator` |
| `allowed_response_scope` | `list[str]` | yes | Copied from decision and/or report |
| `forbidden_response_scope` | `list[str]` | yes | Copied from decision and/or report |
| `required_citations` | `list[str]` | yes | Report fields or artifact IDs that must be cited |
| `missing_inputs` | `list[str]` | no | From decision — drives missing-data explanations |
| `blocked_claims` | `list[str]` | yes | From decision and/or report |

\* **At least one** of the following must be present:

1. Non-empty `source_report_ids` and/or `source_reports`
2. Non-empty `source_artifact_ids`
3. `answerability_decision` explaining why no report exists (states 3–5)

### Request rules

1. `answerability_decision.state` is **input**, not output — LLM must not recalculate or alter answerability state.
2. `allowed_response_scope` and `forbidden_response_scope` are copied from the decision and/or source reports; LLM cannot expand scope.
3. `blocked_claims` must be forwarded to the response validator.
4. When `answerability_decision.state` is `ANSWERABLE_FROM_REGISTERED_ARTIFACT` or `ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT`, request must include at least one `source_report_id`.
5. `user_question` informs explanation style only — it does not override claim taxonomy or evidence level.

---

## 5. LLM explanation response contract

### Future contract: `LLMExplanationResponse`

**Module (future):** `src/mip/contracts/llm_explanation.py` — **not implemented in this plan**.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `response_id` | `str` | yes | Stable unique ID |
| `request_id` | `str` | yes | Links to `LLMExplanationRequest.request_id` |
| `schema_version` | `str` | yes | e.g. `llm_explanation_response_v1` |
| `preserved_answerability_state` | `AgentAnswerabilityState` | yes | Must equal request decision state |
| `preserved_governance_status` | `list[str]` | yes | Governance labels from source report(s); no upgrade |
| `summary` | `str` | yes | Short explanation (1–3 sentences) |
| `plain_language_explanation` | `str` | yes | Business-language narrative |
| `allowed_interpretations` | `list[str]` | yes | What reader may conclude |
| `blocked_interpretations` | `list[str]` | yes | What reader must not conclude |
| `missing_data_explanation` | `str` | no | Required when state is `NEEDS_USER_INPUT_OR_DATA` |
| `recommended_next_steps` | `list[str]` | yes | From source report `recommended_next_steps` and/or decision fallback only |
| `citations_to_report_fields` | `list[str]` | yes | e.g. `summary`, `findings`, `missing_data`, `blocked_claims` |
| `citations_to_artifact_ids` | `list[str]` | yes | Provenance artifact IDs cited |
| `unsupported_claims_detected` | `list[str]` | yes | Claims flagged during validation (empty if clean) |
| `safety_footer` | `str` | yes | e.g. "This explanation does not create measurement authority." |

### Required response behavior

1. **Preserve** `answerability_decision.state` in `preserved_answerability_state` — validator fails on mismatch.
2. **Preserve** `governance_status` from each source report — no upgrade from `advisory_only` to `candidate` or certified labels.
3. **Preserve** `blocked_claims` and `forbidden_downstream_uses` — response must not contradict them.
4. **Cite** source report IDs and/or artifact IDs in `citations_to_*` fields.
5. **Never add** new unsupported measurement claims (ROI, lift, optimizer output, etc.) unless explicitly framed as blocked in `blocked_interpretations`.

---

## 6. Explanation modes

Explanation mode is derived from `AgentAnswerabilityState` — not a parallel taxonomy.

| `AgentAnswerabilityState` | Explanation mode | LLM explains |
|---------------------------|------------------|--------------|
| `ANSWERABLE_FROM_REGISTERED_ARTIFACT` | `explain_registered_report` | Existing report/artifact fields within allowed downstream uses |
| `ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT` | `explain_deterministic_tool_output` | Generated deterministic report or tool output envelope |
| `NEEDS_CORE_DIAGNOSTIC_OR_ML` | `explain_core_ml_requirement` | Why MMM/GeoX/DecisionSurface is required; what inputs/outputs are needed |
| `NEEDS_USER_INPUT_OR_DATA` | `explain_missing_data` | Missing-data checklist from decision and/or report |
| `BLOCKED_BY_CLAIM_BOUNDARY` | `explain_governance_boundary` | Why claim is blocked; safe alternatives from `recommended_next_steps` |

Secondary mapping from `AgentAnswerMode` (from answerability decision) may refine tone but must not change state.

---

## 7. Allowed LLM behavior

| Category | Allowed |
|----------|---------|
| Report content | Explain `summary`, `findings`, `missing_data`, `recommended_next_steps`, `workflow_payload` fields present in source report |
| Translation | Convert technical terms to plain language without changing meaning |
| Evidence framing | Explain why evidence is advisory, diagnostic, candidate, or blocked |
| Missing data | List missing fields from report `missing_data` and decision `missing_inputs` |
| Safe routing | Explain why core MMM/GeoX/DecisionSurface is needed using decision `required_core_engine` |
| Governance | Explain why a claim is blocked using `blocked_claims` and `forbidden_downstream_uses` |
| Next steps | Suggest steps already present in report `recommended_next_steps` or decision `fallback_message` patterns |

---

## 8. Blocked LLM behavior

| Category | Blocked |
|----------|---------|
| Measurement claims | Create causal lift, ROI, channel contribution, response curves |
| Optimization | Create budget recommendations, optimizer outputs, scenario plans |
| GeoX design | Choose matched markets, assign treatment/control units |
| Diagnostics | Calculate power/MDE |
| Governance override | Upgrade `governance_status`; downgrade or remove `blocked_claims` |
| Evidence promotion | Convert advisory/diagnostic evidence into decision or production evidence |
| Fabrication | Invent missing SE/uncertainty; fill null fields; infer facts not in source |
| Provenance | Cite nonexistent artifacts or report IDs |
| Readiness claims | Claim production readiness or certified measurement without certified source |
| Answerability | Reclassify or override `AgentAnswerabilityState` |

Reuse `FORBIDDEN_LLM_OUTPUT_CLAIM_TYPES` and `default_forbidden_claim_topics()` from `mip.contracts.llm_provider` in validators.

---

## 9. Citation and provenance requirements

Every explanation must satisfy:

1. **At least one citation** to a source report field or artifact ID.
2. **Report field citations** should reference conceptual sections:
   - `summary`
   - `findings`
   - `missing_data`
   - `blocked_claims`
   - `allowed_downstream_uses`
   - `forbidden_downstream_uses`
   - `workflow_payload` (when explaining structured content)
3. **Artifact citations** use `ArtifactReference.artifact_id` from `source_input_ref` or `artifact_refs`.
4. **No report case:** when state is 3–5 and no report exists, explanation must cite `AgentAnswerabilityDecision` fields (`state`, `fallback_message`, `blocked_claims`, `missing_inputs`).
5. **Orphan explanations forbidden:** `ANSWERABLE_FROM_*` states require non-empty `citations_to_report_fields` or `citations_to_artifact_ids`.

---

## 10. Response validation plan

### Future function: `validate_llm_explanation_response(...)`

**Module (future):** `src/mip/llm/explanation_validation.py` — **not implemented in this plan**.

Deterministic validation runs **before** any LLM response is shown to users.

| Check | Rule |
|-------|------|
| State preservation | `response.preserved_answerability_state == request.answerability_decision.state` |
| Governance preservation | No upgrade in `preserved_governance_status` vs source reports |
| Citations | Required citations present for answerable states |
| Blocked claims | Response text does not contradict `blocked_claims` |
| Forbidden scope | Response does not violate `forbidden_response_scope` |
| Unsupported terms | Forbidden claim fragments absent unless in `blocked_interpretations` |
| Numeric claims | No ROI/lift/MDE/optimizer numeric values unless present in certified source artifact |
| Safety footer | Non-empty `safety_footer` |

Validation returns a structured pass/fail report (future: `LLMExplanationValidationReport`). Failed validation blocks display and returns decision fallback message instead.

**No LLM in validator.** Validation is regex/contract-based only.

---

## 11. Relationship to agent capability eval fixtures

| Eval layer | Tests | Scope |
|------------|-------|-------|
| **Answerability eval fixtures** (`examples/fixtures/agent_capability_eval/`) | State routing | `evaluate_agent_answerability` → expected `AgentAnswerabilityState` |
| **LLM explanation evals** (future) | Explanation quality + safety | Canned `LLMExplanationResponse` → validator pass/fail |

**Keep separate.** Answerability evals prove the evaluator routes correctly. Explanation evals prove the LLM (or canned responses) preserve state and do not add claims.

Future explanation eval cases should test:

- Explanation preserves `AgentAnswerabilityState`
- Explanation does not add unsupported claims
- Explanation cites source report/artifact IDs
- Blocked/missing/core-ML cases produce safe fallback narratives
- Advisory-only reports never produce ROI/causal language in `allowed_interpretations`

Do **not** merge answerability state evals and explanation-quality evals into one harness in v1.

---

## 12. Future implementation sequence

| Order | Item | Type |
|-------|------|------|
| 1 | **This contract plan** | Docs ✓ |
| 2 | `LLMExplanationRequest` / `LLMExplanationResponse` typed contracts (report-explanation v1) | Code |
| 3 | `validate_llm_explanation_response(...)` deterministic validator | Code |
| 4 | Fixture-based explanation validation tests using **canned responses** | Tests |
| 5 | Provider/BYOK/runtime planning (separate plan) | Docs |
| 6 | LLM implementation over deterministic reports only | Code |
| 7 | Agent runtime / tool registry (P17) | Code — later |

**Explicit blocks:**

- LLM runtime before typed explanation contracts + validator
- Provider calls before canned-response validation passes
- Free-form explanations without `AgentAnswerabilityDecision` + source reports
- Merging answerability evals with explanation evals

---

## 13. Stop/go criteria

### Safe now

- [x] Docs/contract planning (this document)
- [ ] Typed `LLMExplanationRequest` / `LLMExplanationResponse` contracts (report-explanation v1)
- [ ] Deterministic `validate_llm_explanation_response(...)`
- [ ] Canned-response explanation validation tests

### Needs more detail before implementation

- Production prompt templates and tone guidelines
- Provider abstraction and BYOK configuration
- Chat UI binding and streaming behavior
- Provider-specific error handling and retry policy

### Blocked

- Free-form LLM explanations without source reports/decisions
- Direct LLM access to raw fixtures/tools without answerability gate
- LLM deciding or altering `AgentAnswerabilityState`
- Provider runtime calls (`OpenAI`, `Anthropic`, `Ollama`, BYOK)
- Production chat agent without explanation validator
- Generated explanations stored without provenance

---

## References

- [Agent Answerability and Fallback Contract Plan 001](AGENT_ANSWERABILITY_AND_FALLBACK_CONTRACT_PLAN_001.md)
- [MIP Report, Adapter, and Agent Contract Plan 001](MIP_REPORT_ADAPTER_AGENT_CONTRACT_PLAN_001.md) — §8 LLM explanation boundary
- `mip.contracts.agent_answerability` — `AgentAnswerabilityDecision`, five-state machine
- `mip.contracts.deterministic_report` — `DeterministicReportEnvelope`
- `mip.contracts.llm_provider` — P7b provider-governance contracts (distinct layer)
- `mip.evaluation.agent_capability_fixtures` — answerability eval fixtures
- `examples/fixtures/agent_capability_eval/` — 10 regression cases
