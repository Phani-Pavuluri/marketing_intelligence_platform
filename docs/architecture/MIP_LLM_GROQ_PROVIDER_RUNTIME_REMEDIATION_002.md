# Groq Provider Runtime Remediation 002

`GROQ_PROVIDER_RUNTIME_REMEDIATED_002`

The ambiguous exact readiness probes are now handled by the typed deterministic
`readiness_probe` route before provider invocation. This avoids the recorded
short-input server-side `json_validate_failed` without weakening
`conversational_provider_wire_v3`. Analytical short inputs remain on the Groq
conversation path. Targeted verification passed: `test` was not invoked and
MMM, GeoX, and measurement invoked Groq without fallback. Phase F remains
paused. Next: `MIP_LLM_GROQ_LIVE_PROVIDER_AND_PUBLIC_DEMO_ACCEPTANCE_003`.
