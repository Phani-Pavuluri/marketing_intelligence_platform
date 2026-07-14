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
class ChatResponseView:
    """User-facing, deterministic presentation of a governed demo response."""

    question: str
    supported: bool
    primary_answer: str
    readiness_label: str
    blocked_summary: str
    next_step: str
    evidence: tuple[str, ...]
    cannot_say: tuple[str, ...]
    blocked_claims: tuple[str, ...]
    technical_next_artifact: str | None
    follow_up_question_ids: tuple[str, ...]


SAMPLE_PROMPTS: tuple[tuple[str, str], ...] = (
    ("Is my data ready for MMM?", "mmm_readiness_1"),
    ("What can I conclude from the current data?", "data_missingness_1"),
    ("Can I estimate ROI or channel contribution?", "data_missingness_2"),
    ("Can I move budget between channels?", "budget_planning_guardrail_1"),
    ("Is this data ready for a GeoX test?", "geox_readiness_1"),
    ("What is the next measurement step?", "mmm_readiness_2"),
    ("How do MMM and GeoX work together?", "data_missingness_1"),
)

_FOLLOW_UPS_BY_QUESTION_ID: dict[str, tuple[str, ...]] = {
    "mmm_readiness_1": ("mmm_readiness_2", "geox_readiness_1", "data_missingness_2"),
    "mmm_readiness_2": ("mmm_readiness_1", "grain_compatibility_1", "calibration_context_1"),
    "geox_readiness_1": ("calibration_context_1", "data_missingness_2", "mmm_readiness_1"),
    "grain_compatibility_1": ("mmm_readiness_1", "mmm_readiness_2"),
    "budget_planning_guardrail_1": ("mmm_readiness_1", "data_missingness_2"),
    "calibration_context_1": ("mmm_readiness_1", "geox_readiness_1"),
    "data_missingness_1": ("mmm_readiness_1", "geox_readiness_1", "budget_planning_guardrail_1"),
    "data_missingness_2": ("mmm_readiness_1", "budget_planning_guardrail_1", "geox_readiness_1"),
}

_PRIMARY_ANSWERS: dict[str, tuple[str, str, str, str]] = {
    "mmm_readiness_1": (
        "Your data is structurally ready for an initial MMM assessment. "
        "Compatible spend, KPI, geography, time, and control fields are available.",
        "MMM readiness: available now",
        "A model has not been fitted, so ROI, contribution, and budget guidance remain blocked.",
        "Review the readiness evidence, then use a governed model workflow when available.",
    ),
    "mmm_readiness_2": (
        "The core fields needed to assess MMM readiness are present. What is still missing is "
        "a governed model output for decision-making.",
        "MMM readiness: evidence available",
        "The demo cannot turn raw data into ROI, contribution, or a spending decision.",
        "Start with the canonical panel and complete a governed model workflow.",
    ),
    "geox_readiness_1": (
        "Your data can be reviewed for GeoX design readiness. It includes a DMA-level panel, "
        "a KPI, spend context, and candidate pre/test periods.",
        "GeoX readiness: reviewable",
        "The demo cannot assign markets, promise power, or report lift.",
        "Review the design evidence with a measurement owner before creating an experiment design.",
    ),
    "grain_compatibility_1": (
        "Spend is recorded by week, DMA, and channel, while the KPI is recorded by week and DMA. "
        "They must be combined carefully so the KPI is counted once per market-week.",
        "Data compatibility: needs normalization",
        "The long spend table is not a ready-to-run model input by itself.",
        "Use the canonical wide panel for readiness review.",
    ),
    "budget_planning_guardrail_1": (
        "No. This demo can explain readiness, but it cannot recommend moving budget "
        "between channels.",
        "Recommendation readiness: blocked",
        "ROI, contribution, and optimized-spend claims require governed model results.",
        "Complete a governed model and recommendation review before considering a budget change.",
    ),
    "calibration_context_1": (
        "The calibration fixture provides context for a future measurement workflow. It does not "
        "calibrate a live model or support a performance claim.",
        "Calibration readiness: context only",
        "No live effect, ROI, lift, or recommendation can be inferred.",
        "Map calibration evidence to a governed model run when that workflow is available.",
    ),
    "data_missingness_1": (
        "You can assess readiness, data compatibility, and what evidence is still needed. "
        "The demo can also explain why measurement and recommendation claims are blocked.",
        "Evidence status: fixture-backed",
        "It cannot produce fitted causal, ROI, lift, or spending results.",
        "Choose a readiness or GeoX question to explore the next measurement step.",
    ),
    "data_missingness_2": (
        "This demo cannot provide ROI, ROAS, channel contribution, budget recommendations, "
        "model results, market assignment, or GeoX lift.",
        "Decision claims: blocked",
        "Those claims require governed model, experiment-design, or readout evidence.",
        "Start with a readiness assessment to see what evidence is available now.",
    ),
}


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


def classify_supported_question(
    fixture: ChatFirstDemoFixture,
    question: str,
) -> str | None:
    """Map a supported business question to a governed fixture question deterministically."""
    normalized = " ".join(question.casefold().split())
    for item in fixture.questions:
        if normalized == " ".join(item.question.casefold().split()):
            return item.question_id

    if any(term in normalized for term in ("roi", "roas", "contribution", "conclude")):
        if "roi" in normalized or "roas" in normalized:
            return "data_missingness_2"
        return "data_missingness_1"
    if any(term in normalized for term in ("budget", "spend", "move money", "channel")):
        return "budget_planning_guardrail_1"
    if "mmm and geox" in normalized or "mmm geox" in normalized:
        return "data_missingness_1"
    if any(term in normalized for term in ("geox", "geo experiment", "dma test", "market test")):
        return "geox_readiness_1"
    if any(term in normalized for term in ("grain", "compatible", "normalization")):
        return "grain_compatibility_1"
    if "calibration" in normalized:
        return "calibration_context_1"
    if any(term in normalized for term in ("mmm", "data ready", "readiness", "next measurement")):
        return "mmm_readiness_1"
    return None


def build_chat_response_view(
    fixture: ChatFirstDemoFixture,
    question: str,
) -> ChatResponseView:
    """Build a concise safe response plus technical details for the chat UI."""
    question_id = classify_supported_question(fixture, question)
    if question_id is None:
        return ChatResponseView(
            question=question,
            supported=False,
            primary_answer=(
                "This deterministic demo supports readiness, evidence, MMM, GeoX, and "
                "planning-boundary questions. Try one of the suggested prompts below."
            ),
            readiness_label="Question support: choose a guided prompt",
            blocked_summary="It does not invent answers outside its governed fixture coverage.",
            next_step="Choose a sample prompt about readiness, evidence, MMM, GeoX, or planning.",
            evidence=(),
            cannot_say=(),
            blocked_claims=fixture.forbidden_claims,
            technical_next_artifact=None,
            follow_up_question_ids=("mmm_readiness_1", "geox_readiness_1"),
        )

    response = build_deterministic_demo_response(fixture, question_id)
    primary, readiness, blocked, next_step = _PRIMARY_ANSWERS[question_id]
    return ChatResponseView(
        question=question,
        supported=True,
        primary_answer=primary,
        readiness_label=readiness,
        blocked_summary=blocked,
        next_step=next_step,
        evidence=response.required_evidence,
        cannot_say=response.cannot_say,
        blocked_claims=response.blocked_claims,
        technical_next_artifact=response.next_required_artifact,
        follow_up_question_ids=_FOLLOW_UPS_BY_QUESTION_ID[question_id],
    )


def sample_prompt_labels(fixture: ChatFirstDemoFixture) -> tuple[tuple[str, str], ...]:
    """Return display labels paired with the governed fixture questions they submit."""
    known_ids = {item.question_id for item in fixture.questions}
    return tuple(
        (label, question_id)
        for label, question_id in SAMPLE_PROMPTS
        if question_id in known_ids
    )


def follow_up_questions(
    fixture: ChatFirstDemoFixture,
    response: ChatResponseView,
) -> tuple[DemoQuestion, ...]:
    """Return governed follow-up questions without creating a new answer."""
    questions = {item.question_id: item for item in fixture.questions}
    return tuple(
        questions[question_id]
        for question_id in response.follow_up_question_ids
        if question_id in questions
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
