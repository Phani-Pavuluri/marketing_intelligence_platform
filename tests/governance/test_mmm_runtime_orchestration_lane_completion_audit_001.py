"""Governance checks for MMM runtime orchestration lane completion audit."""

from __future__ import annotations

import json
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_MMM_RUNTIME_ORCHESTRATION_LANE_COMPLETION_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_MMM_RUNTIME_ORCHESTRATION_LANE_COMPLETION_AUDIT_001_summary.json"
)

_ALLOWED_VERDICTS = (
    "LANE_COMPLETE_READY_FOR_DECISION_SURFACE_PLANNING_ANSWER_LANE",
    "LANE_COMPLETE_WITH_DEFERRED_NONBLOCKING_GAPS",
    "LANE_NOT_COMPLETE_BLOCKING_RUNTIME_CONTROL_PLANE_GAPS",
)

_REQUIRED_CHAIN_ARTIFACTS = (
    "MIP_PLANNING_MMM_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001",
    "MIP_PLANNING_MMM_CALIBRATION_SIGNAL_INTAKE_FROM_TABULAR_SOURCE_001",
    "MIP_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_AND_READINESS_001",
    "MIP_MMM_EXISTING_MODEL_AVAILABILITY_GATE_001",
    "MIP_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_001",
    "MIP_MMM_RUNTIME_ADAPTER_CONTRACT_001",
    "MIP_MMM_RUNTIME_RESULT_INGESTION_AND_DIAGNOSTICS_CONTRACT_001",
    "MIP_MMM_ARTIFACT_GOVERNANCE_AND_USE_READINESS_GATE_001",
    "MIP_MMM_ARTIFACT_GOVERNANCE_ROUTING_GATE_AUDIT_001",
)

_TRUE_FLAGS = (
    "audit_completed",
    "source_data_readiness_supported",
    "calibration_signal_intake_supported",
    "calibration_mapping_readiness_supported",
    "existing_model_availability_supported",
    "trusted_input_model_run_eligibility_supported",
    "runtime_adapter_handoff_supported",
    "runtime_result_ingestion_supported",
    "artifact_governance_use_readiness_supported",
    "runtime_lane_closed",
    "lineage_preserved",
)

_FALSE_FLAGS = (
    "separate_model_promotion_gate_needed",
    "trust_report_construction_implemented",
    "decision_surface_construction_implemented",
    "recommendation_contract_generation_implemented",
    "artifact_loading_implemented",
    "model_execution_implemented",
    "production_code_changed",
)


def test_audit_doc_exists() -> None:
    assert _AUDIT.is_file()


def test_summary_json_exists() -> None:
    assert _SUMMARY.is_file()


def test_verdict_is_allowed_value() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["lane_completion_verdict"] in _ALLOWED_VERDICTS


def test_summary_audit_completed_true() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["audit_completed"] is True


def test_summary_key_booleans_truthful() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _TRUE_FLAGS:
        assert summary[key] is True, key
    for key in _FALSE_FLAGS:
        assert summary[key] is False, key


def test_audit_names_main_completed_artifacts() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for artifact in _REQUIRED_CHAIN_ARTIFACTS:
        assert artifact in content, f"missing chain artifact: {artifact}"


def test_audit_states_whether_lane_is_closed() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "runtime/control-plane lane closed" in content
    assert "**yes**" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["runtime_lane_closed"] is True


def test_audit_distinguishes_blocking_vs_deferred_gaps() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "blocking gaps" in content
    assert "deferred nonblocking gaps" in content
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["blocking_gaps"] == []
    assert isinstance(summary["deferred_nonblocking_gaps"], list)
    assert summary["deferred_nonblocking_gaps"]


def test_audit_states_next_recommended_lane() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert (
        summary["next_lane_recommended"]
        == "MMM_DECISION_SURFACE_PLANNING_ANSWER_ELIGIBILITY_LANE"
    )
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MMM_DECISION_SURFACE_PLANNING_ANSWER_ELIGIBILITY_LANE" in content


def test_audit_is_audit_only_scope() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "audit-only" in content or "audit only" in content
    assert "did not add or modify production code" in content


def test_no_production_code_changed() -> None:
    """Audit deliverables only; production tree remains present and unchanged by this audit."""
    assert Path("src/mip/contracts/mmm_artifact_governance_use_readiness.py").is_file()
    assert Path("src/mip/workflows/mmm_artifact_governance_use_readiness.py").is_file()
    assert _AUDIT.is_file()
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["production_code_changed"] is False
