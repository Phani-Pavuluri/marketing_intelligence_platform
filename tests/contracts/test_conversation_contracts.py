from datetime import UTC, datetime
from typing import Any

# ruff: noqa: E501
import pytest
from pydantic import ValidationError

from mip.contracts.conversation import (
    CapabilityDescriptor,
    CapabilityStatus,
    DialogueResolutionStatus,
    DialogueState,
    EntryMode,
    EventType,
    EvidencePacket,
    ExecutionMode,
    IntentEnvelope,
    InteractionEvent,
    InterpretationSource,
    RequirementGap,
    ResolvedArtifact,
    ResponseContract,
    VerificationResult,
    VerificationStatus,
    WorkflowNode,
    WorkspaceContext,
)


def event() -> InteractionEvent:
    return InteractionEvent(
        event_id="evt-1",
        session_id="sess-1",
        conversation_id="conv-1",
        workspace_id="ws-1",
        event_type=EventType.USER_MESSAGE,
        timestamp=datetime(2026, 1, 1, tzinfo=UTC),
        source_view="chat",
        source_component="composer",
        payload={"text": "hello"},
    )


def workspace(mode: EntryMode = EntryMode.EMPTY) -> WorkspaceContext:
    return WorkspaceContext(
        session_id="sess-1", conversation_id="conv-1", workspace_id="ws-1", entry_mode=mode
    )


def intent(clarify: bool = False) -> IntentEnvelope:
    return IntentEnvelope(
        domain="mmm",
        user_goal="understand requirements",
        intent="mmm.intake.requirements",
        confidence=0.9,
        clarification_required=clarify,
        clarification_targets=["date_range"] if clarify else [],
        interpretation_source=InterpretationSource.DETERMINISTIC_RULE,
    )


def test_event_and_contract_round_trip_is_deterministic() -> None:
    original = event()
    assert InteractionEvent.model_validate_json(original.model_dump_json()) == original
    assert original.model_dump_json() == event().model_dump_json()
    assert original.timestamp.tzinfo is not None


def test_event_rejects_naive_timestamp_and_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        InteractionEvent.model_validate({"event_id": "x"})
    with pytest.raises(ValidationError):
        InteractionEvent.model_validate({**event().model_dump(), "timestamp": datetime(2026, 1, 1)})


def test_intent_confidence_and_clarification_invariants() -> None:
    assert intent().interpretation_source == InterpretationSource.DETERMINISTIC_RULE
    with pytest.raises(ValidationError):
        IntentEnvelope.model_validate({**intent().model_dump(), "confidence": 2})
    with pytest.raises(ValidationError):
        IntentEnvelope.model_validate(
            {**intent().model_dump(), "clarification_required": True, "clarification_targets": []}
        )


def test_workspace_empty_sample_upload_modes_have_no_default_dataset() -> None:
    assert workspace().active_dataset_id is None
    assert workspace(EntryMode.SAMPLE).entry_mode != workspace(EntryMode.UPLOAD).entry_mode
    changed_view = workspace().model_copy(update={"active_view": "dashboard"})
    assert changed_view.conversation_id == workspace().conversation_id


def test_dialogue_pending_resolution_and_cancellation() -> None:
    pending = DialogueState(
        original_question="Can I proceed?",
        resolution_status=DialogueResolutionStatus.PENDING,
        clarification_targets=["dataset"],
        missing_fields=["dataset"],
    )
    assert pending.resolution_status == DialogueResolutionStatus.PENDING
    assert DialogueState(resolution_status=DialogueResolutionStatus.CANCELLED).missing_fields == []
    with pytest.raises(ValidationError):
        DialogueState(resolution_status=DialogueResolutionStatus.PENDING)
    with pytest.raises(ValidationError):
        DialogueState(resolution_status=DialogueResolutionStatus.RESOLVED, missing_fields=["x"])


def test_requirement_gap_supports_complete_and_incomplete_states() -> None:
    complete = RequirementGap(
        capability_id="mmm.intake.requirements", next_allowed_actions=["continue"]
    )
    incomplete = RequirementGap(
        capability_id="mmm.intake.readiness",
        missing_required_inputs=["kpi"],
        blocked_actions=["fit"],
    )
    assert complete.missing_required_inputs == []
    assert "fit" in incomplete.blocked_actions


def test_capability_and_workflow_are_declarative() -> None:
    descriptor = CapabilityDescriptor(
        capability_id="planning.recommendation.explain_blocked",
        capability_version="1",
        owner="mip",
        domain="planning",
        status=CapabilityStatus.BLOCKED,
        supported_intents=["planning.recommendation.explain_blocked"],
        supported_event_types=[EventType.USER_MESSAGE],
        execution_modes=[ExecutionMode.FIXTURE],
        blocked_claims=["recommendation"],
    )
    node = WorkflowNode(
        node_id="define_decision",
        display_name="Define the decision",
        business_purpose="scope",
        supported_user_questions=["What decision are you making?"],
        required_capability_ids=[descriptor.capability_id],
        execution_mode=ExecutionMode.FIXTURE,
        blocked_actions=["fit"],
    )
    assert descriptor.status == CapabilityStatus.BLOCKED
    assert node.next_valid_node_ids == []


def test_artifacts_evidence_and_responses_preserve_claim_boundaries() -> None:
    artifact = ResolvedArtifact(
        artifact_id="fixture-1",
        artifact_type="dataset",
        source="fixture",
        execution_mode=ExecutionMode.FIXTURE,
        compatibility_status="compatible",
        claim_eligibility=["demo_only"],
        lineage=["fixture-source"],
    )
    packet = EvidencePacket(
        interaction_event=event(),
        intent=intent(),
        workspace_context=workspace(),
        dialogue_state=DialogueState(),
        requirement_gap=RequirementGap(capability_id="mmm.intake.requirements"),
        execution_status="not_executed",
        active_artifact=artifact,
        resolved_artifacts=[artifact],
    )
    response = ResponseContract(
        direct_answer="Need a KPI.", claim_status="limited", missing_inputs=["kpi"]
    )
    assert (
        packet.model_dump_json()
        == EvidencePacket.model_validate_json(packet.model_dump_json()).model_dump_json()
    )
    assert response.technical_details == []
    with pytest.raises(ValidationError):
        ResolvedArtifact.model_validate(
            {**artifact.model_dump(), "claim_eligibility": ["production evidence"]}
        )


@pytest.mark.parametrize(
    "status,payload",
    [
        (VerificationStatus.PASSED, {}),
        (VerificationStatus.BLOCKED, {"violations": ["unsupported claim"]}),
        (VerificationStatus.REWRITTEN, {"rewritten_fields": ["direct_answer"]}),
        (VerificationStatus.REQUIRES_CLARIFICATION, {"required_clarifications": ["kpi"]}),
        (VerificationStatus.REQUIRES_HUMAN_REVIEW, {"human_review_reason": "conflict"}),
    ],
)
def test_verification_status_requirements(
    status: VerificationStatus, payload: dict[str, Any]
) -> None:
    assert VerificationResult(status=status, **payload).status == status.value


def test_verification_rejects_impossible_states() -> None:
    with pytest.raises(ValidationError):
        VerificationResult(status=VerificationStatus.BLOCKED)
    with pytest.raises(ValidationError):
        VerificationResult(status=VerificationStatus.REQUIRES_HUMAN_REVIEW)
