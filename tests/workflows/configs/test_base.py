"""Tests for shared config draft base types."""

import pytest
from pydantic import ValidationError

from mip.workflows.configs.base import (
    ConfigDraftMetadata,
    ConfigDraftValidationReport,
    DraftConfigStatus,
)
from mip.workflows.intake.objectives import BusinessObjectiveType
from mip.workflows.intake.requirements import WorkflowType


def _validation(**kwargs: object) -> ConfigDraftValidationReport:
    base = {
        "status": DraftConfigStatus.DRAFTABLE,
        "warnings": [],
        "blocking_reasons": [],
        "production_eligible": True,
    }
    base.update(kwargs)
    return ConfigDraftValidationReport(**base)  # type: ignore[arg-type]


def test_validation_report_blocked_requires_reasons() -> None:
    with pytest.raises(ValidationError, match="blocking_reasons"):
        ConfigDraftValidationReport(
            status=DraftConfigStatus.BLOCKED,
            warnings=[],
            blocking_reasons=[],
            production_eligible=False,
        )


def test_metadata_requires_matching_validation_status() -> None:
    with pytest.raises(ValidationError, match="validation status"):
        ConfigDraftMetadata(
            objective_type=BusinessObjectiveType.CONVERSION_ROI,
            workflow_type=WorkflowType.MMM_CHANNEL_ROI,
            status=DraftConfigStatus.DRAFTABLE,
            generated_marker="draft:test",
            production_eligible=True,
            validation=_validation(status=DraftConfigStatus.BLOCKED, blocking_reasons=["blocked"]),
        )


def test_metadata_blocked_requires_blocking_reasons() -> None:
    with pytest.raises(ValidationError, match="blocking_reasons"):
        ConfigDraftMetadata(
            objective_type=BusinessObjectiveType.CONVERSION_ROI,
            workflow_type=WorkflowType.MMM_CHANNEL_ROI,
            status=DraftConfigStatus.BLOCKED,
            generated_marker="draft:test",
            production_eligible=False,
            validation=_validation(
                status=DraftConfigStatus.BLOCKED,
                blocking_reasons=["blocked"],
            ),
            blocking_reasons=[],
        )


def test_metadata_rejects_empty_generated_marker() -> None:
    with pytest.raises(ValidationError, match="generated_marker"):
        ConfigDraftMetadata(
            objective_type=BusinessObjectiveType.CONVERSION_ROI,
            workflow_type=WorkflowType.MMM_CHANNEL_ROI,
            status=DraftConfigStatus.DRAFTABLE,
            generated_marker="   ",
            production_eligible=True,
            validation=_validation(),
        )
