# Conversational Turn Mode and LLM Handoff Contracts 001

CF1 adds provider-free, versioned contracts under `mip.contracts.conversation`. `InteractionMode` distinguishes general explanation, platform guidance, artifact interpretation, governed action, typed UI action, and unsupported turns. `TurnDecision` expresses interpretation and grounding; it is never authorization. `GovernedActionProposal` is an untrusted, identifier-based proposal with no executor or callable payload.

`GroundingRequirements` enumerates permitted evidence sources. `TurnClaimPolicy` is fail-closed by mode: platform status requires structured truth, artifact numbers require provenance and verification, execution claims require execution results, and recommendations remain blocked. `FallbackPolicy` makes deterministic routing, safe clarification, provider-unavailable, and unsupported responses explicit. `ProviderDisclosure` records only audited provider/configuration identity and user-visible disclosure; it stores no API keys, private chain-of-thought, or hidden reasoning.

The contracts compose with `IntentEnvelope` for compatibility, the capability registry and workflow graph for later deterministic validation, `EvidencePacket` for artifact grounding, `ResponseContract` for user-visible output, and `VerificationResult` for claim checks. No provider, prompt, retrieval, artifact-resolution, or execution runtime is added. The requirements marker remains `-e .`.

Focused tests cover all modes, fail-closed invariants, proposals, claim policy, disclosure, deterministic round trips, and optional-engine-free imports. The next artifact is `MIP_CONVERSATIONAL_PLATFORM_TRUTH_AND_KNOWLEDGE_CORPUS_001`.
