"""Structural checks for MIP method promotion handoff consumer runtime application checkpoint."""

from __future__ import annotations

import json
import re
from pathlib import Path

_DOC = Path(
    "docs/contracts/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_APPLICATION_CHECKPOINT_001.md"
)
_SUMMARY = Path(
    "docs/contracts/archives/MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_APPLICATION_CHECKPOINT_001_summary.json"
)
_ROADMAP_EXEC = Path("docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md")
_REPO_INTEGRATION = Path("docs/architecture/REPO_INTEGRATION_STRATEGY.md")
_RUNTIME_MODULE = Path("src/mip/contracts/method_promotion_handoff_consumer.py")

_ARTIFACT = "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_APPLICATION_CHECKPOINT_001"
_NEXT = "MIP_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_CONTRACT_001"
_DECISION = "PROCEED_TO_METHOD_PROMOTION_HANDOFF_ROUTING_ANSWERABILITY_CONTRACT_NOT_INTEGRATION"
_VERDICT = "mip_consumer_runtime_stable_for_routing_contract_planning_not_integration"

_REQUIRED_SECTIONS = (
    "## 1. Metadata",
    "## 2. Why this checkpoint exists",
    "## 3. Runtime inventory",
    "## 4. Runtime contract conformance assessment",
    "## 5. Boundary preservation assessment",
    "## 6. Accepted behavior assessment",
    "## 7. Blocked behavior assessment",
    "## 8. Generic approval semantics assessment",
    "## 9. Integration readiness decision table",
    "## 10. Required next MIP contract before integration",
    "## 11. Decision",
    "## 12. Recommended next artifact",
    "## 13. Non-goals",
    "## 14. Validation results",
)

_TRUE_FLAGS = (
    "runtime_application_checkpoint_completed",
    "runtime_contract_conformance_assessed",
    "boundary_preservation_assessed",
    "accepted_behavior_assessed",
    "blocked_behavior_assessed",
    "generic_approval_semantics_assessed",
    "integration_readiness_assessed",
    "required_next_mip_contract_defined",
    "validator_normalizer_behavior_confirmed",
    "valid_handoff_accepted_for_governance_context_only",
    "valid_handoff_rejected_for_decisioning",
    "generic_approve_review_continuation_preserved_as_weak_context",
    "source_of_truth_boundary_preserved",
    "raw_evidence_not_scored",
    "missing_evidence_not_repaired",
    "package_source_of_truth_not_overridden",
    "ready_for_routing_contract_planning",
)

_FALSE_FLAGS = (
    "runtime_behavior_changed",
    "ready_for_answer_eligibility_integration",
    "ready_for_mip_runtime_integration_with_answers",
    "ready_for_decision_surface_construction",
    "ready_for_trust_report_bypass",
    "ready_for_recommendation_contract_generation",
    "ready_for_planning_recommendation",
    "ready_for_budget_spend_roi_recommendation",
    "ready_for_catalog_claim_production_authorization",
    "mip_integration_implemented",
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


def test_checkpoint_doc_exists() -> None:
    assert _DOC.is_file()
    content = _DOC.read_text(encoding="utf-8")
    assert _ARTIFACT in content
    assert _VERDICT in content
    assert _DECISION in content
    assert _NEXT in content
    for section in _REQUIRED_SECTIONS:
        assert section in content, section
    assert "validate_and_normalize_method_promotion_handoff" in content
    assert "MIPMethodPromotionHandoffConsumerRecord" in content
    assert "ready_for_routing_contract_planning` | **true**" in content
    assert "ready_for_answer_eligibility_integration` | **false**" in content


def test_summary_json_validates() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == _ARTIFACT
    assert summary["status"] == "completed"
    assert (
        summary["scope"]
        == "runtime_application_checkpoint_docs_tests_only_no_integration_no_decision_authorization"
    )
    assert summary["depends_on"] == [
        "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_001",
        "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_RUNTIME_CONTRACT_001",
        "MIP_METHOD_PROMOTION_HANDOFF_CONSUMER_CONTRACT_001",
    ]
    assert summary["upstream_package_commit"] == "42f4484"
    assert summary["runtime_module_reviewed"] == "mip.contracts.method_promotion_handoff_consumer"
    assert summary["decision"] == _DECISION
    assert summary["recommended_next_artifact"] == _NEXT
    assert summary["final_verdict"] == _VERDICT
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag
    text = _SUMMARY.read_text(encoding="utf-8")
    for pattern in _FORBIDDEN_TRUE_PATTERNS:
        assert re.search(pattern, text) is None, pattern


def test_runtime_checkpoint_completed_and_behavior_unchanged() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["runtime_application_checkpoint_completed"] is True
    assert summary["runtime_behavior_changed"] is False
    assert _RUNTIME_MODULE.is_file()
    # Checkpoint must not alter the runtime module in this branch worktree state
    # beyond what was already merged for RUNTIME_001.
    content = _DOC.read_text(encoding="utf-8")
    assert "Runtime module not modified by this artifact" in content


def test_assessments_and_readiness_flags() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["runtime_contract_conformance_assessed"] is True
    assert summary["boundary_preservation_assessed"] is True
    assert summary["accepted_behavior_assessed"] is True
    assert summary["blocked_behavior_assessed"] is True
    assert summary["generic_approval_semantics_assessed"] is True
    assert summary["integration_readiness_assessed"] is True
    assert summary["valid_handoff_accepted_for_governance_context_only"] is True
    assert summary["valid_handoff_rejected_for_decisioning"] is True
    assert summary["ready_for_routing_contract_planning"] is True
    assert summary["ready_for_answer_eligibility_integration"] is False
    assert summary["ready_for_decision_surface_construction"] is False
    assert summary["ready_for_trust_report_bypass"] is False
    assert summary["ready_for_recommendation_contract_generation"] is False
    assert summary["ready_for_planning_recommendation"] is False


def test_roadmap_and_integration_strategy_reference_artifact() -> None:
    assert _ARTIFACT in _ROADMAP_EXEC.read_text(encoding="utf-8")
    assert _ARTIFACT in _REPO_INTEGRATION.read_text(encoding="utf-8")
