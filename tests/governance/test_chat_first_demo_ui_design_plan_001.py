"""Governance checks for chat-first demo UI design plan 001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_DESIGN = Path("docs/demo/MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001.md")
_SUMMARY = Path(
    "docs/demo/archives/MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001_summary.json"
)
_TRUE_FLAGS = (
    "chat_first_demo_ui_design_plan_created",
    "demo_onboarding_guide_referenced",
    "demo_fixture_referenced",
    "sample_questions_referenced",
    "expected_answer_behavior_referenced",
    "lifecycle_walkthrough_referenced",
    "chat_first_primary_workflow_defined",
    "start_here_flow_defined",
    "sample_question_chips_defined",
    "readiness_cards_defined",
    "evidence_inspected_panel_defined",
    "cannot_say_blocked_claims_panel_defined",
    "next_required_artifact_panel_defined",
    "lifecycle_walkthrough_panel_defined",
    "llm_response_boundary_integration_documented",
    "future_integration_placeholders_documented",
    "blocked_claims_documented",
)
_FALSE_FLAGS = (
    "ui_code_implemented",
    "streamlit_behavior_changed",
    "llm_provider_execution_implemented",
    "prompt_execution_implemented",
    "mmm_fitting_implemented",
    "mmm_export_adapter_implemented",
    "roi_roas_computation_implemented",
    "channel_contribution_computation_implemented",
    "optimizer_simulator_implemented",
    "budget_recommendation_generated",
    "geox_assignment_implemented",
    "geox_lift_readout_implemented",
    "calibration_signal_runtime_ingestion_implemented",
    "decision_surface_generation_implemented",
    "recommendation_contract_generation_implemented",
)


def _load_summary() -> dict[str, Any]:
    value = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_design_and_summary_exist_and_summary_is_parseable() -> None:
    assert _DESIGN.is_file()
    assert _SUMMARY.is_file()
    _load_summary()


def test_design_references_artifact_inputs_and_fixture() -> None:
    content = _DESIGN.read_text(encoding="utf-8")
    for reference in (
        "MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001",
        "MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001",
        "data/demo/domain_fixtures/saas_subscriptions/v1/",
        "sample_questions.json",
        "expected_answer_behavior.json",
        "lifecycle_walkthrough.json",
    ):
        assert reference in content


def test_design_defines_chat_first_workflow_and_start_here_flow() -> None:
    content = _DESIGN.read_text(encoding="utf-8")
    assert "Chat is the primary workflow" in content
    assert "Demo shortcuts guide the user into chat" in content
    assert "Evidence and guardrail panels make the chat answer auditable" in content
    assert "## Start-here flow" in content
    assert "Try SaaS subscriptions demo dataset" in content


def test_design_defines_question_chips_and_readiness_cards() -> None:
    content = _DESIGN.read_text(encoding="utf-8")
    assert "## Sample question chips" in content
    assert "Can this dataset support MMM readiness?" in content
    assert "## Readiness cards" in content
    for field in (
        "Status",
        "Evidence inspected",
        "Allowed summary",
        "Cannot-say",
        "Next required artifact",
    ):
        assert field in content


def test_design_defines_auditability_and_guardrail_panels() -> None:
    content = _DESIGN.read_text(encoding="utf-8")
    for heading in (
        "## Evidence inspected panel",
        "## Cannot-say / blocked-claims panel",
        "## Next-required-artifact panel",
        "## Lifecycle walkthrough panel",
    ):
        assert heading in content


def test_design_lists_all_required_blocked_claims() -> None:
    content = _DESIGN.read_text(encoding="utf-8")
    for claim in (
        "channel ROI",
        "ROAS",
        "incremental contribution",
        "channel contribution",
        "budget shift recommendation",
        "future spend recommendation",
        "optimized spend",
        "MMM model fit result",
        "MMM posterior/effect result",
        "GeoX treatment/control assignment",
        "GeoX lift",
        "GeoX readout",
        "causal claim",
    ):
        assert claim in content


def test_design_documents_response_chain_and_preserved_fields() -> None:
    content = _DESIGN.read_text(encoding="utf-8")
    for name in (
        "MMMPlanningRenderedResponse",
        "MMMLLMResponseBoundary",
        "MMMResponseBoundaryApplicationOutput",
        "MMMResponseTemplateOutput",
        "can_say",
        "cannot_say",
        "safe_response_guidance",
        "lineage and provenance",
        "human-review indicators",
    ):
        assert name in content


def test_design_documents_future_integration_placeholders() -> None:
    content = _DESIGN.read_text(encoding="utf-8")
    assert "## Future integration placeholders" in content
    for placeholder in (
        "MMM export adapter",
        "MMM ROI/contribution artifact rendering",
        "MMM optimizer / `RecommendationContract` rendering",
        "GeoX design artifact rendering",
        "GeoX readout artifact rendering",
        "provider-backed LLM execution",
        "uploaded-data workflow",
        "production `TrustReport` / `DecisionSurface` integration",
    ):
        assert placeholder in content


def test_design_explicitly_defers_ui_and_streamlit_implementation() -> None:
    content = _DESIGN.read_text(encoding="utf-8")
    assert "does not implement UI code or app behavior" in content
    assert "no UI code" in content
    assert "no Streamlit changes" in content
    assert "MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001" in content


def test_summary_flags_match_design_boundary() -> None:
    summary = _load_summary()
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag
    assert summary["recommended_next_artifact"] == (
        "MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001"
    )
