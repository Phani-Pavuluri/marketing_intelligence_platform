"""Deterministic copy and answer views for the guided workspace shell."""

from __future__ import annotations

from dataclasses import dataclass

CANONICAL_HERO = "Turn marketing data into trustworthy spend decisions"

STARTER_PROMPTS: tuple[str, ...] = (
    "What can MIP help my marketing team do?",
    "What data would I need to analyze channel performance?",
    "Should I use MMM, GeoX, or both?",
    "Show me how MIP supports next-quarter planning.",
)


@dataclass(frozen=True)
class ShellAnswer:
    """Business-facing deterministic response for a P1 shell prompt."""

    direct_answer: str
    useful_detail: str
    important_limitation: str
    next_action: str
    follow_ups: tuple[str, ...]
    category: str

    def render_text(self) -> str:
        return (
            f"{self.direct_answer}\n\n"
            f"**Useful detail:** {self.useful_detail}\n\n"
            f"**Important limitation:** {self.important_limitation}\n\n"
            f"**Next action:** {self.next_action}\n\n"
            f"**You could also ask:** {', '.join(self.follow_ups)}"
        )


_STARTER_ANSWERS: dict[str, ShellAnswer] = {
    STARTER_PROMPTS[0]: ShellAnswer(
        "MIP helps marketing teams turn evidence into safer spend decisions.",
        "It can organize historical channel measurement, show uncertainty and evidence gaps, "
        "prepare planning prerequisites, route governed GeoX requests, and explain how "
        "compatible experiment evidence can improve future MMM understanding.",
        "The public demo is deterministic. It does not claim that every capability is live, "
        "and it does not authorize recommendations without governed evidence.",
        "Explore the SaaS growth-planning example to see a concrete fixture-backed journey.",
        (STARTER_PROMPTS[1], STARTER_PROMPTS[2]),
        "platform_capabilities",
    ),
    STARTER_PROMPTS[1]: ShellAnswer(
        "Start with channel spend, a KPI outcome, and a reliable time field.",
        "Useful inputs usually include geography or segment grain, controls, promotion or "
        "calendar context, enough usable history and variation, and optional experiment "
        "evidence. Those are general requirements, not a statement about the SaaS demo.",
        "MIP cannot assess a specific dataset until you select the sample or use the future "
        "readiness workflow.",
        "Explore the sample to inspect its preloaded structure, or review what the planned "
        "readiness workflow will accept.",
        (STARTER_PROMPTS[2], STARTER_PROMPTS[3]),
        "data_requirements",
    ),
    STARTER_PROMPTS[2]: ShellAnswer(
        "MMM and GeoX answer related but different measurement questions.",
        "MMM helps assess cross-channel historical evidence and planning readiness. GeoX is "
        "useful when an important incremental causal question remains uncertain. Together, "
        "experiment evidence can inform a later calibration workflow.",
        "MIP orchestrates the governed workflow; MMM does not design GeoX tests, and no LLM "
        "chooses treatment markets or executes an experiment.",
        "Start with the decision and evidence gap, then select the appropriate governed path.",
        (STARTER_PROMPTS[0], STARTER_PROMPTS[3]),
        "method_choice",
    ),
    STARTER_PROMPTS[3]: ShellAnswer(
        "Next-quarter planning starts with governed evidence, not an immediate budget "
        "recommendation.",
        "The required chain is governed MMM evidence, supported spend ranges, baseline or "
        "candidate simulation, uncertainty and extrapolation checks, then recommendation "
        "authorization.",
        "This demo does not run live simulation or optimization and does not authorize budget "
        "recommendations.",
        "Explore the SaaS planning example to see the evidence and readiness boundary.",
        (STARTER_PROMPTS[1], STARTER_PROMPTS[2]),
        "planning",
    ),
}


def starter_answer(question: str) -> ShellAnswer | None:
    """Return the distinct deterministic answer for a canonical starter prompt."""

    return _STARTER_ANSWERS.get(question)


def preselection_answer(question: str) -> ShellAnswer:
    """Return a safe answer when a dataset-specific question has no context."""

    answer = starter_answer(question)
    if answer is not None:
        return answer
    return ShellAnswer(
        "I can explain platform capabilities and measurement prerequisites before a dataset is "
        "selected.",
        "For a concrete fixture-backed example, choose the SaaS growth-planning use case. "
        "The Analyze my data path currently explains the planned readiness workflow only.",
        "I cannot make dataset-specific readiness, channel, GeoX, or planning claims without "
        "an explicit active context.",
        "Select the SaaS growth-planning example to explore a concrete dataset, or choose "
        "Analyze my data to review the planned readiness workflow.",
        STARTER_PROMPTS[:2],
        "dataset_required",
    )
