"""Governance checks for MMM planning-answer eligibility gate checkpoint audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_CHECKPOINT_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_MMM_PLANNING_ANSWER_ELIGIBILITY_GATE_CHECKPOINT_AUDIT_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "CHECKPOINT_PASSED_READY_FOR_PLANNING_ANSWER_ENVELOPE_AUDIT",
    "CHECKPOINT_PASSED_READY_FOR_PLANNING_ANSWER_ENVELOPE_IMPLEMENTATION",
    "CHECKPOINT_NEEDS_DECISION_SURFACE_ADAPTER_AUDIT_FIRST",
    "CHECKPOINT_NOT_PASSED_MISSING_DETERMINISTIC_ELIGIBILITY",
)

_REQUIRED_GATE_PATHS = (
    "mip.contracts.mmm_planning_answer_eligibility",
    "mip.workflows.mmm_planning_answer_eligibility",
)

_TRUE_FLAGS = (
    "audit_completed",
    "planning_answer_eligibility_gate_exists",
    "question_level_eligibility_supported",
    "planning_question_taxonomy_supported",
    "descriptive_mode_supported",
    "diagnostic_mode_supported",
    "scenario_comparison_mode_supported",
    "simulation_only_mode_supported",
    "recommendation_eligible_mode_supported",
    "blocked_deferred_modes_supported",
    "artifact_use_readiness_consumed",
    "recommendation_requests_blocked_until_gates_pass",
    "optimizer_simulator_requests_do_not_execute",
    "llm_bypass_prevented",
    "checkpoint_passed",
)

_FALSE_FLAGS = (
    "planning_answer_envelope_exists",
    "decision_surface_adapter_required_before_envelope",
    "recommendation_contract_layer_required_now",
    "production_code_changed",
)


def test_audit_doc_exists() -> None:
    assert _AUDIT.is_file()


def test_summary_json_exists() -> None:
    assert _SUMMARY.is_file()


def test_verdict_is_allowed_value() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["checkpoint_verdict"] in _ALLOWED_VERDICTS


def test_summary_audit_completed_true() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["audit_completed"] is True


def test_summary_key_booleans_truthful() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _TRUE_FLAGS:
        assert summary[key] is True, key
    for key in _FALSE_FLAGS:
        assert summary[key] is False, key


def test_audit_names_planning_answer_eligibility_gate_files() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for path in _REQUIRED_GATE_PATHS:
        assert path in content, f"missing gate path: {path}"
    assert "evaluate_mmm_planning_answer_eligibility" in content


def test_audit_states_whether_checkpoint_passed() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "planning-answer eligibility checkpoint passed" in content
    assert "**yes**" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["checkpoint_passed"] is True


def test_audit_distinguishes_blocking_vs_deferred_gaps() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "blocking gaps" in content
    assert "deferred nonblocking" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["blocking_gaps"] == []
    assert isinstance(summary["deferred_nonblocking_gaps"], list)
    assert summary["deferred_nonblocking_gaps"]


def test_audit_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["recommended_next_artifact"] == "MIP_MMM_PLANNING_ANSWER_ENVELOPE_AUDIT_001"
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_PLANNING_ANSWER_ENVELOPE_AUDIT_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/contracts/mmm_planning_answer_eligibility.py").is_file()
    assert Path("src/mip/workflows/mmm_planning_answer_eligibility.py").is_file()
    assert _AUDIT.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
