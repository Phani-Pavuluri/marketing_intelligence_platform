"""Tests for Planning/MMM tabular source adapter compatibility workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.planning_mmm_tabular_source_adapter import (
    PlanningMMMTabularSourceAdapterIssueCode,
    PlanningMMMTabularSourceAdapterRequest,
    PlanningMMMTabularSourceAdapterResult,
    PlanningMMMTabularSourceAdapterStatus,
)
from mip.contracts.planning_mmm_uploaded_csv_adapter import (
    PlanningMMMUploadedCSVAdapterRequest,
    PlanningMMMUploadedCSVRole,
)
from mip.contracts.planning_mmm_uploaded_csv_input_plan import (
    PlanningMMMUploadedCSVInputPlanStatus,
)
from mip.contracts.planning_mmm_uploaded_csv_workflow_readiness import (
    PlanningMMMUploadedCSVWorkflowReadinessStatus,
)
from mip.contracts.tabular_source_reference import (
    TabularSourceAccessMode,
    TabularSourceInspectionResult,
    TabularSourceInspectionStatus,
    TabularSourceMaterializationMode,
    TabularSourceType,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationRequest,
    UploadedCSVSource,
    UploadedCSVSourceType,
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
_WORKFLOW_SOURCE = Path("src/mip/workflows/planning_mmm_tabular_source_adapter.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/planning_mmm_tabular_source_adapter.py")
_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "lift", "roi_value", "roas_value")
_FORBIDDEN_RUNTIME_PATTERNS = (
    "databricks",
    "warehouse",
    "api_tabular_source",
    "registered_table_source",
    "spark",
    "jdbc",
    "odbc",
)


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


def _tabular_from_uploaded_csv(
    *,
    include_optional: bool = True,
    request_id: str = "tabular-1",
) -> TabularSourceInspectionResult:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-tab",
            sources=_core_sources(include_optional=include_optional),
        )
    )
    return build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id=request_id,
        materialization_result=materialization,
    )


def _adapt_tabular(
    tabular_result: TabularSourceInspectionResult | None,
    *,
    request_id: str = "adapt-tab",
    explicit_role_by_source_id: dict[str, PlanningMMMUploadedCSVRole] | None = None,
    required_columns_by_role: dict[str, list[str]] | None = None,
) -> PlanningMMMTabularSourceAdapterResult:
    return adapt_tabular_sources_for_planning_mmm(
        PlanningMMMTabularSourceAdapterRequest(
            request_id=request_id,
            tabular_source_result=tabular_result,
            explicit_role_by_source_id=explicit_role_by_source_id or {},
            required_columns_by_role=required_columns_by_role or {},
        )
    )


def test_successful_tabular_adapter_with_explicit_roles() -> None:
    tabular = _tabular_from_uploaded_csv()
    result = _adapt_tabular(tabular, explicit_role_by_source_id=_explicit_roles())
    assert result.status in {
        PlanningMMMTabularSourceAdapterStatus.ADAPTED,
        PlanningMMMTabularSourceAdapterStatus.ADAPTED_WITH_WARNINGS,
    }
    assert result.availability is not None
    assert result.availability.has_historical_spend
    assert result.availability.has_historical_outcome
    assert len(result.data_source_refs) >= 2
    assert len(result.tabular_source_references) >= 2
    assert PlanningMMMTabularSourceAdapterIssueCode.DATA_SOURCE_REF_PRESERVED in result.issues


def test_successful_tabular_adapter_with_declared_role_hints() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-hint",
            sources=[
                _source(source_id="spend", path=_SPEND_PATH, declared_role_hint="historical_spend"),
                _source(source_id="outcome", path=_OUTCOME_PATH, declared_role_hint="outcome"),
            ],
        )
    )
    tabular = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="tabular-hint",
        materialization_result=materialization,
    )
    result = _adapt_tabular(tabular)
    assert result.status in {
        PlanningMMMTabularSourceAdapterStatus.ADAPTED,
        PlanningMMMTabularSourceAdapterStatus.ADAPTED_WITH_WARNINGS,
    }
    assert PlanningMMMTabularSourceAdapterIssueCode.ROLE_HINT_USED in result.issues


def test_uploaded_csv_compatibility_path_equivalent_availability() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-equiv",
            sources=_core_sources(include_optional=False),
        )
    )
    csv_adapter = adapt_uploaded_csvs_for_planning_mmm(
        PlanningMMMUploadedCSVAdapterRequest(
            request_id="csv-adapt",
            materialization_result=materialization,
            explicit_role_by_source_id=_explicit_roles(include_optional=False),
        )
    )
    tabular = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="tabular-equiv",
        materialization_result=materialization,
    )
    tabular_adapter = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    assert csv_adapter.availability is not None
    assert tabular_adapter.availability is not None
    assert tabular_adapter.availability.has_historical_spend == (
        csv_adapter.availability.has_historical_spend
    )
    assert tabular_adapter.availability.has_historical_outcome == (
        csv_adapter.availability.has_historical_outcome
    )
    assert (
        PlanningMMMTabularSourceAdapterIssueCode.UPLOADED_CSV_COMPATIBILITY_PATH_SUPPORTED
        in tabular_adapter.issues
    )


def test_missing_tabular_source_result_blocked() -> None:
    result = _adapt_tabular(None)
    assert (
        result.status
        == PlanningMMMTabularSourceAdapterStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT
    )


def test_blocked_tabular_source_result_blocked() -> None:
    tabular = TabularSourceInspectionResult(
        request_id="blocked",
        status=TabularSourceInspectionStatus.BLOCKED_MISSING_SOURCE,
    )
    result = _adapt_tabular(tabular)
    assert result.status == PlanningMMMTabularSourceAdapterStatus.BLOCKED_TABULAR_SOURCE_NOT_READY


def test_missing_required_role_blocked() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-miss",
            sources=[_source(source_id="spend", path=_SPEND_PATH)],
        )
    )
    tabular = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="tabular-miss",
        materialization_result=materialization,
    )
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id={
            "spend": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
        },
    )
    assert result.status == PlanningMMMTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE


def test_duplicate_required_role_blocked() -> None:
    tabular = _tabular_from_uploaded_csv(include_optional=False)
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id={
            "spend": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
            "outcome": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
        },
    )
    assert result.status == PlanningMMMTabularSourceAdapterStatus.BLOCKED_DUPLICATE_ROLE


def test_ambiguous_unknown_role_blocked() -> None:
    tabular = _tabular_from_uploaded_csv(include_optional=False)
    result = _adapt_tabular(tabular)
    assert result.status == PlanningMMMTabularSourceAdapterStatus.BLOCKED_AMBIGUOUS_ROLE


def test_missing_required_columns_blocked() -> None:
    tabular = _tabular_from_uploaded_csv(include_optional=False)
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
        required_columns_by_role={
            str(PlanningMMMUploadedCSVRole.HISTORICAL_SPEND): ["missing_column"],
        },
    )
    assert result.status == PlanningMMMTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS


def test_missing_data_source_ref_blocked() -> None:
    tabular = _tabular_from_uploaded_csv(include_optional=False)
    stripped = tabular.model_copy(
        update={
            "inspections": [
                inspection.model_copy(
                    update={
                        "source_reference": inspection.source_reference.model_copy(
                            update={"data_source_ref": None}
                        )
                    }
                )
                for inspection in tabular.inspections
            ]
        }
    )
    result = _adapt_tabular(
        stripped,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    assert (
        result.status
        == PlanningMMMTabularSourceAdapterStatus.BLOCKED_DATA_SOURCE_REF_UNAVAILABLE
    )


def test_optional_roles_missing_warning_only() -> None:
    tabular = _tabular_from_uploaded_csv(include_optional=False)
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    assert result.status in {
        PlanningMMMTabularSourceAdapterStatus.ADAPTED,
        PlanningMMMTabularSourceAdapterStatus.ADAPTED_WITH_WARNINGS,
    }
    assert (
        PlanningMMMTabularSourceAdapterIssueCode.OPTIONAL_CHANNEL_TAXONOMY_MISSING in result.issues
    )


def test_lineage_preserved() -> None:
    tabular = _tabular_from_uploaded_csv(include_optional=False)
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    assert "adapter_stage" in result.lineage
    assert (
        PlanningMMMTabularSourceAdapterIssueCode.TABULAR_SOURCE_LINEAGE_PRESERVED in result.issues
    )


def test_input_plan_compatibility_through_helper() -> None:
    tabular = _tabular_from_uploaded_csv(include_optional=False)
    tabular_adapter = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    plan_request = build_uploaded_csv_input_plan_request_from_tabular_source_adapter_result(
        tabular_adapter,
        request_id="plan-tab",
    )
    plan_result = build_planning_mmm_uploaded_csv_input_plan(plan_request)
    assert plan_result.status in {
        PlanningMMMUploadedCSVInputPlanStatus.PLAN_READY,
        PlanningMMMUploadedCSVInputPlanStatus.PLAN_READY_WITH_WARNINGS,
    }


def test_workflow_readiness_compatibility_through_tabular_path() -> None:
    tabular = _tabular_from_uploaded_csv(include_optional=False)
    tabular_adapter = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    plan_request = build_uploaded_csv_input_plan_request_from_tabular_source_adapter_result(
        tabular_adapter,
        request_id="plan-wf",
    )
    plan_result = build_planning_mmm_uploaded_csv_input_plan(plan_request)
    from mip.contracts.planning_mmm_uploaded_csv_workflow_readiness import (
        PlanningMMMUploadedCSVWorkflowReadinessRequest,
    )

    readiness = evaluate_planning_mmm_workflow_readiness_from_uploaded_csv(
        PlanningMMMUploadedCSVWorkflowReadinessRequest(
            request_id="wf-tab",
            input_plan_result=plan_result,
        )
    )
    assert readiness.status in {
        PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_FOR_MMM_WORKFLOW_READINESS,
        PlanningMMMUploadedCSVWorkflowReadinessStatus.READY_WITH_WARNINGS,
    }


def test_no_csv_reread_in_tabular_adapter_modules() -> None:
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "read_csv" not in source
        assert "import pandas" not in source


def test_no_connector_runtime_modules_added() -> None:
    src_root = Path("src/mip")
    for path in src_root.rglob("*.py"):
        stem = path.stem.lower()
        for pattern in _FORBIDDEN_RUNTIME_PATTERNS:
            assert pattern not in stem, f"unexpected runtime module: {path}"


def test_no_sql_network_spark_in_workflow() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8").lower()
    for term in ("requests", "httpx", "urllib", "spark", "sqlalchemy", "execute("):
        assert term not in source


def test_no_mmm_fitting_optimizer_simulator() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")
    assert "DecisionSurface" not in source
    assert "RecommendationContract" not in source
    assert "fit(" not in source


def test_no_metric_recomputation_fields() -> None:
    tabular = _tabular_from_uploaded_csv(include_optional=False)
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in result.model_dump()


def test_reference_only_tabular_source_representable() -> None:
    from mip.workflows.tabular_source_inspection import build_tabular_source_reference

    reference = build_tabular_source_reference(
        source_id="warehouse-1",
        source_type=TabularSourceType.WAREHOUSE_TABLE,
        access_mode=TabularSourceAccessMode.REFERENCE_ONLY,
        materialization_mode=TabularSourceMaterializationMode.REFERENCE_ONLY,
        source_uri="warehouse://analytics.fact_spend",
    )
    assert reference.source_type == TabularSourceType.WAREHOUSE_TABLE
