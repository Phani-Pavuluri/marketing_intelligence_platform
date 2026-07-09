"""Tests for GeoX readout result ingestion contracts."""

from __future__ import annotations

from mip.contracts import (
    CLAIM_AUTHORIZATION_OWNER,
    GeoXPostTestSpendEvidenceArtifact,
    GeoXReadoutClaimReadiness,
    GeoXReadoutExplanationAudience,
    GeoXReadoutResultEnvelope,
    GeoXReadoutResultExplanation,
    GeoXReadoutResultIngestionRequest,
    GeoXReadoutResultIngestionResult,
    GeoXReadoutResultIssueCode,
    GeoXReadoutResultStatus,
    GeoXTrustedReadoutSpendHandoffArtifact,
)

_REQUIRED_STATUSES = {
    GeoXReadoutResultStatus.READY_FOR_EXPLANATION,
    GeoXReadoutResultStatus.EXPLAINED_READY_PACKAGE_RESULT,
    GeoXReadoutResultStatus.EXPLAINED_BLOCKED_PACKAGE_RESULT,
    GeoXReadoutResultStatus.EXPLAINED_DIAGNOSTIC_ONLY_PACKAGE_RESULT,
    GeoXReadoutResultStatus.BLOCKED_MISSING_EVIDENCE_ARTIFACT,
    GeoXReadoutResultStatus.BLOCKED_MISSING_TRUSTED_HANDOFF_ARTIFACT,
    GeoXReadoutResultStatus.BLOCKED_MALFORMED_PACKAGE_ARTIFACT,
    GeoXReadoutResultStatus.BLOCKED_CLAIM_AUTHORIZATION_NOT_EVALUATED,
}

_FORBIDDEN_TOP_LEVEL_FIELDS = (
    "spend_delta",
    "delta_mu",
    "lift",
    "roi",
    "roas",
)


def _evidence(
    *,
    readiness_status: str = "READY",
    blocking_reasons: list[str] | None = None,
    warnings: list[str] | None = None,
    package_output_summary: dict[str, str | float | int | bool | None] | None = None,
    experiment_id: str = "exp-1",
    claim_owner: str = CLAIM_AUTHORIZATION_OWNER,
) -> GeoXPostTestSpendEvidenceArtifact:
    return GeoXPostTestSpendEvidenceArtifact(
        artifact_id=f"evidence:{experiment_id}",
        experiment_id=experiment_id,
        readiness_status=readiness_status,
        blocking_reasons=blocking_reasons or [],
        warnings=warnings or [],
        package_output_summary=package_output_summary
        or {"readiness_status": readiness_status},
        claim_authorization_owner=claim_owner,
    )


def _handoff(
    *,
    experiment_id: str = "exp-1",
    roi_status: str = "NOT_EVALUATED",
    claim_owner: str = CLAIM_AUTHORIZATION_OWNER,
) -> GeoXTrustedReadoutSpendHandoffArtifact:
    return GeoXTrustedReadoutSpendHandoffArtifact(
        artifact_id=f"handoff:{experiment_id}",
        experiment_id=experiment_id,
        spend_readiness_summary={"readiness_status": "READY", "spend_delta_ready": True},
        package_handoff_summary={"roi_claim_authorization_status": roi_status},
        claim_authorization_owner=claim_owner,
    )


def test_required_enums_exist() -> None:
    assert _REQUIRED_STATUSES.issubset(set(GeoXReadoutResultStatus))
    assert GeoXReadoutResultIssueCode.MISSING_EVIDENCE_ARTIFACT in GeoXReadoutResultIssueCode
    assert GeoXReadoutExplanationAudience.BUSINESS in GeoXReadoutExplanationAudience
    assert GeoXReadoutClaimReadiness.NOT_AUTHORIZED in GeoXReadoutClaimReadiness


def test_models_serialize() -> None:
    request = GeoXReadoutResultIngestionRequest(
        request_id="req-1",
        evidence_artifact=_evidence(),
        trusted_handoff_artifact=_handoff(),
    )
    payload = request.model_dump_json()
    assert "evidence_artifact" in payload
    result = GeoXReadoutResultIngestionResult(
        request_id="req-1",
        status=GeoXReadoutResultStatus.BLOCKED_MISSING_EVIDENCE_ARTIFACT,
    )
    assert result.result_envelope is None


def test_envelope_no_top_level_metric_fields() -> None:
    schema = GeoXReadoutResultEnvelope.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL_FIELDS:
        assert field not in properties


def test_package_computed_spend_delta_allowed_in_summary_only() -> None:
    envelope = GeoXReadoutResultEnvelope(
        result_id="result-1",
        experiment_id="exp-1",
        status=GeoXReadoutResultStatus.EXPLAINED_READY_PACKAGE_RESULT,
        package_readiness_status="READY",
        package_output_summary={"package_computed_spend_delta": 749.0},
        claim_readiness=GeoXReadoutClaimReadiness.DELEGATED_TO_CLAIM_AUTHORIZATION_RUNTIME,
        explanation=_minimal_explanation(),
    )
    assert envelope.package_output_summary["package_computed_spend_delta"] == 749.0
    assert "spend_delta" not in envelope.model_dump()


def test_claim_readiness_not_authorized_by_default() -> None:
    envelope = GeoXReadoutResultEnvelope(
        result_id="result-1",
        experiment_id="exp-1",
        status=GeoXReadoutResultStatus.EXPLAINED_BLOCKED_PACKAGE_RESULT,
        package_readiness_status="BLOCKED_MISSING_SPEND_BASELINE",
        claim_readiness=GeoXReadoutClaimReadiness.NOT_AUTHORIZED,
        explanation=_minimal_explanation(),
    )
    assert envelope.claim_readiness != GeoXReadoutClaimReadiness.READY_FOR_DECISION_SURFACE_REVIEW
    payload = envelope.model_dump_json().lower()
    assert "authorized" in payload
    assert "mip_authorized" not in payload


def test_contracts_exported_from_mip_contracts() -> None:
    from mip import contracts

    assert hasattr(contracts, "GeoXReadoutResultIngestionRequest")
    assert hasattr(contracts, "GeoXReadoutResultEnvelope")
    assert hasattr(contracts, "GeoXReadoutResultStatus")


def _minimal_explanation() -> GeoXReadoutResultExplanation:
    return GeoXReadoutResultExplanation(
        summary="summary",
        readiness_explanation="ready",
        blocker_explanation="none",
        warning_explanation="none",
        claim_boundary_explanation="delegated",
        next_action="review",
        business_safe_summary="safe",
    )


def test_request_defaults() -> None:
    request = GeoXReadoutResultIngestionRequest(request_id="req-1")
    assert request.audience == GeoXReadoutExplanationAudience.TECHNICAL
    assert request.include_package_output_summary is True
