# LLM Read-only Conversational Front Door 001

CF4 adds `mip.conversation`, a provider-neutral front-door seam. It assembles bounded user text, approved retrieval passages, and structured platform truth, then invokes a configured provider or falls back safely. `FakeConversationalProvider` supports deterministic tests; configuration is disabled unless environment settings are complete. The concrete configured seam fails closed when no supported SDK adapter is available, so imports and deployment remain provider-independent.

Provider output is parsed into the existing `TurnDecision` boundary. Answers are user-visible text only; proposals remain separate and are never authorization or execution payloads. Typed UI events remain deterministic. Artifact interpretation, uploaded-file analysis, model fitting, GeoX execution, simulation, optimization, recommendations, and arbitrary tools remain blocked. Provider disclosures contain configuration identity and user-visible fallback state, never credentials or private reasoning.

Retrieval uses `DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER`; platform status uses `PlatformTruthSnapshot`. These sources remain separate. The deterministic fallback provides concise explanations for MMM, GeoX, help, and general supported MIP topics without the robotic legacy clarification. Browser review and live-provider smoke testing remain pending when unavailable. Next artifact: `MIP_LLM_CONVERSATIONAL_FRONT_DOOR_EVALUATION_GATE_001`.

## Runtime-status update

The runtime can select Groq only through explicit configuration, but [live/public-demo acceptance](MIP_LLM_GROQ_LIVE_PROVIDER_AND_PUBLIC_DEMO_ACCEPTANCE_001.md) is currently `GROQ_LIVE_ACCEPTANCE_BLOCKED_BY_PROVIDER_FAILURE`. The deterministic router remains the active fallback; no public-provider promotion is authorized.
