"""Governance checks for MMM LLM response boundary audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_LLM_RESPONSE_BOUNDARY_AUDIT_001.md")
_SUMMARY = Path("docs/audits/archives/MIP_MMM_LLM_RESPONSE_BOUNDARY_AUDIT_001_summary.json")

_ALLOWED_VERDICTS = (
    "FULLY_COVERED_BY_EXISTING_FUNCTIONALITY",
    "PARTIALLY_COVERED_NEEDS_THIN_MMM_LLM_RESPONSE_BOUNDARY",
    "PARTIALLY_COVERED_NEEDS_GENERIC_LLM_RESPONSE_BOUNDARY",
    "MISSING_NEEDS_NEW_MMM_LLM_RESPONSE_BOUNDARY",
    "CHECKPOINT_NEEDS_ORCHESTRATION_ROUTING_AUDIT_FIRST",
    "CHECKPOINT_NEEDS_DECISION_SURFACE_ADAPTER_AUDIT_FIRST",
)

_REQUIRED_RENDERER_PATHS = (
    "mip.reports.mmm_planning_response_renderer",
    "MMMPlanningRenderedResponse",
)

_TRUE_FLAGS = (
    "audit_completed",
    "deterministic_renderer_exists",
    "rendered_sections_available",
    "llm_safety_relevant",
    "adjacent_invent_phrase_guards_exist",
)

_FALSE_FLAGS = (
    "llm_response_boundary_exists",
    "llm_boundary_consumes_rendered_sections",
    "verbatim_section_policy_exists",
    "rewritable_section_policy_exists",
    "forbidden_additions_policy_exists",
    "cannot_say_preservation_policy_exists",
    "caveat_preservation_policy_exists",
    "blocked_deferred_preservation_policy_exists",
    "human_review_preservation_policy_exists",
    "evidence_reference_preservation_policy_exists",
    "recommendation_request_refusal_policy_exists",
    "unsupported_numeric_claim_policy_exists",
    "claim_invention_blocked",
    "softening_blockers_blocked",
    "llm_provider_behavior_implemented",
    "llm_call_implemented",
    "orchestration_required_before_boundary",
    "decision_surface_adapter_required_before_boundary",
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


def test_audit_names_planning_response_renderer_files() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for path in _REQUIRED_RENDERER_PATHS:
        assert path in content, f"missing renderer path: {path}"
    assert "render_mmm_planning_response" in content


def test_audit_names_llm_safety() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    assert "mip.llm.safety" in content


def test_audit_states_whether_llm_response_boundary_exists() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "llm-facing response boundary" in content or "llm response boundary" in content
    assert "**no**" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["llm_response_boundary_exists"] is False


def test_audit_states_claim_invention_and_blocker_softening_guard_status() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "claim invention" in content
    assert "softening" in content or "soften" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["claim_invention_blocked"] is False
    assert summary["softening_blockers_blocked"] is False
    assert summary["adjacent_invent_phrase_guards_exist"] is True


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
    assert summary["recommended_next_artifact"] == "MIP_MMM_LLM_RESPONSE_BOUNDARY_001"
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_LLM_RESPONSE_BOUNDARY_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/reports/mmm_planning_response_renderer.py").is_file()
    assert Path("src/mip/llm/safety.py").is_file()
    assert _AUDIT.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
