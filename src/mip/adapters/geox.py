"""GeoX adapter interface contracts."""

from __future__ import annotations

from mip.adapters.base import (
    AdapterInputBundle,
    AdapterOutputBundle,
    AdapterRunKind,
    AdapterRunStatus,
    AdapterValidationReport,
)
from mip.contracts.base import ContractBaseModel
from mip.workflows.configs.base import DraftConfigStatus
from mip.workflows.configs.geox import GeoXConfigDraft

_EXECUTABLE_DRAFT_STATUSES = frozenset(
    {
        DraftConfigStatus.DRAFTABLE,
        DraftConfigStatus.DRAFTABLE_WITH_WARNINGS,
    }
)


class GeoXAdapterInput(ContractBaseModel):
    """Governed GeoX adapter input derived from a config draft."""

    source_config_marker: str
    draft_status: DraftConfigStatus
    production_eligible: bool
    outcome_field: str | None = None
    date_field: str | None = None
    pre_period_field: str | None = None
    test_period_field: str | None = None
    treatment_unit_field: str | None = None
    spend_field: str | None = None
    channel_field: str | None = None
    controls_placeholder: str | None = None
    exclusions_placeholder: str | None = None


class GeoXAdapterOutputPlaceholder(ContractBaseModel):
    """Governed placeholder metadata for future GeoX adapter output."""

    artifact_type: str = "geox_adapter_placeholder"
    config_marker: str
    workflow_notes: str = "Adapter output placeholder only; no experiment estimates or execution."


def build_geox_adapter_input(config_draft: GeoXConfigDraft) -> AdapterInputBundle:
    """Build an adapter input bundle from a governed GeoX config draft."""
    metadata = config_draft.metadata
    if metadata.status == DraftConfigStatus.BLOCKED:
        msg = "blocked config draft cannot produce executable adapter input"
        raise ValueError(msg)

    adapter_status = (
        AdapterRunStatus.VALIDATED
        if metadata.status in _EXECUTABLE_DRAFT_STATUSES
        else AdapterRunStatus.DRAFT
    )
    geox_input = GeoXAdapterInput(
        source_config_marker=metadata.generated_marker,
        draft_status=metadata.status,
        production_eligible=metadata.production_eligible,
        outcome_field=config_draft.outcome_field,
        date_field=config_draft.date_field,
        pre_period_field=config_draft.pre_period_field,
        test_period_field=config_draft.test_period_field,
        treatment_unit_field=config_draft.treatment_unit_field,
        spend_field=config_draft.spend_field,
        channel_field=config_draft.channel_field,
        controls_placeholder=config_draft.controls_placeholder,
        exclusions_placeholder=config_draft.exclusions_placeholder,
    )
    return AdapterInputBundle(
        kind=AdapterRunKind.GEOX,
        status=adapter_status,
        source_config_marker=metadata.generated_marker,
        objective_type=str(metadata.objective_type),
        warnings=list(metadata.warnings),
        blocking_reasons=list(metadata.blocking_reasons),
        geox_input=geox_input,
    )


def build_geox_adapter_output_placeholder(
    config_draft: GeoXConfigDraft,
    *,
    status: AdapterRunStatus = AdapterRunStatus.COMPLETED,
) -> AdapterOutputBundle:
    """Build a governed GeoX adapter output placeholder for contract tests."""
    marker = config_draft.metadata.generated_marker
    validation = AdapterValidationReport(
        status=status,
        passed_checks=["source_config_marker_present", "placeholder_only_output"],
    )
    return AdapterOutputBundle(
        kind=AdapterRunKind.GEOX,
        status=status,
        source_config_marker=marker,
        validation=validation,
        geox_output=GeoXAdapterOutputPlaceholder(config_marker=marker),
    )
