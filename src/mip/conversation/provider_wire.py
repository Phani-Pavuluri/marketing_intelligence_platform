"""Strict Groq-facing conversational wire schema and deterministic normalization."""

from __future__ import annotations

import json
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from mip.contracts.conversation import InteractionMode
from mip.control_plane.capability_registry import DEFAULT_CAPABILITY_REGISTRY
from mip.control_plane.workflow_graph import DEFAULT_WORKFLOW_GRAPH

GROQ_WIRE_SCHEMA_VERSION = "conversational_provider_wire_v2"
GROQ_WIRE_SCHEMA_MAX_BYTES = 8_000


class ProviderWireSchemaError(ValueError):
    pass


class InputItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=128)
    value: str | None


class GroqConversationalProviderWireV2(BaseModel):
    """Small closed schema: optionality is nullable, never omission."""

    model_config = ConfigDict(extra="forbid")
    interaction_mode: Literal[
        "general_explanation",
        "platform_guidance",
        "artifact_interpretation",
        "governed_action",
        "typed_ui_action",
        "unsupported",
    ]
    answer: str = Field(min_length=1, max_length=4_000)
    topic: str = Field(min_length=1, max_length=128)
    domain: str = Field(min_length=1, max_length=128)
    user_goal: str = Field(min_length=1, max_length=128)
    clarification_question: str | None
    retrieval_document_ids: list[str] = Field(max_length=10)
    platform_truth_reference_ids: list[str] = Field(max_length=20)
    proposed_capability_id: str | None
    proposed_workflow_node: str | None
    known_inputs: list[InputItem] = Field(max_length=20)
    inferred_inputs: list[InputItem] = Field(max_length=20)
    missing_inputs: list[str] = Field(max_length=20)
    action_requested: bool
    artifact_context_required: bool


def groq_wire_schema() -> dict[str, object]:
    return GroqConversationalProviderWireV2.model_json_schema()


def lint_groq_wire_schema(schema: dict[str, object]) -> None:
    """Fail before transport when the restricted provider-wire schema drifts."""
    encoded = json.dumps(schema, sort_keys=True)
    if len(encoded) > GROQ_WIRE_SCHEMA_MAX_BYTES:
        raise ProviderWireSchemaError("schema_size_limit")
    forbidden = {
        "patternProperties",
        "unevaluatedProperties",
        "dependentRequired",
        "if",
        "then",
        "else",
        "additionalItems",
    }

    def walk(node: object) -> None:
        if isinstance(node, dict):
            if forbidden.intersection(node):
                raise ProviderWireSchemaError("unsupported_schema_keyword")
            if node.get("type") == "object" or "properties" in node:
                if node.get("additionalProperties") is not False:
                    raise ProviderWireSchemaError("open_object")
                if set(node.get("properties", ())) != set(node.get("required", ())):
                    raise ProviderWireSchemaError("missing_required_property")
            if node.get("type") == "object" and isinstance(node.get("additionalProperties"), dict):
                raise ProviderWireSchemaError("arbitrary_dictionary")
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(schema)


def map_groq_wire_to_internal(
    raw: dict[str, object], *, allowed_source_ids: set[str], allowed_truth_ids: set[str]
) -> dict[str, object]:
    wire = GroqConversationalProviderWireV2.model_validate(raw)
    try:
        mode = InteractionMode(wire.interaction_mode)
    except ValueError as exc:
        raise ProviderWireSchemaError("unknown_interaction_mode") from exc
    if wire.proposed_capability_id is not None:
        try:
            DEFAULT_CAPABILITY_REGISTRY.get(wire.proposed_capability_id)
        except LookupError as exc:
            raise ProviderWireSchemaError("unknown_capability") from exc
    if wire.proposed_workflow_node is not None:
        try:
            DEFAULT_WORKFLOW_GRAPH.get_node(wire.proposed_workflow_node)
        except LookupError as exc:
            raise ProviderWireSchemaError("unknown_workflow_node") from exc
    if not set(wire.retrieval_document_ids).issubset(allowed_source_ids):
        raise ProviderWireSchemaError("unknown_source_document")
    if not set(wire.platform_truth_reference_ids).issubset(allowed_truth_ids):
        raise ProviderWireSchemaError("unknown_platform_truth_reference")
    if wire.artifact_context_required or mode == InteractionMode.ARTIFACT_INTERPRETATION:
        raise ProviderWireSchemaError("artifact_context_unresolved")
    answer = wire.answer.casefold()
    if wire.action_requested and re.search(
        r"\b(i|we|mip)\s+(fit|ran|executed|completed)\b", answer
    ):
        raise ProviderWireSchemaError("execution_claim")
    if "recommend" in answer or "optimal budget" in answer or "treatment market" in answer:
        raise ProviderWireSchemaError("prohibited_claim")
    return {
        "interaction_mode": mode.value,
        "topic": wire.topic,
        "domain": wire.domain,
        "user_goal": wire.user_goal,
        "answer": wire.answer,
        "requires_platform_truth": mode == InteractionMode.PLATFORM_GUIDANCE,
        "requires_retrieval": bool(wire.retrieval_document_ids),
        "requires_artifact": False,
        "requires_execution": False,
        "candidate_capability_id": wire.proposed_capability_id,
        "requested_workflow_node_id": wire.proposed_workflow_node,
        "known_inputs": {item.name: item.value for item in wire.known_inputs},
        "inferred_inputs": {item.name: item.value for item in wire.inferred_inputs},
        "missing_inputs": wire.missing_inputs,
        "clarification_required": wire.clarification_question is not None,
        "clarification_targets": [wire.clarification_question]
        if wire.clarification_question
        else [],
        "source_document_ids": wire.retrieval_document_ids,
        "platform_truth_reference_ids": wire.platform_truth_reference_ids,
    }
