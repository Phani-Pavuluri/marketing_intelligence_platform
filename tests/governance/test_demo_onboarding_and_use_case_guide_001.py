"""Governance checks for demo onboarding and use case guide 001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_GUIDE = Path("docs/demo/MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001.md")
_SUMMARY = Path(
    "docs/demo/archives/MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001_summary.json"
)
_FIXTURE_DIR = Path("data/demo/domain_fixtures/saas_subscriptions/v1")
_FIXTURE_JSON_FILES = (
    "sample_questions.json",
    "expected_answer_behavior.json",
    "lifecycle_walkthrough.json",
    "manifest.json",
)
_CATEGORIES = (
    "mmm_readiness",
    "geox_readiness",
    "grain_compatibility",
    "budget_planning_guardrail",
    "calibration_context",
    "data_missingness",
)
_TRUE_FLAGS = (
    "demo_onboarding_guide_created",
    "saas_subscriptions_fixture_referenced",
    "sample_questions_referenced",
    "expected_answer_behavior_referenced",
    "lifecycle_walkthrough_referenced",
    "mmm_readiness_flow_documented",
    "geox_readiness_flow_documented",
    "grain_compatibility_flow_documented",
    "budget_guardrail_flow_documented",
    "calibration_context_flow_documented",
    "allowed_claims_documented",
    "blocked_claims_documented",
    "mmm_export_dependency_documented",
    "recommendation_contract_dependency_documented",
    "geox_assignment_lift_blocked_documented",
    "future_ui_implications_documented",
)
_FALSE_FLAGS = (
    "ui_implemented",
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


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_guide_and_summary_exist_and_summary_is_parseable() -> None:
    assert _GUIDE.is_file()
    assert _SUMMARY.is_file()
    _load_json(_SUMMARY)


def test_guide_identifies_artifact_fixture_and_fixture_contracts() -> None:
    content = _GUIDE.read_text(encoding="utf-8")
    assert "MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001" in content
    assert "data/demo/domain_fixtures/saas_subscriptions/v1/" in content
    assert "sample_questions.json" in content
    assert "expected_answer_behavior.json" in content
    assert "lifecycle_walkthrough.json" in content


def test_guide_includes_all_sample_question_categories() -> None:
    content = _GUIDE.read_text(encoding="utf-8")
    for category in _CATEGORIES:
        assert f"`{category}`" in content


def test_guide_documents_allowed_claims() -> None:
    content = _GUIDE.read_text(encoding="utf-8")
    for phrase in (
        "readiness status",
        "grain compatibility",
        "normalization requirements",
        "missing-data",
        "GeoX design-readiness explanations",
        "calibration context as fixture/demo context only",
        "next required governed artifact",
    ):
        assert phrase in content


def test_guide_documents_blocked_claims() -> None:
    content = _GUIDE.read_text(encoding="utf-8")
    for phrase in (
        "channel ROI",
        "ROAS",
        "incremental contribution",
        "channel contribution",
        "budget shift recommendation",
        "future spend recommendation",
        "optimized spend",
        "GeoX treatment/control assignment",
        "GeoX lift",
        "GeoX readout",
    ):
        assert phrase in content


def test_guide_documents_mmm_export_and_recommendation_dependencies() -> None:
    content = _GUIDE.read_text(encoding="utf-8")
    for artifact in (
        "MMMExportBundle",
        "MMMChannelROIArtifact",
        "MMMOptimizerResultArtifact",
        "MMMRecommendationContract",
        "RecommendationContract",
        "MIP_MMM_EXPORT_ADAPTER_CONTRACT_001",
    ):
        assert artifact in content


def test_guide_documents_future_ui_without_implementing_it() -> None:
    content = _GUIDE.read_text(encoding="utf-8")
    assert "Future chat-first UI implications" in content
    assert "Start here card" in content
    assert "sample question chips" in content
    assert "This artifact does not implement UI" in content
    assert "MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001" in content


def test_summary_flags_match_guide_boundary() -> None:
    summary = _load_json(_SUMMARY)
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag
    assert summary["recommended_next_artifact"] == (
        "MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001"
    )


def test_fixture_json_files_remain_parseable() -> None:
    for filename in _FIXTURE_JSON_FILES:
        path = _FIXTURE_DIR / filename
        assert path.is_file(), filename
        _load_json(path)
