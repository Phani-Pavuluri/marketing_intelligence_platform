"""Tests for common intake workbench contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from mip.contracts.common_intake import (
    CommonDataProfileSummary,
    CommonIntakeStatus,
    CommonIntakeWorkbench,
    DataSnapshot,
    DataSnapshotStatus,
    GeoCoverageSummary,
    IngestionMode,
    LLMAnswerGroundingContext,
    MediaCoverageSummary,
    MetricAvailabilitySummary,
    SourceIngestionRecord,
    WorkflowSupportAssessment,
    WorkflowSupportStatus,
)
from mip.contracts.intake import DataGrain, GeoGrain
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import DataSourceMode

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)

_FORBIDDEN_FRAGMENTS = (
    "lift estimate",
    "roi is",
    "budget allocation",
    "mde result",
    "power result",
    "matched markets",
    "treatment assignment",
    "control assignment",
    "causal effect",
)


def test_source_ingestion_record_constructs_without_file_io() -> None:
    record = SourceIngestionRecord(
        ingestion_id="ing-001",
        source_id="src-outcome",
        asset_type=DataAssetType.OUTCOME_KPI_DATA,
        source_mode=DataSourceMode.SAMPLE_DEMO_DATA,
        ingestion_mode=IngestionMode.SAMPLE_DEMO_DATA,
        declared_uri_or_ref="demo://national-weekly-outcome",
        ingested_at=_NOW,
    )
    assert record.snapshot_id is None
    assert record.status == DataSnapshotStatus.DECLARED


def test_data_snapshot_metadata_only_no_raw_rows() -> None:
    snapshot = DataSnapshot(
        snapshot_id="snap-001",
        source_id="src-outcome",
        asset_type=DataAssetType.OUTCOME_KPI_DATA,
        row_count=104,
        column_count=8,
        geo_grain=GeoGrain.NATIONAL,
        time_grain=DataGrain.WEEKLY,
        created_at=_NOW,
    )
    dumped = snapshot.model_dump()
    assert "rows" not in dumped
    assert "dataframe" not in dumped
    assert "raw_data" not in dumped
    assert snapshot.row_count == 104


def test_common_data_profile_summary_holds_coverage_summaries() -> None:
    profile = CommonDataProfileSummary(
        profile_id="prof-001",
        snapshot_id="snap-001",
        source_id="src-outcome",
        asset_type=DataAssetType.OUTCOME_KPI_DATA,
        metric_availability=MetricAvailabilitySummary(
            summary_id="met-001",
            source_id="src-outcome",
            metric_ids=["conversions"],
        ),
        geo_coverage=GeoCoverageSummary(
            summary_id="geo-001",
            source_id="src-outcome",
            geo_grain=GeoGrain.NATIONAL,
            geo_count=1,
        ),
        media_coverage=MediaCoverageSummary(
            summary_id="media-001",
            source_id="src-media",
            spend_present=True,
        ),
        created_at=_NOW,
    )
    assert profile.metric_availability is not None
    assert profile.geo_coverage is not None
    assert profile.media_coverage is not None


def test_workflow_support_assessment_blocked_requires_reasons() -> None:
    with pytest.raises(ValidationError, match="blocking_reasons"):
        WorkflowSupportAssessment(
            assessment_id="wsa-001",
            session_id="sess-001",
            recommendation_id="rec-001",
            plan_id="plan-001",
            manifest_id="man-001",
            support_status=WorkflowSupportStatus.BLOCKED,
            created_at=_NOW,
        )


def test_llm_grounding_context_blocks_forbidden_topics_by_default() -> None:
    context = LLMAnswerGroundingContext(
        context_id="ctx-001",
        session_id="sess-001",
        blocked_answer_topics=[
            "causal_lift",
            "roi",
            "budget_recommendation",
            "mde_power_result",
            "matched_markets",
            "treatment_control_assignment",
        ],
        created_at=_NOW,
    )
    blocked = set(context.blocked_answer_topics)
    assert "causal_lift" in blocked
    assert "matched_markets" in blocked


def test_common_intake_workbench_blocked_requires_reasons() -> None:
    with pytest.raises(ValidationError, match="blocking_reasons"):
        CommonIntakeWorkbench(
            workbench_id="wb-001",
            session_id="sess-001",
            recommendation_id="rec-001",
            plan_id="plan-001",
            manifest_id="man-001",
            status=CommonIntakeStatus.BLOCKED,
            created_at=_NOW,
        )


def test_forbidden_claims_rejected_in_profile_summary() -> None:
    with pytest.raises(ValidationError, match="forbidden claim"):
        CommonDataProfileSummary(
            profile_id="prof-bad",
            snapshot_id="snap-001",
            source_id="src-outcome",
            asset_type=DataAssetType.OUTCOME_KPI_DATA,
            warnings=["The lift estimate is 12%."],
            created_at=_NOW,
        )


def test_contracts_have_no_forbidden_result_fields() -> None:
    assessment = WorkflowSupportAssessment(
        assessment_id="wsa-001",
        session_id="sess-001",
        recommendation_id="rec-001",
        plan_id="plan-001",
        manifest_id="man-001",
        created_at=_NOW,
    )
    forbidden_keys = {
        "mde",
        "power",
        "power_result",
        "matched_markets",
        "lift",
        "roi",
        "budget_recommendation",
        "treatment_assignment",
        "control_assignment",
        "effect_estimate",
    }
    assert forbidden_keys.isdisjoint(assessment.model_dump().keys())
    serialized = str(assessment.model_dump()).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in serialized
