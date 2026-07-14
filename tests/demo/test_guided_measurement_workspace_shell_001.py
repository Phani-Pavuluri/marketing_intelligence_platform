"""P1 regressions for the guided measurement workspace shell."""

from __future__ import annotations

from streamlit.testing.v1 import AppTest

from mip.demo.guided_workspace_shell import (
    CANONICAL_HERO,
    STARTER_PROMPTS,
    UPLOAD_INFORMATION_COPY,
    WELCOME_COPY,
    preselection_answer,
    starter_answer,
)
from mip.demo.product_flow import (
    initial_product_state,
    select_dataset,
    select_sample_mode,
    select_upload_information,
)
from mip.demo.sample_journey import load_sample_journey


def test_starter_answers_are_distinct_substantive_and_safe() -> None:
    answers = [starter_answer(prompt) for prompt in STARTER_PROMPTS]

    assert all(answer is not None for answer in answers)
    rendered = [answer.render_text() for answer in answers if answer is not None]
    assert len(rendered) == 4
    assert len(set(rendered)) == 4
    assert "channels appear to be driving results" in rendered[0]
    assert "marketing spend by channel" in rendered[1]
    assert "does not directly design the experiment" in rendered[2]
    assert "does not run live optimization" in rendered[3]
    forbidden = ("saas subscriptions", "paid conversions", "search, meta", "weekly × dma")
    assert not any(term in "\n".join(rendered).casefold() for term in forbidden)
    assert not any(term in WELCOME_COPY.casefold() for term in forbidden)
    assert not any(term in UPLOAD_INFORMATION_COPY.casefold() for term in forbidden)


def test_entry_modes_are_explicit_and_resettable() -> None:
    bundle = load_sample_journey("saas_subscriptions_demo_v1")
    state = initial_product_state()

    assert state["entry_mode"] is None
    assert state["active_dataset_id"] is None
    assert state["active_starter_prompt_id"] is None
    select_sample_mode(state)
    assert state["entry_mode"] == "sample_use_case"
    assert state["active_dataset_id"] is None
    select_upload_information(state)
    assert state["entry_mode"] == "upload_readiness_information"
    assert state["active_dataset_id"] is None
    select_dataset(state, bundle)
    assert state["entry_mode"] == "sample_use_case"
    assert state["active_use_case_id"] == "saas_growth_planning"
    assert initial_product_state()["entry_mode"] is None


def test_preselection_answer_blocks_dataset_specific_claims() -> None:
    answer = preselection_answer("Is this dataset ready and is Meta uncertain?")

    assert "cannot make dataset-specific" in answer.important_limitation
    assert "Select a sample measurement story" in answer.next_action


def test_guided_shell_renders_and_entry_modes_remain_honest() -> None:
    app = AppTest.from_file("app/streamlit_app.py").run()

    assert not app.exception
    rendered = "\n".join(markdown.value for markdown in app.markdown)
    assert CANONICAL_HERO in "\n".join(title.value for title in app.title)
    assert "Understand channel performance" in rendered
    assert {"Measure", "Plan", "Experiment", "Learn"} <= {
        markdown.value.replace("**", "") for markdown in app.markdown
    }
    labels = {button.label for button in app.button}
    assert set(STARTER_PROMPTS) <= labels
    assert "Explore SaaS growth-planning example" in labels
    assert "Review readiness workspace scope" in labels
    assert "Choose a sample journey stage" not in rendered
    assert "Start with a question" not in rendered

    buttons = list(app.button)
    next(button for button in buttons if button.label == STARTER_PROMPTS[0]).click().run()
    assert not app.exception
    assert len(app.chat_message) == 1
    first_answer = "\n".join(info.value for info in app.info)
    assert "channels appear to be driving results" in first_answer

    next(button for button in app.button if button.label == STARTER_PROMPTS[1]).click().run()
    assert not app.exception
    second_answer = "\n".join(info.value for info in app.info)
    assert "marketing spend by channel" in second_answer
    assert "channels appear to be driving results" not in second_answer
    assert len(app.chat_message) == 1

    next(
        button for button in app.button if button.label == "Review readiness workspace scope"
    ).click().run()
    assert not app.exception
    assert any("planned, not implemented" in info.value for info in app.info)

    sample_app = AppTest.from_file("app/streamlit_app.py").run()
    next(
        button
        for button in sample_app.button
        if button.label == "Explore SaaS growth-planning example"
    ).click().run()
    assert not sample_app.exception
    assert any(
        button.label == "Activate SaaS growth-planning example" for button in sample_app.button
    )

    next(
        button
        for button in sample_app.button
        if button.label == "Activate SaaS growth-planning example"
    ).click().run()
    assert not sample_app.exception
    rendered_after = "\n".join(markdown.value for markdown in sample_app.markdown)
    assert "Active demo dataset: SaaS subscriptions" in rendered_after
    assert "Select the sample dataset" not in rendered_after
