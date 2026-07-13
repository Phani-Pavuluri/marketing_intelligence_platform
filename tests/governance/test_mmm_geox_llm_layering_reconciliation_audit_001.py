"""Governance checks for MMM GeoX LLM layering reconciliation audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_GEOX_LLM_LAYERING_RECONCILIATION_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_MMM_GEOX_LLM_LAYERING_RECONCILIATION_AUDIT_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "PROCEED_TO_MMM_LLM_RESPONSE_TEMPLATE_AS_SCOPED",
    "PROCEED_TO_MMM_LLM_RESPONSE_TEMPLATE_RESCOPED_TO_APPLICATION_PACKAGE",
    "PROCEED_TO_DOMAIN_DATASET_FIXTURE_STRATEGY_FIRST",
    "PROCEED_TO_ORCHESTRATION_ROUTING_AUDIT_FIRST",
    "PROCEED_TO_GENERIC_RESPONSE_BOUNDARY_STRATEGY_AUDIT_FIRST",
    "PROCEED_TO_METHOD_PROMOTION_MYPY_CLEANUP_FIRST",
    "STOP_LAYERING_INCONSISTENCY_FOUND",
)

_TRUE_FLAGS = (
    "audit_completed",
    "mmm_llm_response_boundary_exists",
    "mmm_response_boundary_application_exists",
    "method_promotion_handoff_answerability_application_exists",
    "geox_handoff_context_compatible",
    "template_should_consume_boundary",
    "template_should_consume_boundary_application_package",
    "method_promotion_lane_safe_to_pause",
    "domain_dataset_strategy_needed",
    "mip_mmm_geox_layering_aligned",
)

_FALSE_FLAGS = (
    "mmm_llm_response_template_exists",
    "template_work_redundant",
    "domain_dataset_strategy_blocks_prompt_template",
    "mip_duplicates_method_engine_logic",
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


def test_audit_mentions_mmm_llm_response_boundary() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MMMLLMResponseBoundary" in content
    assert "mmm_llm_response_boundary" in content


def test_audit_mentions_boundary_application_packaging() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MMMResponseBoundaryApplicationOutput" in content
    assert "package_mmm_llm_response_boundary" in content
    assert "mmm_response_boundary_application" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["mmm_response_boundary_application_exists"] is True


def test_audit_mentions_method_promotion_handoff_answerability() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "method-promotion" in content or "method promotion" in content
    assert "answerability" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["method_promotion_handoff_answerability_application_exists"] is True


def test_audit_mentions_geox_handoff_compatibility() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    assert "GeoX" in content or "geox" in content.lower()
    assert "handoff" in content.lower()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["geox_handoff_context_compatible"] is True


def test_audit_states_recommended_chain() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    assert "Recommended MMM LLM chain" in content or "recommended intended chain" in content.lower()
    assert "MMMResponseBoundaryApplicationOutput" in content
    assert "MMMLLMResponseTemplate" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert "MMMResponseBoundaryApplicationOutput" in summary["recommended_mmm_llm_chain"]
    assert "MMMLLMResponseTemplate" in summary["recommended_mmm_llm_chain"]


def test_audit_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert (
        summary["recommended_next_artifact"]
        == "MIP_MMM_LLM_RESPONSE_TEMPLATE_RESCOPING_001"
    )
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_LLM_RESPONSE_TEMPLATE_RESCOPING_001" in content


def test_audit_distinguishes_gap_categories() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "blocking gaps" in content
    assert "redundancy risks" in content
    assert "compatibility risks" in content
    assert "deferred nonblocking" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["blocking_gaps"] == []
    assert isinstance(summary["redundancy_risks"], list)
    assert summary["redundancy_risks"]
    assert isinstance(summary["compatibility_risks"], list)
    assert summary["compatibility_risks"]
    assert isinstance(summary["deferred_nonblocking_gaps"], list)
    assert summary["deferred_nonblocking_gaps"]


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/llm/mmm_response_boundary_application.py").is_file()
    assert Path("src/mip/contracts/mmm_llm_response_boundary.py").is_file()
    assert _AUDIT.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
    assert summary["method_promotion_handoff_consumer_modified"] is False
