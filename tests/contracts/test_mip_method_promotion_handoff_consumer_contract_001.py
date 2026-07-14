"""Structural checks for MIP method promotion handoff consumer contract."""

from __future__ import annotations

import json
import re
from pathlib import Path

_DOC = Path("docs/contracts/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001.md")
_SUMMARY = Path(
    "docs/contracts/archives/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001_summary.json"
)
_ROADMAP_EXEC = Path("docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md")
_REPO_INTEGRATION = Path("docs/architecture/REPO_INTEGRATION_STRATEGY.md")

_REQUIRED_SECTIONS = (
    "## 1. Metadata",
    "## 2. Why this contract exists",
    "## 3. Upstream object consumed",
    "## 4. MIP consumer object",
    "## 5. Required validation rules",
    "## 6. Fixed MIP non-authorization statuses",
    "## 7. MIP allowed actions",
    "## 8. MIP blocked actions",
    "## 9. Generic decision semantics in MIP",
    "## 10. Consumer statuses",
    "## 11. Routing semantics",
    "## 12. Relationship to existing MIP contracts",
    "## 13. Runtime implementation stance",
    "## 14. Recommended next artifact",
    "## 15. Non-goals",
    "## 16. Validation results",
)

_FIXED_STATUSES = (
    "NOT_AUTHORIZED_BY_METHOD_PROMOTION_HANDOFF",
    "NOT_BYPASSED_BY_METHOD_PROMOTION_HANDOFF",
    "NOT_PROMOTED_BY_METHOD_PROMOTION_HANDOFF",
)

_CONSUMER_STATUSES = (
    "CONSUMER_RECORD_READY_FOR_GOVERNANCE_CONTEXT",
    "CONSUMER_RECORD_BLOCKED_MISSING_HANDOFF",
    "CONSUMER_RECORD_BLOCKED_UNSUPPORTED_SOURCE_PACKAGE",
    "CONSUMER_RECORD_BLOCKED_MISSING_PROFILE_ID",
    "CONSUMER_RECORD_BLOCKED_MISSING_CANONICAL_IDENTITY",
    "CONSUMER_RECORD_BLOCKED_MISSING_DECISION_SCOPE",
    "CONSUMER_RECORD_BLOCKED_MISSING_SOURCE_OF_TRUTH_REFS",
    "CONSUMER_RECORD_BLOCKED_MISSING_BOUNDARY_STATUSES",
    "CONSUMER_RECORD_BLOCKED_MISSING_ALLOWED_USES",
    "CONSUMER_RECORD_BLOCKED_MISSING_PROHIBITED_USES",
    "CONSUMER_RECORD_BLOCKED_AUTHORIZATION_STATUS_WEAKENED",
    "CONSUMER_RECORD_BLOCKED_TRUST_BYPASS_ATTEMPT",
    "CONSUMER_RECORD_BLOCKED_RECOMMENDATION_AUTHORIZATION_ATTEMPT",
    "CONSUMER_RECORD_BLOCKED_DECISION_SURFACE_AUTHORIZATION_ATTEMPT",
    "CONSUMER_RECORD_BLOCKED_CLAIM_OR_PRODUCTION_AUTHORIZATION_ATTEMPT",
    "CONSUMER_RECORD_BLOCKED_PROMOTION_ATTEMPT",
)

_TRUE_FLAGS = (
    "consumer_contract_defined",
    "consumer_object_defined",
    "required_validation_rules_defined",
    "fixed_mip_non_authorization_statuses_required",
    "mip_allowed_actions_defined",
    "mip_blocked_actions_defined",
    "generic_approve_review_continuation_semantics_defined_for_mip",
    "consumer_statuses_defined",
    "routing_semantics_defined",
    "relationship_to_existing_mip_contracts_defined",
    "runtime_implementation_deferred",
    "decision_surface_remains_separately_gated",
    "trust_report_remains_separately_required",
    "recommendation_contract_remains_separately_gated",
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

_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001"
_VERDICT = "mip_consumer_contract_defined_no_runtime_no_decision_authorization"


def test_consumer_contract_doc_exists() -> None:
    assert _DOC.is_file()
    content = _DOC.read_text(encoding="utf-8")
    assert "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001" in content
    assert "MethodPromotionGenericAdapterMIPHandoff" in content
    assert "MIPMethodPromotionHandoffConsumerRecord" in content
    assert _VERDICT in content


def test_summary_json_validates() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001"
    assert summary["status"] == "completed"
    assert summary["artifact_type"] == "mip_method_promotion_handoff_consumer_contract"
    assert (
        summary["scope"]
        == "mip_side_consumer_contract_docs_tests_only_"
        "no_runtime_integration_no_decision_authorization"
    )
    assert (
        summary["upstream_package_artifact"]
        == "METHOD_PROMOTION_GENERIC_ADAPTER_MIP_HANDOFF_RUNTIME_APPLICATION_CHECKPOINT_001"
    )
    assert summary["upstream_package_commit"] == "42f4484"
    assert summary["upstream_package_source"] == "panel_exp"
    assert summary["final_verdict"] == _VERDICT


def test_required_sections_present() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


def test_consumer_contract_and_object_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["consumer_contract_defined"] is True
    assert summary["consumer_object_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    assert "MIPMethodPromotionHandoffConsumerRecord" in content
    assert "consumer_record_id" in content
    assert "received_handoff_id" in content


def test_validation_rules_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["required_validation_rules_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    assert "source_package != panel_exp" in content
    assert "generic_decision_status" in content
    assert "missing" in content.lower()
    assert "prohibited uses are absent or weakened" in content


def test_fixed_mip_non_authorization_statuses_required() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["fixed_mip_non_authorization_statuses_required"] is True
    content = _DOC.read_text(encoding="utf-8")
    for status in _FIXED_STATUSES:
        assert status in content, status


def test_allowed_and_blocked_actions_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["mip_allowed_actions_defined"] is True
    assert summary["mip_blocked_actions_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    assert "display governance context" in content
    assert "create DecisionSurface from handoff" in content
    assert "generate RecommendationContract" in content
    assert "bypass TrustReport" in content


def test_generic_approve_semantics_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["generic_approve_review_continuation_semantics_defined_for_mip"] is True
    content = _DOC.read_text(encoding="utf-8")
    assert "APPROVE_REVIEW_CONTINUATION" in content
    assert "does not mean" in content.lower()
    assert "DecisionSurface readiness" in content


def test_consumer_statuses_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["consumer_statuses_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    for status in _CONSUMER_STATUSES:
        assert status in content, status


def test_routing_semantics_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["routing_semantics_defined"] is True
    content = _DOC.read_text(encoding="utf-8")
    assert "governance context route" in content
    assert "planning recommendation route" in content
    assert "DecisionSurface approval route" in content


def test_relationship_to_mip_contracts_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["relationship_to_existing_mip_contracts_defined"] is True
    assert summary["decision_surface_remains_separately_gated"] is True
    assert summary["trust_report_remains_separately_required"] is True
    assert summary["recommendation_contract_remains_separately_gated"] is True
    assert summary["claim_catalog_production_readiness_remain_separate"] is True
    assert summary["handoff_is_governance_context_only"] is True
    content = _DOC.read_text(encoding="utf-8")
    assert "DecisionSurface" in content
    assert "TrustReport" in content
    assert "RecommendationContract" in content
    assert "governance context only" in content.lower()


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


def test_docs_registry_references_artifact() -> None:
    assert "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001" in _ROADMAP_EXEC.read_text(
        encoding="utf-8"
    )
    assert "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001" in _REPO_INTEGRATION.read_text(
        encoding="utf-8"
    )
