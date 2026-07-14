# ruff: noqa: E501
"""Deterministic intent and bounded-conversation regressions."""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

from mip.demo.guided_workspace_intents import answer_shell_question, classify_shell_intent


def test_intent_router_recognizes_common_paraphrases() -> None:
    cases = {
        "test": "greeting_or_smoke_test",
        "what data do you need": "data_requirements",
        "what files should I upload": "analyze_my_data",
        "should I use MMM or an experiment": "mmm_vs_geox",
        "can I move budget next quarter": "planning",
        "how do I know what to trust": "trust_and_uncertainty",
        "show me an example": "sample_use_case",
        "can I upload my files": "analyze_my_data",
        "is Meta performing well": "dataset_specific_without_dataset",
    }

    for question, expected in cases.items():
        assert classify_shell_intent(question, has_active_dataset=False) == expected


def test_intent_router_handles_greeting_ambiguity_and_unsupported_questions() -> None:
    assert "I'm ready." in answer_shell_question("hello", has_active_dataset=False).answer.direct_answer
    ambiguous = answer_shell_question("What data do I need for MMM and GeoX?", has_active_dataset=False)
    assert ambiguous.intent == "ambiguous_measurement_question"
    assert "Are you asking" in ambiguous.answer.useful_detail
    unsupported = answer_shell_question("write a poem", has_active_dataset=False)
    assert unsupported.intent == "unsupported_question"
    assert "reframe" in unsupported.answer.useful_detail


def test_free_form_answers_are_relevant_plain_and_no_saas_before_selection() -> None:
    data = answer_shell_question("what data do you need", has_active_dataset=False).answer.render_text()
    planning = answer_shell_question("can I move budget", has_active_dataset=False).answer.render_text()
    trust = answer_shell_question("how confident is the result", has_active_dataset=False).answer.render_text()
    method = answer_shell_question("when should I use GeoX", has_active_dataset=False).answer.render_text()

    assert "marketing spend by channel" in data
    assert "does not run live optimization" in planning
    assert "data quality" in trust
    assert "several channels" in method
    assert len({data, planning, trust, method}) == 4
    forbidden = ("saas", "paid conversions", "search", "meta", "youtube", "dma", "fixture-backed")
    assert not any(term in "\n".join((data, planning, trust, method)).casefold() for term in forbidden)


def test_bounded_transcript_and_free_form_chat_render_without_duplicates() -> None:
    app = AppTest.from_file("app/streamlit_app.py").run()

    assert not app.exception
    assert len(app.chat_input) == 1
    app.chat_input[0].set_value("test").run()
    assert not app.exception
    assert len(app.chat_message) == 3
    assert any("I'm ready." in markdown.value for markdown in app.markdown)

    app.chat_input[0].set_value("what data do you need").run()
    assert not app.exception
    assert len(app.chat_message) == 5
    rendered = "\n".join(markdown.value for markdown in app.markdown)
    assert "marketing spend by channel" in rendered
    assert "measurement prerequisites" not in rendered.casefold()
