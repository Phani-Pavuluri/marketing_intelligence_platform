# Groq Live Provider and Public Demo Acceptance 002

## Verdict

`GROQ_LIVE_ACCEPTANCE_002_BLOCKED_BY_PROVIDER_FAILURE`

The automated baseline passed, but the mandatory live regression cannot meet its
zero-fallback requirement. `acceptance_2a_test` reached Groq and failed at
`full_wire_schema_parse` with sanitized provider category `invalid_request` and
safe code `json_validate_failed`; deterministic fallback was used. This is not
a rate-limit result. No raw prompt, output, provider response, transcript, or
credential was retained.

Four subsequent distinct mandatory calls were observed without retrying the
failed case: MMM, GeoX, data-needs, and help. Three parsed and mapped without
fallback; their detailed sanitized evidence is archived. The failed mandatory
turn is sufficient to prevent live acceptance, public-demo promotion, local or
public-browser certification, and Phase F resumption. The task's remaining live
budget was deliberately not spent after this conclusive gate failure.

`conversational_provider_wire_v3`, MIP-authored current-turn references,
conditional comparison behavior, and all action and claim guards are unchanged.

Next artifact: `MIP_LLM_GROQ_PROVIDER_RUNTIME_REMEDIATION_002`.
