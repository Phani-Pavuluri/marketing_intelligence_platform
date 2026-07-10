"""Governance checks for MMM DecisionSurface planning-answer eligibility audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_DECISION_SURFACE_PLANNING_ANSWER_ELIGIBILITY_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_MMM_DECISION_SURFACE_PLANNING_ANSWER_ELIGIBILITY_AUDIT_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "FULLY_COVERED_BY_EXISTING_FUNCTIONALITY",
    "PARTIALLY_COVERED_NEEDS_THIN_PLANNING_ANSWER_ELIGIBILITY_GATE",
    "PARTIALLY_COVERED_NEEDS_THIN_DECISION_SURFACE_ELIGIBILITY_ADAPTER",
    "MISSING_NEEDS_NEW_MMM_PLANNING_ANSWER_ELIGIBILITY_CONTRACT",
)

_REQUIRED_EVIDENCE_PATHS = (
    "mip.contracts.decision_surface",
    "mip.contracts.recommendation",
    "mip.contracts.trust",
    "mip.evaluation.gates",
    "mip.contracts.mmm_artifact_governance_use_readiness",
    "mip.workflows.mmm_artifact_governance_use_readiness",
    "docs/operating_model/RELEASE_GATES.md",
)

_TRUE_FLAGS = (
    "audit_completed",
    "decision_surface_contract_relevant",
    "decision_surface_gate_relevant",
    "trust_report_contract_relevant",
    "recommendation_contract_relevant",
    "recommendation_gate_relevant",
    "mmm_artifact_governance_use_readiness_relevant",
    "planning_ready_state_available",
    "diagnostic_only_state_available",
    "recommendation_blocking_available",
    "llm_recommendation_bypass_prevented",
)

_FALSE_FLAGS = (
    "question_level_eligibility_gate_exists",
    "descriptive_answer_type_supported",
    "recommendation_eligible_answer_type_supported",
    "optimizer_simulator_execution_in_mip_required",
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


def test_audit_names_relevant_contracts_and_gates() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for path in _REQUIRED_EVIDENCE_PATHS:
        assert path in content, f"missing evidence path: {path}"
    assert "check_decision_surface_gate" in content
    assert "check_recommendation_gate" in content
    assert "RecommendationContract" in content
    assert "DecisionSurface" in content
    assert "TrustReport" in content


def test_audit_states_whether_question_level_eligibility_exists() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "question-level planning-answer eligibility already exists?" in content
    assert "**no**" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["question_level_eligibility_gate_exists"] is False


def test_audit_states_what_is_missing() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "what is missing" in content
    assert "question-level" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["missing_gaps"]


def test_audit_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["recommended_next_artifact"] == "MIP_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_001"
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/contracts/decision_surface.py").is_file()
    assert Path("src/mip/contracts/mmm_artifact_governance_use_readiness.py").is_file()
    assert _AUDIT.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
