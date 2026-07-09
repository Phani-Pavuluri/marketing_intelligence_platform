"""Tests for GeoX panel_exp runtime-call contracts (Stage 3B)."""

from __future__ import annotations

import pytest

from mip.contracts import (
    CLAIM_AUTHORIZATION_OWNER,
    GeoXFixtureMaterializationResult,
    GeoXFixtureMaterializationStatus,
    GeoXMaterializedInputAvailability,
    GeoXPanelExpIntegrationStatus,
    GeoXPanelExpRuntimeCallIssueCode,
    GeoXPanelExpRuntimeCallMode,
    GeoXPanelExpRuntimeCallRequest,
    GeoXPanelExpRuntimeCallResult,
    GeoXPanelExpRuntimeCallStatus,
    GeoXPostTestExperimentType,
    GeoXPostTestSpendAdapterInputPlan,
    GeoXPostTestSpendEvidenceArtifact,
    GeoXTrustedReadoutSpendHandoffArtifact,
)

_REQUIRED_STATUSES = {
    GeoXPanelExpRuntimeCallStatus.READY,
    GeoXPanelExpRuntimeCallStatus.CALLED_PANEL_EXP_RUNTIME,
    GeoXPanelExpRuntimeCallStatus.BLOCKED_PANEL_EXP_IMPORT_FAILED,
    GeoXPanelExpRuntimeCallStatus.BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED,
    GeoXPanelExpRuntimeCallStatus.BLOCKED_MATERIALIZED_ASSIGNMENT_INPUT_REQUIRED,
    GeoXPanelExpRuntimeCallStatus.BLOCKED_POST_TEST_SPEND_INPUT_BUILD_FAILED,
    GeoXPanelExpRuntimeCallStatus.BLOCKED_PANEL_EXP_RUNTIME_FAILED,
    GeoXPanelExpRuntimeCallStatus.BLOCKED_TRUSTED_READOUT_HANDOFF_FAILED,
    GeoXPanelExpRuntimeCallStatus.BLOCKED_RUNTIME_CALL_NOT_ALLOWED,
    GeoXPanelExpRuntimeCallStatus.BLOCKED_FIXTURE_MATERIALIZATION_REQUIRED,
}

_FORBIDDEN_FIELD_FRAGMENTS = (
    "mip_computed_spend_delta",
    "mip_spend_delta",
    "delta_mu",
    "roi_value",
    "roas_value",
    "computed_lift",
    "lift_value",
)


def _adapter_plan(*, ready: bool = False) -> GeoXPostTestSpendAdapterInputPlan:
    return GeoXPostTestSpendAdapterInputPlan(
        request_id="plan-1",
        experiment_id="exp-1",
        integration_status=(
            GeoXPanelExpIntegrationStatus.READY_TO_BUILD_POST_TEST_SPEND_INPUT
            if ready
            else GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_CONFIRMED_SPEND_MAPPING
        ),
        materialized_input_availability=GeoXMaterializedInputAvailability(
            has_materialized_spend_df=True,
            has_materialized_assignment_df=True,
        ),
        experiment_type=GeoXPostTestExperimentType.HOLDOUT,
        source_lineage={
            "post_period_start": "2026-01-01",
            "post_period_end": "2026-01-31",
            "experiment_type": "holdout",
        },
        mapped_handoff_fields={
            "spend_date_column": "date",
            "spend_geo_column": "dma",
            "spend_amount_column": "spend",
        },
        ready_to_call_runtime=ready,
    )


def test_required_enums_exist() -> None:
    assert _REQUIRED_STATUSES.issubset(set(GeoXPanelExpRuntimeCallStatus))
    assert GeoXPanelExpRuntimeCallIssueCode.PANEL_EXP_IMPORT_FAILED in (
        GeoXPanelExpRuntimeCallIssueCode
    )
    assert GeoXPanelExpRuntimeCallMode.FIXTURE_ONLY in GeoXPanelExpRuntimeCallMode


def test_models_serialize() -> None:
    request = GeoXPanelExpRuntimeCallRequest(
        request_id="req-1",
        adapter_input_plan=_adapter_plan(),
    )
    payload = request.model_dump_json()
    assert "adapter_input_plan" in payload
    result = GeoXPanelExpRuntimeCallResult(
        request_id="req-1",
        status=GeoXPanelExpRuntimeCallStatus.BLOCKED_RUNTIME_CALL_NOT_ALLOWED,
    )
    assert result.runtime_called is False


def test_runtime_called_defaults_false() -> None:
    result = GeoXPanelExpRuntimeCallResult(
        request_id="req-1",
        status=GeoXPanelExpRuntimeCallStatus.BLOCKED_RUNTIME_CALL_NOT_ALLOWED,
    )
    assert result.runtime_called is False


def test_allow_runtime_call_false_cannot_mark_runtime_called() -> None:
    with pytest.raises(ValueError, match="runtime_called must be true"):
        GeoXPanelExpRuntimeCallResult(
            request_id="req-1",
            status=GeoXPanelExpRuntimeCallStatus.CALLED_PANEL_EXP_RUNTIME,
            runtime_called=False,
        )


def test_evidence_artifact_uses_package_labeled_fields() -> None:
    artifact = GeoXPostTestSpendEvidenceArtifact(
        artifact_id="artifact-1",
        experiment_id="exp-1",
        readiness_status="READY",
        package_output_summary={"package_computed_spend_delta": 749.0},
    )
    assert artifact.package_output_summary["package_computed_spend_delta"] == 749.0
    assert "spend_delta" not in artifact.model_dump()


def test_claim_authorization_owner_delegated() -> None:
    artifact = GeoXPostTestSpendEvidenceArtifact(
        artifact_id="artifact-1",
        experiment_id="exp-1",
        readiness_status="READY",
    )
    handoff = GeoXTrustedReadoutSpendHandoffArtifact(
        artifact_id="handoff-1",
        experiment_id="exp-1",
    )
    assert artifact.claim_authorization_owner == CLAIM_AUTHORIZATION_OWNER
    assert handoff.claim_authorization_owner == CLAIM_AUTHORIZATION_OWNER


def test_contracts_do_not_expose_mip_computed_metric_fields() -> None:
    for model in (
        GeoXPanelExpRuntimeCallRequest,
        GeoXPanelExpRuntimeCallResult,
        GeoXPostTestSpendEvidenceArtifact,
        GeoXTrustedReadoutSpendHandoffArtifact,
    ):
        schema = model.model_json_schema()
        blob = str(schema).lower()
        for fragment in _FORBIDDEN_FIELD_FRAGMENTS:
            assert fragment not in blob


def test_contracts_exported_from_mip_contracts() -> None:
    from mip import contracts

    assert hasattr(contracts, "GeoXPanelExpRuntimeCallRequest")
    assert hasattr(contracts, "GeoXPanelExpRuntimeCallResult")
    assert hasattr(contracts, "GeoXPanelExpRuntimeCallStatus")


def test_fixture_result_optional_on_request() -> None:
    request = GeoXPanelExpRuntimeCallRequest(
        request_id="req-1",
        adapter_input_plan=_adapter_plan(),
        fixture_materialization_result=GeoXFixtureMaterializationResult(
            request_id="fixture-1",
            status=GeoXFixtureMaterializationStatus.MATERIALIZED,
        ),
    )
    assert request.fixture_materialization_result is not None
