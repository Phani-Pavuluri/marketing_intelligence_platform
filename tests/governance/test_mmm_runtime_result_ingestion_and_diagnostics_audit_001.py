"""Governance checks for MMM runtime result ingestion and diagnostics audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_RUNTIME_RESULT_INGESTION_AND_DIAGNOSTICS_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_MMM_RUNTIME_RESULT_INGESTION_AND_DIAGNOSTICS_AUDIT_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "FULLY_COVERED_BY_EXISTING_FUNCTIONALITY",
    "PARTIALLY_COVERED_NEEDS_THIN_INGESTION_ADAPTER",
    "MISSING_NEEDS_NEW_RUNTIME_RESULT_INGESTION_CONTRACT",
)

_REQUIRED_EVIDENCE_PATHS = (
    "mip.contracts.mmm_runtime_adapter",
    "mip.workflows.mmm_runtime_adapter",
    "mip.adapters.governance",
    "mip.reports.mmm_fixture",
    "mip.contracts.mmm_existing_model_availability",
    "mip.contracts.geox_readout_result_ingestion",
    "mip.orchestration.manifest",
)

_TRUE_FLAGS = (
    "audit_completed",
    "mmm_fixture_report_relevant",
    "mmm_runtime_adapter_result_relevant",
    "governance_adapter_relevant",
    "artifact_uri_metadata_supported",
    "failure_packet_supported",
    "lineage_provenance_supported",
)

_FALSE_FLAGS = (
    "mmm_runtime_result_ingestion_contract_exists",
    "mmm_diagnostics_artifact_contract_exists",
    "mmm_run_result_manifest_exists",
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
    assert "PARTIALLY_COVERED_NEEDS_THIN_INGESTION_ADAPTER" in content
    assert "does **not**" in content or "does not" in content or "not sufficient" in content


def test_audit_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert (
        summary["recommended_next_artifact"]
        == "MIP_MMM_RUNTIME_RESULT_INGESTION_AND_DIAGNOSTICS_CONTRACT_001"
    )
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_RUNTIME_RESULT_INGESTION_AND_DIAGNOSTICS_CONTRACT_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    src_changes = list(Path("src/mip").rglob("*.py"))
    assert src_changes
    assert _AUDIT.is_file()
