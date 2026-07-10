"""Application-path checks for method-promotion handoff answerability guard."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from mip.contracts.method_promotion_handoff_answerability_application import (
    MethodPromotionHandoffAnswerabilityApplicationInput,
    MethodPromotionHandoffAnswerabilityApplicationOutput,
    apply_method_promotion_handoff_answerability_guard,
    serialize_method_promotion_handoff_answerability_application_output,
)
from mip.contracts.method_promotion_handoff_consumer import (
    FIXED_AUTH,
    FIXED_BYPASS,
    FIXED_PROMO,
)

_DOC = Path(
    "docs/contracts/MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_APPLICATION_001.md"
)
_SUMMARY = Path(
    "docs/contracts/archives/MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_APPLICATION_001_summary.json"
)
_ROADMAP_EXEC = Path("docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md")
_REPO_INTEGRATION = Path("docs/architecture/REPO_INTEGRATION_STRATEGY.md")

_ARTIFACT = "MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_APPLICATION_001"
_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_APPLICATION_CHECKPOINT_001"
_VERDICT = "narrow_answerability_application_path_implemented_no_llm_no_answer_eligibility"

_CAPABILITY_FALSE = (
    "can_answer_decisioning_question",
    "can_answer_planning_question",
    "can_generate_recommendation",
    "can_create_decision_surface",
    "can_bypass_trust_report",
    "can_generate_recommendation_contract",
)

_TRUE_FLAGS = (
    "application_path_implemented",
    "consumer_runtime_called",
    "answerability_guard_called",
    "serializer_implemented",
    "valid_governance_explanation_path_supported",
    "planning_recommendation_intent_blocks",
    "budget_optimization_intent_blocks",
    "spend_reallocation_intent_blocks",
    "roi_roas_intent_blocks",
    "lift_claim_intent_blocks",
    "production_readout_intent_blocks",
    "catalog_claim_approval_intent_blocks",
    "invalid_handoff_blocks",
    "safe_response_guidance_returned",
    "handoff_governance_context_only",
)

_FALSE_FLAGS = (
    "can_answer_decisioning_question",
    "can_answer_planning_question",
    "can_generate_recommendation",
    "can_create_decision_surface",
    "can_bypass_trust_report",
    "can_generate_recommendation_contract",
    "llm_orchestration_integration_implemented",
    "answer_eligibility_integration_implemented",
    "user_facing_answer_generation_implemented",
    "decision_surface_authorized",
    "trust_report_bypassed",
    "recommendation_contract_authorized",
    "planning_recommendation_enabled",
    "planning_answer_eligibility_enabled",
    "budget_optimization_enabled",
    "spend_movement_authorized",
    "roi_roas_authorized",
    "method_promoted",
    "instrument_promoted",
    "catalog_unblocked",
    "production_compatibility_authorized",
    "claim_authorization_changed",
    "causal_lift_claim_authorized",
    "business_lift_claim_authorized",
    "statistical_claim_authorized",
    "calibration_signal_created",
    "experiment_evidence_created",
    "raw_evidence_scored",
    "package_source_of_truth_overridden",
)

_FORBIDDEN_TRUE_PATTERNS = tuple(
    rf'"{flag}"\s*:\s*true'
    for flag in _FALSE_FLAGS
    if not flag.startswith("can_")
)

_MIP_ALLOWED_USES = (
    "display_as_governance_context",
    "display_method_review_lineage",
    "display_profile_identity",
    "display_decision_scope",
    "display_missing_evidence",
    "display_blockers",
    "display_warnings",
    "display_prohibited_actions",
    "route_to_separate_catalog_review",
    "route_to_separate_claim_authorization_review",
    "route_to_separate_production_compatibility_review",
    "block_unsupported_recommendations",
    "explain_restricted_review_or_null_monitor_scope",
)

_MIP_PROHIBITED_USES = (
    "create_or_approve_decision_surface",
    "bypass_trust_report",
    "generate_recommendation_contract",
    "enable_planning_answer_eligibility",
    "authorize_spend_movement",
    "authorize_budget_optimization",
    "calculate_or_authorize_roi_roas",
    "authorize_production_readout",
    "authorize_production_compatibility",
    "unblock_catalog",
    "authorize_claims",
    "claim_causal_lift",
    "claim_business_lift",
    "claim_statistical_significance",
    "claim_confidence_interval_validity",
    "claim_p_value_validity",
    "claim_power_validity",
    "promote_method",
    "promote_instrument",
    "override_source_packet_runtime",
    "override_source_decision_runtime",
    "score_raw_evidence_quality",
    "repair_missing_evidence",
    "upgrade_approve_review_continuation_to_readiness",
)

_FIXED_STATUS_FIELDS = (
    "decision_surface_authorization_status",
    "recommendation_authorization_status",
    "catalog_authorization_status",
    "production_readout_authorization_status",
    "production_compatibility_authorization_status",
    "claim_authorization_status",
    "spend_roi_authorization_status",
    "causal_lift_authorization_status",
    "statistical_claim_authorization_status",
)


def _fixed_boundary() -> dict[str, str]:
    boundary = {field: FIXED_AUTH for field in _FIXED_STATUS_FIELDS}
    boundary["trust_report_bypass_status"] = FIXED_BYPASS
    boundary["method_promotion_status"] = FIXED_PROMO
    boundary["instrument_promotion_status"] = FIXED_PROMO
    return boundary


def _valid_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "handoff_id": "handoff-tbrridge-001",
        "source_package": "panel_exp",
        "source_artifact_id": "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_001",
        "source_runtime": "METHOD_PROMOTION_GENERIC_RUNTIME_001",
        "source_runtime_version": "1",
        "profile_id": "tbrridge_restricted_review_v1",
        "canonical_identity": {
            "method_family": "tbrridge",
            "profile_id": "tbrridge_restricted_review_v1",
        },
        "decision_scope": {"scope": "restricted_review"},
        "generic_packet_status": "PACKET_READY",
        "generic_eligibility_status": "ELIGIBLE_FOR_RESTRICTED_REVIEW",
        "generic_decision_status": "APPROVE_REVIEW_CONTINUATION",
        "generic_governance_stage": "method_promotion_review",
        "source_of_truth_refs": {
            "source_packet_ref": "packet://tbrridge/1",
            "source_decision_ref": "decision://tbrridge/1",
            "source_governance_summary_ref": "gov://tbrridge/1",
        },
        "source_packet_ref": "packet://tbrridge/1",
        "source_decision_ref": "decision://tbrridge/1",
        "source_governance_summary_ref": "gov://tbrridge/1",
        "missing_evidence": ("power_analysis",),
        "blockers": (),
        "warnings": ("restricted_review_only",),
        "prohibited_actions": ("promote_method",),
        "boundary_statuses": _fixed_boundary(),
        "mip_allowed_uses": list(_MIP_ALLOWED_USES),
        "mip_prohibited_uses": list(_MIP_PROHIBITED_USES),
        "decision_surface_authorization_status": FIXED_AUTH,
        "trust_report_bypass_status": FIXED_BYPASS,
        "recommendation_authorization_status": FIXED_AUTH,
        "catalog_authorization_status": FIXED_AUTH,
        "production_readout_authorization_status": FIXED_AUTH,
        "production_compatibility_authorization_status": FIXED_AUTH,
        "claim_authorization_status": FIXED_AUTH,
        "method_promotion_status": FIXED_PROMO,
        "instrument_promotion_status": FIXED_PROMO,
        "spend_roi_authorization_status": FIXED_AUTH,
        "causal_lift_authorization_status": FIXED_AUTH,
        "statistical_claim_authorization_status": FIXED_AUTH,
        "lineage": {"upstream": "panel_exp"},
    }
    payload.update(overrides)
    return payload


def _apply(
    *,
    payload: dict[str, Any] | None,
    user_intent: str,
) -> MethodPromotionHandoffAnswerabilityApplicationOutput:
    return apply_method_promotion_handoff_answerability_guard(
        MethodPromotionHandoffAnswerabilityApplicationInput(
            raw_handoff_payload=payload,
            user_intent=user_intent,
        )
    )


def _assert_capabilities_false(
    output: MethodPromotionHandoffAnswerabilityApplicationOutput,
) -> None:
    for field in _CAPABILITY_FALSE:
        assert getattr(output, field) is False, field
    assert output.safe_response_guidance
    assert "answer_with_recommendation" in output.blocked_answer_modes
    assert output.lineage.get("consumer_runtime_called") is True
    assert output.lineage.get("answerability_guard_called") is True


def test_public_api_import() -> None:
    assert MethodPromotionHandoffAnswerabilityApplicationInput is not None
    assert MethodPromotionHandoffAnswerabilityApplicationOutput is not None
    assert callable(apply_method_promotion_handoff_answerability_guard)
    assert callable(serialize_method_promotion_handoff_answerability_application_output)


def test_valid_handoff_explain_governance_display_only() -> None:
    output = _apply(
        payload=_valid_payload(),
        user_intent="explain_method_governance",
    )
    assert output.consumer_accepted_for_governance_context is True
    assert output.consumer_runtime_status == (
        "CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT"
    )
    assert output.answerability_routing_status == (
        "METHOD_PROMOTION_HANDOFF_ROUTING_CONTEXT_AVAILABLE"
    )
    assert output.can_display_governance_context is True
    assert "explain_governance_context" in output.allowed_answer_modes
    assert "answer_with_recommendation" not in output.allowed_answer_modes
    _assert_capabilities_false(output)


def test_valid_handoff_planning_recommendation_blocks() -> None:
    output = _apply(
        payload=_valid_payload(),
        user_intent="ask_for_planning_recommendation",
    )
    assert output.consumer_accepted_for_governance_context is True
    assert output.answerability_routing_status == (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_PLANNING_RECOMMENDATION"
    )
    assert output.next_review_lane == "planning_review"
    _assert_capabilities_false(output)


def test_valid_handoff_budget_optimization_blocks() -> None:
    output = _apply(
        payload=_valid_payload(),
        user_intent="ask_for_budget_optimization",
    )
    assert output.answerability_routing_status == (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_BUDGET_OPTIMIZATION"
    )
    _assert_capabilities_false(output)


def test_valid_handoff_spend_reallocation_blocks() -> None:
    output = _apply(
        payload=_valid_payload(),
        user_intent="ask_for_spend_reallocation",
    )
    assert output.answerability_routing_status == (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_SPEND_REALLOCATION"
    )
    _assert_capabilities_false(output)


def test_valid_handoff_roi_roas_blocks() -> None:
    output = _apply(payload=_valid_payload(), user_intent="ask_for_roi_roas")
    assert output.answerability_routing_status == (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_ROI_ROAS"
    )
    _assert_capabilities_false(output)


def test_valid_handoff_lift_claim_blocks() -> None:
    output = _apply(payload=_valid_payload(), user_intent="ask_for_lift_claim")
    assert output.answerability_routing_status == (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CLAIM_AUTHORIZATION"
    )
    assert output.next_review_lane == "claim_authorization_review"
    _assert_capabilities_false(output)


def test_valid_handoff_production_readout_blocks() -> None:
    output = _apply(payload=_valid_payload(), user_intent="ask_for_production_readout")
    assert output.answerability_routing_status == (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CATALOG_PRODUCTION"
    )
    assert output.next_review_lane == "production_compatibility_review"
    _assert_capabilities_false(output)


def test_valid_handoff_catalog_claim_approval_blocks() -> None:
    output = _apply(
        payload=_valid_payload(),
        user_intent="ask_for_catalog_or_claim_approval",
    )
    assert output.answerability_routing_status == (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CATALOG_PRODUCTION"
    )
    assert output.next_review_lane == "catalog_review"
    _assert_capabilities_false(output)


def test_invalid_handoff_blocks() -> None:
    output = _apply(payload=None, user_intent="explain_method_governance")
    assert output.consumer_accepted_for_governance_context is False
    assert output.consumer_runtime_status == (
        "CONSUMER_RUNTIME_BLOCKED_MISSING_PAYLOAD"
    )
    assert output.answerability_routing_status == (
        "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISIONING"
    )
    assert output.can_display_governance_context is False
    assert output.consumer_validation_errors
    _assert_capabilities_false(output)


def test_serializer_json_safe() -> None:
    output = _apply(
        payload=_valid_payload(),
        user_intent="explain_method_governance",
    )
    serialized = serialize_method_promotion_handoff_answerability_application_output(
        output
    )
    json.dumps(serialized)
    assert isinstance(serialized["allowed_answer_modes"], list)
    assert isinstance(serialized["blocked_answer_modes"], list)
    assert serialized["can_generate_recommendation"] is False


def test_doc_and_summary_flags() -> None:
    assert _DOC.is_file()
    content = _DOC.read_text(encoding="utf-8")
    assert _ARTIFACT in content
    assert _VERDICT in content
    assert _NEXT in content
    assert "apply_method_promotion_handoff_answerability_guard" in content
    assert "Only run the checkpoint if the next step is LLM/answer integration" in content

    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == _ARTIFACT
    assert summary["recommended_next_artifact"] == _NEXT
    assert summary["final_verdict"] == _VERDICT
    assert summary["application_module_added"] == (
        "mip.contracts.method_promotion_handoff_answerability_application"
    )
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag
    text = _SUMMARY.read_text(encoding="utf-8")
    for pattern in _FORBIDDEN_TRUE_PATTERNS:
        assert re.search(pattern, text) is None, pattern


def test_roadmap_and_integration_strategy_reference_artifact() -> None:
    assert _ARTIFACT in _ROADMAP_EXEC.read_text(encoding="utf-8")
    assert _ARTIFACT in _REPO_INTEGRATION.read_text(encoding="utf-8")
