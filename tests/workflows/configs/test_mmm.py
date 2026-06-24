"""Tests for MMM config draft schema."""

import pytest
from pydantic import ValidationError

from mip.workflows.configs.base import (
    ConfigDraftMetadata,
    ConfigDraftValidationReport,
    DraftConfigStatus,
)
from mip.workflows.configs.mmm import MMMConfigDraft
from mip.workflows.intake.objectives import BusinessObjectiveType
from mip.workflows.intake.requirements import WorkflowType


def test_mmm_config_rejects_empty_controls() -> None:
    metadata = ConfigDraftMetadata(
        objective_type=BusinessObjectiveType.CONVERSION_ROI,
        workflow_type=WorkflowType.MMM_CHANNEL_ROI,
        status=DraftConfigStatus.DRAFTABLE,
        generated_marker="draft:test",
        production_eligible=True,
        validation=ConfigDraftValidationReport(
            status=DraftConfigStatus.DRAFTABLE,
            production_eligible=True,
        ),
    )
    with pytest.raises(ValidationError, match="controls"):
        MMMConfigDraft(
            metadata=metadata,
            outcome_field="conversions",
            spend_field="spend",
            date_field="date",
            controls=[""],
        )
