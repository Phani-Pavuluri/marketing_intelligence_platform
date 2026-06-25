"""Tests for intake column mapping contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_mapping import (
    CanonicalMappingCandidate,
    CanonicalMappingStatus,
    ColumnMappingConfidence,
    ColumnMappingConfirmation,
    ColumnMappingProposal,
    ColumnMappingStatus,
    SemanticMappingDimension,
    SemanticMappingReport,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def test_column_mapping_proposal_with_canonical_candidates() -> None:
    proposal = ColumnMappingProposal(
        proposal_id="prop-001",
        source_id="outcome",
        asset_type=DataAssetType.OUTCOME_KPI_DATA,
        source_column="conversions",
        semantic_dimension=SemanticMappingDimension.METRIC_VALUE,
        confidence=ColumnMappingConfidence.HIGH,
        canonical_candidates=[
            CanonicalMappingCandidate(
                candidate_id="cand-001",
                dimension=SemanticMappingDimension.METRIC_VALUE,
                source_value="conversions",
                canonical_id="conversions",
                canonical_label="Conversions",
                confidence=ColumnMappingConfidence.MEDIUM,
            )
        ],
        why_proposed="Column name matches outcome metric field.",
    )
    assert proposal.status == ColumnMappingStatus.PROPOSED
    assert len(proposal.canonical_candidates) == 1


def test_column_mapping_confirmation_construction() -> None:
    confirmation = ColumnMappingConfirmation(
        confirmation_id="conf-001",
        proposal_id="prop-001",
        source_id="outcome",
        asset_type=DataAssetType.OUTCOME_KPI_DATA,
        source_column="week",
        semantic_dimension=SemanticMappingDimension.DATE,
        confirmed=True,
        confirmed_by="analyst@example.com",
        confirmed_at=_NOW,
    )
    assert confirmation.confirmed is True


def test_rejected_confirmation_requires_explanation() -> None:
    with pytest.raises(ValidationError, match="rejected confirmation requires"):
        ColumnMappingConfirmation(
            confirmation_id="conf-002",
            proposal_id="prop-002",
            source_id="media",
            asset_type=DataAssetType.MEDIA_SPEND_DATA,
            source_column="cost",
            semantic_dimension=SemanticMappingDimension.SPEND,
            confirmed=False,
        )


def test_canonical_candidate_can_be_unresolved() -> None:
    candidate = CanonicalMappingCandidate(
        candidate_id="cand-unresolved",
        dimension=SemanticMappingDimension.CHANNEL,
        source_value="paid_social_meta",
        canonical_id="",
        confidence=ColumnMappingConfidence.LOW,
        warnings=["Canonical channel registry resolution deferred to later phase."],
    )
    assert candidate.canonical_id == ""
    assert candidate.confidence == ColumnMappingConfidence.LOW


def test_semantic_mapping_report_serializes() -> None:
    report = SemanticMappingReport(
        report_id="report-001",
        manifest_id="sess-001-manifest",
        session_id="sess-001",
        recommendation_id="rec-001",
        plan_id="sess-001-plan",
        mapping_status=ColumnMappingStatus.NEEDS_USER_CONFIRMATION,
        created_at=_NOW,
    )
    payload = report.model_dump()
    assert payload["mapping_status"] == "needs_user_confirmation"


def test_canonical_mapping_status_values() -> None:
    assert CanonicalMappingStatus.UNRESOLVED.value == "unresolved"
