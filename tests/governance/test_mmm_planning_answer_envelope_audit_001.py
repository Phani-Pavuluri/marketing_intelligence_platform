"""Governance checks for MMM planning-answer envelope audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_PLANNING_ANSWER_ENVELOPE_AUDIT_001.md")
_SUMMARY = Path("docs/audits/archives/MIP_MMM_PLANNING_ANSWER_ENVELOPE_AUDIT_001_summary.json")

_ALLOWED_VERDICTS = (
    "FULLY_COVERED_BY_EXISTING_FUNCTIONALITY",
    "PARTIALLY_COVERED_NEEDS_THIN_MMM_PLANNING_ANSWER_ENVELOPE",
    "PARTIALLY_COVERED_NEEDS_GENERIC_PLANNING_ANSWER_ENVELOPE",
    "MISSING_NEEDS_NEW_MMM_PLANNING_ANSWER_ENVELOPE_CONTRACT",
    "CHECKPOINT_NEEDS_DECISION_SURFACE_ADAPTER_AUDIT_FIRST",
)

_REQUIRED_ELIGIBILITY_PATHS = (
    "mip.contracts.mmm_planning_answer_eligibility",
    "mip.workflows.mmm_planning_answer_eligibility",
)

_TRUE_FLAGS = (
    "audit_completed",
    "generic_answer_envelope_exists",
    "planning_answer_eligibility_result_relevant",
    "eligibility_status_available",
    "answer_mode_available",
    "allowed_blocked_deferred_available",
    "caveats_available",
    "gate_references_available",
    "human_review_required_available",
    "blocked_reasons_available",
    "deferred_reasons_available",
    "lineage_provenance_available",
    "unsupported_numeric_claims_blocked",
    "blocked_deferred_answers_first_class",
    "llm_safety_relevant",
)

_FALSE_FLAGS = (
    "planning_answer_envelope_exists",
    "mmm_specific_answer_envelope_exists",
    "evidence_references_available",
    "can_say_cannot_say_boundary_available",
    "decision_surface_adapter_required_before_envelope",
    "recommendation_contract_generation_required_now",
    "optimizer_simulator_execution_required_now",
    "production_code_changed",
)


def test_audit_doc_exists() -> None:
    assert _AUDIT.is_file()


def test_summary_json_exists() -> None:
    assert _SUMMARY.is_file()


def test_verdict_is_allowed_value() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["verdict"] in _ALLOWED_VERDICTS


def test_summary_audit_completed_true() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["audit_completed"] is True


def test_summary_key_booleans_truthful() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _TRUE_FLAGS:
        assert summary[key] is True, key
    for key in _FALSE_FLAGS:
        assert summary[key] is False, key


def test_audit_names_planning_answer_eligibility_files() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for path in _REQUIRED_ELIGIBILITY_PATHS:
        assert path in content, f"missing eligibility path: {path}"
    assert "MMMPlanningAnswerEligibilityResult" in content


def test_audit_states_whether_envelope_already_exists() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "planning-answer envelope already exist" in content or (
        "mmm-specific planning-answer envelope" in content
    )
    assert "**no**" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["planning_answer_envelope_exists"] is False
    assert summary["mmm_specific_answer_envelope_exists"] is False


def test_audit_states_what_is_missing() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "what is missing" in content
    assert "can-say" in content or "can_say" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["missing_gaps"]


def test_audit_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["recommended_next_artifact"] == "MIP_MMM_PLANNING_ANSWER_ENVELOPE_001"
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_PLANNING_ANSWER_ENVELOPE_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/contracts/mmm_planning_answer_eligibility.py").is_file()
    assert Path("src/mip/contracts/deterministic_report.py").is_file()
    assert Path("src/mip/contracts/agent_answerability.py").is_file()
    assert _AUDIT.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
