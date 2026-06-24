"""Deterministic LLM provider interfaces and mock implementation."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, field_validator

from mip.contracts.base import ContractBaseModel
from mip.llm.explanations import (
    EXECUTION_DISCLAIMER,
    assert_safe_explanation,
    explain_blockers,
    explain_next_steps,
    explain_workflow_summary,
)
from mip.workflows.orchestrator import WorkflowRunSummary


class LLMProviderName(StrEnum):
    """Supported LLM provider identifiers."""

    MOCK = "mock"


class LLMProviderResponse(ContractBaseModel):
    """Structured response from an LLM provider."""

    provider: LLMProviderName
    text: str
    disclaimers: list[str] = Field(default_factory=list)

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, value: str) -> str:
        if not value.strip():
            msg = "provider response text cannot be empty"
            raise ValueError(msg)
        return value

    @field_validator("disclaimers")
    @classmethod
    def disclaimers_not_empty(cls, value: list[str]) -> list[str]:
        if any(not item.strip() for item in value):
            msg = "disclaimers cannot contain empty strings"
            raise ValueError(msg)
        return value


class MockLLMProvider:
    """Deterministic explanation provider with no network calls or API keys."""

    provider_name: LLMProviderName = LLMProviderName.MOCK

    def explain(self, summary: WorkflowRunSummary) -> LLMProviderResponse:
        """Explain a workflow summary conversationally."""
        text = explain_workflow_summary(summary)
        return self._build_response(text)

    def explain_blockers(self, summary: WorkflowRunSummary) -> LLMProviderResponse:
        """Explain only blocking reasons from a workflow summary."""
        text = explain_blockers(summary)
        return self._build_response(text)

    def explain_next_steps(self, summary: WorkflowRunSummary) -> LLMProviderResponse:
        """Explain recommended questions and fixes from a workflow summary."""
        text = explain_next_steps(summary)
        return self._build_response(text)

    def _build_response(self, text: str) -> LLMProviderResponse:
        assert_safe_explanation(text)
        return LLMProviderResponse(
            provider=self.provider_name,
            text=text,
            disclaimers=[EXECUTION_DISCLAIMER],
        )
