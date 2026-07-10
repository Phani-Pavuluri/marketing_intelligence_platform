"""Tests for Planning/MMM calibration-signal tabular intake workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.planning_mmm_calibration_signal_tabular_intake import (
    PlanningMMMCalibrationSignalConstructionMode,
    PlanningMMMCalibrationSignalTabularIntakeIssueCode,
    PlanningMMMCalibrationSignalTabularIntakeRequest,
    PlanningMMMCalibrationSignalTabularIntakeResult,
    PlanningMMMCalibrationSignalTabularIntakeStatus,
)
from mip.contracts.planning_mmm_tabular_source_adapter import (
    PlanningMMMTabularSourceAdapterRequest,
)
from mip.contracts.planning_mmm_uploaded_csv_adapter import PlanningMMMUploadedCSVRole
from mip.contracts.tabular_source_reference import (
    TabularSourceInspectionResult,
    TabularSourceInspectionStatus,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationRequest,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.workflows.planning_mmm_calibration_signal_tabular_intake import (
    intake_calibration_signals_from_tabular_source,
    summarize_calibration_signal_tabular_intake,
)
from mip.workflows.planning_mmm_tabular_source_adapter import (
    adapt_tabular_sources_for_planning_mmm,
)
from mip.workflows.tabular_source_inspection import (
    build_tabular_source_inspection_from_uploaded_csv_materialization,
)
from mip.workflows.uploaded_csv_materialization import materialize_uploaded_csvs

_FIXTURE_ROOT = Path("examples/fixtures/planning_mmm_uploaded_csv_adapter")
_SPEND_PATH = str(_FIXTURE_ROOT / "historical_spend.csv")
_OUTCOME_PATH = str(_FIXTURE_ROOT / "historical_outcome.csv")
_CALIBRATION_PATH = str(_FIXTURE_ROOT / "calibration_signals.csv")
_WORKFLOW_SOURCE = Path("src/mip/workflows/planning_mmm_calibration_signal_tabular_intake.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/planning_mmm_calibration_signal_tabular_intake.py")
_FORBIDDEN_TOP_LEVEL = ("spend_delta", "delta_mu", "roi_value", "roas_value")
_FIXTURE_REQUIRED_COLUMNS = ["channel", "lift", "standard_error"]
_FIXTURE_COLUMN_ALIASES = {
    "lift": ["prior_lift"],
    "standard_error": ["prior_uncertainty"],
}


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


def _tabular_from_sources(
    sources: list[UploadedCSVSource],
    *,
    request_id: str = "tabular-cal-1",
) -> TabularSourceInspectionResult:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(request_id="mat-cal", sources=sources)
    )
    return build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id=request_id,
        materialization_result=materialization,
    )


def _intake(
    tabular_result: TabularSourceInspectionResult | None,
    *,
    request_id: str = "intake-cal-1",
    explicit_calibration_source_ids: list[str] | None = None,
    required_columns: list[str] | None = None,
    optional_columns: list[str] | None = None,
    column_role_aliases: dict[str, list[str]] | None = None,
    require_full_calibration_signal_construction: bool = False,
) -> PlanningMMMCalibrationSignalTabularIntakeResult:
    return intake_calibration_signals_from_tabular_source(
        PlanningMMMCalibrationSignalTabularIntakeRequest(
            request_id=request_id,
            tabular_source_result=tabular_result,
            explicit_calibration_source_ids=explicit_calibration_source_ids or [],
            required_columns=required_columns or list(_FIXTURE_REQUIRED_COLUMNS),
            optional_columns=optional_columns or [],
            column_role_aliases=column_role_aliases or dict(_FIXTURE_COLUMN_ALIASES),
            require_full_calibration_signal_construction=require_full_calibration_signal_construction,
        )
    )


def test_successful_intake_with_explicit_source_id() -> None:
    tabular = _tabular_from_sources(
        [
            _source(source_id="spend", path=_SPEND_PATH),
            _source(source_id="outcome", path=_OUTCOME_PATH),
            _source(source_id="calibration", path=_CALIBRATION_PATH),
        ]
    )
    result = _intake(tabular, explicit_calibration_source_ids=["calibration"])
    assert result.status in {
        PlanningMMMCalibrationSignalTabularIntakeStatus.INTAKE_READY,
        PlanningMMMCalibrationSignalTabularIntakeStatus.INTAKE_READY_WITH_WARNINGS,
    }
    assert result.envelope is not None
    assert len(result.envelope.calibration_signal_sources) == 1
    assert PlanningMMMCalibrationSignalTabularIntakeIssueCode.DATA_SOURCE_REF_PRESERVED in (
        result.issues
    )


def test_successful_intake_via_declared_role_hint() -> None:
    tabular = _tabular_from_sources(
        [
            _source(source_id="spend", path=_SPEND_PATH),
            _source(source_id="outcome", path=_OUTCOME_PATH),
            _source(
                source_id="calibration",
                path=_CALIBRATION_PATH,
                declared_role_hint="calibration_signals",
            ),
        ]
    )
    result = _intake(tabular)
    assert result.status in {
        PlanningMMMCalibrationSignalTabularIntakeStatus.INTAKE_READY,
        PlanningMMMCalibrationSignalTabularIntakeStatus.INTAKE_READY_WITH_WARNINGS,
    }


def test_uploaded_csv_compatibility_path() -> None:
    tabular = _tabular_from_sources(
        [
            _source(source_id="spend", path=_SPEND_PATH),
            _source(source_id="outcome", path=_OUTCOME_PATH),
            _source(source_id="calibration", path=_CALIBRATION_PATH),
        ]
    )
    result = _intake(tabular, explicit_calibration_source_ids=["calibration"])
    assert result.envelope is not None
    assert result.envelope.calibration_signal_sources[0].source_id == "calibration"


def test_generic_planning_mmm_path_compatibility() -> None:
    tabular = _tabular_from_sources(
        [
            _source(source_id="spend", path=_SPEND_PATH),
            _source(source_id="outcome", path=_OUTCOME_PATH),
            _source(source_id="calibration", path=_CALIBRATION_PATH),
        ]
    )
    adapter = adapt_tabular_sources_for_planning_mmm(
        PlanningMMMTabularSourceAdapterRequest(
            request_id="adapt-cal",
            tabular_source_result=tabular,
            explicit_role_by_source_id={
                "spend": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
                "outcome": PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME,
                "calibration": PlanningMMMUploadedCSVRole.CALIBRATION_SIGNALS,
            },
        )
    )
    assert adapter.availability is not None
    assert adapter.availability.has_calibration_signals is True
    assert adapter.availability.calibration_signals_source_id == "calibration"
    intake = _intake(tabular, explicit_calibration_source_ids=["calibration"])
    assert intake.envelope is not None
    assert intake.envelope.calibration_signal_sources[0].source_id == "calibration"


def test_missing_tabular_source_result_blocked() -> None:
    result = _intake(None)
    assert (
        result.status
        == PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT
    )


def test_blocked_tabular_source_result_blocked() -> None:
    tabular = TabularSourceInspectionResult(
        request_id="blocked-cal",
        status=TabularSourceInspectionStatus.BLOCKED_MISSING_SOURCE,
    )
    result = _intake(tabular)
    assert (
        result.status
        == PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_TABULAR_SOURCE_NOT_READY
    )


def test_missing_calibration_signal_source_blocked() -> None:
    tabular = _tabular_from_sources(
        [_source(source_id="spend", path=_SPEND_PATH)]
    )
    result = _intake(tabular)
    assert (
        result.status
        == PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_MISSING_CALIBRATION_SIGNAL_SOURCE
    )


def test_duplicate_calibration_signal_source_blocked() -> None:
    tabular = _tabular_from_sources(
        [
            _source(
                source_id="calibration-1",
                path=_CALIBRATION_PATH,
                declared_role_hint="calibration",
            ),
            _source(
                source_id="calibration-2",
                path=_CALIBRATION_PATH,
                declared_role_hint="calibration_signals",
            ),
        ]
    )
    result = _intake(tabular)
    blocked_status = (
        PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_DUPLICATE_CALIBRATION_SIGNAL_SOURCE
    )
    assert result.status == blocked_status


def test_missing_required_columns_blocked() -> None:
    tabular = _tabular_from_sources(
        [_source(source_id="calibration", path=_CALIBRATION_PATH)]
    )
    result = _intake(
        tabular,
        explicit_calibration_source_ids=["calibration"],
        required_columns=["channel", "metric", "estimand", "lift", "missing_col"],
    )
    assert (
        result.status
        == PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_MISSING_REQUIRED_COLUMNS
    )


def test_optional_columns_missing_warning_only() -> None:
    tabular = _tabular_from_sources(
        [
            _source(source_id="spend", path=_SPEND_PATH),
            _source(source_id="calibration", path=_CALIBRATION_PATH),
        ]
    )
    result = _intake(
        tabular,
        explicit_calibration_source_ids=["calibration"],
        optional_columns=["geo_scope", "evidence_source"],
    )
    assert (
        result.status
        == PlanningMMMCalibrationSignalTabularIntakeStatus.INTAKE_READY_WITH_WARNINGS
    )
    assert PlanningMMMCalibrationSignalTabularIntakeIssueCode.OPTIONAL_COLUMNS_MISSING in (
        result.issues
    )


def test_full_calibration_signal_construction_required_but_unavailable_blocked() -> None:
    tabular = _tabular_from_sources(
        [_source(source_id="calibration", path=_CALIBRATION_PATH)]
    )
    result = _intake(
        tabular,
        explicit_calibration_source_ids=["calibration"],
        require_full_calibration_signal_construction=True,
    )
    blocked_status = (
        PlanningMMMCalibrationSignalTabularIntakeStatus.BLOCKED_CALIBRATION_SIGNAL_CONTRACT_UNAVAILABLE
    )
    assert result.status == blocked_status


def test_deferred_mapping_preserved() -> None:
    tabular = _tabular_from_sources(
        [_source(source_id="calibration", path=_CALIBRATION_PATH)]
    )
    result = _intake(tabular, explicit_calibration_source_ids=["calibration"])
    assert result.envelope is not None
    assert result.envelope.deferred_mappings
    deferred = result.envelope.deferred_mappings[0]
    assert deferred.metadata_compatible is True
    assert (
        deferred.construction_mode
        == PlanningMMMCalibrationSignalConstructionMode.CALIBRATION_SIGNAL_CONSTRUCTION_DEFERRED
    )
    assert PlanningMMMCalibrationSignalTabularIntakeIssueCode.DEFERRED_MAPPING_CREATED in (
        result.issues
    )


def test_data_source_refs_preserved() -> None:
    tabular = _tabular_from_sources(
        [_source(source_id="calibration", path=_CALIBRATION_PATH)]
    )
    result = _intake(tabular, explicit_calibration_source_ids=["calibration"])
    assert result.envelope is not None
    assert len(result.envelope.data_source_refs) == 1


def test_tabular_source_refs_preserved() -> None:
    tabular = _tabular_from_sources(
        [_source(source_id="calibration", path=_CALIBRATION_PATH)]
    )
    result = _intake(tabular, explicit_calibration_source_ids=["calibration"])
    assert result.envelope is not None
    assert len(result.envelope.tabular_source_references) == 1


def test_lineage_preserved() -> None:
    tabular = _tabular_from_sources(
        [_source(source_id="calibration", path=_CALIBRATION_PATH)]
    )
    result = _intake(tabular, explicit_calibration_source_ids=["calibration"])
    assert result.lineage.get("intake_stage") == "planning_mmm_calibration_signal_tabular_intake"
    assert PlanningMMMCalibrationSignalTabularIntakeIssueCode.LINEAGE_PRESERVED in result.issues


def test_execution_flags_remain_false() -> None:
    tabular = _tabular_from_sources(
        [_source(source_id="calibration", path=_CALIBRATION_PATH)]
    )
    result = _intake(tabular, explicit_calibration_source_ids=["calibration"])
    assert result.envelope is not None
    for flag, value in result.envelope.execution_allowed.items():
        assert value is False, flag


def test_summarize_metadata_only() -> None:
    tabular = _tabular_from_sources(
        [_source(source_id="calibration", path=_CALIBRATION_PATH)]
    )
    result = _intake(tabular, explicit_calibration_source_ids=["calibration"])
    summary = summarize_calibration_signal_tabular_intake(result)
    execution_allowed = summary["execution_allowed"]
    assert isinstance(execution_allowed, dict)
    assert execution_allowed["model_execution"] is False


def test_no_csv_reread_in_modules() -> None:
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "read_csv" not in source
        assert "import pandas" not in source


def test_no_model_fitting_or_calibration_math() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")
    assert "DecisionSurface" not in source
    assert "RecommendationContract" not in source
    assert "fit(" not in source


def test_no_metric_recomputation_fields() -> None:
    tabular = _tabular_from_sources(
        [_source(source_id="calibration", path=_CALIBRATION_PATH)]
    )
    result = _intake(tabular, explicit_calibration_source_ids=["calibration"])
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in result.model_dump()
