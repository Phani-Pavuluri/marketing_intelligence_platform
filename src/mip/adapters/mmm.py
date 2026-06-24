"""MMM adapter interface contracts."""

from __future__ import annotations

from pydantic import Field

from mip.adapters.base import (
    AdapterInputBundle,
    AdapterOutputBundle,
    AdapterRunKind,
    AdapterRunStatus,
    AdapterValidationReport,
)
from mip.contracts.base import ContractBaseModel
from mip.workflows.configs.base import DraftConfigStatus
from mip.workflows.configs.mmm import MMMConfigDraft

_EXECUTABLE_DRAFT_STATUSES = frozenset(
    {
        DraftConfigStatus.DRAFTABLE,
        DraftConfigStatus.DRAFTABLE_WITH_WARNINGS,
    }
)


class MMMAdapterInput(ContractBaseModel):
    """Governed MMM adapter input derived from a config draft."""

    source_config_marker: str
    draft_status: DraftConfigStatus
    production_eligible: bool
    outcome_field: str | None = None
    spend_field: str | None = None
    date_field: str | None = None
    channel_field: str | None = None
    geo_field: str | None = None
    product_field: str | None = None
    campaign_field: str | None = None
    controls: list[str] = Field(default_factory=list)
    time_grain: str | None = None
    history_weeks: int | None = None


class MMMAdapterOutputPlaceholder(ContractBaseModel):
    """Governed placeholder metadata for future MMM adapter output."""

    artifact_type: str = "mmm_adapter_placeholder"
    config_marker: str
    workflow_notes: str = "Adapter output placeholder only; no model execution or estimates."


def build_mmm_adapter_input(config_draft: MMMConfigDraft) -> AdapterInputBundle:
    """Build an adapter input bundle from a governed MMM config draft."""
    metadata = config_draft.metadata
    if metadata.status == DraftConfigStatus.BLOCKED:
        msg = "blocked config draft cannot produce executable adapter input"
        raise ValueError(msg)

    adapter_status = (
        AdapterRunStatus.VALIDATED
        if metadata.status in _EXECUTABLE_DRAFT_STATUSES
        else AdapterRunStatus.DRAFT
    )
    mmm_input = MMMAdapterInput(
        source_config_marker=metadata.generated_marker,
        draft_status=metadata.status,
        production_eligible=metadata.production_eligible,
        outcome_field=config_draft.outcome_field,
        spend_field=config_draft.spend_field,
        date_field=config_draft.date_field,
        channel_field=config_draft.channel_field,
        geo_field=config_draft.geo_field,
        product_field=config_draft.product_field,
        campaign_field=config_draft.campaign_field,
        controls=list(config_draft.controls),
        time_grain=config_draft.time_grain,
        history_weeks=config_draft.history_weeks,
    )
    return AdapterInputBundle(
        kind=AdapterRunKind.MMM,
        status=adapter_status,
        source_config_marker=metadata.generated_marker,
        objective_type=str(metadata.objective_type),
        warnings=list(metadata.warnings),
        blocking_reasons=list(metadata.blocking_reasons),
        mmm_input=mmm_input,
    )


def build_mmm_adapter_output_placeholder(
    config_draft: MMMConfigDraft,
    *,
    status: AdapterRunStatus = AdapterRunStatus.COMPLETED,
) -> AdapterOutputBundle:
    """Build a governed MMM adapter output placeholder for contract tests."""
    marker = config_draft.metadata.generated_marker
    validation = AdapterValidationReport(
        status=status,
        passed_checks=["source_config_marker_present", "placeholder_only_output"],
    )
    return AdapterOutputBundle(
        kind=AdapterRunKind.MMM,
        status=status,
        source_config_marker=marker,
        validation=validation,
        mmm_output=MMMAdapterOutputPlaceholder(config_marker=marker),
    )
