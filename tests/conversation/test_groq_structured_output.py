from __future__ import annotations

from collections.abc import Callable

import pytest
from pydantic import ValidationError

from mip.conversation.provider import GROQ_WIRE_INSTRUCTIONS, _sanitized_provider_error
from mip.conversation.provider_wire import (
    GroqConversationalProviderWireV2,
    ProviderWireSchemaError,
    map_groq_wire_to_internal,
)


def valid_wire(**overrides: object) -> dict[str, object]:
    wire: dict[str, object] = {
        "interaction_mode": "comparison",
        "answer": (
            "The right choice depends on the measurement objective and available causal evidence."
        ),
        "topic": "mmm_geox",
        "domain": "measurement",
        "user_goal": "compare_methods",
        "clarification_question": None,
        "proposed_capability_id": None,
        "proposed_workflow_node": None,
        "known_inputs": [],
        "inferred_inputs": [],
        "missing_inputs": [],
        "action_requested": False,
        "artifact_context_required": False,
    }
    wire.update(overrides)
    return wire


def test_groq_instruction_requires_complete_v3_shape_and_preserves_authority_boundaries() -> None:
    for field in GroqConversationalProviderWireV2.model_fields:
        assert field in GROQ_WIRE_INSTRUCTIONS
    assert "null, never omission" in GROQ_WIRE_INSTRUCTIONS
    assert "must always be arrays" in GROQ_WIRE_INSTRUCTIONS
    assert "use comparison for conditional MMM-versus-GeoX" in GROQ_WIRE_INSTRUCTIONS
    assert "non-authoritative proposals only" in GROQ_WIRE_INSTRUCTIONS
    assert "Do not request or emit retrieval-document IDs" in GROQ_WIRE_INSTRUCTIONS


def test_valid_conditional_comparison_parses_and_maps() -> None:
    parsed = GroqConversationalProviderWireV2.model_validate(valid_wire())
    mapped = map_groq_wire_to_internal(
        parsed.model_dump(), allowed_source_ids=set(), allowed_truth_ids=set()
    )
    assert mapped["interaction_mode"] == "general_explanation"
    assert str(mapped["answer"]).startswith("The right choice depends")


@pytest.mark.parametrize(
    "wire",
    [
        pytest.param(valid_wire(), id="baseline"),
    ],
)
def test_v3_baseline_is_strictly_valid(wire: dict[str, object]) -> None:
    assert GroqConversationalProviderWireV2.model_validate(wire).interaction_mode == "comparison"


@pytest.mark.parametrize(
    ("wire", "path", "error_type"),
    [
        (
            lambda: {key: value for key, value in valid_wire().items() if key != "answer"},
            "answer",
            "missing",
        ),
        (lambda: valid_wire(interaction_mode="recommend"), "interaction_mode", "literal_error"),
        (lambda: valid_wire(clarification_question=7), "clarification_question", "string_type"),
        (
            lambda: valid_wire(known_inputs=[{"name": "objective"}]),
            "known_inputs.0.value",
            "missing",
        ),
    ],
)
def test_invalid_v3_shapes_fail_with_typed_safe_diagnostics(
    wire: Callable[[], dict[str, object]], path: str, error_type: str
) -> None:
    with pytest.raises(ValidationError) as raised:
        GroqConversationalProviderWireV2.model_validate(wire())
    diagnostic = _sanitized_provider_error(raised.value, stage="full_wire_schema_parse")
    assert diagnostic.validation_field_path == path
    assert diagnostic.validation_error_type == error_type
    assert diagnostic.validation_error_count == 1


def test_multiple_validation_errors_are_counted_without_retaining_rejected_values() -> None:
    secret = "raw-rejected-value-must-never-appear"
    with pytest.raises(ValidationError) as raised:
        GroqConversationalProviderWireV2.model_validate(
            valid_wire(interaction_mode=secret, action_requested=None)
        )
    diagnostic = _sanitized_provider_error(raised.value, stage="full_wire_schema_parse")
    assert diagnostic.validation_error_count == 2
    assert secret not in diagnostic.__dict__.values()
    assert secret not in str(diagnostic)


@pytest.mark.parametrize(
    "proposal",
    [
        {"proposed_capability_id": "not_a_registered_capability"},
        {"proposed_workflow_node": "not_a_registered_workflow_node"},
    ],
)
def test_invalid_governance_proposals_fail_closed(proposal: dict[str, object]) -> None:
    with pytest.raises(ProviderWireSchemaError):
        map_groq_wire_to_internal(
            valid_wire(**proposal), allowed_source_ids=set(), allowed_truth_ids=set()
        )


@pytest.mark.parametrize(
    "answer",
    [
        "MIP recommends MMM for you.",
        "MIP executed MMM for you.",
        "This has the optimal budget allocation.",
        "Choose the treatment market now.",
    ],
)
def test_claim_guards_reject_unconditional_or_execution_guidance(answer: str) -> None:
    with pytest.raises(ProviderWireSchemaError):
        map_groq_wire_to_internal(
            valid_wire(answer=answer, action_requested=True),
            allowed_source_ids=set(),
            allowed_truth_ids=set(),
        )
