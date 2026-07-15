# ruff: noqa
# mypy: ignore-errors
from mip.conversation import ConversationalFrontDoor, FakeConversationalProvider, ProviderConfig
from mip.conversation.provider import GROQ_BASE_URL, GroqResponsesProvider, LLMConversationRequest, OpenAIResponsesProvider
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


def test_openai_adapter_uses_lazy_structured_responses_parse(monkeypatch):
    class Parsed:
        def model_dump(self):
            return {"interaction_mode": "general_explanation", "topic": "mmm", "domain": "mmm", "user_goal": "explain", "answer": "MMM explanation"}
    class Responses:
        def parse(self, **kwargs):
            assert kwargs["store"] is False
            assert kwargs["max_output_tokens"] == 1200
            assert "tools" not in kwargs
            return type("Response", (), {"output_parsed": Parsed()})()
    class Client:
        def __init__(self, **kwargs): self.responses = Responses()
    monkeypatch.setattr("openai.OpenAI", Client)
    config = ProviderConfig(enabled=True, provider_id="openai", model_id="gpt-test")
    monkeypatch.setenv("OPENAI_API_KEY", "redacted-test-key")
    response = OpenAIResponsesProvider(config).generate(LLMConversationRequest(prompt="hello", config=config))
    assert response.output["answer"] == "MMM explanation"
    assert response.disclosure.provider_id == "openai"
    assert "redacted-test-key" not in repr(response.disclosure)


def test_groq_adapter_uses_compatible_endpoint_without_store(monkeypatch):
    class Parsed:
        def model_dump(self):
            return {"interaction_mode": "general_explanation", "topic": "mmm", "domain": "mmm", "user_goal": "explain", "answer": "MMM explanation"}
    class Responses:
        def parse(self, **kwargs):
            assert kwargs["model"] == "openai/gpt-oss-20b"
            assert "store" not in kwargs
            assert "tools" not in kwargs
            return type("Response", (), {"output_parsed": Parsed()})()
    class Client:
        def __init__(self, **kwargs):
            assert kwargs["base_url"] == GROQ_BASE_URL
            self.responses = Responses()
    monkeypatch.setattr("openai.OpenAI", Client)
    monkeypatch.setenv("GROQ_API_KEY", "redacted-test-key")
    config = ProviderConfig(enabled=True, provider_id="groq", model_id="openai/gpt-oss-20b")
    response = GroqResponsesProvider(config).generate(LLMConversationRequest(prompt="hello", config=config))
    assert response.disclosure.provider_id == "groq"


def test_groq_model_catalog_fails_closed(monkeypatch):
    config = ProviderConfig(enabled=True, provider_id="groq", model_id="unsupported/model")
    monkeypatch.setenv("GROQ_API_KEY", "redacted-test-key")
    with __import__("pytest").raises(Exception):
        GroqResponsesProvider(config).generate(LLMConversationRequest(prompt="hello", config=config))
