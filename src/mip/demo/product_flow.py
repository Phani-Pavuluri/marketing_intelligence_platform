# ruff: noqa: E501
"""Deterministic state and view models for the chat-first sample journey."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mip.demo.sample_journey import SampleJourneyBundle, ordered_stages

DATASET_ID = "saas_subscriptions_demo_v1"
DATASET_NAME = "SaaS subscriptions"


@dataclass(frozen=True)
class ProductAnswer:
    text: str
    category: str
    next_action: str
    artifact_id: str | None = None


def initial_product_state() -> dict[str, Any]:
    """Return a no-dataset state with no hidden fixture context."""
    return {
        "entry_mode": None,
        "active_dataset_id": None,
        "active_use_case_id": None,
        "active_journey_id": None,
        "active_stage_id": None,
        "conversation_messages": [],
        "active_starter_prompt_id": None,
        "completed_stage_ids": [],
        "available_artifact_ids": set(),
        "last_answer_category": "onboarding",
        "suggested_follow_up_ids": [],
        "demo_execution_mode": "none",
    }


def select_sample_mode(state: dict[str, Any]) -> None:
    """Enter sample mode without activating a dataset."""
    state.update(initial_product_state())
    state["entry_mode"] = "sample_use_case"


def select_upload_information(state: dict[str, Any]) -> None:
    """Enter the non-upload informational readiness path."""
    state.update(initial_product_state())
    state["entry_mode"] = "upload_readiness_information"


def select_dataset(state: dict[str, Any], bundle: SampleJourneyBundle) -> None:
    """Set explicit demo context and clear incompatible journey state."""
    state.update(initial_product_state())
    state["entry_mode"] = "sample_use_case"
    state["active_dataset_id"] = bundle.dataset_id
    state["active_use_case_id"] = "saas_growth_planning"
    state["available_artifact_ids"] = {"dataset_manifest", "mmm_panel"}
    state["demo_execution_mode"] = "fixture_backed_replay"


def select_journey(state: dict[str, Any], bundle: SampleJourneyBundle, stage_id: str) -> None:
    """Activate a fixture-backed journey stage after explicit dataset selection."""
    if state["active_dataset_id"] != bundle.dataset_id:
        raise ValueError("dataset must be selected before a journey")
    stage = next((item for item in ordered_stages(bundle) if item["stage_id"] == stage_id), None)
    if stage is None:
        raise ValueError("unknown journey stage")
    state["active_journey_id"] = bundle.journey_id
    state["active_stage_id"] = stage_id
    state["available_artifact_ids"].update(stage["artifact_ids"])
    state["demo_execution_mode"] = stage["execution_mode"]


def product_answer(state: dict[str, Any], bundle: SampleJourneyBundle, question: str) -> ProductAnswer:
    """Return safe deterministic business-language answers for active context."""
    normalized = question.casefold()
    if state["active_dataset_id"] is None:
        if any(term in normalized for term in ("ready", "roi", "roas", "dataset", "data")):
            return ProductAnswer(
                "Select the SaaS subscriptions demo below to assess a concrete dataset, or ask what data you would need to upload for your own use case.",
                "onboarding",
                "Select a sample dataset.",
            )
        return ProductAnswer(
            "MIP helps you understand data requirements, choose MMM or GeoX, inspect governed evidence, and see which planning conclusions are trustworthy.",
            "onboarding",
            "Explore the SaaS subscriptions sample journey.",
        )
    stage = state["active_stage_id"] or "select_dataset"
    if stage == "planning_readiness":
        return ProductAnswer(
            "Active demo dataset: SaaS subscriptions. Explanation is available, but simulation and recommendation readiness are blocked.",
            "planning",
            "Review the missing governed simulation and recommendation evidence.",
            "planning_readiness",
        )
    if "geox" in normalized or stage in {"evidence_gap", "geox_request", "geox_readout"}:
        return ProductAnswer(
            "Active demo dataset: SaaS subscriptions. The sample shows a governed GeoX evidence workflow for Meta; MIP routes the request while GeoX owns feasibility and assignment.",
            "geox",
            "Review the sample evidence and its limits.",
            "geox_readout" if "geox_readout" in bundle.artifacts else None,
        )
    return ProductAnswer(
        "Active demo dataset: SaaS subscriptions. This fixture supports readiness and illustrative evidence explanation, not live fitting, ROI, or budget recommendations.",
        "dataset",
        "Choose a journey stage to inspect its fixture-backed evidence.",
        "mmm_result" if "mmm_result" in bundle.artifacts else None,
    )
