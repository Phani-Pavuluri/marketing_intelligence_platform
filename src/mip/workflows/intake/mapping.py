"""Deterministic semantic mapping report assembly (P4 / I6)."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum

from mip.contracts.intake_assets import RequiredDataAsset, SampleColumnRole
from mip.contracts.intake_mapping import (
    ColumnMappingConfirmation,
    ColumnMappingProposal,
    ColumnMappingStatus,
    SemanticMappingDimension,
    SemanticMappingReport,
)
from mip.contracts.intake_sources import DataSourceRef, GeoXIntakeManifest, MMMIntakeManifest


@dataclass(frozen=True)
class _RequiredMapping:
    """Required semantic dimension for a manifest source."""

    source_id: str
    asset_type: str
    dimension: str
    sample_column_role: str | None = None
    alternative_dimensions: frozenset[str] = frozenset()


def _enum_slug(value: object) -> str:
    if isinstance(value, StrEnum):
        return value.value
    return str(value)


def _role_slug(role: SampleColumnRole | str | None) -> str | None:
    if role is None:
        return None
    return _enum_slug(role)


def _dimension_from_role(role: SampleColumnRole) -> SemanticMappingDimension:
    mapping: dict[SampleColumnRole, SemanticMappingDimension] = {
        SampleColumnRole.DATE: SemanticMappingDimension.DATE,
        SampleColumnRole.GEO: SemanticMappingDimension.GEO,
        SampleColumnRole.MARKET: SemanticMappingDimension.MARKET,
        SampleColumnRole.COUNTRY: SemanticMappingDimension.COUNTRY,
        SampleColumnRole.PRODUCT: SemanticMappingDimension.PRODUCT,
        SampleColumnRole.METRIC_ID: SemanticMappingDimension.METRIC_ID,
        SampleColumnRole.METRIC_VALUE: SemanticMappingDimension.METRIC_VALUE,
        SampleColumnRole.CHANNEL: SemanticMappingDimension.CHANNEL,
        SampleColumnRole.PLATFORM: SemanticMappingDimension.PLATFORM,
        SampleColumnRole.CAMPAIGN: SemanticMappingDimension.CAMPAIGN,
        SampleColumnRole.SPEND: SemanticMappingDimension.SPEND,
        SampleColumnRole.IMPRESSIONS: SemanticMappingDimension.IMPRESSIONS,
        SampleColumnRole.CLICKS: SemanticMappingDimension.CLICKS,
        SampleColumnRole.CONTROL: SemanticMappingDimension.CONTROL,
        SampleColumnRole.MAPPING_SOURCE: SemanticMappingDimension.SOURCE_TO_CANONICAL_MAPPING,
        SampleColumnRole.MAPPING_TARGET: SemanticMappingDimension.SOURCE_TO_CANONICAL_MAPPING,
        SampleColumnRole.EFFECT_ESTIMATE: SemanticMappingDimension.EFFECT_ESTIMATE,
        SampleColumnRole.STANDARD_ERROR: SemanticMappingDimension.STANDARD_ERROR,
        SampleColumnRole.TIME_WINDOW: SemanticMappingDimension.TIME_WINDOW,
        SampleColumnRole.STATUS: SemanticMappingDimension.STATUS,
    }
    return mapping[role]


_DefaultSpec = tuple[SemanticMappingDimension, SampleColumnRole | None, frozenset[str]]


def _default_required_mappings(source_id: str, asset_type: str) -> list[_RequiredMapping]:
    defaults: dict[str, list[_DefaultSpec]] = {
        "outcome_kpi_data": [
            (SemanticMappingDimension.DATE, SampleColumnRole.DATE, frozenset()),
            (
                SemanticMappingDimension.METRIC_ID,
                SampleColumnRole.METRIC_ID,
                frozenset({"metric"}),
            ),
            (SemanticMappingDimension.METRIC_VALUE, SampleColumnRole.METRIC_VALUE, frozenset()),
        ],
        "media_spend_data": [
            (SemanticMappingDimension.DATE, SampleColumnRole.DATE, frozenset()),
            (SemanticMappingDimension.CHANNEL, SampleColumnRole.CHANNEL, frozenset()),
            (SemanticMappingDimension.SPEND, SampleColumnRole.SPEND, frozenset()),
        ],
        "calendar_seasonality_data": [
            (SemanticMappingDimension.DATE, SampleColumnRole.DATE, frozenset()),
            (SemanticMappingDimension.CONTROL, SampleColumnRole.CONTROL, frozenset()),
        ],
        "control_data": [
            (SemanticMappingDimension.DATE, SampleColumnRole.DATE, frozenset()),
            (SemanticMappingDimension.CONTROL, SampleColumnRole.CONTROL, frozenset()),
        ],
        "channel_mapping": [
            (
                SemanticMappingDimension.SOURCE_TO_CANONICAL_MAPPING,
                SampleColumnRole.MAPPING_SOURCE,
                frozenset(),
            ),
            (
                SemanticMappingDimension.SOURCE_TO_CANONICAL_MAPPING,
                SampleColumnRole.MAPPING_TARGET,
                frozenset(),
            ),
        ],
        "calibration_signal_data": [
            (SemanticMappingDimension.METRIC, None, frozenset({"metric_id"})),
            (
                SemanticMappingDimension.EFFECT_ESTIMATE,
                SampleColumnRole.EFFECT_ESTIMATE,
                frozenset(),
            ),
            (SemanticMappingDimension.STANDARD_ERROR, SampleColumnRole.STANDARD_ERROR, frozenset()),
            (SemanticMappingDimension.TIME_WINDOW, SampleColumnRole.TIME_WINDOW, frozenset()),
            (SemanticMappingDimension.STATUS, SampleColumnRole.STATUS, frozenset()),
        ],
        "experiment_export_data": [
            (SemanticMappingDimension.METRIC, None, frozenset({"metric_id"})),
            (SemanticMappingDimension.TIME_WINDOW, SampleColumnRole.TIME_WINDOW, frozenset()),
            (SemanticMappingDimension.STATUS, SampleColumnRole.STATUS, frozenset()),
        ],
    }
    specs = defaults.get(asset_type, [])
    return [
        _RequiredMapping(
            source_id=source_id,
            asset_type=asset_type,
            dimension=_enum_slug(dimension),
            sample_column_role=_role_slug(role),
            alternative_dimensions=alternatives,
        )
        for dimension, role, alternatives in specs
    ]


def _requirements_from_expected_assets(
    expected_assets: Sequence[RequiredDataAsset],
    source_by_asset: dict[str, DataSourceRef],
) -> list[_RequiredMapping]:
    requirements: list[_RequiredMapping] = []
    for asset in expected_assets:
        asset_type = _enum_slug(asset.asset_type)
        if _enum_slug(asset.requirement_level) != "required":
            continue
        source = source_by_asset.get(asset_type)
        if source is None:
            continue
        if asset.sample_schema is not None:
            for column in asset.sample_schema.required_columns:
                if not column.required:
                    continue
                requirements.append(
                    _RequiredMapping(
                        source_id=source.source_id,
                        asset_type=asset_type,
                        dimension=_enum_slug(_dimension_from_role(column.role)),
                        sample_column_role=_role_slug(column.role),
                    )
                )
            continue
        requirements.extend(_default_required_mappings(source.source_id, asset_type))
    return requirements


def _iter_manifest_sources(
    manifest: MMMIntakeManifest | GeoXIntakeManifest,
) -> list[DataSourceRef]:
    sources: list[DataSourceRef] = []
    if isinstance(manifest, MMMIntakeManifest):
        if manifest.outcome_source is not None:
            sources.append(manifest.outcome_source)
        sources.extend(manifest.media_sources)
        sources.extend(manifest.control_sources)
        sources.extend(manifest.mapping_sources)
        sources.extend(manifest.calibration_signal_sources)
        sources.extend(manifest.experiment_export_sources)
        return sources

    if manifest.outcome_source is not None:
        sources.append(manifest.outcome_source)
    if manifest.geo_mapping_source is not None:
        sources.append(manifest.geo_mapping_source)
    sources.extend(manifest.media_sources)
    sources.extend(manifest.experiment_export_sources)
    return sources


def _requirement_key(requirement: _RequiredMapping) -> str:
    role = _role_slug(requirement.sample_column_role)
    role_suffix = f":{role}" if role else ""
    return (
        f"{requirement.source_id}:{requirement.asset_type}:"
        f"{requirement.dimension}{role_suffix}"
    )


def _proposal_matches_requirement(
    proposal: ColumnMappingProposal,
    requirement: _RequiredMapping,
    *,
    confirmed: bool,
) -> bool:
    if not confirmed:
        return False
    if proposal.source_id != requirement.source_id:
        return False
    if _enum_slug(proposal.asset_type) != requirement.asset_type:
        return False

    proposal_dimension = _enum_slug(proposal.semantic_dimension)
    allowed_dimensions = {requirement.dimension, *requirement.alternative_dimensions}
    if proposal_dimension not in allowed_dimensions:
        return False

    req_role = _role_slug(requirement.sample_column_role)
    prop_role = _role_slug(proposal.sample_column_role)
    if req_role is not None and prop_role is not None and req_role != prop_role:
        return False
    if req_role is not None and prop_role is None:
        return False
    return True


def _is_confirmed(
    proposal: ColumnMappingProposal,
    confirmations_by_proposal: dict[str, ColumnMappingConfirmation],
) -> bool:
    confirmation = confirmations_by_proposal.get(proposal.proposal_id)
    if confirmation is not None:
        return confirmation.confirmed
    return _enum_slug(proposal.status) == ColumnMappingStatus.CONFIRMED


def _collect_requirements(
    manifest: MMMIntakeManifest | GeoXIntakeManifest,
    expected_assets: Sequence[RequiredDataAsset] | None,
) -> list[_RequiredMapping]:
    sources = _iter_manifest_sources(manifest)
    source_by_asset = {_enum_slug(source.asset_type): source for source in sources}

    if expected_assets:
        return _requirements_from_expected_assets(expected_assets, source_by_asset)

    requirements: list[_RequiredMapping] = []
    for source in sources:
        requirements.extend(
            _default_required_mappings(source.source_id, _enum_slug(source.asset_type))
        )
    return requirements


def build_semantic_mapping_report(
    manifest: MMMIntakeManifest | GeoXIntakeManifest,
    proposals: Sequence[ColumnMappingProposal],
    confirmations: Sequence[ColumnMappingConfirmation] = (),
    expected_assets: Sequence[RequiredDataAsset] | None = None,
) -> SemanticMappingReport:
    """Build a semantic mapping report from manifest proposals and confirmations."""

    proposal_list = list(proposals)
    confirmation_list = list(confirmations)
    confirmations_by_proposal = {
        confirmation.proposal_id: confirmation for confirmation in confirmation_list
    }

    ambiguous_mappings = [
        proposal
        for proposal in proposal_list
        if _enum_slug(proposal.status) == ColumnMappingStatus.AMBIGUOUS
    ]
    blocked_mappings = [
        proposal
        for proposal in proposal_list
        if _enum_slug(proposal.status)
        in {ColumnMappingStatus.BLOCKED, ColumnMappingStatus.REJECTED}
    ]

    requirements = _collect_requirements(manifest, expected_assets)
    unconfirmed_required: list[str] = []
    for requirement in requirements:
        satisfied = any(
            _proposal_matches_requirement(
                proposal,
                requirement,
                confirmed=_is_confirmed(proposal, confirmations_by_proposal),
            )
            for proposal in proposal_list
        )
        if not satisfied:
            unconfirmed_required.append(_requirement_key(requirement))

    warnings = list(manifest.warnings)
    blocking_reasons: list[str] = []
    if unconfirmed_required:
        warnings.append("Required semantic mappings are not yet confirmed.")

    if blocked_mappings:
        mapping_status = ColumnMappingStatus.BLOCKED
        blocking_reasons.extend(
            reason
            for proposal in blocked_mappings
            for reason in proposal.blocking_reasons
        )
        if not blocking_reasons:
            blocking_reasons.append("One or more column mappings are blocked.")
    elif unconfirmed_required:
        mapping_status = ColumnMappingStatus.NEEDS_USER_CONFIRMATION
    elif requirements:
        mapping_status = ColumnMappingStatus.CONFIRMED
    else:
        mapping_status = ColumnMappingStatus.PROPOSED

    return SemanticMappingReport(
        report_id=f"{manifest.manifest_id}-mapping-report",
        manifest_id=manifest.manifest_id,
        session_id=manifest.session_id,
        recommendation_id=manifest.recommendation_id,
        plan_id=manifest.plan_id,
        mapping_status=mapping_status,
        proposals=proposal_list,
        confirmations=confirmation_list,
        unconfirmed_required_mappings=unconfirmed_required,
        ambiguous_mappings=ambiguous_mappings,
        blocked_mappings=blocked_mappings,
        warnings=warnings,
        blocking_reasons=blocking_reasons,
        created_at=datetime.now(tz=UTC),
    )
