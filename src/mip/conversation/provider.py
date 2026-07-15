"""Provider protocol and deterministic fake; real credentials are never persisted."""
# ruff: noqa
# mypy: ignore-errors
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from mip.contracts.conversation import ProviderDisclosure
from mip.conversation.provider_config import ProviderConfig

class ProviderUnavailableError(RuntimeError):
    pass

class ProviderError(ProviderUnavailableError):
    def __init__(self, category: str):
        self.category = category
        super().__init__(category)

@dataclass(frozen=True)
class LLMConversationRequest:
    prompt: str
    config: ProviderConfig

@dataclass(frozen=True)
class LLMConversationResponse:
    output: dict
    disclosure: ProviderDisclosure

class ConversationalLLMProvider(Protocol):
    provider_id: str
    def generate(self, request: LLMConversationRequest) -> LLMConversationResponse: ...

class FakeConversationalProvider:
    provider_id = "fake"
    def __init__(self, output: dict | None = None, *, fail: bool = False):
        self.output = output
        self.fail = fail
        self.calls = 0
    def generate(self, request: LLMConversationRequest) -> LLMConversationResponse:
        self.calls += 1
        if self.fail: raise ProviderUnavailableError("configured provider unavailable")
        output = self.output or {"answer": "I can explain MIP concepts and current governed boundaries.", "interaction_mode": "general_explanation", "topic": "measurement", "domain": "platform", "user_goal": "explain"}
        return LLMConversationResponse(output=output, disclosure=ProviderDisclosure(invocation_status="invoked", provider_id=self.provider_id, model_id="fake", prompt_template_id=request.config.prompt_template_id, prompt_version=request.config.prompt_version, configuration_id="fake"))

class ConfiguredProvider:
    """Lazy configured-provider factory; OpenAI is the supported concrete adapter."""
    provider_id = "openai"
    def __init__(self, config: ProviderConfig): self.config = config
    def generate(self, request: LLMConversationRequest) -> LLMConversationResponse:
        if request.config.provider_id != "openai":
            raise ProviderError("provider_not_configured")
        return OpenAIResponsesProvider(request.config).generate(request)

class OpenAIConversationalTurnWireOutput(__import__("pydantic").BaseModel):
    model_config = {"extra": "forbid"}
    interaction_mode: str
    topic: str
    domain: str
    user_goal: str
    answer: str
    requires_platform_truth: bool = False
    requires_retrieval: bool = False
    requires_artifact: bool = False
    requires_execution: bool = False
    candidate_capability_id: str | None = None
    requested_workflow_node_id: str | None = None
    known_inputs: dict = {}
    inferred_inputs: dict = {}
    missing_inputs: list[str] = []
    clarification_required: bool = False
    clarification_targets: list[str] = []
    source_document_ids: list[str] = []
    platform_truth_reference_ids: list[str] = []

class OpenAIResponsesProvider:
    provider_id = "openai"
    def __init__(self, config: ProviderConfig): self.config = config
    def generate(self, request: LLMConversationRequest) -> LLMConversationResponse:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self._credential(), timeout=self.config.timeout_seconds, max_retries=self.config.max_retries, project=self.config.project)
            response = client.responses.parse(model=self.config.model_id, instructions="Return only the strict structured output. Never execute tools or claim execution.", input=request.prompt, text_format=OpenAIConversationalTurnWireOutput, max_output_tokens=self.config.max_output_tokens, store=False)
            parsed = getattr(response, "output_parsed", None)
            if parsed is None: raise ProviderError("malformed_structured_output")
            return LLMConversationResponse(output=parsed.model_dump(), disclosure=ProviderDisclosure(invocation_status="invoked", provider_id="openai", model_id=self.config.model_id, prompt_template_id=self.config.prompt_template_id, prompt_version=self.config.prompt_version, configuration_id=self.config.configuration_id))
        except ProviderError: raise
        except Exception as exc:
            name = type(exc).__name__.lower()
            category = "timeout" if "timeout" in name else "authentication_failure" if "auth" in name else "rate_limit" if "rate" in name else "unknown_provider_failure"
            raise ProviderError(category) from None
    def _credential(self) -> str:
        import os
        key = os.getenv("OPENAI_API_KEY", "")
        if not key: raise ProviderError("provider_not_configured")
        return key
