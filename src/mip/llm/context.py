"""Structured explanation context for future LLM providers."""

from pydantic import Field, field_validator, model_validator

from mip.contracts import ConfidenceTier, ContractBaseModel, TrustReport
from mip.llm.safety import (
    allowed_actions_for_confidence_tier,
    blocked_actions_for_confidence_tier,
)


class LLMExplanationContext(ContractBaseModel):
    """Deterministic context bundle for explaining a governed artifact."""

    artifact_id: str
    artifact_type: str
    confidence_tier: ConfidenceTier
    summary: str
    warnings: list[str] = Field(default_factory=list)
    failures: list[str] = Field(default_factory=list)
    unsupported_claims: list[str] = Field(default_factory=list)
    allowed_actions: list[str] = Field(default_factory=list)
    blocked_actions: list[str] = Field(default_factory=list)
    source_trace_uri: str | None = None

    @field_validator("artifact_id", "artifact_type", "summary")
    @classmethod
    def non_empty_strings(cls, value: str) -> str:
        if not value.strip():
            msg = "artifact_id, artifact_type, and summary cannot be empty"
            raise ValueError(msg)
        return value

    @model_validator(mode="after")
    def blocked_requires_detail(self) -> "LLMExplanationContext":
        if self.confidence_tier == ConfidenceTier.BLOCKED:
            if not self.failures and not self.warnings and not self.unsupported_claims:
                msg = "blocked tier requires failures, warnings, or unsupported_claims"
                raise ValueError(msg)
        return self


def context_from_trust_report(report: TrustReport) -> LLMExplanationContext:
    """Build explanation context from a TrustReport without LLM calls."""
    tier = ConfidenceTier(report.confidence_tier)
    tier_value = tier.value
    summary = f"Artifact {report.output_id} is {tier_value} for {report.output_type}."
    warnings = _dedupe_stable([*report.warnings, *report.diagnostics.warnings])

    return LLMExplanationContext(
        artifact_id=report.output_id,
        artifact_type=report.output_type,
        confidence_tier=tier,
        summary=summary,
        warnings=warnings,
        failures=list(report.diagnostics.failures),
        unsupported_claims=list(report.unsupported_claims),
        allowed_actions=allowed_actions_for_confidence_tier(tier),
        blocked_actions=blocked_actions_for_confidence_tier(tier),
        source_trace_uri=report.trace_uri,
    )


def _dedupe_stable(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            ordered.append(item)
    return ordered
