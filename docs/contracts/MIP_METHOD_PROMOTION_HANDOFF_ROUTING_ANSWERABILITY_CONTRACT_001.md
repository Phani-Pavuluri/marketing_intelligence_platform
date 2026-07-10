# MIP Method Promotion Handoff Routing Answerability Contract 001

## 1. Metadata

| Field | Value |
|-------|-------|
| **artifact_id** | `MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_CONTRACT_001` |
| **artifact_type** | `mip_method_promotion_handoff_routing_answerability_contract` |
| **status** | `completed` |
| **scope** | `routing_answerability_contract_docs_tests_only_no_runtime_integration_no_answer_eligibility` |
| **depends_on** | `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_APPLICATION_CHECKPOINT_001`, `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001` |
| **final_verdict** | `routing_answerability_contract_defined_governance_context_only_no_integration` |
| **recommended_next** | `MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_CONTRACT_001` |

**Dependency chain:**

1. `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001`
2. `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001`
3. `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001`
4. `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_APPLICATION_CHECKPOINT_001`
5. **this contract**

Checkpoint decision consumed: `PROCEED_TO_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_CONTRACT_NOT_INTEGRATION`

`contract_defined` = true

---

## 2. Why this contract exists

MIP now has a validator/normalizer (`mip.contracts.method_promotion_handoff_consumer`) that creates safe method-promotion governance records (`MIPMethodPromotionHandoffConsumerRecord`).

The next dangerous boundary is **routing/answerability**: a displayable governance record must not be upgraded into answer eligibility, recommendations, DecisionSurface construction, TrustReport bypass, RecommendationContract generation, planning advice, spend/ROI/budget action, claim/catalog/production authorization, or method/instrument promotion.

This contract defines where those records may be used without allowing those upgrades. It prevents LLM/orchestration from treating “governance context is displayable” as “MIP can answer a planning/reallocation question.”

---

## 3. Consumed object

Consumed object: **`MIPMethodPromotionHandoffConsumerRecord`**

(Plus runtime-output flags when available from `MIPMethodPromotionHandoffConsumerRuntimeOutput`.)

### Fields used by routing/answerability

- `consumer_status`
- `routing_hint`
- `accepted_for_governance_context` (runtime output)
- `rejected_for_decisioning` (runtime output)
- `profile_id`
- `canonical_identity`
- `decision_scope`
- `generic_decision_status`
- `source_of_truth_refs`
- `blockers`
- `warnings`
- `prohibited_actions`
- `boundary_statuses`
- `consumer_allowed_actions`
- `consumer_blocked_actions`
- all fixed non-authorization statuses (`NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF`, `NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF`, `NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF`)
- `lineage`

`consumed_object_defined` = true

---

## 4. Allowed routing uses

MIP routing may use the record for:

- `governance_context_display`
- `diagnostic_explanation`
- `method_review_lineage_display`
- `profile_identity_display`
- `decision_scope_display`
- `blocker_warning_display`
- `unsupported_recommendation_block`
- `route_to_separate_catalog_review`
- `route_to_separate_claim_authorization_review`
- `route_to_separate_production_compatibility_review`
- `human_review_context`

`allowed_routing_uses_defined` = true

---

## 5. Blocked routing uses

MIP routing must **not** use the record for:

- `planning_answer_eligibility`
- `recommendation_answer_eligibility`
- `budget_optimization_answer_eligibility`
- `spend_reallocation_answer_eligibility`
- ROI/ROAS recommendation
- DecisionSurface construction
- DecisionSurface approval
- TrustReport bypass
- RecommendationContract generation
- production readout
- catalog unblock
- claim authorization
- method/instrument promotion
- CalibrationSignal creation
- ExperimentEvidence creation
- raw evidence scoring
- source package override
- LLM claim authorization

`blocked_routing_uses_defined` = true

---

## 6. Answerability semantics

If a user asks:

- “Can I use this method?”
- “Can I reallocate spend?”
- “Can this support planning?”
- “Can we recommend budget changes?”
- “Is this production-ready?”
- “Can I claim lift/significance/ROI?”

Then this handoff record **alone** must result in:

- blocked/deferred answer
- explanation that method-promotion handoff is **governance context only**
- routing to an appropriate separate review lane if available

It must **not** result in:

- allowed planning answer
- recommendation
- DecisionSurface
- TrustReport bypass
- RecommendationContract
- lift/ROI/statistical claim

`APPROVE_REVIEW_CONTINUATION` on the record is **not** answer eligibility.

`answerability_semantics_defined` = true  
`handoff_governance_context_only` = true  
`approve_review_continuation_not_answer_eligibility` = true

---

## 7. Safe answer modes

### Allowed answer modes

- `explain_governance_context`
- `explain_method_review_scope`
- `explain_blockers_and_warnings`
- `explain_non_authorization_status`
- `defer_to_catalog_review`
- `defer_to_claim_authorization_review`
- `defer_to_production_compatibility_review`
- `block_unsupported_recommendation`

### Blocked answer modes

- `answer_with_recommendation`
- `answer_with_budget_reallocation`
- `answer_with_roi_roas_claim`
- `answer_with_causal_lift_claim`
- `answer_with_statistical_significance_claim`
- `answer_with_production_readout`
- `answer_with_decision_surface`
- `answer_with_recommendation_contract`

`safe_answer_modes_defined` = true  
`blocked_answer_modes_defined` = true

---

## 8. Routing/answerability statuses

Conceptual statuses:

- `METHOD_PROMOTION_HANDOFF_ROUTING_CONTEXT_AVAILABLE`
- `METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISIONING`
- `METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_PLANNING_RECOMMENDATION`
- `METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISION_SURFACE`
- `METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_TRUST_BYPASS`
- `METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_RECOMMENDATION_CONTRACT`
- `METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CLAIM_AUTHORIZATION`
- `METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CATALOG_PRODUCTION`
- `METHOD_PROMOTION_HANDOFF_ROUTING_DEFER_TO_SEPARATE_REVIEW_LANE`

`routing_answerability_statuses_defined` = true

---

## 9. LLM orchestration guardrails

### LLM/orchestration may

- summarize governance context
- mention profile identity/scope
- explain why recommendation is blocked
- list missing evidence/blockers/warnings
- direct user to separate review lane

### LLM/orchestration must not

- reinterpret `APPROVE_REVIEW_CONTINUATION` as approval
- infer production readiness
- infer causal/statistical validity
- produce spend/budget/ROI recommendations
- bypass deterministic gates
- synthesize missing authorization
- convert governance context into RecommendationContract or DecisionSurface

`llm_orchestration_guardrails_defined` = true

---

## 10. Relationship to existing gates

- DecisionSurface gate remains separate.
- TrustReport gate remains separate.
- RecommendationContract gate remains separate.
- Planning answer eligibility remains separate.
- Claim/catalog/production gates remain separate.
- CalibrationSignal and ExperimentEvidence are not created by this path.
- This path is governance-context-only.

`relationship_to_existing_gates_defined` = true  
`decision_surface_remains_separately_gated` = true  
`trust_report_remains_separately_required` = true  
`recommendation_contract_remains_separately_gated` = true  
`planning_answer_eligibility_remains_separate` = true  
`claim_catalog_production_readiness_remain_separate` = true

---

## 11. Runtime implementation stance

This artifact is **contract-only**.

Routing/answerability runtime integration is deferred.

Before runtime integration:

- define a typed routing/answerability runtime contract (or implement narrowly only if current MIP patterns already support direct runtime after that contract)
- tests must prove governance records cannot produce recommendations or DecisionSurface eligibility
- LLM answer layer must receive explicit can-say / cannot-say boundaries

`runtime_integration_deferred` = true

---

## 12. Recommended next artifact

**`MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_CONTRACT_001`**

Scope:

- define typed runtime contract for routing/answerability consumption
- no runtime implementation yet
- no LLM integration
- no answer eligibility
- no DecisionSurface
- no TrustReport bypass
- no RecommendationContract
- no planning/spend/ROI authorization

---

## 13. Non-goals

- no routing runtime implemented
- no answer eligibility integration implemented
- no LLM orchestration integration implemented
- no DecisionSurface authorized
- no TrustReport bypass
- no RecommendationContract authorized
- no planning recommendation enabled
- no planning answer eligibility enabled
- no budget optimization enabled
- no spend movement authorized
- no ROI/ROAS authorized
- no method promoted
- no instrument promoted
- no catalog unblock
- no production compatibility authorization
- no claim authorization
- no causal/business lift claim
- no statistical claim
- no CalibrationSignal created
- no ExperimentEvidence created
- no raw evidence scoring
- no package source-of-truth override

---

## 14. Validation results

- `python -m json.tool docs/contracts/archives/MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_CONTRACT_001_summary.json`
- `git diff --check`
- `python -m pytest tests/contracts/test_mip_method_promotion_handoff_routing_answerability_contract_001.py -q`
- `python -m pytest -q`
- Safety grep: no forbidden runtime/integration/authorization `*.true` flags
- Capability grep: contract / routing / answerability / LLM guardrail / deferred flags present
