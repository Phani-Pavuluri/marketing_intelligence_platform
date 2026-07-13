"""Governance checks for MMM LLM response template checkpoint audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_LLM_RESPONSE_TEMPLATE_CHECKPOINT_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_MMM_LLM_RESPONSE_TEMPLATE_CHECKPOINT_AUDIT_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "CHECKPOINT_PASSED_READY_FOR_DOMAIN_DATASET_FIXTURE_STRATEGY",
    "CHECKPOINT_PASSED_READY_FOR_LLM_RESPONSE_VERIFIER_AUDIT",
    "CHECKPOINT_PASSED_READY_FOR_PROMPT_EXECUTION_AUDIT",
    "CHECKPOINT_PASSED_READY_FOR_ORCHESTRATION_ROUTING_AUDIT",
    "CHECKPOINT_NOT_PASSED_TEMPLATE_FIX_REQUIRED",
)

_TRUE_FLAGS = (
    "audit_completed",
    "template_checkpoint_passed",
    "template_exists",
    "application_package_consumed",
    "raw_boundary_direct_input_blocked",
    "can_say_slots_supported",
    "cannot_say_slots_supported",
    "cannot_say_prioritized",
    "safe_response_guidance_slots_supported",
    "gate_requirement_slots_supported",
    "provenance_reference_slots_supported",
    "lineage_reference_slots_supported",
    "readiness_flag_slots_supported",
    "human_review_slots_supported",
    "refusal_defer_only_template_supported_when_not_ready",
    "normal_prompt_assembly_blocked_when_not_ready",
    "readiness_true_does_not_execute_prompt",
    "llm_explanation_plan_parallel_path_blocked",
    "prompt_execution_absent",
    "provider_integration_absent",
    "llm_call_absent",
    "orchestration_routing_absent",
    "user_facing_answer_generation_absent",
    "global_mypy_clean",
    "full_repo_ruff_preexisting_limitations_present",
)

_FALSE_FLAGS = (
    "production_code_changed",
    "template_behavior_modified",
    "application_package_behavior_modified",
)


def test_audit_doc_exists() -> None:
    assert _AUDIT.is_file()


def test_summary_json_exists() -> None:
    assert _SUMMARY.is_file()


def test_verdict_is_allowed_value() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["checkpoint_verdict"] in _ALLOWED_VERDICTS


def test_summary_key_booleans_truthful() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _TRUE_FLAGS:
        assert summary[key] is True, key
    for key in _FALSE_FLAGS:
        assert summary[key] is False, key


def test_audit_names_template_and_application_package() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MMMResponseTemplateOutput" in content
    assert "MMMResponseBoundaryApplicationOutput" in content
    assert "application package" in content.lower()
    assert "template input" in content.lower()


def test_audit_states_raw_boundary_direct_input_blocked() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "raw" in content and "boundary" in content
    assert "blocked" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["raw_boundary_direct_input_blocked"] is True


def test_audit_states_whether_checkpoint_passed() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "checkpoint passed" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["template_checkpoint_passed"] is True
    assert summary["checkpoint_verdict"].startswith("CHECKPOINT_PASSED_")


def test_audit_distinguishes_blocking_and_deferred_gaps() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "blocking gaps" in content
    assert "deferred nonblocking" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["blocking_gaps"] == []
    assert isinstance(summary["deferred_nonblocking_gaps"], list)
    assert summary["deferred_nonblocking_gaps"]


def test_audit_states_full_repo_ruff_limitation() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "ruff" in content
    assert "pre-existing" in content or "preexisting" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["full_repo_ruff_preexisting_limitations_present"] is True
    assert isinstance(summary["known_validation_limitations"], list)
    assert summary["known_validation_limitations"]


def test_audit_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["recommended_next_artifact"] == "MIP_DOMAIN_DATASET_FIXTURE_STRATEGY_001"
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_DOMAIN_DATASET_FIXTURE_STRATEGY_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/llm/mmm_response_template.py").is_file()
    assert Path("src/mip/llm/mmm_response_boundary_application.py").is_file()
    assert _AUDIT.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
    assert summary["template_behavior_modified"] is False
    assert summary["application_package_behavior_modified"] is False
