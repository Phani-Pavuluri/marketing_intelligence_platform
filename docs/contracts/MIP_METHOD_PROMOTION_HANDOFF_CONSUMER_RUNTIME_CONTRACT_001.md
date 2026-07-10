# MIP Method Promotion Handoff Consumer Runtime Contract 001

## 1. Metadata

| Field | Value |
|-------|-------|
| **artifact_id** | `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001` |
| **artifact_type** | `mip_method_promotion_handoff_consumer_runtime_contract` |
| **status** | `completed` |
| **scope** | `mip_side_runtime_contract_docs_tests_only_no_runtime_implementation_no_decision_authorization` |
| **depends_on** | `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001` |
| **upstream_package_artifact** | `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001` |
| **upstream_package_commit** | `42f4484` |
| **upstream_package_source** | `panel_exp` |
| **final_verdict** | `mip_consumer_runtime_contract_defined_no_runtime_no_decision_authorization` |
| **recommended_next** | `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001` |

**Related MIP governance (consume, do not bypass):**

- `DecisionSurface` — remains separately gated
- `TrustReport` — remains separately required
- `RecommendationContract` — remains separately gated
- Planning answer eligibility — remains separately gated

---

## 2. Why this runtime contract exists

MIP has a consumer contract (`MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001`) defining how MIP may consume package-side `MethodPromotionGenericAdapterMIPHandoff` as governance context. There is still **no runtime contract** and **no runtime implementation**.

Before runtime implementation, MIP needs typed validation and normalization semantics:

- what a future runtime may accept
- what it must validate
- how it normalizes into `MIPMethodPromotionHandoffConsumerRecord`
- which statuses and routing hints are allowed
- which decisioning paths remain blocked

The future runtime’s job is to **validate and normalize governance context**, not authorize decisions.

This artifact is **docs/tests only**. It does not implement runtime code, create a runtime adapter, construct DecisionSurface, bypass TrustReport, generate RecommendationContract, or enable planning answer eligibility.

`runtime_contract_defined` = true

---

## 3. Runtime contract boundary

### Future runtime may

- accept a package-side `MethodPromotionGenericAdapterMIPHandoff`-like payload
- validate required fields
- validate fixed non-authorization statuses
- validate allowed/blocked actions
- validate source-of-truth refs
- normalize into `MIPMethodPromotionHandoffConsumerRecord`
- emit safe consumer status
- emit safe routing hint
- preserve lineage

### Future runtime must not

- construct DecisionSurface
- approve DecisionSurface
- bypass TrustReport
- generate RecommendationContract
- enable planning answer eligibility
- authorize budget optimization
- authorize spend movement
- authorize ROI/ROAS
- authorize claim/catalog/production readiness
- promote method/instrument
- repair missing evidence
- score raw evidence quality
- override package source runtimes

---

## 4. Runtime input contract

Conceptual input: **`MIPMethodPromotionHandoffConsumerRuntimeInput`**

| Field | Role |
|-------|------|
| `raw_handoff_payload` | Package-side handoff payload (required) |
| `ingestion_context` | MIP ingestion context metadata |
| `received_at` | Ingestion timestamp |
| `source_package_expected` | Always `panel_exp` |
| `upstream_artifact_expected` | Optional expected upstream artifact id |
| `strict_validation` | Default `true` |
| `lineage_context` | Optional lineage enrichment |

### Input validation

- `raw_handoff_payload` required
- source package must be `panel_exp`
- strict validation default `true`
- no defaulting into authorization

`runtime_input_contract_defined` = true

---

## 5. Runtime output contract

Conceptual output: **`MIPMethodPromotionHandoffConsumerRuntimeOutput`**

| Field | Role |
|-------|------|
| `consumer_record` | Normalized `MIPMethodPromotionHandoffConsumerRecord` or blocked stub |
| `consumer_status` | Runtime consumer status (section 9) |
| `validation_errors` | Blocking validation errors |
| `validation_warnings` | Non-authorizing warnings |
| `routing_hint` | Allowed routing hint only (section 10) |
| `accepted_for_governance_context` | True only when ready for governance display/routing |
| `rejected_for_decisioning` | Always true for decisioning/recommendation/spend paths |
| `lineage` | Runtime + upstream lineage |

### Output must preserve

- source handoff id
- source package
- profile id
- canonical identity
- decision scope
- generic statuses
- source-of-truth refs
- blockers / warnings / prohibited actions
- fixed non-authorization statuses

`runtime_output_contract_defined` = true

---

## 6. MIP consumer record normalized fields

Normalized object: **`MIPMethodPromotionHandoffConsumerRecord`**

| Field | Role |
|-------|------|
| `consumer_record_id` | MIP consumer record id |
| `received_handoff_id` | Upstream `handoff_id` |
| `source_package` | Must remain `panel_exp` |
| `source_artifact_id` | Preserved |
| `source_runtime` | Preserved |
| `source_runtime_version` | Preserved |
| `profile_id` | Preserved |
| `canonical_identity` | Preserved |
| `decision_scope` | Preserved |
| `generic_packet_status` | Preserved |
| `generic_eligibility_status` | Preserved |
| `generic_decision_status` | Preserved as weak context |
| `generic_governance_stage` | Preserved |
| `source_of_truth_refs` | Preserved |
| `source_packet_ref` | Preserved |
| `source_decision_ref` | Preserved |
| `source_governance_summary_ref` | Preserved |
| `missing_evidence` | Preserved |
| `blockers` | Preserved |
| `warnings` | Preserved |
| `prohibited_actions` | Preserved |
| `boundary_statuses` | Preserved |
| `mip_allowed_uses` | Preserved |
| `mip_prohibited_uses` | Preserved |
| `consumer_allowed_actions` | MIP-side allowed actions |
| `consumer_blocked_actions` | MIP-side blocked actions |
| `decision_surface_authorization_status` | Fixed non-authorization |
| `trust_report_bypass_status` | Fixed non-bypass |
| `recommendation_authorization_status` | Fixed non-authorization |
| `catalog_authorization_status` | Fixed non-authorization |
| `production_readout_authorization_status` | Fixed non-authorization |
| `production_compatibility_authorization_status` | Fixed non-authorization |
| `claim_authorization_status` | Fixed non-authorization |
| `method_promotion_status` | Fixed non-promotion |
| `instrument_promotion_status` | Fixed non-promotion |
| `spend_roi_authorization_status` | Fixed non-authorization |
| `causal_lift_authorization_status` | Fixed non-authorization |
| `statistical_claim_authorization_status` | Fixed non-authorization |
| `consumer_status` | Consumer/runtime status |
| `routing_hint` | Allowed routing hint |
| `lineage` | Consumer + upstream lineage |
| `created_from_handoff` | Upstream handoff id / refs |

`consumer_record_normalization_defined` = true

---

## 7. Required validation rules

Future runtime must block if:

- payload missing
- `source_package != panel_exp`
- `handoff_id` missing
- `profile_id` missing
- `canonical_identity` missing
- `decision_scope` missing
- `generic_decision_status` missing
- `source_of_truth_refs` missing
- `boundary_statuses` missing
- `mip_allowed_uses` missing
- `mip_prohibited_uses` missing
- fixed non-authorization statuses missing
- authorization status stronger than `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF`
- TrustReport status stronger than `NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF`
- promotion status stronger than `NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF`
- prohibited actions absent or weakened
- handoff attempts to create DecisionSurface, RecommendationContract, TrustReport bypass, spend/ROI recommendation, production readout, catalog unblock, claim authorization, or promotion
- generic `APPROVE_REVIEW_CONTINUATION` is represented as production/recommendation/planning readiness

`required_validation_rules_defined` = true

---

## 8. Fixed non-authorization statuses

Future runtime must preserve:

| Status field | Fixed value |
|--------------|-------------|
| `decision_surface_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `trust_report_bypass_status` | `NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF` |
| `recommendation_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `catalog_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `production_readout_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `production_compatibility_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `claim_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `method_promotion_status` | `NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF` |
| `instrument_promotion_status` | `NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF` |
| `spend_roi_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `causal_lift_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |
| `statistical_claim_authorization_status` | `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF` |

`fixed_mip_non_authorization_statuses_required` = true

---

## 9. Consumer runtime statuses

- `CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT`
- `CONSUMER_RUNTIME_BLOCKED_MISSING_PAYLOAD`
- `CONSUMER_RUNTIME_BLOCKED_UNSUPPORTED_SOURCE_PACKAGE`
- `CONSUMER_RUNTIME_BLOCKED_MISSING_HANDOFF_ID`
- `CONSUMER_RUNTIME_BLOCKED_MISSING_PROFILE_ID`
- `CONSUMER_RUNTIME_BLOCKED_MISSING_CANONICAL_IDENTITY`
- `CONSUMER_RUNTIME_BLOCKED_MISSING_DECISION_SCOPE`
- `CONSUMER_RUNTIME_BLOCKED_MISSING_GENERIC_DECISION_STATUS`
- `CONSUMER_RUNTIME_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS`
- `CONSUMER_RUNTIME_BLOCKED_MISSING_BOUNDARY_STATUSES`
- `CONSUMER_RUNTIME_BLOCKED_MISSING_ALLOWED_USES`
- `CONSUMER_RUNTIME_BLOCKED_MISSING_PROHIBITED_USES`
- `CONSUMER_RUNTIME_BLOCKED_AUTHORIZATION_STATUS_WEAKENED`
- `CONSUMER_RUNTIME_BLOCKED_TRUST_BYPASS_ATTEMPT`
- `CONSUMER_RUNTIME_BLOCKED_RECOMMENDATION_AUTHORIZATION_ATTEMPT`
- `CONSUMER_RUNTIME_BLOCKED_DECISION_SURFACE_AUTHORIZATION_ATTEMPT`
- `CONSUMER_RUNTIME_BLOCKED_CLAIM_OR_PRODUCTION_AUTHORIZATION_ATTEMPT`
- `CONSUMER_RUNTIME_BLOCKED_PROMOTION_ATTEMPT`
- `CONSUMER_RUNTIME_BLOCKED_PLANNING_RECOMMENDATION_ATTEMPT`
- `CONSUMER_RUNTIME_BLOCKED_SPEND_ROI_AUTHORIZATION_ATTEMPT`
- `CONSUMER_RUNTIME_BLOCKED_SOURCE_OF_TRUTH_OVERRIDE_ATTEMPT`
- `CONSUMER_RUNTIME_BLOCKED_GENERIC_APPROVAL_UPGRADE_ATTEMPT`

`consumer_runtime_statuses_defined` = true

`CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT` means governance-context consumption only. It does **not** imply DecisionSurface, RecommendationContract, TrustReport bypass, planning answer eligibility, or production readiness.

---

## 10. Routing hints

### Allowed routing hints

- `ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY`
- `ROUTE_TO_DIAGNOSTIC_EXPLANATION`
- `ROUTE_TO_CATALOG_REVIEW`
- `ROUTE_TO_CLAIM_AUTHORIZATION_REVIEW`
- `ROUTE_TO_PRODUCTION_COMPATIBILITY_REVIEW`
- `ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK`

### Blocked routing hints

- `ROUTE_TO_DECISION_SURFACE_APPROVAL`
- `ROUTE_TO_TRUST_REPORT_BYPASS`
- `ROUTE_TO_RECOMMENDATION_CONTRACT`
- `ROUTE_TO_PLANNING_RECOMMENDATION`
- `ROUTE_TO_BUDGET_OPTIMIZER`
- `ROUTE_TO_SPEND_REALLOCATION`
- `ROUTE_TO_ROI_ROAS_RECOMMENDATION`
- `ROUTE_TO_PRODUCTION_READOUT`

`routing_hints_defined` = true

---

## 11. Generic approval handling

Future runtime must treat `APPROVE_REVIEW_CONTINUATION` as **weak governance context only**.

### It may support

- display
- lineage
- separate review routing
- unsupported recommendation blocking

### It must not support

- planning answer eligibility
- DecisionSurface readiness
- TrustReport sufficiency
- RecommendationContract readiness
- production readiness
- catalog eligibility
- claim authorization
- spend/ROI recommendation readiness
- causal/statistical validity

`generic_approval_handling_defined` = true

---

## 12. Relationship to MIP gates

| MIP gate / surface | Relationship |
|--------------------|--------------|
| DecisionSurface gate | Remains separate |
| TrustReport gate | Remains separate |
| RecommendationContract gate | Remains separate |
| Planning answer eligibility gate | Remains separate |
| Claim / catalog / production readiness | Remain separate |
| `CalibrationSignal` | This runtime contract creates none |
| `ExperimentEvidence` | This runtime contract creates none |
| `DecisionSurface` | This runtime contract creates none |
| `RecommendationContract` | This runtime contract creates none |

This handoff remains **governance context only**.

`relationship_to_mip_gates_defined` = true  
`decision_surface_remains_separately_gated` = true  
`trust_report_remains_separately_required` = true  
`recommendation_contract_remains_separately_gated` = true  
`planning_answer_eligibility_remains_separately_gated` = true  
`claim_catalog_production_readiness_remain_separate` = true  
`handoff_is_governance_context_only` = true

---

## 13. Required runtime tests for future implementation

Future implementation must cover:

- valid handoff normalizes into consumer record
- missing payload blocks
- unsupported source package blocks
- missing required fields block
- missing fixed statuses block
- weakened authorization statuses block
- TrustReport bypass attempt blocks
- RecommendationContract attempt blocks
- DecisionSurface attempt blocks
- claim/catalog/production attempts block
- planning recommendation attempt blocks
- spend/ROI attempt blocks
- source override attempt blocks
- generic approval upgrade attempt blocks
- allowed route emits governance display only
- blocked routes are never emitted
- serializer is JSON-safe if implemented

`future_runtime_tests_defined` = true

---

## 14. Runtime implementation stance

**Runtime implementation is still deferred.**

Next step should be runtime implementation only after this contract is merged.

`runtime_implementation_deferred` = true  
`mip_runtime_implemented` = false  
`mip_integration_implemented` = false

---

## 15. Recommended next artifact

**`MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001`**

Scope:

- implement MIP-side runtime validator/normalizer according to this contract
- no DecisionSurface construction
- no TrustReport bypass
- no RecommendationContract
- no planning recommendation eligibility
- no budget/spend/ROI recommendation
- no claim/catalog/production authorization
- no method/instrument promotion

---

## 16. Non-goals

- no MIP runtime implemented
- no MIP integration implemented
- no package runtime changed
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

Forbidden flags for this artifact (all false):

- `mip_runtime_implemented`
- `mip_integration_implemented`
- `package_runtime_changed`
- `decision_surface_authorized`
- `trust_report_bypassed`
- `recommendation_contract_authorized`
- `planning_recommendation_enabled`
- `planning_answer_eligibility_enabled`
- `budget_optimization_enabled`
- `spend_movement_authorized`
- `roi_roas_authorized`
- `method_promoted`
- `instrument_promoted`
- `catalog_unblocked`
- `production_compatibility_authorized`
- `claim_authorization_changed`
- `causal_lift_claim_authorized`
- `business_lift_claim_authorized`
- `statistical_claim_authorized`
- `calibration_signal_created`
- `experiment_evidence_created`
- `raw_evidence_scored`
- `package_source_of_truth_overridden`

---

## 17. Validation results

- `python -m json.tool docs/contracts/archives/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001_summary.json` — valid JSON
- `python -m pytest tests/contracts/test_mip_method_promotion_handoff_consumer_runtime_contract_001.py -q` — governance assertions pass
- Safety grep — no forbidden runtime/integration/authorization flags true
- Capability grep — runtime contract/input/output, normalization, validation rules, runtime deferred true
