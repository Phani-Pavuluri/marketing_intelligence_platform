"""Structural checks for MIP roadmap state audit after handoff answerability application."""

from __future__ import annotations

import json
import re
from pathlib import Path

_DOC = Path(
    "docs/roadmap/MIP_ROADMAP_STATE_AUDIT_AFTER_HANDOFF_ANSWERABILITY_APPLICATION_001.md"
)
_SUMMARY = Path(
    "docs/contracts/archives/MIP_ROADMAP_STATE_AUDIT_AFTER_HANDOFF_ANSWERABILITY_APPLICATION_001_summary.json"
)
_ROADMAP_EXEC = Path("docs/roadmap/ROADMAP_EXECUTION_SEQUENCE.md")
_REPO_INTEGRATION = Path("docs/architecture/REPO_INTEGRATION_STRATEGY.md")

_ARTIFACT = "MIP_ROADMAP_STATE_AUDIT_AFTER_HANDOFF_ANSWERABILITY_APPLICATION_001"
_DECISION = "PROCEED_TO_MMM_OR_LLM_RESPONSE_BOUNDARY_AUDIT_NOT_HANDOFF_CHECKPOINT"
_VERDICT = "handoff_answerability_lane_safe_to_pause_next_boundary_selected"
_ALLOWED_NEXT = (
    "MIP_MMM_LLM_RESPONSE_BOUNDARY_AUDIT_001",
    "MIP_MMM_PLANNING_RESPONSE_RENDERER_CHECKPOINT_AUDIT_001",
)

_REQUIRED_SECTIONS = (
    "## 1. Metadata",
    "## 2. Why this audit exists",
    "## 3. Completed handoff lane inventory",
    "## 4. Candidate next boundaries",
    "## 5. Readiness matrix",
    "## 6. Decision",
    "## 7. Recommended next artifact",
    "## 8. Non-goals",
    "## 9. Validation results",
)

_TRUE_FLAGS = (
    "handoff_answerability_application_completed",
    "handoff_lane_safe_to_pause",
    "candidate_boundaries_assessed",
    "mmm_planning_response_boundary_assessed",
    "llm_response_boundary_assessed",
    "answer_orchestration_integration_assessed",
    "demo_app_surface_integration_assessed",
    "more_handoff_checkpointing_assessed",
    "readiness_matrix_created",
    "next_boundary_selected",
)

_FALSE_FLAGS = (
    "additional_handoff_checkpoint_required_now",
    "runtime_code_changed",
    "llm_integration_implemented",
    "answer_orchestration_integration_implemented",
    "app_demo_integration_implemented",
    "handoff_checkpoint_added",
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
    assert _DECISION in content
    assert _VERDICT in content
    for section in _REQUIRED_SECTIONS:
        assert section in content, section
    assert "handoff_lane_safe_to_pause` = true" in content
    assert "additional_handoff_checkpoint_required_now` = false" in content
    assert "| Boundary | Existing evidence | Missing piece |" in content


def test_summary_json_validates() -> None:
    assert _SUMMARY.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == _ARTIFACT
    assert summary["status"] == "completed"
    assert (
        summary["scope"]
        == "docs_tests_only_next_boundary_selection_after_handoff_answerability_application"
    )
    assert summary["decision"] == _DECISION
    assert summary["final_verdict"] == _VERDICT
    assert summary["recommended_next_artifact"] in _ALLOWED_NEXT
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag
    text = _SUMMARY.read_text(encoding="utf-8")
    for pattern in _FORBIDDEN_TRUE_PATTERNS:
        assert re.search(pattern, text) is None, pattern


def test_handoff_lane_pause_and_boundary_selection() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["handoff_lane_safe_to_pause"] is True
    assert summary["additional_handoff_checkpoint_required_now"] is False
    assert summary["candidate_boundaries_assessed"] is True
    assert summary["readiness_matrix_created"] is True
    assert summary["next_boundary_selected"] is True
    assert summary["runtime_code_changed"] is False
    # Evidence-based selection: renderer stable → LLM response boundary audit lane.
    assert summary["recommended_next_artifact"] == "MIP_MMM_LLM_RESPONSE_BOUNDARY_AUDIT_001"


def test_roadmap_and_integration_strategy_reference_artifact() -> None:
    assert _ARTIFACT in _ROADMAP_EXEC.read_text(encoding="utf-8")
    assert _ARTIFACT in _REPO_INTEGRATION.read_text(encoding="utf-8")
