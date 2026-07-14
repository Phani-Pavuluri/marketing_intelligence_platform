"""Render and key-uniqueness regressions for the chat-first Streamlit page."""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

from mip.demo.chat_first_demo import (
    build_chat_response_view,
    build_prompt_widget_key,
    follow_up_questions,
    load_chat_first_demo_fixture,
    sample_prompt_labels,
)


def test_prompt_widget_key_is_deterministic_and_namespaced() -> None:
    initial = build_prompt_widget_key(
        namespace="guided_prompt", question_id="data_missingness_1", position=1
    )

    assert initial == build_prompt_widget_key(
        namespace="guided_prompt", question_id="data_missingness_1", position=1
    )
    assert initial != build_prompt_widget_key(
        namespace="conversation_follow_up", question_id="data_missingness_1", position=1
    )
    assert initial != build_prompt_widget_key(
        namespace="guided_prompt", question_id="data_missingness_1", position=2
    )


def test_configured_prompt_and_follow_up_keys_are_unique() -> None:
    fixture = load_chat_first_demo_fixture()
    prompts = sample_prompt_labels(fixture)
    prompt_ids = [question_id for _, question_id in prompts]
    initial_keys = {
        build_prompt_widget_key(
            namespace="guided_prompt", question_id=question_id, position=position
        )
        for position, question_id in enumerate(prompt_ids)
    }
    follow_up_keys = {
        build_prompt_widget_key(
            namespace="conversation_follow_up",
            question_id=follow_up.question_id,
            position=(source_position * 100) + follow_up_position,
        )
        for source_position, question in enumerate(fixture.questions)
        for follow_up_position, follow_up in enumerate(
            follow_up_questions(fixture, build_chat_response_view(fixture, question.question))
        )
    }

    assert len(prompt_ids) > len(set(prompt_ids))
    assert len(initial_keys) == len(prompts)
    assert len(follow_up_keys) == sum(
        len(follow_up_questions(fixture, build_chat_response_view(fixture, question.question)))
        for question in fixture.questions
    )
    assert initial_keys.isdisjoint(follow_up_keys)


def test_canonical_streamlit_page_renders_and_chat_interactions_rerun() -> None:
    app = AppTest.from_file("app/streamlit_app.py").run()

    assert not app.exception
    assert len(app.chat_input) == 1
    assert len(app.button) == 7
    assert app.button[0].label == "Reset conversation"

    app.button[1].click().run()
    assert not app.exception
    assert len(app.chat_message) >= 2

    app.chat_input[0].set_value("Can I estimate ROI?").run()
    assert not app.exception

    app.button[0].click().run()
    assert not app.exception
    assert len(app.chat_input) == 1
