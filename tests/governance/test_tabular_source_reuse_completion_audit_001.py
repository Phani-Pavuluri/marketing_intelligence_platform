"""Governance checks for tabular source reuse completion audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_TABULAR_SOURCE_REUSE_COMPLETION_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_TABULAR_SOURCE_REUSE_COMPLETION_AUDIT_001_summary.json"
)

_PRIOR_CONTRACT_SUMMARIES = (
    "docs/audits/archives/MIP_TABULAR_SOURCE_REUSE_CONTRACT_AUDIT_001_summary.json",
    "docs/contracts/archives/MIP_TABULAR_SOURCE_REFERENCE_AND_INSPECTION_001_summary.json",
    "docs/contracts/archives/MIP_PLANNING_MMM_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001_summary.json",
    "docs/contracts/archives/MIP_PLANNING_MMM_READINESS_REPORT_ADAPTER_001_summary.json",
    "docs/contracts/archives/MIP_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001_summary.json",
)

_TRUE_FLAGS = (
    "tabular_source_reuse_completion_audit_completed",
    "reusable_tabular_source_framework_complete_for_current_milestone",
    "common_tabular_source_boundary_confirmed",
    "tabular_source_inspection_result_confirmed",
    "uploaded_csv_compatibility_view_confirmed",
    "planning_mmm_generic_source_path_confirmed",
    "planning_mmm_readiness_report_adapter_confirmed",
    "geox_generic_source_path_confirmed",
    "geox_runtime_bridge_compatibility_confirmed",
    "uploaded_csv_paths_preserved",
    "future_source_adapter_contract_confirmed",
    "source_adapter_sprawl_guardrails_confirmed",
    "planning_mmm_lane_preserved",
    "geox_lane_preserved",
)

_FALSE_FLAGS = (
    "databricks_adapter_implemented",
    "warehouse_adapter_implemented",
    "api_adapter_implemented",
    "registered_table_adapter_implemented",
    "live_connector_runtime_implemented",
    "credentials_handling_implemented",
    "network_calls_implemented",
    "spark_dependency_added",
    "sql_execution_implemented",
    "warehouse_client_added",
    "databricks_sdk_added",
    "source_specific_downstream_adapter_sprawl_allowed",
    "planning_mmm_lane_rewritten",
    "geox_lane_rewritten",
    "uploaded_csv_paths_rewritten",
    "model_fitting_implemented",
    "bayesian_fitting_implemented",
    "optimizer_implemented",
    "simulator_implemented",
    "budget_allocation_calculation_implemented",
    "marginal_roi_calculation_implemented",
    "incrementality_calculation_implemented",
    "lift_computation_implemented",
    "spend_delta_computation_implemented",
    "delta_mu_computation_implemented",
    "roi_roas_computation_implemented",
    "recommendation_contract_generation_implemented",
    "decision_surface_execution_implemented",
    "trust_report_bypassed",
    "claim_authorization_implemented",
    "llm_provider_behavior_modified",
)

_REQUIRED_PHRASES = (
    "Reusable tabular source framework complete for current milestone",
    "External connector adapters remain deferred",
    "TabularSourceInspectionResult",
    "adapt_tabular_sources_for_planning_mmm",
    "adapt_tabular_sources_for_geox_readout",
    "future source adapters must emit TabularSourceInspectionResult",
    "must not reimplement downstream Planning/MMM or GeoX logic",
)

_CORE_TABULAR_FILES = (
    "src/mip/contracts/tabular_source_reference.py",
    "src/mip/workflows/tabular_source_inspection.py",
)

_PLANNING_MMM_GENERIC_FILES = (
    "src/mip/contracts/planning_mmm_tabular_source_adapter.py",
    "src/mip/workflows/planning_mmm_tabular_source_adapter.py",
    "src/mip/contracts/planning_mmm_readiness_report_adapter.py",
    "src/mip/workflows/planning_mmm_readiness_report_adapter.py",
)

_GEOX_GENERIC_FILES = (
    "src/mip/contracts/geox_tabular_source_adapter.py",
    "src/mip/workflows/geox_tabular_source_adapter.py",
)

_UPLOADED_CSV_PRESERVED_FILES = (
    "src/mip/contracts/planning_mmm_uploaded_csv_adapter.py",
    "src/mip/workflows/planning_mmm_uploaded_csv_adapter.py",
    "src/mip/contracts/geox_uploaded_csv_adapter.py",
    "src/mip/workflows/geox_uploaded_csv_adapter.py",
    "src/mip/contracts/geox_uploaded_csv_runtime_bridge.py",
    "src/mip/workflows/geox_uploaded_csv_runtime_bridge.py",
)

_FORBIDDEN_RUNTIME_PATTERNS = (
    "databricks",
    "warehouse",
    "api_tabular",
    "registered_table",
    "spark",
    "jdbc",
    "odbc",
)


def test_audit_doc_exists() -> None:
    assert _AUDIT.is_file()


def test_summary_json_exists() -> None:
    assert _SUMMARY.is_file()


def test_summary_true_flags() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _TRUE_FLAGS:
        assert key in summary, key
        assert summary[key] is True, key


def test_summary_false_flags() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _FALSE_FLAGS:
        assert key in summary, key
        assert summary[key] is False, key


def test_prior_artifact_summaries_exist() -> None:
    for path in _PRIOR_CONTRACT_SUMMARIES:
        assert Path(path).is_file(), path


def test_audit_contains_required_phrases() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for phrase in _REQUIRED_PHRASES:
        assert phrase in content, f"missing phrase: {phrase}"


def test_core_tabular_source_files_exist() -> None:
    for path in _CORE_TABULAR_FILES:
        assert Path(path).is_file(), path


def test_planning_mmm_generic_source_files_exist() -> None:
    for path in _PLANNING_MMM_GENERIC_FILES:
        assert Path(path).is_file(), path


def test_geox_generic_source_files_exist() -> None:
    for path in _GEOX_GENERIC_FILES:
        assert Path(path).is_file(), path


def test_uploaded_csv_adapter_files_preserved() -> None:
    for path in _UPLOADED_CSV_PRESERVED_FILES:
        assert Path(path).is_file(), path


def test_no_forbidden_external_source_adapter_modules() -> None:
    src_root = Path("src/mip")
    for path in src_root.rglob("*.py"):
        stem = path.stem.lower()
        for pattern in _FORBIDDEN_RUNTIME_PATTERNS:
            assert pattern not in stem, f"forbidden runtime module stem: {path}"


def test_no_connector_dependencies_in_pyproject() -> None:
    pyproject = Path("pyproject.toml").read_text(encoding="utf-8").lower()
    for dep in (
        "databricks-sdk",
        "pyspark",
        "sqlalchemy",
        "snowflake",
        "bigquery",
        "redshift",
        "jdbc",
        "odbc",
    ):
        assert dep not in pyproject, f"unexpected connector dependency: {dep}"


def test_summary_recommends_next_artifacts() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["recommended_next_artifact"] == (
        "MIP_PLANNING_MMM_CALIBRATION_SIGNAL_INTAKE_FROM_TABULAR_SOURCE_001"
    )
    assert summary["alternative_next_artifact"] == (
        "MIP_GEOX_READOUT_RESULT_ROUTING_FROM_TABULAR_SOURCE_001"
    )
    assert summary["external_connector_adapters_deferred"] is True


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content
