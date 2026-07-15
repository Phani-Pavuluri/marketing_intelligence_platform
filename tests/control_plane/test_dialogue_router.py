from datetime import UTC, datetime

# ruff: noqa: E501
import pytest

from mip.contracts.conversation import (
    DialogueResolutionStatus,
    DialogueState,
    EventType,
    InteractionEvent,
    WorkspaceContext,
)
from mip.control_plane import (
    DEFAULT_CAPABILITY_REGISTRY,
    DialogueRouter,
    RoutingResult,
    UnknownCapabilityError,
)


def route(
    text: str, *, context: WorkspaceContext | None = None, dialogue: DialogueState | None = None
) -> RoutingResult:
    context = context or WorkspaceContext(session_id="s", conversation_id="c", workspace_id="w", active_view="workspace_home")
    event = InteractionEvent(
        event_id="e1", session_id="s", conversation_id="c", workspace_id="w",
        event_type=EventType.USER_MESSAGE, timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        source_view="chat", source_component="input", payload={"text": text},
    )
    return DialogueRouter().route(event=event, workspace=context, dialogue=dialogue or DialogueState())


@pytest.mark.parametrize("text", [
    "What data do I need for MMM?",
    "What data is needed to build an MMM model?",
    "What files should I provide for marketing mix modeling?",
    "Which columns are required for MMM?",
])
def test_explicit_mmm_requirements_never_become_comparison(text: str) -> None:
    result = route(text)
    assert result.intent_envelope.candidate_capability_id == "mmm.intake.requirements"
    assert result.intent_envelope.domain == "mmm"
    assert not result.intent_envelope.clarification_required


def test_mmm_readiness_extracts_only_stated_slots() -> None:
    result = route("I have historical spend by channel and geo. Can this build an MMM?")
    assert result.intent_envelope.candidate_capability_id == "mmm.intake.readiness"
    assert set(result.known_input_updates) >= {"spend", "channel", "geography"}
    assert "primary_kpi" in result.missing_input_updates
    assert "time_frequency" in result.missing_input_updates


def test_pending_clarification_resolves_follow_up_and_correction() -> None:
    pending = DialogueState(
        pending_intent="assess_mmm_readiness", pending_capability_id="mmm.intake.readiness",
        selected_domain="mmm", missing_fields=["primary_kpi", "time_frequency", "history_start", "history_end"],
        clarification_targets=["primary_kpi", "time_frequency", "history_start", "history_end"],
        resolution_status=DialogueResolutionStatus.PENDING,
    )
    result = route("Paid conversions, weekly, January 2024 through June 2026.", dialogue=pending)
    assert result.intent_envelope.interpretation_source == "pending_clarification"
    assert result.confirmed_input_updates["primary_kpi"] == "paid_conversions"
    assert result.confirmed_input_updates["time_frequency"] == "weekly"
    assert result.updated_dialogue_state.resolution_status == DialogueResolutionStatus.RESOLVED.value
    corrected = route("Actually, the KPI is revenue.", dialogue=pending)
    assert corrected.confirmed_input_updates["primary_kpi"] == "revenue"


def test_contextual_uncertainty_requires_artifact_without_context() -> None:
    assert route("Why is this interval wide?").clarification_question
    context = WorkspaceContext(session_id="s", conversation_id="c", workspace_id="w", active_domain="mmm", active_artifact_id="mmm-result")
    result = route("Why is this interval wide?", context=context)
    assert result.intent_envelope.candidate_capability_id == "mmm.channel_uncertainty.explain"


def test_geox_planning_greeting_and_unsupported_routes() -> None:
    assert route("What data is needed for GeoX?").intent_envelope.candidate_capability_id == "geox.intake.requirements"
    assert route("Can you optimize next quarter?").intent_envelope.candidate_capability_id == "planning.simulation.request"
    assert route("hello").intent_envelope.candidate_capability_id == "platform.onboarding"
    unsupported = route("What is the weather tomorrow?")
    assert unsupported.intent_envelope.domain == "unknown"
    assert unsupported.selected_capability is None


def test_typed_ui_actions_win_and_unknown_capabilities_fail_closed() -> None:
    context = WorkspaceContext(session_id="s", conversation_id="c", workspace_id="w")
    event = InteractionEvent(
        event_id="e2", session_id="s", conversation_id="c", workspace_id="w",
        event_type=EventType.ANALYZE_MY_DATA_SELECTED, timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        source_view="chat", source_component="button", payload={"text": "What data is needed for MMM?"},
    )
    result = DialogueRouter().route(event=event, workspace=context, dialogue=DialogueState())
    assert result.intent_envelope.candidate_capability_id == "uploaded_data.intake"
    with pytest.raises(UnknownCapabilityError):
        DEFAULT_CAPABILITY_REGISTRY.get("not-registered")
