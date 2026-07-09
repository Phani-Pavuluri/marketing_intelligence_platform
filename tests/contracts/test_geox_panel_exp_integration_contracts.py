"""Tests for GeoX panel_exp integration boundary contracts (Stage 3A)."""

from __future__ import annotations

import pytest

from mip.contracts import (
    GEOX_HANDOFF_HELPER_CALLABLE,
    GEOX_INPUT_MODEL,
    GEOX_INTEGRATION_CALLABLES,
    GEOX_INTEGRATION_COMMIT,
    GEOX_INTEGRATION_MODULE_PATH,
    GEOX_OUTPUT_MODEL,
    GEOX_PACKAGE_MAIN_HEAD,
    GEOX_PRIMARY_CALLABLE,
    GEOX_RUNTIME_COMMIT,
    GEOX_RUNTIME_MODULE_PATH,
    RECOMMENDED_NEXT_STAGE_3B_ARTIFACT,
    GeoXMaterializedInputAvailability,
    GeoXPanelExpIntegrationIssueCode,
    GeoXPanelExpIntegrationRequest,
    GeoXPanelExpIntegrationResult,
    GeoXPanelExpIntegrationStatus,
    GeoXPanelExpRuntimeCallable,
    GeoXPanelExpRuntimeReference,
    GeoXPostTestExperimentType,
    GeoXPostTestSpendAdapterInputPlan,
    GeoXReadoutInputHandoff,
    GeoXReadoutIntent,
    GeoXReadoutResolutionStatus,
)

_REQUIRED_STATUSES = {
    GeoXPanelExpIntegrationStatus.READY_TO_BUILD_POST_TEST_SPEND_INPUT,
    GeoXPanelExpIntegrationStatus.READY_TO_CALL_GEOX_POST_TEST_SPEND_RUNTIME,
    GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED,
    GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_ASSIGNMENT_INPUT_REQUIRED,
    GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_CONFIRMED_SPEND_MAPPING,
    GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_CONFIRMED_ASSIGNMENT_MAPPING,
    GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_POST_PERIOD_DATES,
    GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_EXPERIMENT_TYPE,
    GeoXPanelExpIntegrationStatus.BLOCKED_MISSING_BASELINE_FOR_EXPERIMENT_TYPE,
    GeoXPanelExpIntegrationStatus.BLOCKED_NO_SPEND_READINESS_REQUESTED,
    GeoXPanelExpIntegrationStatus.BLOCKED_PANEL_EXP_RUNTIME_NOT_CONFIGURED,
    GeoXPanelExpIntegrationStatus.BLOCKED_PANEL_EXP_IMPORT_NOT_ALLOWED,
}

_FORBIDDEN_FIELD_FRAGMENTS = (
    "spend_delta",
    "delta_mu",
    "roi_value",
    "roas_value",
    "computed_lift",
    "lift_value",
    "spend_df",
    "assignment_df",
    "dataframe",
)

_FORBIDDEN_DATAFRAME_FIELD_NAMES = (
    "spend_df",
    "assignment_df",
    "spend_dataframe",
    "assignment_dataframe",
)


def _handoff(**kwargs: str | GeoXReadoutIntent | GeoXReadoutResolutionStatus) -> GeoXReadoutInputHandoff:
    defaults: dict[str, str | GeoXReadoutIntent | GeoXReadoutResolutionStatus] = {
        "request_id": "h-1",
        "readout_intent": GeoXReadoutIntent.READOUT_WITH_COST_PER,
        "experiment_id": "exp-1",
        "mip_resolution_status": GeoXReadoutResolutionStatus.READY_FOR_COST_PER_READOUT,
    }
    defaults.update(kwargs)
    return GeoXReadoutInputHandoff(**defaults)  # type: ignore[arg-type]


def test_required_enums_exist() -> None:
    assert _REQUIRED_STATUSES.issubset(set(GeoXPanelExpIntegrationStatus))
    assert GeoXPanelExpRuntimeCallable.BUILD_POST_TEST_SPEND_EVIDENCE in GeoXPanelExpRuntimeCallable
    assert GeoXPostTestExperimentType.GO_DARK in GeoXPostTestExperimentType
    assert GeoXPanelExpIntegrationIssueCode.CLAIM_AUTHORIZATION_DELEGATED in (
        GeoXPanelExpIntegrationIssueCode
    )


def test_runtime_reference_defaults_match_geox_api_handoff() -> None:
    ref = GeoXPanelExpRuntimeReference()
    assert ref.package_main_head == GEOX_PACKAGE_MAIN_HEAD == "9fe4b92"
    assert ref.runtime_commit == GEOX_RUNTIME_COMMIT == "b400912"
    assert ref.integration_commit == GEOX_INTEGRATION_COMMIT == "9039fda"
    assert ref.runtime_module_path == GEOX_RUNTIME_MODULE_PATH
    assert ref.primary_callable == GEOX_PRIMARY_CALLABLE == "build_post_test_spend_evidence"
    assert ref.handoff_helper_callable == GEOX_HANDOFF_HELPER_CALLABLE
    assert list(ref.integration_callables) == list(GEOX_INTEGRATION_CALLABLES)
    assert ref.integration_module_path == GEOX_INTEGRATION_MODULE_PATH
    assert ref.input_model == GEOX_INPUT_MODEL == "PostTestSpendInput"
    assert ref.output_model == GEOX_OUTPUT_MODEL == "PostTestSpendEvidence"


def test_models_serialize_round_trip() -> None:
    plan = GeoXPostTestSpendAdapterInputPlan(
        request_id="req-1",
        experiment_id="exp-1",
        integration_status=GeoXPanelExpIntegrationStatus.BLOCKED_MATERIALIZED_SPEND_INPUT_REQUIRED,
        materialized_input_availability=GeoXMaterializedInputAvailability(),
    )
    request = GeoXPanelExpIntegrationRequest(request_id="req-1", handoff=_handoff())
    result = GeoXPanelExpIntegrationResult(
        request_id="req-1",
        integration_status=plan.integration_status,
        adapter_input_plan=plan,
    )
    restored = GeoXPanelExpIntegrationResult.model_validate(result.model_dump())
    assert restored.request_id == "req-1"
    assert restored.runtime_called is False
    assert GeoXPanelExpIntegrationRequest.model_validate(request.model_dump())


def test_no_dataframe_fields_on_models() -> None:
    models = (
        GeoXMaterializedInputAvailability,
        GeoXPostTestSpendAdapterInputPlan,
        GeoXPanelExpIntegrationRequest,
        GeoXPanelExpIntegrationResult,
    )
    for model in models:
        for field_name in model.model_fields:
            assert field_name not in _FORBIDDEN_DATAFRAME_FIELD_NAMES, field_name


def test_no_forbidden_metric_output_fields() -> None:
    models = (
        GeoXPostTestSpendAdapterInputPlan,
        GeoXPanelExpIntegrationResult,
    )
    for model in models:
        field_names = " ".join(model.model_fields).lower()
        for fragment in _FORBIDDEN_FIELD_FRAGMENTS:
            if fragment in {"spend_df", "assignment_df", "dataframe"}:
                continue
            assert fragment not in field_names, f"{model.__name__} has forbidden field {fragment}"


def test_runtime_called_defaults_false_and_cannot_be_true() -> None:
    plan = GeoXPostTestSpendAdapterInputPlan(
        request_id="req-1",
        experiment_id="exp-1",
        integration_status=GeoXPanelExpIntegrationStatus.READY_TO_BUILD_POST_TEST_SPEND_INPUT,
        materialized_input_availability=GeoXMaterializedInputAvailability(
            has_materialized_spend_df=True,
            has_assignment_mapping=True,
        ),
    )
    result = GeoXPanelExpIntegrationResult(
        request_id="req-1",
        integration_status=plan.integration_status,
        adapter_input_plan=plan,
    )
    assert result.runtime_called is False
    with pytest.raises(ValueError, match="runtime_called must remain false"):
        GeoXPanelExpIntegrationResult(
            request_id="bad",
            integration_status=plan.integration_status,
            adapter_input_plan=plan,
            runtime_called=True,
        )


def test_contracts_exported_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_STAGE_3B_ARTIFACT == "MIP_GEOX_READOUT_PANEL_EXP_RUNTIME_CALL_001B"
