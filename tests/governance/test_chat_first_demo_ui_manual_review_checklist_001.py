"""Governance checks for chat-first demo UI manual review checklist 001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_CHECKLIST = Path(
    "docs/demo/MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_CHECKLIST_001.md"
)
_SUMMARY = Path(
    "docs/demo/archives/"
    "MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_CHECKLIST_001_summary.json"
)
_TRUE_FLAGS = (
    "manual_review_checklist_created",
    "local_launch_checklist_documented",
    "demo_entry_checklist_documented",
    "sample_question_checklist_documented",
    "expected_answer_checklist_documented",
    "claim_safety_checklist_documented",
    "panel_checklist_documented",
    "lifecycle_walkthrough_checklist_documented",
    "no_runtime_execution_checklist_documented",
    "docker_validation_checklist_documented",
    "manual_review_result_template_documented",
    "pass_fail_criteria_documented",
)
_FALSE_FLAGS = (
    "ui_features_added",
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
    "uploaded_data_workflow_implemented",
)


def _content() -> str:
    return _CHECKLIST.read_text(encoding="utf-8")


def _load_summary() -> dict[str, Any]:
    value = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_checklist_and_summary_exist_and_summary_is_parseable() -> None:
    assert _CHECKLIST.is_file()
    assert _SUMMARY.is_file()
    _load_summary()


def test_checklist_identifies_artifact_and_completed_preconditions() -> None:
    content = _content()
    for reference in (
        "MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_CHECKLIST_001",
        "MIP_DEMO_DOMAIN_DATASETS_001",
        "MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001",
        "MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001",
        "MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001",
        "MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001",
        "MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_001",
        "MIP_CHAT_FIRST_DEMO_UI_SMOKE_VALIDATION_001",
    ):
        assert reference in content
    for commit in ("1662b92", "0430e07", "fccb2fe", "5616ac9", "ecec3e5", "95c3ded"):
        assert commit in content


def test_checklist_contains_all_required_review_sections() -> None:
    content = _content()
    for heading in (
        "## 1. Scope",
        "## 2. Preconditions",
        "## 3. Local launch checklist",
        "## 4. Demo entry checklist",
        "## 5. Sample question checklist",
        "## 6. Expected answer checklist",
        "## 7. Claim-safety checklist",
        "## 8. Panel checklist",
        "## 9. Lifecycle walkthrough checklist",
        "## 10. No-runtime-execution checklist",
        "## 11. Docker validation checklist",
        "## 12. Manual review result template",
        "## 13. Pass/fail criteria",
        "## 14. Recommended next artifact",
    ):
        assert heading in content


def test_local_launch_and_demo_entry_are_actionable() -> None:
    content = _content()
    for command in (
        "git switch main",
        "git pull --ff-only origin main",
        "poetry install",
        "poetry run streamlit run app/streamlit_app.py",
    ):
        assert command in content
    for phrase in (
        "Marketing Intelligence Platform",
        "Chat-first SaaS demo",
        "saas_subscriptions_demo_v1",
        "No uploaded-data workflow",
        "No provider or API key",
    ):
        assert phrase in content


def test_sample_categories_and_questions_are_complete() -> None:
    content = _content()
    for category in (
        "mmm_readiness",
        "geox_readiness",
        "grain_compatibility",
        "budget_planning_guardrail",
        "calibration_context",
        "data_missingness",
    ):
        assert f"`{category}`" in content
    for question in (
        "Can this dataset support MMM readiness?",
        "What data is missing for MMM?",
        "Can I run a DMA-level GeoX experiment for Meta?",
        "Explain the grain difference between raw spend and KPI.",
        "Can I use this to recommend a budget shift next quarter?",
        "What does the calibration signal let me say?",
        "What can you safely say from this data?",
        "What can you not say yet?",
    ):
        assert question in content


def test_expected_answers_panels_and_lifecycle_are_reviewed() -> None:
    content = _content()
    for phrase in (
        "deterministic or fixture-backed",
        "Allowed claims",
        "Cannot-say / blocked-claims panel",
        "Next-required-artifact panel",
        "Evidence inspected panel",
        "Lifecycle walkthrough panel",
        "Select demo dataset",
        "Inspect raw spend and KPI grain",
        "Use canonical MMM-ready panel",
        "Ask for channel ROI",
        "Ask for budget shift",
        "Ask for GeoX assignment",
        "future integration",
    ):
        assert phrase in content


def test_claim_safety_and_no_runtime_boundary_are_explicit() -> None:
    content = _content()
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
    for runtime in (
        "LLM provider execution",
        "prompt execution",
        "MMM fitting",
        "MMM export adapter execution",
        "ROI/ROAS computation",
        "optimizer/simulator execution",
        "uploaded-data workflow",
    ):
        assert runtime in content


def test_docker_reporting_rule_and_result_template_are_complete() -> None:
    content = _content()
    for command in ("docker version", "docker info", "docker ps", "make validate-docker"):
        assert command in content
    assert "Docker pass cannot be claimed" in content
    assert "unless `make validate-docker` exits 0" in content
    assert "## Manual review result" in content
    assert "Pass / pass with known limitations / fail" in content
    assert "Host fallback used: yes/no" in content


def test_pass_fail_criteria_and_next_artifact_are_explicit() -> None:
    content = _content()
    assert "Pass requires all of the following" in content
    assert "Fail if any of the following occurs" in content
    assert "Docker status is misreported" in content
    assert "MIP_CHAT_FIRST_DEMO_UI_RELEASE_READINESS_AUDIT_001" in content


def test_summary_flags_match_documented_boundary() -> None:
    summary = _load_summary()
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag
    assert summary["recommended_next_artifact"] == (
        "MIP_CHAT_FIRST_DEMO_UI_RELEASE_READINESS_AUDIT_001"
    )
