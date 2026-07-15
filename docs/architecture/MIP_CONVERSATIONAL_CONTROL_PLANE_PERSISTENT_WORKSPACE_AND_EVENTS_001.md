# Conversational Control Plane Persistent Workspace and Events 001

Phase C adds a deterministic in-memory workspace runtime at `src/mip/control_plane/workspace.py` and a thin Streamlit adapter at `streamlit_workspace.py`. One stable session, conversation, and workspace identity is created per in-process Streamlit session. The append-only typed event log is the canonical source; `WorkspaceContext`, `DialogueState`, and visible messages are derived from it. State can serialize and replay deterministically, and event access is defensive.

Supported transitions include user/assistant messages, starter selections, sample activation, Analyze-my-data, artifact/report/dashboard navigation, clear-sample, and explicit reset. Sample and upload paths preserve conversation identity; sample activation is fixture-backed and never jumps directly to planning; Analyze-my-data clears incompatible sample state without processing files. Navigation preserves chat and context. Clear-sample preserves visible conversation. Reset retains the same workspace and conversation identities, retains the reset and prior audit history internally, and moves the visible transcript and derived context to the valid initial state.

The Streamlit adapter derives legacy aliases from the canonical workspace so stale legacy values cannot override it. Existing bounded transcript, single composer, starter behavior, sample flow, upload-information path, and Advanced tools remain intact. Core reducer code has no Streamlit, provider, optional-engine, routing, workflow, upload, RAG, or LLM dependency.

Legacy fields are compatibility aliases: `conversation_messages`, `entry_mode`, `active_dataset_id`, `active_use_case_id`, `active_view`, and `active_artifact_id`. They can be removed after downstream renderers consume the canonical workspace directly.

Browser checkpoint: interactive browser review was unavailable in this agent environment and remains pending user verification; AppTest and Docker/public deployment checks passed.

Next artifact: `MIP_CONVERSATIONAL_CONTROL_PLANE_DIALOGUE_ROUTER_001`.
