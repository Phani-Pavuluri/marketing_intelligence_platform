"""Structural checks for MMM LLM response boundary application readiness audit."""

from __future__ import annotations

import json
import re
from pathlib import Path

_DOC = Path(
    "docs/roadmap/MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_READINESS_AUDIT_001.md"
)
_SUMMARY = Path(
    "docs/contracts/archives/MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_READINESS_AUDIT_001_summary.json"
)
_ROADMAP_EXEC = Path("docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md")
_REPO_INTEGRATION = Path("docs/architecture/REPO_INTEGRATION_STRATEGY.md")

_ARTIFACT = "MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_READINESS_AUDIT_001"
_ALLOWED_DECISIONS = (
    "PROCEED_TO_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_NOT_FULL_ORCHESTRATION",
    "PROCEED_TO_MMM_LLM_RESPONSE_BOUNDARY_HARDENING_NOT_APPLICATION",
)
_ALLOWED_NEXT = (
    "MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001",
    "MIP_MMM_LLM_RESPONSE_BOUNDARY_HARDENING_001",
)
_VERDICT = "mmm_llm_response_boundary_application_readiness_audited_next_step_selected"

_REQUIRED_SECTIONS = (
    "## 1. Metadata",
    "## 2. Why this audit exists",
    "## 3. Boundary inventory",
    "## 4. Readiness assessment",
    "## 5. Risks if skipped",
    "## 6. Decision",
    "## 7. Recommended next artifact",
    "## 8. Non-goals",
    "## 9. Validation results",
)

_TRUE_FLAGS = (
    "boundary_inventory_completed",
    "readiness_assessment_completed",
    "risks_if_skipped_documented",
    "next_step_selected",
    "deterministic_mmm_planning_sections_assessed",
    "llm_response_boundary_assessed",
    "allowed_response_content_assessed",
    "prohibited_response_content_assessed",
    "unsupported_recommendation_behavior_assessed",
    "decision_surface_gate_preserved",
    "trust_report_gate_preserved",
    "recommendation_contract_gate_preserved",
    "spend_roi_budget_gate_preserved",
    "claims_gate_preserved",
)

_FALSE_FLAGS = (
    "runtime_code_changed",
    "llm_integration_implemented",
    "user_facing_answer_generation_implemented",
    "full_orchestration_implemented",
    "decision_surface_authorized",
    "trust_report_bypassed",
    "recommendation_contract_authorized",
    "planning_recommendation_enabled",
    "budget_optimization_enabled",
    "spend_movement_authorized",
    "roi_roas_authorized",
    "claim_authorization_changed",
    "catalog_unblocked",
    "production_compatibility_authorized",
    "method_promoted",
    "instrument_promoted",
)

_FORBIDDEN_TRUE_PATTERNS = tuple(rf'"{flag}"\s*:\s*true' for flag in _FALSE_FLAGS)


def test_audit_doc_exists() -> None:
    assert _DOC.is_file()
    content = _DOC.read_text(encoding="utf-8")
    assert _ARTIFACT in content
    assert _VERDICT in content
    for section in _REQUIRED_SECTIONS:
        assert section in content, section
    assert "MIP_MMM_LLM_RESPONSE_BOUNDARY_001" in content
    assert "**PASS**" in content


def test_summary_json_validates() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == _ARTIFACT
    assert summary["status"] == "completed"
    assert (
        summary["scope"]
        == "docs_tests_only_application_readiness_audit_no_runtime_no_llm_integration"
    )
    assert summary["depends_on"] == [
        "MIP_MMM_LLM_RESPONSE_BOUNDARY_001",
        "MIP_ROADMAP_STATE_AUDIT_AFTER_HANDOFF_ANSWERABILITY_APPLICATION_001",
    ]
    assert summary["decision"] in _ALLOWED_DECISIONS
    assert summary["recommended_next_artifact"] in _ALLOWED_NEXT
    assert summary["final_verdict"] == _VERDICT
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag
    text = _SUMMARY.read_text(encoding="utf-8")
    for pattern in _FORBIDDEN_TRUE_PATTERNS:
        assert re.search(pattern, text) is None, pattern


def test_readiness_selects_application_not_hardening() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["boundary_inventory_completed"] is True
    assert summary["readiness_assessment_completed"] is True
    assert summary["risks_if_skipped_documented"] is True
    assert summary["next_step_selected"] is True
    assert summary["decision_surface_gate_preserved"] is True
    assert summary["trust_report_gate_preserved"] is True
    assert summary["recommendation_contract_gate_preserved"] is True
    assert summary["runtime_code_changed"] is False
    # Evidence: clear boundary + rendered sections + checkpoint passed → application.
    assert summary["decision"] == (
        "PROCEED_TO_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_NOT_FULL_ORCHESTRATION"
    )
    assert summary["recommended_next_artifact"] == (
        "MIP_MMM_LLM_RESPONSE_BOUNDARY_APPLICATION_001"
    )


def test_roadmap_and_integration_strategy_reference_artifact() -> None:
    assert _ARTIFACT in _ROADMAP_EXEC.read_text(encoding="utf-8")
    assert _ARTIFACT in _REPO_INTEGRATION.read_text(encoding="utf-8")
