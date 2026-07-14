from mip.demo.product_flow import (
    initial_product_state,
    product_answer,
    select_dataset,
    select_journey,
)
from mip.demo.sample_journey import load_sample_journey


def test_no_dataset_state_blocks_dataset_claims() -> None:
    bundle = load_sample_journey("saas_subscriptions_demo_v1")
    state = initial_product_state()
    answer = product_answer(state, bundle, "Is my data ready for MMM?")
    assert state["active_dataset_id"] is None
    assert "Select the SaaS subscriptions demo" in answer.text
    assert "your data is ready" not in answer.text.casefold()


def test_dataset_and_journey_state_are_explicit_and_resettable() -> None:
    bundle = load_sample_journey("saas_subscriptions_demo_v1")
    state = initial_product_state()
    select_dataset(state, bundle)
    select_journey(state, bundle, "evidence_gap")
    assert state["active_dataset_id"] == "saas_subscriptions_demo_v1"
    assert state["active_stage_id"] == "evidence_gap"
    assert "evidence_gap" in state["available_artifact_ids"]
    state.update(initial_product_state())
    assert state["active_journey_id"] is None
