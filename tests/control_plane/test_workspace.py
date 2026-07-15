from datetime import UTC, datetime, timedelta

# ruff: noqa: E501
import pytest

from mip.contracts.conversation import EntryMode, EventType
from mip.control_plane import InMemoryWorkspace, WorkspaceTransitionError


def workspace() -> InMemoryWorkspace:
    clock = iter(datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=i) for i in range(30))
    return InMemoryWorkspace(session_id="s1", conversation_id="c1", workspace_id="w1", timestamp_factory=lambda: next(clock))


def test_initial_identity_and_empty_context() -> None:
    current = workspace()
    context = current.current_context()
    assert (context.session_id, context.conversation_id, context.workspace_id) == ("s1", "c1", "w1")
    assert context.active_view == "workspace_home"
    assert context.active_dataset_id is None
    assert current.visible_messages() == ()


def test_messages_are_append_only_correlated_and_replayable() -> None:
    current = workspace()
    current.emit(EventType.USER_MESSAGE, payload={"text": "hello"}, source_view="chat", source_component="input")
    current.emit(EventType.ASSISTANT_RESPONSE, payload={"text": "hi"}, source_view="chat", source_component="answer", causation_id=current.events()[-1].event_id)
    assert [item.event_type for item in current.visible_messages()] == [EventType.USER_MESSAGE.value, EventType.ASSISTANT_RESPONSE.value]
    assert len(current.events()) == 2
    state = current.to_state()
    replayed = InMemoryWorkspace.from_state(state, timestamp_factory=lambda: datetime(2026, 1, 1, tzinfo=UTC))
    assert replayed.current_context() == current.current_context()
    with pytest.raises(WorkspaceTransitionError):
        current.append(current.events()[0])


def test_starter_is_not_a_chat_message_and_sample_preserves_identity() -> None:
    current = workspace()
    current.emit(EventType.USER_MESSAGE, payload={"text": "What data?"})
    current.emit(EventType.STARTER_PROMPT_SELECTED, payload={"starter_prompt_id": "requirements"})
    current.emit(EventType.SAMPLE_USE_CASE_SELECTED, payload={"dataset_id": "saas", "use_case_id": "growth", "available_artifact_ids": ["manifest"]})
    context = current.current_context()
    assert len(current.visible_messages()) == 1
    assert context.entry_mode == EntryMode.SAMPLE.value
    assert (context.active_dataset_id, context.active_use_case_id) == ("saas", "growth")
    assert context.conversation_id == "c1"


def test_upload_navigation_clear_sample_and_artifact_preserve_history() -> None:
    current = workspace()
    current.emit(EventType.USER_MESSAGE, payload={"text": "begin"})
    current.emit(EventType.SAMPLE_USE_CASE_SELECTED, payload={"dataset_id": "saas", "use_case_id": "growth"})
    current.emit(EventType.ANALYZE_MY_DATA_SELECTED)
    assert current.current_context().entry_mode == EntryMode.UPLOAD.value
    assert current.current_context().active_dataset_id is None
    current.emit(EventType.ARTIFACT_OPENED, payload={"artifact_id": "report-1", "active_view": "report"})
    assert current.current_context().active_artifact_id == "report-1"
    current.emit(EventType.SYSTEM_RESULT, payload={"action": "clear_sample"})
    assert current.current_context().active_view == "workspace_home"
    assert len(current.visible_messages()) == 1


def test_reset_clears_visible_and_derived_state_but_retains_history_and_identity() -> None:
    current = workspace()
    current.emit(EventType.USER_MESSAGE, payload={"text": "before"})
    current.emit(EventType.SAMPLE_USE_CASE_SELECTED, payload={"dataset_id": "saas", "use_case_id": "growth"})
    current.emit(EventType.RESET_REQUESTED)
    context = current.current_context()
    assert context.active_dataset_id is None
    assert context.active_use_case_id is None
    assert context.entry_mode == EntryMode.EMPTY.value
    assert current.visible_messages() == ()
    assert current.events()[-1].event_type == EventType.RESET_REQUESTED.value
    assert (context.workspace_id, context.conversation_id) == ("w1", "c1")


def test_identity_and_transition_fail_closed() -> None:
    current = workspace()
    current.emit(EventType.USER_MESSAGE, payload={"text": "ok"})
    original = current.events()[0]
    with pytest.raises(WorkspaceTransitionError):
        current.append(original.model_copy(update={"event_id": "other", "workspace_id": "wrong"}))
    with pytest.raises(WorkspaceTransitionError):
        current.emit(EventType.ARTIFACT_OPENED)
