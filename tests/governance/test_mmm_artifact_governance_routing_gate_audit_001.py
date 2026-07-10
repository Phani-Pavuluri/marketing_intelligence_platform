"""Governance checks for MMM artifact governance routing gate audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_ARTIFACT_GOVERNANCE_ROUTING_GATE_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_MMM_ARTIFACT_GOVERNANCE_ROUTING_GATE_AUDIT_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "FULLY_COVERED_BY_EXISTING_FUNCTIONALITY",
    "PARTIALLY_COVERED_NEEDS_THIN_GOVERNANCE_AND_USE_READINESS_GATE",
    "MISSING_NEEDS_NEW_MMM_ARTIFACT_GOVERNANCE_ROUTING_GATE",
)

_REQUIRED_EVIDENCE_PATHS = (
    "mip.contracts.mmm_runtime_result_ingestion",
    "mip.workflows.mmm_runtime_result_ingestion",
    "mip.adapters.governance",
    "mip.contracts.mmm_existing_model_availability",
    "mip.evaluation.gates",
    "mip.contracts.geox_readout_trust_routing",
    "docs/operating_model/RELEASE_GATES.md",
)

_TRUE_FLAGS = (
    "audit_completed",
    "governance_adapter_relevant",
    "governance_adapter_supports_mmm_placeholders",
    "runtime_result_ingestion_result_supported",
    "mmm_model_artifact_relevant",
    "model_artifact_promotion_status_supported",
    "combined_governance_and_use_readiness_gate_recommended",
)

_FALSE_FLAGS = (
    "mmm_artifact_governance_routing_gate_exists",
    "governance_adapter_supports_external_mmm_runtime_results",
    "trust_review_readiness_supported",
    "decision_surface_review_readiness_supported",
    "separate_model_promotion_gate_needed",
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


def test_audit_names_relevant_files() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for path in _REQUIRED_EVIDENCE_PATHS:
        assert path in content, f"missing evidence path: {path}"


def test_audit_states_coverage_level() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    assert "PARTIALLY_COVERED_NEEDS_THIN_GOVERNANCE_AND_USE_READINESS_GATE" in content
    assert "does **not**" in content or "does not" in content or "not sufficient" in content


def test_audit_states_whether_separate_promotion_gate_needed() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "separate model artifact promotion/readiness gate needed?" in content
    assert "**no**" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["separate_model_promotion_gate_needed"] is False


def test_audit_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert (
        summary["recommended_next_artifact"]
        == "MIP_MMM_ARTIFACT_GOVERNANCE_AND_USE_READINESS_GATE_001"
    )
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_ARTIFACT_GOVERNANCE_AND_USE_READINESS_GATE_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    src_changes = list(Path("src/mip").rglob("*.py"))
    assert src_changes
    assert _AUDIT.is_file()
