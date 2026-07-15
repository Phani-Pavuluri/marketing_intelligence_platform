"""Thin compatibility adapter for Streamlit session state."""
# ruff: noqa: E501
from __future__ import annotations

from typing import Any

from mip.control_plane.workspace import InMemoryWorkspace

WORKSPACE_KEY = "control_plane_workspace"


def get_workspace(session_state: Any) -> InMemoryWorkspace:
    workspace = session_state.get(WORKSPACE_KEY)
    if not isinstance(workspace, InMemoryWorkspace):
        workspace = InMemoryWorkspace()
        session_state[WORKSPACE_KEY] = workspace
    return workspace


def sync_legacy_aliases(session_state: Any, workspace: InMemoryWorkspace) -> dict[str, Any]:
    """Derive legacy product-flow fields; legacy values never override canonical state."""
    context = workspace.current_context()
    aliases = {
        "entry_mode": (
            "sample_use_case" if context.entry_mode == "sample"
            else "upload_readiness_information" if context.entry_mode == "upload"
            else None
        ),
        "active_dataset_id": context.active_dataset_id,
        "active_use_case_id": context.active_use_case_id,
        "active_view": context.active_view,
        "active_artifact_id": context.active_artifact_id,
        "conversation_messages": [
            {"role": "user" if event.event_type == "user_message" else "assistant", "content": event.payload.get("text", "")}
            for event in workspace.visible_messages()
        ],
    }
    for key, value in aliases.items():
        session_state[key] = value
    return aliases
