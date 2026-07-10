"""Tests for Planning/MMM readiness report adapter workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.planning_mmm_readiness_report_adapter import (
    PlanningMMMReadinessReportAdapterIssueCode,
    PlanningMMMReadinessReportAdapterRequest,
    PlanningMMMReadinessReportAdapterResult,
    PlanningMMMReadinessReportAdapterStatus,
    PlanningMMMReadinessReportCompatibilityMode,
)
from mip.contracts.planning_mmm_tabular_source_adapter import (
    PlanningMMMTabularSourceAdapterRequest,
)
from mip.contracts.planning_mmm_uploaded_csv_adapter import (
    PlanningMMMUploadedCSVAdapterRequest,
    PlanningMMMUploadedCSVRole,
)
from mip.contracts.planning_mmm_uploaded_csv_input_plan import (
    PlanningMMMUploadedCSVInputPlanRequest,
)
from mip.contracts.planning_mmm_uploaded_csv_workflow_readiness import (
    PlanningMMMUploadedCSVWorkflowReadinessRequest,
    PlanningMMMUploadedCSVWorkflowReadinessResult,
    PlanningMMMUploadedCSVWorkflowReadinessStatus,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationRequest,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.workflows.planning_mmm_readiness_report_adapter import (
    adapt_planning_mmm_workflow_readiness_to_readiness_report,
    summarize_planning_mmm_readiness_report_adapter,
)
from mip.workflows.planning_mmm_tabular_source_adapter import (
    adapt_tabular_sources_for_planning_mmm,
    build_uploaded_csv_input_plan_request_from_tabular_source_adapter_result,
)
from mip.workflows.planning_mmm_uploaded_csv_adapter import adapt_uploaded_csvs_for_planning_mmm
from mip.workflows.planning_mmm_uploaded_csv_input_plan import (
    build_planning_mmm_uploaded_csv_input_plan,
)
from mip.workflows.planning_mmm_uploaded_csv_workflow_readiness import (
    evaluate_planning_mmm_workflow_readiness_from_uploaded_csv,
)
from mip.workflows.tabular_source_inspection import (
    build_tabular_source_inspection_from_uploaded_csv_materialization,
)
from mip.workflows.uploaded_csv_materialization import materialize_uploaded_csvs

_FIXTURE_ROOT = Path("examples/fixtures/planning_mmm_uploaded_csv_adapter")
_SPEND_PATH = str(_FIXTURE_ROOT / "historical_spend.csv")
_OUTCOME_PATH = str(_FIXTURE_ROOT / "historical_outcome.csv")
_TAXONOMY_PATH = str(_FIXTURE_ROOT / "channel_taxonomy.csv")
_BUDGET_PATH = str(_FIXTURE_ROOT / "budget_constraints.csv")
_CALIBRATION_PATH = str(_FIXTURE_ROOT / "calibration_signals.csv")
_CONFIG_PATH = str(_FIXTURE_ROOT / "model_config.csv")
_WORKFLOW_SOURCE = Path("src/mip/workflows/planning_mmm_readiness_report_adapter.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/planning_mmm_readiness_report_adapter.py")
_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi_value", "roas_value")


def _source(*, source_id: str, path: str) -> UploadedCSVSource:
    return UploadedCSVSource(
        source_id=source_id,
        source_type=UploadedCSVSourceType.UPLOADED_CSV,
        path=path,
        original_filename=Path(path).name,
    )


def _core_sources(*, include_optional: bool = True) -> list[UploadedCSVSource]:
    sources = [
        _source(source_id="spend", path=_SPEND_PATH),
        _source(source_id="outcome", path=_OUTCOME_PATH),
    ]
    if include_optional:
        sources.extend(
            [
                _source(source_id="taxonomy", path=_TAXONOMY_PATH),
                _source(source_id="budget", path=_BUDGET_PATH),
                _source(source_id="calibration", path=_CALIBRATION_PATH),
                _source(source_id="config", path=_CONFIG_PATH),
            ]
        )
    return sources


def _explicit_roles(*, include_optional: bool = True) -> dict[str, PlanningMMMUploadedCSVRole]:
    roles = {
        "spend": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
        "outcome": PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME,
    }
    if include_optional:
        roles.update(
            {
                "taxonomy": PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY,
                "budget": PlanningMMMUploadedCSVRole.BUDGET_CONSTRAINTS,
                "calibration": PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS,
                "config": PlanningMMMUploadedCSVRole.MODEL_CONFIG,
            }
        )
    return roles


def _workflow_readiness_from_uploaded_csv(
    *, include_optional: bool = True,
) -> PlanningMMMUploadedCSVWorkflowReadinessResult:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-rr",
            sources=_core_sources(include_optional=include_optional),
        )
    )
    adapter = adapt_uploaded_csvs_for_planning_mmm(
        PlanningMMMUploadedCSVAdapterRequest(
            request_id="adapt-rr",
            materialization_result=materialization,
            explicit_role_by_source_id=_explicit_roles(include_optional=include_optional),
        )
    )
    plan = build_planning_mmm_uploaded_csv_input_plan(
        PlanningMMMUploadedCSVInputPlanRequest(
            request_id="plan-rr",
            adapter_result=adapter,
        )
    )
    return evaluate_planning_mmm_workflow_readiness_from_uploaded_csv(
        PlanningMMMUploadedCSVWorkflowReadinessRequest(
            request_id="wf-rr",
            input_plan_result=plan,
        )
    )


def _workflow_readiness_from_tabular(
    *, include_optional: bool = True,
) -> PlanningMMMUploadedCSVWorkflowReadinessResult:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-tab-rr",
            sources=_core_sources(include_optional=include_optional),
        )
    )
    tabular = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="tabular-rr",
        materialization_result=materialization,
    )
    tabular_adapter = adapt_tabular_sources_for_planning_mmm(
        PlanningMMMTabularSourceAdapterRequest(
            request_id="adapt-tab-rr",
            tabular_source_result=tabular,
            explicit_role_by_source_id=_explicit_roles(include_optional=include_optional),
        )
    )
    plan_request = build_uploaded_csv_input_plan_request_from_tabular_source_adapter_result(
        tabular_adapter,
        request_id="plan-tab-rr",
    )
    plan = build_planning_mmm_uploaded_csv_input_plan(plan_request)
    return evaluate_planning_mmm_workflow_readiness_from_uploaded_csv(
        PlanningMMMUploadedCSVWorkflowReadinessRequest(
            request_id="wf-tab-rr",
            input_plan_result=plan,
        )
    )


def _adapt(
    workflow_result: PlanningMMMUploadedCSVWorkflowReadinessResult | None,
    *,
    request_id: str = "rr-1",
    require_full_mmm_data_readiness_report: bool = False,
) -> PlanningMMMReadinessReportAdapterResult:
    return adapt_planning_mmm_workflow_readiness_to_readiness_report(
        PlanningMMMReadinessReportAdapterRequest(
            request_id=request_id,
            workflow_readiness_result=workflow_result,
            require_full_mmm_data_readiness_report=require_full_mmm_data_readiness_report,
        )
    )


def test_successful_metadata_compatible_report() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=True)
    result = _adapt(workflow)
    assert result.status in {
        PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED,
        PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED_WITH_WARNINGS,
    }
    assert result.envelope is not None
    assert result.envelope.compatibility.mode in {
        PlanningMMMReadinessReportCompatibilityMode.METADATA_COMPATIBLE,
        PlanningMMMReadinessReportCompatibilityMode.FULL_REPORT_CONSTRUCTION_DEFERRED,
    }
    assert (
        PlanningMMMReadinessReportAdapterIssueCode.MMM_DATA_READINESS_METADATA_COMPATIBLE
        in result.issues
        or PlanningMMMReadinessReportAdapterIssueCode.MMM_DATA_READINESS_FULL_CONSTRUCTION_DEFERRED
        in result.issues
    )


def test_ready_with_optional_gaps() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    result = _adapt(workflow)
    assert result.status == PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED_WITH_WARNINGS
    assert PlanningMMMReadinessReportAdapterIssueCode.OPTIONAL_INPUT_MISSING in result.issues


def test_missing_workflow_readiness_result_blocked() -> None:
    result = _adapt(None)
    assert (
        result.status
        == PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_WORKFLOW_READINESS_RESULT
    )


def test_workflow_readiness_blocked() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    workflow = workflow.model_copy(
        update={
            "status": (
                PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_INPUT_PLAN_NOT_READY
            )
        }
    )
    result = _adapt(workflow)
    assert (
        result.status
        == PlanningMMMReadinessReportAdapterStatus.BLOCKED_WORKFLOW_READINESS_NOT_READY
    )


def test_missing_required_input_blocked() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    assert workflow.report is not None
    workflow = workflow.model_copy(
        update={
            "status": PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_INPUT,
            "report": workflow.report.model_copy(
                update={"missing_required_inputs": ["historical_spend"]}
            ),
        }
    )
    result = _adapt(workflow)
    assert result.status == PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_REQUIRED_INPUT


def test_missing_required_columns_blocked() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    assert workflow.report is not None
    workflow = workflow.model_copy(
        update={
            "status": (
                PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_COLUMNS
            ),
            "report": workflow.report.model_copy(
                update={"missing_required_columns": ["historical_spend:missing_col"]}
            ),
        }
    )
    result = _adapt(workflow)
    assert result.status == PlanningMMMReadinessReportAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS


def test_full_mmm_data_readiness_required_but_unavailable_blocked() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=True)
    result = _adapt(workflow, require_full_mmm_data_readiness_report=True)
    assert (
        result.status
        == PlanningMMMReadinessReportAdapterStatus.BLOCKED_MMM_DATA_READINESS_CONTRACT_UNAVAILABLE
    )


def test_deferred_objects_preserved() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    result = _adapt(workflow)
    assert result.envelope is not None
    for key in (
        "IntakeManifest",
        "MMMConfigDraft",
        "ModelCalibrationReadiness",
        "CalibrationSignalMapping",
    ):
        assert key in result.envelope.deferred_objects
    assert PlanningMMMReadinessReportAdapterIssueCode.DEFERRED_OBJECTS_PRESERVED in result.issues


def test_data_source_refs_preserved() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    result = _adapt(workflow)
    assert result.envelope is not None
    assert len(result.envelope.data_source_refs) >= 2
    assert PlanningMMMReadinessReportAdapterIssueCode.DATA_SOURCE_REFS_PRESERVED in result.issues


def test_tabular_source_refs_preserved_when_present() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    assert workflow.report is not None
    workflow = workflow.model_copy(
        update={
            "report": workflow.report.model_copy(
                update={
                    "lineage": {
                        **workflow.report.lineage,
                        "tabular_source_reference_ids": "spend,outcome",
                    }
                }
            )
        }
    )
    result = _adapt(workflow)
    assert result.envelope is not None
    assert len(result.envelope.tabular_source_refs) == 2
    assert PlanningMMMReadinessReportAdapterIssueCode.TABULAR_SOURCE_REFS_PRESERVED in result.issues


def test_readiness_status_tier_preserved() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    result = _adapt(workflow)
    assert result.envelope is not None
    assert result.envelope.source_workflow_readiness_status
    assert result.envelope.source_workflow_readiness_tier
    assert PlanningMMMReadinessReportAdapterIssueCode.READINESS_STATUS_PRESERVED in result.issues
    assert PlanningMMMReadinessReportAdapterIssueCode.READINESS_TIER_PRESERVED in result.issues


def test_execution_flags_remain_false() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    result = _adapt(workflow)
    assert result.envelope is not None
    for flag, value in result.envelope.execution_allowed.items():
        assert value is False, flag


def test_uploaded_csv_workflow_readiness_path_compatibility() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    result = _adapt(workflow)
    assert result.envelope is not None
    assert result.envelope.data_source_refs


def test_generic_tabular_workflow_readiness_path_compatibility() -> None:
    workflow = _workflow_readiness_from_tabular(include_optional=False)
    result = _adapt(workflow)
    assert result.status in {
        PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED,
        PlanningMMMReadinessReportAdapterStatus.REPORT_ADAPTED_WITH_WARNINGS,
    }


def test_summarize_metadata_only() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    result = _adapt(workflow)
    summary = summarize_planning_mmm_readiness_report_adapter(result)
    execution_allowed = summary["execution_allowed"]
    assert isinstance(execution_allowed, dict)
    assert execution_allowed["model_execution"] is False


def test_no_csv_reread_in_readiness_report_adapter_modules() -> None:
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "read_csv" not in source
        assert "import pandas" not in source


def test_no_mmm_fitting_optimizer_simulator() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")
    assert "DecisionSurface" not in source
    assert "RecommendationContract" not in source
    assert "fit(" not in source


def test_no_metric_recomputation_fields() -> None:
    workflow = _workflow_readiness_from_uploaded_csv(include_optional=False)
    result = _adapt(workflow)
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in result.model_dump()
