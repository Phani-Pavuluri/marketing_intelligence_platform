"""Lightweight structural checks for agent answerability fallback contract plan."""

from __future__ import annotations

import json
from pathlib import Path

_PLAN = Path(
    "docs/architecture/AGENT_ANSWERABILITY_AND_FALLBACK_CONTRACT_PLAN_001.md"
)
_SUMMARY = Path(
    "docs/architecture/archives/"
    "agent_answerability_fallback_contract_plan_001_summary.json"
)

_REQUIRED_SECTIONS = (
    "## 4. Top-level answerability state machine",
    "## 5. Answerability decision contract",
    "## 6. Evidence levels",
    "## 7. Claim taxonomy",
    "## 8. Tool availability and fallback behavior",
    "## 9. UX-safe fallback responses",
    "## 10. Anti-hardcoding principle",
    "## 11. Relationship to deterministic reports",
    "## 12. Relationship to core ML",
    "## 13. Evaluation harness plan",
    "## 15. Stop/go criteria",
)

_ANSWERABILITY_STATES = (
    "ANSWERABLE_FROM_REGISTERED_ARTIFACT",
    "ANSWERABLE_FROM_DETERMINISTIC_TOOL_OUTPUT",
    "NEEDS_CORE_DIAGNOSTIC_OR_ML",
    "NEEDS_USER_INPUT_OR_DATA",
    "BLOCKED_BY_CLAIM_BOUNDARY",
)

_BLOCKED_CLAIM_TERMS = (
    "causal_lift",
    "roi",
    "budget_optimization",
    "power_mde",
    "matched_market",
    "treatment_assignment",
    "optimizer",
)


def test_agent_answerability_fallback_plan_exists() -> None:
    assert _PLAN.is_file()


def test_plan_includes_answerability_decision_contract() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "AgentAnswerabilityDecision" in content
    assert "confidence_in_routing" in content


def test_plan_includes_five_state_machine() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "AgentAnswerabilityState" in content
    for state in _ANSWERABILITY_STATES:
        assert state in content, f"missing state: {state}"


def test_plan_includes_required_sections() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


def test_plan_includes_answer_modes() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for mode in (
        "direct_report_explanation",
        "advisory_only_guidance",
        "missing_data_request",
        "blocked_unsupported_claim",
        "tool_unavailable_fallback",
    ):
        assert mode in content, f"missing answer mode: {mode}"


def test_plan_includes_evidence_levels() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for level in (
        "general_knowledge",
        "business_profile_only",
        "deterministic_workflow_report",
        "core_mmm_required",
        "certified_decision_surface_required",
    ):
        assert level in content, f"missing evidence level: {level}"


def test_plan_includes_claim_taxonomy() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "## 7. Claim taxonomy" in content
    for claim in ("cold_start_advisory", "causal_lift", "budget_optimization"):
        assert claim in content


def test_plan_includes_tool_availability_fallback() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "ToolAvailabilityStatus" in content
    assert "tool_unavailable_fallback" in content


def test_plan_includes_ux_safe_fallback_behavior() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "Graceful degradation" in content or "graceful degradation" in content.lower()


def test_plan_includes_anti_hardcoding_principle() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "## 10. Anti-hardcoding principle" in content
    assert "hardcode" in content.lower()


def test_plan_relationship_to_deterministic_reports() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "DeterministicReportEnvelope" in content
    assert "forbidden_downstream_uses" in content
    assert "governance_status" in content


def test_plan_relationship_to_core_ml() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "## 12. Relationship to core ML" in content
    assert "NEEDS_CORE_DIAGNOSTIC_OR_ML" in content


def test_plan_includes_evaluation_harness() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "AgentCapabilityEvalCase" in content
    assert "expected_state" in content


def test_plan_documents_blocked_claims() -> None:
    content = _PLAN.read_text(encoding="utf-8").lower()
    for term in _BLOCKED_CLAIM_TERMS:
        assert term in content, f"missing blocked claim term: {term}"


def test_plan_summary_json_exists() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["plan_id"] == "AGENT_ANSWERABILITY_AND_FALLBACK_CONTRACT_PLAN_001"
    assert len(summary["answerability_states"]) == 5
