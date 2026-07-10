# MIP Method Promotion Handoff Consumer Runtime 001

## 1. Metadata

| Field | Value |
|-------|-------|
| **artifact_id** | `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001` |
| **artifact_type** | `mip_method_promotion_handoff_consumer_runtime` |
| **status** | `completed` |
| **scope** | `mip_side_validator_normalizer_runtime_no_decision_authorization` |
| **depends_on** | `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001`, `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001` |
| **upstream_package_artifact** | `METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001` |
| **upstream_package_commit** | `42f4484` |
| **runtime_module** | `mip.contracts.method_promotion_handoff_consumer` |
| **final_verdict** | `mip_consumer_runtime_implemented_as_validator_normalizer_no_decision_authorization` |
| **recommended_next** | `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_APPLICATION_CHECKPOINT_001` |

**Related MIP governance (consume, do not bypass):**

- `DecisionSurface` — remains separately gated
- `TrustReport` — remains separately required
- `RecommendationContract` — remains separately gated
- Planning answer eligibility — remains separately gated

---

## 2. Contract dependency

This runtime implements:

- `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001`
- `MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001`

Upstream package handoff shape: `MethodPromotionGenericAdapterMIPHandoff`-like payload from `panel_exp` (`42f4484`).

`runtime_implemented` = true  
`validator_implemented` = true  
`normalizer_implemented` = true  
`serializer_implemented` = true

---

## 3. Runtime API

```python
from mip.contracts.method_promotion_handoff_consumer import (
    MIPMethodPromotionHandoffConsumerRuntimeInput,
    MIPMethodPromotionHandoffConsumerRuntimeOutput,
    MIPMethodPromotionHandoffConsumerRecord,
    MIPMethodPromotionHandoffConsumerStatus,
    MIPMethodPromotionHandoffRoutingHint,
    MIPMethodPromotionHandoffAuthorizationStatus,
    MIPMethodPromotionHandoffBypassStatus,
    MIPMethodPromotionHandoffPromotionStatus,
    validate_and_normalize_method_promotion_handoff,
    serialize_method_promotion_handoff_consumer_record,
)
```

Primary entrypoint: `validate_and_normalize_method_promotion_handoff(runtime_input)`.

This runtime is an **enforcement gate**. It validates and normalizes governance context only.

---

## 4. Input/output models

### Input — `MIPMethodPromotionHandoffConsumerRuntimeInput`

| Field | Role |
|-------|------|
| `raw_handoff_payload` | Package-side handoff mapping (required for acceptance) |
| `ingestion_context` | Optional MIP ingestion metadata |
| `received_at` | Optional ingestion timestamp |
| `source_package_expected` | Default `panel_exp` |
| `upstream_artifact_expected` | Optional expected upstream artifact id |
| `strict_validation` | Default `true` |
| `lineage_context` | Optional lineage enrichment |

### Output — `MIPMethodPromotionHandoffConsumerRuntimeOutput`

| Field | Role |
|-------|------|
| `consumer_record` | Normalized record, or `None` when blocked |
| `consumer_status` | Runtime consumer status |
| `validation_errors` | Blocking errors |
| `validation_warnings` | Non-authorizing warnings |
| `routing_hint` | Allowed or blocked routing hint |
| `accepted_for_governance_context` | True only for valid governance-context acceptance |
| `rejected_for_decisioning` | Always `true` |
| `lineage` | Runtime + upstream lineage |

`runtime_input_output_implemented` = true

---

## 5. Consumer record

`MIPMethodPromotionHandoffConsumerRecord` preserves package identity, decision scope, generic statuses, source-of-truth refs, missing evidence, blockers, warnings, prohibited actions, boundary statuses, and MIP allowed/prohibited uses.

It always stamps MIP-side:

- `consumer_allowed_actions` / `consumer_blocked_actions`
- fixed non-authorization / non-bypass / non-promotion statuses
- `consumer_status` / `routing_hint` for governance-context display when ready
- `created_from_handoff = true`

`consumer_record_implemented` = true

---

## 6. Validation behavior

1. Missing/empty payload → `CONSUMER_RUNTIME_BLOCKED_MISSING_PAYLOAD`, no record.
2. `source_package != panel_exp` → unsupported source package block.
3. Missing required fields → most specific missing-* status.
4. Fixed non-authorization statuses missing or weakened → block.
5. Prohibited uses missing or weakened → block.
6. DecisionSurface / TrustReport bypass / RecommendationContract / planning / spend-ROI / claim-catalog-production / promotion attempts → block.
7. `APPROVE_REVIEW_CONTINUATION` preserved as weak governance context only.
8. Never repair missing evidence.
9. Never score raw evidence.
10. Never override package source-of-truth refs.
11. Valid payload → accepted for governance context, rejected for decisioning, route to governance display.

`missing_payload_blocks` = true  
`unsupported_source_package_blocks` = true  
`missing_required_fields_block` = true  
`weakened_authorization_statuses_block` = true  
`trust_report_bypass_attempt_blocks` = true  
`recommendation_authorization_attempt_blocks` = true  
`decision_surface_authorization_attempt_blocks` = true  
`claim_or_production_authorization_attempt_blocks` = true  
`promotion_attempt_blocks` = true  
`planning_recommendation_attempt_blocks` = true  
`spend_roi_authorization_attempt_blocks` = true  
`source_of_truth_override_attempt_blocks` = true  
`generic_approval_upgrade_attempt_blocks` = true  
`raw_evidence_not_scored` = true  
`missing_evidence_not_repaired` = true  
`package_source_of_truth_not_overridden` = true

---

## 7. Fixed statuses

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

`fixed_mip_non_authorization_statuses_enforced` = true

---

## 8. Allowed/blocked actions

### Allowed consumer actions

- `display_governance_context`
- `display_method_review_lineage`
- `display_profile_identity`
- `display_decision_scope`
- `display_missing_evidence`
- `display_blockers`
- `display_warnings`
- `display_prohibited_actions`
- `display_non_authorization_statuses`
- `route_to_separate_catalog_review`
- `route_to_separate_claim_authorization_review`
- `route_to_separate_production_compatibility_review`
- `block_unsupported_recommendations`
- `explain_restricted_review_or_null_monitor_scope`
- `attach_governance_context_to_diagnostic_explanation`

### Blocked consumer actions

- `create_decision_surface`
- `approve_decision_surface`
- `bypass_trust_report`
- `generate_recommendation_contract`
- `enable_planning_answer_eligibility`
- `authorize_spend_movement`
- `authorize_budget_optimization`
- `calculate_or_authorize_roi_roas`
- `authorize_production_readout`
- `authorize_production_compatibility`
- `unblock_catalog`
- `authorize_claims`
- `claim_causal_lift`
- `claim_business_lift`
- `claim_statistical_significance`
- `claim_confidence_interval_validity`
- `claim_p_value_validity`
- `claim_power_validity`
- `promote_method`
- `promote_instrument`
- `override_source_packet_runtime`
- `override_source_decision_runtime`
- `score_raw_evidence_quality`
- `repair_missing_evidence`
- `upgrade_approve_review_continuation_to_readiness`

`allowed_actions_enforced` = true  
`blocked_actions_enforced` = true

---

## 9. Consumer statuses

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

`consumer_statuses_implemented` = true

---

## 10. Routing hints

### Allowed

- `ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY`
- `ROUTE_TO_DIAGNOSTIC_EXPLANATION`
- `ROUTE_TO_CATALOG_REVIEW`
- `ROUTE_TO_CLAIM_AUTHORIZATION_REVIEW`
- `ROUTE_TO_PRODUCTION_COMPATIBILITY_REVIEW`
- `ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK`

### Blocked

- `ROUTE_BLOCKED_DECISION_SURFACE_APPROVAL`
- `ROUTE_BLOCKED_TRUST_REPORT_BYPASS`
- `ROUTE_BLOCKED_RECOMMENDATION_CONTRACT`
- `ROUTE_BLOCKED_PLANNING_RECOMMENDATION`
- `ROUTE_BLOCKED_BUDGET_OPTIMIZER`
- `ROUTE_BLOCKED_SPEND_REALLOCATION`
- `ROUTE_BLOCKED_ROI_ROAS_RECOMMENDATION`
- `ROUTE_BLOCKED_PRODUCTION_READOUT`

`routing_hints_implemented` = true

---

## 11. Generic approval handling

`APPROVE_REVIEW_CONTINUATION` is preserved as **weak governance context only**.

It may support display, lineage, separate review routing, and unsupported-recommendation blocking.

It must not imply planning answer eligibility, DecisionSurface readiness, TrustReport sufficiency, RecommendationContract readiness, production readiness, catalog eligibility, claim authorization, spend/ROI readiness, or causal/statistical validity.

Upgrade attempts (`production_ready`, `upgrade_approve_review_continuation_to_readiness`, etc.) are blocked.

`generic_approve_review_continuation_preserved_as_weak_context` = true

---

## 12. Non-authorization guarantees

Valid handoff acceptance:

- `accepted_for_governance_context` = true
- `rejected_for_decisioning` = true
- `routing_hint` = `ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY`
- `consumer_status` = `CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT`

This runtime does **not**:

- implement MIP answer-eligibility / routing integration (`mip_integration_implemented` = false)
- authorize DecisionSurface
- bypass TrustReport
- authorize RecommendationContract
- enable planning recommendation / answer eligibility
- authorize budget optimization, spend movement, or ROI/ROAS
- promote method or instrument
- unblock catalog or authorize production compatibility / claims
- create CalibrationSignal or ExperimentEvidence

`valid_handoff_accepted_for_governance_context_only` = true  
`valid_handoff_rejected_for_decisioning` = true

---

## 13. Serialization semantics

`serialize_method_promotion_handoff_consumer_record(record) -> dict`

Returns a JSON-safe dict:

- enum values as strings
- tuples/lists as lists
- nested mappings preserved

---

## 14. Tests/validation

- `tests/contracts/test_mip_method_promotion_handoff_consumer_runtime_001.py`
- public API import
- valid normalize + governance-only acceptance
- fixed statuses / allowed / blocked actions
- missing-field and attempt blocks
- serializer JSON-safe
- summary/doc governance flags
- roadmap / integration strategy references

---

## 15. Recommended next artifact

**`MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_APPLICATION_CHECKPOINT_001`**

Purpose: checkpoint runtime behavior before any answer-eligibility/routing integration.

---

## 16. Non-goals

- DecisionSurface creation or approval
- TrustReport bypass
- RecommendationContract generation
- Planning answer eligibility
- Budget optimization / spend movement / ROI-ROAS authorization
- Claim / catalog / production readiness authorization
- Method or instrument promotion
- Raw evidence scoring or missing-evidence repair
- Package source-of-truth override
- MIP integration beyond validator/normalizer

---

## Validation results

- `python -m json.tool docs/contracts/archives/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001_summary.json`
- `git diff --check`
- `python -m pytest tests/contracts/test_mip_method_promotion_handoff_consumer_runtime_001.py -q`
