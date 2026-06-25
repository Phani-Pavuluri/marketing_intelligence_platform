"""Tests for semantic mapping report assembly."""

from datetime import UTC, datetime
from typing import Any

from mip.contracts.intake import (
    DataGrain,
    GeoGrain,
    IntakeIntendedUse,
    MeasurementIntakeSession,
    MeasurementWorkflowKind,
)
from mip.contracts.intake_assets import DataAssetType, SampleColumnRole
from mip.contracts.intake_mapping import (
    ColumnMappingConfirmation,
    ColumnMappingProposal,
    ColumnMappingStatus,
    SemanticMappingDimension,
    SemanticMappingReport,
)
from mip.contracts.intake_sources import (
    DataSourceMode,
    DataSourceType,
    UploadedFileSourceRef,
)
from mip.workflows.intake.assets import build_intake_plan
from mip.workflows.intake.manifest import build_intake_manifest
from mip.workflows.intake.mapping import build_semantic_mapping_report
from mip.workflows.intake.recommendation import recommend_intake_path

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

_FORBIDDEN_FRAGMENTS = (
    "roi is",
    "lift estimate",
    "budget allocation",
    "coefficient",
    "causal effect",
    "data is compatible",
    "model-ready",
)


def _session(**overrides: Any) -> MeasurementIntakeSession:
    base: dict[str, Any] = {
        "session_id": "sess-001",
        "business_question": "How are paid channels affecting conversions?",
        "intended_use": IntakeIntendedUse.DIAGNOSTIC_ONLY,
        "workflow_kind": MeasurementWorkflowKind.MMM,
        "time_grain": DataGrain.WEEKLY,
        "geo_grain": GeoGrain.NATIONAL,
        "metric_id": "conversions",
        "estimand_id": "incremental_conversions",
        "created_at": _NOW,
    }
    base.update(overrides)
    return MeasurementIntakeSession(**base)


def _source(asset_type: DataAssetType, source_id: str) -> UploadedFileSourceRef:
    return UploadedFileSourceRef(
        source_id=source_id,
        source_mode=DataSourceMode.STREAMLIT_FILE_UPLOAD,
        source_type=DataSourceType.FILE,
        asset_type=asset_type,
        uri_or_table_ref=f"upload://sess-001/{source_id}.csv",
        created_at=_NOW,
    )


def _manifest() -> Any:
    recommendation = recommend_intake_path(_session())
    plan = build_intake_plan(recommendation)
    sources = [
        _source(DataAssetType.OUTCOME_KPI_DATA, "outcome"),
        _source(DataAssetType.MEDIA_SPEND_DATA, "media"),
        _source(DataAssetType.CHANNEL_MAPPING, "channel-map"),
        _source(DataAssetType.CALENDAR_SEASONALITY_DATA, "calendar"),
    ]
    return build_intake_manifest(_session(), recommendation, plan, sources), plan


def _proposal(
    proposal_id: str,
    source_id: str,
    asset_type: DataAssetType,
    source_column: str,
    dimension: SemanticMappingDimension,
    *,
    status: ColumnMappingStatus = ColumnMappingStatus.PROPOSED,
    role: SampleColumnRole | None = None,
) -> ColumnMappingProposal:
    return ColumnMappingProposal(
        proposal_id=proposal_id,
        source_id=source_id,
        asset_type=asset_type,
        source_column=source_column,
        semantic_dimension=dimension,
        sample_column_role=role,
        status=status,
    )


def _confirmation(
    proposal: ColumnMappingProposal,
    *,
    confirmed: bool = True,
) -> ColumnMappingConfirmation:
    return ColumnMappingConfirmation(
        confirmation_id=f"conf-{proposal.proposal_id}",
        proposal_id=proposal.proposal_id,
        source_id=proposal.source_id,
        asset_type=proposal.asset_type,
        source_column=proposal.source_column,
        semantic_dimension=proposal.semantic_dimension,
        confirmed=confirmed,
        confirmed_by="analyst@example.com" if confirmed else None,
        confirmed_at=_NOW if confirmed else None,
        notes=None if confirmed else "Column does not represent spend.",
        warnings=[] if confirmed else ["Rejected by user."],
    )


def _assert_no_forbidden_claims(report: SemanticMappingReport) -> None:
    text_parts = [
        *report.warnings,
        *report.blocking_reasons,
        *report.unconfirmed_required_mappings,
    ]
    combined = " ".join(text_parts).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in combined


def test_missing_required_outcome_mappings_needs_confirmation() -> None:
    manifest, plan = _manifest()
    report = build_semantic_mapping_report(
        manifest,
        proposals=[],
        expected_assets=plan.required_assets,
    )
    assert report.mapping_status == ColumnMappingStatus.NEEDS_USER_CONFIRMATION
    assert report.unconfirmed_required_mappings
    _assert_no_forbidden_claims(report)


def test_confirmed_outcome_mappings_report_confirmed() -> None:
    manifest, _plan = _manifest()
    proposals = [
        _proposal(
            "p-date",
            "outcome",
            DataAssetType.OUTCOME_KPI_DATA,
            "week",
            SemanticMappingDimension.DATE,
            role=SampleColumnRole.DATE,
        ),
        _proposal(
            "p-metric",
            "outcome",
            DataAssetType.OUTCOME_KPI_DATA,
            "metric_id",
            SemanticMappingDimension.METRIC_ID,
            role=SampleColumnRole.METRIC_ID,
        ),
        _proposal(
            "p-value",
            "outcome",
            DataAssetType.OUTCOME_KPI_DATA,
            "conversions",
            SemanticMappingDimension.METRIC_VALUE,
            role=SampleColumnRole.METRIC_VALUE,
        ),
        _proposal(
            "m-date",
            "media",
            DataAssetType.MEDIA_SPEND_DATA,
            "week",
            SemanticMappingDimension.DATE,
            role=SampleColumnRole.DATE,
        ),
        _proposal(
            "m-channel",
            "media",
            DataAssetType.MEDIA_SPEND_DATA,
            "channel",
            SemanticMappingDimension.CHANNEL,
            role=SampleColumnRole.CHANNEL,
        ),
        _proposal(
            "m-spend",
            "media",
            DataAssetType.MEDIA_SPEND_DATA,
            "spend",
            SemanticMappingDimension.SPEND,
            role=SampleColumnRole.SPEND,
        ),
        _proposal(
            "c-date",
            "calendar",
            DataAssetType.CALENDAR_SEASONALITY_DATA,
            "week",
            SemanticMappingDimension.DATE,
            role=SampleColumnRole.DATE,
        ),
        _proposal(
            "c-control",
            "calendar",
            DataAssetType.CALENDAR_SEASONALITY_DATA,
            "holiday_flag",
            SemanticMappingDimension.CONTROL,
            role=SampleColumnRole.CONTROL,
        ),
        _proposal(
            "map-src",
            "channel-map",
            DataAssetType.CHANNEL_MAPPING,
            "source_channel",
            SemanticMappingDimension.SOURCE_TO_CANONICAL_MAPPING,
            role=SampleColumnRole.MAPPING_SOURCE,
        ),
        _proposal(
            "map-tgt",
            "channel-map",
            DataAssetType.CHANNEL_MAPPING,
            "canonical_channel",
            SemanticMappingDimension.SOURCE_TO_CANONICAL_MAPPING,
            role=SampleColumnRole.MAPPING_TARGET,
        ),
    ]
    confirmations = [_confirmation(proposal) for proposal in proposals]
    report = build_semantic_mapping_report(
        manifest,
        proposals=proposals,
        confirmations=confirmations,
    )
    assert report.mapping_status == ColumnMappingStatus.CONFIRMED
    assert report.unconfirmed_required_mappings == []
    _assert_no_forbidden_claims(report)


def test_media_missing_spend_needs_confirmation() -> None:
    manifest, plan = _manifest()
    proposals = [
        _proposal(
            "m-date",
            "media",
            DataAssetType.MEDIA_SPEND_DATA,
            "week",
            SemanticMappingDimension.DATE,
            role=SampleColumnRole.DATE,
        ),
        _proposal(
            "m-channel",
            "media",
            DataAssetType.MEDIA_SPEND_DATA,
            "channel",
            SemanticMappingDimension.CHANNEL,
            role=SampleColumnRole.CHANNEL,
        ),
    ]
    confirmations = [_confirmation(proposal) for proposal in proposals]
    report = build_semantic_mapping_report(
        manifest,
        proposals=proposals,
        confirmations=confirmations,
        expected_assets=plan.required_assets,
    )
    assert report.mapping_status == ColumnMappingStatus.NEEDS_USER_CONFIRMATION
    assert any("media" in item and "spend" in item for item in report.unconfirmed_required_mappings)
    _assert_no_forbidden_claims(report)


def test_ambiguous_channel_mapping_surfaced() -> None:
    manifest, plan = _manifest()
    ambiguous = _proposal(
        "m-channel",
        "media",
        DataAssetType.MEDIA_SPEND_DATA,
        "media_type",
        SemanticMappingDimension.CHANNEL,
        status=ColumnMappingStatus.AMBIGUOUS,
        role=SampleColumnRole.CHANNEL,
    )
    report = build_semantic_mapping_report(
        manifest,
        proposals=[ambiguous],
        expected_assets=plan.required_assets,
    )
    assert len(report.ambiguous_mappings) == 1
    assert report.ambiguous_mappings[0].proposal_id == "m-channel"
    _assert_no_forbidden_claims(report)


def test_blocked_mapping_makes_report_blocked() -> None:
    manifest, plan = _manifest()
    blocked = ColumnMappingProposal(
        proposal_id="m-spend",
        source_id="media",
        asset_type=DataAssetType.MEDIA_SPEND_DATA,
        source_column="cost_usd",
        semantic_dimension=SemanticMappingDimension.SPEND,
        sample_column_role=SampleColumnRole.SPEND,
        status=ColumnMappingStatus.BLOCKED,
        blocking_reasons=["Currency column blocked pending finance review."],
    )
    report = build_semantic_mapping_report(
        manifest,
        proposals=[blocked],
        expected_assets=plan.required_assets,
    )
    assert report.mapping_status == ColumnMappingStatus.BLOCKED
    assert report.blocked_mappings
    _assert_no_forbidden_claims(report)


def test_rejected_confirmation_does_not_count_as_confirmed() -> None:
    manifest, plan = _manifest()
    proposal = _proposal(
        "m-spend",
        "media",
        DataAssetType.MEDIA_SPEND_DATA,
        "spend",
        SemanticMappingDimension.SPEND,
        role=SampleColumnRole.SPEND,
    )
    report = build_semantic_mapping_report(
        manifest,
        proposals=[proposal],
        confirmations=[_confirmation(proposal, confirmed=False)],
        expected_assets=plan.required_assets,
    )
    assert report.mapping_status == ColumnMappingStatus.NEEDS_USER_CONFIRMATION
    _assert_no_forbidden_claims(report)


def test_report_preserves_manifest_ids() -> None:
    manifest, plan = _manifest()
    report = build_semantic_mapping_report(
        manifest,
        proposals=[],
        expected_assets=plan.required_assets,
    )
    assert report.manifest_id == manifest.manifest_id
    assert report.session_id == manifest.session_id
    assert report.recommendation_id == manifest.recommendation_id
    assert report.plan_id == manifest.plan_id
    _assert_no_forbidden_claims(report)
