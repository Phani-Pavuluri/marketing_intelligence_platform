"""Tests for GeoX config draft schema."""

import pytest
from pydantic import ValidationError

from mip.workflows.configs.base import (
    ConfigDraftMetadata,
    ConfigDraftValidationReport,
    DraftConfigStatus,
)
from mip.workflows.configs.geox import PRE_PERIOD_PLACEHOLDER, GeoXConfigDraft
from mip.workflows.intake.objectives import BusinessObjectiveType
from mip.workflows.intake.requirements import WorkflowType


def test_geox_config_preserves_placeholders() -> None:
    metadata = ConfigDraftMetadata(
        objective_type=BusinessObjectiveType.EXPERIMENT_DESIGN,
        workflow_type=WorkflowType.GEOX_EXPERIMENT_DESIGN,
        status=DraftConfigStatus.DRAFTABLE,
        generated_marker="draft:test",
        production_eligible=True,
        validation=ConfigDraftValidationReport(
            status=DraftConfigStatus.DRAFTABLE,
            production_eligible=True,
        ),
    )
    draft = GeoXConfigDraft(
        metadata=metadata,
        outcome_field="outcome",
        date_field="date",
        treatment_unit_field="geo",
        pre_period_field=PRE_PERIOD_PLACEHOLDER,
    )
    assert draft.pre_period_field == PRE_PERIOD_PLACEHOLDER


def test_geox_config_rejects_empty_placeholder() -> None:
    metadata = ConfigDraftMetadata(
        objective_type=BusinessObjectiveType.EXPERIMENT_DESIGN,
        workflow_type=WorkflowType.GEOX_EXPERIMENT_DESIGN,
        status=DraftConfigStatus.DRAFTABLE,
        generated_marker="draft:test",
        production_eligible=True,
        validation=ConfigDraftValidationReport(
            status=DraftConfigStatus.DRAFTABLE,
            production_eligible=True,
        ),
    )
    with pytest.raises(ValidationError, match="placeholder"):
        GeoXConfigDraft(
            metadata=metadata,
            pre_period_field="   ",
        )
