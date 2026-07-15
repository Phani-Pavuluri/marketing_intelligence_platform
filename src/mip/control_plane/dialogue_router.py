"""Provider-free dialogue-aware deterministic routing."""
# ruff: noqa: E501
from __future__ import annotations

import re

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.conversation import (
    CapabilityDescriptor,
    DialogueResolutionStatus,
    DialogueState,
    EventType,
    IntentEnvelope,
    InteractionEvent,
    InterpretationSource,
    WorkspaceContext,
)
from mip.control_plane.capability_registry import (
    DEFAULT_CAPABILITY_REGISTRY,
    CapabilityRegistry,
    UnknownCapabilityError,
)


class RoutingError(ValueError):
    """Raised when a deterministic route cannot be validated."""


class RoutingResult(ContractBaseModel):
    intent_envelope: IntentEnvelope
    updated_dialogue_state: DialogueState
    known_input_updates: dict[str, str] = Field(default_factory=dict)
    missing_input_updates: list[str] = Field(default_factory=list)
    confirmed_input_updates: dict[str, str] = Field(default_factory=dict)
    inferred_input_updates: dict[str, str] = Field(default_factory=dict)
    selected_capability: CapabilityDescriptor | None = None
    clarification_question: str | None = None
    clarification_targets: list[str] = Field(default_factory=list)
    routing_rule_id: str


_MONTH = r"(January|February|March|April|May|June|July|August|September|October|November|December)"
_DATE_RANGE = re.compile(rf"(?P<start>{_MONTH}[ ]+[0-9]{{4}})[ ]+through[ ]+(?P<end>{_MONTH}[ ]+[0-9]{{4}})", re.I)
_SLOT_WORDS = {
    "paid conversions": "paid_conversions",
    "conversions": "conversions",
    "revenue": "revenue",
    "sales": "sales",
    "weekly": "weekly",
    "daily": "daily",
    "monthly": "monthly",
}


def _normalize(value: str) -> str:
    return " ".join(value.casefold().strip().split())


def _extract_slots(text: str) -> tuple[dict[str, str], dict[str, str]]:
    normalized = _normalize(text)
    detected: dict[str, str] = {}
    inferred: dict[str, str] = {}
    if "spend" in normalized:
        detected["spend"] = "detected"
    if "channel" in normalized:
        detected["channel"] = "detected"
    if "geo" in normalized or "geography" in normalized or "market" in normalized:
        detected["geography"] = "detected"
    for phrase, slot in sorted(_SLOT_WORDS.items(), key=lambda item: -len(item[0])):
        if phrase == "conversions" and "paid conversions" in normalized:
            continue
        if phrase in normalized:
            detected[{"weekly": "time_frequency", "daily": "time_frequency", "monthly": "time_frequency"}.get(slot, "primary_kpi")] = slot
    match = _DATE_RANGE.search(text)
    if match:
        detected["history_start"] = re.sub(r"s+", "-", match.group("start").lower())
        detected["history_end"] = re.sub(r"s+", "-", match.group("end").lower())
    if "promotion" in normalized or "holiday" in normalized or "control" in normalized:
        detected["controls"] = "detected"
    if "next quarter" in normalized or "next-quarter" in normalized:
        detected["planning_horizon"] = "next_quarter"
    if "start" in normalized and ("experiment" in normalized or "test" in normalized):
        inferred["experiment_question"] = "experiment timing requested"
    return detected, inferred


class DialogueRouter:
    """Deterministic interpretation; selection never authorizes execution."""

    def route(
        self,
        *,
        event: InteractionEvent,
        workspace: WorkspaceContext,
        dialogue: DialogueState,
        registry: CapabilityRegistry = DEFAULT_CAPABILITY_REGISTRY,
    ) -> RoutingResult:
        if event.workspace_id != workspace.workspace_id or event.conversation_id != workspace.conversation_id:
            raise RoutingError("event identity does not match workspace")
        typed = self._typed_route(event, registry)
        if typed is not None:
            return typed
        if event.event_type != EventType.USER_MESSAGE:
            return self._unsupported("unsupported_event", workspace, dialogue, registry)
        text = str(event.payload.get("text", ""))
        if not text.strip():
            raise RoutingError("user_message requires text")
        if dialogue.resolution_status in {DialogueResolutionStatus.PENDING.value, DialogueResolutionStatus.PARTIALLY_RESOLVED.value}:
            result = self._resolve_pending(text, workspace, dialogue, registry)
            if result is not None:
                return result
        return self._language_route(text, workspace, dialogue, registry)

    def _typed_route(self, event: InteractionEvent, registry: CapabilityRegistry) -> RoutingResult | None:
        mapping = {
            EventType.SAMPLE_USE_CASE_SELECTED: ("platform", "sample_use_case_request", "sample.use_case.activate"),
            EventType.ANALYZE_MY_DATA_SELECTED: ("data", "analyze_my_data_request", "uploaded_data.intake"),
            EventType.ARTIFACT_OPENED: ("artifact", "open_artifact", "artifact.open"),
            EventType.REPORT_OPENED: ("report", "open_report", "report.open"),
            EventType.DASHBOARD_FILTER_CHANGED: ("dashboard", "update_dashboard_context", "dashboard.context.update"),
        }
        if event.event_type not in mapping:
            return None
        domain, intent, capability_id = mapping[event.event_type]
        capability = self._capability(capability_id, registry)
        envelope = IntentEnvelope(domain=domain, user_goal=intent, intent=intent, candidate_capability_id=capability_id, confidence=1.0, interpretation_source=InterpretationSource.TYPED_UI_ACTION)
        return RoutingResult(intent_envelope=envelope, updated_dialogue_state=DialogueState(), selected_capability=capability, routing_rule_id=f"typed_ui.{event.event_type}")

    def _language_route(self, text: str, workspace: WorkspaceContext, dialogue: DialogueState, registry: CapabilityRegistry) -> RoutingResult:
        normalized = _normalize(text)
        slots, inferred = _extract_slots(text)
        if any(term in normalized for term in ("uncertain", "uncertainty", "interval wide", "confidence interval")):
            if workspace.active_artifact_id or workspace.active_domain == "mmm":
                return self._result("mmm", "explain_channel_uncertainty", "mmm.channel_uncertainty.explain", "rule.mmm.uncertainty", workspace, dialogue, registry)
            return self._clarification("mmm", "explain_channel_uncertainty", "Which MMM result or interval should I explain?", ["active_artifact_id"], workspace, dialogue, registry)
        if normalized in {"hello", "hi", "hey", "test", "are you working"}:
            return self._result("platform", "platform_capabilities", "platform.onboarding", "rule.platform.smoke", workspace, dialogue, registry)
        if "mmm" in normalized or "mix model" in normalized or "marketing mix" in normalized:
            if any(term in normalized for term in ("what data", "what files", "which columns", "data needed", "files required", "provide")):
                return self._result("mmm", "mmm_data_requirements", "mmm.intake.requirements", "rule.mmm.requirements", workspace, dialogue, registry)
            if any(term in normalized for term in ("ready", "enough", "build", "historical spend")):
                missing = [field for field in ("primary_kpi", "time_frequency", "history_start", "history_end") if field not in slots and field not in workspace.known_inputs]
                return self._result("mmm", "assess_mmm_readiness", "mmm.intake.readiness", "rule.mmm.readiness", workspace, dialogue, registry, slots, inferred, missing)
            if any(term in normalized for term in ("run", "fit", "model")):
                return self._result("mmm", "request_mmm_run", "mmm.run.request", "rule.mmm.run", workspace, dialogue, registry, slots, inferred)
        if "geox" in normalized or "geo experiment" in normalized or "geo test" in normalized:
            if any(term in normalized for term in ("what data", "what files", "requirements")):
                return self._result("geox", "geox_data_requirements", "geox.intake.requirements", "rule.geox.requirements", workspace, dialogue, registry)
            if any(term in normalized for term in ("design", "create", "request", "start")):
                return self._result("geox", "create_geox_design_request", "geox.design_request.create", "rule.geox.design", workspace, dialogue, registry, slots, inferred)
            if "market" in normalized and ("which" in normalized or "select" in normalized):
                return self._clarification("geox", "geox_data_requirements", "Which governed GeoX owner or constraint should determine markets?", ["assignment_constraints"], workspace, dialogue, registry)
        if "mmm or geox" in normalized or "mix model or an experiment" in normalized or "instead of mmm" in normalized:
            return self._clarification("platform", "trust_and_uncertainty", "Are you deciding between historical measurement and an incrementality experiment?", ["business_goal"], workspace, dialogue, registry)
        if any(term in normalized for term in ("budget", "optimize", "spend next quarter", "move budget")):
            capability_id = "planning.simulation.request" if any(term in normalized for term in ("simulate", "optimize", "move budget")) else "planning.recommendation.explain_blocked"
            intent = "request_plan_simulation" if capability_id.endswith("simulation.request") else "explain_recommendation_blocked"
            return self._result("planning", intent, capability_id, "rule.planning.blocked", workspace, dialogue, registry, slots, inferred)
        if "trust" in normalized or "confidence" in normalized:
            if workspace.active_artifact_id:
                return self._result("mmm", "explain_channel_uncertainty", "mmm.channel_uncertainty.explain", "rule.context.trust", workspace, dialogue, registry)
            return self._clarification("platform", "trust_and_uncertainty", "Which result or analysis do you want to assess?", ["active_artifact_id"], workspace, dialogue, registry)
        if "data" in normalized and any(term in normalized for term in ("need", "required", "provide")):
            return self._result("data", "general_data_requirements", "data.requirements.explain", "rule.data.requirements", workspace, dialogue, registry)
        return self._unsupported("rule.unsupported", workspace, dialogue, registry)

    def _resolve_pending(self, text: str, workspace: WorkspaceContext, dialogue: DialogueState, registry: CapabilityRegistry) -> RoutingResult | None:
        slots, inferred = _extract_slots(text)
        if not slots and not inferred:
            if "forget" in _normalize(text) or "cancel" in _normalize(text):
                updated = dialogue.model_copy(update={"resolution_status": DialogueResolutionStatus.CANCELLED.value, "clarification_targets": [], "missing_fields": []})
                return self._result(dialogue.selected_domain or "unknown", "cancel_pending", None, "dialogue.cancel", workspace, updated, registry)
            return None
        remaining = [field for field in dialogue.missing_fields if field not in slots]
        updated_status = DialogueResolutionStatus.RESOLVED.value if not remaining else DialogueResolutionStatus.PARTIALLY_RESOLVED.value
        updated = dialogue.model_copy(update={"resolution_status": updated_status, "missing_fields": remaining, "clarification_targets": remaining})
        capability_id = dialogue.pending_capability_id
        if not capability_id:
            return self._unsupported("dialogue.no_capability", workspace, updated, registry)
        return self._result(dialogue.selected_domain or "mmm", dialogue.pending_intent or "assess_mmm_readiness", capability_id, "dialogue.resolve_pending", workspace, updated, registry, slots, inferred, remaining)

    def _result(self, domain: str, intent: str, capability_id: str | None, rule: str, workspace: WorkspaceContext, dialogue: DialogueState, registry: CapabilityRegistry, slots: dict[str, str] | None = None, inferred: dict[str, str] | None = None, missing: list[str] | None = None) -> RoutingResult:
        capability = self._capability(capability_id, registry) if capability_id else None
        slots, inferred = slots or {}, inferred or {}
        envelope = IntentEnvelope(domain=domain, user_goal=intent, intent=intent, candidate_capability_id=capability_id, known_inputs={**workspace.known_inputs, **slots}, missing_or_unknown_inputs=missing or [], confidence=0.95 if capability else 0.1, interpretation_source=InterpretationSource.PENDING_CLARIFICATION if rule.startswith("dialogue.") else InterpretationSource.DETERMINISTIC_RULE)
        updated = dialogue
        if missing:
            updated = dialogue.model_copy(update={"pending_intent": intent, "pending_capability_id": capability_id, "selected_domain": domain, "missing_fields": missing, "clarification_targets": missing, "resolution_status": DialogueResolutionStatus.PENDING.value})
        return RoutingResult(intent_envelope=envelope, updated_dialogue_state=updated, known_input_updates=slots, confirmed_input_updates=slots, inferred_input_updates=inferred, missing_input_updates=missing or [], selected_capability=capability, clarification_targets=missing or [], routing_rule_id=rule)

    def _clarification(self, domain: str, intent: str, question: str, targets: list[str], workspace: WorkspaceContext, dialogue: DialogueState, registry: CapabilityRegistry) -> RoutingResult:
        capability_id = {"trust_and_uncertainty": "mmm.channel_uncertainty.explain", "geox_data_requirements": "geox.intake.requirements"}.get(intent)
        updated = dialogue.model_copy(update={"pending_intent": intent, "pending_capability_id": capability_id, "selected_domain": domain, "missing_fields": targets, "clarification_targets": targets, "clarification_question": question, "resolution_status": DialogueResolutionStatus.PENDING.value})
        result = self._result(domain, intent, capability_id, "clarification.required", workspace, updated, registry, missing=targets)
        return result.model_copy(update={"clarification_question": question})

    def _unsupported(self, rule: str, workspace: WorkspaceContext, dialogue: DialogueState, registry: CapabilityRegistry) -> RoutingResult:
        envelope = IntentEnvelope(domain="unknown", user_goal="unsupported", intent="unsupported", confidence=0.0, clarification_required=True, clarification_targets=["supported_goal"], interpretation_source=InterpretationSource.DETERMINISTIC_RULE)
        updated = dialogue.model_copy(update={"resolution_status": DialogueResolutionStatus.PENDING.value, "missing_fields": ["supported_goal"], "clarification_targets": ["supported_goal"], "clarification_question": "What measurement, data, experiment, or planning question should I help with?"})
        return RoutingResult(intent_envelope=envelope, updated_dialogue_state=updated, clarification_question=updated.clarification_question, clarification_targets=["supported_goal"], routing_rule_id=rule)

    @staticmethod
    def _capability(capability_id: str | None, registry: CapabilityRegistry) -> CapabilityDescriptor:
        if not capability_id:
            raise RoutingError("route has no capability")
        try:
            return registry.get(capability_id)
        except UnknownCapabilityError as exc:
            raise RoutingError(str(exc)) from exc
