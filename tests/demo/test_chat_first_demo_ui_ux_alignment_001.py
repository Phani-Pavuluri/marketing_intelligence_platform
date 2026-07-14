"""Behavior checks for the chat-first measurement-copilot presentation."""

from __future__ import annotations

from mip.demo.chat_first_demo import (
    build_chat_response_view,
    classify_supported_question,
    follow_up_questions,
    load_chat_first_demo_fixture,
    sample_prompt_labels,
)


def test_sample_prompts_cover_measurement_copilot_categories() -> None:
    fixture = load_chat_first_demo_fixture()
    labels = {label for label, _ in sample_prompt_labels(fixture)}

    assert "Is my data ready for MMM?" in labels
    assert "Can I estimate ROI or channel contribution?" in labels
    assert "Is this data ready for a GeoX test?" in labels
    assert "How do MMM and GeoX work together?" in labels


def test_typed_supported_questions_classify_deterministically() -> None:
    fixture = load_chat_first_demo_fixture()

    assert classify_supported_question(fixture, "Is my data ready for MMM?") == "mmm_readiness_1"
    assert classify_supported_question(fixture, "Can I estimate ROI?") == "data_missingness_2"
    assert (
        classify_supported_question(fixture, "Is this ready for a GeoX test?")
        == "geox_readiness_1"
    )


def test_unsupported_question_fails_safely_without_inventing_an_answer() -> None:
    fixture = load_chat_first_demo_fixture()
    response = build_chat_response_view(fixture, "Which campaign will win next quarter?")

    assert response.supported is False
    assert "supports readiness" in response.primary_answer
    assert "roi" in " ".join(response.blocked_claims).lower()


def test_primary_response_is_user_facing_and_keeps_internal_terms_in_details() -> None:
    fixture = load_chat_first_demo_fixture()
    response = build_chat_response_view(fixture, "Is my data ready for MMM?")
    primary = response.primary_answer.lower()

    assert response.supported is True
    assert len(response.primary_answer) < 260
    assert "mmexportbundle" not in primary
    assert "recommendationcontract" not in primary
    assert "artifact" not in primary
    assert response.evidence
    assert response.blocked_claims
    assert response.technical_next_artifact


def test_follow_ups_are_governed_fixture_questions() -> None:
    fixture = load_chat_first_demo_fixture()
    response = build_chat_response_view(fixture, "Can I move budget between channels?")
    follow_ups = follow_up_questions(fixture, response)

    assert follow_ups
    assert {item.question_id for item in follow_ups} <= {
        item.question_id for item in fixture.questions
    }
