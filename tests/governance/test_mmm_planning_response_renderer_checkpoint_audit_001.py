"""Governance checks for MMM planning response renderer checkpoint audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_PLANNING_RESPONSE_RENDERER_CHECKPOINT_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_MMM_PLANNING_RESPONSE_RENDERER_CHECKPOINT_AUDIT_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "CHECKPOINT_PASSED_READY_FOR_LLM_RESPONSE_BOUNDARY_AUDIT",
    "CHECKPOINT_PASSED_READY_FOR_ORCHESTRATION_ROUTING_AUDIT",
    "CHECKPOINT_NEEDS_DECISION_SURFACE_ADAPTER_AUDIT_FIRST",
    "CHECKPOINT_NOT_PASSED_MISSING_RENDERER_CAPABILITY",
)

_REQUIRED_RENDERER_PATHS = (
    "mip.reports.mmm_planning_response_renderer",
    "render_mmm_planning_response",
)

_TRUE_FLAGS = (
    "audit_completed",
    "planning_response_renderer_exists",
    "mmm_planning_answer_envelope_consumed",
    "status_rendered",
    "answer_mode_rendered",
    "can_say_rendered",
    "cannot_say_rendered",
    "caveats_rendered",
    "required_gates_rendered",
    "blocked_deferred_reasons_rendered",
    "human_review_rendered",
    "evidence_references_rendered",
    "blocked_deferred_answers_first_class",
    "lineage_preserved",
    "deterministic_rendering_only",
    "unsupported_numeric_claims_not_rendered_as_allowed",
    "recommendations_not_generated",
    "llm_calls_absent",
    "decision_surface_execution_absent",
    "trust_report_construction_absent",
    "recommendation_contract_generation_absent",
    "optimizer_simulator_execution_absent",
    "artifact_model_loading_absent",
    "checkpoint_passed",
)

_FALSE_FLAGS = (
    "llm_response_boundary_exists",
    "orchestration_routes_renderer_to_response",
    "decision_surface_adapter_required_before_llm_boundary",
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


def test_audit_names_planning_response_renderer_files() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for path in _REQUIRED_RENDERER_PATHS:
        assert path in content, f"missing renderer path: {path}"
    assert "MMMPlanningRenderedResponse" in content


def test_audit_states_whether_renderer_checkpoint_passed() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "planning-response renderer checkpoint passed" in content
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
    assert summary["recommended_next_artifact"] == "MIP_MMM_LLM_RESPONSE_BOUNDARY_AUDIT_001"
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_LLM_RESPONSE_BOUNDARY_AUDIT_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/reports/mmm_planning_response_renderer.py").is_file()
    assert _AUDIT.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
