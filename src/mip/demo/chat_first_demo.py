"""Deterministic loader and answer builder for the chat-first SaaS demo.

This module reads static fixture metadata only. It does not import or execute
LLM providers, prompts, MMM/GeoX engines, optimizers, or recommendation logic.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_FIXTURE_DIR = Path(__file__).resolve().parents[3] / (
    "data/demo/domain_fixtures/saas_subscriptions/v1"
)

_REQUIRED_JSON_FILES = (
    "manifest.json",
    "sample_questions.json",
    "expected_answer_behavior.json",
    "lifecycle_walkthrough.json",
)


@dataclass(frozen=True)
class DemoQuestion:
    """One fixture-backed sample question."""

    question_id: str
    category: str
    question: str


@dataclass(frozen=True)
class DeterministicDemoResponse:
    """Expected response behavior copied from fixture metadata."""

    question_id: str
    category: str
    question: str
    allowed_answer_summary: str
    required_evidence: tuple[str, ...]
    cannot_say: tuple[str, ...]
    blocked_claims: tuple[str, ...]
    next_required_artifact: str | None
    human_review_required: bool


@dataclass(frozen=True)
class DemoLifecycleStep:
    """One lifecycle row for deterministic display."""

    step_id: str
    title: str
    status: str
    available_now: bool
    fixture_backed: bool
    blocked: bool
    next_required_artifact: str | None


@dataclass(frozen=True)
class ChatFirstDemoFixture:
    """Parsed and cross-referenced chat-first demo fixture."""

    fixture_dir: Path
    fixture_id: str
    allowed_claims: tuple[str, ...]
    forbidden_claims: tuple[str, ...]
    questions: tuple[DemoQuestion, ...]
    behaviors_by_question_id: dict[str, dict[str, Any]]
    lifecycle_steps: tuple[DemoLifecycleStep, ...]
    inspected_files: tuple[str, ...]


def load_chat_first_demo_fixture(
    fixture_dir: Path = DEFAULT_FIXTURE_DIR,
) -> ChatFirstDemoFixture:
    """Load and cross-reference the four governed JSON fixture files."""

    payloads = {
        filename: _read_json_object(fixture_dir / filename)
        for filename in _REQUIRED_JSON_FILES
    }
    manifest = payloads["manifest.json"]
    questions_payload = _require_list(payloads["sample_questions.json"], "questions")
    behaviors_payload = _require_list(
        payloads["expected_answer_behavior.json"], "behaviors"
    )
    lifecycle_payload = _require_list(
        payloads["lifecycle_walkthrough.json"], "steps"
    )

    questions = tuple(_parse_question(item) for item in questions_payload)
    behaviors = {_required_text(item, "question_id"): item for item in behaviors_payload}
    if len(behaviors) != len(behaviors_payload):
        raise ValueError("expected answer behaviors must have unique question_id values")
    missing_behaviors = [
        question.question_id
        for question in questions
        if question.question_id not in behaviors
    ]
    if missing_behaviors:
        raise ValueError(f"sample questions missing expected behavior: {missing_behaviors}")

    lifecycle_steps = tuple(_parse_lifecycle_step(item) for item in lifecycle_payload)
    return ChatFirstDemoFixture(
        fixture_dir=fixture_dir,
        fixture_id=_required_text(manifest, "fixture_id"),
        allowed_claims=_string_tuple(manifest.get("allowed_claims")),
        forbidden_claims=_string_tuple(manifest.get("forbidden_claims")),
        questions=questions,
        behaviors_by_question_id=behaviors,
        lifecycle_steps=lifecycle_steps,
        inspected_files=_REQUIRED_JSON_FILES,
    )


def build_deterministic_demo_response(
    fixture: ChatFirstDemoFixture,
    question_id: str,
) -> DeterministicDemoResponse:
    """Build a display response exclusively from expected behavior metadata."""

    question = next(
        (item for item in fixture.questions if item.question_id == question_id),
        None,
    )
    if question is None:
        raise ValueError(f"unknown demo question_id: {question_id}")
    behavior = fixture.behaviors_by_question_id[question_id]
    behavior_question = _required_text(behavior, "question")
    if behavior_question != question.question:
        raise ValueError(f"question text mismatch for {question_id}")
    next_artifact = behavior.get("next_required_artifact")
    if next_artifact is not None and not isinstance(next_artifact, str):
        raise ValueError(f"next_required_artifact must be text or null for {question_id}")
    human_review = behavior.get("human_review_required")
    if not isinstance(human_review, bool):
        raise ValueError(f"human_review_required must be boolean for {question_id}")

    return DeterministicDemoResponse(
        question_id=question.question_id,
        category=question.category,
        question=question.question,
        allowed_answer_summary=_required_text(behavior, "allowed_answer_summary"),
        required_evidence=_string_tuple(behavior.get("required_evidence")),
        cannot_say=_string_tuple(behavior.get("cannot_say")),
        blocked_claims=_string_tuple(behavior.get("blocked_claims")),
        next_required_artifact=next_artifact,
        human_review_required=human_review,
    )


def _read_json_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"required demo fixture file missing: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid demo fixture JSON: {path.name}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"demo fixture JSON must be an object: {path.name}")
    return value


def _require_list(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    value = payload.get(key)
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise ValueError(f"{key} must be a list of objects")
    return value


def _required_text(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be non-empty text")
    return value


def _string_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item.strip() for item in value
    ):
        raise ValueError("expected a list of non-empty strings")
    return tuple(value)


def _parse_question(payload: dict[str, Any]) -> DemoQuestion:
    return DemoQuestion(
        question_id=_required_text(payload, "question_id"),
        category=_required_text(payload, "category"),
        question=_required_text(payload, "question"),
    )


def _parse_lifecycle_step(payload: dict[str, Any]) -> DemoLifecycleStep:
    boolean_fields = ("available_now", "fixture_backed", "blocked")
    for field in boolean_fields:
        if not isinstance(payload.get(field), bool):
            raise ValueError(f"lifecycle {field} must be boolean")
    next_artifact = payload.get("next_required_artifact")
    if next_artifact is not None and not isinstance(next_artifact, str):
        raise ValueError("lifecycle next_required_artifact must be text or null")
    return DemoLifecycleStep(
        step_id=_required_text(payload, "step_id"),
        title=_required_text(payload, "title"),
        status=_required_text(payload, "status"),
        available_now=payload["available_now"],
        fixture_backed=payload["fixture_backed"],
        blocked=payload["blocked"],
        next_required_artifact=next_artifact,
    )
