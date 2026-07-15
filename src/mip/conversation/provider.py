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
    """Explicit seam for a future SDK adapter; unavailable until an SDK adapter is installed."""
    provider_id = "configured"
    def __init__(self, config: ProviderConfig): self.config = config
    def generate(self, request: LLMConversationRequest) -> LLMConversationResponse:
        raise ProviderUnavailableError("configured provider adapter is unavailable")
