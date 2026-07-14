"""Governance checks for chat-first demo UI release readiness audit 001."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_AUDIT = Path("docs/demo/MIP_CHAT_FIRST_DEMO_UI_RELEASE_READINESS_AUDIT_001.md")
_SUMMARY = Path(
    "docs/demo/archives/MIP_CHAT_FIRST_DEMO_UI_RELEASE_READINESS_AUDIT_001_summary.json"
)
_TRUE_FLAGS = (
    "release_readiness_audit_created",
    "demo_domain_datasets_referenced",
    "llm_response_verifier_audit_referenced",
    "onboarding_guide_referenced",
    "ui_design_plan_referenced",
    "ui_implementation_plan_referenced",
    "ui_implementation_referenced",
    "ui_smoke_validation_referenced",
    "manual_review_checklist_referenced",
    "fixture_backed_behavior_audited",
    "claim_safety_audited",
    "docker_validation_status_audited",
    "internal_demo_readiness_decision_recorded",
    "external_release_readiness_decision_recorded",
    "production_claim_authorization_decision_recorded",
    "release_decision_table_created",
    "required_next_actions_documented",
)
_FALSE_FLAGS = (
    "external_release_authorized",
    "production_claims_authorized",
    "provider_backed_llm_demo_authorized",
    "live_mmm_geox_decisioning_authorized",
    "uploaded_data_workflow_authorized",
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


def _content() -> str:
    return _AUDIT.read_text(encoding="utf-8")


def _load_summary() -> dict[str, Any]:
    value = json.loads(_SUMMARY.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_audit_and_summary_exist_and_summary_is_parseable() -> None:
    assert _AUDIT.is_file()
    assert _SUMMARY.is_file()
    _load_summary()


def test_audit_identifies_itself_and_all_required_inputs() -> None:
    content = _content()
    for reference in (
        "MIP_CHAT_FIRST_DEMO_UI_RELEASE_READINESS_AUDIT_001",
        "MIP_DEMO_DOMAIN_DATASETS_001",
        "MIP_MMM_LLM_RESPONSE_VERIFIER_AUDIT_001",
        "MIP_DEMO_ONBOARDING_AND_USE_CASE_GUIDE_001",
        "MIP_CHAT_FIRST_DEMO_UI_DESIGN_PLAN_001",
        "MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_PLAN_001",
        "MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_001",
        "MIP_CHAT_FIRST_DEMO_UI_SMOKE_VALIDATION_001",
        "MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_CHECKLIST_001",
    ):
        assert reference in content
    for commit in ("1662b92", "0430e07", "fccb2fe", "5616ac9", "ecec3e5", "95c3ded", "6f40ae4"):
        assert commit in content


def test_audit_covers_all_readiness_dimensions() -> None:
    content = _content()
    for dimension in (
        "Fixture availability",
        "Deterministic answer behavior",
        "Sample question coverage",
        "Allowed-claims rendering",
        "Blocked-claims rendering",
        "Next-required-artifact rendering",
        "Evidence inspected rendering",
        "Lifecycle walkthrough rendering",
        "Automated smoke tests",
        "Manual review checklist availability",
        "Docker validation status",
        "Release blockers",
        "Production-claim blockers",
    ):
        assert dimension in content


def test_audit_records_required_release_verdicts() -> None:
    content = _content()
    for verdict in (
        "INTERNAL_DEMO_READY_PENDING_MANUAL_REVIEW",
        "EXTERNAL_RELEASE_BLOCKED_PENDING_MANUAL_REVIEW_AND_FULL_DOCKER_GATE_DECISION",
        "PRODUCTION_CLAIMS_NOT_AUTHORIZED",
    ):
        assert verdict in content


def test_docker_audit_distinguishes_historical_and_current_failures() -> None:
    content = _content()
    assert (
        "Docker validation executed; tests passed inside Docker; strict full-repo Ruff gate "
        "failed on known pre-existing lint debt. This is not a full Docker validation pass."
        in content
    )
    assert "Ruff passed" in content
    assert "Global mypy then failed" in content
    assert "The required post-change `make validate-docker` run then exited 0" in content
    assert "the final Docker validation passed" in content
    assert "Host fallback was not used" in content


def test_production_and_geox_claims_remain_blocked() -> None:
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


def test_release_decision_table_has_all_required_surfaces_and_columns() -> None:
    content = _content()
    for column in ("Status", "Evidence", "Blocker", "Next action"):
        assert column in content
    for surface in (
        "Internal demo",
        "External demo",
        "Production-like claims",
        "Provider-backed LLM demo",
        "Live MMM/GeoX decisioning",
        "Uploaded-data workflow",
    ):
        assert f"| {surface} |" in content


def test_required_actions_and_next_artifact_are_documented() -> None:
    content = _content()
    assert "## 9. Required next actions" in content
    assert "Run `MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_CHECKLIST_001`" in content
    assert "Keep production claims blocked" in content
    assert "MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_RESULT_001" in content


def test_summary_flags_and_verdicts_match_audit_boundary() -> None:
    summary = _load_summary()
    for flag in _TRUE_FLAGS:
        assert summary[flag] is True, flag
    for flag in _FALSE_FLAGS:
        assert summary[flag] is False, flag
    assert summary["internal_demo_verdict"] == (
        "INTERNAL_DEMO_READY_PENDING_MANUAL_REVIEW"
    )
    assert summary["external_release_verdict"] == (
        "EXTERNAL_RELEASE_BLOCKED_PENDING_MANUAL_REVIEW_AND_FULL_DOCKER_GATE_DECISION"
    )
    assert summary["production_claims_verdict"] == "PRODUCTION_CLAIMS_NOT_AUTHORIZED"
    assert summary["recommended_next_artifact"] == (
        "MIP_CHAT_FIRST_DEMO_UI_MANUAL_REVIEW_RESULT_001"
    )
