"""Governance checks for MMM LLM response template rescoping."""

from __future__ import annotations

import json
from pathlib import Path

_DOC = Path("docs/design/MIP_MMM_LLM_RESPONSE_TEMPLATE_RESCOPING_001.md")
_SUMMARY = Path(
    "docs/design/archives/MIP_MMM_LLM_RESPONSE_TEMPLATE_RESCOPING_001_summary.json"
)

_ALLOWED_DECISIONS = (
    "RESCOPE_TEMPLATE_TO_CONSUME_APPLICATION_PACKAGE",
    "RESCOPE_TEMPLATE_TO_CONSUME_APPLICATION_PACKAGE_WITH_REFUSAL_ONLY_WHEN_NOT_READY",
    "BLOCK_TEMPLATE_UNTIL_APPLICATION_PACKAGE_READINESS_TRUE",
    "PIVOT_TO_GENERIC_TEMPLATE_STRATEGY",
    "STOP_RESCOPING_INCONSISTENCY_FOUND",
)

_TRUE_FLAGS = (
    "rescoping_completed",
    "template_should_consume_application_package",
    "application_package_exists",
    "application_package_fields_sufficient_for_template",
    "ready_for_llm_prompt_assembly_false_handled",
    "refusal_only_template_allowed_when_not_ready",
    "normal_prompt_assembly_blocked_when_not_ready",
    "can_say_preserved",
    "cannot_say_prioritized",
    "safe_response_guidance_preserved",
    "unsupported_deferred_preserved",
    "gates_preserved",
    "provenance_lineage_required",
    "loose_boundary_mapping_requires_provenance",
    "llm_explanation_plan_parallel_path_blocked",
)

_FALSE_FLAGS = (
    "template_should_consume_raw_boundary",
    "mypy_cleanup_required_before_template_implementation",
    "production_code_changed",
    "application_package_behavior_changed",
    "method_promotion_handoff_consumer_modified",
)


def test_rescoping_doc_exists() -> None:
    assert _DOC.is_file()


def test_summary_json_exists() -> None:
    assert _SUMMARY.is_file()


def test_decision_is_allowed_value() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["decision"] in _ALLOWED_DECISIONS


def test_summary_key_booleans_truthful() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _TRUE_FLAGS:
        assert summary[key] is True, key
    for key in _FALSE_FLAGS:
        assert summary[key] is False, key


def test_doc_states_template_consumes_application_package() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "MMMResponseBoundaryApplicationOutput" in content
    assert "consumes" in content.lower() or "consume" in content.lower()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["template_should_consume_application_package"] is True
    assert summary["correct_template_input"] == "MMMResponseBoundaryApplicationOutput"


def test_doc_states_template_must_not_consume_raw_boundary() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "MMMLLMResponseBoundary" in content
    assert "not allowed" in content.lower()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["template_should_consume_raw_boundary"] is False
    assert summary["raw_boundary_direct_input"] == "not_allowed"


def test_doc_handles_ready_for_llm_prompt_assembly_false() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "ready_for_llm_prompt_assembly=false" in content
    assert "normal explanatory prompt assembly" in content.lower()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["ready_for_llm_prompt_assembly_false_handled"] is True
    assert summary["normal_prompt_assembly_blocked_when_not_ready"] is True


def test_doc_states_refusal_only_templates_allowed() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "refusal-only" in content
    assert "allowed" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["refusal_only_template_allowed_when_not_ready"] is True


def test_doc_states_provenance_requirement_for_loose_boundary_mapping() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "provenance" in content
    assert "loose" in content or "optional" in content
    assert "response_boundary" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["loose_boundary_mapping_requires_provenance"] is True
    assert summary["provenance_lineage_required"] is True


def test_doc_blocks_llm_explanation_plan_parallel_path() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "LLMExplanationPlan" in content
    assert "parallel" in content.lower()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["llm_explanation_plan_parallel_path_blocked"] is True


def test_doc_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert (
        summary["recommended_next_artifact"]
        == "MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001"
    )
    content = _DOC.read_text(encoding="utf-8")
    assert "MIP_MMM_LLM_RESPONSE_TEMPLATE_FROM_APPLICATION_PACKAGE_001" in content


def test_rescoping_is_design_only_scope() -> None:
    content = _DOC.read_text(encoding="utf-8").lower()
    assert "rescoping only" in content or "design / rescoping only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/llm/mmm_response_boundary_application.py").is_file()
    assert Path("src/mip/contracts/mmm_llm_response_boundary.py").is_file()
    assert _DOC.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
    assert summary["application_package_behavior_changed"] is False
    assert summary["method_promotion_handoff_consumer_modified"] is False
