"""Tests for Planning/MMM uploaded CSV input plan contracts."""

from __future__ import annotations

from datetime import UTC, datetime

from mip.contracts import (
    RECOMMENDED_NEXT_PLANNING_MMM_WORKFLOW_READINESS_ARTIFACT,
    PlanningMMMUploadedCSVInputPlanIssueCode,
    PlanningMMMUploadedCSVInputPlanReadinessTier,
    PlanningMMMUploadedCSVInputPlanRequest,
    PlanningMMMUploadedCSVInputPlanResult,
    PlanningMMMUploadedCSVInputPlanStatus,
    PlanningMMMUploadedCSVInputRequirement,
    PlanningMMMUploadedCSVRole,
)
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import (
    DataSourceMode,
    DataSourceRef,
    DataSourceStatus,
    DataSourceType,
)
from mip.contracts.planning_mmm_uploaded_csv_adapter import (
    PlanningMMMUploadedCSVAdapterResult,
    PlanningMMMUploadedCSVAdapterStatus,
)

_FORBIDDEN_TOP_LEVEL = (
    "spend_delta",
    "delta_mu",
    "lift",
    "roi",
    "roas",
    "optimal_budget",
    "marginal_roi",
    "recommendation",
)


def test_required_enums_exist() -> None:
    assert PlanningMMMUploadedCSVInputPlanStatus.PLAN_READY in (
        PlanningMMMUploadedCSVInputPlanStatus
    )
    assert PlanningMMMUploadedCSVInputPlanIssueCode.NO_MODEL_EXECUTION in (
        PlanningMMMUploadedCSVInputPlanIssueCode
    )
    assert PlanningMMMUploadedCSVInputPlanReadinessTier.BLOCKED in (
        PlanningMMMUploadedCSVInputPlanReadinessTier
    )


def test_models_serialize() -> None:
    request = PlanningMMMUploadedCSVInputPlanRequest(request_id="req-1")
    assert request.require_channel_taxonomy is False
    result = PlanningMMMUploadedCSVInputPlanResult(
        request_id="req-1",
        status=PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_ADAPTER_RESULT,
    )
    assert result.plan is None


def test_requirement_with_data_source_ref() -> None:
    source_ref = DataSourceRef(
        source_id="spend-1",
        source_mode=DataSourceMode.LOCAL_FILE_PATH_MANIFEST,
        source_type=DataSourceType.FILE,
        asset_type=DataAssetType.MEDIA_SPEND_DATA,
        uri_or_table_ref="/tmp/spend.csv",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=DataSourceStatus.DECLARED,
    )
    requirement = PlanningMMMUploadedCSVInputRequirement(
        role=PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
        available=True,
        data_source_ref=source_ref,
    )
    assert requirement.role == PlanningMMMUploadedCSVRole.HISTORICAL_SPEND


def test_readiness_metadata_execution_flags_false() -> None:
    from mip.contracts.planning_mmm_uploaded_csv_input_plan import PlanningMMMUploadedCSVInputPlan

    plan = PlanningMMMUploadedCSVInputPlan(
        plan_id="plan-1",
        readiness_tier=PlanningMMMUploadedCSVInputPlanReadinessTier.READY_WITH_OPTIONAL_GAPS,
        readiness_metadata={
            "model_execution_allowed": False,
            "optimizer_execution_allowed": False,
            "recommendation_generation_allowed": False,
            "decision_surface_execution_allowed": False,
            "claim_authorization_allowed": False,
        },
    )
    assert plan.readiness_metadata["model_execution_allowed"] is False


def test_deferred_objects_can_be_represented() -> None:
    from mip.contracts.planning_mmm_uploaded_csv_input_plan import PlanningMMMUploadedCSVInputPlan

    plan = PlanningMMMUploadedCSVInputPlan(
        plan_id="plan-1",
        readiness_tier=PlanningMMMUploadedCSVInputPlanReadinessTier.READY_FOR_WORKFLOW_READINESS,
        deferred_objects={
            "IntakeManifest": "deferred until session/workflow context exists",
            "MMMConfigDraft": "deferred until model specification context exists",
        },
    )
    assert "IntakeManifest" in plan.deferred_objects


def test_result_no_top_level_metric_fields() -> None:
    schema = PlanningMMMUploadedCSVInputPlanResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_PLANNING_MMM_WORKFLOW_READINESS_ARTIFACT == (
        "MIP_PLANNING_MMM_WORKFLOW_READINESS_FROM_UPLOADED_CSV_001"
    )


def test_adapter_result_attachment() -> None:
    request = PlanningMMMUploadedCSVInputPlanRequest(
        request_id="req-1",
        adapter_result=PlanningMMMUploadedCSVAdapterResult(
            request_id="adapt-1",
            status=PlanningMMMUploadedCSVAdapterStatus.ADAPTED,
        ),
    )
    assert request.adapter_result is not None
