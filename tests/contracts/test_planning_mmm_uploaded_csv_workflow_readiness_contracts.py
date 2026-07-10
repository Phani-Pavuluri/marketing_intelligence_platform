"""Tests for Planning/MMM uploaded CSV workflow readiness contracts."""

from __future__ import annotations

from datetime import UTC, datetime

from mip.contracts import (
    RECOMMENDED_NEXT_PLANNING_MMM_READINESS_REPORT_ADAPTER_ARTIFACT,
    PlanningMMMUploadedCSVWorkflowReadinessIssueCode,
    PlanningMMMUploadedCSVWorkflowReadinessReport,
    PlanningMMMUploadedCSVWorkflowReadinessRequest,
    PlanningMMMUploadedCSVWorkflowReadinessResult,
    PlanningMMMUploadedCSVWorkflowReadinessStatus,
    PlanningMMMUploadedCSVWorkflowReadinessTier,
)
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import (
    DataSourceMode,
    DataSourceRef,
    DataSourceStatus,
    DataSourceType,
)
from mip.contracts.planning_mmm_uploaded_csv_input_plan import (
    PlanningMMMUploadedCSVInputPlan,
    PlanningMMMUploadedCSVInputPlanReadinessTier,
    PlanningMMMUploadedCSVInputPlanResult,
    PlanningMMMUploadedCSVInputPlanStatus,
)

_FORBIDDEN_TOP_LEVEL = (
    "spend_delta",
    "delta_mu",
    "lift",
    "roi",
    "roas",
    "incrementality",
    "optimal_budget",
    "marginal_roi",
    "recommendation",
)


def test_required_enums_exist() -> None:
    assert (
        PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_FOR_MMM_WORKFLOW_READINESS
        in PlanningMMMUploadedCSVWorkflowReadinessStatus
    )
    assert (
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.NO_MODEL_EXECUTION
        in PlanningMMMUploadedCSVWorkflowReadinessIssueCode
    )
    assert (
        PlanningMMMUploadedCSVWorkflowReadinessTier.BLOCKED
        in PlanningMMMUploadedCSVWorkflowReadinessTier
    )


def test_models_serialize() -> None:
    request = PlanningMMMUploadedCSVWorkflowReadinessRequest(request_id="req-1")
    assert request.require_column_validated_schema is False
    result = PlanningMMMUploadedCSVWorkflowReadinessResult(
        request_id="req-1",
        status=PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_INPUT_PLAN_RESULT,
    )
    assert result.report is None


def test_report_can_include_data_source_refs() -> None:
    source_ref = DataSourceRef(
        source_id="spend-1",
        source_mode=DataSourceMode.LOCAL_FILE_PATH_MANIFEST,
        source_type=DataSourceType.FILE,
        asset_type=DataAssetType.MEDIA_SPEND_DATA,
        uri_or_table_ref="/tmp/spend.csv",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=DataSourceStatus.DECLARED,
    )
    report = PlanningMMMUploadedCSVWorkflowReadinessReport(
        report_id="report-1",
        status=PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_FOR_MMM_WORKFLOW_READINESS,
        tier=PlanningMMMUploadedCSVWorkflowReadinessTier.READY_FOR_GATED_WORKFLOW,
        data_source_refs=[source_ref],
    )
    assert report.data_source_refs[0].source_id == "spend-1"


def test_deferred_objects_can_be_represented() -> None:
    report = PlanningMMMUploadedCSVWorkflowReadinessReport(
        report_id="report-1",
        status=PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_WITH_WARNINGS,
        tier=PlanningMMMUploadedCSVWorkflowReadinessTier.READY_FOR_GATED_WORKFLOW_WITH_WARNINGS,
        deferred_objects={
            "IntakeManifest": "deferred until session/workflow context exists",
            "MMMConfigDraft": "deferred until model specification context exists",
        },
    )
    assert "IntakeManifest" in report.deferred_objects


def test_execution_flags_are_false() -> None:
    report = PlanningMMMUploadedCSVWorkflowReadinessReport(
        report_id="report-1",
        status=PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_FOR_MMM_WORKFLOW_READINESS,
        tier=PlanningMMMUploadedCSVWorkflowReadinessTier.READY_FOR_GATED_WORKFLOW,
        execution_allowed={
            "model_execution": False,
            "bayesian_model_execution": False,
            "optimizer_execution": False,
            "simulator_execution": False,
            "decision_surface_execution": False,
            "recommendation_generation": False,
            "claim_authorization": False,
        },
    )
    assert report.execution_allowed["model_execution"] is False
    assert report.execution_allowed["claim_authorization"] is False


def test_result_no_top_level_metric_fields() -> None:
    schema = PlanningMMMUploadedCSVWorkflowReadinessResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_PLANNING_MMM_READINESS_REPORT_ADAPTER_ARTIFACT == (
        "MIP_PLANNING_MMM_READINESS_REPORT_ADAPTER_001"
    )


def test_input_plan_result_attachment() -> None:
    request = PlanningMMMUploadedCSVWorkflowReadinessRequest(
        request_id="req-1",
        input_plan_result=PlanningMMMUploadedCSVInputPlanResult(
            request_id="plan-1",
            status=PlanningMMMUploadedCSVInputPlanStatus.PLAN_READY,
            plan=PlanningMMMUploadedCSVInputPlan(
                plan_id="planning-mmm-input-plan:plan-1",
                readiness_tier=PlanningMMMUploadedCSVInputPlanReadinessTier.READY_FOR_WORKFLOW_READINESS,
            ),
        ),
    )
    assert request.input_plan_result is not None
