"""Tests for Planning/MMM trusted input and model-run eligibility contracts."""

from __future__ import annotations

from mip.contracts import (
    FORBIDDEN_PLANNING_MMM_MODEL_RUN_ELIGIBILITY_RESULT_FIELD_NAMES,
    RECOMMENDED_NEXT_MMM_RUNTIME_ADAPTER_CONTRACT_ARTIFACT,
    PlanningMMMModelRunEligibilityDecision,
    PlanningMMMModelRunEligibilityIssueCode,
    PlanningMMMModelRunEligibilityRequest,
    PlanningMMMModelRunEligibilityResult,
    PlanningMMMModelRunEligibilityStatus,
    PlanningMMMTrustedInputComponentStatus,
    PlanningMMMTrustedInputPackage,
    PlanningMMMTrustedInputStatus,
)

_FORBIDDEN_TOP_LEVEL = (
    "spend_delta",
    "delta_mu",
    "roi",
    "roas",
    "incrementality",
    "optimal_budget",
    "marginal_roi",
    "recommendation",
    "budget_recommendation",
)


def test_required_enums_exist() -> None:
    assert PlanningMMMTrustedInputStatus.TRUSTED_INPUT_READY in PlanningMMMTrustedInputStatus
    assert (
        PlanningMMMModelRunEligibilityStatus.ELIGIBLE_TO_REQUEST_MODEL_RUN
        in PlanningMMMModelRunEligibilityStatus
    )
    assert PlanningMMMModelRunEligibilityDecision.REQUEST_NEW_MODEL_RUN in (
        PlanningMMMModelRunEligibilityDecision
    )
    assert PlanningMMMModelRunEligibilityIssueCode.NO_MODEL_EXECUTION in (
        PlanningMMMModelRunEligibilityIssueCode
    )


def test_models_serialize() -> None:
    request = PlanningMMMModelRunEligibilityRequest(request_id="elig-req-1")
    assert request.model_config_present is False
    assert request.require_calibration_readiness is False
    assert request.allow_existing_model_reuse is True
    result = PlanningMMMModelRunEligibilityResult(
        request_id="elig-req-1",
        trusted_input_status=PlanningMMMTrustedInputStatus.TRUSTED_INPUT_BLOCKED,
        eligibility_status=PlanningMMMModelRunEligibilityStatus.BLOCKED,
        decision=PlanningMMMModelRunEligibilityDecision.BLOCK,
    )
    assert result.eligible_to_request_model_run is False


def test_trusted_input_package_preserves_metadata_refs() -> None:
    package = PlanningMMMTrustedInputPackage(
        package_id="pkg-1",
        request_id="elig-req-2",
        data_readiness_request_id="data-1",
        data_readiness_status="report_adapted",
        calibration_readiness_request_id="cal-1",
        calibration_readiness_status="ready_for_model_calibration",
        existing_model_availability_request_id="model-1",
        existing_model_availability_status="usable_existing_model",
        existing_model_selected_id="mmm-1",
        model_config_id="cfg-1",
        model_config_present=True,
        required_component_statuses=[
            PlanningMMMTrustedInputComponentStatus(
                component_name="historical_spend",
                present=True,
                required=True,
                status="present",
            )
        ],
        lineage={"stage": "eligibility"},
    )
    assert package.data_readiness_request_id == "data-1"
    assert package.existing_model_selected_id == "mmm-1"
    assert package.lineage["stage"] == "eligibility"


def test_no_forbidden_top_level_fields() -> None:
    for field_name in PlanningMMMModelRunEligibilityResult.model_fields:
        assert field_name not in _FORBIDDEN_TOP_LEVEL
    assert "roi" in FORBIDDEN_PLANNING_MMM_MODEL_RUN_ELIGIBILITY_RESULT_FIELD_NAMES


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_MMM_RUNTIME_ADAPTER_CONTRACT_ARTIFACT == (
        "MIP_MMM_RUNTIME_ADAPTER_CONTRACT_001"
    )
