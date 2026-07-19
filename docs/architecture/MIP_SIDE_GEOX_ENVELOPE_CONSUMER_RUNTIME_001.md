# MIP-side GeoX envelope consumer runtime

## Metadata
Task `MIP_SIDE_GEOX_ENVELOPE_CONSUMER_RUNTIME_001`; non-production MIP runtime wrapper.

## Purpose and dependencies
Wraps `MIP_SIDE_GEOX_ENVELOPE_CONSUMER_CONTRACT_001` for incoming dictionaries. It does not call or modify GeoX.

## Public API and status semantics
`GeoXEnvelopeConsumerRuntimeInput`, `GeoXEnvelopeConsumerRuntimeOutput`, `consume_geox_artifact_envelope_for_mip`, and `serialize_geox_envelope_consumer_runtime_output` are provided. Runtime statuses are accepted diagnostic, accepted answerability, blocked, and rejected invalid envelope.

## Behavior and safety
Required fields are validated; blocked reasons and warnings are preserved; unknown kinds, production authorization, production consumption, and unsafe downstream eligibility are blocked. `can_say` reports only receipt and safe context. `cannot_say` always dominates unsafe claims, including causal lift/readout, assignment, exports, TrustReport, DecisionSurface, RecommendationContract, LLM decisioning, and budget optimization.

## Serialization and readiness
Output is deterministic JSON-safe data with stable scalar/list fields and no source mutation. All production, export, decisioning, selector/router, multicell, and agent readiness flags are false.

## Tests and validation
Focused tests cover diagnostic, blocked/export, rejection, serialization, and non-mutation behavior. Full integration and production runtime are explicitly out of scope.

## Final verdict
MIP-side consumer runtime added with no GeoX call and no authorization. **PROCEED_TO_MIP_SIDE_GEOX_ENVELOPE_CONSUMER_APPLICATION_CHECKPOINT**.

## Recommended next artifact
`MIP_SIDE_GEOX_ENVELOPE_CONSUMER_APPLICATION_CHECKPOINT_001`.
