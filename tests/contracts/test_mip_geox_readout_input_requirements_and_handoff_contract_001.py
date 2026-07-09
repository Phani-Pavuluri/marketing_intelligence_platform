"""Structural checks for MIP GeoX readout input handoff contract."""

from __future__ import annotations

import json
import re
from pathlib import Path

_DOC = Path("docs/contracts/MIP_GEOX_READOUT_INPUT_REQUIREMENTS_AND_HANDOFF_CONTRACT_001.md")
_SUMMARY = Path(
    "docs/contracts/archives/"
    "MIP_GEOX_READOUT_INPUT_REQUIREMENTS_AND_HANDOFF_CONTRACT_001_summary.json"
)

_REQUIRED_SECTIONS = (
    "## 2. Why this contract exists",
    "## 3. Package / MIP ownership split",
    "## 4. MIP readout intent detection",
    "## 5. Required MIP inputs for any GeoX readout",
    "## 6. Conditional MIP inputs for spend-derived metrics",
    "## 7. Conditional MIP inputs for value/margin mapping",
    "## 8. MIP missing-input prompts",
    "## 9. Typed handoff object",
    "## 10. MIP resolution statuses",
    "## 11. MIP-to-panel_exp rules",
    "## 12. Trust / claim boundary",
    "## 13. Runtime follow-up plan",
    "## 14. Non-goals",
)

_READOUT_INTENTS = (
    "READOUT_KPI_ONLY",
    "READOUT_WITH_LIFT",
    "READOUT_WITH_COST_PER",
    "READOUT_WITH_ROAS",
    "READOUT_WITH_PROFIT_ROI",
    "READOUT_WITH_DECISION_RECOMMENDATION_REQUEST",
    "READOUT_UNCLEAR_METRIC_REQUEST",
)

_FORBIDDEN_FLAGS = (
    "runtime_implemented",
    "panel_exp_runtime_call_implemented",
    "spend_ingestion_system_created",
    "spend_delta_computed_in_mip",
    "roi_roas_computed_in_mip",
    "claim_authorization_duplicated",
    "trust_report_bypassed",
    "decision_surface_bypassed",
    "recommendation_contract_bypassed",
    "business_recommendation_authorized",
    "production_decisioning_authorized",
)

_FORBIDDEN_RUNTIME_PATTERNS = tuple(
    rf'"{flag}"\s*:\s*true' for flag in _FORBIDDEN_FLAGS
)


def test_contract_doc_exists() -> None:
    assert _DOC.is_file()


def test_summary_json_exists() -> None:
    assert _SUMMARY.is_file()


def test_required_sections_present() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for section in _REQUIRED_SECTIONS:
        assert section in content, f"missing section: {section}"


def test_kpi_requirements_defined() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "KPI dataset reference" in content
    assert "KPI date/week column mapping" in content
    assert "experiment_id" in content


def test_spend_requirements_defined() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "spend dataset reference" in content.lower()
    assert "spend amount column" in content
    assert "BLOCKED_MISSING_SPEND_FOR_EFFICIENCY" in content


def test_value_margin_requirements_defined() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "value/margin mapping" in content.lower() or "value mapping" in content.lower()
    assert "margin/profit mapping" in content.lower()
    assert "BLOCKED_MISSING_VALUE_MAPPING_FOR_ROAS" in content


def test_typed_handoff_object_defined() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "GeoXReadoutInputHandoff" in content
    assert "panel_exp_target_contract" in content
    assert "GEOX_FINAL_TEST_RESULTS_SPEND_AND_ROI_READINESS_CONTRACT_001" in content


def test_mip_panel_exp_ownership_split_defined() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "MIP owner?" in content
    assert "panel_exp owner?" in content
    assert "User request interpretation" in content
    assert "Compute spend_delta readiness" in content


def test_panel_exp_owns_spend_delta_derivation() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "panel_exp" in content
    assert "spend_delta" in content
    assert "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001" in content


def test_mip_does_not_compute_spend_delta() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "must **not** compute `spend_delta`" in content
    assert "No embedded `spend_delta`" in content


def test_claim_authorization_delegated() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "CLAIM_AUTHORIZATION_RUNTIME_001" in content
    assert "claim authorization" in content.lower()


def test_runtime_followup_artifact() -> None:
    content = _DOC.read_text(encoding="utf-8")
    assert "MIP_GEOX_READOUT_INPUT_RESOLUTION_RUNTIME_001" in content


def test_readout_intents_defined() -> None:
    content = _DOC.read_text(encoding="utf-8")
    for intent in _READOUT_INTENTS:
        assert intent in content, f"missing intent: {intent}"


def test_summary_json_validates() -> None:
    summary = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert summary["artifact_id"] == "MIP_GEOX_READOUT_INPUT_REQUIREMENTS_AND_HANDOFF_CONTRACT_001"
    assert summary["mip_geox_readout_handoff_contract_completed"] is True
    assert summary["panel_exp_spend_delta_delegated"] is True
    assert summary["claim_authorization_delegated"] is True
    assert summary["recommended_next_mip_artifact"] == (
        "MIP_GEOX_READOUT_INPUT_RESOLUTION_RUNTIME_001"
    )
    assert summary["required_panel_exp_runtime"] == (
        "GEOX_POST_TEST_SPEND_READINESS_ADAPTER_RUNTIME_001"
    )
    for flag in _FORBIDDEN_FLAGS:
        assert summary[flag] is False, f"forbidden flag must be false: {flag}"


def test_summary_json_forbidden_flags_not_true() -> None:
    raw = _SUMMARY.read_text(encoding="utf-8")
    for pattern in _FORBIDDEN_RUNTIME_PATTERNS:
        assert not re.search(pattern, raw), f"forbidden pattern matched: {pattern}"


def test_no_llm_control_plane_docs_modified_in_this_lane() -> None:
    """This lane must not depend on LLM control-plane evaluation strategy files."""
    llm_eval_doc = Path(
        "docs/evaluation/MIP_LLM_CONTROL_PLANE_EVALUATION_STRATEGY_001.md"
    )
    assert not llm_eval_doc.is_file()
