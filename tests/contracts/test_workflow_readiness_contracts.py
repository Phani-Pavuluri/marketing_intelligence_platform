"""Tests for workflow readiness report contracts."""

from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from mip.contracts.workflow_readiness import (
    BaseWorkflowReadinessReport,
    CalibrationSignalReadinessReport,
    DecisionReviewReadinessReport,
    GeoXDesignReadinessReport,
    MMMDataReadinessReport,
    WorkflowReadinessReportType,
    WorkflowReadinessStatus,
)

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


def _base_report(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "report_id": "rep-001",
        "session_id": "sess-001",
        "recommendation_id": "rec-001",
        "manifest_id": "man-001",
        "assessment_id": "wsa-001",
        "report_type": WorkflowReadinessReportType.MMM_DATA_READINESS,
        "created_at": _NOW,
    }
    base.update(overrides)
    return base


def test_mmm_readiness_report_constructs() -> None:
    report = MMMDataReadinessReport(**_base_report())
    assert report.report_type == WorkflowReadinessReportType.MMM_DATA_READINESS
    assert report.status == WorkflowReadinessStatus.NOT_APPLICABLE


def test_blocked_readiness_report_requires_blocking_reasons() -> None:
    with pytest.raises(ValidationError, match="blocking_reasons"):
        MMMDataReadinessReport(
            **_base_report(status=WorkflowReadinessStatus.BLOCKED),
        )


def test_readiness_report_rejects_forbidden_claims() -> None:
    with pytest.raises(ValidationError, match="forbidden claim"):
        GeoXDesignReadinessReport(
            **_base_report(
                report_type=WorkflowReadinessReportType.GEOX_DESIGN_READINESS,
                warnings=["The lift estimate is significant."],
            ),
        )


def test_readiness_reports_have_no_forbidden_result_fields() -> None:
    report = CalibrationSignalReadinessReport(
        **_base_report(
            report_type=WorkflowReadinessReportType.CALIBRATION_SIGNAL_READINESS,
        ),
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
    assert forbidden_keys.isdisjoint(report.model_dump().keys())
    serialized = str(report.model_dump()).lower()
    for fragment in _FORBIDDEN_FRAGMENTS:
        assert fragment not in serialized


def test_specific_report_types() -> None:
    geox = GeoXDesignReadinessReport(
        **_base_report(report_type=WorkflowReadinessReportType.GEOX_DESIGN_READINESS),
    )
    decision = DecisionReviewReadinessReport(
        **_base_report(report_type=WorkflowReadinessReportType.DECISION_REVIEW_READINESS),
    )
    assert isinstance(geox, BaseWorkflowReadinessReport)
    assert decision.requires_human_approval is True
