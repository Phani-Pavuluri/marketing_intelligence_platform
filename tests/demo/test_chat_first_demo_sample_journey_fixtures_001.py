"""Contract tests for the deterministic SaaS sample journey bundle."""

import pytest

from mip.demo.sample_journey import (
    JOURNEY_ID,
    contextual_prompts,
    list_enabled_demo_datasets,
    load_sample_journey,
    ordered_stages,
    resolve_artifact,
)


def test_golden_chain_loads_with_resolved_references() -> None:
    bundle = load_sample_journey("saas_subscriptions_demo_v1")
    assert bundle.journey_id == JOURNEY_ID
    assert [stage["stage_id"] for stage in ordered_stages(bundle)] == [
        "select_dataset", "upload_requirements", "mmm_readiness", "mmm_run",
        "evidence_gap", "geox_request", "geox_readout", "calibration",
        "refreshed_mmm", "planning_readiness",
    ]
    for stage in ordered_stages(bundle):
        for artifact_id in stage["artifact_ids"]:
            assert resolve_artifact(bundle, artifact_id)["artifact_id"] == artifact_id


def test_fixture_labels_numeric_consistency_and_claim_safety() -> None:
    bundle = load_sample_journey("saas_subscriptions_demo_v1")
    assert list_enabled_demo_datasets() == ("saas_subscriptions_demo_v1",)
    assert bundle.artifacts["evidence_gap"]["affected_channel"] == "Meta"
    assert bundle.artifacts["geox_readout"]["channel"] == "Meta"
    assert bundle.artifacts["calibration_signal"]["treatment"] == "downweighted"
    assert bundle.artifacts["planning_readiness"]["recommendation_readiness"] == "blocked"
    for artifact_id, artifact in bundle.artifacts.items():
        if artifact_id == "prompt_catalog":
            continue
        assert artifact["demo_only"] is True
        assert artifact["live_execution"] is False
        assert artifact["production_evidence"] is False


def test_contextual_prompts_fail_closed_when_prerequisites_are_missing() -> None:
    bundle = load_sample_journey("saas_subscriptions_demo_v1")
    assert not contextual_prompts(bundle, "calibration", set())
    prompts = contextual_prompts(bundle, "calibration", {"geox_readout"})
    assert prompts[0]["prompt_id"] == "calibration"
    with pytest.raises(ValueError, match="unknown"):
        load_sample_journey("unknown")
    with pytest.raises(ValueError, match="unknown"):
        contextual_prompts(bundle, "unknown", set())
