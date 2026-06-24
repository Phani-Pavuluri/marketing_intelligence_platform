"""Tests for workflow run summary models."""

import pytest
from pydantic import ValidationError

from mip.workflows.configs.base import (
    ConfigDraftMetadata,
    ConfigDraftValidationReport,
    DraftConfigStatus,
)
from mip.workflows.configs.mmm import MMMConfigDraft
from mip.workflows.intake import (
    BusinessObjective,
    BusinessObjectiveType,
    evaluate_objective_feasibility,
)
from mip.workflows.intake.requirements import WorkflowType
from mip.workflows.orchestrator.summary import WorkflowRunStatus, WorkflowRunSummary
from mip.workflows.readiness.profile import profile_to_availability
from mip.workflows.readiness.report import build_readiness_from_records


def test_blocked_summary_requires_blocking_reasons() -> None:
    objective = BusinessObjective(objective_type=BusinessObjectiveType.CONVERSION_ROI)
    readiness = build_readiness_from_records(
        [{"date": "2025-01-01", "spend": 1, "conversions": 2}] * 3,
        objective,
    )
    feasibility = evaluate_objective_feasibility(
        objective,
        profile_to_availability(readiness.profile),
    )
    metadata = ConfigDraftMetadata(
        objective_type=BusinessObjectiveType.CONVERSION_ROI,
        workflow_type=WorkflowType.MMM_CHANNEL_ROI,
        status=DraftConfigStatus.BLOCKED,
        generated_marker="draft:test",
        production_eligible=False,
        blocking_reasons=["blocked"],
        validation=ConfigDraftValidationReport(
            status=DraftConfigStatus.BLOCKED,
            blocking_reasons=["blocked"],
            production_eligible=False,
        ),
    )
    draft = MMMConfigDraft(metadata=metadata)
    with pytest.raises(ValidationError, match="blocking_reasons"):
        WorkflowRunSummary(
            objective=objective,
            profile=readiness.profile,
            feasibility=feasibility,
            readiness=readiness,
            config_draft=draft,
            status=WorkflowRunStatus.BLOCKED,
            blocking_reasons=[],
            narrative_summary="blocked run",
        )
