"""Governance checks for MMM planning-answer envelope checkpoint audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_PLANNING_ANSWER_ENVELOPE_CHECKPOINT_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_MMM_PLANNING_ANSWER_ENVELOPE_CHECKPOINT_AUDIT_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "CHECKPOINT_PASSED_READY_FOR_PLANNING_RESPONSE_RENDERING_AUDIT",
    "CHECKPOINT_PASSED_READY_FOR_LLM_RESPONSE_BOUNDARY_AUDIT",
    "CHECKPOINT_NEEDS_DECISION_SURFACE_ADAPTER_AUDIT_FIRST",
    "CHECKPOINT_NOT_PASSED_MISSING_ANSWER_ENVELOPE_CAPABILITY",
)

_REQUIRED_ENVELOPE_PATHS = (
    "mip.contracts.mmm_planning_answer_envelope",
    "mip.workflows.mmm_planning_answer_envelope",
)

_TRUE_FLAGS = (
    "audit_completed",
    "planning_answer_envelope_exists",
    "eligibility_result_consumed",
    "answer_mode_preserved",
    "allowed_blocked_deferred_status_preserved",
    "caveats_preserved",
    "gate_references_preserved",
    "human_review_required_preserved",
    "evidence_references_supported",
    "can_say_boundaries_supported",
    "cannot_say_boundaries_supported",
    "unsupported_numeric_claims_blocked",
    "recommendation_claims_blocked_without_gate",
    "scenario_simulation_claims_blocked_without_decision_surface",
    "blocked_deferred_answers_first_class",
    "lineage_preserved",
    "checkpoint_passed",
)

_FALSE_FLAGS = (
    "deterministic_response_renderer_exists",
    "llm_response_boundary_exists",
    "orchestration_routes_envelope_to_renderer",
    "decision_surface_adapter_required_before_renderer",
    "recommendation_contract_generation_required_now",
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


def test_audit_names_planning_answer_envelope_files() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for path in _REQUIRED_ENVELOPE_PATHS:
        assert path in content, f"missing envelope path: {path}"
    assert "build_mmm_planning_answer_envelope" in content


def test_audit_states_whether_checkpoint_passed() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "planning-answer envelope checkpoint passed" in content
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
    assert (
        summary["recommended_next_artifact"]
        == "MIP_MMM_PLANNING_RESPONSE_RENDERING_AUDIT_001"
    )
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_PLANNING_RESPONSE_RENDERING_AUDIT_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/contracts/mmm_planning_answer_envelope.py").is_file()
    assert Path("src/mip/workflows/mmm_planning_answer_envelope.py").is_file()
    assert _AUDIT.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
