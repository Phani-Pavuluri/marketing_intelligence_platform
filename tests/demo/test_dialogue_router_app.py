from streamlit.testing.v1 import AppTest

# ruff: noqa: E501


def _transcript_markers(app: AppTest) -> list[str]:
    return [item.value for item in app.markdown if "conversation-transcript" in item.value]


def test_empty_transcript_container_is_absent_until_real_message() -> None:
    app = AppTest.from_file("app/streamlit_app.py").run()
    assert not app.exception
    assert len(app.chat_input) == 1
    assert _transcript_markers(app) == []

    next(button for button in app.button if button.label == "What data would I need to analyze channel performance?").click().run()
    assert _transcript_markers(app) == []

    next(button for button in app.button if button.label == "Explore SaaS growth-planning example").click().run()
    assert _transcript_markers(app) == []

    app = AppTest.from_file("app/streamlit_app.py").run()
    next(button for button in app.button if button.label == "Review readiness workspace scope").click().run()
    assert _transcript_markers(app) == []

    app = AppTest.from_file("app/streamlit_app.py").run()
    app.chat_input[0].set_value("what data do you need for MMM").run()
    assert not app.exception
    assert len(_transcript_markers(app)) == 1
    assert sum(message.name == "user" for message in app.chat_message) == 1
    assert sum(message.name == "assistant" for message in app.chat_message) == 2
    app.button[0].click().run()
    assert not app.exception
    assert _transcript_markers(app) == []
    assert len(app.chat_input) == 1
