"""Tests for GeoX tabular source adapter compatibility workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.geox_tabular_source_adapter import (
    GeoXTabularSourceAdapterIssueCode,
    GeoXTabularSourceAdapterRequest,
    GeoXTabularSourceAdapterResult,
    GeoXTabularSourceAdapterStatus,
)
from mip.contracts.geox_uploaded_csv_adapter import (
    GeoXUploadedCSVAdapterRequest,
    GeoXUploadedCSVAdapterStatus,
    GeoXUploadedCSVRole,
)
from mip.contracts.tabular_source_reference import (
    TabularSourceInspectionResult,
    TabularSourceInspectionStatus,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationRequest,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.workflows.geox_tabular_source_adapter import (
    adapt_tabular_sources_for_geox_readout,
    build_uploaded_csv_geox_adapter_result_from_tabular_source_adapter_result,
)
from mip.workflows.geox_uploaded_csv_adapter import (
    adapt_uploaded_csvs_for_geox_readout,
    build_geox_dataset_references_from_uploaded_csv_adapter_result,
)
from mip.workflows.tabular_source_inspection import (
    build_tabular_source_inspection_from_uploaded_csv_materialization,
)
from mip.workflows.uploaded_csv_materialization import materialize_uploaded_csvs

_FIXTURE_ROOT = Path("examples/fixtures/geox_uploaded_csv_adapter")
_KPI_PATH = str(_FIXTURE_ROOT / "kpi_panel.csv")
_SPEND_PATH = str(_FIXTURE_ROOT / "spend_panel.csv")
_ASSIGNMENT_PATH = str(_FIXTURE_ROOT / "assignment_table.csv")
_METADATA_PATH = str(_FIXTURE_ROOT / "experiment_metadata.csv")
_WORKFLOW_SOURCE = Path("src/mip/workflows/geox_tabular_source_adapter.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/geox_tabular_source_adapter.py")
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


def _tabular_from_uploaded_csv(
    *,
    include_metadata: bool = True,
    request_id: str = "tabular-geox-1",
) -> TabularSourceInspectionResult:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-tab-geox",
            sources=_core_sources(include_metadata=include_metadata),
        )
    )
    return build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id=request_id,
        materialization_result=materialization,
    )


def _adapt_tabular(
    tabular_result: TabularSourceInspectionResult | None,
    *,
    request_id: str = "adapt-tab-geox",
    explicit_role_by_source_id: dict[str, GeoXUploadedCSVRole] | None = None,
    required_columns_by_role: dict[str, list[str]] | None = None,
) -> GeoXTabularSourceAdapterResult:
    return adapt_tabular_sources_for_geox_readout(
        GeoXTabularSourceAdapterRequest(
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
        GeoXTabularSourceAdapterStatus.ADAPTED,
        GeoXTabularSourceAdapterStatus.ADAPTED_WITH_WARNINGS,
    }
    assert result.availability is not None
    assert result.availability.has_kpi_panel is True
    assert result.availability.has_spend_panel is True
    assert result.availability.has_assignment_table is True
    assert len(result.data_source_refs) >= 3
    assert len(result.tabular_source_references) >= 3
    assert GeoXTabularSourceAdapterIssueCode.DATA_SOURCE_REF_PRESERVED in result.issues


def test_successful_tabular_adapter_with_declared_role_hints() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-hint-geox",
            sources=[
                _source(source_id="kpi", path=_KPI_PATH, declared_role_hint="kpi_panel"),
                _source(source_id="spend", path=_SPEND_PATH, declared_role_hint="spend"),
                _source(
                    source_id="assignment",
                    path=_ASSIGNMENT_PATH,
                    declared_role_hint="assignment",
                ),
            ],
        )
    )
    tabular = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="tabular-hint-geox",
        materialization_result=materialization,
    )
    result = _adapt_tabular(tabular)
    assert result.status in {
        GeoXTabularSourceAdapterStatus.ADAPTED,
        GeoXTabularSourceAdapterStatus.ADAPTED_WITH_WARNINGS,
    }
    assert GeoXTabularSourceAdapterIssueCode.ROLE_HINT_USED in result.issues


def test_uploaded_csv_compatibility_path_equivalent_availability() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-equiv-geox",
            sources=_core_sources(include_metadata=False),
        )
    )
    csv_adapter = adapt_uploaded_csvs_for_geox_readout(
        GeoXUploadedCSVAdapterRequest(
            request_id="adapt-csv-geox",
            materialization_result=materialization,
            explicit_role_by_source_id=_explicit_roles(include_metadata=False),
        )
    )
    tabular = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="tabular-equiv-geox",
        materialization_result=materialization,
    )
    tabular_adapter = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
    )
    assert csv_adapter.availability is not None
    assert tabular_adapter.availability is not None
    assert tabular_adapter.availability.has_kpi_panel == csv_adapter.availability.has_kpi_panel
    assert tabular_adapter.availability.has_spend_panel == csv_adapter.availability.has_spend_panel
    assert (
        tabular_adapter.availability.has_assignment_table
        == csv_adapter.availability.has_assignment_table
    )


def test_missing_tabular_source_result_blocked() -> None:
    result = _adapt_tabular(None)
    assert (
        result.status == GeoXTabularSourceAdapterStatus.BLOCKED_MISSING_TABULAR_SOURCE_RESULT
    )


def test_blocked_tabular_source_result_blocked() -> None:
    tabular = TabularSourceInspectionResult(
        request_id="blocked-tab",
        status=TabularSourceInspectionStatus.BLOCKED_MISSING_SOURCE,
    )
    result = _adapt_tabular(tabular)
    assert result.status == GeoXTabularSourceAdapterStatus.BLOCKED_TABULAR_SOURCE_NOT_READY


def test_missing_required_role_blocked() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-missing-role",
            sources=[_source(source_id="kpi", path=_KPI_PATH)],
        )
    )
    tabular = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="tabular-missing-role",
        materialization_result=materialization,
    )
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id={"kpi": GeoXUploadedCSVRole.KPI_PANEL},
    )
    assert result.status == GeoXTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE


def test_duplicate_required_role_blocked() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-dup",
            sources=[
                _source(source_id="kpi-1", path=_KPI_PATH),
                _source(source_id="kpi-2", path=_KPI_PATH),
                _source(source_id="spend", path=_SPEND_PATH),
                _source(source_id="assignment", path=_ASSIGNMENT_PATH),
            ],
        )
    )
    tabular = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="tabular-dup",
        materialization_result=materialization,
    )
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id={
            "kpi-1": GeoXUploadedCSVRole.KPI_PANEL,
            "kpi-2": GeoXUploadedCSVRole.KPI_PANEL,
            "spend": GeoXUploadedCSVRole.SPEND_PANEL,
            "assignment": GeoXUploadedCSVRole.ASSIGNMENT_TABLE,
        },
    )
    assert result.status == GeoXTabularSourceAdapterStatus.BLOCKED_DUPLICATE_ROLE


def test_ambiguous_unknown_role_blocked() -> None:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(
            request_id="mat-unknown",
            sources=[_source(source_id="unknown", path=_KPI_PATH)],
        )
    )
    tabular = build_tabular_source_inspection_from_uploaded_csv_materialization(
        request_id="tabular-unknown",
        materialization_result=materialization,
    )
    result = _adapt_tabular(tabular)
    assert result.status == GeoXTabularSourceAdapterStatus.BLOCKED_AMBIGUOUS_ROLE


def test_missing_required_columns_blocked() -> None:
    tabular = _tabular_from_uploaded_csv(include_metadata=False)
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
        required_columns_by_role={
            str(GeoXUploadedCSVRole.KPI_PANEL): ["date", "dma", "missing_metric"],
        },
    )
    assert result.status == GeoXTabularSourceAdapterStatus.BLOCKED_MISSING_REQUIRED_COLUMNS


def test_missing_data_source_ref_blocked() -> None:
    tabular = _tabular_from_uploaded_csv(include_metadata=False)
    stripped_inspections = []
    for inspection in tabular.inspections:
        ref = inspection.source_reference.model_copy(update={"data_source_ref": None})
        stripped_inspections.append(inspection.model_copy(update={"source_reference": ref}))
    stripped = tabular.model_copy(update={"inspections": stripped_inspections})
    result = _adapt_tabular(
        stripped,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
    )
    assert result.status == GeoXTabularSourceAdapterStatus.BLOCKED_DATA_SOURCE_REF_UNAVAILABLE


def test_optional_metadata_missing_warning_only() -> None:
    tabular = _tabular_from_uploaded_csv(include_metadata=False)
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
    )
    assert result.status == GeoXTabularSourceAdapterStatus.ADAPTED_WITH_WARNINGS
    assert GeoXTabularSourceAdapterIssueCode.OPTIONAL_GEO_METADATA_MISSING in result.issues


def test_lineage_preserved() -> None:
    tabular = _tabular_from_uploaded_csv(include_metadata=False)
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
        request_id="lineage-geox",
    )
    assert result.lineage.get("adapter_stage") == "geox_tabular_source_adapter"
    assert GeoXTabularSourceAdapterIssueCode.TABULAR_SOURCE_LINEAGE_PRESERVED in result.issues


def test_runtime_bridge_compatibility_helper() -> None:
    tabular = _tabular_from_uploaded_csv(include_metadata=False)
    tabular_result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
    )
    uploaded_shape = build_uploaded_csv_geox_adapter_result_from_tabular_source_adapter_result(
        tabular_result
    )
    assert uploaded_shape.status in {
        GeoXUploadedCSVAdapterStatus.ADAPTED,
        GeoXUploadedCSVAdapterStatus.ADAPTED_WITH_WARNINGS,
    }
    refs = build_geox_dataset_references_from_uploaded_csv_adapter_result(uploaded_shape)
    assert len(refs) >= 3
    assert uploaded_shape.availability is not None
    assert uploaded_shape.availability.has_spend_panel is True


def test_no_csv_reread_in_geox_tabular_adapter_modules() -> None:
    for path in (_WORKFLOW_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "read_csv" not in source
        assert "import pandas" not in source


def test_no_connector_runtime_patterns() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8").lower()
    for pattern in _FORBIDDEN_RUNTIME_PATTERNS:
        assert pattern not in source


def test_no_panel_exp_or_causal_computation() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")
    assert "import panel_exp" not in source
    assert "from panel_exp" not in source
    assert "fit(" not in source


def test_no_metric_recomputation_fields() -> None:
    tabular = _tabular_from_uploaded_csv(include_metadata=False)
    result = _adapt_tabular(
        tabular,
        explicit_role_by_source_id=_explicit_roles(include_metadata=False),
    )
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in result.model_dump()
