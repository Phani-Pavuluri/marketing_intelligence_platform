# ruff: noqa
# mypy: ignore-errors
from mip.conversation import ConversationalFrontDoor, FakeConversationalProvider, ProviderConfig
from mip.conversation.provider import ConfiguredProvider, GROQ_BASE_URL, GroqResponsesProvider, LLMConversationRequest, OpenAIResponsesProvider, ProviderError, _sanitized_provider_error
from mip.control_plane.workspace import InMemoryWorkspace
from mip.conversation.provider_wire import map_groq_wire_to_internal


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


@__import__("pytest").mark.parametrize("probe", ["test", "ping", "health check", "are you working"])
def test_readiness_probes_use_typed_deterministic_route_without_provider_invocation(probe):
    provider = FakeConversationalProvider()
    result = ConversationalFrontDoor(provider, ProviderConfig(enabled=True, provider_id="fake", model_id="test")).handle(probe, workspace=workspace())
    assert provider.calls == 0
    assert result.provider_disclosure.invocation_status == "not_invoked"
    assert result.provider_disclosure.fallback_used is False
    assert "ready" in result.answer.casefold()


@__import__("pytest").mark.parametrize("text", ["measurement", "mmm", "geox", "help"])
def test_analytical_short_inputs_remain_provider_routed(text):
    provider = FakeConversationalProvider()
    ConversationalFrontDoor(provider, ProviderConfig(enabled=True, provider_id="fake", model_id="test")).handle(text, workspace=workspace())
    assert provider.calls == 1


def test_provider_failure_preserves_safe_fallback():
    front = ConversationalFrontDoor(FakeConversationalProvider(fail=True), ProviderConfig(enabled=True, provider_id="fake", model_id="test"))
    result = front.handle("how can you help", workspace=workspace())
    assert "Measure" in result.answer
    assert result.provider_disclosure.fallback_used


def test_provider_failure_disclosure_preserves_sanitized_category():
    class FailingProvider:
        provider_id = "groq"

        def generate(self, request):
            raise ProviderError("connection_failure", failed_compatibility_stage="plain_response")

    result = ConversationalFrontDoor(FailingProvider(), ProviderConfig(enabled=True, provider_id="groq", model_id="openai/gpt-oss-20b")).handle("whats MMM", workspace=workspace())
    assert result.provider_disclosure.fallback_used
    assert result.provider_disclosure.provider_error_category == "connection_failure"
    assert result.provider_disclosure.failed_compatibility_stage == "plain_response"
    assert result.provider_disclosure.fallback_reason == "provider_error"


def test_configured_provider_disclosure_uses_configured_provider_id():
    assert ConfiguredProvider(ProviderConfig(enabled=True, provider_id="groq", model_id="openai/gpt-oss-20b")).provider_id == "groq"


def test_groq_connection_error_is_sanitized(monkeypatch):
    class APIConnectionError(Exception):
        pass

    class Client:
        def __init__(self, **kwargs):
            self.responses = type("Responses", (), {"parse": lambda self, **kwargs: (_ for _ in ()).throw(APIConnectionError())})()

    monkeypatch.setattr("openai.OpenAI", Client)
    monkeypatch.setenv("GROQ_API_KEY", "redacted-test-key")
    config = ProviderConfig(enabled=True, provider_id="groq", model_id="openai/gpt-oss-20b")
    with __import__("pytest").raises(ProviderError, match="connection_failure") as error:
        GroqResponsesProvider(config).generate(LLMConversationRequest(prompt="hello", config=config))
    assert error.value.failed_compatibility_stage == "full_wire_schema_parse"


def test_openai_adapter_uses_lazy_structured_responses_parse(monkeypatch):
    class Parsed:
        def model_dump(self):
            return {"interaction_mode": "general_explanation", "answer": "MMM explanation", "topic": "mmm", "domain": "mmm", "user_goal": "explain", "clarification_question": None, "proposed_capability_id": None, "proposed_workflow_node": None, "known_inputs": [], "inferred_inputs": [], "missing_inputs": [], "action_requested": False, "artifact_context_required": False}
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
            assert "previous_response_id" not in kwargs
            assert "stream" not in kwargs
            assert "background" not in kwargs
            assert "reasoning" not in kwargs
            assert kwargs["text_format"].__name__ == "GroqConversationalProviderWireV2"
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


def test_wire_mapper_injects_only_current_turn_references():
    raw = {"interaction_mode": "general_explanation", "answer": "MMM uses historical data.", "topic": "mmm", "domain": "measurement", "user_goal": "explain", "clarification_question": None, "proposed_capability_id": None, "proposed_workflow_node": None, "known_inputs": [], "inferred_inputs": [], "missing_inputs": [], "action_requested": False, "artifact_context_required": False}
    result = map_groq_wire_to_internal(raw, allowed_source_ids={"mmm_primer"}, allowed_truth_ids={"truth.current"})
    assert result["source_document_ids"] == ["mmm_primer"]
    assert result["platform_truth_reference_ids"] == ["truth.current"]


def test_wire_mapper_handles_empty_current_turn_context_safely():
    raw = {"interaction_mode": "general_explanation", "answer": "MMM uses historical data.", "topic": "mmm", "domain": "measurement", "user_goal": "explain", "clarification_question": None, "proposed_capability_id": None, "proposed_workflow_node": None, "known_inputs": [], "inferred_inputs": [], "missing_inputs": [], "action_requested": False, "artifact_context_required": False}
    result = map_groq_wire_to_internal(raw, allowed_source_ids=set(), allowed_truth_ids=set())
    assert result["source_document_ids"] == []
    assert result["platform_truth_reference_ids"] == []


def test_wire_mapper_normalizes_comparison_and_safe_recommendation_language():
    raw = {"interaction_mode": "comparison", "answer": "I would not recommend one method universally.", "topic": "mmm_geox", "domain": "measurement", "user_goal": "compare", "clarification_question": None, "proposed_capability_id": None, "proposed_workflow_node": None, "known_inputs": [], "inferred_inputs": [], "missing_inputs": [], "action_requested": False, "artifact_context_required": False}
    result = map_groq_wire_to_internal(raw, allowed_source_ids=set(), allowed_truth_ids=set())
    assert result["interaction_mode"] == "general_explanation"


@__import__("pytest").mark.parametrize("answer", ["MIP recommends this budget.", "Choose treatment markets now.", "MIP executed the MMM."])
def test_wire_mapper_blocks_comparison_safety_violations(answer):
    raw = {"interaction_mode": "comparison", "answer": answer, "topic": "mmm_geox", "domain": "measurement", "user_goal": "compare", "clarification_question": None, "proposed_capability_id": None, "proposed_workflow_node": None, "known_inputs": [], "inferred_inputs": [], "missing_inputs": [], "action_requested": True, "artifact_context_required": False}
    with __import__("pytest").raises(Exception):
        map_groq_wire_to_internal(raw, allowed_source_ids=set(), allowed_truth_ids=set())


@__import__("pytest").mark.parametrize(
    ("status", "name", "expected"),
    [
        (401, "APIStatusError", "authentication_failure"),
        (403, "APIStatusError", "permission_failure"),
        (404, "APIStatusError", "unsupported_model"),
        (429, "RateLimitError", "rate_limit"),
        (400, "BadRequestError", "invalid_request"),
        (500, "InternalServerError", "server_failure"),
        (None, "APITimeoutError", "timeout"),
        (None, "APIConnectionError", "connection_failure"),
        (None, "UnexpectedError", "unknown_provider_failure"),
    ],
)
def test_provider_error_mapping_is_sanitized(status, name, expected):
    exception_type = type(name, (Exception,), {})
    error = exception_type()
    error.status_code = status
    error.body = {"error": {"code": "safe-code"}}
    error.request_id = "req_safe"
    mapped = _sanitized_provider_error(error, stage="plain_response")
    assert mapped.category == expected
    assert mapped.failed_compatibility_stage == "plain_response"
    assert mapped.safe_provider_error_code == "safe-code"
    assert mapped.safe_request_id == "req_safe"
    assert mapped.http_status_class == (f"{status // 100}xx" if status else None)
