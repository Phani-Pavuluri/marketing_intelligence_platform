"""Deterministic in-memory workspace and event reduction."""
# ruff: noqa: E501, UP037
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from mip.contracts.conversation import (
    DialogueState,
    EntryMode,
    EventType,
    ExecutionMode,
    InteractionEvent,
    WorkspaceContext,
)


class WorkspaceTransitionError(ValueError):
    """Raised when an event cannot be applied to this workspace."""


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


class InMemoryWorkspace:
    """Append-only event log with a deterministic derived workspace context."""

    def __init__(
        self,
        *,
        session_id: str | None = None,
        conversation_id: str | None = None,
        workspace_id: str | None = None,
        timestamp_factory: Any = lambda: datetime.now(UTC),
    ) -> None:
        self.session_id = session_id or _id("session")
        self.conversation_id = conversation_id or _id("conversation")
        self.workspace_id = workspace_id or _id("workspace")
        self._timestamp_factory = timestamp_factory
        self._history: list[InteractionEvent] = []
        self._event_ids: set[str] = set()
        self._visible_start = 0
        self._context = WorkspaceContext(
            session_id=self.session_id,
            conversation_id=self.conversation_id,
            workspace_id=self.workspace_id,
            active_view="workspace_home",
        )
        self._dialogue = DialogueState()

    def events(self) -> tuple[InteractionEvent, ...]:
        return tuple(event.model_copy(deep=True) for event in self._history)

    def current_context(self) -> WorkspaceContext:
        return self._context.model_copy(deep=True)

    def dialogue_state(self) -> DialogueState:
        return self._dialogue.model_copy(deep=True)

    def visible_messages(self) -> tuple[InteractionEvent, ...]:
        visible = (EventType.USER_MESSAGE, EventType.ASSISTANT_RESPONSE)
        return tuple(event.model_copy(deep=True) for event in self._history[self._visible_start:] if event.event_type in visible)

    def append(self, event: InteractionEvent) -> WorkspaceContext:
        if event.workspace_id != self.workspace_id or event.conversation_id != self.conversation_id:
            raise WorkspaceTransitionError("event identity does not match workspace")
        if event.event_id in self._event_ids:
            raise WorkspaceTransitionError(f"duplicate event ID: {event.event_id}")
        if event.causation_id and event.causation_id not in self._event_ids:
            raise WorkspaceTransitionError("causation_id must reference an existing event")
        if self._history and event.timestamp < self._history[-1].timestamp:
            raise WorkspaceTransitionError("event timestamps must be ordered")
        self._event_ids.add(event.event_id)
        self._history.append(event.model_copy(deep=True))
        self._reduce(event)
        return self.current_context()

    def emit(
        self,
        event_type: EventType,
        *,
        source_view: str = "workspace",
        source_component: str = "workspace_runtime",
        payload: dict[str, Any] | None = None,
        requested_action: str | None = None,
        active_artifact_id: str | None = None,
        causation_id: str | None = None,
        event_id: str | None = None,
    ) -> WorkspaceContext:
        return self.append(
            InteractionEvent(
                event_id=event_id or _id("event"),
                session_id=self.session_id,
                conversation_id=self.conversation_id,
                workspace_id=self.workspace_id,
                event_type=event_type,
                timestamp=self._timestamp_factory(),
                source_view=source_view,
                source_component=source_component,
                requested_action=requested_action,
                payload=payload or {},
                active_artifact_id=active_artifact_id,
                causation_id=causation_id,
            )
        )

    def _reduce(self, event: InteractionEvent) -> None:
        payload = event.payload
        update: dict[str, Any] = {}
        if event.event_type == EventType.USER_MESSAGE:
            if not str(payload.get("text", "")).strip():
                raise WorkspaceTransitionError("user_message requires non-empty text")
        elif event.event_type == EventType.ASSISTANT_RESPONSE:
            if not str(payload.get("text", "")).strip():
                raise WorkspaceTransitionError("assistant_response requires non-empty text")
        elif event.event_type == EventType.STARTER_PROMPT_SELECTED:
            update["known_inputs"] = {**self._context.known_inputs, "active_starter_prompt_id": payload.get("starter_prompt_id")}
        elif event.event_type == EventType.SAMPLE_USE_CASE_SELECTED:
            sample_id = payload.get("dataset_id")
            use_case_id = payload.get("use_case_id")
            if not sample_id or not use_case_id:
                raise WorkspaceTransitionError("sample selection requires dataset_id and use_case_id")
            update.update(
                entry_mode=EntryMode.SAMPLE, active_dataset_id=sample_id, active_use_case_id=use_case_id,
                active_view=payload.get("active_view", "sample_use_case"), execution_mode=ExecutionMode.FIXTURE,
                available_artifact_ids=list(payload.get("available_artifact_ids", [])),
                uploaded_file_inventory=[], session_artifact_ids=[], claim_state="demo_only",
            )
        elif event.event_type == EventType.ANALYZE_MY_DATA_SELECTED:
            update.update(
                entry_mode=EntryMode.UPLOAD, active_dataset_id=None, active_use_case_id=None,
                active_view=payload.get("active_view", "upload_readiness"), execution_mode=ExecutionMode.UPLOADED_SESSION,
                available_artifact_ids=[], session_artifact_ids=[], claim_state="unverified",
            )
        elif event.event_type in {EventType.ARTIFACT_OPENED, EventType.REPORT_OPENED}:
            artifact_id = payload.get("artifact_id") or event.active_artifact_id
            if not artifact_id:
                raise WorkspaceTransitionError("artifact navigation requires artifact_id")
            update["active_artifact_id"] = artifact_id
            update["active_view"] = payload.get("active_view", "artifact")
        elif event.event_type == EventType.DASHBOARD_FILTER_CHANGED:
            update["active_view"] = payload.get("active_view", "dashboard")
            update["known_inputs"] = {**self._context.known_inputs, **payload.get("filters", {})}
        elif event.event_type == EventType.SYSTEM_RESULT and payload.get("action") == "clear_sample":
            update.update(entry_mode=EntryMode.EMPTY, active_dataset_id=None, active_use_case_id=None, active_view="workspace_home", active_artifact_id=None, active_workflow_node_id=None, available_artifact_ids=[], session_artifact_ids=[], execution_mode=None, claim_state="unverified")
        elif event.event_type == EventType.SYSTEM_RESULT and payload.get("action") == "enter_sample_mode":
            update.update(entry_mode=EntryMode.SAMPLE, active_view="sample_use_case")
        elif event.event_type == EventType.SYSTEM_RESULT and payload.get("action") == "routing_update":
            update["known_inputs"] = {**self._context.known_inputs, **payload.get("known_inputs", {})}
            update["missing_inputs"] = list(payload.get("missing_inputs", []))
        elif event.event_type == EventType.RESET_REQUESTED:
            self._visible_start = len(self._history)
            update = WorkspaceContext(
                session_id=self.session_id, conversation_id=self.conversation_id, workspace_id=self.workspace_id, active_view="workspace_home"
            ).model_dump()
            self._dialogue = DialogueState()
        if payload.get("dialogue_state") is not None:
            self._dialogue = DialogueState.model_validate(payload["dialogue_state"])
        if update:
            self._context = self._context.model_copy(update=update)
        messages = [event.payload.get("text", "") for event in self._history[self._visible_start:] if event.event_type in {EventType.USER_MESSAGE, EventType.ASSISTANT_RESPONSE}]
        self._context = self._context.model_copy(update={"recent_messages": messages[-20:]})

    def to_state(self) -> dict[str, Any]:
        return {"session_id": self.session_id, "conversation_id": self.conversation_id, "workspace_id": self.workspace_id, "events": [event.model_dump(mode="json") for event in self._history], "context": self._context.model_dump(mode="json"), "dialogue_state": self._dialogue.model_dump(mode="json")}

    @classmethod
    def from_state(cls, state: dict[str, Any], *, timestamp_factory: Any = lambda: datetime.now(UTC)) -> "InMemoryWorkspace":
        workspace = cls(session_id=state["session_id"], conversation_id=state["conversation_id"], workspace_id=state["workspace_id"], timestamp_factory=timestamp_factory)
        for raw in state.get("events", []):
            workspace.append(InteractionEvent.model_validate(raw))
        return workspace
