"""GeoX readout fixture materialization contracts (narrow local fixtures only)."""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.geox_readout_input_resolution import DatasetReference, DatasetSourceType

_MATERIALIZED_MODEL_CONFIG = ConfigDict(
    extra="forbid",
    validate_assignment=True,
    use_enum_values=True,
    str_strip_whitespace=True,
    arbitrary_types_allowed=True,
)
DEFAULT_ALLOWED_FILE_EXTENSIONS = (".csv",)
DEFAULT_MAX_FIXTURE_ROWS = 10_000

RECOMMENDED_NEXT_STAGE_3B_ARTIFACT = "MIP_GEOX_READOUT_PANEL_EXP_RUNTIME_CALL_001B"

DEFAULT_FIXTURE_ROOTS = (
    "examples/fixtures/geox_readout_materialization",
)
DEFAULT_ALLOWED_SOURCE_TYPES = (
    DatasetSourceType.REGISTERED_ARTIFACT,
    DatasetSourceType.UPLOADED_CSV,
)


class GeoXFixtureMaterializationStatus(StrEnum):
    """Outcome of fixture/local-artifact materialization."""

    MATERIALIZED = "materialized"
    BLOCKED_SOURCE_NOT_REGISTERED = "blocked_source_not_registered"
    BLOCKED_SOURCE_TYPE_UNSUPPORTED = "blocked_source_type_unsupported"
    BLOCKED_LOCAL_PATH_NOT_ALLOWED = "blocked_local_path_not_allowed"
    BLOCKED_LOCAL_FILE_NOT_FOUND = "blocked_local_file_not_found"
    BLOCKED_FILE_FORMAT_UNSUPPORTED = "blocked_file_format_unsupported"
    BLOCKED_DECLARED_COLUMNS_MISSING = "blocked_declared_columns_missing"
    BLOCKED_DATASET_ROLE_UNCLEAR = "blocked_dataset_role_unclear"
    BLOCKED_SPEND_DATASET_MISSING = "blocked_spend_dataset_missing"
    BLOCKED_ASSIGNMENT_DATASET_MISSING = "blocked_assignment_dataset_missing"
    BLOCKED_MATERIALIZATION_DISABLED = "blocked_materialization_disabled"


class GeoXFixtureMaterializationIssueCode(StrEnum):
    """Typed fixture materialization issue codes."""

    SOURCE_NOT_REGISTERED = "source_not_registered"
    SOURCE_TYPE_UNSUPPORTED_FOR_FIXTURE_MATERIALIZATION = (
        "source_type_unsupported_for_fixture_materialization"
    )
    LOCAL_PATH_OUTSIDE_ALLOWED_FIXTURE_ROOT = "local_path_outside_allowed_fixture_root"
    LOCAL_FILE_NOT_FOUND = "local_file_not_found"
    FILE_FORMAT_UNSUPPORTED = "file_format_unsupported"
    DECLARED_COLUMNS_MISSING_FROM_MATERIALIZED_DATA = (
        "declared_columns_missing_from_materialized_data"
    )
    DATASET_ROLE_UNCLEAR = "dataset_role_unclear"
    SPEND_DATASET_MISSING = "spend_dataset_missing"
    ASSIGNMENT_DATASET_MISSING = "assignment_dataset_missing"
    MATERIALIZATION_DISABLED = "materialization_disabled"
    PANEL_EXP_RUNTIME_NOT_CALLED = "panel_exp_runtime_not_called"
    POST_TEST_SPEND_INPUT_NOT_INSTANTIATED = "post_test_spend_input_not_instantiated"


class GeoXMaterializedDatasetRole(StrEnum):
    """Explicit materialization role for a fixture dataset."""

    SPEND = "spend"
    ASSIGNMENT = "assignment"
    KPI = "kpi"
    VALUE_MAPPING = "value_mapping"
    MARGIN_MAPPING = "margin_mapping"
    UNKNOWN = "unknown"


class GeoXFixtureMaterializationPolicy(ContractBaseModel):
    """Safety policy for controlled fixture materialization."""

    enabled: bool = True
    allowed_fixture_roots: list[str] = Field(
        default_factory=lambda: list(DEFAULT_FIXTURE_ROOTS)
    )
    allowed_source_types: list[DatasetSourceType] = Field(
        default_factory=lambda: list(DEFAULT_ALLOWED_SOURCE_TYPES)
    )
    allowed_file_extensions: list[str] = Field(
        default_factory=lambda: list(DEFAULT_ALLOWED_FILE_EXTENSIONS)
    )
    max_rows: int = DEFAULT_MAX_FIXTURE_ROWS
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXFixtureDatasetMaterializationRequest(ContractBaseModel):
    """Materialize one declared dataset reference from a local fixture."""

    dataset_ref: DatasetReference
    role: GeoXMaterializedDatasetRole
    required_columns: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXMaterializedDataset(BaseModel):
    """Materialized in-memory dataset for fixture/test paths only."""

    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    dataset_ref_id: str
    role: GeoXMaterializedDatasetRole
    dataframe: Any
    columns: list[str] = Field(default_factory=list)
    row_count: int = 0
    source_lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXFixtureMaterializationRequest(ContractBaseModel):
    """Batch fixture materialization request."""

    request_id: str
    dataset_requests: list[GeoXFixtureDatasetMaterializationRequest] = Field(
        default_factory=list
    )
    policy: GeoXFixtureMaterializationPolicy = Field(
        default_factory=GeoXFixtureMaterializationPolicy
    )
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXFixtureMaterializationResult(BaseModel):
    """Fixture materialization result — may include in-memory dataframes."""

    model_config = _MATERIALIZED_MODEL_CONFIG

    request_id: str
    status: GeoXFixtureMaterializationStatus
    materialized_datasets: list[GeoXMaterializedDataset] = Field(default_factory=list)
    spend_dataset: GeoXMaterializedDataset | None = None
    assignment_dataset: GeoXMaterializedDataset | None = None
    issues: list[GeoXFixtureMaterializationIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
