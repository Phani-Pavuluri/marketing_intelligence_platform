"""Deterministic copy and answer views for the guided workspace shell."""

from __future__ import annotations

from dataclasses import dataclass

CANONICAL_HERO = "Turn marketing data into trustworthy spend decisions"
WELCOME_COPY = (
    "MIP helps you understand what is driving marketing performance, where the evidence is "
    "uncertain, and what is safe to do next—whether you are measuring channels, planning "
    "future spend, or deciding what to test.\n\n"
    "Ask a question below, explore a sample measurement story, or review what data would be "
    "needed for your own analysis."
)
UPLOAD_INFORMATION_COPY = (
    "The readiness workspace is planned, not implemented here. It will support CSV inventory, "
    "profiling, column mapping, grain checks, and MMM/GeoX readiness. It will not provide live "
    "fitting, ROI, optimization, or experiment execution."
)

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
            f"{self.useful_detail}\n\n"
            f"**Important limitation:** {self.important_limitation}\n\n"
            f"**Next action:** {self.next_action}\n\n"
            f"You could also ask: {', '.join(self.follow_ups)}"
        )


_STARTER_ANSWERS: dict[str, ShellAnswer] = {
    STARTER_PROMPTS[0]: ShellAnswer(
        "MIP helps a marketing team understand which channels appear to be driving results, "
        "how confident the evidence is, and what should happen next.",
        "It connects historical channel analysis, future-budget planning, and incrementality "
        "experiments in one workflow. It can help answer which channels are contributing, "
        "where results are uncertain, what to test, and whether it is safe to change next "
        "quarter's budget.",
        "MIP does not automatically turn weak evidence into a recommendation.",
        "Explore a sample measurement story or ask what data is needed for your analysis.",
        (STARTER_PROMPTS[1], STARTER_PROMPTS[2]),
        "platform_capabilities",
    ),
    STARTER_PROMPTS[1]: ShellAnswer(
        "At minimum, you need marketing spend by channel over time and a business outcome "
        "such as conversions, revenue, or new customers.",
        "Helpful supporting data includes dates, channel names, spend, the KPI outcome, and "
        "a region or segment when available. Promotions, pricing changes, holidays, product "
        "launches, other major non-marketing drivers, and optional experiment results add "
        "useful context. More history and meaningful changes in spend usually make the "
        "analysis more reliable.",
        "These are general requirements; no specific dataset has been assessed yet.",
        "Explore a sample measurement story or review the planned readiness workspace.",
        (STARTER_PROMPTS[2], STARTER_PROMPTS[3]),
        "data_requirements",
    ),
    STARTER_PROMPTS[2]: ShellAnswer(
        "Use MMM when you want to understand how several channels have performed together "
        "over time. Use GeoX when you need a cleaner causal answer for a specific channel, "
        "campaign, or region.",
        "They are often most useful together: MMM can show where the evidence is weak, and "
        "a GeoX experiment can provide stronger evidence for that specific question. MIP "
        "coordinates the workflow.",
        "MMM does not directly design the experiment, the assistant does not choose treatment "
        "markets, and experiment feasibility and assignment belong to the experiment system.",
        "Start with the business question and the uncertainty you need to resolve.",
        (STARTER_PROMPTS[0], STARTER_PROMPTS[3]),
        "method_choice",
    ),
    STARTER_PROMPTS[3]: ShellAnswer(
        "Planning next quarter requires more than knowing which channels performed well in "
        "the past.",
        "The platform first checks whether the model is reliable, whether proposed spend is "
        "within a range the data can support, and how uncertain the expected outcome is. The "
        "practical flow is: understand the current plan → compare possible spend changes → "
        "estimate likely business impact → check uncertainty and risk → decide whether a "
        "recommendation is justified.",
        "The current demo does not run live optimization or authorize budget changes.",
        "Explore a sample measurement story to see the planning readiness boundary.",
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
        "Choose a sample measurement story for a concrete example. The Analyze my data path "
        "currently explains the planned readiness workflow only.",
        "I cannot make dataset-specific readiness, channel, GeoX, or planning claims without "
        "an explicit active context.",
        "Select a sample measurement story to explore a concrete dataset, or choose Analyze "
        "my data to review the planned readiness workflow.",
        STARTER_PROMPTS[:2],
        "dataset_required",
    )
