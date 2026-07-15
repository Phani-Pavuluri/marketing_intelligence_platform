# Conversational Control Plane Typed Contracts 001

Phase A adds provider-free, versioned Pydantic contracts under `src/mip/contracts/conversation/` and exports them from the package initializer. All use `conversation_control_plane_v1`, strict extra-field rejection, deterministic JSON serialization, and fail-closed invariants.

Contracts are `InteractionEvent`, `IntentEnvelope`, `WorkspaceContext`, `DialogueState`, `RequirementGap`, `CapabilityDescriptor`, `WorkflowNode`, `ResolvedArtifact`, `EvidencePacket`, `ResponseContract`, and `VerificationResult`, with supporting conflict, validation, and navigation types. Events use stable IDs and timezone-aware timestamps; intents bound confidence and clarification; workspace state keeps conversation identity separate from view and has no default dataset; dialogue states reject contradictions; capabilities and workflow nodes are declarative; fixture artifacts cannot claim production evidence; packets and responses remain valid without retrieval or LLM context; verification states require their supporting evidence.

Existing CalibrationSignal, DecisionSurface, RecommendationContract, TrustReport, MMM, and GeoX artifacts are composed by references and strings rather than duplicated. Optional engines are not imported. Builders in focused tests cover empty/sample/upload workspaces, MMM intents, pending dialogue, complete/incomplete gaps, fixture and upload artifacts, evidence packets, blocked responses, and verification outcomes.

This change deliberately does not implement routing, reducers, registry runtime, workflow execution, artifact resolution, response generation, claim verification runtime, upload processing, RAG, LLM execution, or domain engines. Phase B can begin because the contract surface and serialization invariants are explicit.

Next artifact: `MIP_CONVERSATIONAL_CONTROL_PLANE_CAPABILITY_REGISTRY_001`.
