"""Structural checks for MIP method promotion handoff routing answerability runtime contract."""

from __future__ import annotations

import json
import re
from pathlib import Path

_DOC = Path(
    "docs/contracts/MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_CONTRACT_001.md"
)
_SUMMARY = Path(
    "docs/contracts/archives/MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_CONTRACT_001_summary.json"
)
_ROADMAP_EXEC = Path("docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md")
_REPO_INTEGRATION = Path("docs/architecture/REPO_INTEGRATION_STRATEGY.md")

_ARTIFACT = "MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_CONTRACT_001"
_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_RUNTIME_001"
_VERDICT = "routing_answerability_runtime_contract_defined_no_runtime_no_answer_eligibility"

_REQUIRED_SECTIONS = (
    "## 1. Metadata",
    "## 2. Why this runtime contract exists",
    "## 3. Runtime boundary",
    "## 4. Runtime input contract",
    "## 5. Runtime output contract",
    "## 6. Routing statuses",
    "## 7. Allowed answer modes",
    "## 8. Blocked answer modes",
    "## 9. Deterministic decision rules",
    "## 10. Safe response guidance",
    "## 11. Relationship to existing gates",
    "## 12. Recommended next artifact",
    "## 13. Non-goals",
    "## 14. Validation results",
)

_ROUTING_STATUSES = (
    "METHOD_PROMOTION_HANDOFF_ROUTING_CONTEXT_AVAILABLE",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISIONING",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_PLANNING_RECOMMENDATION",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_BUDGET_OPTIMIZATION",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_SPEND_REALLOCATION",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_ROI_ROAS",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_DECISION_SURFACE",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_TRUST_BYPASS",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_RECOMMENDATION_CONTRACT",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CLAIM_AUTHORIZATION",
    "METHOD_PROMOTION_HANDOFF_ROUTING_BLOCKED_FOR_CATALOG_PRODUCTION",
    "METHOD_PROMOTION_HANDOFF_ROUTING_DEFER_TO_SEPARATE_REVIEW_LANE",
)

_TRUE_FLAGS = (
    "runtime_contract_defined",
    "runtime_input_contract_defined",
    "runtime_output_contract_defined",
    "routing_statuses_defined",
    "allowed_answer_modes_defined",
    "blocked_answer_modes_defined",
    "deterministic_decision_rules_defined",
    "safe_response_guidance_defined",
    "relationship_to_existing_gates_defined",
    "runtime_implementation_deferred",
    "handoff_governance_context_only",
    "approve_review_continuation_not_answer_eligibility",
    "non_authorization_statuses_dominate",
    "blocked_actions_dominate",
    "prohibited_actions_dominate",
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
    assert "MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeInput" in content
    assert "MIPMethodPromotionHandoffRoutingAnswerabilityRuntimeOutput" in content
    assert "MIPMethodPromotionHandoffConsumerRecord" in content
    for section in _REQUIRED_SECTIONS:
        assert section in content, section
    for status in _ROUTING_STATUSES:
        assert status in content, status
    assert "explain_governance_context" in content
    assert "answer_with_recommendation" in content
    assert "APPROVE_REVIEW_CONTINUATION" in content
    assert "not** answer eligibility" in content or "not answer eligibility" in content.lower()
    assert "Non-authorization statuses always dominate" in content
    assert "consumer_blocked_actions` always dominate" in content
    assert "`prohibited_actions` always dominate" in content
    assert "This handoff can be used only as governance context." in content


def test_summary_json_validates() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == _ARTIFACT
    assert summary["status"] == "completed"
    assert (
        summary["scope"]
        == "routing_answerability_runtime_contract_docs_tests_only_no_runtime_no_answer_eligibility"
    )
    assert summary["depends_on"] == [
        "MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_CONTRACT_001",
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


def test_runtime_input_output_and_rules_defined() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["runtime_input_contract_defined"] is True
    assert summary["runtime_output_contract_defined"] is True
    assert summary["routing_statuses_defined"] is True
    assert summary["allowed_answer_modes_defined"] is True
    assert summary["blocked_answer_modes_defined"] is True
    assert summary["deterministic_decision_rules_defined"] is True
    assert summary["safe_response_guidance_defined"] is True
    assert summary["non_authorization_statuses_dominate"] is True
    assert summary["blocked_actions_dominate"] is True
    assert summary["prohibited_actions_dominate"] is True
    assert summary["approve_review_continuation_not_answer_eligibility"] is True


def test_existing_gates_remain_separate_and_runtime_deferred() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["decision_surface_remains_separately_gated"] is True
    assert summary["trust_report_remains_separately_required"] is True
    assert summary["recommendation_contract_remains_separately_gated"] is True
    assert summary["planning_answer_eligibility_remains_separate"] is True
    assert summary["claim_catalog_production_readiness_remain_separate"] is True
    assert summary["runtime_implementation_deferred"] is True
    assert summary["handoff_governance_context_only"] is True
    assert summary["routing_runtime_implemented"] is False
    assert summary["answer_eligibility_integration_implemented"] is False
    assert summary["llm_orchestration_integration_implemented"] is False


def test_roadmap_and_integration_strategy_reference_artifact() -> None:
    assert _ARTIFACT in _ROADMAP_EXEC.read_text(encoding="utf-8")
    assert _ARTIFACT in _REPO_INTEGRATION.read_text(encoding="utf-8")
