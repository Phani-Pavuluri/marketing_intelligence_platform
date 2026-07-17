# Groq Comparison Structured-Output Remediation 001

## Verdict

`GROQ_COMPARISON_STRUCTURED_OUTPUT_REMEDIATED`

The Groq-only strict-output instruction now explicitly requires every
`conversational_provider_wire_v3` field, explicit `null` for absent nullable
fields, and arrays (including `[]`) for every list field. It names `comparison`
as the only interaction mode for conditional MMM-versus-GeoX guidance. It also
states that capability/workflow IDs are proposals only and that retrieval,
source, platform-truth, and reference IDs must not be emitted by the provider.
The OpenAI instruction and request path are unchanged.

The earlier `comparison_3_choice` failure was a Groq front-door strict-output
rejection at `full_wire_schema_parse`, with safe code `json_validate_failed`.
The provider did not expose a typed field path, error type, or error count for
that earlier server-side rejection; no rejected value, response body, prompt, or
transcript was retained. Narrow safe observability now records typed Pydantic
field path, error type, field category, and count when such local structured
validation data exists, while retaining no rejected input values.

The deterministic regression suite covers the complete v3 instruction and
shape, valid conditional comparisons, missing required fields, invalid enums,
invalid nullability, malformed `InputItem` lists, multiple errors, sanitized
diagnostics, invalid governance proposals, and the claim guards. Conditional
MMM/GeoX guidance remains allowed; unconditional recommendations, execution,
budget allocation, and treatment assignment remain blocked.

## Targeted live verification

One continuous three-turn Groq conversation completed within the task's
three-call budget. Every turn was accepted, parsed, mapped, and claim-guarded
without fallback. The final comparison response met the deterministic
conditional-guidance check. Only sanitized status metadata is recorded in the
associated evidence artifact.

`conversational_provider_wire_v3`, deterministic current-turn retrieval/truth
reference injection, the conditional-comparison mapper normalization, and all
capability, workflow, artifact, action, execution, recommendation,
treatment-assignment, and claim guards remain intact. Public-demo acceptance is
still pending and Phase F remains paused.

Next artifact: `MIP_LLM_GROQ_LIVE_PROVIDER_AND_PUBLIC_DEMO_ACCEPTANCE_002`.
