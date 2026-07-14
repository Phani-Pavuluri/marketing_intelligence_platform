"""Tests for deterministic chat-first demo loading and answer behavior."""

from __future__ import annotations

import inspect

import pytest

from mip.demo.chat_first_demo import (
    build_deterministic_demo_response,
    load_chat_first_demo_fixture,
)


def test_fixture_loader_parses_and_cross_references_all_json_inputs() -> None:
    fixture = load_chat_first_demo_fixture()
    assert fixture.fixture_id == "saas_subscriptions_demo_v1"
    assert fixture.inspected_files == (
        "manifest.json",
        "sample_questions.json",
        "expected_answer_behavior.json",
        "lifecycle_walkthrough.json",
    )
    assert len(fixture.questions) == len(fixture.behaviors_by_question_id) == 8
    assert len(fixture.lifecycle_steps) == 10


def test_sample_question_categories_are_present() -> None:
    fixture = load_chat_first_demo_fixture()
    assert {question.category for question in fixture.questions} == {
        "mmm_readiness",
        "geox_readiness",
        "grain_compatibility",
        "budget_planning_guardrail",
        "calibration_context",
        "data_missingness",
    }


def test_budget_guardrail_response_blocks_roi_and_recommendations() -> None:
    fixture = load_chat_first_demo_fixture()
    response = build_deterministic_demo_response(
        fixture, "budget_planning_guardrail_1"
    )
    blocked = {claim.lower() for claim in response.blocked_claims}
    assert {"channel roi", "roas", "budget shift recommendation"} <= blocked
    assert "future spend recommendation" in blocked
    assert response.human_review_required is True
    assert "RecommendationContract" in (response.next_required_artifact or "")


def test_geox_readiness_response_blocks_assignment_lift_and_readout() -> None:
    fixture = load_chat_first_demo_fixture()
    response = build_deterministic_demo_response(fixture, "geox_readiness_1")
    blocked = {claim.lower() for claim in response.blocked_claims}
    cannot_say = " ".join(response.cannot_say).lower()
    assert "treatment/control assignment" in blocked
    assert "geox lift" in blocked
    assert "treatment vs control" in cannot_say
    assert "lift" in cannot_say
    assert "GeoX readout" in fixture.forbidden_claims


def test_mmm_readiness_allows_readiness_and_blocks_fit_and_roi() -> None:
    fixture = load_chat_first_demo_fixture()
    response = build_deterministic_demo_response(fixture, "mmm_readiness_1")
    assert "readiness inspection" in response.allowed_answer_summary
    blocked = {claim.lower() for claim in response.blocked_claims}
    assert "mmm model fit result" in blocked
    assert {"channel roi", "roas"} <= blocked


def test_lifecycle_includes_available_blocked_and_future_dependencies() -> None:
    fixture = load_chat_first_demo_fixture()
    statuses = {step.status for step in fixture.lifecycle_steps}
    assert "available_now" in statuses
    assert "blocked" in statuses
    assert any(step.available_now for step in fixture.lifecycle_steps)
    assert any(step.blocked for step in fixture.lifecycle_steps)
    assert any(step.next_required_artifact for step in fixture.lifecycle_steps)


def test_unknown_question_is_rejected_without_free_form_generation() -> None:
    fixture = load_chat_first_demo_fixture()
    with pytest.raises(ValueError, match="unknown demo question_id"):
        build_deterministic_demo_response(fixture, "write_anything")


def test_helper_has_no_provider_model_or_optimizer_execution_surface() -> None:
    import mip.demo.chat_first_demo as module

    source = inspect.getsource(module).lower()
    forbidden_calls = (
        "provider.generate(",
        "provider.complete(",
        "fit_mmm(",
        "run_geox(",
        "optimize_budget(",
        "generate_recommendation(",
    )
    assert not any(call in source for call in forbidden_calls)


def test_canonical_streamlit_app_imports_with_chat_first_helper() -> None:
    import app.streamlit_app as streamlit_app

    assert callable(streamlit_app.main)
    assert callable(streamlit_app._render_chat_first_demo_tab)
