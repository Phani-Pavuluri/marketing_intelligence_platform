"""Smoke validation for the deterministic chat-first demo UI path."""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from typing import Any

import pytest

from mip.demo.chat_first_demo import (
    build_deterministic_demo_response,
    load_chat_first_demo_fixture,
)

FIXTURE_DIR = Path("data/demo/domain_fixtures/saas_subscriptions/v1")
IMPLEMENTATION_SUMMARY = Path(
    "docs/demo/archives/MIP_CHAT_FIRST_DEMO_UI_IMPLEMENTATION_001_summary.json"
)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _response_text(question_id: str) -> str:
    fixture = load_chat_first_demo_fixture()
    response = build_deterministic_demo_response(fixture, question_id)
    return " ".join(
        (
            response.allowed_answer_summary,
            *response.cannot_say,
            *response.blocked_claims,
            response.next_required_artifact or "",
        )
    ).lower()


def test_fixture_loader_smoke_loads_all_governed_json_files() -> None:
    fixture = load_chat_first_demo_fixture()

    expected_files = (
        "manifest.json",
        "sample_questions.json",
        "expected_answer_behavior.json",
        "lifecycle_walkthrough.json",
    )
    assert fixture.inspected_files == expected_files
    assert all((FIXTURE_DIR / filename).is_file() for filename in expected_files)
    assert fixture.fixture_id == "saas_subscriptions_demo_v1"
    assert len(fixture.questions) == len(fixture.behaviors_by_question_id) == 8


def test_sample_question_categories_cover_the_demo_question_set() -> None:
    fixture = load_chat_first_demo_fixture()

    assert {question.category for question in fixture.questions} == {
        "mmm_readiness",
        "geox_readiness",
        "grain_compatibility",
        "budget_planning_guardrail",
        "calibration_context",
        "data_missingness",
    }


@pytest.mark.parametrize(
    ("question_id", "expected_fragments"),
    (
        ("mmm_readiness_1", ("readiness inspection", "mmm fitting", "roi")),
        ("geox_readiness_1", ("design readiness", "assignment", "lift")),
        (
            "grain_compatibility_1",
            ("week×dma×channel", "double-counts conversions", "pivots spend wide"),
        ),
        (
            "budget_planning_guardrail_1",
            ("budget shift recommendations are blocked", "recommendationcontract"),
        ),
    ),
)
def test_deterministic_answers_render_from_fixture_metadata(
    question_id: str,
    expected_fragments: tuple[str, ...],
) -> None:
    rendered = _response_text(question_id)

    assert all(fragment in rendered for fragment in expected_fragments)


def test_blocked_claims_remain_visible_across_fixture_and_answers() -> None:
    fixture = load_chat_first_demo_fixture()
    behavior_text = " ".join(
        _response_text(question.question_id) for question in fixture.questions
    )
    blocked_text = " ".join(fixture.forbidden_claims).lower() + " " + behavior_text

    for claim in (
        "roi",
        "roas",
        "channel contribution",
        "budget recommendation",
        "optimized next-quarter spend",
        "geox assignment",
        "geox lift",
        "geox readout",
        "causal claim",
    ):
        assert claim in blocked_text


def test_allowed_claims_stay_within_fixture_backed_explanation_boundary() -> None:
    fixture = load_chat_first_demo_fixture()

    assert set(fixture.allowed_claims) == {
        "readiness",
        "grain compatibility",
        "missing data",
        "normalization requirement",
        "evidence availability",
        "blocked reason",
        "next required artifact",
    }
    calibration = _response_text("calibration_context_1")
    assert "context" in calibration
    assert "does not calibrate a live model" in calibration
    assert "authorize roi, lift, or recommendation claims" in calibration


def test_lifecycle_exposes_available_blocked_and_future_integration_steps() -> None:
    fixture = load_chat_first_demo_fixture()

    available_now = [step for step in fixture.lifecycle_steps if step.available_now]
    blocked = [step for step in fixture.lifecycle_steps if step.blocked]
    future_integrations = [
        step for step in fixture.lifecycle_steps if step.next_required_artifact
    ]

    assert available_now
    assert blocked
    assert future_integrations
    assert all(step.fixture_backed for step in fixture.lifecycle_steps)
    assert all(not step.available_now for step in blocked)


def test_ui_import_and_required_panel_renderers_are_available() -> None:
    import app.streamlit_app as streamlit_app

    assert callable(streamlit_app.main)
    assert callable(streamlit_app._render_chat_first_demo_tab)
    answer_source = inspect.getsource(streamlit_app._render_chat_first_answer)
    tab_source = inspect.getsource(streamlit_app._render_chat_first_demo_tab)
    lifecycle_source = inspect.getsource(streamlit_app._render_chat_first_lifecycle)

    for panel in (
        "Deterministic answer",
        "Evidence inspected",
        "Next required artifact",
        "Cannot say",
        "Blocked claims",
    ):
        assert panel in answer_source
    assert "Fixture readiness and allowed claims" in tab_source
    assert "Fixture-wide forbidden claims" in tab_source
    assert "Full MMM + GeoX lifecycle walkthrough" in lifecycle_source


def test_no_provider_model_optimizer_or_geox_runtime_path_is_enabled() -> None:
    import mip.demo.chat_first_demo as helper

    summary = _load_json(IMPLEMENTATION_SUMMARY)
    false_runtime_flags = (
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
    assert all(summary[flag] is False for flag in false_runtime_flags)

    source = inspect.getsource(helper).lower()
    forbidden_runtime_calls = (
        "provider.generate(",
        "provider.complete(",
        "execute_prompt(",
        "fit_mmm(",
        "load_mmm_export(",
        "compute_roi(",
        "compute_roas(",
        "optimize_budget(",
        "run_geox(",
        "assign_markets(",
        "compute_lift(",
    )
    assert not any(call in source for call in forbidden_runtime_calls)
