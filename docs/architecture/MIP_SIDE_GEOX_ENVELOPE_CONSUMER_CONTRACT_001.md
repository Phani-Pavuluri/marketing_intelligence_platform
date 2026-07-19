# MIP-side GeoX envelope consumer contract

This contract defines fixture/non-production consumption of GeoX artifact envelopes. MIP validates the complete envelope shape, recognizes the governed artifact kinds, preserves blocked reasons and warnings, and classifies accepted context as `diagnostic_context_only` or `answerability_context_only`.

Unknown kinds, missing required fields, unsupported statuses, or unauthorized production claims are rejected or blocked. The consumer may state only diagnostic or answerability context. It must not authorize assignment, causal readout, CalibrationSignal or ExperimentEvidence export, production TrustReport assembly, DecisionSurface, RecommendationContract, LLM decisioning, or budget optimization.

The lightweight API is in `src/mip/contracts/geox_envelope_consumer.py`; it does not call GeoX, persist artifacts, execute jobs, or integrate production runtime. The future sequence is validate envelope → normalize context → preserve blockers → classify safe context → return blocked diagnostics.
