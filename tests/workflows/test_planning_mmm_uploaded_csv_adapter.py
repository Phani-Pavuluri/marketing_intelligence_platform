"""Tests for Planning/MMM uploaded CSV adapter workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.intake_assets import DataAssetType
from mip.contracts.planning_mmm_uploaded_csv_adapter import (
    PlanningMMMUploadedCSVAdapterIssueCode,
    PlanningMMMUploadedCSVAdapterRequest,
    PlanningMMMUploadedCSVAdapterResult,
    PlanningMMMUploadedCSVAdapterStatus,
    PlanningMMMUploadedCSVRole,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationRequest,
    UploadedCSVMaterializationResult,
    UploadedCSVMaterializationStatus,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.workflows.planning_mmm_uploaded_csv_adapter import (
    adapt_uploaded_csvs_for_planning_mmm,
    build_intake_manifest_compatibility_from_uploaded_csv_adapter_result,
    build_mmm_config_draft_compatibility_from_uploaded_csv_adapter_result,
    build_model_readiness_compatibility_from_uploaded_csv_adapter_result,
    build_planning_mmm_data_source_refs_from_uploaded_csv_adapter_result,
    build_planning_mmm_input_availability_from_uploaded_csv_adapter_result,
)
from mip.workflows.uploaded_csv_materialization import materialize_uploaded_csvs

_FIXTURE_ROOT = Path("examples/fixtures/planning_mmm_uploaded_csv_adapter")
_SPEND_PATH = str(_FIXTURE_ROOT / "historical_spend.csv")
_OUTCOME_PATH = str(_FIXTURE_ROOT / "historical_outcome.csv")
_TAXONOMY_PATH = str(_FIXTURE_ROOT / "channel_taxonomy.csv")
_BUDGET_PATH = str(_FIXTURE_ROOT / "budget_constraints.csv")
_CALIBRATION_PATH = str(_FIXTURE_ROOT / "calibration_signals.csv")
_CONFIG_PATH = str(_FIXTURE_ROOT / "model_config.csv")
_WORKFLOW_SOURCE = Path("src/mip/workflows/planning_mmm_uploaded_csv_adapter.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/planning_mmm_uploaded_csv_adapter.py")
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


def _materialize(
    sources: list[UploadedCSVSource],
    *,
    request_id: str = "mat-1",
) -> UploadedCSVMaterializationResult:
    return materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(request_id=request_id, sources=sources)
    )


def _adapt(
    materialization_result: UploadedCSVMaterializationResult,
    *,
    request_id: str = "adapt-1",
    explicit_role_by_source_id: dict[str, PlanningMMMUploadedCSVRole] | None = None,
    required_columns_by_role: dict[str, list[str]] | None = None,
) -> PlanningMMMUploadedCSVAdapterResult:
    return adapt_uploaded_csvs_for_planning_mmm(
        PlanningMMMUploadedCSVAdapterRequest(
            request_id=request_id,
            materialization_result=materialization_result,
            explicit_role_by_source_id=explicit_role_by_source_id or {},
            required_columns_by_role=required_columns_by_role or {},
        )
    )


def test_successful_adapter_with_explicit_roles() -> None:
    materialization = _materialize(_core_sources())
    result = _adapt(materialization, explicit_role_by_source_id=_explicit_roles())
    assert result.status in {
        PlanningMMMUploadedCSVAdapterStatus.ADAPTED,
        PlanningMMMUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS,
    }
    assert result.availability is not None
    assert result.availability.has_historical_spend
    assert result.availability.has_historical_outcome
    assert len(result.data_source_refs) >= 2
    assert PlanningMMMUploadedCSVAdapterIssueCode.DATA_SOURCE_REF_CREATED in result.issues


def test_successful_adapter_with_declared_role_hints() -> None:
    sources = [
        _source(source_id="spend", path=_SPEND_PATH, declared_role_hint="historical_spend"),
        _source(source_id="outcome", path=_OUTCOME_PATH, declared_role_hint="outcome"),
    ]
    materialization = _materialize(sources)
    result = _adapt(materialization)
    assert result.status in {
        PlanningMMMUploadedCSVAdapterStatus.ADAPTED,
        PlanningMMMUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS,
    }
    assert PlanningMMMUploadedCSVAdapterIssueCode.ROLE_HINT_USED in result.issues


def test_missing_materialization_result_blocked() -> None:
    result = adapt_uploaded_csvs_for_planning_mmm(
        PlanningMMMUploadedCSVAdapterRequest(
            request_id="adapt-1",
            materialization_result=None,
        )
    )
    assert result.status == (
        PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MISSING_MATERIALIZATION_RESULT
    )


def test_materialization_blocked() -> None:
    materialization = _materialize(_core_sources(include_optional=False))
    materialization = materialization.model_copy(
        update={"status": UploadedCSVMaterializationStatus.BLOCKED_EMPTY_FILE}
    )
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    assert result.status == PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MATERIALIZATION_NOT_READY


def test_missing_required_role_blocked() -> None:
    materialization = _materialize([_source(source_id="spend", path=_SPEND_PATH)])
    result = _adapt(
        materialization,
        explicit_role_by_source_id={"spend": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND},
    )
    assert result.status == PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE


def test_duplicate_required_role_blocked() -> None:
    materialization = _materialize(
        [
            _source(source_id="spend1", path=_SPEND_PATH),
            _source(source_id="spend2", path=_SPEND_PATH),
            _source(source_id="outcome", path=_OUTCOME_PATH),
        ]
    )
    result = _adapt(
        materialization,
        explicit_role_by_source_id={
            "spend1": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
            "spend2": PlanningMMMUploadedCSVRole.HISTORICAL_SPEND,
            "outcome": PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME,
        },
    )
    assert result.status == PlanningMMMUploadedCSVAdapterStatus.BLOCKED_DUPLICATE_ROLE


def test_unknown_role_blocked() -> None:
    materialization = _materialize(
        [
            _source(source_id="unknown", path=_SPEND_PATH),
            _source(source_id="outcome", path=_OUTCOME_PATH),
        ]
    )
    result = _adapt(
        materialization,
        explicit_role_by_source_id={"outcome": PlanningMMMUploadedCSVRole.HISTORICAL_OUTCOME},
    )
    assert result.status == PlanningMMMUploadedCSVAdapterStatus.BLOCKED_AMBIGUOUS_ROLE


def test_missing_required_columns_blocked() -> None:
    materialization = _materialize(_core_sources(include_optional=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
        required_columns_by_role={
            str(PlanningMMMUploadedCSVRole.HISTORICAL_SPEND): ["missing_column"],
        },
    )
    assert result.status == PlanningMMMUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS


def test_optional_channel_taxonomy_missing_warning_only() -> None:
    materialization = _materialize(_core_sources(include_optional=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    assert result.status in {
        PlanningMMMUploadedCSVAdapterStatus.ADAPTED,
        PlanningMMMUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS,
    }
    assert (
        PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_CHANNEL_TAXONOMY_MISSING in result.issues
    )


def test_optional_budget_constraints_missing_warning_only() -> None:
    materialization = _materialize(_core_sources(include_optional=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    assert (
        PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_BUDGET_CONSTRAINTS_MISSING
        in result.issues
    )


def test_optional_calibration_signals_missing_warning_only() -> None:
    materialization = _materialize(_core_sources(include_optional=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    assert (
        PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_CALIBRATION_SIGNALS_MISSING
        in result.issues
    )


def test_optional_model_config_missing_warning_only() -> None:
    materialization = _materialize(_core_sources(include_optional=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    assert PlanningMMMUploadedCSVAdapterIssueCode.OPTIONAL_MODEL_CONFIG_MISSING in result.issues


def test_data_source_ref_preserves_lineage_and_hints() -> None:
    materialization = _materialize(_core_sources(include_optional=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    spend_ref = next(
        ref
        for ref in result.data_source_refs
        if ref.asset_type == DataAssetType.MEDIA_SPEND_DATA
    )
    assert spend_ref.source_id == "spend"
    assert spend_ref.declared_scope.get("planning_mmm_role") == "historical_spend"
    assert "normalized_columns" in spend_ref.declared_scope


def test_intake_manifest_compatibility_metadata_only() -> None:
    materialization = _materialize(_core_sources(include_optional=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    compatibility = build_intake_manifest_compatibility_from_uploaded_csv_adapter_result(result)
    assert compatibility["compatibility_status"] == "metadata_only"
    assert compatibility["outcome_source_ref_id"] == "outcome"
    assert "deferred_manifest_fields" in compatibility


def test_mmm_config_draft_compatibility_metadata_only() -> None:
    materialization = _materialize(_core_sources(include_optional=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    compatibility = build_mmm_config_draft_compatibility_from_uploaded_csv_adapter_result(result)
    assert compatibility["compatibility_status"] == "metadata_only"
    assert compatibility["suggested_spend_field"] == "spend"
    assert compatibility["suggested_outcome_field"] == "revenue"


def test_model_readiness_compatibility_metadata_only() -> None:
    materialization = _materialize(_core_sources(include_optional=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    compatibility = build_model_readiness_compatibility_from_uploaded_csv_adapter_result(result)
    assert compatibility["compatibility_status"] == "metadata_only"
    assert compatibility["model_readiness_evaluated"] is False
    assert compatibility["has_historical_spend"] is True


def test_compatibility_helpers() -> None:
    materialization = _materialize(_core_sources())
    result = _adapt(materialization, explicit_role_by_source_id=_explicit_roles())
    refs = build_planning_mmm_data_source_refs_from_uploaded_csv_adapter_result(result)
    availability = build_planning_mmm_input_availability_from_uploaded_csv_adapter_result(result)
    assert len(refs) >= 2
    assert availability.has_historical_spend


def test_no_csv_reread_in_adapter_modules() -> None:
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "read_csv" not in source
        assert "import pandas" not in source


def test_no_mmm_fitting_optimizer_simulator_imports() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")
    assert "DecisionSurface" not in source
    assert "RecommendationContract" not in source
    assert "panel_exp" not in source
    assert "claim_authorization" not in source
    assert "import optimizer" not in source.lower()
    assert "from optimizer" not in source.lower()
    assert "fit(" not in source


def test_shared_core_remains_generic() -> None:
    shared_source = _SHARED_CORE.read_text(encoding="utf-8")
    for role in ("HISTORICAL_SPEND", "CHANNEL_TAXONOMY", "CALIBRATION_SIGNALS"):
        assert role not in shared_source
    assert "PlanningMMMUploadedCSVRole" not in shared_source


def test_no_metric_recomputation_fields() -> None:
    materialization = _materialize(_core_sources(include_optional=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_optional=False),
    )
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in result.model_dump()
