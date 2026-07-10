"""Governance checks for MMM planning response rendering audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_PLANNING_RESPONSE_RENDERING_AUDIT_001.md")
_SUMMARY = Path("docs/audits/archives/MIP_MMM_PLANNING_RESPONSE_RENDERING_AUDIT_001_summary.json")

_ALLOWED_VERDICTS = (
    "FULLY_COVERED_BY_EXISTING_FUNCTIONALITY",
    "PARTIALLY_COVERED_NEEDS_THIN_MMM_PLANNING_RESPONSE_RENDERER",
    "PARTIALLY_COVERED_NEEDS_GENERIC_RESPONSE_RENDERER",
    "MISSING_NEEDS_NEW_MMM_PLANNING_RESPONSE_RENDERER",
    "CHECKPOINT_NEEDS_LLM_RESPONSE_BOUNDARY_AUDIT_FIRST",
    "CHECKPOINT_NEEDS_DECISION_SURFACE_ADAPTER_AUDIT_FIRST",
)

_REQUIRED_ENVELOPE_PATHS = (
    "mip.contracts.mmm_planning_answer_envelope",
    "mip.workflows.mmm_planning_answer_envelope",
)

_TRUE_FLAGS = (
    "audit_completed",
    "generic_response_renderer_exists",
    "mmm_planning_answer_envelope_relevant",
    "checkpoint_passed_toward_renderer_implementation",
)

_FALSE_FLAGS = (
    "planning_response_renderer_exists",
    "mmm_specific_response_renderer_exists",
    "can_render_status",
    "can_render_answer_mode",
    "can_render_can_say",
    "can_render_cannot_say",
    "can_render_caveats",
    "can_render_required_gates",
    "can_render_blocked_deferred_reasons",
    "can_render_human_review_required",
    "can_render_evidence_references",
    "can_render_lineage",
    "orchestration_routes_envelope_to_renderer",
    "llm_response_boundary_required_before_renderer",
    "decision_surface_adapter_required_before_renderer",
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


def test_audit_names_planning_answer_envelope_files() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for path in _REQUIRED_ENVELOPE_PATHS:
        assert path in content, f"missing envelope path: {path}"
    assert "MMMPlanningAnswerEnvelope" in content


def test_audit_states_whether_deterministic_renderer_exists() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "deterministic" in content and "renderer" in content
    assert "**no**" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["planning_response_renderer_exists"] is False
    assert summary["mmm_specific_response_renderer_exists"] is False


def test_audit_states_whether_checkpoint_passed_toward_renderer() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "checkpoint toward renderer implementation" in content
    assert "**passed**" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["checkpoint_passed_toward_renderer_implementation"] is True


def test_audit_distinguishes_blocking_vs_deferred_gaps() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "blocking gaps" in content
    assert "deferred nonblocking" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["blocking_gaps"] == []
    assert isinstance(summary["deferred_nonblocking_gaps"], list)
    assert summary["deferred_nonblocking_gaps"]


def test_audit_states_known_validation_limitation() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "known validation limitation" in content
    assert "mypy" in content
    assert "method-promotion" in content or "method promotion" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert isinstance(summary["known_validation_limitations"], list)
    assert summary["known_validation_limitations"]


def test_audit_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["recommended_next_artifact"] == "MIP_MMM_PLANNING_RESPONSE_RENDERER_001"
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_PLANNING_RESPONSE_RENDERER_001" in content


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
