"""Structural checks for MIP method promotion handoff consumer runtime contract."""

from __future__ import annotations

import json
import re
from pathlib import Path

_DOC = Path("docs/contracts/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001.md")
_SUMMARY = Path(
    "docs/contracts/archives/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001_summary.json"
)
_ROADMAP_EXEC = Path("docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md")
_REPO_INTEGRATION = Path("docs/architecture/REPO_INTEGRATION_STRATEGY.md")

_REQUIRED_SECTIONS = (
    "## 1. Metadata",
    "## 2. Why this runtime contract exists",
    "## 3. Runtime contract boundary",
    "## 4. Runtime input contract",
    "## 5. Runtime output contract",
    "## 6. MIP consumer record normalized fields",
    "## 7. Required validation rules",
    "## 8. Fixed non-authorization statuses",
    "## 9. Consumer runtime statuses",
    "## 10. Routing hints",
    "## 11. Generic approval handling",
    "## 12. Relationship to MIP gates",
    "## 13. Required runtime tests for future implementation",
    "## 14. Runtime implementation stance",
    "## 15. Recommended next artifact",
    "## 16. Non-goals",
    "## 17. Validation results",
)

_FIXED_STATUSES = (
    "NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF",
    "NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF",
    "NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF",
)

_RUNTIME_STATUSES = (
    "CONSUMER_RUNTIME_READY_FOR_GOVERNANCE_CONTEXT",
    "CONSUMER_RUNTIME_BLOCKED_MISSING_PAYLOAD",
    "CONSUMER_RUNTIME_BLOCKED_UNSUPPORTED_SOURCE_PACKAGE",
    "CONSUMER_RUNTIME_BLOCKED_MISSING_HANDOFF_ID",
    "CONSUMER_RUNTIME_BLOCKED_MISSING_PROFILE_ID",
    "CONSUMER_RUNTIME_BLOCKED_MISSING_CANONICAL_IDENTITY",
    "CONSUMER_RUNTIME_BLOCKED_MISSING_DECISION_SCOPE",
    "CONSUMER_RUNTIME_BLOCKED_MISSING_GENERIC_DECISION_STATUS",
    "CONSUMER_RUNTIME_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS",
    "CONSUMER_RUNTIME_BLOCKED_MISSING_BOUNDARY_STATUSES",
    "CONSUMER_RUNTIME_BLOCKED_MISSING_ALLOWED_USES",
    "CONSUMER_RUNTIME_BLOCKED_MISSING_PROHIBITED_USES",
    "CONSUMER_RUNTIME_BLOCKED_AUTHORIZATION_STATUS_WEAKENED",
    "CONSUMER_RUNTIME_BLOCKED_TRUST_BYPASS_ATTEMPT",
    "CONSUMER_RUNTIME_BLOCKED_RECOMMENDATION_AUTHORIZATION_ATTEMPT",
    "CONSUMER_RUNTIME_BLOCKED_DECISION_SURFACE_AUTHORIZATION_ATTEMPT",
    "CONSUMER_RUNTIME_BLOCKED_CLAIM_OR_PRODUCTION_AUTHORIZATION_ATTEMPT",
    "CONSUMER_RUNTIME_BLOCKED_PROMOTION_ATTEMPT",
    "CONSUMER_RUNTIME_BLOCKED_PLANNING_RECOMMENDATION_ATTEMPT",
    "CONSUMER_RUNTIME_BLOCKED_SPEND_ROI_AUTHORIZATION_ATTEMPT",
    "CONSUMER_RUNTIME_BLOCKED_SOURCE_OF_TRUTH_OVERRIDE_ATTEMPT",
    "CONSUMER_RUNTIME_BLOCKED_GENERIC_APPROVAL_UPGRADE_ATTEMPT",
)

_ALLOWED_ROUTES = (
    "ROUTE_TO_GOVERNANCE_CONTEXT_DISPLAY",
    "ROUTE_TO_DIAGNOSTIC_EXPLANATION",
    "ROUTE_TO_CATALOG_REVIEW",
    "ROUTE_TO_CLAIM_AUTHORIZATION_REVIEW",
    "ROUTE_TO_PRODUCTION_COMPATIBILITY_REVIEW",
    "ROUTE_TO_UNSUPPORTED_RECOMMENDATION_BLOCK",
)

_BLOCKED_ROUTES = (
    "ROUTE_TO_DECISION_SURFACE_APPROVAL",
    "ROUTE_TO_TRUST_REPORT_BYPASS",
    "ROUTE_TO_RECOMMENDATION_CONTRACT",
    "ROUTE_TO_PLANNING_RECOMMENDATION",
    "ROUTE_TO_BUDGET_OPTIMIZER",
    "ROUTE_TO_SPEND_REALLOCATION",
    "ROUTE_TO_ROI_ROAS_RECOMMENDATION",
    "ROUTE_TO_PRODUCTION_READOUT",
)

_TRUE_FLAGS = (
    "runtime_contract_defined",
    "runtime_input_contract_defined",
    "runtime_output_contract_defined",
    "consumer_record_normalization_defined",
    "required_validation_rules_defined",
    "fixed_mip_non_authorization_statuses_required",
    "consumer_runtime_statuses_defined",
    "routing_hints_defined",
    "generic_approval_handling_defined",
    "relationship_to_mip_gates_defined",
    "future_runtime_tests_defined",
    "runtime_implementation_deferred",
    "decision_surface_remains_separately_gated",
    "trust_report_remains_separately_required",
    "recommendation_contract_remains_separately_gated",
    "planning_answer_eligibility_remains_separately_gated",
    "claim_catalog_production_readiness_remain_separate",
    "handoff_is_governance_context_only",
)

_FALSE_FLAGS = (
    "mip_runtime_implemented",
    "mip_integration_implemented",
    "package_runtime_changed",
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

_FORBIDDEN_TRUE_PATTERNS = tuple(rf'"{flag}"\s*:\s*true' for flag in _FALSE_FLAGS)

_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001"
_VERDICT = "mip_consumer_runtime_contract_defined_no_runtime_no_decision_authorization"


def test_runtime_contract_doc_exists() -> None:
    assert _DOC.is_file()
    content = _DOC.read_text(encoding="utf-8")
    assert "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001" in content
    assert "MIPMethodPromotionHandoffConsumerRuntimeInput" in content
    assert "MIPMethodPromotionHandoffConsumerRuntimeOutput" in content
    assert "MIPMethodPromotionHandoffConsumerRecord" in content
    assert _VERDICT in content


def test_summary_json_validates() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001"
    assert summary["status"] == "completed"
    assert summary["artifact_type"] == "mip_method_promotion_handoff_consumer_runtime_contract"
    assert (
        summary["scope"]
        == "mip_side_runtime_contract_docs_tests_only_no_runtime_implementation_no_decision_authorization"
    )
    assert summary["depends_on"] == ["MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001"]
    assert (
        summary["upstream_package_artifact"]
        == "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001"
    )
    assert summary["upstream_package_commit"] == "42f4484"
    assert summary["final_verdict"] == _VERDICT


def test_required_sections_present() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


def test_runtime_input_output_contracts_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["runtime_contract_defined"] is True
    assert summary["runtime_input_contract_defined"] is True
    assert summary["runtime_output_contract_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    assert "raw_handoff_payload" in content
    assert "accepted_for_governance_context" in content
    assert "rejected_for_decisioning" in content


def test_consumer_record_normalization_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["consumer_record_normalization_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    assert "consumer_record_id" in content
    assert "received_handoff_id" in content
    assert "created_from_handoff" in content


def test_required_validation_rules_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["required_validation_rules_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    assert "source_package != panel_exp" in content
    assert "generic_decision_status" in content
    assert "APPROVE_REVIEW_CONTINUATION" in content


def test_fixed_mip_non_authorization_statuses_required() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["fixed_mip_non_authorization_statuses_required"] is True
    content = _DOC.read_text(encoding="utf-8")
    for status in _FIXED_STATUSES:
        assert status in content, status


def test_consumer_runtime_statuses_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["consumer_runtime_statuses_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    for status in _RUNTIME_STATUSES:
        assert status in content, status


def test_routing_hints_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["routing_hints_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    for route in _ALLOWED_ROUTES:
        assert route in content, route
    for route in _BLOCKED_ROUTES:
        assert route in content, route


def test_generic_approval_handling_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["generic_approval_handling_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    assert "weak governance context only" in content.lower()
    assert "planning answer eligibility" in content.lower()


def test_relationship_to_mip_gates_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["relationship_to_mip_gates_defined"] is True
    assert summary["decision_surface_remains_separately_gated"] is True
    assert summary["trust_report_remains_separately_required"] is True
    assert summary["recommendation_contract_remains_separately_gated"] is True
    assert summary["planning_answer_eligibility_remains_separately_gated"] is True
    assert summary["claim_catalog_production_readiness_remain_separate"] is True
    assert summary["handoff_is_governance_context_only"] is True


def test_future_runtime_tests_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["future_runtime_tests_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    assert "valid handoff normalizes into consumer record" in content
    assert "blocked routes are never emitted" in content


def test_runtime_deferred_and_forbidden_flags_false() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["runtime_implementation_deferred"] is True
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag


def test_summary_forbidden_flags_not_true_in_raw_json() -> None:
    raw = _SUMMARY.read_text(encoding="utf-8")
    for pattern in _FORBIDDEN_TRUE_PATTERNS:
        assert not re.search(pattern, raw), f"forbidden pattern matched: {pattern}"


def test_recommended_next_artifact_exact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["recommended_next_artifact"] == _NEXT
    assert _NEXT in _DOC.read_text(encoding="utf-8")


def test_docs_roadmap_and_integration_strategy_reference_artifact() -> None:
    assert (
        "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001"
        in _ROADMAP_EXEC.read_text(encoding="utf-8")
    )
    assert (
        "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001"
        in _REPO_INTEGRATION.read_text(encoding="utf-8")
    )
