# ruff: noqa
# mypy: ignore-errors
from mip.conversation import ConversationalFrontDoor, FakeConversationalProvider, ProviderConfig
from mip.control_plane.workspace import InMemoryWorkspace


def workspace():
    return InMemoryWorkspace(session_id="s", conversation_id="c", workspace_id="w")


def test_fake_provider_is_llm_first_and_disclosed():
    front = ConversationalFrontDoor(FakeConversationalProvider(), ProviderConfig(enabled=True, provider_id="fake", model_id="test"))
    result = front.handle("whats MMM", workspace=workspace())
    assert "answer" not in result.answer.lower()
    assert result.provider_disclosure.invocation_status == "invoked"


def test_disabled_provider_falls_back_naturally():
    result = ConversationalFrontDoor(config=ProviderConfig()).handle("whats GeoX", workspace=workspace())
    assert "GeoX" in result.answer or "geo" in result.answer.lower()
    assert result.provider_disclosure.fallback_used is True or result.provider_disclosure.invocation_status == "not_invoked"


def test_provider_failure_preserves_safe_fallback():
    front = ConversationalFrontDoor(FakeConversationalProvider(fail=True), ProviderConfig(enabled=True, provider_id="fake", model_id="test"))
    result = front.handle("how can you help", workspace=workspace())
    assert "Measure" in result.answer
    assert result.provider_disclosure.fallback_used
