"""Tests for GeoX uploaded CSV adapter workflow."""

from __future__ import annotations

from pathlib import Path

import pytest

from mip.contracts.geox_readout_input_resolution import (
    DatasetSemanticType,
    DatasetSourceType,
    GeoXReadoutInputResolutionRequest,
)
from mip.contracts.geox_readout_source_inspection import SourceInspectionStatus
from mip.contracts.geox_uploaded_csv_adapter import (
    GeoXUploadedCSVAdapterIssueCode,
    GeoXUploadedCSVAdapterRequest,
    GeoXUploadedCSVAdapterResult,
    GeoXUploadedCSVAdapterStatus,
    GeoXUploadedCSVRole,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationRequest,
    UploadedCSVMaterializationResult,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.workflows.geox_readout_input_resolution import resolve_geox_readout_inputs
from mip.workflows.geox_readout_source_inspection import inspect_dataset_reference
from mip.workflows.geox_uploaded_csv_adapter import (
    adapt_uploaded_csvs_for_geox_readout,
    build_geox_dataset_references_from_uploaded_csv_adapter_result,
    build_geox_materialized_input_availability_from_uploaded_csv_adapter_result,
)
from mip.workflows.uploaded_csv_materialization import materialize_uploaded_csvs

_FIXTURE_ROOT = Path("examples/fixtures/geox_uploaded_csv_adapter")
_KPI_PATH = str(_FIXTURE_ROOT / "kpi_panel.csv")
_SPEND_PATH = str(_FIXTURE_ROOT / "spend_panel.csv")
_ASSIGNMENT_PATH = str(_FIXTURE_ROOT / "assignment_table.csv")
_METADATA_PATH = str(_FIXTURE_ROOT / "experiment_metadata.csv")
_WORKFLOW_SOURCE = Path("src/mip/workflows/geox_uploaded_csv_adapter.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/geox_uploaded_csv_adapter.py")
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
    explicit_role_by_source_id: dict[str, GeoXUploadedCSVRole] | None = None,
    required_columns_by_role: dict[str, list[str]] | None = None,
) -> GeoXUploadedCSVAdapterResult:
    return adapt_uploaded_csvs_for_geox_readout(
        GeoXUploadedCSVAdapterRequest(
            request_id=request_id,
            materialization_result=materialization_result,
            explicit_role_by_source_id=explicit_role_by_source_id or {},
            required_columns_by_role=required_columns_by_role or {},
        )
    )


def _core_sources(*, include_metadata: bool = True) -> list[UploadedCSVSource]:
    sources = [
        _source(source_id="kpi", path=_KPI_PATH),
        _source(source_id="spend", path=_SPEND_PATH),
        _source(source_id="assignment", path=_ASSIGNMENT_PATH),
    ]
    if include_metadata:
        sources.append(_source(source_id="metadata", path=_METADATA_PATH))
    return sources


def _explicit_roles(*, include_metadata: bool = True) -> dict[str, GeoXUploadedCSVRole]:
    roles = {
        "kpi": GeoXUploadedCSVRole.KPI_PANEL,
        "spend": GeoXUploadedCSVRole.SPEND_PANEL,
        "assignment": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
    }
    if include_metadata:
        roles["metadata"] = GeoXUploadedCSVRole.EXPERIMENT_METADATA
    return roles


def test_successful_adapter_with_explicit_roles() -> None:
    materialization = _materialize(_core_sources())
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(),
    )
    assert result.status in {
        GeoXUploadedCSVAdapterStatus.ADAPTED,
        GeoXUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS,
    }
    assert result.availability is not None
    assert result.availability.has_kpi_panel is True
    assert result.availability.has_spend_panel is True
    assert result.availability.has_assignment_table is True
    assert len(result.dataset_references) >= 3
    assert GeoXUploadedCSVAdapterIssueCode.ROLE_EXPLICITLY_PROVIDED in result.issues


def test_successful_adapter_with_declared_role_hints() -> None:
    sources = [
        _source(source_id="kpi", path=_KPI_PATH, declared_role_hint="kpi_panel"),
        _source(source_id="spend", path=_SPEND_PATH, declared_role_hint="spend"),
        _source(source_id="assignment", path=_ASSIGNMENT_PATH, declared_role_hint="assignment"),
    ]
    materialization = _materialize(sources)
    result = _adapt(materialization)
    assert result.status in {
        GeoXUploadedCSVAdapterStatus.ADAPTED,
        GeoXUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS,
    }
    assert GeoXUploadedCSVAdapterIssueCode.ROLE_HINT_USED in result.issues
    assert GeoXUploadedCSVAdapterIssueCode.OPTIONAL_METADATA_MISSING in result.issues


def test_missing_materialization_result_blocked() -> None:
    result = adapt_uploaded_csvs_for_geox_readout(
        GeoXUploadedCSVAdapterRequest(request_id="missing")
    )
    assert result.status == GeoXUploadedCSVAdapterStatus.BLOCKED_MISSING_MATERIALIZATION_RESULT


def test_materialization_blocked() -> None:
    materialization = _materialize([])
    result = _adapt(materialization)
    assert result.status == GeoXUploadedCSVAdapterStatus.BLOCKED_MATERIALIZATION_NOT_READY


def test_missing_required_role_blocked() -> None:
    materialization = _materialize([_source(source_id="kpi", path=_KPI_PATH)])
    result = _adapt(
        materialization,
        explicit_role_by_source_id={"kpi": GeoXUploadedCSVRole.KPI_PANEL},
    )
    assert result.status == GeoXUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE


def test_duplicate_required_role_blocked() -> None:
    materialization = _materialize(
        [
            _source(source_id="kpi-1", path=_KPI_PATH),
            _source(source_id="kpi-2", path=_KPI_PATH),
            _source(source_id="spend", path=_SPEND_PATH),
            _source(source_id="assignment", path=_ASSIGNMENT_PATH),
        ]
    )
    result = _adapt(
        materialization,
        explicit_role_by_source_id={
            "kpi-1": GeoXUploadedCSVRole.KPI_PANEL,
            "kpi-2": GeoXUploadedCSVRole.KPI_PANEL,
            "spend": GeoXUploadedCSVRole.SPEND_PANEL,
            "assignment": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
        },
    )
    assert result.status == GeoXUploadedCSVAdapterStatus.BLOCKED_DUPLICATE_ROLE


def test_unknown_role_blocked() -> None:
    materialization = _materialize([_source(source_id="unknown", path=_KPI_PATH)])
    result = _adapt(materialization)
    assert result.status == GeoXUploadedCSVAdapterStatus.BLOCKED_AMBIGUOUS_ROLE


def test_missing_required_columns_blocked() -> None:
    materialization = _materialize(_core_sources(include_metadata=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
        required_columns_by_role={
            str(GeoXUploadedCSVRole.KPI_PANEL): ["date", "dma", "missing_metric"],
        },
    )
    assert result.status == GeoXUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS


def test_optional_metadata_missing_warning_only() -> None:
    materialization = _materialize(_core_sources(include_metadata=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
    )
    assert result.status == GeoXUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS
    assert GeoXUploadedCSVAdapterIssueCode.OPTIONAL_METADATA_MISSING in result.issues


def test_dataset_reference_preserves_lineage_and_hints() -> None:
    materialization = _materialize(
        [_source(source_id="kpi", path=_KPI_PATH, declared_role_hint="kpi_panel")]
        + [
            _source(source_id="spend", path=_SPEND_PATH),
            _source(source_id="assignment", path=_ASSIGNMENT_PATH),
        ]
    )
    result = _adapt(
        materialization,
        explicit_role_by_source_id={
            "spend": GeoXUploadedCSVRole.SPEND_PANEL,
            "assignment": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
        },
    )
    kpi_ref = next(
        ref
        for ref in result.dataset_references
        if ref.semantic_type == DatasetSemanticType.KPI_PANEL
    )
    assert kpi_ref.source_type == DatasetSourceType.UPLOADED_CSV
    assert kpi_ref.lineage["declared_role_hint"] == "kpi_panel"
    assert kpi_ref.lineage["geox_uploaded_csv_adapter"] == "true"


def test_source_inspection_compatibility() -> None:
    materialization = _materialize(_core_sources(include_metadata=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
    )
    for dataset_ref in build_geox_dataset_references_from_uploaded_csv_adapter_result(result):
        inspection = inspect_dataset_reference(dataset_ref)
        assert inspection.inspection_status == SourceInspectionStatus.INSPECTED


def test_input_resolution_compatibility() -> None:
    materialization = _materialize(_core_sources(include_metadata=False))
    adapter_result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
    )
    refs = build_geox_dataset_references_from_uploaded_csv_adapter_result(adapter_result)
    resolution = resolve_geox_readout_inputs(
        GeoXReadoutInputResolutionRequest(
            request_id="resolve-1",
            dataset_refs=refs,
            geox_runtime_available=True,
        )
    )
    status = str(resolution.resolution_status)
    assert resolution.handoff is not None or status.startswith("blocked")


def test_no_csv_reread_in_adapter_module() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")
    assert "read_csv" not in source
    assert "import pandas" not in source


def test_no_csv_reread_when_adapting(monkeypatch: pytest.MonkeyPatch) -> None:
    materialization = _materialize(_core_sources(include_metadata=False))

    def _fail_read_csv(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise AssertionError("read_csv must not be called during GeoX adapter")

    monkeypatch.setattr("mip.workflows.uploaded_csv_materialization.pd.read_csv", _fail_read_csv)
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
    )
    assert result.status == GeoXUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS


def test_no_panel_exp_import_or_call() -> None:
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "import panel_exp" not in source
        assert "from panel_exp" not in source


def test_no_metric_recomputation_fields() -> None:
    materialization = _materialize(_core_sources(include_metadata=False))
    result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
    )
    schema = result.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_shared_core_remains_generic() -> None:
    shared_source = _SHARED_CORE.read_text(encoding="utf-8")
    for token in ("KPI_PANEL", "SPEND_PANEL", "ASSIGNMENT_TABLE", "EXPERIMENT_METADATA"):
        assert token not in shared_source


def test_materialized_input_availability_helper() -> None:
    materialization = _materialize(_core_sources(include_metadata=False))
    adapter_result = _adapt(
        materialization,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
    )
    availability = build_geox_materialized_input_availability_from_uploaded_csv_adapter_result(
        adapter_result
    )
    assert availability.has_materialized_spend_df is True
    assert availability.has_materialized_assignment_df is True
    assert availability.materialized_spend_ref_optional == _SPEND_PATH
