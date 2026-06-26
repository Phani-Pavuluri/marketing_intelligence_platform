"""Lightweight structural checks for LLM explanation contract plan."""

from __future__ import annotations

import json
from pathlib import Path

_PLAN = Path("docs/architecture/LLM_EXPLANATION_CONTRACT_PLAN_001.md")
_SUMMARY = Path(
    "docs/architecture/archives/llm_explanation_contract_plan_001_summary.json"
)

_REQUIRED_SECTIONS = (
    "## 2. Problem statement",
    "## 3. Core principle",
    "## 4. LLM explanation request contract",
    "## 5. LLM explanation response contract",
    "## 6. Explanation modes",
    "## 7. Allowed LLM behavior",
    "## 8. Blocked LLM behavior",
    "## 9. Citation and provenance requirements",
    "## 10. Response validation plan",
    "## 11. Relationship to agent capability eval fixtures",
    "## 12. Future implementation sequence",
    "## 13. Stop/go criteria",
)

_BLOCKED_BEHAVIORS = (
    "causal lift",
    "roi",
    "budget recommendation",
    "optimizer",
    "matched market",
    "treatment",
    "power",
    "mde",
    "override",
    "governance_status",
)


def test_llm_explanation_contract_plan_exists() -> None:
    assert _PLAN.is_file()


def test_plan_core_principle() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "LLM explains; deterministic contracts decide" in content


def test_plan_includes_request_contract() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "LLMExplanationRequest" in content
    assert "answerability_decision" in content
    assert "source_report_ids" in content
    assert "forbidden_response_scope" in content


def test_plan_includes_response_contract() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "LLMExplanationResponse" in content
    assert "preserved_answerability_state" in content
    assert "preserved_governance_status" in content
    assert "safety_footer" in content


def test_plan_answerability_state_preservation() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "must not recalculate" in content.lower() or "must not recalculate or alter" in content
    assert "AgentAnswerabilityState" in content


def test_plan_governance_status_preservation() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "governance_status" in content
    assert "no upgrade" in content.lower() or "Preserve" in content


def test_plan_citation_provenance_requirements() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "citations_to_report_fields" in content
    assert "citations_to_artifact_ids" in content
    assert "forbidden_downstream_uses" in content


def test_plan_allowed_llm_behavior() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "## 7. Allowed LLM behavior" in content
    assert "plain language" in content.lower() or "plain_language" in content


def test_plan_blocked_llm_behavior() -> None:
    content = _PLAN.read_text(encoding="utf-8").lower()
    for term in _BLOCKED_BEHAVIORS:
        assert term in content, f"missing blocked behavior term: {term}"


def test_plan_validation_plan() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "validate_llm_explanation_response" in content
    assert "## 10. Response validation plan" in content


def test_plan_relationship_to_agent_capability_eval_fixtures() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "agent_capability_eval" in content
    assert "Keep separate" in content or "separate" in content.lower()


def test_plan_includes_required_sections() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


def test_plan_stop_go_criteria() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "## 13. Stop/go criteria" in content
    assert "Blocked" in content


def test_plan_no_provider_runtime_implementation() -> None:
    content = _PLAN.read_text(encoding="utf-8").lower()
    assert "not implemented in this plan" in content
    assert "no llm runtime" in content or "docs/contract planning only" in content


def test_plan_summary_json_exists() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["plan_id"] == "LLM_EXPLANATION_CONTRACT_PLAN_001"
    assert summary["core_principle"] == "llm_explains_deterministic_contracts_decide"
    assert "validate_llm_explanation_response" in summary["validation_function"]
