"""Provider protocol and deterministic fake; real credentials are never persisted."""
# ruff: noqa
# mypy: ignore-errors
from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol
from pydantic import BaseModel, ValidationError
from mip.contracts.conversation import ProviderDisclosure
from mip.conversation.provider_config import ProviderConfig
from mip.conversation.provider_wire import GroqConversationalProviderWireV2, lint_groq_wire_schema, groq_wire_schema

class ProviderUnavailableError(RuntimeError):
    pass

class ProviderError(ProviderUnavailableError):
    def __init__(self, category: str, *, http_status_class: str | None = None, safe_provider_error_code: str | None = None, safe_request_id: str | None = None, failed_compatibility_stage: str | None = None, validation_field_path: str | None = None, validation_error_type: str | None = None, expected_schema_field_category: str | None = None, validation_error_count: int | None = None):
        self.category = category
        self.http_status_class = http_status_class
        self.safe_provider_error_code = safe_provider_error_code
        self.safe_request_id = safe_request_id
        self.failed_compatibility_stage = failed_compatibility_stage
        self.validation_field_path = validation_field_path
        self.validation_error_type = validation_error_type
        self.expected_schema_field_category = expected_schema_field_category
        self.validation_error_count = validation_error_count
        super().__init__(category)

def _safe_validation_diagnostics(exc: Exception) -> dict[str, object]:
    """Extract type metadata only; rejected values and provider text are never retained."""
    if not isinstance(exc, ValidationError):
        return {}
    errors = exc.errors()
    first = errors[0] if errors else {}
    location = first.get("loc", ())
    path = ".".join(str(part) for part in location if isinstance(part, (str, int)))
    field = str(location[0]) if location and isinstance(location[0], str) else None
    return {
        "validation_field_path": path or None,
        "validation_error_type": str(first.get("type")) if first.get("type") else None,
        "expected_schema_field_category": field,
        "validation_error_count": len(errors),
    }

def _sanitized_provider_error(exc: Exception, *, stage: str) -> ProviderError:
    """Map provider exceptions to safe diagnostics without retaining response bodies."""
    status = getattr(exc, "status_code", None)
    name = type(exc).__name__.casefold()
    body = getattr(exc, "body", None)
    error = body.get("error", {}) if isinstance(body, dict) else {}
    code = error.get("code") or getattr(exc, "code", None)
    if status == 401: category = "authentication_failure"
    elif status == 403: category = "permission_failure"
    elif status == 404: category = "unsupported_model"
    elif status == 429: category = "rate_limit"
    elif isinstance(status, int) and 400 <= status < 500: category = "invalid_request"
    elif isinstance(status, int) and status >= 500: category = "server_failure"
    elif "timeout" in name: category = "timeout"
    elif "connection" in name: category = "connection_failure"
    else: category = "unknown_provider_failure"
    return ProviderError(category, http_status_class=f"{status // 100}xx" if isinstance(status, int) else None, safe_provider_error_code=str(code) if code else None, safe_request_id=getattr(exc, "request_id", None), failed_compatibility_stage=stage, **_safe_validation_diagnostics(exc))

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
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.provider_id = config.provider_id
    def generate(self, request: LLMConversationRequest) -> LLMConversationResponse:
        if request.config.provider_id == "groq":
            return GroqResponsesProvider(request.config).generate(request)
        if request.config.provider_id != "openai":
            raise ProviderError("provider_not_configured")
        return OpenAIResponsesProvider(request.config).generate(request)

class OpenAIConversationalTurnWireOutput(BaseModel):
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
            raise _sanitized_provider_error(exc, stage="full_wire_schema_parse") from None
    def _credential(self) -> str:
        import os
        key = os.getenv("OPENAI_API_KEY", "")
        if not key: raise ProviderError("provider_not_configured")
        return key

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
GROQ_MODELS = frozenset({"openai/gpt-oss-20b", "openai/gpt-oss-120b"})
GROQ_WIRE_INSTRUCTIONS = (
    "Return only the strict structured output. Never execute tools or claim execution. "
    "Populate every required conversational_provider_wire_v3 field: interaction_mode, answer, topic, "
    "domain, user_goal, clarification_question, proposed_capability_id, proposed_workflow_node, "
    "known_inputs, inferred_inputs, missing_inputs, action_requested, and artifact_context_required. "
    "interaction_mode must be exactly one registered value: general_explanation, comparison, "
    "platform_guidance, artifact_interpretation, governed_action, typed_ui_action, or unsupported; "
    "use comparison for conditional MMM-versus-GeoX method guidance. "
    "Use null, never omission, for absent clarification_question, proposed_capability_id, and "
    "proposed_workflow_node. known_inputs, inferred_inputs, and missing_inputs must always be arrays, "
    "using [] when empty; each known or inferred item has name and nullable value. "
    "Capability and workflow identifiers are non-authoritative proposals only. Do not request or emit "
    "retrieval-document IDs, source-document IDs, platform-truth IDs, or reference IDs."
)

class GroqResponsesProvider(OpenAIResponsesProvider):
    provider_id = "groq"
    def generate(self, request: LLMConversationRequest) -> LLMConversationResponse:
        if request.config.model_id not in GROQ_MODELS:
            raise ProviderError("unsupported_model")
        try:
            lint_groq_wire_schema(groq_wire_schema())
            from openai import OpenAI
            client = OpenAI(api_key=self._credential(), base_url=GROQ_BASE_URL, timeout=self.config.timeout_seconds, max_retries=self.config.max_retries)
            response = client.responses.parse(model=self.config.model_id, instructions=GROQ_WIRE_INSTRUCTIONS, input=request.prompt, text_format=GroqConversationalProviderWireV2, max_output_tokens=self.config.max_output_tokens)
            parsed = getattr(response, "output_parsed", None)
            if parsed is None: raise ProviderError("malformed_structured_output")
            return LLMConversationResponse(output=parsed.model_dump(), disclosure=ProviderDisclosure(invocation_status="invoked", provider_id="groq", model_id=self.config.model_id, prompt_template_id=self.config.prompt_template_id, prompt_version=self.config.prompt_version, configuration_id=self.config.configuration_id))
        except ProviderError: raise
        except Exception as exc:
            raise _sanitized_provider_error(exc, stage="full_wire_schema_parse") from None
    def _credential(self) -> str:
        import os
        key = os.getenv("GROQ_API_KEY", "")
        if not key: raise ProviderError("provider_not_configured")
        return key
