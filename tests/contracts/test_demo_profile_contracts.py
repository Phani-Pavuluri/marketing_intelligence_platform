"""Tests for P8 demo profiling contracts."""

from datetime import UTC, datetime

import pytest

from mip.contracts.common_intake import WorkflowSupportRoute
from mip.contracts.demo_profile import (
    MAX_DEMO_COLUMN_SAMPLE_VALUES,
    MAX_DEMO_PROFILE_ROWS,
    DemoColumnProfile,
    DemoColumnSemanticRole,
    DemoDatasetKind,
    DemoDatasetProfile,
    DemoProfileToWorkflowSummary,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def test_demo_column_profile_caps_sample_values() -> None:
    with pytest.raises(ValueError, match="sample_values capped"):
        DemoColumnProfile(
            column_name="sessions",
            semantic_role=DemoColumnSemanticRole.SESSIONS,
            sample_values=[str(i) for i in range(MAX_DEMO_COLUMN_SAMPLE_VALUES + 1)],
        )


def test_demo_dataset_profile_rejects_row_count_above_cap() -> None:
    with pytest.raises(ValueError, match="row_count exceeds demo cap"):
        DemoDatasetProfile(
            profile_id="demo-too-large",
            dataset_kind=DemoDatasetKind.UNKNOWN,
            row_count=MAX_DEMO_PROFILE_ROWS + 1,
            created_at=_NOW,
        )


def test_demo_profile_to_workflow_summary_round_trip() -> None:
    summary = DemoProfileToWorkflowSummary(
        summary_id="wf-001",
        profile_id="profile-001",
        dataset_kind=DemoDatasetKind.WEBSITE_TRAFFIC,
        common_profile_summary_id="common-001",
        supported_workflow_routes=[],
        blocked_workflow_routes=[WorkflowSupportRoute.NATIONAL_MMM],
        created_at=_NOW,
    )
    assert summary.profile_id == "profile-001"
    assert WorkflowSupportRoute.NATIONAL_MMM in summary.blocked_workflow_routes
