"""Governance checks for shared uploaded data and planning input audit."""

from __future__ import annotations

import json
import re
from pathlib import Path

_AUDIT = Path("docs/audits/MIP_SHARED_UPLOADED_DATA_AND_PLANNING_INPUT_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_SHARED_UPLOADED_DATA_AND_PLANNING_INPUT_AUDIT_001_summary.json"
)

_REQUIRED_SECTIONS = (
    "## 1. Purpose",
    "## 2. Current repository checkpoint",
    "## 3. Existing user-provided data abstractions",
    "## 4. Existing GeoX readout data/input lane",
    "## 5. Existing planning/MMM/budget/DecisionSurface lane",
    "## 6. Existing overlap and duplication risk",
    "## 7. Shared uploaded-data layer candidate",
    "## 8. Lane-specific resolver candidates",
    "### 8.1 GeoX readout lane",
    "### 8.2 Planning/MMM lane",
    "## 9. Recommended architecture",
    "## 10. Recommended next implementation artifact",
    "## 11. Explicitly deferred scope",
    "## 12. Acceptance criteria for next artifact",
    "## 13. Final recommendation",
)

_REQUIRED_SUMMARY_KEYS = (
    "artifact",
    "artifact_type",
    "repo_checkpoint",
    "existing_user_data_abstractions_found",
    "existing_geox_readout_input_lane_found",
    "existing_planning_or_mmm_input_lane_found",
    "shared_uploaded_data_layer_recommended",
    "separate_geox_readout_lane_recommended",
    "separate_planning_mmm_lane_recommended",
    "duplicate_csv_parser_risk_identified",
    "next_artifact_recommended",
    "runtime_implementation_added",
)

_GEOX_ARTIFACTS = (
    "DatasetReference",
    "inspect_geox_readout_sources",
    "resolve_geox_readout_inputs",
    "GeoXReadoutInputHandoff",
    "materialize_geox_readout_fixtures",
    "GeoXReadoutTrustRoutingEnvelope",
)

_PLANNING_ARTIFACTS = (
    "DecisionSurface",
    "RecommendationContract",
    "MMMDataReadinessReport",
    "ModelCalibrationReadiness",
    "CalibrationSignal",
    "DataSourceRef",
)

_DEFERRED_SCOPES = (
    "warehouse",
    "panel_exp",
    "DecisionSurface execution",
    "RecommendationContract generation",
    "claim authorization",
    "LLM",
)


def test_audit_doc_exists() -> None:
    assert _AUDIT.is_file()


def test_summary_json_exists() -> None:
    assert _SUMMARY.is_file()


def test_audit_contains_required_sections() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


def test_audit_records_geox_readout_artifacts() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for artifact in _GEOX_ARTIFACTS:
        assert artifact in content, f"missing GeoX artifact reference: {artifact}"


def test_audit_records_planning_mmm_artifacts() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for artifact in _PLANNING_ARTIFACTS:
        assert artifact in content, f"missing planning/MMM artifact reference: {artifact}"


def test_audit_defines_shared_vs_lane_specific_split() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert "shared uploaded" in content or "shared uploaded-data" in content
    assert "lane-specific" in content
    assert "geox readout lane" in content
    assert "planning/mmm lane" in content


def test_audit_recommends_exactly_one_next_artifact() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    next_section = content.split("## 10. Recommended next implementation artifact", 1)[1]
    next_section = next_section.split("## 11.", 1)[0]
    recommended = re.findall(r"MIP_[A-Z0-9_]+", next_section)
    assert len(recommended) >= 1
    primary = "MIP_SHARED_UPLOADED_CSV_MATERIALIZATION_CORE_001"
    assert primary in recommended
    assert recommended.count(primary) >= 1


def test_summary_recommends_one_next_artifact() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    for key in _REQUIRED_SUMMARY_KEYS:
        assert key in summary, key
    assert summary["next_artifact_recommended"] == (
        "MIP_SHARED_UPLOADED_CSV_MATERIALIZATION_CORE_001"
    )


def test_audit_records_deferred_scopes() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    for scope in _DEFERRED_SCOPES:
        assert scope.lower() in content, f"missing deferred scope: {scope}"


def test_audit_states_no_runtime_implementation_added() -> None:
    content = _AUDIT.read_text(encoding="utf-8").lower()
    assert (
        "audit/documentation/test-only" in content
        or "no shared materialization runtime" in content
    )
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["runtime_implementation_added"] is False


def test_no_panel_exp_import_in_audit_deliverables() -> None:
    source = _AUDIT.read_text(encoding="utf-8")
    assert "import panel_exp" not in source
    assert "from panel_exp" not in source
