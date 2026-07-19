import copy
import json

from mip.contracts.geox_envelope_consumer import REQUIRED_FIELDS
from mip.runtime.geox_envelope_consumer_runtime import (
    GeoXEnvelopeConsumerRuntimeInput,
    consume_geox_artifact_envelope_for_mip,
    serialize_geox_envelope_consumer_runtime_output,
)


def fixture(
    kind: str = "assignment_candidate",
    status: str = "diagnostic_context_only",
) -> dict[str, object]:
    e: dict[str, object] = {
        f: (
            []
            if f in {"blocked_reasons", "warnings", "upstream_artifacts"}
            else {}
            if f == "provenance"
            else "x"
        )
        for f in REQUIRED_FIELDS
    }
    e.update(
        artifact_kind=kind,
        artifact_id="fixture-1",
        authorization_status="not_authorized",
        mip_consumption_status=status,
        downstream_eligibility="explain_only",
    )
    return e


def test_runtime_boundaries_and_non_mutation() -> None:
    e = fixture()
    original = copy.deepcopy(e)
    out = consume_geox_artifact_envelope_for_mip(
        GeoXEnvelopeConsumerRuntimeInput(e, request_id="r")
    )
    assert (
        out.runtime_status == "accepted_diagnostic_context"
        and not out.ready_for_decision_surface
        and e == original
    )
    assert json.dumps(serialize_geox_envelope_consumer_runtime_output(out), sort_keys=True)


def test_blocked_export_and_unsafe_inputs() -> None:
    e = fixture("calibration_signal_candidate", "blocked")
    e["authorization_status"] = "authorized"
    out = consume_geox_artifact_envelope_for_mip(GeoXEnvelopeConsumerRuntimeInput(e))
    assert not out.accepted and not out.ready_for_calibration_signal_export
    assert "cannot export CalibrationSignal" in out.cannot_say


def test_missing_and_unknown_are_rejected_or_blocked() -> None:
    assert (
        consume_geox_artifact_envelope_for_mip(GeoXEnvelopeConsumerRuntimeInput({})).runtime_status
        == "rejected_invalid_envelope"
    )
    assert (
        consume_geox_artifact_envelope_for_mip(
            GeoXEnvelopeConsumerRuntimeInput(fixture("unknown"))
        ).runtime_status
        == "blocked"
    )
