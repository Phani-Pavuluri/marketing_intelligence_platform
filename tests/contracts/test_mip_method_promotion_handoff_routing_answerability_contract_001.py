"""Structural checks for MIP method promotion handoff routing answerability contract."""

from __future__ import annotations

import json
import re
from pathlib import Path

_DOC = Path(
    "docs/contracts/MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_CONTRACT_001.md"
)
_SUMMARY = Path(
    "docs/contracts/archives/MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_CONTRACT_001_summary.json"
)
_ROADMAP_EXEC = Path("docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md")
_REPO_INTEGRATION = Path("docs/architecture/REPO_INTEGRATION_STRATEGY.md")

_ARTIFACT = "MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_CONTRACT_001"
_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_CONTRACT_001"
_VERDICT = "routing_answerability_contract_defined_governance_context_only_no_integration"

_REQUIRED_SECTIONS = (
    "## 1. Metadata",
    "## 2. Why this contract exists",
    "## 3. Consumed object",
    "## 4. Allowed routing uses",
    "## 5. Blocked routing uses",
    "## 6. Answerability semantics",
    "## 7. Safe answer modes",
    "## 8. Routing/answerability statuses",
    "## 9. LLM orchestration guardrails",
    "## 10. Relationship to existing gates",
    "## 11. Runtime implementation stance",
    "## 12. Recommended next artifact",
    "## 13. Non-goals",
    "## 14. Validation results",
)

_ROUTING_STATUSES = (
    "METHOD_PROMOTION_HANDOFF_ROUTING_CONTEXT_AVAILABLE",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISIONING",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_PLANNING_RECOMMENDATION",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISION_SURFACE",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_TRUST_BYPASS",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_RECOMMENDATION_CONTRACT",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CLAIM_AUTHORIZATION",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CATALOG_PRODUCTION",
    "METHOD_PROMOTION_HANDOFF_ROUTING_DEFER_TO_SEPARATE_REVIEW_LANE",
)

_SAFE_MODES = (
    "explain_governance_context",
    "explain_method_review_scope",
    "explain_blockers_and_warnings",
    "explain_non_authorization_status",
    "defer_to_catalog_review",
    "defer_to_claim_authorization_review",
    "defer_to_production_compatibility_review",
    "block_unsupported_recommendation",
)

_BLOCKED_MODES = (
    "answer_with_recommendation",
    "answer_with_budget_reallocation",
    "answer_with_roi_roas_claim",
    "answer_with_causal_lift_claim",
    "answer_with_statistical_significance_claim",
    "answer_with_production_readout",
    "answer_with_decision_surface",
    "answer_with_recommendation_contract",
)

_TRUE_FLAGS = (
    "contract_defined",
    "consumed_object_defined",
    "allowed_routing_uses_defined",
    "blocked_routing_uses_defined",
    "answerability_semantics_defined",
    "safe_answer_modes_defined",
    "blocked_answer_modes_defined",
    "routing_answerability_statuses_defined",
    "llm_orchestration_guardrails_defined",
    "relationship_to_existing_gates_defined",
    "runtime_integration_deferred",
    "handoff_governance_context_only",
    "approve_review_continuation_not_answer_eligibility",
    "decision_surface_remains_separately_gated",
    "trust_report_remains_separately_required",
    "recommendation_contract_remains_separately_gated",
    "planning_answer_eligibility_remains_separate",
    "claim_catalog_production_readiness_remain_separate",
)

_FALSE_FLAGS = (
    "routing_runtime_implemented",
    "answer_eligibility_integration_implemented",
    "llm_orchestration_integration_implemented",
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


def test_contract_doc_exists() -> None:
    assert _DOC.is_file()
    content = _DOC.read_text(encoding="utf-8")
    assert _ARTIFACT in content
    assert _VERDICT in content
    assert _NEXT in content
    assert "MIPMethodPromotionHandoffConsumerRecord" in content
    for section in _REQUIRED_SECTIONS:
        assert section in content, section
    for status in _ROUTING_STATUSES:
        assert status in content, status
    for mode in _SAFE_MODES:
        assert mode in content, mode
    for mode in _BLOCKED_MODES:
        assert mode in content, mode
    assert "governance_context_display" in content
    assert "planning_answer_eligibility" in content
    assert "APPROVE_REVIEW_CONTINUATION" in content
    assert "not** answer eligibility" in content or "not answer eligibility" in content.lower()


def test_summary_json_validates() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == _ARTIFACT
    assert summary["status"] == "completed"
    assert (
        summary["scope"]
        == "routing_answerability_contract_docs_tests_only_no_runtime_integration_no_answer_eligibility"
    )
    assert summary["depends_on"] == [
        "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_APPLICATION_CHECKPOINT_001",
        "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001",
    ]
    assert summary["recommended_next_artifact"] == _NEXT
    assert summary["final_verdict"] == _VERDICT
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag
    text = _SUMMARY.read_text(encoding="utf-8")
    for pattern in _FORBIDDEN_TRUE_PATTERNS:
        assert re.search(pattern, text) is None, pattern


def test_consumed_object_and_routing_semantics_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["consumed_object_defined"] is True
    assert summary["allowed_routing_uses_defined"] is True
    assert summary["blocked_routing_uses_defined"] is True
    assert summary["answerability_semantics_defined"] is True
    assert summary["safe_answer_modes_defined"] is True
    assert summary["blocked_answer_modes_defined"] is True
    assert summary["routing_answerability_statuses_defined"] is True
    assert summary["llm_orchestration_guardrails_defined"] is True


def test_existing_gates_remain_separate_and_runtime_deferred() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["decision_surface_remains_separately_gated"] is True
    assert summary["trust_report_remains_separately_required"] is True
    assert summary["recommendation_contract_remains_separately_gated"] is True
    assert summary["planning_answer_eligibility_remains_separate"] is True
    assert summary["claim_catalog_production_readiness_remain_separate"] is True
    assert summary["runtime_integration_deferred"] is True
    assert summary["handoff_governance_context_only"] is True
    assert summary["approve_review_continuation_not_answer_eligibility"] is True
    assert summary["routing_runtime_implemented"] is False
    assert summary["answer_eligibility_integration_implemented"] is False
    assert summary["llm_orchestration_integration_implemented"] is False


def test_roadmap_and_integration_strategy_reference_artifact() -> None:
    assert _ARTIFACT in _ROADMAP_EXEC.read_text(encoding="utf-8")
    assert _ARTIFACT in _REPO_INTEGRATION.read_text(encoding="utf-8")
