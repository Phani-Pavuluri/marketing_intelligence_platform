"""Narrow, non-production runtime wrapper for GeoX envelope consumption."""
from dataclasses import dataclass
from typing import Any, Mapping

from mip.contracts.geox_envelope_consumer import (
    GeoXEnvelopeConsumerDecision,
    GeoXEnvelopeConsumerInput,
    evaluate_geox_envelope_for_mip_consumption,
)


@dataclass(frozen=True)
class GeoXEnvelopeConsumerRuntimeInput:
    envelope: Mapping[str, Any]
    request_id: str | None = None
    user_intent: str | None = None
    strict: bool = True


@dataclass(frozen=True)
class GeoXEnvelopeConsumerRuntimeOutput:
    accepted: bool
    runtime_status: str
    consumer_status: str
    decision: str
    artifact_kind: str
    artifact_id: str
    request_id: str | None
    user_intent: str | None
    mip_consumption_status: str
    authorization_status: str
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    can_say: tuple[str, ...]
    cannot_say: tuple[str, ...]
    normalized: dict[str, Any]
    ready_for_trust_report_production: bool
    ready_for_experiment_evidence_export: bool
    ready_for_calibration_signal_export: bool
    ready_for_decision_surface: bool
    ready_for_recommendation_contract: bool
    ready_for_llm_decisioning: bool
    ready_for_budget_optimization: bool
    validation_errors: tuple[str, ...]


_UNSAFE = ("cannot claim production causal lift", "cannot choose treatment/control markets", "cannot authorize causal readout", "cannot export CalibrationSignal", "cannot export MIP ExperimentEvidence", "cannot assemble production TrustReport", "cannot create DecisionSurface", "cannot create RecommendationContract", "cannot provide budget optimization or spend reallocation recommendation", "cannot use this as LLM decisioning authority")


def consume_geox_artifact_envelope_for_mip(inp: GeoXEnvelopeConsumerRuntimeInput) -> GeoXEnvelopeConsumerRuntimeOutput:
    envelope = dict(inp.envelope)
    unsafe = []
    if envelope.get("authorization_status") in {"authorized", "production_authorized"}:
        unsafe.append("production_authorization_not_consumable")
    if envelope.get("mip_consumption_status") not in {None, "diagnostic_context_only", "answerability_context_only", "blocked"}:
        unsafe.append("production_consumption_status_not_consumable")
    if envelope.get("downstream_eligibility") in {"decision_surface", "recommendation_contract", "budget_optimization", "production"}:
        unsafe.append("downstream_production_eligibility_not_consumable")
    contract = evaluate_geox_envelope_for_mip_consumption(GeoXEnvelopeConsumerInput(envelope))
    blocked = tuple(contract.blocked_reasons) + tuple(unsafe)
    validation_errors = tuple(unsafe)
    if unsafe:
        status, decision, accepted = "blocked", "blocked", False
    elif contract.decision == GeoXEnvelopeConsumerDecision.REJECT:
        status, decision, accepted = "rejected_invalid_envelope", "reject", False
        validation_errors = tuple(contract.blocked_reasons)
    elif contract.decision == GeoXEnvelopeConsumerDecision.BLOCKED:
        status, decision, accepted = "blocked", "blocked", True
    elif contract.decision == GeoXEnvelopeConsumerDecision.DIAGNOSTIC_CONTEXT_ONLY:
        status, decision, accepted = "accepted_diagnostic_context", contract.decision.value, True
    else:
        status, decision, accepted = "accepted_answerability_context", contract.decision.value, True
    can_say = tuple(contract.can_say) + (("artifact envelope was received",) if not validation_errors else ())
    return GeoXEnvelopeConsumerRuntimeOutput(accepted, status, contract.consumer_status.value, decision, contract.artifact_kind, contract.artifact_id, inp.request_id, inp.user_intent, contract.mip_consumption_status, contract.authorization_status, blocked, contract.warnings, can_say, tuple(dict.fromkeys(contract.cannot_say + _UNSAFE)), {**contract.normalized, "strict": inp.strict}, False, False, False, False, False, False, False, validation_errors)


def serialize_geox_envelope_consumer_runtime_output(output: GeoXEnvelopeConsumerRuntimeOutput) -> dict[str, Any]:
    return {"accepted": output.accepted, "runtime_status": output.runtime_status, "consumer_status": output.consumer_status, "decision": output.decision, "artifact_kind": output.artifact_kind, "artifact_id": output.artifact_id, "request_id": output.request_id, "user_intent": output.user_intent, "mip_consumption_status": output.mip_consumption_status, "authorization_status": output.authorization_status, "blocked_reasons": list(output.blocked_reasons), "warnings": list(output.warnings), "can_say": list(output.can_say), "cannot_say": list(output.cannot_say), "normalized": dict(output.normalized), "ready_for_trust_report_production": False, "ready_for_experiment_evidence_export": False, "ready_for_calibration_signal_export": False, "ready_for_decision_surface": False, "ready_for_recommendation_contract": False, "ready_for_llm_decisioning": False, "ready_for_budget_optimization": False, "validation_errors": list(output.validation_errors)}
