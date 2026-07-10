"""Tests for Planning/MMM calibration-signal mapping and readiness contracts."""

from __future__ import annotations

from datetime import UTC, date, datetime

from mip.contracts import (
    DEFAULT_MAX_SIGNAL_AGE_DAYS,
    FORBIDDEN_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_READINESS_RESULT_FIELD_NAMES,
    RECOMMENDED_NEXT_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_ARTIFACT,
    PlanningMMMCalibrationSignalMappedRecord,
    PlanningMMMCalibrationSignalMappingIssueCode,
    PlanningMMMCalibrationSignalMappingReadinessRequest,
    PlanningMMMCalibrationSignalMappingReadinessResult,
    PlanningMMMCalibrationSignalMappingStatus,
    PlanningMMMCalibrationSignalMappingTarget,
    PlanningMMMCalibrationSignalReadinessAssessment,
    PlanningMMMCalibrationSignalReadinessStatus,
    PlanningMMMCalibrationSignalRecordMetadata,
    PlanningMMMCalibrationSignalUsability,
    TabularSourceAccessMode,
    TabularSourceMaterializationMode,
    TabularSourceReference,
    TabularSourceType,
)
from mip.contracts.intake_assets import DataAssetType
from mip.contracts.intake_sources import (
    DataSourceMode,
    DataSourceRef,
    DataSourceStatus,
    DataSourceType,
)

_FORBIDDEN_TOP_LEVEL = (
    "spend_delta",
    "delta_mu",
    "roi",
    "roas",
    "incrementality",
    "optimal_budget",
    "marginal_roi",
    "recommendation",
    "budget_recommendation",
)


def test_required_enums_exist() -> None:
    assert PlanningMMMCalibrationSignalMappingStatus.MAPPING_READY in (
        PlanningMMMCalibrationSignalMappingStatus
    )
    assert PlanningMMMCalibrationSignalReadinessStatus.READY_FOR_MODEL_CALIBRATION in (
        PlanningMMMCalibrationSignalReadinessStatus
    )
    assert PlanningMMMCalibrationSignalUsability.USABLE_FOR_CALIBRATION in (
        PlanningMMMCalibrationSignalUsability
    )
    assert PlanningMMMCalibrationSignalMappingIssueCode.NO_MODEL_EXECUTION in (
        PlanningMMMCalibrationSignalMappingIssueCode
    )


def test_models_serialize() -> None:
    target = PlanningMMMCalibrationSignalMappingTarget(
        target_model_id="mmm-1",
        metric="revenue",
        estimand="incremental_contribution",
    )
    assert target.max_signal_age_days == DEFAULT_MAX_SIGNAL_AGE_DAYS
    assert target.allow_diagnostic_only is False
    assert target.require_uncertainty is True
    request = PlanningMMMCalibrationSignalMappingReadinessRequest(
        request_id="req-1",
        target=target,
    )
    assert request.intake_result is None


def test_mapped_records_preserve_refs_and_lineage() -> None:
    source_ref = DataSourceRef(
        source_id="calibration",
        source_mode=DataSourceMode.LOCAL_FILE_PATH_MANIFEST,
        source_type=DataSourceType.FILE,
        asset_type=DataAssetType.CALIBRATION_SIGNAL_DATA,
        uri_or_table_ref="/tmp/calibration.csv",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        status=DataSourceStatus.DECLARED,
    )
    tabular_ref = TabularSourceReference(
        source_id="calibration",
        source_type=TabularSourceType.UPLOADED_CSV,
        access_mode=TabularSourceAccessMode.LOCAL_FILE,
        materialization_mode=TabularSourceMaterializationMode.MATERIALIZED_IN_MEMORY,
        data_source_ref=source_ref,
    )
    record = PlanningMMMCalibrationSignalMappedRecord(
        record_id="rec-1",
        source_id="calibration",
        data_source_ref=source_ref,
        tabular_source_reference=tabular_ref,
        lineage={"stage": "mapping"},
        effect_field_name="prior_lift",
        uncertainty_field_name="prior_uncertainty",
    )
    assert record.data_source_ref is not None
    assert record.tabular_source_reference is not None
    assert record.lineage["stage"] == "mapping"


def test_no_forbidden_top_level_fields() -> None:
    for field_name in PlanningMMMCalibrationSignalMappingReadinessResult.model_fields:
        assert field_name not in _FORBIDDEN_TOP_LEVEL
    assert "roi" in FORBIDDEN_PLANNING_MMM_CALIBRATION_SIGNAL_MAPPING_READINESS_RESULT_FIELD_NAMES


def test_assessment_and_result_models() -> None:
    assessment = PlanningMMMCalibrationSignalReadinessAssessment(
        readiness_status=PlanningMMMCalibrationSignalReadinessStatus.DEFERRED,
        model_calibration_readiness_deferred=True,
    )
    result = PlanningMMMCalibrationSignalMappingReadinessResult(
        request_id="req-2",
        mapping_status=PlanningMMMCalibrationSignalMappingStatus.MAPPING_DEFERRED,
        readiness_status=PlanningMMMCalibrationSignalReadinessStatus.DEFERRED,
        assessment=assessment,
    )
    assert result.execution_allowed == {}


def test_exports_from_mip_contracts() -> None:
    assert (
        RECOMMENDED_NEXT_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_ARTIFACT
        == "MIP_PLANNING_MMM_TRUSTED_INPUT_AND_MODEL_RUN_ELIGIBILITY_001"
    )


def test_record_metadata_model() -> None:
    record = PlanningMMMCalibrationSignalRecordMetadata(
        record_id="rec-meta",
        source_id="calibration",
        metric="revenue",
        channel="search",
        estimand="incremental_contribution",
        start_date=date(2025, 1, 1),
        end_date=date(2025, 12, 31),
    )
    assert record.metric == "revenue"
