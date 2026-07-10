"""Governance checks for tabular source reuse contract audit."""

from __future__ import annotations

import json
import re
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_TABULAR_SOURCE_REUSE_CONTRACT_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_TABULAR_SOURCE_REUSE_CONTRACT_AUDIT_001_summary.json"
)

_REQUIRED_SECTIONS = (
    "## 1. Purpose",
    "## 2. Current source-to-lane architecture",
    "## 3. Reusable downstream boundary",
    "## 4. Future adapter rule",
    "## 5. Source-specific expectations",
    "## 6. CSV-specific leakage audit",
    "## 7. Proposed future extraction path",
    "## 8. Non-divergence checkpoint",
    "## 9. Architecture guardrails",
    "## 10. Recommended next step",
)

_TRUE_FLAGS = (
    "tabular_source_reuse_contract_audit_completed",
    "current_uploaded_csv_lane_documented",
    "geox_uploaded_csv_lane_preserved",
    "planning_mmm_uploaded_csv_lane_preserved",
    "future_source_adapter_contract_defined",
    "source_specific_responsibilities_defined",
    "downstream_reuse_boundary_defined",
    "csv_specific_leakage_audited",
    "future_extraction_path_defined",
    "non_divergence_checkpoint_recorded",
    "return_to_current_lane_checkpoint_recorded",
    "databricks_adapter_deferred",
    "warehouse_adapter_deferred",
    "api_adapter_deferred",
    "registered_table_adapter_deferred",
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
    "csv_core_rewritten",
    "geox_lane_rewritten",
    "planning_mmm_lane_rewritten",
    "model_fitting_implemented",
    "optimizer_implemented",
    "simulator_implemented",
    "recommendation_generation_implemented",
    "decision_surface_execution_implemented",
    "claim_authorization_implemented",
    "llm_provider_behavior_modified",
)

_UPLOADED_CSV_LANE_MARKERS = (
    "materialize_uploaded_csvs()",
    "UploadedCSVMaterializationResult",
    "MaterializedTabularDataset",
    "UploadedCSVInspection",
)

_GEOX_LANE_MARKERS = (
    "adapt_uploaded_csvs_for_geox_readout()",
    "call_geox_post_test_spend_runtime_for_uploaded_csvs()",
    "ingest_geox_readout_result_for_explanation()",
    "route_geox_readout_result_to_trust_boundaries()",
)

_PLANNING_LANE_MARKERS = (
    "adapt_uploaded_csvs_for_planning_mmm()",
    "build_planning_mmm_uploaded_csv_input_plan()",
    "evaluate_planning_mmm_workflow_readiness_from_uploaded_csv()",
)

_REUSE_BOUNDARY_MARKERS = (
    "TabularSourceReference",
    "TabularSourceInspection",
    "TabularSourceSchema",
    "TabularSourceLineage",
    "TabularSourceAvailability",
    "DataSourceRef",
)

_FORBIDDEN_NEW_RUNTIME_PATTERNS = (
    "databricks",
    "warehouse",
    "api_tabular_source",
    "registered_table_source",
    "spark",
    "jdbc",
    "odbc",
)

_ALLOWED_MENTION_PATHS = (
    "docs/audits/",
    "tests/governance/",
)


def test_audit_doc_exists() -> None:
    assert _AUDIT.is_file()


def test_summary_json_exists() -> None:
    assert _SUMMARY.is_file()


def test_audit_contains_required_sections() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


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


def test_audit_documents_current_uploaded_csv_lane() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for marker in _UPLOADED_CSV_LANE_MARKERS:
        assert marker in content, f"missing uploaded CSV marker: {marker}"


def test_audit_documents_geox_lane() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for marker in _GEOX_LANE_MARKERS:
        assert marker in content, f"missing GeoX lane marker: {marker}"


def test_audit_documents_planning_mmm_lane() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for marker in _PLANNING_LANE_MARKERS:
        assert marker in content, f"missing Planning/MMM lane marker: {marker}"


def test_audit_documents_future_source_adapter_contract() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower().replace("*", "")
    assert "future source adapters" in content or "future adapter rule" in content
    assert "not reimplement" in content


def test_audit_documents_reuse_boundary() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for marker in _REUSE_BOUNDARY_MARKERS:
        assert marker in content, f"missing reuse boundary marker: {marker}"


def test_audit_documents_non_divergence_checkpoint() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    assert "## 8. Non-divergence checkpoint" in content
    assert "does not authorize connector implementation" in content.lower()


def test_audit_documents_return_to_current_lane_checkpoint() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_PLANNING_MMM_READINESS_REPORT_ADAPTER_001" in content
    assert "return-to-current-lane checkpoint" in content.lower()


def test_audit_defers_source_adapters() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    for term in ("databricks", "warehouse", "api extract", "registered artifact"):
        assert term in content


def test_no_new_runtime_source_adapter_modules() -> None:
    src_root = Path("src/mip")
    for path in src_root.rglob("*.py"):
        rel = str(path).lower()
        if any(allowed in rel for allowed in _ALLOWED_MENTION_PATHS):
            continue
        stem = path.stem.lower()
        for pattern in _FORBIDDEN_NEW_RUNTIME_PATTERNS:
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


def test_audit_recommends_default_lane_continuation() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["default_next_artifact_recommended"] == (
        "MIP_PLANNING_MMM_READINESS_REPORT_ADAPTER_001"
    )
    assert summary["alternative_next_artifact_recommended"] == (
        "MIP_TABULAR_SOURCE_REFERENCE_AND_INSPECTION_001"
    )


def test_audit_records_extraction_path() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    steps = re.findall(r"MIP_[A-Z0-9_]+", content)
    assert "MIP_TABULAR_SOURCE_REFERENCE_AND_INSPECTION_001" in steps
    assert "MIP_UPLOADED_CSV_TO_TABULAR_SOURCE_COMPATIBILITY_001" in steps


def test_audit_doc_no_runtime_implementation_claim() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit/design only" in content or "audit only" in content
    assert "did not add" in content.replace("*", "")
