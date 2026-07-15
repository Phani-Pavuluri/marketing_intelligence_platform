import pytest

# ruff: noqa: E501
from mip.contracts.conversation import CapabilityStatus, EventType, ExecutionMode
from mip.control_plane import (
    CAPABILITY_REGISTRY_VERSION,
    DEFAULT_CAPABILITY_REGISTRY,
    CapabilityRegistry,
    UnknownCapabilityError,
)

REQUIRED_IDS = {
    "platform.onboarding", "data.requirements.explain", "sample.use_case.activate",
    "uploaded_data.intake", "uploaded_data.profile", "uploaded_data.map_columns",
    "uploaded_data.assess_compatibility", "mmm.intake.requirements", "mmm.intake.readiness",
    "mmm.run.request", "mmm.result.explain", "mmm.channel_uncertainty.explain",
    "planning.readiness", "planning.simulation.request", "planning.recommendation.explain_blocked",
    "geox.intake.requirements", "geox.design_request.create", "geox.feasibility.explain",
    "geox.readout.explain", "calibration.compatibility.validate", "calibration.signal.explain",
    "mmm.refresh.compare", "decision_package.build", "artifact.open", "report.open",
    "dashboard.context.update",
}


def test_default_registry_is_complete_immutable_and_deterministic() -> None:
    registry = DEFAULT_CAPABILITY_REGISTRY
    assert registry.registry_version == CAPABILITY_REGISTRY_VERSION
    assert registry.validate() == ()
    assert tuple(item.capability_id for item in registry.list_all()) == tuple(sorted(REQUIRED_IDS))
    assert registry.fingerprint() == registry.fingerprint()
    descriptor = registry.get("platform.onboarding")
    descriptor.owner = "attempted mutation"
    assert registry.get("platform.onboarding").owner != "attempted mutation"


def test_inventory_and_unknown_lookup() -> None:
    assert REQUIRED_IDS <= {item.capability_id for item in DEFAULT_CAPABILITY_REGISTRY.list_all()}
    with pytest.raises(UnknownCapabilityError):
        DEFAULT_CAPABILITY_REGISTRY.get("not.registered")


def test_discovery_filters_are_deterministic_and_metadata_only() -> None:
    fixture = DEFAULT_CAPABILITY_REGISTRY.find(status=CapabilityStatus.FIXTURE_BACKED)
    assert fixture == DEFAULT_CAPABILITY_REGISTRY.find(status=CapabilityStatus.FIXTURE_BACKED)
    assert DEFAULT_CAPABILITY_REGISTRY.find(domain="mmm", supported_intent="mmm.result.explain")
    assert DEFAULT_CAPABILITY_REGISTRY.find(supported_event_type=EventType.FILE_UPLOADED)
    assert DEFAULT_CAPABILITY_REGISTRY.find(execution_mode=ExecutionMode.UPLOADED_SESSION)
    assert DEFAULT_CAPABILITY_REGISTRY.find(workflow_node_id="plan_next_quarter")
    assert DEFAULT_CAPABILITY_REGISTRY.find(domain="does-not-exist") == ()
    assert not any(callable(value) for descriptor in DEFAULT_CAPABILITY_REGISTRY.list_all() for value in descriptor.model_dump().values())


def test_status_claim_input_and_execution_boundaries() -> None:
    registry = DEFAULT_CAPABILITY_REGISTRY
    assert registry.get("sample.use_case.activate").status == CapabilityStatus.FIXTURE_BACKED.value
    assert registry.get("planning.simulation.request").status == CapabilityStatus.BLOCKED.value
    assert registry.get("planning.simulation.request").execution_modes == [ExecutionMode.FUTURE_ENGINE.value]
    assert registry.get("mmm.run.request").status == CapabilityStatus.BLOCKED.value
    assert registry.get("geox.design_request.create").blocked_claims
    assert set(registry.get("mmm.intake.requirements").required_inputs).isdisjoint(
        registry.get("mmm.intake.requirements").conditional_inputs
    )


def test_registry_constructor_rejects_duplicate_and_invalid_relationships() -> None:
    descriptor = DEFAULT_CAPABILITY_REGISTRY.get("platform.onboarding")
    with pytest.raises(ValueError, match="capability IDs must be unique"):
        CapabilityRegistry([descriptor, descriptor])
    invalid = descriptor.model_copy(update={"next_capability_ids": ["missing.capability"]})
    with pytest.raises(ValueError, match="unknown next capability"):
        CapabilityRegistry([invalid])
