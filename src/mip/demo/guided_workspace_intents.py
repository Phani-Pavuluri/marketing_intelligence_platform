# ruff: noqa: E501
"""Small deterministic free-form router for guided workspace shell questions."""

from __future__ import annotations

from dataclasses import dataclass

from mip.demo.guided_workspace_shell import STARTER_PROMPTS, ShellAnswer, starter_answer


@dataclass(frozen=True)
class ShellIntentResponse:
    """A classified shell answer suitable for the current session context."""

    intent: str
    answer: ShellAnswer


def classify_shell_intent(question: str, *, has_active_dataset: bool) -> str:
    """Classify common shell questions with stable, ordered keyword rules."""

    normalized = " ".join(question.casefold().split())
    if normalized in {"test", "hello", "hi", "hey", "are you working"}:
        return "greeting_or_smoke_test"
    if not has_active_dataset and any(
        term in normalized for term in ("meta", "search", "youtube", "this dataset", "my data")
    ):
        return "dataset_specific_without_dataset"
    if any(term in normalized for term in ("upload", "my files", "analyze my data")):
        return "analyze_my_data"
    if any(term in normalized for term in ("show me an example", "sample use case", "sample story")):
        return "sample_use_case"
    if ("data" in normalized or "files" in normalized or "columns" in normalized) and any(
        term in normalized for term in ("geox", "experiment", "mmm")
    ):
        return "ambiguous_measurement_question"
    if any(term in normalized for term in ("mmm", "geox", "experiment", "causal")):
        return "mmm_vs_geox"
    if any(term in normalized for term in ("budget", "plan", "next quarter", "spend change")):
        return "planning"
    if any(term in normalized for term in ("trust", "confident", "confidence", "uncertain", "uncertainty")):
        return "trust_and_uncertainty"
    if any(term in normalized for term in ("data", "file", "column", "input", "provide")):
        return "data_requirements"
    if any(term in normalized for term in ("what can", "help", "platform do", "capabilities")):
        return "platform_capabilities"
    if len(normalized.split()) <= 2:
        return "unsupported_question"
    return "unsupported_question"


def answer_shell_question(question: str, *, has_active_dataset: bool) -> ShellIntentResponse:
    """Construct a relevant, provider-free answer for a classified shell intent."""

    intent = classify_shell_intent(question, has_active_dataset=has_active_dataset)
    starter_by_intent = {
        "platform_capabilities": STARTER_PROMPTS[0],
        "data_requirements": STARTER_PROMPTS[1],
        "mmm_vs_geox": STARTER_PROMPTS[2],
        "planning": STARTER_PROMPTS[3],
    }
    starter_prompt = starter_by_intent.get(intent)
    if starter_prompt is not None:
        answer = starter_answer(starter_prompt)
        assert answer is not None
        return ShellIntentResponse(intent, answer)
    answers = {
        "greeting_or_smoke_test": ShellAnswer(
            "I'm ready.",
            "Ask about channel performance, required data, MMM, GeoX experiments, or future-budget planning.",
            "I do not run models or make budget changes in this demo.",
            "Choose a starter question or type a marketing-measurement question.",
            STARTER_PROMPTS[:2],
            intent,
        ),
        "trust_and_uncertainty": ShellAnswer(
            "MIP should show how much confidence to place in an answer, not just the answer itself.",
            "It checks data quality, model validation, uncertainty, whether spend levels are familiar or outside prior experience, whether experiment evidence agrees with the model, and whether planning evidence exists.",
            "When evidence is weak or incomplete, MIP should say so rather than produce a confident recommendation.",
            "Ask what data is needed or whether MMM, GeoX, or both fit your question.",
            (STARTER_PROMPTS[1], STARTER_PROMPTS[2]),
            intent,
        ),
        "sample_use_case": ShellAnswer(
            "A sample measurement story lets you explore the workflow without using your own data.",
            "It shows how MIP moves from a business question to evidence, uncertainty, planning readiness, and a possible experiment need.",
            "The sample is deterministic and does not represent a live analysis.",
            "Choose Explore a sample use case below.",
            (STARTER_PROMPTS[0], STARTER_PROMPTS[3]),
            intent,
        ),
        "analyze_my_data": ShellAnswer(
            "The planned readiness workspace will help organize the data needed for analysis.",
            "It is intended to review channel spend, outcomes, controls, optional experiment results, columns, and data grain before any model work.",
            "File upload and live analysis are not implemented in this demo.",
            "Choose Analyze my data below to review the planned scope.",
            (STARTER_PROMPTS[1],),
            intent,
        ),
        "dataset_specific_without_dataset": ShellAnswer(
            "I need an explicit dataset before making channel- or result-specific claims.",
            "Select the sample measurement story to explore a concrete dataset, or choose Analyze my data to review what would be required for your own analysis.",
            "Without that context, I cannot say how a channel or dataset is performing.",
            "Choose one of the two entry paths below.",
            (STARTER_PROMPTS[1], STARTER_PROMPTS[2]),
            intent,
        ),
        "ambiguous_measurement_question": ShellAnswer(
            "I can help, but I need to narrow the question first.",
            "Are you asking about the data needed for MMM, the data needed for a GeoX experiment, or both?",
            "The answer depends on whether you need broad channel measurement or a focused causal test.",
            "Tell me which measurement question matters most.",
            (STARTER_PROMPTS[1], STARTER_PROMPTS[2]),
            intent,
        ),
        "unsupported_question": ShellAnswer(
            "I can help with marketing measurement, channel data, MMM, GeoX experiments, and planning readiness.",
            "Could you reframe the question around one of those areas?",
            "I should not pretend to answer questions outside this demo's measurement scope.",
            "Try a starter question or ask about data, channel performance, experiments, or planning.",
            STARTER_PROMPTS[:2],
            intent,
        ),
    }
    return ShellIntentResponse(intent, answers[intent])
