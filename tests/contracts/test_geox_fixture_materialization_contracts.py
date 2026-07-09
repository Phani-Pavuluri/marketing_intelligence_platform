"""Tests for GeoX fixture materialization contracts."""

from __future__ import annotations

import pytest

from mip.contracts import (
    DEFAULT_FIXTURE_ROOTS,
    DEFAULT_MAX_FIXTURE_ROWS,
    RECOMMENDED_NEXT_STAGE_3B_ARTIFACT,
    DatasetReference,
    DatasetSemanticType,
    DatasetSourceType,
    GeoXFixtureDatasetMaterializationRequest,
    GeoXFixtureMaterializationIssueCode,
    GeoXFixtureMaterializationPolicy,
    GeoXFixtureMaterializationRequest,
    GeoXFixtureMaterializationResult,
    GeoXFixtureMaterializationStatus,
    GeoXMaterializedDataset,
    GeoXMaterializedDatasetRole,
)

_REQUIRED_STATUSES = {
    GeoXFixtureMaterializationStatus.MATERIALIZED,
    GeoXFixtureMaterializationStatus.BLOCKED_SOURCE_NOT_REGISTERED,
    GeoXFixtureMaterializationStatus.BLOCKED_SOURCE_TYPE_UNSUPPORTED,
    GeoXFixtureMaterializationStatus.BLOCKED_LOCAL_PATH_NOT_ALLOWED,
    GeoXFixtureMaterializationStatus.BLOCKED_LOCAL_FILE_NOT_FOUND,
    GeoXFixtureMaterializationStatus.BLOCKED_FILE_FORMAT_UNSUPPORTED,
    GeoXFixtureMaterializationStatus.BLOCKED_DECLARED_COLUMNS_MISSING,
    GeoXFixtureMaterializationStatus.BLOCKED_DATASET_ROLE_UNCLEAR,
    GeoXFixtureMaterializationStatus.BLOCKED_SPEND_DATASET_MISSING,
    GeoXFixtureMaterializationStatus.BLOCKED_ASSIGNMENT_DATASET_MISSING,
    GeoXFixtureMaterializationStatus.BLOCKED_MATERIALIZATION_DISABLED,
}

_FORBIDDEN_FIELD_FRAGMENTS = (
    "spend_delta",
    "delta_mu",
    "roi_value",
    "roas_value",
    "computed_lift",
    "lift_value",
    "posttestspendinput",
    "posttestspendevidence",
)


def test_required_enums_exist() -> None:
    assert _REQUIRED_STATUSES.issubset(set(GeoXFixtureMaterializationStatus))
    assert GeoXFixtureMaterializationIssueCode.PANEL_EXP_RUNTIME_NOT_CALLED in (
        GeoXFixtureMaterializationIssueCode
    )
    assert GeoXMaterializedDatasetRole.SPEND in GeoXMaterializedDatasetRole


def test_policy_defaults_are_safe() -> None:
    policy = GeoXFixtureMaterializationPolicy()
    assert policy.enabled is True
    assert DEFAULT_FIXTURE_ROOTS[0] in policy.allowed_fixture_roots
    assert DatasetSourceType.REGISTERED_ARTIFACT in policy.allowed_source_types
    assert DatasetSourceType.WAREHOUSE_TABLE not in policy.allowed_source_types
    assert ".csv" in policy.allowed_file_extensions
    assert policy.max_rows == DEFAULT_MAX_FIXTURE_ROWS


def test_metadata_models_serialize() -> None:
    ref = DatasetReference(
        dataset_ref_id="fixture-1",
        source_type=DatasetSourceType.REGISTERED_ARTIFACT,
        semantic_type=DatasetSemanticType.SPEND_PANEL,
        source_uri_or_handle="registered://examples/fixtures/geox_readout_materialization/spend_panel.csv",
        file_name_or_table_name="examples/fixtures/geox_readout_materialization/spend_panel.csv",
        declared_or_detected_columns=["date", "dma", "spend"],
        classification_confidence=0.9,
    )
    request = GeoXFixtureMaterializationRequest(
        request_id="req-1",
        dataset_requests=[
            GeoXFixtureDatasetMaterializationRequest(
                dataset_ref=ref,
                role=GeoXMaterializedDatasetRole.SPEND,
                required_columns=["date", "dma", "spend"],
            )
        ],
    )
    restored = GeoXFixtureMaterializationRequest.model_validate(request.model_dump())
    assert restored.request_id == "req-1"


def test_no_forbidden_panel_exp_or_metric_fields_on_metadata_models() -> None:
    models = (
        GeoXFixtureMaterializationPolicy,
        GeoXFixtureDatasetMaterializationRequest,
        GeoXFixtureMaterializationRequest,
    )
    for model in models:
        field_names = " ".join(model.model_fields).lower()
        for fragment in _FORBIDDEN_FIELD_FRAGMENTS:
            assert fragment not in field_names, f"{model.__name__} has forbidden field {fragment}"


def test_materialized_dataset_preserves_dataset_ref_id() -> None:
    import pandas as pd  # type: ignore[import-untyped]

    dataset = GeoXMaterializedDataset(
        dataset_ref_id="preserve-me",
        role=GeoXMaterializedDatasetRole.SPEND,
        dataframe=pd.DataFrame({"date": ["2026-01-06"], "spend": [1.0]}),
        columns=["date", "spend"],
        row_count=1,
    )
    assert dataset.dataset_ref_id == "preserve-me"


def test_contracts_exported_from_mip_contracts() -> None:
    assert RECOMMENDED_NEXT_STAGE_3B_ARTIFACT == "MIP_GEOX_READOUT_PANEL_EXP_RUNTIME_CALL_001B"
    assert GeoXFixtureMaterializationResult is not None


def test_result_requires_status() -> None:
    with pytest.raises(ValueError):
        GeoXFixtureMaterializationResult(request_id="bad", status=None)  # type: ignore[arg-type]
