"""Governance checks for domain dataset schema contract checkpoint audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path(
    "docs/audits/MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_CHECKPOINT_AUDIT_001.md"
)
_SUMMARY = Path(
    "docs/audits/archives/MIP_DOMAIN_DATASET_SCHEMA_CONTRACT_CHECKPOINT_AUDIT_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "CHECKPOINT_PASSED_READY_FOR_DEMO_DOMAIN_DATASETS",
    "CHECKPOINT_PASSED_READY_FOR_DATASET_GENERATION_PLAN",
    "CHECKPOINT_NOT_PASSED_SCHEMA_FIX_REQUIRED",
    "CHECKPOINT_NOT_PASSED_OWNERSHIP_BOUNDARY_FIX_REQUIRED",
    "CHECKPOINT_NOT_PASSED_EXPECTED_BEHAVIOR_FIX_REQUIRED",
)

_TRUE_FLAGS = (
    "audit_completed",
    "schema_contract_exists",
    "fixture_manifest_supported",
    "tier_schema_supported",
    "business_domain_schema_supported",
    "dataset_family_schema_supported",
    "owner_boundary_supported",
    "spend_kpi_expectations_supported",
    "control_signal_expectations_supported",
    "calibration_signal_expectations_supported",
    "experiment_metadata_expectations_supported",
    "readiness_expectations_supported",
    "expected_behavior_supported",
    "can_say_cannot_say_expectations_supported",
    "human_review_expectations_supported",
    "forbidden_recommendation_expectations_supported",
    "llm_demo_eval_scenarios_supported",
    "tier_1_demo_generation_ready",
    "tier_2_realistic_panel_generation_ready",
    "tier_3_package_snapshot_reference_ready",
    "dataset_generation_absent",
    "production_connector_absent",
    "mmm_fitting_absent",
    "geox_estimator_logic_absent",
    "calibration_signal_runtime_change_absent",
    "decision_surface_absent",
    "trust_report_bypass_absent",
    "recommendation_contract_absent",
    "optimizer_simulator_absent",
    "roi_roas_lift_incrementality_computation_absent",
    "llm_provider_execution_absent",
    "prompt_execution_absent",
    "ui_demo_absent",
    "global_mypy_clean",
    "full_repo_ruff_preexisting_limitations_present",
)

_FALSE_FLAGS = (
    "production_code_changed",
    "schema_behavior_modified",
    "dataset_generation_implemented",
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


def test_audit_names_manifest_and_required_concepts() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    assert "DomainDatasetFixtureManifest" in content
    assert "DomainFixtureTier" in content
    assert "DomainFixtureBusinessDomain" in content
    assert "DomainFixtureDatasetFamily" in content
    assert "DomainFixtureOwner" in content
    assert "TIER_1_TINY_DETERMINISTIC" in content
    assert "TIER_2_REALISTIC_SYNTHETIC_PANEL" in content
    assert "TIER_3_PACKAGE_EXPORTED_METHOD_SIMULATION_SNAPSHOT" in content
    assert "can_say" in content.lower()
    assert "cannot_say" in content.lower()


def test_audit_states_whether_checkpoint_passed() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "checkpoint passed" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["checkpoint_verdict"].startswith("CHECKPOINT_PASSED_")


def test_audit_distinguishes_blocking_and_deferred_gaps() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "blocking gaps" in content
    assert "deferred nonblocking" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["blocking_gaps"] == []
    assert isinstance(summary["deferred_nonblocking_gaps"], list)
    assert summary["deferred_nonblocking_gaps"]


def test_audit_states_no_dataset_generation_implemented() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "no dataset generation" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["dataset_generation_absent"] is True
    assert summary["dataset_generation_implemented"] is False


def test_audit_states_recommended_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["recommended_next_artifact"] == "MIP_DEMO_DOMAIN_DATASETS_001"
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_DEMO_DOMAIN_DATASETS_001" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    assert Path("src/mip/contracts/domain_dataset_fixtures.py").is_file()
    assert _AUDIT.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
    assert summary["schema_behavior_modified"] is False
    assert summary["dataset_generation_implemented"] is False
