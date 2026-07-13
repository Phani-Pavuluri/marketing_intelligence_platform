"""Governance checks for MMM LLM response verifier audit 001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_AUDIT = Path("docs/audits/MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001.md")
_SUMMARY = Path(
    "docs/audits/archives/MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001_summary.json"
)
_FIXTURE_DIR = Path("data/demo/domain_fixtures/saas_subscriptions/v1")
_FIXTURE_FILES = (
    "sample_questions.json",
    "expected_answer_behavior.json",
    "lifecycle_walkthrough.json",
    "manifest.json",
)
_CATEGORIES = {
    "mmm_readiness",
    "geox_readiness",
    "grain_compatibility",
    "budget_planning_guardrail",
    "calibration_context",
    "data_missingness",
}
_TRUE_FLAGS = (
    "mmm_llm_response_verifier_audit_completed",
    "demo_fixture_inputs_inspected",
    "sample_questions_verified",
    "expected_answer_behavior_verified",
    "lifecycle_walkthrough_verified",
    "mmm_readiness_questions_verified",
    "geox_readiness_questions_verified",
    "grain_compatibility_questions_verified",
    "budget_planning_guardrail_questions_verified",
    "calibration_context_questions_verified",
    "data_missingness_questions_verified",
    "allowed_readiness_claims_verified",
    "blocked_roi_roas_claims_verified",
    "blocked_channel_contribution_claims_verified",
    "blocked_budget_recommendation_claims_verified",
    "blocked_geox_assignment_lift_claims_verified",
    "mmm_export_dependency_recorded",
    "recommendation_contract_dependency_recorded",
    "response_chain_reviewed",
    "cannot_say_boundaries_verified",
    "safe_response_guidance_verified",
)
_FALSE_FLAGS = (
    "llm_provider_execution_implemented",
    "prompt_execution_implemented",
    "ui_implementation_implemented",
    "mmm_fitting_implemented",
    "mmm_export_adapter_implemented",
    "roi_roas_computation_implemented",
    "incremental_contribution_computation_implemented",
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


def test_audit_and_summary_exist_and_summary_is_parseable() -> None:
    assert _AUDIT.is_file()
    assert _SUMMARY.is_file()
    _load_json(_SUMMARY)


def test_demo_fixture_files_exist_and_are_parseable() -> None:
    for filename in _FIXTURE_FILES:
        path = _FIXTURE_DIR / filename
        assert path.is_file(), filename
        _load_json(path)


def test_audit_identifies_artifact_categories_and_allowed_behavior() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    assert "MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001" in content
    for category in _CATEGORIES:
        assert f"`{category}`" in content
    for phrase in (
        "readiness-compatible",
        "week × DMA × channel",
        "once per `week × DMA`",
        "GeoX design readiness",
        "fixture/context only",
    ):
        assert phrase in content


def test_audit_records_blocked_claims_and_dependencies() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for phrase in (
        "channel ROI",
        "ROAS",
        "incremental contribution",
        "channel contribution",
        "budget shift recommendations",
        "future spend recommendations",
        "optimized spend",
        "GeoX treatment/control assignment",
        "GeoX lift",
        "GeoX readout",
        "MMMExportBundle",
        "MMM-EXPORT-001/002/003",
        "MIP_MMM_EXPORT_ADAPTER_CONTRACT_001",
        "RecommendationContract",
    ):
        assert phrase in content


def test_audit_records_response_chain_verdict_non_goals_and_next_artifact() -> None:
    content = _AUDIT.read_text(encoding="utf-8")
    for name in (
        "MMMPlanningRenderedResponse",
        "MMMLLMResponseBoundary",
        "MMMResponseBoundaryApplicationOutput",
        "MMMResponseTemplateOutput",
        "can_say",
        "cannot_say",
        "safe_response_guidance",
        "ready_for_llm_prompt_assembly",
        "CHECKPOINT_PASSED_READY_FOR_DEMO_ONBOARDING_GUIDE",
        "MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001",
    ):
        assert name in content
    for non_goal in (
        "no LLM provider execution",
        "no prompt execution",
        "no UI implementation",
        "no MMM fitting",
        "no MMM export adapter",
        "no ROI/ROAS computation",
        "no incremental contribution computation",
        "no optimizer/simulator",
        "no budget recommendation",
        "no GeoX assignment",
        "no GeoX lift/readout",
        "no `CalibrationSignal` runtime ingestion",
        "no `DecisionSurface` generation",
        "no `RecommendationContract` generation",
    ):
        assert non_goal in content


def test_summary_flags_match_audit_boundary() -> None:
    summary = _load_json(_SUMMARY)
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag
    assert summary["audit_verdict"] == (
        "CHECKPOINT_PASSED_READY_FOR_DEMO_ONBOARDING_GUIDE"
    )
    assert summary["recommended_next_artifact"] == (
        "MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001"
    )


def test_sample_questions_cover_required_categories() -> None:
    questions = _load_json(_FIXTURE_DIR / "sample_questions.json")["questions"]
    assert isinstance(questions, list)
    assert {question["category"] for question in questions} == _CATEGORIES


def test_expected_answers_block_roi_budget_and_geox_claims() -> None:
    behaviors = _load_json(_FIXTURE_DIR / "expected_answer_behavior.json")[
        "behaviors"
    ]
    assert isinstance(behaviors, list)
    blocked = {
        str(claim).lower()
        for behavior in behaviors
        for claim in behavior["blocked_claims"]
    }
    assert {"channel roi", "roas"} <= blocked
    assert {"budget shift recommendation", "future spend recommendation"} <= blocked
    assert {"geox lift", "treatment/control assignment"} <= blocked
