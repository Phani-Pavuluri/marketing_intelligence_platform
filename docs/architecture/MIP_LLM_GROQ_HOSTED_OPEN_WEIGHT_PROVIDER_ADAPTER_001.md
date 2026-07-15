# Groq Hosted Open-weight Provider Adapter 001

MIP now supports a second concrete provider through `GroqResponsesProvider`, reusing the official OpenAI SDK with Groq’s OpenAI-compatible Responses endpoint (`https://api.groq.com/openai/v1`). The adapter uses the existing strict Pydantic wire model and provider protocol. It deliberately omits `store`, provider-managed response state, tools, function calling, streaming, background mode, and reasoning configuration.

Groq is selected only when `MIP_LLM_ENABLED=true`, `MIP_LLM_PROVIDER=groq`, an explicit model is configured, and `GROQ_API_KEY` is present. The strict model catalog permits only `openai/gpt-oss-20b` and `openai/gpt-oss-120b`; unknown models fail closed. The smaller 20B model is the documented public-demo candidate, but no model is silently selected.

OpenAI remains unchanged. Provider failures are sanitized and preserve deterministic fallback; no cross-provider automatic failover is added. Groq output remains subject to MIP source, platform-truth, capability, workflow, artifact, claim, and release-gate validation. No execution, tools, recommendations, or provider-managed conversation state are introduced. Live Groq and browser acceptance remain pending.
