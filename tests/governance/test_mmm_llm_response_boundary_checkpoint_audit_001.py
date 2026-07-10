"""Governance checks for MMM LLM response boundary checkpoint audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_LLM_RESPONSE_BOUNDARY_CHECKPOINT_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_MMM_LLM_RESPONSE_BOUNDARY_CHECKPOINT_AUDIT_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "CHECKPOINT_PASSED_READY_FOR_LLM_RESPONSE_TEMPLATE_AUDIT",
    "CHECKPOINT_PASSED_READY_FOR_ORCHESTRATION_ROUTING_AUDIT",
    "CHECKPOINT_SHOULD_FIX_GLOBAL_MYPY_FIRST",
    "CHECKPOINT_NOT_PASSED_MISSING_LLM_BOUNDARY_CAPABILITY",
)

_REQUIRED_BOUNDARY_PATHS = (
    "mip.contracts.mmm_llm_response_boundary",
    "mip.workflows.mmm_llm_response_boundary",
)

_TRUE_FLAGS = (
    "audit_completed",
    "llm_response_boundary_exists",
    "rendered_response_consumed",
    "section_policies_supported",
    "verbatim_policy_supported",
    "rewritable_policy_supported",
    "forbidden_additions_supported",
    "cannot_say_preservation_supported",
    "caveat_preservation_supported",
    "blocked_deferred_preservation_supported",
    "human_review_preservation_supported",
    "evidence_reference_preservation_supported",
    "recommendation_refusal_supported",
    "optimizer_simulator_refusal_supported",
    "unsupported_numeric_claim_refusal_supported",
    "claim_invention_blocked",
    "blocker_softening_blocked",
    "lineage_preserved",
    "llm_call_absent",
    "provider_integration_absent",
    "prompt_template_execution_absent",
    "orchestration_routing_absent",
    "renderer_behavior_change_absent",
    "global_mypy_known_limitation_present",
    "checkpoint_passed",
)

_FALSE_FLAGS = (
    "production_code_changed",
    "method_promotion_handoff_consumer_modified",
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


def test_audit_names_llm_response_boundary_files() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for path in _REQUIRED_BOUNDARY_PATHS:
        assert path in content, f"missing boundary path: {path}"
    assert "build_mmm_llm_response_boundary" in content
    assert "MMMLLMResponseBoundary" in content


def test_audit_states_whether_boundary_checkpoint_passed() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "llm response boundary checkpoint passed" in content
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
    assert summary["recommended_next_artifact"] == "MIP_MMM_LLM_RESPONSE_TEMPLATE_AUDIT_001"
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_LLM_RESPONSE_TEMPLATE_AUDIT_001" in content


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
