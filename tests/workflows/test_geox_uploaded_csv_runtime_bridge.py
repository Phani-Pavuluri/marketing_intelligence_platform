"""Tests for GeoX uploaded CSV runtime bridge workflow."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from mip.contracts.geox_panel_exp_runtime_call import CLAIM_AUTHORIZATION_OWNER
from mip.contracts.geox_readout_result_ingestion import (
    GeoXReadoutResultIngestionRequest,
    GeoXReadoutResultStatus,
)
from mip.contracts.geox_uploaded_csv_adapter import (
    GeoXUploadedCSVAdapterRequest,
    GeoXUploadedCSVAdapterResult,
    GeoXUploadedCSVAdapterStatus,
    GeoXUploadedCSVRole,
)
from mip.contracts.geox_uploaded_csv_runtime_bridge import (
    GeoXUploadedCSVRuntimeBridgeIssueCode,
    GeoXUploadedCSVRuntimeBridgeRequest,
    GeoXUploadedCSVRuntimeBridgeStatus,
    GeoXUploadedCSVRuntimeColumnMapping,
)
from mip.contracts.uploaded_csv_materialization import (
    UploadedCSVMaterializationRequest,
    UploadedCSVMaterializationResult,
    UploadedCSVMaterializationStatus,
    UploadedCSVSource,
    UploadedCSVSourceType,
)
from mip.workflows.geox_readout_result_ingestion import ingest_geox_readout_result_for_explanation
from mip.workflows.geox_uploaded_csv_adapter import adapt_uploaded_csvs_for_geox_readout
from mip.workflows.geox_uploaded_csv_runtime_bridge import (
    call_geox_post_test_spend_runtime_for_uploaded_csvs,
)
from mip.workflows.uploaded_csv_materialization import materialize_uploaded_csvs

_FIXTURE_ROOT = Path("examples/fixtures/geox_uploaded_csv_adapter")
_KPI_PATH = str(_FIXTURE_ROOT / "kpi_panel.csv")
_SPEND_PATH = str(_FIXTURE_ROOT / "spend_panel.csv")
_ASSIGNMENT_PATH = str(_FIXTURE_ROOT / "assignment_table.csv")
_METADATA_PATH = str(_FIXTURE_ROOT / "experiment_metadata.csv")
_BRIDGE_SOURCE = Path("src/mip/workflows/geox_uploaded_csv_runtime_bridge.py")
_CONTRACT_SOURCE = Path("src/mip/contracts/geox_uploaded_csv_runtime_bridge.py")
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


def _materialize_and_adapt() -> tuple[
    UploadedCSVMaterializationResult,
    GeoXUploadedCSVAdapterResult,
]:
    materialization = materialize_uploaded_csvs(
        UploadedCSVMaterializationRequest(request_id="mat-bridge", sources=_core_sources())
    )
    adapter = adapt_uploaded_csvs_for_geox_readout(
        GeoXUploadedCSVAdapterRequest(
            request_id="adapt-bridge",
            materialization_result=materialization,
            explicit_role_by_source_id=_explicit_roles(),
        )
    )
    return materialization, adapter


def _column_mapping() -> GeoXUploadedCSVRuntimeColumnMapping:
    return GeoXUploadedCSVRuntimeColumnMapping(
        spend_date_column="date",
        spend_geo_column="dma",
        spend_amount_column="spend",
        currency_column="currency",
        assignment_geo_column="dma",
        assignment_cell_column="cell",
        assignment_role_column="treatment",
    )


def _bridge_request(
    materialization: UploadedCSVMaterializationResult | None,
    adapter: GeoXUploadedCSVAdapterResult | None,
    *,
    column_mapping: GeoXUploadedCSVRuntimeColumnMapping | None = None,
) -> GeoXUploadedCSVRuntimeBridgeRequest:
    return GeoXUploadedCSVRuntimeBridgeRequest(
        request_id="bridge-1",
        materialization_result=materialization,
        adapter_result=adapter,
        experiment_id="exp-uploaded-1",
        experiment_type="holdout",
        post_period_start="2026-01-01",
        post_period_end="2026-01-31",
        column_mapping=column_mapping or _column_mapping(),
    )


def test_missing_materialization_result_blocked() -> None:
    _, adapter = _materialize_and_adapt()
    result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(None, adapter)
    )
    assert result.status == (
        GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_MATERIALIZATION_RESULT
    )
    assert GeoXUploadedCSVRuntimeBridgeIssueCode.MISSING_MATERIALIZATION_RESULT in result.issues


def test_materialization_blocked() -> None:
    materialization, adapter = _materialize_and_adapt()
    materialization = materialization.model_copy(
        update={"status": UploadedCSVMaterializationStatus.BLOCKED_EMPTY_FILE}
    )
    result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(materialization, adapter)
    )
    assert result.status == GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MATERIALIZATION_NOT_READY


def test_missing_adapter_result_blocked() -> None:
    materialization, _ = _materialize_and_adapt()
    result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(materialization, None)
    )
    assert result.status == GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_ADAPTER_RESULT


def test_adapter_blocked() -> None:
    materialization, adapter = _materialize_and_adapt()
    adapter = adapter.model_copy(
        update={"status": GeoXUploadedCSVAdapterStatus.BLOCKED_MISSING_REQUIRED_ROLE}
    )
    result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(materialization, adapter)
    )
    assert result.status == GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_ADAPTER_NOT_READY


def test_missing_spend_dataset_blocked() -> None:
    materialization, adapter = _materialize_and_adapt()
    adapter = adapter.model_copy(
        update={
            "role_mappings": [
                mapping
                for mapping in adapter.role_mappings
                if mapping.role != GeoXUploadedCSVRole.SPEND_PANEL
            ],
            "availability": adapter.availability.model_copy(update={"has_spend_panel": False})
            if adapter.availability
            else None,
        }
    )
    result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(materialization, adapter)
    )
    assert result.status == GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_REQUIRED_DATASET


def test_missing_assignment_dataset_blocked() -> None:
    materialization, adapter = _materialize_and_adapt()
    adapter = adapter.model_copy(
        update={
            "role_mappings": [
                mapping
                for mapping in adapter.role_mappings
                if mapping.role != GeoXUploadedCSVRole.ASSIGNMENT_TABLE
            ],
        }
    )
    result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(materialization, adapter)
    )
    assert result.status == GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_REQUIRED_DATASET


def test_missing_dataframe_blocked() -> None:
    materialization, adapter = _materialize_and_adapt()
    materialization = materialization.model_copy(
        update={
            "datasets": [
                dataset.model_copy(update={"dataframe": None})
                if dataset.source_id == "spend"
                else dataset
                for dataset in materialization.datasets
            ]
        }
    )
    result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(materialization, adapter)
    )
    assert result.status == GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_REQUIRED_DATAFRAME


def test_missing_required_column_mapping_blocked() -> None:
    materialization, adapter = _materialize_and_adapt()
    result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(
            materialization,
            adapter,
            column_mapping=GeoXUploadedCSVRuntimeColumnMapping(
                spend_date_column="",
                spend_geo_column="dma",
                spend_amount_column="spend",
            ),
        )
    )
    assert result.status == (
        GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_MISSING_REQUIRED_COLUMN_MAPPING
    )


def test_package_runtime_unavailable_blocked() -> None:
    materialization, adapter = _materialize_and_adapt()

    def _raise_import() -> None:
        msg = "simulated panel_exp import failure"
        raise ImportError(msg)

    with patch(
        "mip.workflows.geox_uploaded_csv_runtime_bridge._import_panel_exp_runtime",
        side_effect=_raise_import,
    ):
        result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
            _bridge_request(materialization, adapter)
        )
    assert result.status == GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_PACKAGE_RUNTIME_UNAVAILABLE
    assert GeoXUploadedCSVRuntimeBridgeIssueCode.PACKAGE_RUNTIME_UNAVAILABLE in result.issues


def test_package_runtime_failure_blocked() -> None:
    materialization, adapter = _materialize_and_adapt()

    def _raise_runtime(_input):  # type: ignore[no-untyped-def]
        msg = "simulated package runtime failure"
        raise RuntimeError(msg)

    with patch(
        "mip.workflows.geox_uploaded_csv_runtime_bridge._import_panel_exp_runtime",
    ) as mock_import:
        mock_import.return_value = {
            "PostTestSpendInput": lambda **kwargs: kwargs,
            "build_post_test_spend_evidence": _raise_runtime,
            "build_trusted_readout_spend_handoff": lambda evidence: {},
        }
        result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
            _bridge_request(materialization, adapter)
        )
    assert result.status == GeoXUploadedCSVRuntimeBridgeStatus.BLOCKED_PACKAGE_RUNTIME_FAILED


def test_successful_runtime_call_with_uploaded_csv_dataframes() -> None:
    pytest.importorskip("panel_exp")
    materialization, adapter = _materialize_and_adapt()
    result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(materialization, adapter)
    )
    assert result.status in {
        GeoXUploadedCSVRuntimeBridgeStatus.RUNTIME_COMPLETED,
        GeoXUploadedCSVRuntimeBridgeStatus.RUNTIME_COMPLETED_WITH_WARNINGS,
    }
    assert result.evidence_artifact is not None
    assert result.trusted_handoff_artifact is not None
    assert result.package_output_summary
    assert GeoXUploadedCSVRuntimeBridgeIssueCode.PACKAGE_EVIDENCE_CREATED in result.issues
    assert GeoXUploadedCSVRuntimeBridgeIssueCode.TRUSTED_HANDOFF_CREATED in result.issues
    assert GeoXUploadedCSVRuntimeBridgeIssueCode.CSV_REPARSE_AVOIDED in result.issues
    assert result.lineage.get("spend_source_id") == "spend"
    assert result.evidence_artifact.claim_authorization_owner == CLAIM_AUTHORIZATION_OWNER


def test_package_computed_spend_delta_in_summary_only() -> None:
    pytest.importorskip("panel_exp")
    materialization, adapter = _materialize_and_adapt()
    result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(materialization, adapter)
    )
    assert result.evidence_artifact is not None
    summary = result.package_output_summary
    if "package_computed_spend_delta" in summary:
        assert "spend_delta" not in result.evidence_artifact.model_dump()


def test_no_csv_reread_in_bridge_modules() -> None:
    for path in (_BRIDGE_SOURCE, _CONTRACT_SOURCE):
        source = path.read_text(encoding="utf-8")
        assert "read_csv" not in source
        assert "import pandas" not in source


def test_no_panel_exp_top_level_import_in_bridge_module() -> None:
    source = _BRIDGE_SOURCE.read_text(encoding="utf-8")
    assert "import panel_exp" not in source
    assert "from panel_exp" not in source


def test_result_ingestion_compatibility() -> None:
    pytest.importorskip("panel_exp")
    materialization, adapter = _materialize_and_adapt()
    bridge_result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(materialization, adapter)
    )
    ingestion = ingest_geox_readout_result_for_explanation(
        GeoXReadoutResultIngestionRequest(
            request_id="ingest-uploaded-bridge",
            evidence_artifact=bridge_result.evidence_artifact,
            trusted_handoff_artifact=bridge_result.trusted_handoff_artifact,
        )
    )
    assert ingestion.status in {
        GeoXReadoutResultStatus.EXPLAINED_READY_PACKAGE_RESULT,
        GeoXReadoutResultStatus.EXPLAINED_BLOCKED_PACKAGE_RESULT,
        GeoXReadoutResultStatus.EXPLAINED_DIAGNOSTIC_ONLY_PACKAGE_RESULT,
    }
    assert ingestion.result_envelope is not None


def test_no_metric_recomputation_fields() -> None:
    pytest.importorskip("panel_exp")
    materialization, adapter = _materialize_and_adapt()
    result = call_geox_post_test_spend_runtime_for_uploaded_csvs(
        _bridge_request(materialization, adapter)
    )
    payload = result.model_dump_json().lower()
    assert "mip_computed" not in payload
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in result.model_dump()
