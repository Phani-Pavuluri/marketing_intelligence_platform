"""Tests for Planning/MMM uploaded CSV workflow readiness workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.planning_mmm_uploaded_csv_adapter import (
    PlanningMMMUploadedCSVAdapterRequest,
    PlanningMMMUploadedCSVAdapterResult,
    PlanningMMMUploadedCSVRole,
)
from mip.contracts.planning_mmm_uploaded_csv_input_plan import (
    PlanningMMMUploadedCSVInputPlanIssueCode,
    PlanningMMMUploadedCSVInputPlanRequest,
    PlanningMMMUploadedCSVInputPlanResult,
    PlanningMMMUploadedCSVInputPlanStatus,
)
from mip.contracts.planning_mmm_uploaded_csv_workflow_readiness import (
    PlanningMMMUploadedCSVWorkflowReadinessIssueCode,
    PlanningMMMUploadedCSVWorkflowReadinessRequest,
    PlanningMMMUploadedCSVWorkflowReadinessResult,
    PlanningMMMUploadedCSVWorkflowReadinessStatus,
    PlanningMMMUploadedCSVWorkflowReadinessTier,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationRequest,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.workflows.planning_mmm_uploaded_csv_adapter import adapt_uploaded_csvs_for_planning_mmm
from mip.workflows.planning_mmm_uploaded_csv_input_plan import (
    build_planning_mmm_uploaded_csv_input_plan,
)
from mip.workflows.planning_mmm_uploaded_csv_workflow_readiness import (
    evaluate_planning_mmm_workflow_readiness_from_uploaded_csv,
    summarize_planning_mmm_uploaded_csv_workflow_readiness,
)
from mip.workflows.uploaded_csv_materialization import materialize_uploaded_csvs

_FIXTURE_ROOT = Path("examples/fixtures/planning_mmm_uploaded_csv_adapter")
_SPEND_PATH = str(_FIXTURE_ROOT / "historical_spend.csv")
_OUTCOME_PATH = str(_FIXTURE_ROOT / "historical_outcome.csv")
_TAXONOMY_PATH = str(_FIXTURE_ROOT / "channel_taxonomy.csv")
_BUDGET_PATH = str(_FIXTURE_ROOT / "budget_constraints.csv")
_CALIBRATION_PATH = str(_FIXTURE_ROOT / "calibration_signals.csv")
_CONFIG_PATH = str(_FIXTURE_ROOT / "model_config.csv")
_WORKFLOW_SOURCE = Path(
    "src/mip/workflows/planning_mmm_uploaded_csv_workflow_readiness.py"
)
_CONTRACT_SOURCE = Path(
    "src/mip/contracts/planning_mmm_uploaded_csv_workflow_readiness.py"
)
_SHARED_CORE = Path("src/mip/workflows/uploaded_csv_materialization.py")
_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi_value", "roas_value")


def _source(
    *,
    source_id: str,
    path: str,
    declared_role_hint: str | None = None,
) -> UploadedCSVSource:
    return UploadedCSVSource(
        source_id=source_id,
        source_type=UploadedCSVSourceType.UPLOADED_CSV,
        path=path,
        original_filename=Path(path).name,
        declared_role_hint=declared_role_hint,
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


def _adapt(
    *,
    include_optional: bool = True,
    required_columns_by_role: dict[str, list[str]] | None = None,
) -> PlanningMMMUploadedCSVAdapterResult:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-wf",
            sources=_core_sources(include_optional=include_optional),
        )
    )
    return adapt_uploaded_csvs_for_planning_mmm(
        PlanningMMMUploadedCSVAdapterRequest(
            request_id="adapt-wf",
            materialization_result=materialization,
            explicit_role_by_source_id=_explicit_roles(include_optional=include_optional),
            required_columns_by_role=required_columns_by_role or {},
        )
    )


def _build_plan(
    adapter: PlanningMMMUploadedCSVAdapterResult | None,
    *,
    request_id: str = "plan-wf",
    required_columns_by_role: dict[str, list[str]] | None = None,
    require_channel_taxonomy: bool = False,
) -> PlanningMMMUploadedCSVInputPlanResult:
    return build_planning_mmm_uploaded_csv_input_plan(
        PlanningMMMUploadedCSVInputPlanRequest(
            request_id=request_id,
            adapter_result=adapter,
            required_columns_by_role=required_columns_by_role or {},
            require_channel_taxonomy=require_channel_taxonomy,
        )
    )


def _evaluate(
    input_plan_result: PlanningMMMUploadedCSVInputPlanResult | None,
    *,
    request_id: str = "wf-1",
    require_column_validated_schema: bool = False,
    require_optional_inputs: bool = False,
    required_optional_inputs: list[str] | None = None,
) -> PlanningMMMUploadedCSVWorkflowReadinessResult:
    return evaluate_planning_mmm_workflow_readiness_from_uploaded_csv(
        PlanningMMMUploadedCSVWorkflowReadinessRequest(
            request_id=request_id,
            input_plan_result=input_plan_result,
            require_column_validated_schema=require_column_validated_schema,
            require_optional_inputs=require_optional_inputs,
            required_optional_inputs=required_optional_inputs or [],
        )
    )


def test_ready_with_all_required_and_optional_inputs() -> None:
    plan_result = _build_plan(_adapt(include_optional=True))
    result = _evaluate(plan_result)
    assert (
        result.status
        == PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_FOR_MMM_WORKFLOW_READINESS
    )
    assert result.report is not None
    assert result.report.tier == (
        PlanningMMMUploadedCSVWorkflowReadinessTier.READY_FOR_GATED_WORKFLOW
    )


def test_ready_with_optional_gaps() -> None:
    plan_result = _build_plan(_adapt(include_optional=False))
    result = _evaluate(plan_result)
    assert result.status == PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_WITH_WARNINGS
    assert result.report is not None
    assert (
        result.report.tier
        == PlanningMMMUploadedCSVWorkflowReadinessTier.READY_FOR_GATED_WORKFLOW_WITH_WARNINGS
    )
    assert (
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.OPTIONAL_INPUT_MISSING in result.issues
    )


def test_missing_input_plan_result_blocked() -> None:
    result = _evaluate(None)
    assert (
        result.status
        == PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_INPUT_PLAN_RESULT
    )


def test_input_plan_blocked() -> None:
    plan_result = _build_plan(_adapt(include_optional=False))
    plan_result = plan_result.model_copy(
        update={"status": PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_ADAPTER_NOT_READY}
    )
    result = _evaluate(plan_result)
    assert (
        result.status
        == PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_INPUT_PLAN_NOT_READY
    )


def test_missing_required_input_blocked() -> None:
    adapter = _adapt(include_optional=False)
    adapter = adapter.model_copy(
        update={
            "role_mappings": [
                mapping
                for mapping in adapter.role_mappings
                if mapping.role != PlanningMMMUploadedCSVRole.HISTORICAL_SPEND
            ],
        }
    )
    plan_result = _build_plan(adapter)
    result = _evaluate(plan_result)
    assert (
        result.status
        == PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_INPUT_PLAN_NOT_READY
        or result.status
        == PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_INPUT
    )


def test_missing_required_columns_from_plan_blocked() -> None:
    plan_result = _build_plan(
        _adapt(include_optional=False),
        required_columns_by_role={
            str(PlanningMMMUploadedCSVRole.HISTORICAL_SPEND): ["missing_column"],
        },
    )
    result = _evaluate(plan_result)
    assert (
        result.status
        == PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_INPUT_PLAN_NOT_READY
        or result.status
        == PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_COLUMNS
    )


def test_column_validated_schema_required_but_role_only_blocked() -> None:
    plan_result = _build_plan(_adapt(include_optional=True))
    result = _evaluate(plan_result, require_column_validated_schema=True)
    assert (
        result.status
        == PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_COLUMNS
    )


def test_optional_inputs_required_globally_and_missing_blocked() -> None:
    plan_result = _build_plan(_adapt(include_optional=False))
    result = _evaluate(plan_result, require_optional_inputs=True)
    assert (
        result.status
        == PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_INPUT
    )


def test_specific_optional_input_required_and_missing_blocked() -> None:
    plan_result = _build_plan(_adapt(include_optional=False))
    result = _evaluate(
        plan_result,
        required_optional_inputs=[str(PlanningMMMUploadedCSVRole.CHANNEL_TAXONOMY)],
    )
    assert (
        result.status
        == PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_MISSING_REQUIRED_INPUT
    )


def test_unsafe_execution_flag_blocked() -> None:
    plan_result = _build_plan(_adapt(include_optional=True))
    assert plan_result.plan is not None
    plan = plan_result.plan.model_copy(
        update={
            "readiness_metadata": {
                **plan_result.plan.readiness_metadata,
                "model_execution_allowed": True,
            }
        }
    )
    plan_result = plan_result.model_copy(update={"plan": plan})
    result = _evaluate(plan_result)
    assert (
        result.status
        == PlanningMMMUploadedCSVWorkflowReadinessStatus.BLOCKED_EXECUTION_FLAGS_NOT_SAFE
    )


def test_deferred_objects_preserved() -> None:
    plan_result = _build_plan(_adapt(include_optional=False))
    result = _evaluate(plan_result)
    assert result.report is not None
    deferred = result.report.deferred_objects
    for key in (
        "IntakeManifest",
        "MMMConfigDraft",
        "ModelCalibrationReadiness",
        "CalibrationSignalMapping",
    ):
        assert key in deferred
    assert (
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.INTAKE_MANIFEST_DEFERRED in result.issues
    )


def test_compatibility_metadata_created() -> None:
    plan_result = _build_plan(_adapt(include_optional=True))
    result = _evaluate(plan_result)
    assert result.report is not None
    compatibility = result.report.compatibility
    assert compatibility["uploaded_csv_input_plan_compatible"] is True
    assert compatibility["mmm_data_readiness_report_compatible"] is True
    assert (
        PlanningMMMUploadedCSVWorkflowReadinessIssueCode.MMM_DATA_READINESS_COMPATIBLE
        in result.issues
    )


def test_data_source_refs_preserved() -> None:
    adapter = _adapt(include_optional=False)
    plan_result = _build_plan(adapter)
    result = _evaluate(plan_result)
    assert result.report is not None
    assert len(result.report.data_source_refs) == len(adapter.data_source_refs)
    spend_ref = next(
        ref for ref in result.report.data_source_refs if ref.source_id == "spend"
    )
    assert spend_ref.declared_scope.get("planning_mmm_role") == "historical_spend"


def test_summarize_workflow_readiness_metadata_only() -> None:
    plan_result = _build_plan(_adapt(include_optional=False))
    result = _evaluate(plan_result)
    summary = summarize_planning_mmm_uploaded_csv_workflow_readiness(result)
    execution_allowed = summary["execution_allowed"]
    assert isinstance(execution_allowed, dict)
    assert execution_allowed["model_execution"] is False


def test_no_csv_reread_in_workflow_readiness_modules() -> None:
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "read_csv" not in source
        assert "import pandas" not in source


def test_no_mmm_fitting_optimizer_simulator_imports() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")
    assert "DecisionSurface" not in source
    assert "RecommendationContract" not in source
    assert "panel_exp" not in source
    assert "import optimizer" not in source.lower()
    assert "fit(" not in source


def test_no_recommendation_claim_auth_decision_surface_execution() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")
    assert "authorize_claim" not in source
    assert "generate_recommendation" not in source
    assert "execute_decision_surface" not in source


def test_shared_core_remains_generic() -> None:
    shared_source = _SHARED_CORE.read_text(encoding="utf-8")
    assert "HISTORICAL_SPEND" not in shared_source
    assert "PlanningMMMUploadedCSVRole" not in shared_source


def test_no_metric_recomputation_fields() -> None:
    plan_result = _build_plan(_adapt(include_optional=False))
    result = _evaluate(plan_result)
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in result.model_dump()


def test_input_plan_regression_still_builds() -> None:
    plan_result = _build_plan(_adapt(include_optional=True))
    assert plan_result.status == PlanningMMMUploadedCSVInputPlanStatus.PLAN_READY
    assert PlanningMMMUploadedCSVInputPlanIssueCode.NO_MODEL_EXECUTION in plan_result.issues
