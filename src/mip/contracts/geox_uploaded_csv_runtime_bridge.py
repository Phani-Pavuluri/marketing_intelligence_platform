"""GeoX uploaded CSV runtime bridge contracts."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.geox_panel_exp_runtime_call import (
    GeoXPostTestSpendEvidenceArtifact,
    GeoXTrustedReadoutSpendHandoffArtifact,
)
from mip.contracts.geox_uploaded_csv_adapter import GeoXUploadedCSVAdapterResult
from mip.contracts.uploaded_csv_materialization import UploadedCSVMaterializationResult

_REQUIRED_SPEND_COLUMN_MAPPING_FIELDS = (
    "spend_date_column",
    "spend_geo_column",
    "spend_amount_column",
)


class GeoXUploadedCSVRuntimeBridgeStatus(StrEnum):
    """Outcome of bridging uploaded CSV materialization into package runtime."""

    RUNTIME_COMPLETED = "runtime_completed"
    RUNTIME_COMPLETED_WITH_WARNINGS = "runtime_completed_with_warnings"
    BLOCKED_MISSING_MATERIALIZATION_RESULT = "blocked_missing_materialization_result"
    BLOCKED_MATERIALIZATION_NOT_READY = "blocked_materialization_not_ready"
    BLOCKED_MISSING_ADAPTER_RESULT = "blocked_missing_adapter_result"
    BLOCKED_ADAPTER_NOT_READY = "blocked_adapter_not_ready"
    BLOCKED_MISSING_REQUIRED_DATASET = "blocked_missing_required_dataset"
    BLOCKED_MISSING_REQUIRED_DATAFRAME = "blocked_missing_required_dataframe"
    BLOCKED_MISSING_REQUIRED_COLUMN_MAPPING = "blocked_missing_required_column_mapping"
    BLOCKED_PACKAGE_RUNTIME_UNAVAILABLE = "blocked_package_runtime_unavailable"
    BLOCKED_PACKAGE_RUNTIME_FAILED = "blocked_package_runtime_failed"


class GeoXUploadedCSVRuntimeBridgeIssueCode(StrEnum):
    """Typed uploaded CSV runtime bridge issue codes."""

    MISSING_MATERIALIZATION_RESULT = "missing_materialization_result"
    MATERIALIZATION_NOT_READY = "materialization_not_ready"
    MISSING_ADAPTER_RESULT = "missing_adapter_result"
    ADAPTER_NOT_READY = "adapter_not_ready"
    MISSING_REQUIRED_DATASET = "missing_required_dataset"
    MISSING_REQUIRED_DATAFRAME = "missing_required_dataframe"
    MISSING_REQUIRED_COLUMN_MAPPING = "missing_required_column_mapping"
    PACKAGE_RUNTIME_UNAVAILABLE = "package_runtime_unavailable"
    PACKAGE_RUNTIME_FAILED = "package_runtime_failed"
    POST_TEST_SPEND_INPUT_CREATED = "post_test_spend_input_created"
    PACKAGE_EVIDENCE_CREATED = "package_evidence_created"
    TRUSTED_HANDOFF_CREATED = "trusted_handoff_created"
    LINEAGE_PRESERVED = "lineage_preserved"
    CSV_REPARSE_AVOIDED = "csv_reparse_avoided"


class GeoXUploadedCSVRuntimeColumnMapping(ContractBaseModel):
    """Explicit column bindings for uploaded CSV package runtime bridge."""

    spend_date_column: str
    spend_geo_column: str
    spend_amount_column: str
    assignment_geo_column: str | None = None
    assignment_cell_column: str | None = None
    assignment_role_column: str | None = None
    currency_column: str | None = None
    spend_cell_column: str | None = None
    spend_channel_column: str | None = None
    spend_campaign_column: str | None = None
    kpi_date_column: str | None = None
    kpi_geo_column: str | None = None
    kpi_outcome_column: str | None = None


class GeoXUploadedCSVRuntimeBridgeRequest(ContractBaseModel):
    """Request to call package runtime using uploaded CSV materialization outputs."""

    request_id: str
    materialization_result: UploadedCSVMaterializationResult | None = None
    adapter_result: GeoXUploadedCSVAdapterResult | None = None
    experiment_id: str
    experiment_type: str
    post_period_start: str
    post_period_end: str
    column_mapping: GeoXUploadedCSVRuntimeColumnMapping
    assignment_mapping: dict[str, str] = Field(default_factory=dict)
    currency: str | None = None
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)


class GeoXUploadedCSVRuntimeBridgeResult(ContractBaseModel):
    """Uploaded CSV runtime bridge result with package artifacts."""

    request_id: str
    status: GeoXUploadedCSVRuntimeBridgeStatus
    evidence_artifact: GeoXPostTestSpendEvidenceArtifact | None = None
    trusted_handoff_artifact: GeoXTrustedReadoutSpendHandoffArtifact | None = None
    package_output_summary: dict[str, str | float | int | bool | None] = Field(
        default_factory=dict
    )
    issues: list[GeoXUploadedCSVRuntimeBridgeIssueCode] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    lineage: dict[str, str] = Field(default_factory=dict)
