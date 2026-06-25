"""Tests for intake data asset contracts."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from mip.contracts.intake import IntakeCandidatePath
from mip.contracts.intake_assets import (
    DataAssetPurpose,
    DataAssetRequirementLevel,
    DataAssetType,
    IntakePlan,
    RequiredDataAsset,
    SampleColumnRole,
    SampleColumnSpec,
    SampleSchemaExpectation,
)

_NOW = datetime(2026, 5, 28, 12, 0, tzinfo=UTC)


def test_sample_column_spec_requires_description() -> None:
    with pytest.raises(ValidationError, match="description"):
        SampleColumnSpec(
            name="week",
            role=SampleColumnRole.DATE,
            description="   ",
        )


def test_sample_schema_requires_columns() -> None:
    with pytest.raises(ValidationError, match="required_columns"):
        SampleSchemaExpectation(
            schema_id="schema-001",
            asset_type=DataAssetType.OUTCOME_KPI_DATA,
            description="Outcome schema",
            required_columns=[],
        )


def test_required_asset_blocks_if_missing_only_for_required_levels() -> None:
    with pytest.raises(ValidationError, match="blocks_if_missing"):
        RequiredDataAsset(
            asset_id="asset-001",
            asset_type=DataAssetType.CONTROL_DATA,
            requirement_level=DataAssetRequirementLevel.OPTIONAL,
            purpose=DataAssetPurpose.CONFOUNDER_CONTROL,
            description="Optional control data",
            blocks_if_missing=True,
        )


def test_intake_plan_blocked_without_required_assets() -> None:
    plan = IntakePlan(
        plan_id="plan-001",
        session_id="sess-001",
        recommendation_id="rec-001",
        recommended_path=IntakeCandidatePath.BLOCKED_NEEDS_MORE_DATA,
        blocking_reasons=["Optimizer path deferred."],
    )
    assert plan.required_assets == []


def test_intake_plan_rejects_forbidden_claims() -> None:
    with pytest.raises(ValidationError, match="forbidden claim"):
        IntakePlan(
            plan_id="plan-001",
            session_id="sess-001",
            recommendation_id="rec-001",
            recommended_path=IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM,
            required_assets=[
                RequiredDataAsset(
                    asset_id="asset-001",
                    asset_type=DataAssetType.OUTCOME_KPI_DATA,
                    requirement_level=DataAssetRequirementLevel.REQUIRED,
                    purpose=DataAssetPurpose.MODEL_OUTCOME,
                    description="The causal effect is confirmed.",
                    blocks_if_missing=True,
                )
            ],
        )


def test_intake_plan_serializes() -> None:
    plan = IntakePlan(
        plan_id="plan-001",
        session_id="sess-001",
        recommendation_id="rec-001",
        recommended_path=IntakeCandidatePath.NATIONAL_DIAGNOSTIC_MMM,
        required_assets=[
            RequiredDataAsset(
                asset_id="asset-001",
                asset_type=DataAssetType.OUTCOME_KPI_DATA,
                requirement_level=DataAssetRequirementLevel.REQUIRED,
                purpose=DataAssetPurpose.MODEL_OUTCOME,
                description="Outcome KPI data",
                blocks_if_missing=True,
            )
        ],
    )
    payload = plan.model_dump()
    assert payload["recommended_path"] == "national_diagnostic_mmm"
