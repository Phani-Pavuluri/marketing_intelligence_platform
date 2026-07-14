"""Typed, fixture-only loader for the deterministic SaaS sample journey."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mip.demo.chat_first_demo import DEFAULT_FIXTURE_DIR

JOURNEY_ID = "saas_subscriptions_measurement_journey_v1"
_JOURNEY_DIR = DEFAULT_FIXTURE_DIR / "journey"
_VALID_MODES = frozenset(
    {
        "existing_fixture",
        "precomputed_demo_artifact",
        "fixture_backed_replay",
        "external_execution_example",
        "future_runtime_integration",
        "blocked",
    }
)
_REUSED_ARTIFACTS = {"dataset_manifest", "mmm_panel"}


@dataclass(frozen=True)
class SampleJourneyBundle:
    """Validated deterministic fixture bundle with no execution behavior."""

    dataset_id: str
    journey_id: str
    manifest: dict[str, Any]
    artifacts: dict[str, dict[str, Any]]
    prompts: tuple[dict[str, Any], ...]


def list_enabled_demo_datasets() -> tuple[str, ...]:
    """Return the single committed enabled journey dataset."""
    return ("saas_subscriptions_demo_v1",)


def load_sample_journey(dataset_id: str, journey_id: str = JOURNEY_ID) -> SampleJourneyBundle:
    """Load and fail closed on malformed, mismatched, or unsafe fixtures."""
    if dataset_id not in list_enabled_demo_datasets() or journey_id != JOURNEY_ID:
        raise ValueError("unknown sample journey")
    manifest = _read_json(_JOURNEY_DIR / "journey_manifest.json")
    if manifest.get("schema_version") != 1:
        raise ValueError("unsupported journey schema version")
    if manifest.get("dataset_id") != dataset_id or manifest.get("journey_id") != journey_id:
        raise ValueError("journey identity mismatch")
    artifacts: dict[str, dict[str, Any]] = {}
    for filename in manifest["artifact_files"]:
        payload = _read_json(_JOURNEY_DIR / filename)
        artifact_id = payload.get("artifact_id")
        if not isinstance(artifact_id, str) or artifact_id in artifacts:
            raise ValueError("invalid or duplicate artifact id")
        if artifact_id != "prompt_catalog":
            _validate_authored_artifact(payload, dataset_id, journey_id)
        artifacts[artifact_id] = payload
    prompts = tuple(artifacts["prompt_catalog"].get("prompts", []))
    bundle = SampleJourneyBundle(dataset_id, journey_id, manifest, artifacts, prompts)
    _validate_bundle(bundle)
    return bundle


def ordered_stages(bundle: SampleJourneyBundle) -> tuple[dict[str, Any], ...]:
    """Return the manifest's deterministic stage order."""
    return tuple(bundle.manifest["stages"])


def resolve_artifact(bundle: SampleJourneyBundle, artifact_id: str) -> dict[str, Any]:
    """Resolve authored and explicitly reused artifact identifiers."""
    if artifact_id in bundle.artifacts:
        return bundle.artifacts[artifact_id]
    if artifact_id in _REUSED_ARTIFACTS:
        return {"artifact_id": artifact_id, "reused": True}
    raise ValueError("unknown artifact reference")


def contextual_prompts(
    bundle: SampleJourneyBundle, stage_id: str, available_artifact_ids: set[str]
) -> tuple[dict[str, Any], ...]:
    """Return at most three eligible prompts; missing prerequisites suppress them."""
    if stage_id not in {stage["stage_id"] for stage in ordered_stages(bundle)}:
        raise ValueError("unknown stage")
    prompts = [
        prompt
        for prompt in bundle.prompts
        if stage_id in prompt["eligible_stage_ids"]
        and set(prompt["required_artifact_ids"]).issubset(available_artifact_ids)
        and not set(prompt["blocked_when_artifact_ids_missing"]) - available_artifact_ids
    ]
    return tuple(sorted(prompts, key=lambda prompt: (prompt["priority"], prompt["prompt_id"]))[:3])


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        raise ValueError(f"malformed journey fixture: {path.name}") from exc
    if not isinstance(payload, dict):
        raise ValueError("journey fixture must be an object")
    return payload


def _validate_authored_artifact(payload: dict[str, Any], dataset_id: str, journey_id: str) -> None:
    if payload.get("dataset_id") != dataset_id or payload.get("journey_id") != journey_id:
        raise ValueError("artifact identity mismatch")
    if payload.get("execution_mode") not in _VALID_MODES:
        raise ValueError("invalid execution mode")
    labels = (("demo_only", True), ("live_execution", False), ("production_evidence", False))
    for key, expected in labels:
        if payload.get(key) != expected:
            raise ValueError("unsafe execution labeling")
    if payload.get("result_origin") != "authored_deterministic_demo_fixture":
        raise ValueError("missing fixture result origin")


def _validate_bundle(bundle: SampleJourneyBundle) -> None:
    stages = ordered_stages(bundle)
    ids = [stage["stage_id"] for stage in stages]
    if len(ids) != len(set(ids)) or bundle.manifest.get("default_first_stage_id") != ids[0]:
        raise ValueError("invalid stage ordering")
    prior: set[str] = set()
    for stage in stages:
        prerequisites = set(stage["required_previous_stage_ids"])
        if stage["execution_mode"] not in _VALID_MODES or not prerequisites.issubset(prior):
            raise ValueError("invalid stage prerequisite")
        for artifact_id in stage["artifact_ids"]:
            resolve_artifact(bundle, artifact_id)
        prior.add(stage["stage_id"])
    result = bundle.artifacts["mmm_result"]
    contributions = result["channel_evidence"]
    contribution_total = sum(item["illustrative_contribution"] for item in contributions)
    if abs(contribution_total - result["contribution_total"]) > result["reconciliation_tolerance"]:
        raise ValueError("contribution total does not reconcile")
    for item in contributions:
        low, high = item["interval"]
        if not low <= item["illustrative_contribution"] <= high:
            raise ValueError("invalid MMM interval")
    readout = bundle.artifacts["geox_readout"]
    if not readout["interval"][0] <= readout["effect_estimate"] <= readout["interval"][1]:
        raise ValueError("invalid GeoX interval")
    comparison = bundle.artifacts["calibration_comparison"]
    after_width = comparison["after"]["interval"][1] - comparison["after"]["interval"][0]
    if abs(comparison["after"]["uncertainty_width"] - after_width) > 1e-9:
        raise ValueError("comparison uncertainty mismatch")
    planning = bundle.artifacts["planning_readiness"]
    planning_blocked = (
        planning["simulation_readiness"] == "blocked"
        and planning["recommendation_readiness"] == "blocked"
        and planning["production_authorization"] is False
    )
    if not planning_blocked:
        raise ValueError("planning must remain blocked")
