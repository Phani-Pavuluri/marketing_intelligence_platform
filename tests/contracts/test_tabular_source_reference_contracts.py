"""Tests for generic tabular source reference contracts."""

from __future__ import annotations

from mip.contracts import (
    RECOMMENDED_NEXT_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_ARTIFACT,
    RECOMMENDED_NEXT_PLANNING_MMM_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_ARTIFACT,
    TabularSourceAccessMode,
    TabularSourceAvailability,
    TabularSourceInspection,
    TabularSourceInspectionResult,
    TabularSourceInspectionStatus,
    TabularSourceIssueCode,
    TabularSourceLineage,
    TabularSourceMaterializationMode,
    TabularSourceReference,
    TabularSourceSchema,
    TabularSourceType,
)
from mip.contracts.tabular_source_reference import TabularSourceColumn

_FORBIDDEN_TOP_LEVEL = (
    "spend_delta",
    "delta_mu",
    "lift",
    "roi",
    "roas",
    "incrementality",
    "optimal_budget",
    "marginal_roi",
    "recommendation",
)

_FUTURE_SOURCE_TYPES = (
    TabularSourceType.DATABRICKS_TABLE,
    TabularSourceType.WAREHOUSE_TABLE,
    TabularSourceType.API_EXTRACT,
    TabularSourceType.REGISTERED_TABLE,
    TabularSourceType.REGISTERED_ARTIFACT,
)


def test_required_enums_exist() -> None:
    assert TabularSourceType.UPLOADED_CSV in TabularSourceType
    assert TabularSourceAccessMode.LOCAL_FILE in TabularSourceAccessMode
    assert TabularSourceInspectionStatus.INSPECTED in TabularSourceInspectionStatus
    assert TabularSourceMaterializationMode.MATERIALIZED_IN_MEMORY in (
        TabularSourceMaterializationMode
    )
    assert TabularSourceIssueCode.SOURCE_REFERENCE_CREATED in TabularSourceIssueCode


def test_future_source_types_are_enum_only() -> None:
    for source_type in _FUTURE_SOURCE_TYPES:
        assert source_type in TabularSourceType
        assert isinstance(source_type.value, str)


def test_models_serialize() -> None:
    reference = TabularSourceReference(
        source_id="src-1",
        source_type=TabularSourceType.WAREHOUSE_TABLE,
        access_mode=TabularSourceAccessMode.REFERENCE_ONLY,
        materialization_mode=TabularSourceMaterializationMode.REFERENCE_ONLY,
        source_uri="warehouse://db/schema/table",
        source_name="events",
    )
    payload = reference.model_dump()
    assert payload["source_type"] == "warehouse_table"


def test_generic_contracts_do_not_require_pandas() -> None:
    from pathlib import Path

    contract_source = Path("src/mip/contracts/tabular_source_reference.py").read_text(
        encoding="utf-8"
    )
    assert "import pandas" not in contract_source
    assert "read_csv" not in contract_source


def test_source_reference_can_represent_uploaded_csv() -> None:
    reference = TabularSourceReference(
        source_id="spend",
        source_type=TabularSourceType.UPLOADED_CSV,
        access_mode=TabularSourceAccessMode.LOCAL_FILE,
        materialization_mode=TabularSourceMaterializationMode.MATERIALIZED_IN_MEMORY,
        source_uri="/tmp/spend.csv",
        source_name="spend.csv",
        declared_role_hint="historical_spend",
    )
    assert reference.source_type == TabularSourceType.UPLOADED_CSV


def test_source_reference_can_represent_reference_only_metadata() -> None:
    reference = TabularSourceReference(
        source_id="db-table-1",
        source_type=TabularSourceType.DATABRICKS_TABLE,
        access_mode=TabularSourceAccessMode.REFERENCE_ONLY,
        materialization_mode=TabularSourceMaterializationMode.REFERENCE_ONLY,
        source_uri="databricks://catalog.schema.table",
        source_name="catalog.schema.table",
        schema=TabularSourceSchema(
            column_names=["date", "channel", "spend"],
            normalized_column_names=["date", "channel", "spend"],
            schema_source="databricks_metadata",
        ),
        lineage=TabularSourceLineage(
            source_id="db-table-1",
            source_type=TabularSourceType.DATABRICKS_TABLE,
            source_uri="databricks://catalog.schema.table",
            created_from="metadata_only",
        ),
    )
    assert reference.materialization_mode == TabularSourceMaterializationMode.REFERENCE_ONLY


def test_availability_reference_only_and_materialized_cases() -> None:
    reference_only = TabularSourceAvailability(
        has_schema=True,
        has_lineage=True,
        is_reference_only=True,
        is_connector_runtime_required=True,
    )
    materialized = TabularSourceAvailability(
        has_schema=True,
        has_lineage=True,
        has_materialized_dataset=True,
        materialized_dataset_id="materialized:spend",
        is_reference_only=False,
        is_connector_runtime_required=False,
    )
    assert reference_only.is_reference_only is True
    assert materialized.has_materialized_dataset is True


def test_result_no_top_level_metric_fields() -> None:
    schema = TabularSourceInspectionResult.model_json_schema()
    properties = schema.get("properties", {})
    for field in _FORBIDDEN_TOP_LEVEL:
        assert field not in properties


def test_exports_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_PLANNING_MMM_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_ARTIFACT == (
        "MIP_PLANNING_MMM_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001"
    )
    assert RECOMMENDED_NEXT_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_ARTIFACT == (
        "MIP_GEOX_TABULAR_SOURCE_ADAPTER_COMPATIBILITY_001"
    )


def test_inspection_model_accepts_column_metadata() -> None:
    inspection = TabularSourceInspection(
        source_reference=TabularSourceReference(
            source_id="src-1",
            source_type=TabularSourceType.API_EXTRACT,
            access_mode=TabularSourceAccessMode.SCHEMA_ONLY,
            materialization_mode=TabularSourceMaterializationMode.NOT_MATERIALIZED,
        ),
        schema=TabularSourceSchema(
            columns=[TabularSourceColumn(name="date", normalized_name="date")],
            column_names=["date"],
            normalized_column_names=["date"],
        ),
    )
    assert inspection.source_schema is not None
    assert inspection.source_schema.columns[0].name == "date"
