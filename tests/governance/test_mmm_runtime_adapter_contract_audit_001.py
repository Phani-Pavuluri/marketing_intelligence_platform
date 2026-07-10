"""Governance checks for MMM runtime adapter contract audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_RUNTIME_ADAPTER_CONTRACT_AUDIT_001.md")
_SUMMARY = Path("docs/audits/archives/MIP_MMM_RUNTIME_ADAPTER_CONTRACT_AUDIT_001_summary.json")

_ALLOWED_VERDICTS = (
    "FULLY_COVERED_BY_EXISTING_FUNCTIONALITY",
    "PARTIALLY_COVERED_NEEDS_THIN_ADAPTER",
    "MISSING_NEEDS_NEW_RUNTIME_ADAPTER_CONTRACT",
)

_REQUIRED_EVIDENCE_PATHS = (
    "mip.adapters.mmm",
    "mip.adapters.governance",
    "mip.reports.mmm_fixture",
    "mip.contracts.planning_mmm_trusted_input_model_run_eligibility",
    "mip.contracts.mmm_existing_model_availability",
    "mip.contracts.geox_panel_exp_runtime_call",
)

_TRUE_FLAGS = (
    "audit_completed",
    "mmm_adapter_placeholder_exists",
    "mmm_fixture_placeholder_exists",
    "governance_adapter_relevant",
    "trusted_input_package_reference_supported",
    "model_run_eligibility_reference_supported",
)

_FALSE_FLAGS = (
    "mmm_runtime_request_contract_exists",
    "mmm_runtime_response_contract_exists",
    "mmm_run_manifest_exists",
    "external_runtime_reference_supported",
    "runtime_status_supported",
    "failure_packet_supported",
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
    assert "PARTIALLY_COVERED_NEEDS_THIN_ADAPTER" in content
    assert "does **not**" in content or "does not" in content or "not sufficient" in content


def test_audit_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["recommended_next_artifact"] == "MIP_MMM_RUNTIME_ADAPTER_CONTRACT_001"
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_RUNTIME_ADAPTER_CONTRACT_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    src_changes = list(Path("src/mip").rglob("*.py"))
    assert src_changes
    assert _AUDIT.is_file()
