# LLM Conversational Front Door Evaluation Gate 001

## Audit result

The deterministic architecture and fake-provider pipeline are testable, but the full release gate is blocked. CF4 contains `ConversationalLLMProvider`, `FakeConversationalProvider`, and `ConfiguredProvider` in `src/mip/conversation/provider.py`; `ConfiguredProvider.generate()` deliberately raises `ProviderUnavailableError`. No concrete SDK-backed live adapter, provider SDK dependency, model invocation, or live credential path exists.

Verdict: `LLM_FRONT_DOOR_BLOCKED_BY_MISSING_CONCRETE_PROVIDER`

Recommended next artifact: `MIP_LLM_CONCRETE_PROVIDER_ADAPTER_REMEDIATION_001`.

## Evaluation coverage

The committed corpus at `tests/fixtures/conversation/llm_front_door_evaluation_v1.json` covers the observed transcript, definitions, platform guidance, follow-ups, governed actions, artifact boundaries, provider failures, and typed UI actions. The evaluation test verifies mandatory regression coverage and provider-disabled fallback without invoking a provider. Naturalness and live conversational quality are intentionally not inferred from fake-provider output.

Automated control-plane and fake-provider checks remain valid: they cover deterministic fallback, approved retrieval/truth integration, structured disclosure, and no-execution boundaries. Live-provider quality, latency, factuality under a real model, and browser acceptance remain pending because no concrete provider adapter and no interactive browser evidence are available.

## Release thresholds and status

Hard safety requirements remain unchanged: no direct execution, no artifact or numerical claims without grounding, no recommendations, no treatment assignment, no secret or private reasoning storage, and deterministic typed actions. Automated Docker validation is the release evidence for these controls; it cannot establish live naturalness or visual acceptance. The requirements marker remains `-e .`.

Phase F remains paused. A concrete provider remediation must first add a bounded SDK-backed adapter, invocation-time credential lookup, typed timeout/error handling, structured-output parsing, and provider smoke evidence. Then run this gate again, followed by the separate live-provider/browser acceptance artifact.

## Current provider-evaluation status

The follow-on [Groq live/public-demo acceptance record](MIP_LLM_GROQ_LIVE_PROVIDER_AND_PUBLIC_DEMO_ACCEPTANCE_001.md) is `GROQ_LIVE_ACCEPTANCE_BLOCKED_BY_PROVIDER_FAILURE`. This historical fake-provider gate remains valid; it does not certify live quality or public deployment.

The subsequent [provider compatibility remediation](MIP_LLM_GROQ_PROVIDER_COMPATIBILITY_REMEDIATION_001.md) is `GROQ_PROVIDER_BLOCKED_BY_STRUCTURED_OUTPUT_COMPATIBILITY`; its sanitized error observability is retained, but it does not satisfy this live-quality gate.
