from mip.contracts.geox_envelope_consumer import *


def envelope(kind="readout_packet", status="diagnostic_context_only"):
    return {field: [] if field in {"blocked_reasons", "warnings", "upstream_artifacts"} else {} if field == "provenance" else "x" for field in REQUIRED_FIELDS} | {"artifact_kind": kind, "artifact_id": "a1", "authorization_status": "not_authorized", "mip_consumption_status": status}


def test_diagnostic_and_answerability_are_accepted():
    assert evaluate_geox_envelope_for_mip_consumption(GeoXEnvelopeConsumerInput(envelope())).decision.value == "diagnostic_context_only"
    assert evaluate_geox_envelope_for_mip_consumption(GeoXEnvelopeConsumerInput(envelope(status="answerability_context_only"))).decision.value == "answerability_context_only"


def test_blocked_reason_preserved_and_exports_blocked():
    out = evaluate_geox_envelope_for_mip_consumption(GeoXEnvelopeConsumerInput(envelope("calibration_signal_candidate", "blocked") | {"authorization_status": "blocked", "blocked_reasons": ["authorization_missing"]}))
    assert "authorization_missing" in out.blocked_reasons
    assert "CalibrationSignal export" in out.cannot_say


def test_unknown_kind_and_missing_fields_rejected():
    assert evaluate_geox_envelope_for_mip_consumption(GeoXEnvelopeConsumerInput(envelope("unknown"))).consumer_status == GeoXEnvelopeConsumerStatus.BLOCKED
    assert evaluate_geox_envelope_for_mip_consumption(GeoXEnvelopeConsumerInput({})).decision == GeoXEnvelopeConsumerDecision.REJECT
