# MIP LLM Groq Provider Wire-Schema Remediation 001

## Verdict

`GROQ_PROVIDER_WIRE_SCHEMA_BLOCKED_BY_MAPPING_SEMANTICS`

This supersedes the generic transport recommendation: plain transport, authentication, minimal structured parsing, reduced structured parsing, and the new direct full-wire parse pass.

## Design and evidence

The previous provider schema was `OpenAIConversationalTurnWireOutput` (1,903 bytes): three object nodes, two open objects, 13 optional/defaulted properties, two arbitrary dictionaries, and two nullable constructs. The new Groq-only `conversational_provider_wire_v2` has required closed objects, bounded strings/lists, nullable-required values, and typed `InputItem` lists instead of arbitrary dictionaries. A recursive local linter rejects open objects, missing required fields, arbitrary dictionaries, unsupported keywords, and oversized schemas.

The direct live full-wire parse succeeds. The wire-to-domain mapper validates interaction modes, capability IDs, workflow nodes, retrieval IDs, platform-truth references, artifact context, execution claims, and recommendation/treatment-assignment claims before the existing internal decision is constructed.

Four bounded live front-door turns did not satisfy the completion gate: two failed with sanitized `invalid_request`; two reached the strict mapper and failed with `wire_mapping_failure`. No raw provider body, prompt, output, transcript, or credential was retained. The schema is therefore not promoted to public acceptance and Phase F remains paused.

## Retained boundaries

No tools, provider-managed state, direct execution, artifact resolution, MMM/GeoX execution, recommendations, or deployment configuration was added. OpenAI retains its existing wire schema and behavior. The Streamlit enum/session-state fix remains unchanged.

## Next artifact

`MIP_LLM_PROVIDER_WIRE_TO_DOMAIN_MAPPING_REMEDIATION_001`
