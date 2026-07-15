from mip.contracts.conversation import CapabilityStatus
from mip.control_plane import DEFAULT_CAPABILITY_REGISTRY


def test_capability_registry_governance_invariants() -> None:
    registry = DEFAULT_CAPABILITY_REGISTRY
    assert registry.validate() == ()
    assert registry.get("planning.simulation.request").status == CapabilityStatus.BLOCKED.value
    assert registry.get("mmm.run.request").status == CapabilityStatus.BLOCKED.value
    assert registry.get("planning.recommendation.explain_blocked").blocked_claims
    assert registry.fingerprint()
