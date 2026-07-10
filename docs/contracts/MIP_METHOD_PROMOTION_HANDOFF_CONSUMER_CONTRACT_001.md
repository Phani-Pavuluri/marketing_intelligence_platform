# MIP Method Promotion Handoff Consumer Contract 001

## 1. Metadata

| Field | Value |
|-------|-------|
| **artifact_id** | `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001` |
| **artifact_type** | `mip_method_promotion_handoff_consumer_contract` |
| **status** | `completed` |
| **scope** | `mip_side_consumer_contract_docs_tests_only_no_runtime_integration_no_decision_authorization` |
| **upstream_package_artifact** | `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001` |
| **upstream_package_commit** | `42f4484` |
| **upstream_package_source** | `panel_exp` |
| **final_verdict** | `mip_consumer_contract_defined_no_runtime_no_decision_authorization` |
| **recommended_next** | `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001` |

**Upstream package chain (GeoX / panel_exp):**

- `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_CONTRACT_001`
- `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001`
- `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001`

**Package decision consumed:** `PROCEED_TO_MIP_INTEGRATION_PLANNING_CONTRACT_NOT_RUNTIME_INTEGRATION`

**Related MIP governance (consume, do not bypass):**

- `DecisionSurface` — remains separately gated
- `TrustReport` — remains separately required
- `RecommendationContract` — remains separately gated

---

## 2. Why this contract exists

GeoX / `panel_exp` can now emit a package-side method-promotion handoff object:

`MethodPromotionGenericAdapterMIPHandoff`

That object is **governance context only**. Package checkpoint `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001` (`42f4484`) concluded the package-side runtime is stable enough for MIP integration **planning**, not runtime integration.

MIP needs a consumer contract before any runtime adapter or orchestration wiring. Without this contract, MIP risks interpreting package method-review continuation (`APPROVE_REVIEW_CONTINUATION`) as:

- DecisionSurface readiness or approval
- TrustReport bypass
- RecommendationContract generation
- production / catalog / claim readiness
- spend movement, budget optimization, or ROI/ROAS advice

This artifact is **docs/tests only**. It does not implement MIP runtime integration, create a runtime adapter, construct DecisionSurface, bypass TrustReport, or generate RecommendationContract.

---

## 3. Upstream object consumed

Conceptual upstream object: **`MethodPromotionGenericAdapterMIPHandoff`**

| Field | Role |
|-------|------|
| `handoff_id` | Unique package handoff id |
| `source_package` | Must be `panel_exp` |
| `source_artifact_id` | Package source artifact id |
| `source_runtime` | Package source runtime id |
| `source_runtime_version` | Optional runtime version |
| `profile_id` | Registered adapter profile |
| `canonical_identity` | Exact instrument identity |
| `decision_scope` | `restricted_review` or `null_monitor` |
| `generic_packet_status` | Mapped packet readiness |
| `generic_eligibility_status` | Mapped eligibility |
| `generic_decision_status` | Mapped decision (weak continuation only) |
| `generic_governance_stage` | `packet_only` / `decision_ready` / `blocked_adapter` |
| `source_packet_ref` | Source packet summary/ref |
| `source_decision_ref` | Source decision summary/ref |
| `source_governance_summary_ref` | Source governance summary/ref |
| `source_of_truth_refs` | Packet/decision runtime artifact ids |
| `missing_evidence` | Preserved missing categories |
| `blockers` | Preserved blockers |
| `warnings` | Preserved warnings |
| `prohibited_actions` | Preserved prohibited actions |
| `boundary_statuses` | Source boundary fields |
| `mip_allowed_uses` | Enumerated allowed uses |
| `mip_prohibited_uses` | Enumerated prohibited uses |
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
| `lineage` | Audit lineage |
| `created_from_artifacts` | Artifact lineage list |
| `handoff_status` | Package handoff readiness/block status |

Supported upstream profiles (context only):

- `tbrridge_restricted_review_v1`
- `scm_jackknife_null_monitor_v1`
- `augsynth_jackknife_restricted_review_v1`

---

## 4. MIP consumer object

Conceptual MIP-side consumer contract object: **`MIPMethodPromotionHandoffConsumerRecord`**

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
| `consumer_allowed_actions` | MIP-side allowed actions (section 7) |
| `consumer_blocked_actions` | MIP-side blocked actions (section 8) |
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
| `consumer_status` | MIP consumer status (section 10) |
| `routing_hint` | Allowed routing hint (section 11) |
| `lineage` | Consumer + upstream lineage |
| `created_from_handoff` | Upstream handoff id / refs |

`consumer_contract_defined` = true  
`consumer_object_defined` = true

---

## 5. Required validation rules

MIP consumer must reject or block if:

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
- any authorization status is stronger than `NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF`
- TrustReport status is stronger than `NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF`
- method/instrument promotion status is stronger than `NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF`
- prohibited uses are absent or weakened
- handoff attempts to create DecisionSurface, TrustReport bypass, RecommendationContract, spend/ROI recommendation, production readout, catalog unblock, or claim authorization

`required_validation_rules_defined` = true

---

## 6. Fixed MIP non-authorization statuses

MIP must preserve:

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

## 7. MIP allowed actions

MIP may:

- display governance context
- display method-review lineage
- display profile identity
- display decision scope
- display missing evidence
- display blockers
- display warnings
- display prohibited actions
- display non-authorization statuses
- route to separate catalog review
- route to separate claim authorization review
- route to separate production compatibility review
- block unsupported recommendations
- explain `restricted_review` or `null_monitor` scope
- attach package governance context to a diagnostic-only explanation

`mip_allowed_actions_defined` = true

---

## 8. MIP blocked actions

MIP must not:

- create DecisionSurface from handoff
- mark DecisionSurface approved
- bypass TrustReport
- generate RecommendationContract
- authorize spend movement
- authorize budget optimization
- calculate or authorize ROI/ROAS
- authorize production readout
- authorize production compatibility
- unblock catalog
- authorize claims
- claim causal lift
- claim business lift
- claim statistical significance
- claim confidence interval validity
- claim p-value validity
- claim power validity
- promote method
- promote instrument
- override source packet runtime
- override source decision runtime
- score raw evidence quality
- repair missing evidence
- upgrade `APPROVE_REVIEW_CONTINUATION` into production/recommendation readiness

`mip_blocked_actions_defined` = true

---

## 9. Generic decision semantics in MIP

**`APPROVE_REVIEW_CONTINUATION` means:**

- package governance summary may be displayed
- profile may continue through governance review context
- MIP may route to separate review lanes

**`APPROVE_REVIEW_CONTINUATION` does not mean:**

- MIP answer eligibility
- planning recommendation eligibility
- DecisionSurface readiness
- TrustReport sufficiency
- RecommendationContract readiness
- production readiness
- catalog eligibility
- claim authorization
- spend/ROI recommendation readiness
- causal/statistical validity

`generic_approve_review_continuation_semantics_defined_for_mip` = true

---

## 10. Consumer statuses

Conceptual MIP consumer statuses:

- `CONSUMER_RECORD_READY_FOR_GOVERNANCE_CONTEXT`
- `CONSUMER_RECORD_BLOCKED_MISSING_HANDOFF`
- `CONSUMER_RECORD_BLOCKED_UNSUPPORTED_SOURCE_PACKAGE`
- `CONSUMER_RECORD_BLOCKED_MISSING_PROFILE_ID`
- `CONSUMER_RECORD_BLOCKED_MISSING_CANONICAL_IDENTITY`
- `CONSUMER_RECORD_BLOCKED_MISSING_DECISION_SCOPE`
- `CONSUMER_RECORD_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS`
- `CONSUMER_RECORD_BLOCKED_MISSING_BOUNDARY_STATUSES`
- `CONSUMER_RECORD_BLOCKED_MISSING_ALLOWED_USES`
- `CONSUMER_RECORD_BLOCKED_MISSING_PROHIBITED_USES`
- `CONSUMER_RECORD_BLOCKED_AUTHORIZATION_STATUS_WEAKENED`
- `CONSUMER_RECORD_BLOCKED_TRUST_BYPASS_ATTEMPT`
- `CONSUMER_RECORD_BLOCKED_RECOMMENDATION_AUTHORIZATION_ATTEMPT`
- `CONSUMER_RECORD_BLOCKED_DECISION_SURFACE_AUTHORIZATION_ATTEMPT`
- `CONSUMER_RECORD_BLOCKED_CLAIM_OR_PRODUCTION_AUTHORIZATION_ATTEMPT`
- `CONSUMER_RECORD_BLOCKED_PROMOTION_ATTEMPT`

`consumer_statuses_defined` = true

Ready status means governance-context consumption only. It does **not** imply DecisionSurface, RecommendationContract, TrustReport bypass, planning answer eligibility, or production readiness.

---

## 11. Routing semantics

**Allowed routing:**

- diagnostic display route
- governance context route
- separate catalog review route
- separate claim authorization review route
- separate production compatibility review route
- unsupported recommendation block route

**Blocked routing:**

- planning recommendation route
- budget optimizer route
- spend reallocation route
- production readout route
- DecisionSurface approval route
- TrustReport bypass route

`routing_semantics_defined` = true

---

## 12. Relationship to existing MIP contracts

| MIP contract / surface | Relationship |
|------------------------|--------------|
| `DecisionSurface` | Remains separately gated; handoff cannot create or approve |
| `TrustReport` | Remains separately required; handoff cannot bypass |
| `RecommendationContract` | Remains separately gated; handoff cannot generate |
| Claim / catalog / production readiness | Remain separate lanes |
| `CalibrationSignal` | Handoff is **not** a calibration signal |
| `ExperimentEvidence` | Handoff is **not** experiment evidence |
| GeoX readout handoff (`GeoXReadoutInputHandoff`) | Orthogonal Lane B spend/readout path; not substituted by this object |

This handoff is **not** a decision surface.  
This handoff is **not** a recommendation contract.  
This handoff is **governance context only**.

`relationship_to_existing_mip_contracts_defined` = true  
`decision_surface_remains_separately_gated` = true  
`trust_report_remains_separately_required` = true  
`recommendation_contract_remains_separately_gated` = true  
`claim_catalog_production_readiness_remain_separate` = true  
`handoff_is_governance_context_only` = true

---

## 13. Runtime implementation stance

**MIP runtime implementation is still deferred.**

This artifact only defines the consumer contract.

Before runtime:

- add MIP-side typed runtime contract
- define adapter input/output types
- define validation gate behavior
- define routing behavior
- define tests for attempted misuse

`runtime_implementation_deferred` = true  
`mip_runtime_implemented` = false  
`mip_integration_implemented` = false

---

## 14. Recommended next artifact

**`MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001`**

Scope:

- define MIP-side runtime contract for validating/normalizing `MethodPromotionGenericAdapterMIPHandoff`
- no runtime implementation yet
- no DecisionSurface creation
- no TrustReport bypass
- no RecommendationContract
- no planning answer eligibility
- no budget/spend/ROI recommendation

---

## 15. Non-goals

- no MIP runtime implemented
- no MIP integration implemented
- no package runtime changed
- no DecisionSurface authorized
- no TrustReport bypass
- no RecommendationContract authorized
- no planning recommendation enabled
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

## 16. Validation results

- `python -m json.tool docs/contracts/archives/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001_summary.json` — valid JSON
- `python -m pytest tests/contracts/test_mip_method_promotion_handoff_consumer_contract_001.py -q` — governance assertions pass
- Safety grep — no forbidden runtime/integration/authorization flags true
- Capability grep — consumer contract/object, validation rules, fixed statuses, governance-context-only, runtime deferred true

**Docs layout note:** This repository uses `docs/contracts/` + `docs/contracts/archives/` (not `docs/05_validation/` / `docs/06_investigations/`). Files are placed consistently with existing MIP contract docs.
