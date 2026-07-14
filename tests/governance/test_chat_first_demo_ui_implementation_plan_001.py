"""Governance checks for chat-first demo UI implementation plan 001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_PLAN = Path("docs/demo/MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001.md")
_SUMMARY = Path(
    "docs/demo/archives/MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001_summary.json"
)
_TRUE_FLAGS = (
    "chat_first_demo_ui_implementation_plan_created",
    "ui_design_plan_referenced",
    "demo_onboarding_guide_referenced",
    "demo_fixture_referenced",
    "preconditions_documented",
    "app_file_discovery_plan_documented",
    "future_files_likely_to_be_touched_documented",
    "staged_implementation_sequence_documented",
    "deterministic_demo_answer_rule_documented",
    "future_ui_components_documented",
    "claim_safety_requirements_documented",
    "next_required_artifact_mapping_documented",
    "validation_plan_documented",
    "rollback_safety_plan_documented",
    "future_integration_placeholders_documented",
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


def test_plan_and_summary_exist_and_summary_is_parseable() -> None:
    assert _PLAN.is_file()
    assert _SUMMARY.is_file()
    _load_summary()


def test_plan_references_prerequisite_artifacts_and_fixture() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for reference in (
        "MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001",
        "MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001",
        "MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001",
        "MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001",
        "MIP_DEMO_DOMAIN_DATASETS_001",
        "data/demo/domain_fixtures/saas_subscriptions/v1/",
    ):
        assert reference in content


def test_plan_lists_precondition_commits() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for commit in ("1662b92", "0430e07", "fccb2fe", "5616ac9"):
        assert commit in content


def test_plan_includes_app_file_discovery_and_candidate_categories() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "## App/file discovery plan" in content
    assert "find app -maxdepth 4 -type f" in content
    assert "find src/mip -maxdepth 4 -type f" in content
    assert "## Future files likely to be touched" in content
    for candidate in (
        "app/streamlit_app.py",
        "app/demo_fixtures.py",
        "app/ui_renderers.py",
        "tests/app/test_streamlit_entrypoint.py",
    ):
        assert candidate in content
    assert "candidate categories and paths, not edits authorized" in content


def test_plan_includes_all_staged_implementation_phases() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for phase in range(6):
        assert f"### Phase {phase}" in content


def test_plan_defines_deterministic_answer_rule_and_components() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "## Deterministic demo answer rule" in content
    assert "not from an LLM provider" in content
    assert "## UI components to implement later" in content
    for component in (
        "StartHerePanel",
        "SampleQuestionChips",
        "ChatMessagePanel",
        "ReadinessCards",
        "EvidenceInspectedPanel",
        "CannotSayPanel",
        "BlockedClaimsPanel",
        "NextRequiredArtifactPanel",
        "LifecycleWalkthroughPanel",
        "FutureIntegrationBadges",
    ):
        assert component in content


def test_plan_defines_claim_safety_and_next_artifact_mapping() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "## Claim-safety requirements" in content
    for claim in (
        "channel ROI",
        "ROAS",
        "incremental contribution",
        "channel contribution",
        "budget shift recommendation",
        "optimized spend",
        "GeoX treatment/control assignment",
        "GeoX lift",
        "GeoX readout",
    ):
        assert claim in content
    assert "## Next-required-artifact mapping" in content
    assert "MMMExportBundle" in content
    assert "MMMRecommendationContract" in content
    assert "governed GeoX design artifact" in content
    assert "governed GeoX readout artifact" in content


def test_plan_includes_validation_rollback_and_future_placeholders() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    for heading in (
        "## Validation plan for future implementation",
        "## Rollback and safety plan",
        "## Future integration placeholders",
    ):
        assert heading in content
    assert "feature flag, dedicated demo route, or isolated section" in content
    assert "provider-backed LLM execution" in content
    assert "production `TrustReport` / `DecisionSurface` integration" in content


def test_plan_explicitly_defers_ui_and_streamlit_implementation() -> None:
    content = _PLAN.read_text(encoding="utf-8")
    assert "does not implement UI code or app behavior" in content
    assert "no UI code" in content
    assert "no Streamlit behavior change" in content
    assert "MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_001" in content


def test_summary_flags_match_plan_boundary() -> None:
    summary = _load_summary()
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag
    assert summary["recommended_next_artifact"] == (
        "MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_001"
    )
