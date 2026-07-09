"""Tests for GeoX fixture materialization workflow."""

from __future__ import annotations

from pathlib import Path

from mip.contracts.geox_fixture_materialization import (
    GeoXFixtureDatasetMaterializationRequest,
    GeoXFixtureMaterializationPolicy,
    GeoXFixtureMaterializationRequest,
    GeoXFixtureMaterializationStatus,
    GeoXMaterializedDatasetRole,
)
from mip.contracts.geox_readout_input_resolution import (
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
)
from mip.workflows.geox_fixture_materialization import (
    build_materialized_input_availability_from_fixture_result,
    materialize_geox_fixture_dataset,
    materialize_geox_readout_fixtures,
)

_FIXTURE_ROOT = Path("examples/fixtures/geox_readout_materialization")
_SPEND_PATH = str(_FIXTURE_ROOT / "spend_panel.csv")
_ASSIGNMENT_PATH = str(_FIXTURE_ROOT / "assignment_table.csv")
_WORKFLOW_SOURCE = Path("src/mip/workflows/geox_fixture_materialization.py")


def _ref(
    *,
    dataset_ref_id: str,
    source_type: DatasetSourceType,
    path: str,
    semantic_type: DatasetSemanticType,
) -> DatasetReference:
    return DatasetReference(
        dataset_ref_id=dataset_ref_id,
        source_type=source_type,
        semantic_type=semantic_type,
        source_uri_or_handle=f"registered://{path}",
        file_name_or_table_name=path,
        declared_or_detected_columns=[],
        classification_confidence=0.9,
    )


def test_materialize_spend_csv_fixture() -> None:
    result = materialize_geox_fixture_dataset(
        GeoXFixtureDatasetMaterializationRequest(
            dataset_ref=_ref(
                dataset_ref_id="geox-fixture-spend-panel",
                source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                path=_SPEND_PATH,
                semantic_type=DatasetSemanticType.SPEND_PANEL,
            ),
            role=GeoXMaterializedDatasetRole.SPEND,
            required_columns=["date", "dma", "spend", "currency"],
        )
    )
    assert result.status == GeoXFixtureMaterializationStatus.MATERIALIZED
    assert result.spend_dataset is not None
    assert result.spend_dataset.row_count >= 4
    assert "spend" in result.spend_dataset.columns


def test_materialize_assignment_csv_fixture() -> None:
    result = materialize_geox_fixture_dataset(
        GeoXFixtureDatasetMaterializationRequest(
            dataset_ref=_ref(
                dataset_ref_id="geox-fixture-assignment-table",
                source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                path=_ASSIGNMENT_PATH,
                semantic_type=DatasetSemanticType.ASSIGNMENT_TABLE,
            ),
            role=GeoXMaterializedDatasetRole.ASSIGNMENT,
            required_columns=["dma", "cell", "treatment"],
        )
    )
    assert result.status == GeoXFixtureMaterializationStatus.MATERIALIZED
    assert result.assignment_dataset is not None
    assert result.assignment_dataset.dataset_ref_id == "geox-fixture-assignment-table"


def test_materialize_both_spend_and_assignment() -> None:
    result = materialize_geox_readout_fixtures(
        GeoXFixtureMaterializationRequest(
            request_id="both",
            dataset_requests=[
                GeoXFixtureDatasetMaterializationRequest(
                    dataset_ref=_ref(
                        dataset_ref_id="geox-fixture-spend-panel",
                        source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                        path=_SPEND_PATH,
                        semantic_type=DatasetSemanticType.SPEND_PANEL,
                    ),
                    role=GeoXMaterializedDatasetRole.SPEND,
                    required_columns=["date", "dma", "spend"],
                ),
                GeoXFixtureDatasetMaterializationRequest(
                    dataset_ref=_ref(
                        dataset_ref_id="geox-fixture-assignment-table",
                        source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                        path=_ASSIGNMENT_PATH,
                        semantic_type=DatasetSemanticType.ASSIGNMENT_TABLE,
                    ),
                    role=GeoXMaterializedDatasetRole.ASSIGNMENT,
                    required_columns=["dma", "cell", "treatment"],
                ),
            ],
        )
    )
    assert result.status == GeoXFixtureMaterializationStatus.MATERIALIZED
    assert result.spend_dataset is not None
    assert result.assignment_dataset is not None
    assert len(result.materialized_datasets) == 2


def test_missing_required_column_blocked() -> None:
    result = materialize_geox_fixture_dataset(
        GeoXFixtureDatasetMaterializationRequest(
            dataset_ref=_ref(
                dataset_ref_id="geox-fixture-spend-panel",
                source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                path=_SPEND_PATH,
                semantic_type=DatasetSemanticType.SPEND_PANEL,
            ),
            role=GeoXMaterializedDatasetRole.SPEND,
            required_columns=["date", "dma", "spend", "nonexistent_column"],
        )
    )
    assert result.status == GeoXFixtureMaterializationStatus.BLOCKED_DECLARED_COLUMNS_MISSING


def test_unsupported_source_type_blocked() -> None:
    result = materialize_geox_fixture_dataset(
        GeoXFixtureDatasetMaterializationRequest(
            dataset_ref=_ref(
                dataset_ref_id="warehouse-spend",
                source_type=DatasetSourceType.WAREHOUSE_TABLE,
                path=_SPEND_PATH,
                semantic_type=DatasetSemanticType.SPEND_PANEL,
            ),
            role=GeoXMaterializedDatasetRole.SPEND,
            required_columns=["date", "dma", "spend"],
        )
    )
    assert result.status == GeoXFixtureMaterializationStatus.BLOCKED_SOURCE_TYPE_UNSUPPORTED


def test_path_outside_allowed_fixture_root_blocked() -> None:
    result = materialize_geox_fixture_dataset(
        GeoXFixtureDatasetMaterializationRequest(
            dataset_ref=_ref(
                dataset_ref_id="outside",
                source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                path="examples/fixtures/stage_a/manifest.json",
                semantic_type=DatasetSemanticType.SPEND_PANEL,
            ),
            role=GeoXMaterializedDatasetRole.SPEND,
            required_columns=[],
        )
    )
    assert result.status == GeoXFixtureMaterializationStatus.BLOCKED_LOCAL_PATH_NOT_ALLOWED


def test_missing_file_blocked() -> None:
    result = materialize_geox_fixture_dataset(
        GeoXFixtureDatasetMaterializationRequest(
            dataset_ref=_ref(
                dataset_ref_id="missing",
                source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                path=str(_FIXTURE_ROOT / "does_not_exist.csv"),
                semantic_type=DatasetSemanticType.SPEND_PANEL,
            ),
            role=GeoXMaterializedDatasetRole.SPEND,
            required_columns=[],
        )
    )
    assert result.status == GeoXFixtureMaterializationStatus.BLOCKED_LOCAL_FILE_NOT_FOUND


def test_unsupported_extension_blocked() -> None:
    policy = GeoXFixtureMaterializationPolicy(allowed_file_extensions=[".csv"])
    result = materialize_geox_fixture_dataset(
        GeoXFixtureDatasetMaterializationRequest(
            dataset_ref=_ref(
                dataset_ref_id="json-file",
                source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                path="examples/fixtures/geox_readout_materialization/manifest.json",
                semantic_type=DatasetSemanticType.SPEND_PANEL,
            ),
            role=GeoXMaterializedDatasetRole.SPEND,
            required_columns=[],
        ),
        policy=policy,
    )
    assert result.status == GeoXFixtureMaterializationStatus.BLOCKED_FILE_FORMAT_UNSUPPORTED


def test_materialization_disabled_blocked() -> None:
    policy = GeoXFixtureMaterializationPolicy(enabled=False)
    result = materialize_geox_fixture_dataset(
        GeoXFixtureDatasetMaterializationRequest(
            dataset_ref=_ref(
                dataset_ref_id="geox-fixture-spend-panel",
                source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                path=_SPEND_PATH,
                semantic_type=DatasetSemanticType.SPEND_PANEL,
            ),
            role=GeoXMaterializedDatasetRole.SPEND,
            required_columns=["date"],
        ),
        policy=policy,
    )
    assert result.status == GeoXFixtureMaterializationStatus.BLOCKED_MATERIALIZATION_DISABLED


def test_unknown_role_blocked() -> None:
    result = materialize_geox_fixture_dataset(
        GeoXFixtureDatasetMaterializationRequest(
            dataset_ref=_ref(
                dataset_ref_id="geox-fixture-spend-panel",
                source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                path=_SPEND_PATH,
                semantic_type=DatasetSemanticType.SPEND_PANEL,
            ),
            role=GeoXMaterializedDatasetRole.UNKNOWN,
            required_columns=["date"],
        )
    )
    assert result.status == GeoXFixtureMaterializationStatus.BLOCKED_DATASET_ROLE_UNCLEAR


def test_stage_3a_availability_helper() -> None:
    result = materialize_geox_readout_fixtures(
        GeoXFixtureMaterializationRequest(
            request_id="availability",
            dataset_requests=[
                GeoXFixtureDatasetMaterializationRequest(
                    dataset_ref=_ref(
                        dataset_ref_id="geox-fixture-spend-panel",
                        source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                        path=_SPEND_PATH,
                        semantic_type=DatasetSemanticType.SPEND_PANEL,
                    ),
                    role=GeoXMaterializedDatasetRole.SPEND,
                    required_columns=["date", "dma", "spend"],
                ),
                GeoXFixtureDatasetMaterializationRequest(
                    dataset_ref=_ref(
                        dataset_ref_id="geox-fixture-assignment-table",
                        source_type=DatasetSourceType.REGISTERED_ARTIFACT,
                        path=_ASSIGNMENT_PATH,
                        semantic_type=DatasetSemanticType.ASSIGNMENT_TABLE,
                    ),
                    role=GeoXMaterializedDatasetRole.ASSIGNMENT,
                    required_columns=["dma", "cell", "treatment"],
                ),
            ],
        )
    )
    availability = build_materialized_input_availability_from_fixture_result(result)
    assert availability.has_materialized_spend_df is True
    assert availability.has_materialized_assignment_df is True
    assert availability.has_assignment_mapping is True
    assert "dataframe" not in availability.model_dump_json().lower()


def test_workflow_does_not_import_panel_exp() -> None:
    source = _WORKFLOW_SOURCE.read_text(encoding="utf-8")
    assert "import panel_exp" not in source
    assert "from panel_exp" not in source
