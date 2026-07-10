"""Governance checks for MMM LLM response template audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_LLM_RESPONSE_TEMPLATE_AUDIT_001.md")
_SUMMARY = Path("docs/audits/archives/MIP_MMM_LLM_RESPONSE_TEMPLATE_AUDIT_001_summary.json")

_ALLOWED_VERDICTS = (
    "FULLY_COVERED_BY_EXISTING_FUNCTIONALITY",
    "PARTIALLY_COVERED_NEEDS_THIN_MMM_LLM_RESPONSE_TEMPLATE",
    "PARTIALLY_COVERED_NEEDS_GENERIC_LLM_RESPONSE_TEMPLATE",
    "MISSING_NEEDS_NEW_MMM_LLM_RESPONSE_TEMPLATE",
    "CHECKPOINT_NEEDS_ORCHESTRATION_ROUTING_AUDIT_FIRST",
    "CHECKPOINT_SHOULD_FIX_GLOBAL_MYPY_FIRST",
)

_REQUIRED_BOUNDARY_PATHS = (
    "mip.contracts.mmm_llm_response_boundary",
    "mip.workflows.mmm_llm_response_boundary",
)

_TRUE_FLAGS = (
    "audit_completed",
    "llm_response_boundary_exists",
    "adjacent_llm_explanation_plan_exists",
    "global_mypy_known_limitation_present",
)

_FALSE_FLAGS = (
    "prompt_template_exists",
    "mmm_specific_prompt_template_exists",
    "generic_prompt_template_exists",
    "template_consumes_llm_response_boundary",
    "template_consumes_rendered_sections",
    "system_instruction_shape_exists",
    "developer_instruction_shape_exists",
    "verbatim_section_injection_supported",
    "rewritable_section_injection_supported",
    "must_include_policy_supported",
    "cannot_omit_policy_supported",
    "forbidden_additions_policy_supported",
    "refusal_policy_supported",
    "provider_integration_required_before_template",
    "orchestration_required_before_template",
    "ui_required_before_template",
    "production_code_changed",
    "method_promotion_handoff_consumer_modified",
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


def test_audit_names_llm_response_boundary_files() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for path in _REQUIRED_BOUNDARY_PATHS:
        assert path in content, f"missing boundary path: {path}"
    assert "MMMLLMResponseBoundary" in content
    assert "build_mmm_llm_response_boundary" in content


def test_audit_states_whether_prompt_template_exists() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "prompt" in content and "template" in content
    assert "**no**" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["prompt_template_exists"] is False
    assert summary["mmm_specific_prompt_template_exists"] is False


def test_audit_states_template_direction_mmm_or_generic() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "mmm-specific" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["template_direction"] == "mmm_specific"


def test_audit_distinguishes_blocking_vs_deferred_gaps() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "blocking gaps" in content
    assert "deferred nonblocking" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["blocking_gaps"] == []
    assert isinstance(summary["deferred_nonblocking_gaps"], list)
    assert summary["deferred_nonblocking_gaps"]


def test_audit_states_known_global_mypy_limitation() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "known validation limitation" in content
    assert "mypy" in content
    assert "method-promotion" in content or "method promotion" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["global_mypy_known_limitation_present"] is True
    assert isinstance(summary["known_validation_limitations"], list)
    assert summary["known_validation_limitations"]


def test_audit_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["recommended_next_artifact"] == "MIP_MMM_LLM_RESPONSE_TEMPLATE_001"
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_LLM_RESPONSE_TEMPLATE_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/contracts/mmm_llm_response_boundary.py").is_file()
    assert Path("src/mip/workflows/mmm_llm_response_boundary.py").is_file()
    assert _AUDIT.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
    assert summary["method_promotion_handoff_consumer_modified"] is False
