"""Tests for GeoX readout result ingestion workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.geox_panel_exp_runtime_call import (
    CLAIM_AUTHORIZATION_OWNER,
    GeoXPanelExpRuntimeCallResult,
    GeoXPanelExpRuntimeCallStatus,
    GeoXPostTestSpendEvidenceArtifact,
    GeoXTrustedReadoutSpendHandoffArtifact,
)
from mip.contracts.geox_readout_result_ingestion import (
    GeoXReadoutClaimReadiness,
    GeoXReadoutExplanationAudience,
    GeoXReadoutResultIngestionRequest,
    GeoXReadoutResultIssueCode,
    GeoXReadoutResultStatus,
)
from mip.workflows.geox_readout_result_ingestion import (
    ingest_geox_readout_result_for_explanation,
)

_INGESTION_SOURCE = Path("src/mip/workflows/geox_readout_result_ingestion.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/geox_readout_result_ingestion.py")

_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi_value", "roas_value")


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
    spend_warnings: list[str] | None = None,
    blocked_efficiency: list[str] | None = None,
    claim_owner: str = CLAIM_AUTHORIZATION_OWNER,
    readiness_summary: dict[str, str | bool] | None = None,
) -> GeoXTrustedReadoutSpendHandoffArtifact:
    return GeoXTrustedReadoutSpendHandoffArtifact(
        artifact_id=f"handoff:{experiment_id}",
        experiment_id=experiment_id,
        spend_readiness_summary=readiness_summary
        or {"readiness_status": "READY", "spend_delta_ready": True},
        blocked_efficiency_metrics=blocked_efficiency or [],
        spend_warnings=spend_warnings or [],
        package_handoff_summary={
            "roi_claim_authorization_status": roi_status,
            "roas": "NOT_COMPUTED",
            "profit_roi": "NOT_COMPUTED",
        },
        claim_authorization_owner=claim_owner,
    )


def _request(
    *,
    evidence: GeoXPostTestSpendEvidenceArtifact | None,
    handoff: GeoXTrustedReadoutSpendHandoffArtifact | None,
    audience: GeoXReadoutExplanationAudience = GeoXReadoutExplanationAudience.TECHNICAL,
) -> GeoXReadoutResultIngestionRequest:
    return GeoXReadoutResultIngestionRequest(
        request_id="ingest-1",
        evidence_artifact=evidence,
        trusted_handoff_artifact=handoff,
        audience=audience,
    )


def test_missing_evidence_artifact_blocked() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(evidence=None, handoff=_handoff())
    )
    assert result.status == GeoXReadoutResultStatus.BLOCKED_MISSING_EVIDENCE_ARTIFACT
    assert GeoXReadoutResultIssueCode.MISSING_EVIDENCE_ARTIFACT in result.issues
    assert result.result_envelope is None


def test_missing_trusted_handoff_artifact_blocked() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(evidence=_evidence(), handoff=None)
    )
    assert result.status == GeoXReadoutResultStatus.BLOCKED_MISSING_TRUSTED_HANDOFF_ARTIFACT
    assert result.result_envelope is None


def test_ready_package_result_explained() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(evidence=_evidence(readiness_status="READY"), handoff=_handoff())
    )
    assert result.status == GeoXReadoutResultStatus.EXPLAINED_READY_PACKAGE_RESULT
    envelope = result.result_envelope
    assert envelope is not None
    assert envelope.package_readiness_status == "READY"
    assert "not a business recommendation" in envelope.explanation.next_action.lower()
    assert envelope.claim_readiness == GeoXReadoutClaimReadiness.READY_FOR_TRUST_REPORT_REVIEW


def test_blocked_package_result_explained() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(
            evidence=_evidence(
                readiness_status="BLOCKED_MISSING_SPEND_BASELINE",
                blocking_reasons=["missing_baseline_or_counterfactual_spend"],
            ),
            handoff=_handoff(
                readiness_summary={
                    "readiness_status": "BLOCKED_MISSING_SPEND_BASELINE",
                    "spend_delta_ready": False,
                }
            ),
        )
    )
    assert result.status == GeoXReadoutResultStatus.EXPLAINED_BLOCKED_PACKAGE_RESULT
    envelope = result.result_envelope
    assert envelope is not None
    assert "baseline" in envelope.explanation.blocker_explanation.lower() or (
        "baseline" in envelope.explanation.next_action.lower()
    )


def test_diagnostic_only_package_result_explained() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(
            evidence=_evidence(readiness_status="PARTIAL_DIAGNOSTIC_ONLY"),
            handoff=_handoff(
                readiness_summary={
                    "readiness_status": "PARTIAL_DIAGNOSTIC_ONLY",
                    "spend_delta_ready": False,
                }
            ),
        )
    )
    assert result.status == GeoXReadoutResultStatus.EXPLAINED_DIAGNOSTIC_ONLY_PACKAGE_RESULT
    envelope = result.result_envelope
    assert envelope is not None
    assert "diagnostic" in envelope.explanation.summary.lower()


def test_package_warnings_preserved_and_explained() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(
            evidence=_evidence(warnings=["spend_window_partial"]),
            handoff=_handoff(spend_warnings=["currency_inferred"]),
        )
    )
    envelope = result.result_envelope
    assert envelope is not None
    assert "spend_window_partial" in envelope.package_warnings
    assert "currency_inferred" in envelope.package_warnings
    assert GeoXReadoutResultIssueCode.PACKAGE_WARNINGS_PRESENT in result.issues


def test_package_computed_spend_delta_preserved_in_summary_only() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(
            evidence=_evidence(
                package_output_summary={
                    "readiness_status": "READY",
                    "package_computed_spend_delta": 749.0,
                }
            ),
            handoff=_handoff(),
        )
    )
    envelope = result.result_envelope
    assert envelope is not None
    assert envelope.package_output_summary["package_computed_spend_delta"] == 749.0
    payload = envelope.model_dump()
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in payload
    assert GeoXReadoutResultIssueCode.SPEND_DELTA_PACKAGE_COMPUTED in result.issues


def test_claim_authorization_delegated_not_authorized_by_mip() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(evidence=_evidence(), handoff=_handoff(roi_status="NOT_EVALUATED"))
    )
    envelope = result.result_envelope
    assert envelope is not None
    assert envelope.claim_authorization_owner == CLAIM_AUTHORIZATION_OWNER
    assert envelope.claim_readiness in {
        GeoXReadoutClaimReadiness.READY_FOR_TRUST_REPORT_REVIEW,
        GeoXReadoutClaimReadiness.DELEGATED_TO_CLAIM_AUTHORIZATION_RUNTIME,
    }
    assert GeoXReadoutResultIssueCode.CLAIM_AUTHORIZATION_NOT_EVALUATED in result.issues
    assert "does not authorize" in envelope.explanation.claim_boundary_explanation.lower()


def test_business_audience_plain_language() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(
            evidence=_evidence(),
            handoff=_handoff(),
            audience=GeoXReadoutExplanationAudience.BUSINESS,
        )
    )
    envelope = result.result_envelope
    assert envelope is not None
    assert envelope.explanation.summary == envelope.explanation.business_safe_summary
    assert "no business claim is authorized" in envelope.explanation.business_safe_summary.lower()


def test_governance_audience_includes_boundary_notes() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(
            evidence=_evidence(),
            handoff=_handoff(),
            audience=GeoXReadoutExplanationAudience.GOVERNANCE,
        )
    )
    envelope = result.result_envelope
    assert envelope is not None
    notes = " ".join(envelope.explanation.governance_notes).lower()
    assert "trustreport" in notes
    assert "decisionsurface" in notes
    assert "recommendationcontract" in notes


def test_malformed_artifact_blocked() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(
            evidence=_evidence(readiness_status="", experiment_id=""),
            handoff=_handoff(experiment_id=""),
        )
    )
    assert result.status == GeoXReadoutResultStatus.BLOCKED_MALFORMED_PACKAGE_ARTIFACT
    assert result.result_envelope is None


def test_stage_3b_runtime_call_result_compatibility() -> None:
    runtime_result = GeoXPanelExpRuntimeCallResult(
        request_id="runtime-1",
        status=GeoXPanelExpRuntimeCallStatus.CALLED_PANEL_EXP_RUNTIME,
        runtime_called=True,
        post_test_spend_evidence_artifact=_evidence(
            package_output_summary={
                "readiness_status": "READY",
                "package_computed_spend_delta": 749.0,
            }
        ),
        trusted_readout_spend_handoff_artifact=_handoff(
            blocked_efficiency=["EFFICIENCY_METRICS_NOT_READY"]
        ),
    )
    result = ingest_geox_readout_result_for_explanation(
        GeoXReadoutResultIngestionRequest(
            request_id="stage-3b-compat",
            evidence_artifact=runtime_result.post_test_spend_evidence_artifact,
            trusted_handoff_artifact=runtime_result.trusted_readout_spend_handoff_artifact,
        )
    )
    assert result.status == GeoXReadoutResultStatus.EXPLAINED_READY_PACKAGE_RESULT
    assert result.result_envelope is not None
    assert result.registered_artifact_ref_optional is None


def test_no_panel_exp_import_in_ingestion_module() -> None:
    for path in (_INGESTION_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "import panel_exp" not in source
        assert "from panel_exp" not in source


def test_no_metric_recomputation_fields() -> None:
    result = ingest_geox_readout_result_for_explanation(
        _request(evidence=_evidence(), handoff=_handoff())
    )
    payload = result.model_dump_json().lower()
    assert "mip_computed" not in payload
    assert "computed_lift" not in payload
    assert GeoXReadoutResultIssueCode.ROI_ROAS_NOT_COMPUTED_IN_MIP in result.issues
    assert GeoXReadoutResultIssueCode.LIFT_NOT_COMPUTED_IN_MIP in result.issues
