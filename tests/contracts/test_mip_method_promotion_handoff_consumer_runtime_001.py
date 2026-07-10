"""Runtime checks for MIP method promotion handoff consumer runtime."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from mip.contracts.method_promotion_handoff_consumer import (
    CONSUMER_ALLOWED_ACTIONS,
    CONSUMER_BLOCKED_ACTIONS,
    FIXED_AUTH,
    FIXED_BYPASS,
    FIXED_PROMO,
    MIPMethodPromotionHandoffAuthorizationStatus,
    MIPMethodPromotionHandoffBypassStatus,
    MIPMethodPromotionHandoffConsumerRecord,
    MIPMethodPromotionHandoffConsumerRuntimeInput,
    MIPMethodPromotionHandoffConsumerRuntimeOutput,
    MIPMethodPromotionHandoffConsumerStatus,
    MIPMethodPromotionHandoffPromotionStatus,
    MIPMethodPromotionHandoffRoutingHint,
    serialize_method_promotion_handoff_consumer_record,
    validate_and_normalize_method_promotion_handoff,
)

_DOC = Path("docs/contracts/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001.md")
_SUMMARY = Path(
    "docs/contracts/archives/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001_summary.json"
)
_ROADMAP_EXEC = Path("docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md")
_REPO_INTEGRATION = Path("docs/architecture/REPO_INTEGRATION_STRATEGY.md")

_ARTIFACT = "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001"
_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_APPLICATION_CHECKPOINT_001"
_VERDICT = "mip_consumer_runtime_implemented_as_validator_normalizer_no_decision_authorization"

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

_TRUE_FLAGS = (
    "runtime_implemented",
    "validator_implemented",
    "normalizer_implemented",
    "serializer_implemented",
    "consumer_record_implemented",
    "runtime_input_output_implemented",
    "fixed_mip_non_authorization_statuses_enforced",
    "allowed_actions_enforced",
    "blocked_actions_enforced",
    "consumer_statuses_implemented",
    "routing_hints_implemented",
    "generic_approve_review_continuation_preserved_as_weak_context",
    "valid_handoff_accepted_for_governance_context_only",
    "valid_handoff_rejected_for_decisioning",
    "missing_payload_blocks",
    "unsupported_source_package_blocks",
    "missing_required_fields_block",
    "weakened_authorization_statuses_block",
    "trust_report_bypass_attempt_blocks",
    "recommendation_authorization_attempt_blocks",
    "decision_surface_authorization_attempt_blocks",
    "claim_or_production_authorization_attempt_blocks",
    "promotion_attempt_blocks",
    "planning_recommendation_attempt_blocks",
    "spend_roi_authorization_attempt_blocks",
    "source_of_truth_override_attempt_blocks",
    "generic_approval_upgrade_attempt_blocks",
    "raw_evidence_not_scored",
    "missing_evidence_not_repaired",
    "package_source_of_truth_not_overridden",
)

_FALSE_FLAGS = (
    "mip_integration_implemented",
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
)

_FORBIDDEN_TRUE_PATTERNS = tuple(rf'"{flag}"\s*:\s*true' for flag in _FALSE_FLAGS)

_MIP_ALLOWED_USES = tuple(sorted({
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
}))

_MIP_PROHIBITED_USES = tuple(sorted({
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
}))


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


def _run(payload: dict[str, Any] | None, **input_kwargs: Any):
    return validate_and_normalize_method_promotion_handoff(
        MIPMethodPromotionHandoffConsumerRuntimeInput(
            raw_handoff_payload=payload,
            **input_kwargs,
        )
    )


def test_public_api_import() -> None:
    assert MIPMethodPromotionHandoffConsumerRuntimeInput is not None
    assert MIPMethodPromotionHandoffConsumerRuntimeOutput is not None
    assert MIPMethodPromotionHandoffConsumerRecord is not None
    assert MIPMethodPromotionHandoffConsumerStatus is not None
    assert MIPMethodPromotionHandoffRoutingHint is not None
    assert MIPMethodPromotionHandoffAuthorizationStatus is not None
    assert MIPMethodPromotionHandoffBypassStatus is not None
    assert MIPMethodPromotionHandoffPromotionStatus is not None
    assert callable(validate_and_normalize_method_promotion_handoff)
    assert callable(serialize_method_promotion_handoff_consumer_record)


def test_valid_handoff_normalizes_into_consumer_record() -> None:
    result = _run(_valid_payload())
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT
    )
    assert result.consumer_record is not None
    assert result.consumer_record.received_handoff_id == "handoff-tbrridge-001"
    assert result.consumer_record.source_package == "panel_exp"
    assert result.consumer_record.profile_id == "tbrridge_restricted_review_v1"
    assert result.consumer_record.created_from_handoff is True


def test_accepted_for_governance_context_and_rejected_for_decisioning() -> None:
    result = _run(_valid_payload())
    assert result.accepted_for_governance_context is True
    assert result.rejected_for_decisioning is True


def test_fixed_non_authorization_statuses_preserved() -> None:
    record = _run(_valid_payload()).consumer_record
    assert record is not None
    for field in _FIXED_STATUS_FIELDS:
        assert getattr(record, field) == FIXED_AUTH
    assert record.trust_report_bypass_status == FIXED_BYPASS
    assert record.method_promotion_status == FIXED_PROMO
    assert record.instrument_promotion_status == FIXED_PROMO


def test_allowed_and_blocked_actions_exact() -> None:
    record = _run(_valid_payload()).consumer_record
    assert record is not None
    assert record.consumer_allowed_actions == CONSUMER_ALLOWED_ACTIONS
    assert record.consumer_blocked_actions == CONSUMER_BLOCKED_ACTIONS


def test_routing_hint_governance_display_for_valid_record() -> None:
    result = _run(_valid_payload())
    assert result.routing_hint == (
        MIPMethodPromotionHandoffRoutingHint.ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY
    )
    assert result.consumer_record is not None
    assert result.consumer_record.routing_hint == (
        MIPMethodPromotionHandoffRoutingHint.ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY
    )


def test_approve_review_continuation_remains_weak_context() -> None:
    result = _run(_valid_payload(generic_decision_status="APPROVE_REVIEW_CONTINUATION"))
    assert result.accepted_for_governance_context is True
    assert result.rejected_for_decisioning is True
    assert result.consumer_record is not None
    assert result.consumer_record.generic_decision_status == "APPROVE_REVIEW_CONTINUATION"
    assert any("weak" in w.lower() for w in result.validation_warnings)


def test_missing_payload_blocks() -> None:
    result = _run(None)
    assert result.consumer_record is None
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_PAYLOAD
    )
    assert result.accepted_for_governance_context is False
    assert result.rejected_for_decisioning is True


def test_unsupported_source_package_blocks() -> None:
    result = _run(_valid_payload(source_package="other_pkg"))
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_UNSUPPORTED_SOURCE_PACKAGE
    )


def test_missing_handoff_id_blocks() -> None:
    payload = _valid_payload()
    del payload["handoff_id"]
    result = _run(payload)
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_HANDOFF_ID
    )


def test_missing_profile_id_blocks() -> None:
    payload = _valid_payload()
    del payload["profile_id"]
    result = _run(payload)
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_PROFILE_ID
    )


def test_missing_canonical_identity_blocks() -> None:
    payload = _valid_payload()
    del payload["canonical_identity"]
    result = _run(payload)
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_CANONICAL_IDENTITY
    )


def test_missing_decision_scope_blocks() -> None:
    payload = _valid_payload()
    del payload["decision_scope"]
    result = _run(payload)
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_DECISION_SCOPE
    )


def test_missing_generic_decision_status_blocks() -> None:
    payload = _valid_payload()
    del payload["generic_decision_status"]
    result = _run(payload)
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_GENERIC_DECISION_STATUS
    )


def test_missing_source_of_truth_refs_blocks() -> None:
    payload = _valid_payload()
    del payload["source_of_truth_refs"]
    result = _run(payload)
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS
    )


def test_missing_boundary_statuses_blocks() -> None:
    payload = _valid_payload()
    # Remove boundary and top-level fixed statuses so merge cannot recover.
    del payload["boundary_statuses"]
    for field in list(_FIXED_STATUS_FIELDS) + [
        "trust_report_bypass_status",
        "method_promotion_status",
        "instrument_promotion_status",
    ]:
        payload.pop(field, None)
    result = _run(payload)
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_BOUNDARY_STATUSES
    )


def test_missing_allowed_uses_blocks() -> None:
    payload = _valid_payload()
    del payload["mip_allowed_uses"]
    result = _run(payload)
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_ALLOWED_USES
    )


def test_missing_prohibited_uses_blocks() -> None:
    payload = _valid_payload()
    del payload["mip_prohibited_uses"]
    result = _run(payload)
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_MISSING_PROHIBITED_USES
    )


def test_weakened_authorization_status_blocks() -> None:
    payload = _valid_payload()
    payload["decision_surface_authorization_status"] = "AUTHORIZED"
    payload["boundary_statuses"] = deepcopy(payload["boundary_statuses"])
    payload["boundary_statuses"]["decision_surface_authorization_status"] = "AUTHORIZED"
    result = _run(payload)
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_AUTHORIZATION_STATUS_WEAKENED
    )


def test_trust_report_bypass_attempt_blocks() -> None:
    result = _run(_valid_payload(bypass_trust_report=True))
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_TRUST_BYPASS_ATTEMPT
    )
    assert result.routing_hint == (
        MIPMethodPromotionHandoffRoutingHint.ROUTE_BLOCKED_TRUST_REPORT_BYPASS
    )


def test_recommendation_contract_attempt_blocks() -> None:
    result = _run(_valid_payload(generate_recommendation_contract=True))
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_RECOMMENDATION_AUTHORIZATION_ATTEMPT
    )


def test_decision_surface_attempt_blocks() -> None:
    result = _run(_valid_payload(create_decision_surface=True))
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_DECISION_SURFACE_AUTHORIZATION_ATTEMPT
    )


def test_claim_or_production_authorization_attempt_blocks() -> None:
    result = _run(_valid_payload(authorize_claims=True))
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_CLAIM_OR_PRODUCTION_AUTHORIZATION_ATTEMPT
    )


def test_promotion_attempt_blocks() -> None:
    result = _run(_valid_payload(promote_method=True))
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_PROMOTION_ATTEMPT
    )


def test_planning_recommendation_attempt_blocks() -> None:
    result = _run(_valid_payload(enable_planning_answer_eligibility=True))
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_PLANNING_RECOMMENDATION_ATTEMPT
    )


def test_spend_roi_attempt_blocks() -> None:
    result = _run(_valid_payload(roi_roas_authorized=True))
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_SPEND_ROI_AUTHORIZATION_ATTEMPT
    )


def test_source_of_truth_override_attempt_blocks() -> None:
    result = _run(_valid_payload(override_source_packet_runtime=True))
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_SOURCE_OF_TRUTH_OVERRIDE_ATTEMPT
    )


def test_generic_approval_upgrade_attempt_blocks() -> None:
    result = _run(
        _valid_payload(
            generic_decision_status="APPROVE_REVIEW_CONTINUATION",
            upgrade_approve_review_continuation_to_readiness=True,
        )
    )
    assert result.consumer_status == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_BLOCKED_GENERIC_APPROVAL_UPGRADE_ATTEMPT
    )


def test_serializer_json_safe() -> None:
    record = _run(_valid_payload()).consumer_record
    assert record is not None
    serialized = serialize_method_promotion_handoff_consumer_record(record)
    assert isinstance(serialized, dict)
    json.dumps(serialized)
    assert isinstance(serialized["consumer_allowed_actions"], list)
    assert isinstance(serialized["consumer_blocked_actions"], list)
    assert serialized["decision_surface_authorization_status"] == FIXED_AUTH
    assert serialized["consumer_status"] == (
        MIPMethodPromotionHandoffConsumerStatus.CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT.value
    )


def test_runtime_doc_exists() -> None:
    assert _DOC.is_file()
    content = _DOC.read_text(encoding="utf-8")
    assert _ARTIFACT in content
    assert "validate_and_normalize_method_promotion_handoff" in content
    assert _VERDICT in content
    assert _NEXT in content


def test_summary_json_governance_flags() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == _ARTIFACT
    assert summary["status"] == "completed"
    assert summary["final_verdict"] == _VERDICT
    assert summary["recommended_next_artifact"] == _NEXT
    assert summary["upstream_package_commit"] == "42f4484"
    assert summary["runtime_module_added"] == "mip.contracts.method_promotion_handoff_consumer"
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
