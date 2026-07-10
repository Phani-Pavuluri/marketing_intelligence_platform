"""Tests for Planning/MMM uploaded CSV input plan workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.planning_mmm_uploaded_csv_adapter import (
    PlanningMMMUploadedCSVAdapterRequest,
    PlanningMMMUploadedCSVAdapterResult,
    PlanningMMMUploadedCSVAdapterStatus,
    PlanningMMMUploadedCSVRole,
)
from mip.contracts.planning_mmm_uploaded_csv_input_plan import (
    PlanningMMMUploadedCSVInputPlanIssueCode,
    PlanningMMMUploadedCSVInputPlanReadinessTier,
    PlanningMMMUploadedCSVInputPlanRequest,
    PlanningMMMUploadedCSVInputPlanResult,
    PlanningMMMUploadedCSVInputPlanStatus,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationRequest,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.workflows.planning_mmm_uploaded_csv_adapter import adapt_uploaded_csvs_for_planning_mmm
from mip.workflows.planning_mmm_uploaded_csv_input_plan import (
    build_planning_mmm_uploaded_csv_input_plan,
    summarize_planning_mmm_uploaded_csv_input_plan,
)
from mip.workflows.uploaded_csv_materialization import materialize_uploaded_csvs

_FIXTURE_ROOT = Path("examples/fixtures/planning_mmm_uploaded_csv_adapter")
_SPEND_PATH = str(_FIXTURE_ROOT / "historical_spend.csv")
_OUTCOME_PATH = str(_FIXTURE_ROOT / "historical_outcome.csv")
_TAXONOMY_PATH = str(_FIXTURE_ROOT / "channel_taxonomy.csv")
_BUDGET_PATH = str(_FIXTURE_ROOT / "budget_constraints.csv")
_CALIBRATION_PATH = str(_FIXTURE_ROOT / "calibration_signals.csv")
_CONFIG_PATH = str(_FIXTURE_ROOT / "model_config.csv")
_WORKFLOW_SOURCE = Path("src/mip/workflows/planning_mmm_uploaded_csv_input_plan.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/planning_mmm_uploaded_csv_input_plan.py")
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
            request_id="mat-plan",
            sources=_core_sources(include_optional=include_optional),
        )
    )
    return adapt_uploaded_csvs_for_planning_mmm(
        PlanningMMMUploadedCSVAdapterRequest(
            request_id="adapt-plan",
            materialization_result=materialization,
            explicit_role_by_source_id=_explicit_roles(include_optional=include_optional),
            required_columns_by_role=required_columns_by_role or {},
        )
    )


def _build_plan(
    adapter: PlanningMMMUploadedCSVAdapterResult | None,
    *,
    request_id: str = "plan-1",
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


def test_successful_plan_required_roles_only() -> None:
    adapter = _adapt(include_optional=False)
    result = _build_plan(adapter)
    assert result.status == PlanningMMMUploadedCSVInputPlanStatus.PLAN_READY_WITH_WARNINGS
    assert result.plan is not None
    assert result.plan.readiness_tier == (
        PlanningMMMUploadedCSVInputPlanReadinessTier.READY_WITH_OPTIONAL_GAPS
    )
    assert PlanningMMMUploadedCSVInputPlanIssueCode.OPTIONAL_INPUT_MISSING in result.issues


def test_successful_plan_all_optional_roles() -> None:
    adapter = _adapt(include_optional=True)
    result = _build_plan(adapter)
    assert result.status == PlanningMMMUploadedCSVInputPlanStatus.PLAN_READY
    assert result.plan is not None
    assert result.plan.readiness_tier == (
        PlanningMMMUploadedCSVInputPlanReadinessTier.READY_FOR_WORKFLOW_READINESS
    )


def test_missing_adapter_result_blocked() -> None:
    result = _build_plan(None)
    assert result.status == (
        PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_ADAPTER_RESULT
    )


def test_adapter_blocked() -> None:
    adapter = _adapt(include_optional=False)
    adapter = adapter.model_copy(
        update={"status": PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE}
    )
    result = _build_plan(adapter)
    assert result.status == PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_ADAPTER_NOT_READY


def test_missing_historical_spend_blocked() -> None:
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
    result = _build_plan(adapter)
    assert (
        result.status
        == PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_REQUIRED_INPUT
    )


def test_missing_historical_outcome_blocked() -> None:
    adapter = _adapt(include_optional=False)
    adapter = adapter.model_copy(
        update={
            "role_mappings": [
                mapping
                for mapping in adapter.role_mappings
                if mapping.role != PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME
            ],
        }
    )
    result = _build_plan(adapter)
    assert (
        result.status
        == PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_REQUIRED_INPUT
    )


def test_optional_role_required_by_request_and_missing_blocked() -> None:
    adapter = _adapt(include_optional=False)
    result = _build_plan(adapter, require_channel_taxonomy=True)
    assert (
        result.status
        == PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_REQUIRED_INPUT
    )


def test_missing_required_columns_blocked() -> None:
    adapter = _adapt(include_optional=False)
    result = _build_plan(
        adapter,
        required_columns_by_role={
            str(PlanningMMMUploadedCSVRole.HISTORICAL_SPEND): ["missing_column"],
        },
    )
    assert (
        result.status
        == PlanningMMMUploadedCSVInputPlanStatus.PLAN_BLOCKED_MISSING_REQUIRED_COLUMNS
    )


def test_role_presence_only_schema() -> None:
    adapter = _adapt(include_optional=False)
    result = _build_plan(adapter)
    assert result.plan is not None
    assert result.plan.readiness_metadata["schema_validation_level"] == "role_presence_only"


def test_required_column_schema() -> None:
    adapter = _adapt(include_optional=False)
    result = _build_plan(
        adapter,
        required_columns_by_role={
            str(PlanningMMMUploadedCSVRole.HISTORICAL_SPEND): ["date", "spend"],
            str(PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME): ["revenue"],
        },
    )
    assert result.plan is not None
    assert result.plan.readiness_metadata["schema_validation_level"] == "role_and_required_columns"


def test_deferred_objects_recorded() -> None:
    adapter = _adapt(include_optional=False)
    result = _build_plan(adapter)
    assert result.plan is not None
    deferred = result.plan.deferred_objects
    for key in (
        "IntakeManifest",
        "MMMConfigDraft",
        "ModelCalibrationReadiness",
        "CalibrationSignalMapping",
    ):
        assert key in deferred
    assert PlanningMMMUploadedCSVInputPlanIssueCode.INTAKE_MANIFEST_DEFERRED in result.issues


def test_readiness_metadata_execution_flags_false() -> None:
    adapter = _adapt(include_optional=False)
    result = _build_plan(adapter)
    assert result.plan is not None
    metadata = result.plan.readiness_metadata
    assert metadata["model_execution_allowed"] is False
    assert metadata["optimizer_execution_allowed"] is False
    assert metadata["recommendation_generation_allowed"] is False
    assert metadata["decision_surface_execution_allowed"] is False
    assert metadata["claim_authorization_allowed"] is False


def test_data_source_refs_preserved() -> None:
    adapter = _adapt(include_optional=False)
    result = _build_plan(adapter)
    assert result.plan is not None
    assert len(result.plan.data_source_refs) == len(adapter.data_source_refs)
    spend_ref = next(
        ref for ref in result.plan.data_source_refs if ref.source_id == "spend"
    )
    assert spend_ref.declared_scope.get("planning_mmm_role") == "historical_spend"


def test_summarize_plan_metadata_only() -> None:
    adapter = _adapt(include_optional=False)
    result = _build_plan(adapter)
    summary = summarize_planning_mmm_uploaded_csv_input_plan(result)
    assert summary["model_execution_allowed"] is False
    deferred_objects = summary["deferred_objects"]
    assert isinstance(deferred_objects, list)
    assert "IntakeManifest" in deferred_objects


def test_no_csv_reread_in_plan_modules() -> None:
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


def test_shared_core_remains_generic() -> None:
    shared_source = _SHARED_CORE.read_text(encoding="utf-8")
    assert "HISTORICAL_SPEND" not in shared_source
    assert "PlanningMMMUploadedCSVRole" not in shared_source


def test_no_metric_recomputation_fields() -> None:
    adapter = _adapt(include_optional=False)
    result = _build_plan(adapter)
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in result.model_dump()
