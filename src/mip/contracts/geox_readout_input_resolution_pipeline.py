"""GeoX readout input resolution pipeline contracts (Stage 2C)."""

from __future__ import annotations

from pydantic import Field

from mip.contracts.base import ContractBaseModel
from mip.contracts.geox_readout_input_resolution import (
    DatasetReference,
    GeoXReadoutInputResolutionRequest,
    GeoXReadoutInputResolutionResult,
)
from mip.contracts.geox_readout_source_inspection import GeoXReadoutSourceInspectionResult

RECOMMENDED_NEXT_STAGE_3_ARTIFACT = "MIP_GEOX_READOUT_PANEL_EXP_INTEGRATION_001"


class GeoXReadoutInputResolutionPipelineResult(ContractBaseModel):
    """End-to-end Stage 2C output: inspection enrichment then resolver outcome."""

    request_id: str
    inspection_result: GeoXReadoutSourceInspectionResult
    enriched_dataset_refs: list[DatasetReference] = Field(default_factory=list)
    enriched_resolution_request: GeoXReadoutInputResolutionRequest
    resolution_result: GeoXReadoutInputResolutionResult
    lineage: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
