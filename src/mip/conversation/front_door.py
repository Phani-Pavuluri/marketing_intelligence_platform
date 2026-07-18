"""LLM-first read-only front door with governed fallback and no execution."""
# ruff: noqa
# mypy: ignore-errors
from __future__ import annotations
from pydantic import BaseModel, Field
from mip.contracts.conversation import DeterministicConversationRoute, ProviderDisclosure, ResponseContract, TurnDecision, InteractionMode, GroundingRequirements, GroundingSource, TurnClaimPolicy, FallbackPolicy, FallbackRoute
from mip.control_plane.dialogue_router import DialogueRouter
from mip.control_plane.workspace import InMemoryWorkspace
from mip.knowledge import build_platform_truth_snapshot
from mip.knowledge.retrieval import DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER, KnowledgeRetrievalQuery
from mip.conversation.provider import ConversationalLLMProvider, ConfiguredProvider, FakeConversationalProvider, LLMConversationRequest, ProviderError, ProviderUnavailableError
from mip.conversation.provider_config import ProviderConfig
from mip.conversation.provider_wire import ProviderWireSchemaError, map_groq_wire_to_internal

class ConversationalTurnOutput(BaseModel):
    turn_decision: TurnDecision
    answer: str
    governed_action_proposal: object | None = None
    clarification_questions: tuple[str, ...] = ()
    suggested_navigation: object | None = None
    source_document_ids: tuple[str, ...] = ()
    platform_truth_references: tuple[str, ...] = ()
    provider_disclosure: ProviderDisclosure

class ConversationalFrontDoor:
    def __init__(self, provider: ConversationalLLMProvider | None = None, config: ProviderConfig | None = None):
        self.config = config or ProviderConfig.from_environment()
        self.provider = provider or (ConfiguredProvider(self.config) if self.config.enabled else None)
    def handle(self, text: str, *, workspace: InMemoryWorkspace, context_terms: tuple[str, ...] = ()) -> ConversationalTurnOutput:
        if self._deterministic_route(text) is DeterministicConversationRoute.READINESS_PROBE:
            return self._readiness_response()
        truth = build_platform_truth_snapshot()
        query = KnowledgeRetrievalQuery(query_id="front-door", query_text=text, interaction_mode=InteractionMode.GENERAL_EXPLANATION, conversation_context_terms=context_terms)
        retrieval = DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER.retrieve(query)
        disclosure = ProviderDisclosure(invocation_status="not_invoked")
        if self.provider:
            try:
                request = LLMConversationRequest(prompt=self._prompt(text, retrieval, truth), config=self.config)
                response = self.provider.generate(request)
                output = response.output
                if response.disclosure.provider_id == "groq":
                    output = map_groq_wire_to_internal(output, allowed_source_ids={h.passage.document_id for h in retrieval.hits}, allowed_truth_ids=set(truth.source_references))
                decision = self._decision(output, retrieval, response.disclosure)
                return ConversationalTurnOutput(turn_decision=decision, answer=str(output.get("answer", "")), source_document_ids=tuple(h.passage.document_id for h in retrieval.hits), platform_truth_references=truth.source_references, provider_disclosure=response.disclosure)
            except ProviderWireSchemaError as exc:
                disclosure = ProviderDisclosure(invocation_status="fallback_used", fallback_used=True, execution_disclosure="Deterministic fallback", provider_id=getattr(self.provider, "provider_id", None), provider_error_category="wire_mapping_failure", failed_compatibility_stage="wire_to_domain_mapping", fallback_reason=str(exc))
            except ProviderError as exc:
                disclosure = ProviderDisclosure(invocation_status="fallback_used", fallback_used=True, execution_disclosure="Deterministic fallback", provider_id=getattr(self.provider, "provider_id", None), provider_error_category=exc.category, http_status_class=exc.http_status_class, safe_provider_error_code=exc.safe_provider_error_code, safe_request_id=exc.safe_request_id, failed_compatibility_stage=exc.failed_compatibility_stage, validation_field_path=exc.validation_field_path, validation_error_type=exc.validation_error_type, expected_schema_field_category=exc.expected_schema_field_category, validation_error_count=exc.validation_error_count, fallback_reason="provider_error")
            except Exception:
                disclosure = ProviderDisclosure(invocation_status="fallback_used", fallback_used=True, execution_disclosure="Deterministic fallback", provider_id=getattr(self.provider, "provider_id", None), provider_error_category="unknown_provider_failure", failed_compatibility_stage="front_door", fallback_reason="provider_error")
        return self._fallback(text, workspace, disclosure)
    def _deterministic_route(self, text: str) -> DeterministicConversationRoute | None:
        if " ".join(text.casefold().split()) in {"test", "ping", "health check", "are you working"}:
            return DeterministicConversationRoute.READINESS_PROBE
        return None
    def _readiness_response(self) -> ConversationalTurnOutput:
        disclosure = ProviderDisclosure(invocation_status="not_invoked", execution_disclosure="Deterministic readiness probe")
        decision = TurnDecision(interaction_mode=InteractionMode.GENERAL_EXPLANATION, topic="platform", domain="platform", user_goal="readiness_probe", requires_general_knowledge=True, grounding_requirements=GroundingRequirements(sources=[GroundingSource.GENERAL_MODEL_KNOWLEDGE]), claim_policy=TurnClaimPolicy.for_mode(InteractionMode.GENERAL_EXPLANATION), fallback_policy=FallbackPolicy(fallback_order=[FallbackRoute.DETERMINISTIC_ROUTER, FallbackRoute.SAFE_CLARIFICATION], allow_deterministic_router=True, allow_safe_clarification=True), provider_disclosure=disclosure, confidence=1.0)
        return ConversationalTurnOutput(turn_decision=decision, answer="MIP is ready to explain measurement, planning, experimentation, and learning boundaries.", provider_disclosure=disclosure)
    def _prompt(self, text, retrieval, truth):
        return f"MIP read-only front door. Answer naturally; never execute. User: {text}\nSources: {[h.passage.content for h in retrieval.hits[:3]]}\nTruth: {truth.global_blocked_claims}"
    def _decision(self, output, retrieval, disclosure):
        mode = InteractionMode(output.get("interaction_mode", "general_explanation"))
        return TurnDecision(interaction_mode=mode, topic=str(output.get("topic", "measurement")), domain=str(output.get("domain", "platform")), user_goal=str(output.get("user_goal", "explain")), requires_platform_truth=mode == InteractionMode.PLATFORM_GUIDANCE, grounding_requirements=GroundingRequirements(sources=[GroundingSource.APPROVED_KNOWLEDGE_RETRIEVAL]), claim_policy=TurnClaimPolicy.for_mode(mode), fallback_policy=FallbackPolicy(fallback_order=[FallbackRoute.DETERMINISTIC_ROUTER, FallbackRoute.SAFE_CLARIFICATION], allow_deterministic_router=True, allow_safe_clarification=True), provider_disclosure=disclosure, confidence=0.8)
    def _fallback(self, text, workspace, disclosure):
        lowered = text.casefold()
        if "mmm" in lowered: answer = DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER.retrieve(KnowledgeRetrievalQuery(query_id="fallback", query_text=text, interaction_mode=InteractionMode.GENERAL_EXPLANATION)).hits[0].passage.content
        elif "geox" in lowered: answer = DEFAULT_APPROVED_KNOWLEDGE_RETRIEVER.retrieve(KnowledgeRetrievalQuery(query_id="fallback", query_text=text, interaction_mode=InteractionMode.GENERAL_EXPLANATION)).hits[0].passage.content
        elif "help" in lowered: answer = "MIP helps teams Measure, Plan, Experiment, and Learn while showing what is ready, uncertain, or blocked."
        else: answer = "I can explain MIP concepts, data requirements, MMM, GeoX, planning, and trust."
        decision = TurnDecision(interaction_mode=InteractionMode.GENERAL_EXPLANATION, topic="measurement", domain="platform", user_goal="explain", requires_general_knowledge=True, grounding_requirements=GroundingRequirements(sources=[GroundingSource.GENERAL_MODEL_KNOWLEDGE]), claim_policy=TurnClaimPolicy.for_mode(InteractionMode.GENERAL_EXPLANATION), fallback_policy=FallbackPolicy(fallback_order=[FallbackRoute.DETERMINISTIC_ROUTER, FallbackRoute.SAFE_CLARIFICATION], allow_deterministic_router=True, allow_safe_clarification=True), provider_disclosure=disclosure, confidence=0.5)
        return ConversationalTurnOutput(turn_decision=decision, answer=answer, provider_disclosure=disclosure)
