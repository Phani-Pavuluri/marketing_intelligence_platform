"""MIP-side, non-production consumer contract for GeoX envelopes."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any


class GeoXEnvelopeConsumerStatus(str, Enum):
    ACCEPTED = "accepted"
    BLOCKED = "blocked"
    REJECTED = "rejected"


class GeoXEnvelopeConsumerDecision(str, Enum):
    DIAGNOSTIC_CONTEXT_ONLY = "diagnostic_context_only"
    ANSWERABILITY_CONTEXT_ONLY = "answerability_context_only"
    BLOCKED = "blocked"
    REJECT = "reject"


REQUIRED_FIELDS = (
    "envelope_version",
    "artifact_kind",
    "artifact_id",
    "artifact_uri",
    "source_system",
    "source_repo",
    "source_commit",
    "created_at",
    "run_id",
    "experiment_id",
    "request_id",
    "input_data_fingerprint",
    "method_family",
    "instrument_id",
    "estimand",
    "kpi",
    "geo_scope",
    "time_window",
    "assignment_scope",
    "diagnostic_status",
    "method_readiness_status",
    "release_gate_status",
    "authorization_status",
    "blocked_reasons",
    "warnings",
    "upstream_artifacts",
    "downstream_eligibility",
    "mip_consumption_status",
    "provenance",
    "schema_hash",
)
KNOWN_KINDS = {
    "geox_request",
    "geox_result",
    "assignment_candidate",
    "assignment_manifest",
    "run_manifest",
    "readout_packet",
    "failure_packet",
    "post_test_spend_evidence",
    "trusted_readout_spend_handoff",
    "experiment_evidence_candidate",
    "calibration_signal_candidate",
}


@dataclass(frozen=True)
class GeoXEnvelopeConsumerInput:
    envelope: Mapping[str, Any]
    source: str = "geox"


@dataclass(frozen=True)
class GeoXEnvelopeConsumerOutput:
    accepted: bool
    consumer_status: GeoXEnvelopeConsumerStatus
    decision: GeoXEnvelopeConsumerDecision
    artifact_kind: str
    artifact_id: str
    mip_consumption_status: str
    authorization_status: str
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    can_say: tuple[str, ...]
    cannot_say: tuple[str, ...]
    normalized: dict[str, Any]


_CANNOT_SAY = (
    "production authorization",
    "causal readout",
    "CalibrationSignal export",
    "MIP ExperimentEvidence export",
    "production TrustReport",
    "DecisionSurface",
    "RecommendationContract",
    "LLM decisioning",
    "budget optimization",
)


def evaluate_geox_envelope_for_mip_consumption(
    inp: GeoXEnvelopeConsumerInput,
) -> GeoXEnvelopeConsumerOutput:
    env = dict(inp.envelope)
    missing = tuple(field for field in REQUIRED_FIELDS if field not in env)
    kind = str(env.get("artifact_kind", "unknown"))
    artifact_id = str(env.get("artifact_id", ""))
    blocked = tuple(str(x) for x in env.get("blocked_reasons", ()))
    warnings = tuple(str(x) for x in env.get("warnings", ()))
    auth = str(env.get("authorization_status", "unknown"))
    consumption = str(env.get("mip_consumption_status", "unknown"))
    if missing:
        return GeoXEnvelopeConsumerOutput(
            False,
            GeoXEnvelopeConsumerStatus.REJECTED,
            GeoXEnvelopeConsumerDecision.REJECT,
            kind,
            artifact_id,
            consumption,
            auth,
            blocked + ("missing_required_fields:" + ",".join(missing),),
            warnings,
            (),
            _CANNOT_SAY,
            {"source": inp.source, "valid": False, "missing_fields": list(missing)},
        )
    if (
        kind not in KNOWN_KINDS
        or auth not in {"not_authorized", "blocked"}
        or consumption not in {"diagnostic_context_only", "answerability_context_only", "blocked"}
    ):
        reason = (
            "unknown_artifact_kind"
            if kind not in KNOWN_KINDS
            else "unsupported_authorization_or_consumption_status"
        )
        return GeoXEnvelopeConsumerOutput(
            False,
            GeoXEnvelopeConsumerStatus.BLOCKED,
            GeoXEnvelopeConsumerDecision.BLOCKED,
            kind,
            artifact_id,
            consumption,
            auth,
            blocked + (reason,),
            warnings,
            (),
            _CANNOT_SAY,
            {"source": inp.source, "valid": False, "blocked": True},
        )
    decision = GeoXEnvelopeConsumerDecision(consumption)
    can_say = (
        ("diagnostic context",)
        if decision == GeoXEnvelopeConsumerDecision.DIAGNOSTIC_CONTEXT_ONLY
        else ("answerability context",)
        if decision == GeoXEnvelopeConsumerDecision.ANSWERABILITY_CONTEXT_ONLY
        else ()
    )
    return GeoXEnvelopeConsumerOutput(
        True,
        GeoXEnvelopeConsumerStatus.ACCEPTED
        if decision != GeoXEnvelopeConsumerDecision.BLOCKED
        else GeoXEnvelopeConsumerStatus.BLOCKED,
        decision,
        kind,
        artifact_id,
        consumption,
        auth,
        blocked,
        warnings,
        can_say,
        _CANNOT_SAY,
        {"source": inp.source, "valid": True, "artifact_kind": kind, "artifact_id": artifact_id},
    )


def serialize_geox_envelope_consumer_output(output: GeoXEnvelopeConsumerOutput) -> dict[str, Any]:
    return {
        "accepted": output.accepted,
        "consumer_status": output.consumer_status.value,
        "decision": output.decision.value,
        "artifact_kind": output.artifact_kind,
        "artifact_id": output.artifact_id,
        "mip_consumption_status": output.mip_consumption_status,
        "authorization_status": output.authorization_status,
        "blocked_reasons": list(output.blocked_reasons),
        "warnings": list(output.warnings),
        "can_say": list(output.can_say),
        "cannot_say": list(output.cannot_say),
        "normalized": dict(output.normalized),
    }
