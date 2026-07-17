# MIP LLM Groq Provider Compatibility Remediation 001

## Verdict

`GROQ_PROVIDER_BLOCKED_BY_STRUCTURED_OUTPUT_COMPATIBILITY`

The original acceptance evidence at commit `87b37d6` recorded 11 deliberate live calls with a 100% fallback rate. The original record had no sanitized provider error category. This remediation isolated the failure without changing the acceptance verdict or rerunning its 11 calls.

## Compatibility ladder

The first plain request from the restricted sandbox produced `APIConnectionError`; the same non-sensitive Probe 1 with network permission completed successfully. Authentication, model access, the fixed Groq base URL, and plain Responses transport therefore pass.

Minimal strict Pydantic parsing and a reduced MIP response schema also completed. The full committed `OpenAIConversationalTurnWireOutput` was rejected as HTTP `4xx` `invalid_request` at `full_wire_schema_parse`. A final sanitized diagnostic identified schema `additionalProperties`/object and response-format constraints; it retained no raw provider body, prompt, or response.

The offline schema audit found a closed root schema of 1,903 bytes, plus provider-sensitive nullable fields and unbounded `known_inputs`/`inferred_inputs` dictionaries. A closed, fully-required Groq-only schema candidate was tried and rejected as well, so it was removed rather than retained as an unverified workaround. The full front-door probe could not run because Probe 5 failed, and all three permitted post-remediation verification calls fell back with `invalid_request`.

## Retained remediation

`ProviderError` now preserves only safe diagnostic metadata: provider error category, HTTP status class, provider-safe error code, request ID, and failed compatibility stage. The front door carries those fields into its fallback disclosure without storing an exception body, prompt, answer, key, or hidden reasoning. Error mapping covers authentication, permission, model access, rate limit, invalid request, timeout, connection, server failure, and unknown failure.

`ConfiguredProvider` now reports its configured provider ID, fixing fallback disclosure of Groq as OpenAI. The isolated Streamlit enum/session-state crash fix remains in place. OpenAI request construction and parsing remain unchanged.

## Boundaries

No artifact resolution, upload processing, MMM/GeoX execution, simulation, optimization, recommendation, provider-managed state, or workflow authorization was added. The deterministic fallback remains active. Phase F remains paused. The public Streamlit authentication redirect is a separate deployment-access issue, not a provider-compatibility result.

## Next artifact

`MIP_LLM_GROQ_PROVIDER_TRANSPORT_REMEDIATION_001`
